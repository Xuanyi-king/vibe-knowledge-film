"""Shared clock + closed-form motion, tested in the real browser runtime."""
import unittest
from pathlib import Path
from engine import render

ROOT = Path(__file__).resolve().parents[1]

class ChoreographyTest(unittest.TestCase):
    def test_tempo_inverse_contact_and_seek_order(self):
        self.assertTrue((ROOT/'engine/vk-motion.mjs').exists(), 'public choreography module missing')
        def check(pg):
            result=pg.evaluate('''async()=>{
              const M=await import('/engine/vk-motion.mjs');
              const score=M.score({end:8,tempo:[{beat:0,bpm:120},{beat:4,bpm:60}],shots:[{id:'a',start:0,end:8}],events:[
                {id:'hit',shot:'a',beat:5,action:'collision',sound:{kind:'impact',material:'metal'}}]});
              const e=score.event('hit');
              const inverse=[0,1,3,5,7].map(t=>score.time(score.beat(t))-t);
              const motion=t=>M.spring(t-e.start,{from:1,to:0,frequency:3,damping:.3});
              const a=motion(4);motion(7);motion(0);const b=motion(4);
              return {start:e.start,inverse,a,b,before:motion(2),contact:motion(3),
                settled:motion(7),path:M.path([[0,0],[0,1],[1,1],[1,0]],.5),
                track:M.track([[0,[0,0]],[1,[2,4]],[2,[2,4]]],1.5),
                critical:M.spring(20,{from:1,to:0,frequency:2,damping:1}),
                over:M.spring(20,{from:1,to:0,frequency:2,damping:2}),
                impulse:M.impulse(0,{velocity:2,frequency:3,damping:.2}),
                contactProfile:typeof M.contact==='function'?M.contact(2,{time:2,from:1.8,to:.19,lead:.7,restitution:.35}):null,
                cameraReplay:(()=>{const c={fov:35,position:{fromArray(){}},lookAt(){},updateProjectionMatrix(){}};
                  const keys=[[0,{position:[0,0,5],target:[0,0,0]}],[1,{position:[0,0,3],target:[0,0,0],fov:60}]];
                  M.camera(c,keys,.5);const first=c.fov;M.camera(c,keys,0);M.camera(c,keys,.5);return[first,c.fov];})()};
            }''')
            self.assertEqual(result['cameraReplay'][0],result['cameraReplay'][1],'omitted camera FOV depends on previous seek')
            self.assertEqual(result['start'],3)
            self.assertLess(max(map(abs,result['inverse'])),1e-10)
            self.assertEqual(result['a'],result['b'])
            self.assertEqual(result['before'],1)
            self.assertEqual(result['contact'],1)
            self.assertLess(abs(result['settled']),1e-6)
            self.assertEqual(result['path'],[.5,.75])
            self.assertEqual(result['track'],[2,4])
            self.assertLess(abs(result['critical']),1e-6)
            self.assertLess(abs(result['over']),1e-6)
            self.assertEqual(result['impulse'],0)
            self.assertIsNotNone(result['contactProfile'],'shared contact/recoil profile missing')
            self.assertAlmostEqual(result['contactProfile']['position'],.19)
            self.assertAlmostEqual(result['contactProfile']['incomingSpeed'],4.6)
            for js in ["M.score({end:2,events:[{id:'x',start:3}]})",
                       "M.score({end:2,events:[{id:'x',start:1},{id:'x',start:1}]})",
                       "M.track([[1,0],[1,2]],1)"]:
                self.assertTrue(pg.evaluate("async()=>{const M=await import('/engine/vk-motion.mjs');try{"+js+";return false}catch{return true}}"))
        render.with_page(ROOT/'examples/fold_C',check)
