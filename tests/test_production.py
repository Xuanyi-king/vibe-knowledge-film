import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]

class ProductionTest(unittest.TestCase):
    def test_one_entry_completes_pipeline_and_reports_blocked_inspection(self):
        self.assertTrue((ROOT/'scripts/produce.py').exists(),'production entry missing')
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            (p/'index.html').write_text('<canvas id="stage"></canvas><script src="/engine/vk.js"></script><script src="film.js"></script>')
            (p/'film.js').write_text("""Promise.all([import('/engine/vk-motion.mjs'),import('/engine/vk-checks.mjs')]).then(([M,C])=>{
              let x=0;const S=M.score({end:.4,events:[{id:'hit',start:.2,duration:.1,sound:{kind:'impact'}}]});
              window.VK_SCORE=S;window.VK_CHECKS=C.visualChecks(S,[{id:'arrival',event:'hit',min:1.99,max:2.01,measure:()=>x}]);
              VK.film({dur:.4,grain:0,draw(fr,t){x=t*10;fr.rect(x,10,20,20,{fill:'#abc'})}});
            });""")
            cmd=[sys.executable,str(ROOT/'scripts/produce.py'),str(p),'--chunk','.2']
            r=subprocess.run(cmd,capture_output=True,text=True)
            self.assertEqual(r.returncode,0,r.stderr+r.stdout)
            report=json.loads((p/'review/production.json').read_text())
            self.assertEqual(report['status'],'technical_complete_needs_subjective_review')
            self.assertEqual(len(report['input_sha256']),64)
            self.assertEqual(len(report['video_sha256']),64)
            self.assertTrue((p/'renders/final.mp4').exists())
            self.assertTrue(json.loads((p/'review/visual-sync.json').read_text())['passed'])
            self.assertEqual(json.loads((p/'audio/sync.json').read_text())['failed'],[])
            old=(p/'renders/final.mp4').read_bytes()
            (p/'film.js').write_text("throw Error('broken source')")
            bad=subprocess.run(cmd,capture_output=True,text=True)
            self.assertNotEqual(bad.returncode,0)
            self.assertEqual((p/'renders/final.mp4').read_bytes(),old)
            self.assertEqual(json.loads((p/'review/production.json').read_text())['status'],'failed')

    def test_force_exit_invalidates_old_success_before_first_step(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'review').mkdir()
            out=p/'review/production.json';out.write_text(json.dumps({'status':'technical_complete_needs_subjective_review'}))
            code="from scripts import produce;from pathlib import Path;import os,sys;produce.subprocess.run=lambda *a,**k:os._exit(7);produce.produce(Path(sys.argv[1]))"
            r=subprocess.run([sys.executable,'-c',code,str(p)],cwd=ROOT,capture_output=True)
            self.assertEqual(r.returncode,7)
            self.assertEqual(json.loads(out.read_text())['status'],'running')

    def test_source_edit_during_final_media_check_cannot_publish_success(self):
        from scripts import produce
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'film.js').write_text('// original')
            def step(cmd,**kwargs):
                if str(cmd[1]).endswith('check_media.py'):(p/'film.js').write_text('// saved during final media inspection')
            meta={'end':.4,'fps':30,'score':True,'checks':1}
            with patch.object(produce.subprocess,'run',side_effect=step),patch.object(produce.render,'with_page',return_value=meta):
                with self.assertRaisesRegex(RuntimeError,'changed during export'):
                    produce.produce(p)
            self.assertEqual(json.loads((p/'review/production.json').read_text())['status'],'failed')
