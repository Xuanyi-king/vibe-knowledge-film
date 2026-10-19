"""Encoded-video phone evidence, not an aesthetic or actual-platform pass.
python scripts/check_mobile.py <final.mp4> [--project <film>] [--times 3.2 5.35 8.5]
Default: 390/320px previews + a 720p CRF30 H.264 stress copy, audio copied.
Never replaces the master. Existing evidence survives a failed generation.
"""
import argparse
from fractions import Fraction
import hashlib,json,math,shutil,subprocess,sys,tempfile
from pathlib import Path
from PIL import Image,ImageDraw,ImageColor
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from engine import render,provenance

PROFILES={'720p-crf30':(1280,30),'540p-crf33':(960,33)}

def run(cmd):
    r=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=600)
    if r.returncode:raise RuntimeError(f'{cmd[0]} failed ({r.returncode}): {r.stderr[-1800:]}')
    return r.stdout

def probe(path):
    d=json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]))
    v=next((s for s in d['streams'] if s['codec_type']=='video'),None)
    if not v:raise ValueError('video stream required')
    a=next((s for s in d['streams'] if s['codec_type']=='audio'),None)
    return {'width':v['width'],'height':v['height'],'fps':float(Fraction(v['avg_frame_rate'])),
            'duration':float(v.get('duration',d['format']['duration'])),'frames':int(v['nb_frames']),
            'sar':v.get('sample_aspect_ratio','1:1'),'audio':a is not None,
            'audio_start':float(a.get('start_time',0)) if a else None,
            'audio_duration':float(a.get('duration',d['format']['duration'])) if a else None}

def sample_plan(end,fps,checks=(),events=(),times=None,limit=32):
    """Budget optional previews, never declared or recognized critical actions.

    Close optional motion samples merge at 0.5s. Required checks/explicit times
    stay on their exact encoded frames, even when they exceed the soft budget.
    Unknown action semantics must be declared through VK_CHECKS/VK_MOBILE_TIMES.
    """
    if not all(math.isfinite(x) and x>0 for x in (end,fps)):raise ValueError('positive finite duration/fps required')
    if not isinstance(limit,int) or isinstance(limit,bool) or limit<1:raise ValueError('sample budget must be a positive integer')
    last=math.ceil(end*fps)-1
    def frame(t):
        if not isinstance(t,(int,float)) or isinstance(t,bool) or not math.isfinite(t) or t<0 or t>=end:raise ValueError('sample times must be finite and within [0, video duration)')
        return min(last,math.floor(t*fps+.5))
    required={frame(c['time']) for c in checks}
    if times is not None:
        explicit=list(times)
        if not explicit:raise ValueError('sample times cannot be empty')
        required.update(frame(t) for t in explicit)
    optional={frame(end*k) for k in [.1,.3,.55,.85]} if times is None else set()
    excluded=0;end_markers=[]
    critical={'contact','impact','collision','reveal','discovery','computed','conclusion','hold','observation','reading','subtitle'}
    for e in events:
        action=str(e.get('action','')).lower()
        if not action:continue
        words=set(action.replace('_','-').split('-'))
        if words & critical:
            if e['start']==end:end_markers.append(e.get('id'))
            required.add(frame(min(e['start'],last/fps)))
            if words & {'hold','reading','subtitle'} and e.get('end',e['start'])>e['start']:
                required.add(frame((e['start']+e['end'])/2))
        elif (e.get('sound') or {}).get('track')=='music' or action in {'note','music'}:excluded+=1
        elif times is None:optional.add(frame((e['start']+e.get('end',e['start']))/2))
    merged=[];near=[];radius=max(1,round(.5*fps))
    for f in sorted(optional-required):
        if any(abs(f-r)<radius for r in required) or (merged and f-merged[-1]<radius):near.append(f)
        else:merged.append(f)
    slots=max(0,limit-len(required))
    chosen=merged if len(merged)<=slots else [merged[math.floor((i+.5)*len(merged)/slots)] for i in range(slots)]
    return {'frames':sorted(required|set(chosen)),'required_frames':sorted(required),'optional_budget':limit,
            'required_exceeds_budget':len(required)>limit,'merged_optional_frames':near,
            'omitted_optional_frames':sorted(set(merged)-set(chosen)),'excluded_music_events':excluded,'end_marker_events':end_markers,
            'policy':'exact declared/critical frames; optional 0.5s merge and distributed soft budget; no aesthetic pass'}

