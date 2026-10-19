"""Prepare licensed, pinned acoustic samples as a local, immutable note bank.
python scripts/prepare_instrument.py <project> <manifest.json> [--out assets/piano]
No runtime sampler, download during rendering, or realtime audio timer.
"""
import argparse,hashlib,json,math,subprocess,sys,tempfile,urllib.request
from fractions import Fraction
from pathlib import Path
import numpy as np
from scipy.signal import resample_poly
from scipy.io import wavfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from engine import provenance
from engine.score_audio import decode,SR


def fetch(url):
    if not url.startswith('https://'):raise ValueError('sample URL requires https')
    with urllib.request.urlopen(url,timeout=60) as r:
        data=r.read(64*1024*1024+1)
    if len(data)>64*1024*1024:raise ValueError('sample exceeds 64 MiB')
    return data


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(project,spec,out='assets/piano'):
    project=Path(project).resolve();dest=(project/out).resolve()
    if not dest.is_relative_to(project) or dest==project:raise ValueError('bank output must be inside project')
    if spec.get('version')!=1 or not spec.get('license'):raise ValueError('version 1 and explicit sample license required')
    sources=spec.get('sources',[]);notes=spec.get('notes',[]);maximum=spec.get('max_seconds',4)
    if not sources or not notes or not math.isfinite(maximum) or not .05<=maximum<=20:raise ValueError('sources, notes, and finite max_seconds [.05,20] required')
    if any(not isinstance(n,int) or isinstance(n,bool) or not 0<=n<=127 for n in notes) or len(set(notes))!=len(notes):raise ValueError('unique MIDI integer notes [0,127] required')
    for s in sources:
        if not isinstance(s.get('midi'),int) or not 0<=s['midi']<=127 or not math.isfinite(s.get('trim',0)) or s.get('trim',0)<0:raise ValueError('invalid sample MIDI/trim')
        if not s.get('url','').startswith('https://') or len(s.get('sha256',''))!=64:raise ValueError('pinned HTTPS source and SHA256 required')
    ffmpeg=subprocess.run(['ffmpeg','-version'],capture_output=True,text=True,check=True).stdout.splitlines()[0]
    identity=hashlib.sha256(json.dumps({'spec':spec,'tool':sha(Path(__file__)),'ffmpeg':ffmpeg},sort_keys=True).encode()).hexdigest()
    index=dest/'bank.json';old=None
    if index.exists():
        try:old=json.loads(index.read_text(encoding='utf-8'))
        except (ValueError,OSError):pass
    def valid_bank():
        try:
            if not old or old.get('identity')!=identity or set(old['notes'])!={str(n) for n in notes}:return False
            for midi,n in old['notes'].items():
                path=(project/n['src']).resolve()
                expected=(dest/identity/f'{midi}.flac').resolve()
                if path!=expected or not path.is_relative_to(project) or n['license']!=spec['license'] or not n['duration']>0:return False
                if not path.is_file() or sha(path)!=n['sha256']:return False
            return True
        except (KeyError,TypeError,ValueError,OSError):return False
    if valid_bank():return old
    cache=Path(tempfile.gettempdir())/'vk-music-source-v1';cache.mkdir(exist_ok=True)
    decoded=[]
    for s in sources:
        path=cache/(s['sha256']+'.wav')
        if not path.exists() or sha(path)!=s['sha256']:
            data=fetch(s['url'])
            if hashlib.sha256(data).hexdigest()!=s['sha256']:raise ValueError('sample SHA256 mismatch: '+s['url'])
            with tempfile.NamedTemporaryFile(dir=cache,delete=False) as f:f.write(data);tmp=Path(f.name)
            try:tmp.replace(path)
            finally:tmp.unlink(missing_ok=True)
        x=decode(path)[round(s.get('trim',0)*SR):]
        if not len(x) or not np.isfinite(x).all():raise ValueError('empty/nonfinite source after trim')
        decoded.append((s['midi'],x))
    dest.mkdir(parents=True,exist_ok=True);folder=dest/identity;folder.mkdir(exist_ok=True)
    result={'version':1,'identity':identity,'license':spec['license'],'sources':sources,'notes':{},'method':'nearest acoustic sample; bandlimited resampling changes pitch and decay duration; not a sustain-pedal model'}
    with tempfile.TemporaryDirectory(dir=dest,prefix='.prepare-') as tmp:
        tmp=Path(tmp)
        for midi in sorted(notes):
            root,x=min(decoded,key=lambda item:abs(item[0]-midi))
            ratio=Fraction(2**((root-midi)/12)).limit_denominator(2048)
            x=resample_poly(x,ratio.numerator,ratio.denominator)[:round(maximum*SR)]
            t=np.arange(len(x))/SR;x=x*np.minimum(1,t/.002)[:,None]*np.minimum(1,(len(x)/SR-t)/.04)[:,None]
            wavfile.write(tmp/'note.wav',SR,x.astype(np.float32))
            candidate=tmp/f'{midi}.flac'
            subprocess.run(['ffmpeg','-v','error','-y','-i',str(tmp/'note.wav'),'-c:a','flac','-sample_fmt','s32',str(candidate)],check=True)
            check=decode(candidate)
            if len(check)!=len(x) or not np.isfinite(check).all():raise RuntimeError('prepared note decode verification failed')
            target=folder/candidate.name;candidate.replace(target)
            result['notes'][str(midi)]={'src':target.relative_to(project).as_posix(),'sha256':sha(target),'duration':len(x)/SR,'source_midi':root,'license':spec['license']}
    # Existing descriptor remains usable if any download/prepare step fails.
    provenance.atomic_json(index,result);return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('project',type=Path);p.add_argument('manifest',type=Path);p.add_argument('--out',default='assets/piano');a=p.parse_args()
    b=prepare(a.project,json.loads(a.manifest.read_text(encoding='utf-8')),a.out);print(f"prepared {len(b['notes'])} notes: {b['identity'][:12]}")
if __name__=='__main__':main()
