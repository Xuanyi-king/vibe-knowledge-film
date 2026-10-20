"""Prepare licensed music clips/anchors for the existing VK_SCORE sample path.
python scripts/prepare_music.py <project> [--config <project>/music.json]
No config/eligible signature source => original fallback, never an illegal download.
Run during preparation; generated assets/music-plan.mjs validates source bytes once
per page initialization, never analyzes DSP during seek().
"""
import argparse,hashlib,json,math,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.analyze_music import analyze_file
from engine.render_cache import digest,atomic_json
from scripts import signature_music

def finite(x):return isinstance(x,(float,int)) and not isinstance(x,bool) and math.isfinite(x)

def prepare(project,config=None):
    project=Path(project).resolve();canonical=project/'music.json'
    if canonical.exists():
        config_sha=digest(canonical)
        saved=json.loads(canonical.read_text(encoding='utf-8'))
        if config is not None and saved!=config:raise ValueError('save the edited config to project/music.json before preparation')
        cfg=saved
    else:
        cfg=config if config is not None else {'mode':'signature'}
        atomic_json(canonical,cfg);config_sha=digest(canonical)
    mode=cfg.get('mode','signature')
    if mode not in {'signature','original','custom'}:raise ValueError('music mode must be signature/original/custom')
    end=cfg.get('end')
    if end is not None and (not finite(end) or end<=0):raise ValueError('film end must be positive seconds')
    rights=cfg.get('rights',{});scope=rights.get('scope','unavailable')
    locked='signature' in cfg
    if locked and (mode!='signature' or not isinstance(cfg['signature'],dict) or cfg['signature'].get('required') is not True or scope!='embed'):
        raise ValueError('signature blocked: required master cannot downgrade or use platform-only music')
    result={'version':1,'config_sha256':config_sha,'selected':'original','source':None,'events':[],'anchors':{},'reason':'no eligible signature asset; compose/use licensed original music',
            'identity_status':'song identity not inferred from filename, BPM or user label','claimed_track':cfg.get('track'),
            'rights':rights,'rights_status':'user-declared scope; legal permission is not independently verified'}
    src=(project/cfg['src']).resolve() if cfg.get('src') else None
    if mode!='original' and scope=='platform-only':
        # No source bytes or sample events are embedded. Platform alignment is a cue,
        # not a claim that its library license permits arbitrary export or editing.
        result.update(selected='platform-later',reason='platform library only; export SFX-only and add authorized music on platform',
                      platform_cues=cfg.get('clips',[]),cue_status='user/editor supplied; platform version and alignment require verification')
    elif mode!='original' and src and src.is_file() and scope=='embed':
        if not src.is_relative_to(project) or src.is_symlink():raise ValueError('embeddable music must be a local project asset copy')
        if not rights.get('statement'):raise ValueError('music needs a source/license or user authorization statement')
        source_sha=digest(src)
        if cfg.get('source_sha256')!=source_sha:raise ValueError('music source fingerprint missing/changed; analyze then review/update config before preparation')
        if end is None:raise ValueError('music clip plan needs film end in seconds')
        if locked:
            analysis,clips,metadata=signature_music.resolve(project,cfg,source_sha);result.update(metadata)
        else:
            analysis=analyze_file(src,project/'review/music/analysis.json',cfg.get('annotations'));clips=cfg.get('clips',[])
        ids={};events=[];used=[]
        if not clips:raise ValueError('external music needs explicit clips; no automatic loop')
        for c in clips:
            name=c.get('id');start=c.get('start');trim=c.get('source_in');duration=c.get('duration')
            if not name or name in ids or not all(finite(x) for x in [start,trim,duration]) or min(start,trim)<0 or duration<=0 or start+duration>end or trim+duration>analysis['duration']+.00001:raise ValueError('clip IDs/times/source range invalid')
            fi=c.get('fade_in',min(.03,duration/4));fo=c.get('fade_out',min(.1,duration/4));gain=c.get('gain',.25)
            if not all(finite(x) and x>=0 for x in [fi,fo]) or fi+fo>duration:raise ValueError('clip fade/gain invalid')
            if isinstance(gain,list):curve=signature_music.gain_curve(gain,duration,fi,fo)
            else:
                if not finite(gain) or gain<0:raise ValueError('clip fade/gain invalid')
                points={0:0 if fi else gain,fi:gain,duration-fo:gain,duration:0 if fo else gain}
                curve=[[t,g] for t,g in sorted(points.items())]
            reuse=any(min(trim+duration,b)>max(trim,a)+1e-6 for a,b in used)
            if reuse and not cfg.get('allow_source_reuse',False):raise ValueError('repeated source needs explicit permission/review; no automatic looping')
            if reuse and not rights.get('allows_loop'):raise ValueError('source reuse requires loop permission declaration')
            used.append((trim,trim+duration));ids[name]={**c,'fade_in':fi,'fade_out':fo}
            events.append({'id':'music-'+name,'start':start,'duration':duration,'action':'music',
                'sound':{'kind':'sample','src':src.relative_to(project).as_posix(),'trim':trim,'track':'music',
                         'license':rights['statement'],'gain':curve}})
        ordered=sorted(ids.values(),key=lambda c:c['start'])
        for a,b in zip(ordered,ordered[1:]):
            overlap=a['start']+a['duration']-b['start']
            if overlap>min(a['fade_out'],b['fade_in'])+1e-6:raise ValueError('overlap exceeds planned crossfade; avoid unintended stacked music')
        if locked and not any(g>0 for e in events for _,g in e['sound']['gain']):
            raise ValueError('required signature cannot be an entirely silent music fallback')
        anchors={}
        for a in cfg.get('anchors',[]):
            c=ids.get(a.get('clip'));t=a.get('source_time');name=a.get('id')
            if not c or not name or name in anchors or not finite(t) or not c['source_in']<=t<c['source_in']+c['duration']:raise ValueError('anchor must name a clip and an included source time')
            anchors[name]=c['start']+t-c['source_in']
        result.update(selected=mode,reason='eligible user-declared embeddable source',source={'src':src.relative_to(project).as_posix(),'sha256':source_sha},
            events=events,anchors=anchors,analysis_identity=analysis['identity'],analysis_grid_verified=analysis['grid_verified'],
            mapping='film_seconds = clip.start + source_seconds - clip.source_in; no speed change',clips=clips)
        if digest(src)!=source_sha:raise RuntimeError('music source changed during preparation')
    elif mode=='custom' or locked:raise ValueError('required music fingerprint/source unavailable or rights do not allow embedding; no fallback')
    folder=project/'assets';folder.mkdir(parents=True,exist_ok=True)
    out=folder/'music-plan.json';loader=folder/'music-plan.mjs'
    # JSON is authoritative, loader pins its bytes. An interrupted pair fails closed.
    if digest(canonical)!=config_sha:raise RuntimeError('music config changed during preparation; prepare again')
    atomic_json(out,result)
    code=(Path(__file__).with_name('music_loader.mjs')).read_text(encoding='utf-8').replace('__PLAN_SHA__',digest(out))
    tmp=loader.with_suffix('.mjs.tmp');tmp.write_text(code,encoding='utf-8');tmp.replace(loader)
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('project',type=Path);p.add_argument('--config',type=Path);a=p.parse_args()
    config=a.config or a.project/'music.json'
    try:r=prepare(a.project,json.loads(config.read_text(encoding='utf-8')) if config.exists() else None)
    except Exception as exc:print(f'music preparation failed: {exc}',file=sys.stderr);return 1
    print(json.dumps({'selected':r['selected'],'reason':r['reason']},ensure_ascii=False));return 0
if __name__=='__main__':sys.exit(main())