def sample_frames(end,fps,checks=(),events=(),times=None):
    return sample_plan(end,fps,checks,events,times)['frames']

def extract_frames(video,frames,folder,variant):
    """One presentation-order decode per input; n is the encoded frame index.

    No timestamp seeking, fps conversion or keyframe approximation. PNG outputs
    are ordinal selected frames, checked before they are associated with n.
    """
    if not frames or any(not isinstance(f,int) or isinstance(f,bool) or f<0 for f in frames) or frames!=sorted(set(frames)):
        raise ValueError('frame indices must be nonnegative, unique and sorted')
    folder=Path(folder);pattern=folder/f'.{variant}-batch-%06d.png'
    expression='select='+('+'.join(f'eq(n\\,{f})' for f in frames))
    script=folder/f'.{variant}-select.txt'
    # Keep even a large explicit list below Windows command-line limits.
    if len(expression)>4096:
        script.write_text(expression,encoding='utf-8');filter_args=['-filter_script:v',str(script)]
    else:filter_args=['-vf',expression]
    try:
        run(['ffmpeg','-v','error','-y','-i',str(video),'-an','-sn','-dn',*filter_args,
             '-fps_mode','passthrough','-frames:v',str(len(frames)),'-start_number','0',str(pattern)])
    finally:script.unlink(missing_ok=True)
    files=[folder/f'.{variant}-batch-{i:06d}.png' for i in range(len(frames))]
    if not all(f.is_file() for f in files):raise RuntimeError('frame extraction incomplete; evidence not published')
    return files

def contrast(a,b):
    def lum(s):
        rgb=ImageColor.getrgb(s)
        if len(rgb)==4 and rgb[3]!=255:raise ValueError('transparent color')
        rgb=[v/255 for v in rgb[:3]]
        rgb=[x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in rgb]
        return sum(a*b for a,b in zip(rgb,[.2126,.7152,.0722]))
    try:x,y=sorted([lum(a),lum(b)]);return (y+.05)/(x+.05)
    except (ValueError,TypeError,AttributeError):return None

def layout_risks(items,width,source_width,source_height):
    risks=[]
    for d in items:
        style=d['style'];importance=d.get('importance','supporting');alpha=style.get('a',1)
        if alpha<=.01:continue
        px=style['size']*width/source_width
        essential=importance=='essential'
        minimum=14 if d.get('role') in {'caption','title','concept','number'} else 12
        row={'text':d['text'],'role':d.get('role'),'importance':importance,'effective_px':round(px,3)}
        if (essential and px<minimum-.001) or (importance=='supporting' and px<11):
            risks.append({**row,'kind':'small-essential-text' if essential else 'small-supporting-text','minimum_px':minimum if essential else 11})
        if min(d['left'],d['top'])<0 or d['left']+d['width']>source_width or d['top']+d['height']>source_height:
            risks.append({**row,'kind':'out-of-frame'})
        if d.get('background'):
            ratio=contrast(style['color'],d['background'])
            if ratio is None:risks.append({**row,'kind':'contrast-metadata-unverified'})
            elif ratio<4.5:risks.append({**row,'kind':'declared-low-contrast','ratio':round(ratio,2),'scope':'author-declared colors; actual image/opacity not inferred'})
        if essential and style.get('blur',0)>0:risks.append({**row,'kind':'essential-blur-review'})
        if essential and abs(style.get('track',0))>style['size']*.2:
            risks.append({**row,'kind':'wide-tracking-review'})
    return risks

def audio_hash(path):
    return run(['ffmpeg','-v','error','-i',str(path),'-map','0:a:0','-c:a','copy','-f','hash','-hash','sha256','-']).strip()

