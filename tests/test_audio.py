import json, runpy, subprocess, sys, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
class AudioTest(unittest.TestCase):
    def failed_mux(self, returncode):
        # A real child overwrites its destination then fails (or emits corrupt
        # bytes with exit 0). The old final must survive either failure mode.
        real_run = subprocess.run
        with tempfile.TemporaryDirectory() as d:
            p=Path(d); (p/'renders').mkdir(); (p/'audio').mkdir()
            out=p/'renders/final.mp4';out.write_bytes(b'previous good film')
            (p/'audio/events.json').write_text(json.dumps({'end':.4,'fps':30,'events':[[0,'tick',{}]],'meta':{}}))
            def broken(cmd, **kw):
                if cmd[0]=='ffmpeg' and '-map' in cmd:
                    cmd=[sys.executable,'-c','import pathlib,sys;pathlib.Path(sys.argv[1]).write_bytes(b"damaged");sys.exit(int(sys.argv[2]))',cmd[-1],str(returncode)]
                return real_run(cmd,**kw)
            with patch.object(sys,'argv',['audio.py',str(p)]), patch.object(subprocess,'run',side_effect=broken):
                try:runpy.run_path(str(ROOT/'engine/audio.py'),run_name='__main__')
                except (subprocess.CalledProcessError,RuntimeError):pass
            self.assertEqual(out.read_bytes(),b'previous good film')
            self.assertEqual(list((p/'renders').iterdir()),[out])

    def test_failed_mux_keeps_previous_final(self): self.failed_mux(7)

    def test_corrupt_successful_mux_keeps_previous_final(self): self.failed_mux(0)

    def test_subsecond_bgm_mux_has_valid_fade(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d); (p/'renders').mkdir(); (p/'audio').mkdir()
            subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','color=s=64x64:r=30:d=0.4','-c:v','libx264',str(p/'renders/raw.mp4')],check=True)
            subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','sine=frequency=440:duration=0.4',str(p/'bgm.wav')],check=True)
            (p/'audio/events.json').write_text(json.dumps({'end':.4,'fps':30,'events':[[0,'tick',{}]],'meta':{}}))
            result=subprocess.run([sys.executable,str(ROOT/'engine/audio.py'),str(p),'--bgm',str(p/'bgm.wav')],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            data=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(p/'renders/final.mp4')]))
            self.assertEqual({s['codec_type'] for s in data['streams']},{'video','audio'})
            self.assertAlmostEqual(float(data['streams'][0]['duration']),.4,places=2)

    def test_shared_score_mux_and_stems(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d); (p/'renders').mkdir(); (p/'audio').mkdir()
            subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','color=s=64x64:r=30:d=0.4','-c:v','libx264',str(p/'renders/raw.mp4')],check=True)
            score={'version':1,'end':.4,'fps':30,'events':[{'id':'tap','start':.1,'end':.35,'sound':{'kind':'impact','material':'wood'}}]}
            (p/'audio/events.json').write_text(json.dumps({'end':.4,'fps':30,'events':[],'score':score}))
            result=subprocess.run([sys.executable,str(ROOT/'engine/audio.py'),str(p),'--stems'],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertTrue((p/'audio/sfx.wav').exists(),'shared-score stems not exported')
            self.assertTrue((p/'audio/mix.json').exists())
            result=subprocess.run([sys.executable,str(ROOT/'scripts/check_av.py'),str(p)],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr+result.stdout)
            report=json.loads((p/'audio/sync.json').read_text())
            self.assertEqual(report['checked'],1)
            self.assertLess(abs(report['events'][0]['lag_seconds']),1/30)
            stale={'end':.8,'fps':60,'events':[],'score':score}
            (p/'audio/events.json').write_text(json.dumps(stale))
            bad=subprocess.run([sys.executable,str(ROOT/'scripts/check_av.py'),str(p)],capture_output=True,text=True)
            self.assertNotEqual(bad.returncode,0)
            self.assertIn('timeline',bad.stderr)


    def test_shared_score_rejects_unreferenced_external_bgm_keeps_final(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d); (p/'renders').mkdir(); (p/'audio').mkdir()
            (p/'renders/final.mp4').write_bytes(b'old film')
            score={'version':1,'end':.4,'events':[]}
            (p/'audio/events.json').write_text(json.dumps({'end':.4,'events':[],'score':score}))
            r=subprocess.run([sys.executable,str(ROOT/'engine/audio.py'),str(p),'--bgm','missing.wav'],capture_output=True,text=True)
            self.assertNotEqual(r.returncode,0)
            self.assertIn('music track',r.stderr)
            self.assertEqual((p/'renders/final.mp4').read_bytes(),b'old film')
