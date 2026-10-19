"""Local-input identity shared by event export, picture rendering, mux and QA.
Sidecars detect stale/mixed artifacts; hashes are not a claim of semantic accuracy.
"""
import hashlib
import json
from pathlib import Path
try:
    from .render_cache import source_files, digest, atomic_json
except ImportError:
    from render_cache import source_files, digest, atomic_json


def identity(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=True,allow_nan=False).encode()).hexdigest()


def stable(proj,sources):
    if source_files(proj)!=sources:raise RuntimeError('render input changed during export; retry after finishing edits; old output kept')


def seal_events(spec,sources):
    payload={k:v for k,v in spec.items() if k!='provenance'}
    return {**payload,'provenance':{'version':1,'sources':sources,'input_sha256':identity(sources),'payload_sha256':identity(payload)}}


def validate_events(proj,spec):
    record=spec.get('provenance',{})
    sources=source_files(proj)
    payload={k:v for k,v in spec.items() if k!='provenance'}
    if (record.get('version')!=1 or record.get('sources')!=sources or
        record.get('input_sha256')!=identity(sources) or record.get('payload_sha256')!=identity(payload)):
        raise RuntimeError('stale or unversioned audio/events.json; run render.py <project> --events after finishing input edits')
    return sources


def sidecar(path):return Path(str(path)+'.provenance.json')


def publish_video(target,out,sources,timeline,kind='raw',**links):
    record={'version':1,'kind':kind,'input_sha256':identity(sources),
            'sha256':digest(target),'timeline':timeline,**links}
    # Publish the sidecar first: interruption can invalidate an old/new pair,
    # but can never make mismatched bytes pass. No metadata-only adoption CLI.
    atomic_json(sidecar(out),record)
    target.replace(out)
    return record


def validate_video(path,spec,sources,kind='raw'):
    try:
        record=json.loads(sidecar(path).read_text(encoding='utf-8'))
        timeline=record['timeline']
        if (record['version']!=1 or record['kind']!=kind or record['input_sha256']!=identity(sources)
            or record['sha256']!=digest(path) or timeline!=dict(end=spec['end'],fps=spec.get('fps',30),start=0,stop=spec['end'])):
            raise ValueError('input, media bytes or timeline differ')
        if kind=='final' and record.get('events_sha256')!=identity(spec):raise ValueError('events differ')
        return record
    except (OSError,KeyError,ValueError,TypeError) as exc:
        raise RuntimeError(f'stale or unversioned {kind} video {path}; re-render raw and re-mux with current events: {exc}') from exc
