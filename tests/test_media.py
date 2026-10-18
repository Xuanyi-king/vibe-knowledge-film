import importlib.util, subprocess, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class MediaTest(unittest.TestCase):
    def check(self,path,**kw):
        spec=importlib.util.spec_from_file_location('check_media',ROOT/'scripts/check_media.py')
        self.assertTrue(Path(spec.origin).exists(),'media checker not implemented')
        m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        return m.inspect_media(path,**kw)
    def make(self,path,color='teal',audio=True):
        cmd=['ffmpeg','-v','error','-y','-f','lavfi','-i',f'color=c={color}:s=1920x1080:r=30:d=0.6']
        if audio: cmd+=['-f','lavfi','-i','sine=frequency=440:duration=0.6']
        subprocess.run(cmd+['-c:v','libx264','-threads','1','-pix_fmt','yuv420p','-c:a','aac','-shortest',str(path)],check=True)
    def test_valid_media_and_duration_mismatch(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'test.mp4'; self.make(p)
            report=self.check(p,expected_duration=.6,loudness=True)
            self.assertEqual(report['errors'],[])
            self.assertIn('sample_peak_db',report['audio'])
            self.assertIsInstance(report['audio']['integrated_lufs'],float)
            self.assertLess(report['audio']['true_peak_dbtp'],0)
            self.assertTrue(self.check(p,expected_duration=3)['errors'])
    def test_black_frames_are_candidates_not_aesthetic_scores(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'test.mp4'; self.make(p,color='black',audio=False)
            report=self.check(p,expected_duration=.6,require_audio=False)
            self.assertEqual(report['errors'],[])
            self.assertTrue(report['candidates']['black'])
            self.assertNotIn('score',report)
            self.assertTrue(self.check(p,expected_duration=.6)['errors'])
    def test_invalid_file_fails(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'bad.mp4';p.write_bytes(b'not a video')
            with self.assertRaises(RuntimeError):self.check(p)
