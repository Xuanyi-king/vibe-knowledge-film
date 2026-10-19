"""Technical production entry after the Agent has authored a complete film.
python scripts/produce.py <project> [--assets geo scene] [--chunk 4] [--jobs 1]
Creative decisions and subjective review remain the Agent's responsibility.
"""
import argparse
import json
import math
import os
import platform
from importlib.metadata import version
from time import perf_counter
from pathlib import Path
import subprocess
import shutil
import tempfile
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from engine import render,provenance
ROOT=Path(__file__).resolve().parents[1]


def output_snapshot(proj, paths):
    """Hash complete output groups, including their evidence files."""
    files={}
    for name in paths:
        path=proj/name
        if not path.exists():raise FileNotFoundError(path)
        if path.is_symlink():raise ValueError('generated evidence cannot be symlinked')
        for item in sorted(path.rglob('*')) if path.is_dir() else [path]:
            if item.is_symlink():raise ValueError('generated evidence cannot be symlinked')
            if item.is_file():files[item.relative_to(proj).as_posix()]=provenance.digest(item)
    return files


def reusable(proj, record, key):
    try:
        return (record.get('key')==key and bool(record.get('outputs')) and
                all((proj/name).resolve().is_relative_to(proj) and not (proj/name).is_symlink() and
                    provenance.digest(proj/name)==sha for name,sha in record['outputs'].items()))
    except (OSError,ValueError,TypeError,AttributeError):return False


def inspect(pg):
    if pg._vk_remote_assets or pg._vk_generated_assets:
        raise ValueError('production requires local assets outside audio/review/renders')
    meta=pg.evaluate('({end:END,fps:FPS,width:VK.W,height:VK.H,score:!!window.VK_SCORE,checks:window.VK_CHECKS?.list().length||0,scene:window.VK_SCENE_INFO||null})')
    meta['browser_version']=pg.context.browser.version
    return meta


