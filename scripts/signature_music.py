"""Strict prepared-index policy, resolving only existing music.json clip fields.
No audio synthesis, beat guessing, rendering clock, or song substitution.
"""
import hashlib,json,math
from pathlib import Path
from scripts.analyze_music import analysis_identity
from engine.render_cache import digest

def number(x):return isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(x)

def binding(project,item):
    if not isinstance(item,dict) or not item.get('src') or not item.get('sha256'):
        raise ValueError('signature blocked: missing index/rights fingerprint')
    raw=project/item['src'];path=raw.resolve()
    if not path.is_relative_to(project) or any(p.is_symlink() for p in [raw,*raw.parents] if p!=project.parent):
        raise ValueError('signature bindings must be local non-symlink assets')
    if not path.is_file() or digest(path)!=item['sha256']:raise ValueError('signature binding fingerprint missing/changed')
    return path,{'src':path.relative_to(project).as_posix(),'sha256':item['sha256']}

def resolve(project,cfg,source_sha):
    lock=cfg['signature'];rights=cfg.get('rights',{})
    if (not isinstance(lock,dict) or lock.get('required') is not True or not lock.get('id') or
        cfg.get('mode')!='signature' or rights.get('scope')!='embed' or rights.get('allows_edit') is not True):
        raise ValueError('signature blocked: required master needs signature mode and documented embed/edit rights')
    path,index_binding=binding(project,{'src':lock.get('index'),'sha256':lock.get('index_sha256')})
    _,rights_binding=binding(project,rights.get('evidence'))
    index=json.loads(path.read_text(encoding='utf-8'));annotations=index.get('annotations') or {}
    payload={k:v for k,v in index.items() if k!='payload_sha256'}
    integrity=hashlib.sha256(json.dumps(payload,sort_keys=True,allow_nan=False).encode()).hexdigest()
    if (index.get('payload_sha256')!=integrity or index.get('source_sha256')!=source_sha or
        annotations.get('source_sha256')!=source_sha or index.get('identity')!=analysis_identity(source_sha,annotations)[0]):
        raise ValueError('signature index fingerprint stale; re-analyze source/algorithm/annotations')
    master=annotations.get('master',{})
    if not index.get('source_format',{}).get('sample_rate'):raise ValueError('signature index needs original source format; re-analyze')
    if (master.get('id')!=lock['id'] or master.get('kind') not in {'independent-music','separated-music'} or
        master.get('music_only') is not True or not master.get('reviewer') or not master.get('evidence') or
        (master.get('kind')=='separated-music' and master.get('residual_sfx_checked') is not True)):
        raise ValueError('signature blocked: independent music identity/listening evidence required; reference mix is not a master')
    sections=annotations.get('sections',[]);ids=set()
    for s in sections:
        if (not s.get('id') or s['id'] in ids or not all(number(s.get(k)) for k in ['start','end']) or
            not 0<=s['start']<s['end']<=index['duration'] or not isinstance(s.get('roles'),list)):
            raise ValueError('signature section boundaries/roles invalid')
        ids.add(s['id'])
        cuts=s.get('cuts',[s['start'],s['end']])
        if (len(cuts)<2 or any(not number(t) or not s['start']<=t<=s['end'] for t in cuts) or
            any(b<=a for a,b in zip(cuts,cuts[1:]))):raise ValueError('signature reviewed cuts invalid')
    clips=[];silences=[];used=[]
    for c in cfg.get('clips',[]):
        if c.get('silence') is True:
            if (not c.get('reason') or not all(number(c.get(k)) for k in ['start','duration']) or
                not 0<=c['start']<c['start']+c['duration']<=cfg['end']):raise ValueError('intentional music silence needs reason and valid times')
            silences.append(c);continue
        if not (c.get('role') or c.get('section') or ('source_in' in c and 'duration' in c)):
            raise ValueError('signature clip needs a narrative role, named section or explicit reviewed cut pair')
        choices=[]
        for s in sections:
            if s.get('verified') is not True or (c.get('section') and c['section']!=s['id']) or (c.get('role') and c['role'] not in s['roles']):continue
            cuts=s.get('cuts',[s['start'],s['end']])
            for i,a in enumerate(cuts):
                for b in cuts[i+1:]:
                    if 'source_in' in c and (not number(c['source_in']) or abs(c['source_in']-a)>1e-6):continue
                    if 'duration' in c and (not number(c['duration']) or abs(c['duration']-(b-a))>1e-6):continue
                    if not number(c.get('start')) or not 0<=c['start']<=cfg['end']-(b-a):continue
                    reused=any(min(b,y)>max(a,x)+1e-6 for x,y in used)
                    choices.append((reused,-(b-a),s['id'],a,b))
        if not choices:raise ValueError('no reviewed section/cut span fits this narrative clip; author a valid plan, never guess a phrase')
        reused,_,section,a,b=min(choices)
        if reused and (cfg.get('allow_source_reuse') is not True or rights.get('allows_loop') is not True):
            raise ValueError('source reuse requires explicit plan and actual loop permission evidence')
        used.append((a,b))
        clips.append({**c,'section':section,'source_in':a,'duration':b-a})
    if not clips:raise ValueError('required signature needs actual music clips, not a silent fallback')
    for gap in silences:
        if any(min(gap['start']+gap['duration'],c['start']+c['duration'])>max(gap['start'],c['start'])+1e-6 for c in clips):
            raise ValueError('intentional music silence overlaps a music clip; use clip gain automation for ducking')
    return index,clips,{'signature':{'id':lock['id'],'index_sha256':index_binding['sha256']},
                        'bindings':[index_binding,rights_binding],'silences':silences}

def gain_curve(value,duration,fade_in=0,fade_out=0):
    if (not isinstance(value,list) or len(value)<2 or any(not isinstance(p,list) or len(p)!=2 or
        not all(number(x) for x in p) or not 0<=p[0]<=duration or p[1]<0 for p in value) or
        any(b[0]<=a[0] for a,b in zip(value,value[1:])) or value[0]!=[0,0] or value[-1]!=[duration,0]):
        raise ValueError('clip gain curve needs increasing finite relative times and zero-valued endpoints at 0/duration')
    positive=[t for t,g in value if g>0]
    if positive and (positive[0]<fade_in-1e-6 or positive[-1]>duration-fade_out+1e-6):
        raise ValueError('gain curve must honor declared fade_in/fade_out before crossfading')
    return value
