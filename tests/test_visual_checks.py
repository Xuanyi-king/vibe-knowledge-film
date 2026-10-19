import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from engine import render

ROOT=Path(__file__).resolve().parents[1]

class VisualChecksTest(unittest.TestCase):
    def test_rendered_condition_fails_when_motion_is_retimed_without_sound(self):
        self.assertTrue((ROOT/'engine/vk-checks.mjs').exists(),'declarative scene condition API missing')
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'review').mkdir()
            (p/'index.html').write_text('<canvas id="stage"></canvas><script src="/engine/vk.js"></script><script src="film.js"></script>')
            code="""Promise.all([import('/engine/vk-motion.mjs'),import('/engine/vk-checks.mjs')]).then(([M,C])=>{
              const state={x:0};const S=M.score({end:.4,events:[{id:'hit',start:.2,duration:.1,sound:{kind:'impact'}}]});
              window.VK_SCORE=S;window.VK_CHECKS=C.visualChecks(S,[{id:'arrival',event:'hit',min:1.999,max:2.001,unit:'px',measure:()=>state.x}]);
              VK.film({dur:.4,grain:0,draw(fr,t){state.x=t*10;fr.rect(state.x,0,10,10,{fill:'#aaa'})}});
            });"""
            for text,passed in [(code,True),(code.replace('state.x=t*10','state.x=(t-.1)*10'),False)]:
                (p/'film.js').write_text(text);render.events(p)
                r=subprocess.run([sys.executable,str(ROOT/'scripts/check_visual.py'),str(p)],capture_output=True,text=True)
                self.assertEqual(r.returncode,0 if passed else 1,r.stderr+r.stdout)
                report=json.loads((p/'review/visual-sync.json').read_text())
                self.assertEqual(report['layer'],'declared_visual_action_sync')
                self.assertEqual(report['passed'],passed)
                self.assertEqual(report['checks'][0]['frame'],6)
                self.assertEqual(report['checks'][0]['event'],'hit')
                self.assertTrue((p/'review/visual/frame_000006.png').exists())
                if passed:green=report
            # Browser exceptions must invalidate an earlier green report too.
            (p/'film.js').write_text(code.replace('measure:()=>state.x','measure:()=>{throw Error("probe explosion")}'))
            render.events(p);(p/'review/visual-sync.json').write_text(json.dumps(green))
            bad=subprocess.run([sys.executable,str(ROOT/'scripts/check_visual.py'),str(p)],capture_output=True,text=True)
            self.assertEqual(bad.returncode,1)
            self.assertFalse(json.loads((p/'review/visual-sync.json').read_text())['passed'])
            # A failed stale-input run must not leave a previous green report.
            (p/'film.js').write_text(code)
            bad=subprocess.run([sys.executable,str(ROOT/'scripts/check_visual.py'),str(p)],capture_output=True,text=True)
            self.assertEqual(bad.returncode,1)
            self.assertFalse(json.loads((p/'review/visual-sync.json').read_text())['passed'])

    def test_invalid_declarations_and_nonfinite_measurements_fail(self):
        def run(pg):
            result=pg.evaluate('''async()=>{
              const {score}=await import('/engine/vk-motion.mjs');const {visualChecks}=await import('/engine/vk-checks.mjs');
              const S=score({end:.4,events:[{id:'hit',start:.2,duration:.2}]});
              const valid={id:'test',event:'hit',min:0,max:1,measure:()=>NaN};
              const fails=d=>{try{visualChecks(S,d);return false}catch{return true}};
              return {nan:visualChecks(S,[valid]).measure('test').passed,
                duplicate:fails([valid,valid]),unknown:fails([{...valid,event:'missing'}]),
                range:fails([{...valid,min:2,max:1}]),lastFrame:fails([{...valid,anchor:'end'}])};
            }''')
            self.assertFalse(result['nan'])
            for key in ['duplicate','unknown','range','lastFrame']:self.assertTrue(result[key],key)
        render.with_page(ROOT/'examples/fold_C',run)
