from pathlib import Path
import subprocess, sys, tempfile, unittest
ROOT=Path(__file__).resolve().parents[1]
class ScaffoldTest(unittest.TestCase):
    def test_custom_is_neutral_and_does_not_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'film'
            cmd=[sys.executable,str(ROOT/'scripts/new_film.py'),str(p),'--world','custom']
            result=subprocess.run(cmd,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            code=(p/'film.js').read_text()
            self.assertIn('bloom: 0',code)
            self.assertIn("theme: 'flat'",code)
            self.assertTrue((p/'direction.md').exists())
            again=subprocess.run(cmd,capture_output=True,text=True)
            self.assertNotEqual(again.returncode,0)
            self.assertEqual((p/'film.js').read_text(),code)
