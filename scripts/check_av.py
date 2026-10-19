"""Measure encoded audio timing against the scheduled source mix, not guessed cuts.
python scripts/check_av.py <project> [--video <path>]
This verifies encoding alignment; it cannot identify a visible collision or judge sound.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from engine import provenance
from engine.score_audio import decode,delay,SR

def check(proj,video):
    (proj/'audio').mkdir(parents=True,exist_ok=True)
    provenance.atomic_json(proj/'audio/sync.json',{'layer':'encoding_audio_sync','checked':0,'failed':['check in progress'],'status':'running'})
    spec=json.loads((proj/'audio/events.json').read_text(encoding='utf-8'))
    sources=provenance.validate_events(proj,spec)
    final=provenance.validate_video(video,spec,sources,kind='final')
    score=spec.get('score')
    if not score:raise ValueError('no shared score; legacy events require manual sound/action review')
    if score['end']!=spec['end'] or score.get('fps',30)!=spec.get('fps',30):raise ValueError('film/score timeline mismatch; re-export and remix')
    mix=json.loads((proj/'audio/mix.json').read_text(encoding='utf-8'))
    if mix['score_sha256']!=hashlib.sha256(json.dumps(score,sort_keys=True).encode()).hexdigest():raise ValueError('stale mix: score changed')
    if mix.get('events_sha256')!=provenance.identity(spec) or mix.get('reference_sha256')!=provenance.digest(proj/'audio/score.wav') or final.get('reference_sha256')!=mix.get('reference_sha256'):raise ValueError('stale source mix/reference; re-mix')
    source=decode(proj/'audio/score.wav');encoded=decode(video)
    if abs(len(source)/SR-score['end'])>1/SR or abs(len(encoded)/SR-score['end'])>.1:raise ValueError('audio duration differs from score timeline')
    results=[];exempt=[];failed=[]
    for e in score['events']:
        if not e.get('sound'):continue
        if e.get('sync')=='exempt':exempt.append({'id':e['id'],'reason':e.get('sync_reason','unspecified')});continue
        # Same absolute windows retain a local copy of any encoder delay.
        a=max(0,round((e['start']-.1)*SR));b=min(len(source),round((e['start']+.3)*SR))
        try:
            r=delay(source[a:b],encoded[a:b],SR)
            r.update(id=e['id'],time=e['start'],frame_quantization_seconds=round(e['start']*score.get('fps',30))/score.get('fps',30)-e['start'])
            if abs(r['lag_seconds'])>1/score.get('fps',30) or r['correlation']<.75:failed.append(e['id'])
            results.append(r)
        except ValueError as exc:failed.append(e['id']);results.append({'id':e['id'],'error':str(exc)})
    report={'layer':'encoding_audio_sync','visual_action_sync':'not_checked',
            'input_sha256':provenance.identity(sources),'events_sha256':provenance.identity(spec),
            'scope':'source mix vs decoded final; visual action conditions require check_visual.py; no aesthetic score',
            'checked':len(results),'exempt':exempt,'failed':failed,'events':results,
            'duration_difference_seconds':(len(encoded)-len(source))/SR}
    if not results:failed.append('no checkable audio events')
    if abs(report['duration_difference_seconds'])>.1:failed.append('audio duration mismatch')
    (proj/'audio/sync.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('project',type=Path);p.add_argument('--video',type=Path);a=p.parse_args()
    try:result=check(a.project,a.video or a.project/'renders/final.mp4')
    except Exception as exc:
        result={'layer':'encoding_audio_sync','visual_action_sync':'not_checked','checked':0,'failed':[str(exc)]}
        (a.project/'audio').mkdir(parents=True,exist_ok=True)
        provenance.atomic_json(a.project/'audio/sync.json',result)
    print(json.dumps(result,indent=2))
    if result['failed']:sys.exit(1)
if __name__=='__main__':main()
