#!/usr/bin/env python3
"""One-film recovery: persistent clips, serial rendering, checked reuse; no source edits."""
from pathlib import Path
import datetime, hashlib, json, os, subprocess, sys, time

PROJECT=Path(__file__).resolve().parent
ROOT=PROJECT.parents[1]
EVIDENCE=ROOT/'evidence/descent_studio'
OUT=PROJECT/'renders'
STATE=EVIDENCE/'recovery_state.json'
SEGMENTS=[(0,2),(2,6),(6,10),(10,14),(14,18),(18,22),(22,26),(26,30),(30,34),(34,36)]
ENV=dict(os.environ)
if not ENV.get('VK_BROWSER') and Path('/usr/bin/chromium').is_file():
    ENV['VK_BROWSER']='/usr/bin/chromium'

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def hashes(): return {n:hashlib.sha256((PROJECT/n).read_bytes()).hexdigest() for n in ['film.js','physics.js','index.html']}
def save():
    tmp=STATE.with_suffix('.tmp');tmp.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf-8');tmp.replace(STATE)
def record(message): print(now(),message,flush=True)
def probe(path,frames):
    if not path.is_file(): return None
    p=subprocess.run(['ffprobe','-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=nb_read_frames,width,height,avg_frame_rate,codec_name,pix_fmt','-of','json',str(path)],capture_output=True,text=True)
    if p.returncode:return None
    try:
        s=json.loads(p.stdout)['streams'][0]
        assert int(s['nb_read_frames'])==frames and s['width']==1920 and s['height']==1080 and s['avg_frame_rate']=='30/1' and s['codec_name']=='h264' and s['pix_fmt']=='yuv420p'
        return s
    except (ValueError,KeyError,IndexError,AssertionError): return None

def execute(label,cmd):
    assert hashes()==state['source_sha256'],'Frozen film source changed'
    entry={'label':label,'started_utc':now(),'command':cmd,'status':'running'};state['operations'].append(entry);save()
    record('START '+label);start=time.monotonic()
    log=EVIDENCE/('recovery_'+label+'.log')
    with log.open('a') as f:
        p=subprocess.run(cmd,env=ENV,stdout=f,stderr=subprocess.STDOUT)
    entry.update(finished_utc=now(),elapsed_seconds=time.monotonic()-start,returncode=p.returncode,status='complete' if p.returncode==0 else 'failed');save()
    record('END '+label+' '+str(p.returncode))
    if p.returncode:raise RuntimeError(f'{label} failed; see {log}')

EVIDENCE.mkdir(exist_ok=True);OUT.mkdir(exist_ok=True)
if STATE.exists():
    state=json.loads(STATE.read_text(encoding='utf-8'));assert hashes()==state['source_sha256'],'Source changed since first recovery'
    for op in state['operations']:
        if op['status']=='running':op.update(status='interrupted',interruption_observed_utc=now(),elapsed_seconds=None)
    state['resumed_utc'].append(now())
else:
    state={'started_utc':now(),'resumed_utc':[],'source_sha256':hashes(),'operations':[],'segments':{},'prior_failed_render':{'log':'interrupted_full_render.log','last_logged_progress':'150/360 in one worker','exact_runtime_seconds':None,'note':'Environment interrupted the monotonic timer; no completed clips survived. Partial bytes and ffprobe failures are in interrupted_render_status.json.'}}
save()
try:
    first=OUT/'seg00.mp4'
    record('Waiting for parent-owned seg00 (60 frames); this script does not render seg00.')
    wait_start=time.monotonic()
    while not probe(first,60):
        if time.monotonic()-wait_start>1800:raise RuntimeError('seg00 not valid after 30 minutes; parent-owned render may have stopped')
        time.sleep(5)
    for i,(a,b) in enumerate(SEGMENTS):
        name=f'seg{i:02d}';path=OUT/(name+'.mp4');expected=round((b-a)*30)
        valid=probe(path,expected)
        if valid:
            state['segments'][name]={'start':a,'end':b,'expected_frames':expected,'checked_utc':now(),'reused':True,'probe':valid};save();record('REUSE '+name);continue
        if i==0:raise RuntimeError('Parent-owned seg00 became invalid')
        execute(name,[sys.executable,str(ROOT/'engine/render.py'),str(PROJECT),'--clip',str(a),str(b),name])
        valid=probe(path,expected)
        if not valid:raise RuntimeError(name+' failed frame/spec verification')
        state['segments'][name]={'start':a,'end':b,'expected_frames':expected,'checked_utc':now(),'reused':False,'probe':valid};save()
    listing=OUT/'recovery_concat.txt'
    listing.write_text(''.join(f"file 'seg{i:02d}.mp4'\n" for i in range(len(SEGMENTS))),encoding='utf-8')
    execute('concat',['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(listing),'-c','copy','-movflags','+faststart',str(OUT/'raw.mp4')])
    assert probe(OUT/'raw.mp4',1080),'Concat must be exactly1080 frames'
    execute('events',[sys.executable,str(ROOT/'engine/render.py'),str(PROJECT),'--events'])
    execute('audio',[sys.executable,str(ROOT/'engine/audio.py'),str(PROJECT)])
    assert probe(OUT/'final.mp4',1080),'Final must be exactly1080 frames'
    execute('check_media',[sys.executable,str(ROOT/'scripts/check_media.py'),str(OUT/'final.mp4'),'--duration','36','--output',str(EVIDENCE/'final_media_report.json')])
    times=[1.5,4.5,5.5,8.8,10.5,12.4,13.2,14.4,15.5,17,20.5,22.5,24.5,27.5,30,35.5]
    select='+'.join(f'eq(n\\,{round(t*30)})' for t in times)
    contact=EVIDENCE/'final_contact.png'
    execute('contact',['ffmpeg','-v','error','-y','-i',str(OUT/'final.mp4'),'-vf',f'select={select},scale=480:270,tile=4x4','-frames:v','1',str(contact)])
    from PIL import Image,ImageDraw,ImageFont
    im=Image.open(contact).convert('RGB');d=ImageDraw.Draw(im);font=ImageFont.truetype(str(ROOT/'engine/fonts/JetBrainsMono.ttf'),18)
    for i,t in enumerate(times):
        x=(i%4)*480;y=(i//4)*270+244;d.rectangle([x,y,x+100,y+26],fill='black');d.text((x+5,y+3),f'{t:.2f}s',font=font,fill='#ffe2a6')
    im.save(EVIDENCE/'final_contact.jpg',quality=94)
    state.update(status='complete',finished_utc=now(),successful_operation_seconds=sum(op.get('elapsed_seconds') or 0 for op in state['operations'] if op['status']=='complete'));save();record('ALL COMPLETE')
except BaseException as ex:
    state.update(status='failed',last_error=str(ex),last_error_utc=now());save();record('FAILED '+str(ex));raise