def safe_output(video,output,project=None):
    raw=Path(output)
    if raw.is_symlink():raise ValueError('mobile evidence output cannot be a symlink')
    out=raw.resolve();video=Path(video).resolve();engine=render.ENGINE.resolve()
    if video.is_relative_to(out):raise ValueError('output cannot contain the master')
    if out.is_relative_to(engine) or engine.is_relative_to(out):raise ValueError('output cannot overlap engine inputs')
    if project:
        project=Path(project).resolve()
        if project.is_relative_to(out):raise ValueError('review output cannot replace the project')
        if out.is_relative_to(project):
            rel=out.relative_to(project)
            if len(rel.parts)<2 or rel.parts[0] not in {'review','renders'}:
                raise ValueError('project-local mobile output must be a dedicated review/ or renders/ subfolder, never source/assets/audio')
    if out.exists():
        try:
            marker=json.loads((out/'report.json').read_text(encoding='utf-8'))
            owned=marker.get('producer')=='vk-mobile-qa' and marker.get('version')==1
        except (OSError,ValueError,AttributeError):owned=False
        if not owned:raise ValueError('existing output is not owned mobile QA evidence; choose a new empty path')
    return out

def review_video(video,output,times=None,widths=(390,320),profile='720p-crf30',layouts=None,context=None,validate=None):
    video=Path(video).resolve();output=safe_output(video,output)
    if profile not in PROFILES:raise ValueError('unknown stress profile; no official platform profile is provided')
    if not widths or any(not isinstance(w,int) or isinstance(w,bool) or w<160 or w>1920 for w in widths):raise ValueError('preview widths must be integers between 160 and 1920')
    meta=probe(video)
    if abs(meta['width']/meta['height']-16/9)>.001 or meta['sar'] not in {'1:1','N/A'}:raise ValueError('mobile preview currently requires square-pixel 16:9 video; no automatic crop/stretch')
    plan=sample_plan(meta['duration'],meta['fps'],times=times);frames=plan['frames']
    before=provenance.digest(video);output.parent.mkdir(parents=True,exist_ok=True)
    stage=Path(tempfile.mkdtemp(prefix='.mobile-',dir=output.parent));backup=None
    try:
        stress=stage/'stress.mp4';target,crf=PROFILES[profile]
        sw=(min(meta['width'],target)//32)*32;sh=sw*9//16
        run(['ffmpeg','-v','error','-y','-i',str(video),'-map','0:v:0','-map','0:a?',
             '-vf',f'scale={sw}:{sh}:flags=lanczos','-c:v','libx264','-preset','veryfast','-crf',str(crf),
             '-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',str(stress)])
        sm=probe(stress)
        if sm['frames']!=meta['frames'] or abs(sm['fps']-meta['fps'])>.001 or abs(sm['duration']-meta['duration'])>.001:raise RuntimeError('stress encoding changed video timing')
        same_audio=audio_hash(video)==audio_hash(stress) if meta['audio'] and sm['audio'] else None
        if meta['audio']!=sm['audio'] or same_audio is False:raise RuntimeError('stress encoding lost or changed audio payload')
        if meta['audio'] and (abs(meta['audio_start']-sm['audio_start'])>.001 or abs(meta['audio_duration']-sm['audio_duration'])>.001):raise RuntimeError('stress encoding changed audio timing')
        report={'producer':'vk-mobile-qa','version':1,'status':'needs_visual_review','actual_platform_verified':False,'video_sha256':before,'video':meta,
                'layout_scope':'only registered type() items; legacy/unregistered text remains unverified',
                'simulation':{**sm,'profile':profile,'crf':crf,'preset':'veryfast','audio':'stream copy','audio_payload_identical':same_audio,
                              'note':'compression pressure test, not Douyin parameters or observed platform output','sha256':provenance.digest(stress)},
                'widths':list(widths),'frames':[],'sampling':plan,'extraction':'one exact select(n) pass per input; no timestamp seeking','sheets':[],'unverified':['object recognition','text occlusion','comfortable reading/hold time','actual local background contrast','aesthetic quality','actual Douyin transcode']}
        if not layouts:report['unverified'].append('text layout unavailable')
        extracted={variant:extract_frames(src,frames,stage,variant) for variant,src in [('master',video),('stress',stress)]}
        for i,frame in enumerate(frames):
            if i%24==0:sheets={w:Image.new('RGB',(w*2,(round(w*9/16)+24)*min(24,len(frames)-i)),'#202426') for w in widths}
            row={'frame':frame,'time':frame/meta['fps'],'previews':{},'layout_risks':{}}
            for variant,src in [('master',video),('stress',stress)]:
                full=extracted[variant][i]
                with Image.open(full) as image:
                    for w in widths:
                        thumb=image.convert('RGB').resize((w,round(w*9/16)),Image.Resampling.LANCZOS)
                        name=f'{variant}-{frame:06d}-{w}.png';thumb.save(stage/name)
                        row['previews'][f'{variant}-{w}']=name
                        sheet=sheets[w];y=(i%24)*(thumb.height+24);sheet.paste(thumb,(0 if variant=='master' else w,y+24))
                        ImageDraw.Draw(sheet).text((8 if variant=='master' else w+8,y+5),f'{variant} {frame/meta["fps"]:.3f}s / {w}px',fill='white')
                full.unlink()
            if layouts:
                row['layout_count']=len(layouts.get(frame,[]))
                for w in widths:row['layout_risks'][str(w)]=layout_risks(layouts.get(frame,[]),w,meta['width'],meta['height'])
            report['frames'].append(row)
            if i%24==23 or i==len(frames)-1:
                for w,sheet in sheets.items():
                    name=f'phone-{w}'+('' if i<24 else f'-{i//24+1:03d}')+'.png'
                    sheet.save(stage/name);report['sheets'].append(name)
        if provenance.digest(video)!=before:raise RuntimeError('master changed during mobile QA; evidence not published')
        if validate:validate()
        report.update(context or {})
        (stage/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
        if output.exists():
            backup=Path(tempfile.mkdtemp(prefix='.mobile-old-',dir=output.parent));backup.rmdir();output.replace(backup)
        try:stage.replace(output)
        except OSError:
            if backup:backup.replace(output);backup=None
            raise
        if backup:shutil.rmtree(backup)
        return report
    finally:
        if stage.exists():shutil.rmtree(stage)

def check_project(proj,video,output,times=None,widths=(390,320),profile='720p-crf30'):
    proj=Path(proj).resolve();video=Path(video).resolve()
    output=safe_output(video,output,proj)
    spec=json.loads((proj/'audio/events.json').read_text(encoding='utf-8'))
    sources=provenance.validate_events(proj,spec)
    provenance.validate_video(video,spec,sources,kind='final')
    layouts={};selection=None
    def go(pg):
        nonlocal times
        nonlocal selection
        d=pg.evaluate('({times:window.VK_MOBILE_TIMES||null,checks:window.VK_CHECKS?.list()||[],events:window.VK_SCORE?.json().events||[]})')
        selection=sample_plan(spec['end'],spec.get('fps',30),d['checks'],d['events'],times if times is not None else d['times']);frames=selection['frames']
        times=[f/spec.get('fps',30) for f in frames]
        for f,t in zip(frames,times):
            render.shot(pg,t)
            if pg._vk_remote_assets or pg._vk_generated_assets:raise RuntimeError('mobile layout requires tracked local scene inputs')
            layouts[f]=pg.evaluate('window.VK_LAYOUT?.() || []')
    render.with_page(proj,go);provenance.stable(proj,sources)
    def validate():
        provenance.stable(proj,sources);provenance.validate_video(video,spec,sources,kind='final')
    result=review_video(video,output,times,widths,profile,layouts if any(layouts.values()) else None,
        context={'input_sha256':provenance.identity(sources),'events_sha256':provenance.identity(spec),'sampling':selection},validate=validate)
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('video',type=Path);p.add_argument('--project',type=Path)
    p.add_argument('--output',type=Path);p.add_argument('--times',nargs='+',type=float);p.add_argument('--widths',nargs='+',type=int,default=[390,320])
    p.add_argument('--profile',choices=list(PROFILES),default='720p-crf30');a=p.parse_args()
    try:
        out=a.output or a.video.parent/'mobile-review'
        r=check_project(a.project,a.video,out,a.times,a.widths,a.profile) if a.project else review_video(a.video,out,a.times,a.widths,a.profile)
        print(json.dumps({'status':r['status'],'output':str(out),'frames':len(r['frames']),'video_sha256':r['video_sha256']},indent=2));return 0
    except Exception as exc:print(f'mobile QA failed: {exc}',file=sys.stderr);return 1
if __name__=='__main__':sys.exit(main())