def produce(proj,chunk=4,jobs=1,assets=(),mode='release',preview=()):
    if mode not in {'draft','standard','release'}:raise ValueError('unsupported production mode')
    if preview:
        if mode!='draft':raise ValueError('preview arguments require draft mode')
        flag,*values=preview
        if flag not in {'--stills','--sheet','--motion','--clip'}:raise ValueError('unsupported preview command')
        if flag=='--clip' and len(values)==3:
            if values.pop()!='draft':raise ValueError('draft clips must be named draft')
        if not values or any(not isinstance(v,(int,float)) or isinstance(v,bool) or
                             not math.isfinite(v) or v<0 for v in values):
            raise ValueError('preview times must be finite and nonnegative')
        if flag in {'--motion','--clip'} and (len(values)!=2 or values[1]<=values[0]):
            raise ValueError('preview range must have start before stop')
        preview=(flag,*values,*(('draft',) if flag=='--clip' else ()))
    if not math.isfinite(chunk) or chunk<=0 or jobs<1:raise ValueError('positive chunk and jobs required')
    proj=proj.resolve();(proj/'review').mkdir(parents=True,exist_ok=True)
    started=perf_counter()
    report={'status':'running','mode':mode,'reused':[],'timings':{},'stages':[],'subjective_visual_review':'not_automated','subjective_listening':'not_automated'}
    report_path=proj/('review/draft.json' if mode=='draft' else 'review/production.json')
    provenance.atomic_json(report_path,report)
    backup=None
    saved=[]
    preserve_backup=False
    def checkpoint(name):
        report['active_stage']=name
        provenance.atomic_json(report_path,report)
    def step(name,script,*args):
        checkpoint(name)
        tick=perf_counter()
        subprocess.run([sys.executable,str(ROOT/script),*map(str,args)],check=True)
        report['timings'][name]=round(perf_counter()-tick,4)
        report['stages'].append(name)
    try:
        if (proj/'music.json').exists():step('music_preparation','scripts/prepare_music.py',proj)
        for asset in assets:
            if asset not in {'geo','scene'}:raise ValueError('supported optional assets: geo, scene')
            step('assets-'+asset,f'engine/get_{asset}_assets.py')
        step('fonts','engine/get_fonts.py')
        if mode=='draft':
            step('preview','engine/render.py',proj,*(preview or ('--sheet',16)))
            report.update(status='preview_needs_review',preview=list(preview or ('--sheet',16)))
            return report
        sources=provenance.source_files(proj)
        checkpoint('inspect')
        tick=perf_counter()
        meta=render.with_page(proj,inspect)
        report['timings']['inspect']=round(perf_counter()-tick,4)
        report['film']=meta
        # Missing runtime metadata (e.g. test doubles) never permits reuse.
        runtime=None
        if meta.get('browser_version'):
            runtime=dict(platform=platform.platform(),python=sys.version,browser=os.environ.get('VK_BROWSER'),
                         software_gl=os.environ.get('VK_SOFTWARE_GL'),
                         packages={n:version(n) for n in ('numpy','scipy','Pillow','playwright')},
                         tools={n:subprocess.run([n,'-version'],check=True,capture_output=True,text=True,
                             encoding='utf-8',errors='replace').stdout for n in ('ffmpeg','ffprobe')})
        implementation={p.name:provenance.digest(p) for p in sorted((ROOT/'scripts').iterdir()) if p.suffix in {'.py','.mjs'}}
        implementation['requirements.txt']=provenance.digest(ROOT/'requirements.txt')
        key=provenance.identity(dict(sources=sources,film=meta,runtime=runtime,implementation=implementation,chunk=chunk,jobs=jobs))
        cache_path=proj/'review/production-cache.json'
        try:
            cache=json.loads(cache_path.read_text(encoding='utf-8'))
            if not isinstance(cache,dict):cache={}
        except (OSError,ValueError):cache={}
        build_reused=runtime is not None and reusable(proj,cache.get('standard',{}),key)
        if build_reused:
            report['reused'].append('standard')
        if not build_reused:
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
        provenance.stable(proj,sources)
        outputs=['audio','renders/raw.mp4',str(provenance.sidecar(Path('renders/raw.mp4'))),
                 'renders/final.mp4',str(provenance.sidecar(Path('renders/final.mp4'))),
                 'review/media.json','review/mastering.json']
        if meta['score']:outputs.append('audio/sync.json')
        if meta['checks']:outputs.extend(['review/visual-sync.json','review/visual'])
        if runtime is not None and not build_reused:
            cache={'standard':{'key':key,'outputs':output_snapshot(proj,outputs)}}
        if mode=='release':
            mobile_key=provenance.identity([key,provenance.digest(proj/'renders/final.mp4')])
            if runtime is not None and reusable(proj,cache.get('mobile',{}),mobile_key):
                report['reused'].append('mobile_evidence')
            else:
                step('mobile_evidence','scripts/check_mobile.py',proj/'renders/final.mp4','--project',proj,'--output',proj/'review/mobile')
                if runtime is not None:
                    cache['mobile']={'key':mobile_key,'outputs':output_snapshot(proj,['review/mobile'])}
        provenance.stable(proj,sources)
        spec=json.loads((proj/'audio/events.json').read_text(encoding='utf-8'))
        provenance.validate_events(proj,spec)
        final=provenance.validate_video(proj/'renders/final.mp4',spec,sources,kind='final')
        reports=[proj/'review/mobile/report.json'] if mode=='release' else []
        if meta['score']:reports.append(proj/'audio/sync.json')
        if meta['checks']:reports.append(proj/'review/visual-sync.json')
        for path in reports:
            if json.loads(path.read_text(encoding='utf-8')).get('video_sha256')!=final['sha256']:
                raise RuntimeError('final changed after sync checks; rerun production')
        if runtime is not None:provenance.atomic_json(cache_path,cache)
        report.update(input_sha256=provenance.identity(sources),video_sha256=final['sha256'],events_sha256=provenance.identity(spec))
        report.update(status='technical_complete_needs_subjective_review' if mode=='release' else 'standard_complete_needs_release_and_review',final='renders/final.mp4',
                      mobile_review='encoded_390_320_and_pressure_evidence_needs_review' if mode=='release' else 'deferred_to_release',
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
        report['elapsed_seconds']=round(perf_counter()-started,4)
        provenance.atomic_json(report_path,report)
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('project',type=Path);p.add_argument('--assets',nargs='*',choices=['geo','scene'],default=[])
    p.add_argument('--chunk',type=float,default=4);p.add_argument('--jobs',type=int,default=1)
    p.add_argument('--mode',choices=['draft','standard','release'],default='release')
    group=p.add_mutually_exclusive_group()
    group.add_argument('--stills',nargs='+',type=float)
    group.add_argument('--motion',nargs=2,type=float)
    group.add_argument('--clip',nargs=2,type=float)
    a=p.parse_args();preview=()
    for name in ('stills','motion','clip'):
        values=getattr(a,name)
        if values is not None:
            if a.mode!='draft':p.error('preview arguments require --mode draft')
            if any(not math.isfinite(v) or v<0 for v in values):p.error('preview times must be finite and nonnegative')
            if name!='stills' and values[1]<=values[0]:p.error('preview stop must follow start')
            preview=(f'--{name}',*values,*(('draft',) if name=='clip' else ()))
    produce(a.project,a.chunk,a.jobs,a.assets,a.mode,preview)
if __name__=='__main__':main()
