"""Conservative onset/tempo/energy candidates for supplied music. No downbeat oracle.
python scripts/analyze_music.py <audio> --out <analysis.json>
Confirm phase, half/double tempo and phrases by listening before using a beat grid.
"""
import argparse
import json
from pathlib import Path
import sys
import hashlib,subprocess
import numpy as np
import scipy
from scipy.ndimage import uniform_filter1d
from scipy.signal import stft,find_peaks,resample_poly,correlate,butter,sosfiltfilt
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from engine.score_audio import decode,SR
from engine.render_cache import atomic_json,digest

def periodicity(feature,hop_seconds):
    y=np.maximum(0,feature-np.quantile(feature,.35))
    if not len(y) or np.max(y)<1e-10:return []
    ac=correlate(y,y,mode='full',method='fft')[len(y)-1:]
    lo=max(1,round(60/220/hop_seconds));hi=min(len(ac)-2,round(60/40/hop_seconds))
    if hi<=lo:return []
    peaks,_=find_peaks(ac[lo-1:hi+2]);lags=[lo-1+i for i in peaks if lo<=lo-1+i<=hi]
    result=[]
    for lag in sorted(lags,key=lambda i:ac[i],reverse=True)[:8]:
        den=ac[lag-1]-2*ac[lag]+ac[lag+1]
        delta=float(.5*(ac[lag-1]-ac[lag+1])/den) if abs(den)>1e-12 else 0
        seconds=(lag+np.clip(delta,-.5,.5))*hop_seconds
        result.append({'bpm':round(60/seconds,4),'period_seconds':round(float(seconds),7),
                       'relative_periodicity':round(float(ac[lag]/max(ac[0],1e-12)),4)})
    return result

def analyze(x,sr):
    if x.ndim==2:x=x.mean(axis=1)
    if not len(x) or not np.isfinite(x).all():raise ValueError('finite non-empty audio required')
    x=x.astype(np.float32);hop=max(1,round(sr*.002));window=min(512,len(x));hop=min(hop,window)
    _,times,z=stft(x,fs=sr,nperseg=window,noverlap=window-hop,boundary='zeros')
    mag=np.abs(z);flux=np.r_[0,np.maximum(0,np.diff(mag,axis=1)).sum(axis=0)]
    scale=float(flux.max());onsets=[]
    if scale>1e-10:
        peaks,_=find_peaks(flux,prominence=scale*.12,distance=max(1,round(.08*sr/hop)))
        onsets=[round(float(times[i]),5) for i in peaks]
    candidates=periodicity(flux,hop/sr)
    energy=[{'time':i/sr,'rms_dbfs':round(float(20*np.log10(max(np.sqrt(np.mean(x[i:i+sr]**2)),1e-12))),2)} for i in range(0,len(x),sr)]
    smooth=np.sqrt(np.maximum(0,uniform_filter1d(x*x,max(1,round(sr*.02)))))
    envelope=smooth[np.clip((times*sr).astype(int),0,len(x)-1)]
    # Independent amplitude-modulation estimate: remove slow section changes and
    # high-rate carrier ripple, rather than autocorrelating noisy sample peaks.
    modulation=sosfiltfilt(butter(2,[.5,8],btype='bandpass',fs=sr/hop,output='sos'),envelope) if len(envelope)>48 else envelope
    activity=np.flatnonzero(envelope>10**(-60/20));duration=len(x)/sr
    active={'threshold_dbfs':-60,'first':round(float(times[activity[0]]),4) if len(activity) else None,
            'last':round(min(duration,float(times[activity[-1]])+hop/sr),4) if len(activity) else None}
    quiet=envelope<=10**(-60/20);edges=np.diff(np.r_[False,quiet,False].astype(int));silences=[]
    for a,b in zip(np.flatnonzero(edges==1),np.flatnonzero(edges==-1)):
        start=max(0,float(times[a]));end=min(duration,b*hop/sr)
        if end-start>=.2:silences.append({'start':round(start,4),'end':round(end,4)})
    density=[sum(i<=t<i+1 for t in onsets) for i in range(len(energy))]
    levels=np.array([r['rms_dbfs'] for r in energy]);change=np.abs(np.diff(levels))+np.abs(np.diff(density))*.5
    peak,_=find_peaks(change,distance=4,prominence=2)
    sections=[{'time':int(i+1),'reason':'energy/onset-density change, not a verified phrase',
               'before_dbfs':float(levels[i]),'after_dbfs':float(levels[i+1]),'strength':round(float(change[i]),2)} for i in sorted(peak,key=lambda i:change[i],reverse=True)[:12]]
    grids=[]
    for candidate in candidates[:3]:
        period=candidate['period_seconds'];lag=max(1,round(period*sr/hop))
        comb=np.bincount(np.arange(len(flux))%lag,weights=flux,minlength=lag)
        phase=float(np.argmax(comb)*hop/sr)
        grids.append({'bpm':candidate['bpm'],'period_seconds':period,'phase_candidate':round(phase,5),
              'times':np.round(np.arange(phase,duration,period),5).tolist(),'verified':False,
              'uncertainty':'phase/accent, half/double tempo and meter need review; not detected downbeats'})
    local=[]
    for start in range(0,max(1,int(duration)-7),8):
        a=round(start*sr/hop);b=round(min(duration,start+16)*sr/hop)
        c=periodicity(flux[a:b],hop/sr)
        if c:local.append({'start':start,'end':min(duration,start+16),'candidates':c[:3]})
    edge=[]
    for t in sorted(set([round(v,3) for v in np.r_[np.arange(0,min(2,duration),.1),np.arange(max(0,duration-2),duration,.1)]])):
        part=x[round(t*sr):min(len(x),round((t+.1)*sr))]
        if len(part):edge.append({'time':t,'rms_dbfs':round(float(20*np.log10(max(np.sqrt(np.mean(part**2)),1e-12))),2)})
    return {'onsets':onsets,'tempo_candidates':candidates,'envelope_tempo_candidates':periodicity(modulation,hop/sr),
            'methods':['spectral_flux_autocorrelation','envelope_autocorrelation','parabolic_period_refinement','onset_density_and_rms_change'],
            'hop_seconds':hop/sr,'duration':duration,'activity':active,'silence_candidates':silences,
            'energy_1s':energy,'onsets_per_second':density,'section_candidates':sections,'local_periodicity':local,
            'beat_grid_candidate':grids[0] if grids else None,'beat_grid_candidates':grids,'edge_energy_100ms':edge,
            'downbeats':None,'phrases':None,'grid_verified':False,
            'scope':'spectral-flux and autocorrelation candidates; soft/noisy or changing-tempo music needs manual annotation; not a music-quality score'}

