"""Conservative onset/tempo/energy candidates for supplied music. No downbeat oracle.
python scripts/analyze_music.py <audio> --out <analysis.json>
Confirm phase, half/double tempo and phrases by listening before using a beat grid.
"""
import argparse
import json
from pathlib import Path
import sys
import numpy as np
from scipy.signal import stft,find_peaks,resample_poly,correlate
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from engine.score_audio import decode,SR

def analyze(x,sr):
    if x.ndim==2:x=x.mean(axis=1)
    if not len(x) or not np.isfinite(x).all():raise ValueError('finite non-empty audio required')
    hop=max(1,round(sr*.01));window=min(512,len(x));hop=min(hop,window)
    _,times,z=stft(x,fs=sr,nperseg=window,noverlap=window-hop,boundary='zeros')
    mag=np.abs(z);flux=np.r_[0,np.maximum(0,np.diff(mag,axis=1)).sum(axis=0)]
    scale=float(flux.max());onsets=[];candidates=[]
    if scale>1e-10:
        peaks,_=find_peaks(flux,prominence=scale*.12,distance=max(1,round(.08*sr/hop)))
        onsets=[round(float(times[i]),5) for i in peaks]
        ac=correlate(flux,flux,mode='full',method='fft')[len(flux)-1:]
        lo=round(sr/hop*60/180);hi=min(len(ac)-1,round(sr/hop*60/60))
        if hi>lo:
            peaks,_=find_peaks(ac[lo-1:hi+2]);lags=[lo-1+i for i in peaks if lo<=lo-1+i<=hi]
            for lag in sorted(lags,key=lambda i:ac[i],reverse=True)[:4]:
                candidates.append({'bpm':round(60*sr/(hop*lag),3),'relative_periodicity':round(float(ac[lag]/max(ac[0],1e-12)),4)})
    energy=[{'time':i/sr,'rms_dbfs':round(float(20*np.log10(max(np.sqrt(np.mean(x[i:i+sr]**2)),1e-12))),2)} for i in range(0,len(x),sr)]
    return {'onsets':onsets,'tempo_candidates':candidates,'energy_1s':energy,'downbeats':None,'phrases':None,'grid_verified':False,
            'scope':'spectral-flux and autocorrelation candidates; soft/noisy or changing-tempo music needs manual annotation; not a music-quality score'}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('audio',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    x=resample_poly(decode(a.audio).mean(axis=1),1,4);r=analyze(x,SR//4)
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(r,indent=2),encoding='utf-8');print(a.out)
if __name__=='__main__':main()
