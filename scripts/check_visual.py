"""Check declared scene conditions after seek() at actual frame times.
python scripts/check_visual.py <project> [--video final.mp4] [--require <id> ...]
Screenshots are evidence for review, not semantic recognition or an aesthetic score.
"""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from engine import render,provenance


def check(proj,video=None,required=()):
    (proj/'review').mkdir(parents=True,exist_ok=True)
    provenance.atomic_json(proj/'review/visual-sync.json',{'layer':'declared_visual_action_sync','passed':False,'status':'running','checks':[]})
    spec=json.loads((proj/'audio/events.json').read_text(encoding='utf-8'))
    sources=provenance.validate_events(proj,spec)
    artifact=provenance.validate_video(video,spec,sources,kind='final') if video else None
    folder=proj/'review/visual';folder.mkdir(parents=True,exist_ok=True)
    report={'layer':'declared_visual_action_sync','scope':'author-declared numeric conditions on rendered object state; not semantic image recognition or subjective acceptance',
            'input_sha256':provenance.identity(sources),'events_sha256':provenance.identity(spec),
            'video_sha256':artifact['sha256'] if artifact else None,'encoding_audio_sync':'not_checked','checks':[],'passed':False}
    def go(pg):
        live=pg.evaluate('({end:END,fps:FPS,score:window.VK_SCORE?.json()||null,checks:window.VK_CHECKS?.list()||[]})')
        if live['end']!=spec['end'] or live['fps']!=spec['fps'] or live['score']!=spec.get('score'):
            raise RuntimeError('live film/score differs from exported events; re-export')
        checks=live['checks']
        if not checks:raise RuntimeError('no declared visual conditions; cannot verify visual action sync')
        missing=set(required)-{d['id'] for d in checks}
        if missing:raise RuntimeError(f'missing required visual checks: {sorted(missing)}')
        for d in checks:
            image=render.shot(pg,d['time'])  # update and actually render BEFORE measuring
            if pg._vk_remote_assets or pg._vk_generated_assets:raise RuntimeError('visual checks require tracked local assets')
            row=pg.evaluate('id=>VK_CHECKS.measure(id)',d['id'])
            name=f"frame_{d['frame']:06d}.png";(folder/name).write_bytes(image)
            row.update(image=f'review/visual/{name}',image_sha256=__import__('hashlib').sha256(image).hexdigest())
            report['checks'].append(row)
    render.with_page(proj,go)
    provenance.stable(proj,sources)
    report['passed']=all(d['passed'] for d in report['checks'])
    provenance.atomic_json(proj/'review/visual-sync.json',report)
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('project',type=Path);p.add_argument('--video',type=Path);p.add_argument('--require',nargs='+',default=[]);a=p.parse_args()
    try:report=check(a.project,a.video,a.require)
    except Exception as exc:
        report={'layer':'declared_visual_action_sync','passed':False,'checks':[],'error':str(exc)}
        (a.project/'review').mkdir(parents=True,exist_ok=True)
        provenance.atomic_json(a.project/'review/visual-sync.json',report)
    print(json.dumps(report,indent=2));return 0 if report['passed'] else 1
if __name__=='__main__':sys.exit(main())
