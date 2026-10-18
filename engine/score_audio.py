"""Offline sample-clock renderer for VK_SCORE v1; no realtime audio backend.
All oscillators, filtered noise and room responses are original procedural audio.
"""
import hashlib
import math
from pathlib import Path
import subprocess
import numpy as np
from scipy.signal import butter, sosfilt, correlate, correlation_lags
try:
    from . import audio as A
except ImportError:
    import audio as A

SR=A.SR
TRACKS=('music','sfx','ambience')
MATERIALS={ # modal ratios, decay seconds, contact-noise cutoff
    'metal':([1,2.756,5.404,8.933],2.0,6500),
    'glass':([1,2.32,4.25,6.63],.85,9000),
    'wood':([1,2.8,5.1],.085,1800),
    'paper':([1,1.7,3.4],.025,3500),
    'felt':([1,2.3],.035,700),
}

def curve(points,t,default=1):
    if points is None:return np.full_like(t,default,dtype=float)
    if isinstance(points,(int,float)):
        if not math.isfinite(points):raise ValueError('non-finite automation')
        return np.full_like(t,points,dtype=float)
    p=np.asarray(points,dtype=float)
    if p.ndim!=2 or p.shape[1]!=2 or not np.isfinite(p).all() or np.any(np.diff(p[:,0])<=0):
        raise ValueError('automation requires increasing finite [time,value] keys')
    return np.interp(t,p[:,0],p[:,1])

def decode(path):
    r=subprocess.run(['ffmpeg','-v','error','-i',str(path),'-f','f64le','-ac','2','-ar',str(SR),'-'],check=True,capture_output=True,timeout=120)
    return np.frombuffer(r.stdout,dtype='<f8').reshape(-1,2).copy()

def voice(e,sr,root):
    p=e['sound'];kind=p['kind'];duration=e['end']-e['start']
    if duration<=0:raise ValueError(f"sound {e['id']} needs an explicit positive duration including its tail")
    n=round(duration*sr);t=np.arange(n)/sr
    rng=np.random.default_rng(int.from_bytes(hashlib.sha256(e['id'].encode()).digest()[:8],'little'))
    if kind=='sample':
        if not p.get('license'):raise ValueError('sample license/provenance required')
        path=(Path(root)/p['src']).resolve()
        if not path.is_relative_to(Path(root).resolve()) or not path.is_file():raise ValueError('sample must be a local project asset')
        raw=decode(path);offset=round(p.get('trim',0)*sr)
        if offset<0:raise ValueError('sample trim must be nonnegative')
        x=np.zeros((n,2));raw=raw[offset:offset+n];x[:len(raw)]=raw
    else:
        material=p.get('material',e.get('material','wood'))
        if material not in MATERIALS:raise ValueError(f'unsupported material {material}; use a licensed sample instead')
        ratios,tau,cutoff=MATERIALS[material]
        f=p.get('frequency',240)*2**(p.get('pitch',0)/12)
        noise=sosfilt(butter(2,min(p.get('cutoff',cutoff),sr*.45),fs=sr,output='sos'),rng.standard_normal(n))
        if kind=='impact':
            x=sum(np.sin(2*np.pi*f*r*t)*np.exp(-t/(tau/(1+.2*i)))/(1+i)**1.3 for i,r in enumerate(ratios) if f*r<sr*.45)
            x=(x*.24+noise*.35*np.exp(-t/.007))*np.minimum(1,t/.001)*e.get('intensity',1)
        elif kind=='friction':
            speed=curve(p.get('speed',e.get('speed',1)),t)
            # Grain envelopes and modulation differ from a one-shot oscillator.
            x=noise*(.55+.22*np.sin(2*np.pi*37*t)+.18*np.sin(2*np.pi*83*t))*np.sqrt(np.maximum(0,speed))*.24
        elif kind=='whoosh':
            x=noise*np.sin(np.pi*t/duration)**2*.16
        elif kind=='pluck':
            f=440*2**((p.get('midi',60)-69)/12)
            x=sum(np.sin(2*np.pi*f*k*t)*np.exp(-t/(.45/k))/(k*k) for k in range(1,6) if f*k<sr*.45)*.28*np.minimum(1,t/.004)
        else:raise ValueError(f'unknown sound kind {kind}')
        pan=curve(p.get('pan',0),t)
        if np.any(np.abs(pan)>1):raise ValueError('pan must be in [-1,1]')
        x=np.stack([x*np.cos((pan+1)*np.pi/4),x*np.sin((pan+1)*np.pi/4)],1)
    if kind=='sample':
        pan=curve(p.get('pan',0),t)
        if np.any(np.abs(pan)>1):raise ValueError('pan must be in [-1,1]')
        # Stereo balance preserves the original image at center; hard pan mutes the opposite channel.
        x*=np.stack([np.cos(np.maximum(pan,0)*np.pi/2),np.cos(np.minimum(pan,0)*np.pi/2)],1)
        if p.get('pitch',0):raise ValueError('sample pitch shifting is not supported; supply a prepared source')
    if p.get('cutoff'):x=A.lowpass(x,p['cutoff'])
    x*=curve(p.get('gain',1),t)[:,None]
    # Micro-fades avoid a truncation click. No automatic long fade hiding contact.
    x*=np.minimum(1,t/.001)[:,None]*np.minimum(1,(duration-t)/.006)[:,None]
    if not np.isfinite(x).all():raise ValueError(f"non-finite sound {e['id']}")
    return x

