"""Real sparse transient mix must stay below the encoded true-peak ceiling."""
import hashlib,json,subprocess,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
from engine import provenance,audio
ROOT=Path(__file__).resolve().parents[1]

class MasteringTest(unittest.TestCase):
    def make(self,p):
        (p/'audio').mkdir();(p/'renders').mkdir();(p/'review').mkdir()
        (p/'film.js').write_text('// sparse high-crest-factor mastering fixture')
        spec={'end':2,'fps':30,'meta':{},'events':[]}
        spec=provenance.seal_events(spec,provenance.source_files(p));provenance.atomic_json(p/'audio/events.json',spec)
        n=96000;t=np.arange(n)/48000;x=.0002*np.sin(2*np.pi*220*t)
        for a in [.4,1.2]:
            ix=(t>=a)&(t<a+.012);x[ix]+=.5*np.sin(2*np.pi*3000*(t[ix]-a))
        audio.write_wav(p/'audio/score.wav',np.column_stack([x,x]))
        raw=p/'renders/raw.mp4';final=p/'renders/final.mp4'
        subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','color=s=64x64:r=30:d=2','-c:v','libx264','-pix_fmt','yuv420p',str(raw)],check=True)
        subprocess.run(['ffmpeg','-v','error','-y','-i',str(raw),'-i',str(p/'audio/score.wav'),'-c:v','copy','-c:a','aac','-shortest',str(final)],check=True)
        sources=provenance.source_files(p);timeline=dict(end=2,fps=30,start=0,stop=2)
        provenance.publish_video(raw,raw,sources,timeline)
        provenance.publish_video(final,final,sources,timeline,kind='final',events_sha256=provenance.identity(spec),reference_sha256=provenance.digest(p/'audio/score.wav'))
        return spec

    def module(self):
        self.assertTrue((ROOT/'scripts/master_audio.py').exists(),'safe encoded-peak mastering stage missing')
        from scripts import master_audio
        return master_audio

    def test_sparse_transients_meet_encoded_ceiling_without_timing_shift(self):
        m=self.module()
        from engine.score_audio import decode,delay
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);spec=self.make(p);report=m.master(p,legacy_source_only=True)
            self.assertLessEqual(report['encoded']['true_peak_dbtp'],-1.5)
            self.assertLessEqual(abs(delay(decode(p/'audio/score.wav'),decode(p/'renders/final.mp4'),48000)['lag_seconds']),1/48000)
            provenance.validate_video(p/'renders/final.mp4',spec,provenance.source_files(p),kind='final')
            self.assertIn('constant_gain',report['method'])

    def test_real_encoder_failure_preserves_final_and_provenance(self):
        m=self.module()
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);self.make(p);out=p/'renders/final.mp4';before=out.read_bytes();stamp=provenance.sidecar(out).read_bytes();real_run=subprocess.run
            def broken(cmd,**kw):
                if str(cmd[-1]).endswith('.mp4'):cmd=[sys.executable,'-c','import sys;sys.exit(7)']
                return real_run(cmd,**kw)
            with patch.object(m.subprocess,'run',side_effect=broken),self.assertRaises((RuntimeError,subprocess.CalledProcessError)):
                m.master(p,legacy_source_only=True)
            self.assertEqual(out.read_bytes(),before);self.assertEqual(provenance.sidecar(out).read_bytes(),stamp)

    def test_legacy_mastering_requires_explicit_source_only_contract(self):
        m=self.module()
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);self.make(p);before=(p/'renders/final.mp4').read_bytes()
            with self.assertRaisesRegex(ValueError,'legacy'):
                m.master(p)
            self.assertEqual((p/'renders/final.mp4').read_bytes(),before)
