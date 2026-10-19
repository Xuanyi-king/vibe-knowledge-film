# -*- coding: utf-8 -*-
"""Objective diagnostics, never an aesthetic score. Exit 1 for technical errors.
python scripts/check_media.py film.mp4 --duration 36 [--allow-silent] [--loudness] [--output report.json]
Black, silence and scene-change detections are candidates for human review.
"""
import argparse
from fractions import Fraction
import json
import math
from pathlib import Path
import re
import subprocess
import sys


def run(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600)
    if result.returncode:
        raise RuntimeError(f"{cmd[0]} failed ({result.returncode}): {result.stderr[-2000:]}")
    return result


def inspect_media(path, expected_duration=None, require_audio=True, loudness=False):
    path = Path(path)
    info = json.loads(run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(path)]).stdout)
    video = next((s for s in info['streams'] if s['codec_type'] == 'video'), None)
    audio = next((s for s in info['streams'] if s['codec_type'] == 'audio'), None)
    if video is None: raise RuntimeError('No video stream')
    errors = []
    fps = float(Fraction(video.get('avg_frame_rate', '0/1')))
    duration = float(video.get('duration', info['format']['duration']))
    if not math.isfinite(duration) or duration <= 0: errors.append('Invalid video duration')
    if (video['width'], video['height']) != (1920, 1080): errors.append('Expected 1920x1080')
    if abs(fps - 30) > .001: errors.append('Expected 30fps')
    if video['codec_name'] != 'h264' or video.get('pix_fmt') != 'yuv420p': errors.append('Expected H.264 yuv420p')
    if expected_duration is not None:
        if not math.isfinite(expected_duration) or expected_duration <= 0: raise ValueError('Expected duration must be positive and finite')
        if abs(duration - expected_duration) > 1 / max(1, fps) + .001: errors.append(f'Duration {duration}s differs from expected {expected_duration}s')
    if require_audio and audio is None: errors.append('Missing audio stream')
    # Decode the whole video; ffmpeg -xerror turns corrupt packets into a failure.
    picture_log = run(['ffmpeg', '-hide_banner', '-nostats', '-xerror', '-i', str(path), '-an',
                       '-vf', 'blackdetect=d=0.08:pix_th=0.04,scdet=t=35', '-f', 'null', '-']).stderr
    black = [{'start': float(a), 'end': float(b), 'duration': float(c)} for a,b,c in re.findall(r'black_start:([\d.]+) black_end:([\d.]+) black_duration:([\d.]+)', picture_log)]
    cuts = [float(t) for t in re.findall(r'lavfi.scd.time: ([\d.]+)', picture_log)]
    audio_metrics = None
    silence = []
    if audio:
        audio_duration = float(audio.get('duration', info['format']['duration']))
        if abs(audio_duration - duration) > .1: errors.append('Audio/video duration mismatch exceeds 100ms')
        log = run(['ffmpeg', '-hide_banner', '-nostats', '-xerror', '-i', str(path), '-vn',
                   '-af', 'astats=metadata=0:reset=0,silencedetect=noise=-60dB:d=0.2', '-f', 'null', '-']).stderr
        def last_metric(label):
            matches = re.findall(label + r': ([-\d.inf]+)', log)
            value = float(matches[-1]) if matches else None
            return value if value is not None and math.isfinite(value) else None
        peak, rms = last_metric('Peak level dB'), last_metric('RMS level dB')
        audio_metrics = {'duration': audio_duration, 'codec': audio['codec_name'], 'sample_rate': audio.get('sample_rate'),
                         'sample_peak_db': peak, 'rms_db': rms, 'note': 'Decoded sample peak, not an intersample true-peak or LUFS measurement.'}
        if peak is not None and peak >= 0: errors.append('Decoded audio reaches or exceeds full scale')
        if loudness:
            measurement=run(['ffmpeg','-hide_banner','-nostats','-i',str(path),'-vn',
                '-af','loudnorm=I=-18:TP=-1.5:LRA=14:print_format=json','-f','null','-']).stderr
            blocks=re.findall(r'\{\s*"input_i"[\s\S]*?\}',measurement)
            if not blocks:raise RuntimeError('FFmpeg did not return a loudness measurement')
            data=json.loads(blocks[-1])
            for output,key in [('integrated_lufs','input_i'),('true_peak_dbtp','input_tp'),('loudness_range_lu','input_lra')]:
                value=float(data[key]);audio_metrics[output]=value if math.isfinite(value) else None
            audio_metrics['note']='Decoded sample peak/RMS plus FFmpeg loudnorm integrated LUFS, true peak and LRA; not a mix-quality score.'
            if audio_metrics['true_peak_dbtp'] is not None and audio_metrics['true_peak_dbtp']>0:errors.append('Intersample true peak exceeds 0 dBTP')

        for start in re.findall(r'silence_start: ([\d.]+)', log): silence.append({'start': float(start)})
        ends = re.findall(r'silence_end: ([\d.]+) \| silence_duration: ([\d.]+)', log)
        for i, (end, length) in enumerate(ends):
            if i < len(silence): silence[i].update(end=float(end), duration=float(length))
    return {'file': str(path), 'video': {'width': video['width'], 'height': video['height'], 'fps': fps, 'duration': duration,
            'codec': video['codec_name'], 'pixel_format': video.get('pix_fmt'), 'frames': video.get('nb_frames')},
            'audio': audio_metrics, 'errors': errors, 'candidates': {'black': black, 'silence': silence, 'scene_change_times': cuts},
            'unverified': ['aesthetic quality', 'unexpected blank colored frames', 'object bounds and subtitle occlusion',
                           'glyph coverage/readability', 'storyboard match', 'factual correctness'],
            'interpretation': 'Candidates require timestamped visual/audio review; intentional black, cuts and silence are allowed.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('video', type=Path)
    parser.add_argument('--duration', type=float)
    parser.add_argument('--allow-silent', action='store_true')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--loudness', action='store_true', help='measure integrated LUFS, true peak and LRA; extra audio pass')
    args = parser.parse_args()
    try: report = inspect_media(args.video, args.duration, not args.allow_silent, args.loudness)
    except (RuntimeError, ValueError, OSError, subprocess.TimeoutExpired) as exc:
        print(str(exc), file=sys.stderr); return 1
    output = json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output + '\n', encoding='utf-8')
    print(output)
    return 1 if report['errors'] else 0

if __name__ == '__main__': sys.exit(main())
