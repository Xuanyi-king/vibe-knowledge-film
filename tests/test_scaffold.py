from pathlib import Path
import subprocess, sys, tempfile, unittest
ROOT=Path(__file__).resolve().parents[1]
class ScaffoldTest(unittest.TestCase):
    def test_custom_is_neutral_and_does_not_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'film'
            cmd=[sys.executable,str(ROOT/'scripts/new_film.py'),str(p),'--world','custom','--duration','78.5']
            result=subprocess.run(cmd,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            code=(p/'film.js').read_text()
            self.assertIn('bloom: 0',code)
            self.assertIn("theme: 'flat'",code)
            self.assertIn('end: 78.5',code)
            self.assertTrue((p/'direction.md').exists())
            again=subprocess.run(cmd,capture_output=True,text=True)
            self.assertNotEqual(again.returncode,0)
            self.assertEqual((p/'film.js').read_text(),code)

    def test_missing_decisions_do_not_create_a_default_film(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'undecided'
            for args,reason in [([], '--world'),(['--world','custom'],'--duration')]:
                result=subprocess.run([sys.executable,str(ROOT/'scripts/new_film.py'),str(p),*args],capture_output=True,text=True)
                self.assertNotEqual(result.returncode,0,result.stdout)
                self.assertIn(reason,result.stderr)
                self.assertFalse(p.exists(),'no style or duration should be chosen on the Agent behalf')

    def test_explicit_legacy_worlds_keep_appearance_and_warn_about_placeholder(self):
        with tempfile.TemporaryDirectory() as d:
            for world,theme in [('B','flat'),('C','night')]:
                p=Path(d)/world
                result=subprocess.run([sys.executable,str(ROOT/'scripts/new_film.py'),str(p),'--world',world],capture_output=True,text=True)
                self.assertEqual(result.returncode,0,result.stderr)
                self.assertIn(f"theme: '{theme}'",(p/'film.js').read_text())
                self.assertIn('end: 30',(p/'film.js').read_text())
                self.assertIn('--duration',result.stderr)
                self.assertIn('30',result.stderr)

    def test_invalid_arguments_leave_existing_project_untouched_even_with_force(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);film=p/'film.js';index=p/'index.html'
            film.write_bytes(b'old film');index.write_bytes(b'old html')
            for duration in ['0','-1','nan','inf','bad']:
                args=[sys.executable,str(ROOT/'scripts/new_film.py'),str(p),'--world','custom','--force','--duration',duration]
                result=subprocess.run(args,capture_output=True,text=True)
                self.assertNotEqual(result.returncode,0)
                self.assertEqual(film.read_bytes(),b'old film')
                self.assertEqual(index.read_bytes(),b'old html')
