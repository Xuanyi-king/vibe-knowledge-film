"""Technical production entry after the Agent has authored a complete film.
python scripts/produce.py <project> [--assets geo scene] [--chunk 4] [--jobs 1]
Creative decisions and subjective review remain the Agent's responsibility.
"""
import argparse
import json
from pathlib import Path
import subprocess
import shutil
import tempfile
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from engine import render,provenance
ROOT=Path(__file__).resolve().parents[1]


def produce(proj,chunk=4,jobs=1,assets=()):
    proj=proj.resolve();(proj/'review').mkdir(parents=True,exist_ok=True)
    report={'status':'running','stages':[],'subjective_visual_review':'not_automated','subjective_listening':'not_automated'}
    provenance.atomic_json(proj/'review/production.json',report)
    backup=None
    saved=[]
    preserve_backup=False
    def checkpoint(name):
        report['active_stage']=name
        provenance.atomic_json(proj/'review/production.json',report)
    def step(name,script,*args):
        checkpoint(name)
        subprocess.run([sys.executable,str(ROOT/script),*map(str,args)],check=True)
        report['stages'].append(name)
    try:
        if (proj/'music.json').exists():step('music_preparation','scripts/prepare_music.py',proj)
        for asset in assets:
            if asset not in {'geo','scene'}:raise ValueError('supported optional assets: geo, scene')
            step('assets-'+asset,f'engine/get_{asset}_assets.py')
        step('fonts','engine/get_fonts.py')
        sources=provenance.source_files(proj)
        checkpoint('inspect')
        meta=render.with_page(proj,lambda pg:pg.evaluate('({end:END,fps:FPS,score:!!window.VK_SCORE,checks:window.VK_CHECKS?.list().length||0})'))
        report['film']=meta
        step('determinism','engine/render.py',proj,'--det')
        step('picture','engine/render.py',proj,'--resume',chunk,'--jobs',jobs)
        step('events','engine/render.py',proj,'--events')
        backup=Path(tempfile.mkdtemp(prefix='.vk-production-',dir=proj/'renders'))
        for item in [proj/'renders/final.mp4',provenance.sidecar(proj/'renders/final.mp4')]:
            if item.exists():
                dest=backup/item.name;shutil.copyfile(item,dest);saved.append((dest,item))
        report['previous_final_backup']=str(backup) if saved else None
        step('sound','engine/audio.py',proj,'--stems')
        step('mastering','scripts/master_audio.py',proj,*(() if meta['score'] else ('--legacy-source-only',)))
        if meta['score']:step('encoding_audio_sync','scripts/check_av.py',proj)
        if meta['checks']:step('declared_visual_action_sync','scripts/check_visual.py',proj,'--video',proj/'renders/final.mp4')
        step('media','scripts/check_media.py',proj/'renders/final.mp4','--duration',meta['end'],'--loudness','--output',proj/'review/media.json')
        step('mobile_evidence','scripts/check_mobile.py',proj/'renders/final.mp4','--project',proj,'--output',proj/'review/mobile')
        provenance.stable(proj,sources)
        spec=json.loads((proj/'audio/events.json').read_text(encoding='utf-8'))
        provenance.validate_events(proj,spec)
        final=provenance.validate_video(proj/'renders/final.mp4',spec,sources,kind='final')
        reports=[proj/'review/mobile/report.json']
        if meta['score']:reports.append(proj/'audio/sync.json')
        if meta['checks']:reports.append(proj/'review/visual-sync.json')
        for path in reports:
            if json.loads(path.read_text(encoding='utf-8')).get('video_sha256')!=final['sha256']:
                raise RuntimeError('final changed after sync checks; rerun production')
        report.update(input_sha256=provenance.identity(sources),video_sha256=final['sha256'],events_sha256=provenance.identity(spec))
        report.update(status='technical_complete_needs_subjective_review',final='renders/final.mp4',
                      mobile_review='encoded_390_320_and_pressure_evidence_needs_review',
                      visual_action_sync='checked_declared_conditions' if meta['checks'] else 'not_declared',
                      encoding_audio_sync='checked' if meta['score'] else 'legacy_not_checked')
    except (Exception,KeyboardInterrupt) as exc:
        report.update(status='failed',error=str(exc))
        if saved:
            try:
                for source,dest in saved:source.replace(dest)
                stamp=provenance.sidecar(proj/'renders/final.mp4')
                if not any(dest==stamp for _,dest in saved):stamp.unlink(missing_ok=True)
                report['previous_final_restored']=True
            except OSError as restore_error:
                preserve_backup=True
                report['restore_error']=str(restore_error)
        raise
    finally:
        if backup and not preserve_backup:
            shutil.rmtree(backup)
            report['previous_final_backup']=None
        provenance.atomic_json(proj/'review/production.json',report)
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('project',type=Path);p.add_argument('--assets',nargs='*',choices=['geo','scene'],default=[])
    p.add_argument('--chunk',type=float,default=4);p.add_argument('--jobs',type=int,default=1);a=p.parse_args()
    produce(a.project,a.chunk,a.jobs,a.assets)
if __name__=='__main__':main()
