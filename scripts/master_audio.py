"""Deliver a current source mix with measured encoded true-peak headroom.
python scripts/master_audio.py <project> [--target -18] [--ceiling -1.5]
Uses constant gain (no lookahead delay or dynamic pumping), then measures AAC.
"""
import argparse,json,math,re,subprocess,sys,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from engine import audio,provenance


def measure(path):
    cmd=['ffmpeg','-hide_banner','-nostats','-i',str(path),'-vn','-af','loudnorm=I=-18:TP=-1.5:LRA=14:print_format=json','-f','null','-']
    r=subprocess.run(cmd,check=True,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=600)
    blocks=re.findall(r'\{\s*"input_i"[\s\S]*?\}',r.stderr)
    if not blocks:raise RuntimeError('mastering: FFmpeg did not return loudness/true-peak measurements')
    data=json.loads(blocks[-1]);out={}
    for key,field in [('integrated_lufs','input_i'),('true_peak_dbtp','input_tp'),('loudness_range_lu','input_lra')]:
        value=float(data[field]);out[key]=value if math.isfinite(value) else None
    return out


def master(proj,target=-18,ceiling=-1.5,legacy_source_only=False):
    if not math.isfinite(target) or not -70<=target<=-5 or not math.isfinite(ceiling) or not -12<=ceiling<=-1:
        raise ValueError('mastering target must be -70..-5 LUFS, ceiling -12..-1 dBTP')
    proj=proj.resolve();(proj/'review').mkdir(exist_ok=True)
    report={'status':'running','method':'measured_constant_gain_with_encoded_peak_check','target_lufs':target,'ceiling_dbtp':ceiling,'attempts':[]}
    path=proj/'review/mastering.json';provenance.atomic_json(path,report)
    try:
        spec=json.loads((proj/'audio/events.json').read_text(encoding='utf-8'));sources=provenance.validate_events(proj,spec)
        if not spec.get('score') and not legacy_source_only:
            raise ValueError('legacy source-only contract required: external --bgm is absent from score.wav; use shared score sample/music or --legacy-source-only only when no external BGM was mixed')
        raw=proj/'renders/raw.mp4';out=proj/'renders/final.mp4';wav=proj/'audio/score.wav'
        provenance.validate_video(raw,spec,sources)
        previous=provenance.validate_video(out,spec,sources,kind='final');reference=provenance.digest(wav)
        if previous.get('reference_sha256')!=reference:raise RuntimeError('mastering: stale source mix; re-export and synthesize first')
        original=measure(wav);report['source']=original
        peak=original['true_peak_dbtp'];loudness=original['integrated_lufs']
        gain=0 if peak is None else min(target-loudness if loudness is not None else 0,ceiling-peak-2)
        with tempfile.TemporaryDirectory(prefix='.vk-master-',dir=out.parent) as folder:
            candidate=Path(folder)/'final.mp4'
            for attempt in range(3):
                subprocess.run(['ffmpeg','-v','error','-y','-i',str(raw),'-i',str(wav),'-map','0:v:0','-map','1:a:0',
                    '-af',f'volume={gain:.9f}dB','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-shortest',str(candidate)],
                    check=True,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=600)
                audio.validate_mux(candidate,spec['end'],spec.get('fps',30));encoded=measure(candidate)
                report['attempts'].append({'gain_db':gain,'encoded':encoded})
                tp=encoded['true_peak_dbtp']
                if tp is None and peak is not None:raise RuntimeError('mastering: non-silent source produced unmeasurable output')
                if tp is None or tp<=ceiling:break
                gain-=tp-ceiling+.5
            else:raise RuntimeError('mastering: encoded peak exceeds ceiling after three measured attempts; previous final kept')
            provenance.stable(proj,sources)
            if provenance.digest(wav)!=reference:raise RuntimeError('mastering: reference mix changed during encode; previous final kept')
            report.update(status='passed',encoded=encoded,gain_db=gain,input_sha256=provenance.identity(sources),reference_sha256=reference,
                          implementation_sha256=provenance.digest(Path(__file__)))
            record=provenance.publish_video(candidate,out,sources,dict(end=spec['end'],fps=spec.get('fps',30),start=0,stop=spec['end']),
                    kind='final',events_sha256=provenance.identity(spec),reference_sha256=reference,mastering={k:report[k] for k in ['method','target_lufs','ceiling_dbtp','gain_db','implementation_sha256']})
            report['video_sha256']=record['sha256']
    except (Exception,KeyboardInterrupt) as exc:
        report.update(status='failed',error=str(exc));raise
    finally:provenance.atomic_json(path,report)
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('project',type=Path);p.add_argument('--target',type=float,default=-18);p.add_argument('--ceiling',type=float,default=-1.5);p.add_argument('--legacy-source-only',action='store_true',help='only when legacy final has no separate --bgm');a=p.parse_args()
    print(json.dumps(master(a.project,a.target,a.ceiling,a.legacy_source_only),indent=2))
if __name__=='__main__':main()