def analyze_file(audio,out,annotations=None):
    audio=Path(audio).resolve();out=Path(out).resolve()
    if audio==out:raise ValueError('analysis output cannot overwrite audio')
    source=digest(audio)
    if annotations and annotations.get('source_sha256')!=source:raise ValueError('annotation source fingerprint differs')
    implementation=digest(Path(__file__))
    ffmpeg=subprocess.run(['ffmpeg','-version'],capture_output=True,text=True,check=True).stdout.splitlines()[0]
    identity=hashlib.sha256(json.dumps({'source':source,'implementation':implementation,'decoder':digest(Path(__file__).resolve().parents[1]/'engine/score_audio.py'),
        'numpy':np.__version__,'scipy':scipy.__version__,'ffmpeg':ffmpeg,'annotations':annotations},sort_keys=True).encode()).hexdigest()
    try:
        cached=json.loads(out.read_text(encoding='utf-8'));payload={k:v for k,v in cached.items() if k!='payload_sha256'}
        integrity=hashlib.sha256(json.dumps(payload,sort_keys=True,allow_nan=False).encode()).hexdigest()
        if cached.get('identity')==identity and cached.get('payload_sha256')==integrity:return cached
    except (OSError,ValueError,TypeError):pass
    x=resample_poly(decode(audio).mean(axis=1),1,4);r=analyze(x,SR//4)
    r.update(version=2,source_sha256=source,source_bytes=audio.stat().st_size,identity=identity,
             implementation_sha256=implementation,ffmpeg=ffmpeg,time_unit='seconds',annotations=None)
    if annotations:
        if not annotations.get('reviewer'):raise ValueError('manual annotation needs reviewer/method')
        for name in ['beats','downbeats']:
            values=annotations.get(name,[])
            if any(isinstance(t,bool) or not isinstance(t,(int,float)) or not np.isfinite(t) or not 0<=t<r['duration'] for t in values) or any(b<=a for a,b in zip(values,values[1:])):raise ValueError('annotation times invalid')
            r[name]=values
        phrases=annotations.get('phrases',[])
        ts=[p['time'] for p in phrases]
        if any(isinstance(t,bool) or not isinstance(t,(int,float)) or not np.isfinite(t) or not 0<=t<r['duration'] for t in ts) or any(b<=a for a,b in zip(ts,ts[1:])):raise ValueError('phrase annotations invalid')
        r.update(phrases=phrases,grid_verified=bool(r['beats']) and annotations.get('complete_grid') is True,
                 annotated_points_verified=True,annotation_scope='only supplied points; full grid requires explicit complete_grid declaration',annotations=annotations)
    if digest(audio)!=source:raise RuntimeError('audio changed during analysis')
    r['payload_sha256']=hashlib.sha256(json.dumps(r,sort_keys=True,allow_nan=False).encode()).hexdigest()
    out.parent.mkdir(parents=True,exist_ok=True);atomic_json(out,r);return r

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('audio',type=Path);p.add_argument('--out',type=Path,required=True);p.add_argument('--annotations',type=Path);a=p.parse_args()
    try:analyze_file(a.audio,a.out,json.loads(a.annotations.read_text(encoding='utf-8')) if a.annotations else None)
    except Exception as exc:print(f'music analysis failed: {exc}',file=sys.stderr);return 1
    print(a.out);return 0
if __name__=='__main__':sys.exit(main())
