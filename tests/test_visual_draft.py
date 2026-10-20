"""Real series scaffold: a missing music module must never load in visual Draft."""
import json, subprocess, sys, tempfile, unittest
from pathlib import Path
from engine import render
from scripts import produce
ROOT=Path(__file__).resolve().parents[1]

class VisualDraftTest(unittest.TestCase):
    def test_missing_master_visual_draft_isolated_and_normal_load_still_locked(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            subprocess.run([sys.executable,str(ROOT/'scripts/new_film.py'),str(p),'--world','custom',
                            '--duration','.4','--series','shape-of-luck'],check=True,capture_output=True)
            config=(p/'music.json').read_bytes()
            (p/'renders').mkdir(); (p/'review').mkdir()
            protected={'renders/final.mp4':b'previous film','review/production.json':b'previous report',
                       'review/production-cache.json':b'previous cache'}
            for name,data in protected.items():(p/name).write_bytes(data)
            result=subprocess.run([sys.executable,str(ROOT/'scripts/produce.py'),str(p),'--mode','draft',
                                   '--visual-only','--stills','.2'],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr+result.stdout)
            self.assertTrue((p/'review/visual-draft/s_0000.20.png').exists())
            self.assertFalse((p/'assets/music-plan.mjs').exists())
            self.assertEqual((p/'music.json').read_bytes(),config)
            for name,data in protected.items():self.assertEqual((p/name).read_bytes(),data)
            clip=subprocess.run([sys.executable,str(ROOT/'scripts/produce.py'),str(p),'--mode','draft',
                                 '--visual-only','--clip','0','.3'],capture_output=True,text=True)
            self.assertEqual(clip.returncode,0,clip.stderr+clip.stdout)
            self.assertTrue((p/'renders/visual-draft/draft.mp4').exists())
            for name,data in protected.items():self.assertEqual((p/name).read_bytes(),data)
            for mode in ['standard','release']:
                r=subprocess.run([sys.executable,str(ROOT/'scripts/produce.py'),str(p),'--mode',mode,
                                  '--visual-only'],capture_output=True)
                self.assertNotEqual(r.returncode,0)
                self.assertEqual((p/'review/production.json').read_bytes(),protected['review/production.json'])
            for mode in ['standard','release']:
                r=subprocess.run([sys.executable,str(ROOT/'scripts/produce.py'),str(p),'--mode',mode],capture_output=True)
                self.assertNotEqual(r.returncode,0)
                self.assertEqual(json.loads((p/'review/production.json').read_text())['status'],'failed')
                self.assertEqual((p/'renders/final.mp4').read_bytes(),protected['renders/final.mp4'])
            self.assertFalse((p/'assets/music-plan.mjs').exists())
            with self.assertRaises(RuntimeError):render.with_page(p,lambda pg:None)
            from unittest.mock import patch
            with patch.object(render,'VISUAL_DRAFT',True):
                with self.assertRaisesRegex(ValueError,'cannot be certified'):
                    render.with_page(p,produce.inspect)

    def test_restored_verified_plan_loads_without_preview_flag(self):
        from tests.test_signature_music import SignatureMusicTest
        from scripts import prepare_music
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            subprocess.run([sys.executable,str(ROOT/'scripts/new_film.py'),str(p),'--world','custom',
                            '--duration','2','--series','shape-of-luck'],check=True,capture_output=True)
            cfg=SignatureMusicTest().fixture(p)
            # Analytic test recording only, never a claim about the real song.
            code=(p/'film.js').read_text(encoding='utf-8').replace('shape-of-luck','pipeline-test-only')
            (p/'film.js').write_text(code,encoding='utf-8')
            (p/'music.json').write_text(json.dumps(cfg),encoding='utf-8')
            prepare_music.prepare(p)
            render.with_page(p,lambda pg:self.assertEqual(pg.evaluate('VK_SCORE.json().events.length'),2))
