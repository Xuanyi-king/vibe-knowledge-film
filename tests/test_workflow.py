"""Adaptive execution must preserve release identity and isolate previews."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from engine import provenance
from scripts import produce

ROOT = Path(__file__).resolve().parents[1]


class WorkflowTest(unittest.TestCase):
    def test_draft_cli_does_not_publish_or_run_release(self):
        with tempfile.TemporaryDirectory(prefix="vk draft 空格 '") as d:
            p=Path(d)
            subprocess.run([sys.executable,str(ROOT/'scripts/new_film.py'),str(p),
                            '--world','custom','--duration','.4'],check=True,capture_output=True)
            (p/'review').mkdir()
            report=p/'review/production.json';report.write_bytes(b'previous release')
            result=subprocess.run([sys.executable,str(ROOT/'scripts/produce.py'),str(p),
                                   '--mode','draft','--stills','.2'],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr+result.stdout)
            self.assertTrue((p/'review/s_0000.20.png').exists())
            self.assertEqual(report.read_bytes(),b'previous release')
            self.assertFalse((p/'renders/final.mp4').exists())
            draft=json.loads((p/'review/draft.json').read_text())
            self.assertEqual(draft['status'],'preview_needs_review')
            self.assertNotIn('media',draft['stages'])

    def test_invalid_modes_and_preview_flags_leave_release_untouched(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'review').mkdir()
            report=p/'review/production.json';report.write_bytes(b'previous release')
            for args in [['--mode','oops'],['--stills','1'],['--mode','draft','--motion','2','1']]:
                result=subprocess.run([sys.executable,str(ROOT/'scripts/produce.py'),str(p),*args],capture_output=True)
                self.assertNotEqual(result.returncode,0)
                self.assertEqual(report.read_bytes(),b'previous release')

    def test_python_draft_api_cannot_select_final_or_export_events(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'review').mkdir();(p/'renders').mkdir()
            final=p/'renders/final.mp4';final.write_bytes(b'previous final')
            for preview in [('--clip',0,.4,'final'),('--events',),('--motion',2,1)]:
                with self.subTest(preview=preview),patch.object(produce.subprocess,'run') as run:
                    with self.assertRaises(ValueError):produce.produce(p,mode='draft',preview=preview)
                    run.assert_not_called()
                    self.assertFalse((p/'review/draft.json').exists())
                    self.assertEqual(final.read_bytes(),b'previous final')

    def test_receipt_rejects_changed_and_missing_outputs(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'audio').mkdir();a=p/'audio/events.json';a.write_text('{}')
            snapshot=produce.output_snapshot(p,['audio'])
            self.assertTrue(produce.reusable(p,{'key':'k','outputs':snapshot},'k'))
            self.assertFalse(produce.reusable(p,{'key':'k','outputs':snapshot},'changed-runtime'))
            a.write_text('{"modified":true}')
            self.assertFalse(produce.reusable(p,{'key':'k','outputs':snapshot},'k'))
            a.write_text('{}');a.unlink()
            self.assertFalse(produce.reusable(p,{'key':'k','outputs':snapshot},'k'))
            self.assertFalse(produce.reusable(p,{},'k'))

    def test_standard_then_release_reuses_build_but_generates_mobile(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            (p/'index.html').write_text('<canvas id="stage"></canvas><script src="/engine/vk.js"></script><script src="film.js"></script>')
            (p/'film.js').write_text("""import('/engine/vk-motion.mjs').then(M=>{
              window.VK_SCORE=M.score({end:.4,events:[{id:'hit',start:.2,duration:.1,sound:{kind:'impact'}}]});
              VK.film({dur:.4,grain:0,draw(fr,t){fr.rect(20+t*10,10,20,20,{fill:'#abc'})}});
            });""")
            standard=produce.produce(p,chunk=.2,mode='standard')
            self.assertEqual(standard['status'],'standard_complete_needs_release_and_review')
            self.assertFalse((p/'review/mobile/report.json').exists())
            final=p/'renders/final.mp4';before=final.stat().st_mtime_ns
            release=produce.produce(p,chunk=.2)
            self.assertEqual(release['stages'],['fonts','mobile_evidence'])
            self.assertEqual(final.stat().st_mtime_ns,before)
            self.assertIn('standard',release['reused'])
            again=produce.produce(p,chunk=.2)
            self.assertEqual(again['stages'],['fonts'])
            self.assertIn('mobile_evidence',again['reused'])
            # Every generated evidence byte is bound; tampering reruns that group.
            image=next((p/'review/mobile').rglob('*.png'))
            image.write_bytes(b'broken evidence')
            repaired=produce.produce(p,chunk=.2)
            self.assertIn('standard',repaired['reused'])
            self.assertIn('mobile_evidence',repaired['stages'])
            # Reference mix and event edits cannot reuse old final or checks.
            for artifact in [p/'audio/score.wav',p/'audio/events.json',final]:
                artifact.write_bytes(b'broken generated artifact')
                rebuilt=produce.produce(p,chunk=.2,mode='standard')
                self.assertNotIn('standard',rebuilt['reused'])
                self.assertIn('sound',rebuilt['stages'])
            # A same-duration source edit is a new input identity.
            source=p/'film.js';source.write_text(source.read_text().replace('#abc','#cba'))
            changed=produce.produce(p,chunk=.2,mode='standard')
            self.assertNotEqual(changed['input_sha256'],standard['input_sha256'])
            self.assertNotIn('standard',changed['reused'])
            spec=json.loads((p/'audio/events.json').read_text())
            provenance.validate_video(final,spec,provenance.validate_events(p,spec),kind='final')
