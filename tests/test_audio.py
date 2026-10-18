import json, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class AudioTest(unittest.TestCase):
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
