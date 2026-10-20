"""Persistent, validated frame-range cache. Uses the existing frame renderer."""
from concurrent.futures import CancelledError, ThreadPoolExecutor, as_completed
from contextlib import contextmanager
from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import subprocess
import tempfile

ENGINE = Path(__file__).resolve().parent
ENCODER = {'codec': 'libx264', 'pix_fmt': 'yuv420p', 'crf': 14, 'preset': 'medium', 'decode_threads': 1, 'encode_threads': 4}


@contextmanager
def cache_lock(path):
    """OS-owned lock: automatically released even when a process is killed."""
    with path.open('a+b') as stream:
        if stream.seek(0, 2) == 0:
            stream.write(b'0'); stream.flush()
        stream.seek(0)
        try:
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            raise RuntimeError('another render owns this project cache; wait for it to finish') from exc
        try:
            yield
        finally:
            stream.seek(0)
            if os.name == 'nt': msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else: fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest() if hasattr(hashlib, 'file_digest') else hashlib.sha256(stream.read()).hexdigest()


def source_files(proj):
    entries = {}
    for label, root in [('project', proj), ('engine', ENGINE)]:
        for path in sorted(root.rglob('*')):
            rel = path.relative_to(root)
            if any(p in {'.git', '__pycache__'} for p in rel.parts): continue
            if label == 'project' and rel.parts[0] in {'renders', 'review', 'audio'}: continue
            if path.is_symlink(): raise ValueError(f'resume requires local input copies, not symlinks: {path}')
            if not path.is_file(): continue
            entries[f'{label}/{rel.as_posix()}'] = digest(path)
    return entries


def checked(cmd, label):
    try:
        return subprocess.run(cmd, check=True, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=600)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError) as exc:
        raise RuntimeError(f'{label}: {str(getattr(exc, "stderr", None) or exc)[-1500:]}') from exc


def validate_video(path, frames, meta):
    result = checked(['ffprobe', '-v', 'error', '-count_frames', '-select_streams', 'v:0',
        '-show_streams', '-of', 'json', str(path)], f'validate {path.name}')
    try:
        s = json.loads(result.stdout)['streams'][0]
        valid = (int(s['nb_read_frames']) == frames and s['width'] == meta['width']
                 and s['height'] == meta['height'] and s['codec_name'] == 'h264'
                 and s['pix_fmt'] == 'yuv420p' and abs(float(Fraction(s['avg_frame_rate'])) - meta['fps']) < .0001
                 and abs(float(s['duration']) - frames / meta['fps']) < .002)
        if not valid: raise ValueError('frame count, dimensions, codec, rate or duration mismatch')
    except (KeyError, IndexError, ValueError, TypeError) as exc:
        raise RuntimeError(f'validate {path.name}: {exc}') from exc
    checked(['ffmpeg', '-v', 'error', '-xerror', '-i', str(path), '-f', 'null', '-'], f'decode {path.name}')


def atomic_json(path, value):
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
    tmp.replace(path)


def render_cached(proj, out, meta, chunk_seconds, jobs, render_part, expected_sources=None):
    if not all(math.isfinite(meta[k]) and meta[k] > 0 for k in ('end', 'fps', 'width', 'height')):
        raise ValueError('resume: invalid film dimensions, duration or fps')
    if not math.isfinite(chunk_seconds) or chunk_seconds <= 0 or round(chunk_seconds * meta['fps']) < 1:
        raise ValueError('resume chunk must contain at least one frame')
    if jobs < 1: raise ValueError('resume jobs must be positive')
    total, step = round(meta['end'] * meta['fps']), round(chunk_seconds * meta['fps'])
    if total < 1: raise ValueError('resume film contains no frames')
    root = proj / 'renders/.vk-cache'; root.mkdir(parents=True, exist_ok=True)
    with cache_lock(root / 'lock'):
        sources = source_files(proj)
        if expected_sources is not None and sources != expected_sources:
            raise RuntimeError('render input changed during browser initialization; retry after finishing edits')
        identity = {'schema': 1, 'sources': sources, 'film': meta, 'chunk_frames': step,
                    'encoder': ENCODER, 'platform': platform.platform(),
                    'ffmpeg': checked(['ffmpeg', '-version'], 'ffmpeg version').stdout}
        key = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()
        folder = root / key[:20]; folder.mkdir(exist_ok=True)
        manifest = folder / 'manifest.json'
        if not manifest.exists(): print(f'cache new identity {key[:20]} (source / runtime / encoding / chunk parameters)', flush=True)
        if manifest.exists():
            try:
                if json.loads(manifest.read_text(encoding='utf-8')) != identity: raise ValueError('identity mismatch')
            except ValueError as exc:
                raise RuntimeError(f'damaged cache manifest: remove {folder} and retry') from exc
        atomic_json(manifest, identity)
        ranges = [(i, min(i + step, total)) for i in range(0, total, step)]
        parts = [folder / f'part{i:05d}.mp4' for i in range(len(ranges))]

        def stable():
            if source_files(proj) != sources:
                raise RuntimeError('render input changed during export; retry after finishing edits; old output kept')

        def part(i):
            path = parts[i]; a, b = ranges[i]; stamp = path.with_suffix('.json')
            try:
                record = json.loads(stamp.read_text(encoding='utf-8'))
                if record != {'start': a, 'stop': b, 'sha256': digest(path)}: raise ValueError('stamp mismatch')
                validate_video(path, b - a, meta)
                print(f'cache reuse {i + 1}/{len(parts)} [{a},{b})', flush=True)
                return
            except (OSError, ValueError, RuntimeError):
                pass
            print(f'cache render {i + 1}/{len(parts)} [{a},{b})', flush=True)
            render_part(proj, path, a / meta['fps'], b / meta['fps'])
            stable()
            validate_video(path, b - a, meta)
            atomic_json(stamp, {'start': a, 'stop': b, 'sha256': digest(path)})

        # Every worker has an independent browser. Completed parts survive any
        # failure; OS locks and atomic part writes make the next run recoverable.
        if jobs == 1:
            for i in range(len(parts)): part(i)
        else:
            failures = []
            with ThreadPoolExecutor(max_workers=min(jobs, len(parts))) as pool:
                futures = {pool.submit(part, i): i for i in range(len(parts))}
                try:
                    for future in as_completed(futures):
                        try: future.result()
                        except CancelledError: continue
                        except Exception as exc:
                            failures.append(f'part {futures[future]}: {exc}')
                            for pending in futures: pending.cancel()
                except BaseException:
                    for pending in futures: pending.cancel()
                    raise  # Only already-running short chunks need to close.
            if failures: raise RuntimeError('resume workers failed; completed parts kept:\n' + '\n'.join(failures))
        stable()
        listing = folder / 'concat.txt'
        listing.write_text(''.join(f"file '{p.name}'\n" for p in parts), encoding='utf-8')
        with tempfile.TemporaryDirectory(prefix='.vk-concat-', dir=out.parent) as tmp:
            target = Path(tmp) / 'raw.mp4'
            checked(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(listing),
                     '-c', 'copy', '-movflags', '+faststart', str(target)], 'concat failed; old output kept')
            validate_video(target, total, meta)
            stable()
            try:
                from .provenance import publish_video
            except ImportError:
                from provenance import publish_video
            publish_video(target, out, sources, dict(end=meta['end'], fps=meta['fps'], start=0, stop=meta['end']))
        print(f'done {out} {total} frames; cache {folder}', flush=True)
        return folder