def render(spec,root):
    if spec.get('version')!=1 or not math.isfinite(spec.get('end',0)) or spec['end']<=0:raise ValueError('VK_SCORE v1 with positive end required')
    n=round(spec['end']*SR);t=np.arange(n)/SR
    stems={k:np.zeros((n,2)) for k in TRACKS};report={'sample_rate':SR,'events':[],'intentional_silence':spec.get('silence',[])}
    ids=set()
    for e in sorted(spec.get('events',[]),key=lambda x:x['id']):
        if e['id'] in ids:raise ValueError('duplicate event ID')
        ids.add(e['id'])
        if not (0<=e['start']<=e['end']<=spec['end']):raise ValueError(f"event {e['id']} outside timeline")
        if not e.get('sound'):continue
        p=e['sound'];track=p.get('track','sfx')
        if track not in stems:raise ValueError('unknown audio track')
        x=voice(e,SR,root)
        anchor=p.get('anchor',0)
        if not math.isfinite(anchor) or not 0<=anchor<len(x)/SR:raise ValueError('sound anchor must lie within source duration')
        i=round((e['start']-anchor)*SR);skip=max(0,-i);dest=max(0,i);count=min(len(x)-skip,n-dest)
        if count>0:stems[track][dest:dest+count]+=x[skip:skip+count]
        report['events'].append({'id':e['id'],'visual_time':e['start'],'scheduled_sample':i,'source_anchor':anchor,'track':track})
    for k,stem in stems.items():
        p=spec.get('tracks',{}).get(k,{})
        if p.get('highpass'):stem[:]=A.highpass(stem,p['highpass'])
        if p.get('lowpass'):stem[:]=A.lowpass(stem,p['lowpass'])
        if p.get('room',0):stem[:]=A.reverb(stem,np.random.default_rng(110+TRACKS.index(k)),t60=p.get('t60',.45),wet=p['room'])
        stem*=curve(p.get('gain',1),t)[:,None]
    master=np.ones(n)
    for a,b in spec.get('silence',[]):
        if not 0<=a<b<=spec['end']:raise ValueError('invalid silence interval')
        master*=1-np.minimum(1,np.maximum(0,(t-a)/.01))*np.minimum(1,np.maximum(0,(b-t)/.01))
    master*=np.minimum(1,(spec['end']-t)/.02)
    for stem in stems.values():stem*=master[:,None]
    x=sum(stems.values());peak=float(np.max(np.abs(x)))
    if not np.isfinite(x).all():raise ValueError('non-finite mix')
    # One common headroom gain preserves stem balance and exact summability.
    gain=min(1,10**(-3/20)/max(peak,1e-12))
    for stem in stems.values():stem*=gain
    x*=gain
    report.update(peak_before_headroom=peak,headroom_gain=gain,peak_dbfs=20*np.log10(max(float(np.max(np.abs(x))),1e-12)))
    return x,stems,report

def delay(reference,encoded,sr,max_seconds=.1):
    a=np.asarray(reference);b=np.asarray(encoded)
    if a.ndim==2:a=a.mean(axis=1)
    if b.ndim==2:b=b.mean(axis=1)
    if np.linalg.norm(a)<1e-10 or np.linalg.norm(b)<1e-10:raise ValueError('silent sync reference/encoded audio; cannot verify')
    c=correlate(b,a,mode='full',method='fft');lags=correlation_lags(len(b),len(a),mode='full');mask=np.abs(lags)<=round(max_seconds*sr)
    j=np.argmax(c[mask]);lag=int(lags[mask][j]);lo=max(0,lag);start=max(0,-lag);n=min(len(a)-start,len(b)-lo)
    score=float(np.dot(a[start:start+n],b[lo:lo+n])/(np.linalg.norm(a[start:start+n])*np.linalg.norm(b[lo:lo+n])))
    return {'lag_seconds':lag/sr,'correlation':score}
