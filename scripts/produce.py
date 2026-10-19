"""Technical production entry after the Agent has authored a complete film.
python scripts/produce.py <project> [--assets geo scene] [--chunk 4] [--jobs 1]
Creative decisions and subjective review remain the Agent's responsibility.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from engine import render,provenance
ROOT=Path(__file__).resolve().parents[1]


def produce(proj,chunk=4,jobs=1,assets=()):
    proj=proj.resolve();(proj/'review').mkdir(parents=True,exist_ok=True)
    report={'status':'running','stages':[],'subjective_visual_review':'not_automated','subjective_listening':'not_automated'}
    def step(name,script,*args):
        report['active_stage']=name
        subprocess.run([sys.executable,str(ROOT/script),*map(str,args)],check=True)
        report['stages'].append(name)
    try:
        for asset in assets:
            if asset not in {'geo','scene'}:raise ValueError('supported optional assets: geo, scene')
            step('assets-'+asset,f'engine/get_{asset}_assets.py')
        step('fonts','engine/get_fonts.py')
        report['active_stage']='inspect'
        meta=render.with_page(proj,lambda pg:pg.evaluate('({end:END,fps:FPS,score:!!window.VK_SCORE,checks:window.VK_CHECKS?.list().length||0})'))
        report['film']=meta
        step('determinism','engine/render.py',proj,'--det')
        step('picture','engine/render.py',proj,'--resume',chunk,'--jobs',jobs)
        step('events','engine/render.py',proj,'--events')
        step('sound','engine/audio.py',proj,'--stems')
        if meta['score']:step('encoding_audio_sync','scripts/check_av.py',proj)
        if meta['checks']:step('declared_visual_action_sync','scripts/check_visual.py',proj,'--video',proj/'renders/final.mp4')
        step('media','scripts/check_media.py',proj/'renders/final.mp4','--duration',meta['end'],'--loudness','--output',proj/'review/media.json')
        report.update(status='technical_complete_needs_subjective_review',final='renders/final.mp4',
                      visual_action_sync='checked_declared_conditions' if meta['checks'] else 'not_declared',
                      encoding_audio_sync='checked' if meta['score'] else 'legacy_not_checked')
    except (Exception,KeyboardInterrupt) as exc:
        report.update(status='failed',error=str(exc))
        raise
    finally:
        provenance.atomic_json(proj/'review/production.json',report)
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('project',type=Path);p.add_argument('--assets',nargs='*',choices=['geo','scene'],default=[])
    p.add_argument('--chunk',type=float,default=4);p.add_argument('--jobs',type=int,default=1);a=p.parse_args()
    produce(a.project,a.chunk,a.jobs,a.assets)
if __name__=='__main__':main()
