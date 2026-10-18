import os
from pathlib import Path
import unittest
from engine import render

ROOT=Path(__file__).resolve().parents[1]


class SceneTest(unittest.TestCase):
    @unittest.skipUnless((ROOT/'engine/vendor/three/three.module.min.js').exists(), 'optional Three.js assets: run engine/get_scene_assets.py')
    def test_complex_scene_replays_and_preserves_link_lengths(self):
        self.assertTrue((ROOT/'engine/vk-scene.mjs').exists(), 'reusable scene layer missing')
        def check(pg):
            self.assertTrue(pg.evaluate("async()=>{const M=await import('/engine/vk-scene.mjs');if(!M.surface)return false;const a=M.surface({seed:7}),b=M.surface({seed:7});const same=a.roughnessMap.image.toDataURL()===b.roughnessMap.image.toDataURL();a.dispose();b.dispose();return same;}"),'seeded reusable material finish missing')
            first=render.shot(pg,2)
            render.shot(pg,5);render.shot(pg,0)
            self.assertEqual(first,render.shot(pg,2))
            info=pg.evaluate('SHOT.inspect()')
            self.assertTrue(info['shadow'])
            self.assertGreater(info['meshes'],15)
            self.assertLess(info['maxLinkError'],1e-7)
            self.assertEqual(info['glError'],0)
            pg.evaluate('SHOT.flat(true)')
            self.assertNotEqual(first,render.shot(pg,2))
        render.with_page(ROOT/'examples/governor_scene',check)


if __name__=='__main__':unittest.main()

class ResonanceTest(unittest.TestCase):
    @unittest.skipUnless((ROOT/'engine/vendor/three/three.module.min.js').exists(), 'optional Three.js assets')
    def test_contact_clock_and_final_composition_replay(self):
        def check(pg):
            a=render.shot(pg,3.8);render.shot(pg,7);render.shot(pg,.5)
            self.assertEqual(a,render.shot(pg,3.8))
            strike=pg.evaluate('SHOT.inspect(2)');before=pg.evaluate('SHOT.inspect(1.8)')
            self.assertAlmostEqual(strike['hammerZ']-.17,.02,delta=.005)
            self.assertGreater(before['hammerZ'],strike['hammerZ'])
            damp=pg.evaluate('SHOT.inspect(16/3)')
            self.assertAlmostEqual(damp['damperX']-.125,.92,delta=.02)
            self.assertEqual(damp['glError'],0)
            data=pg.evaluate('VK_SCORE.json()')
            self.assertEqual(next(e for e in data['events'] if e['id']=='strike')['start'],strike['hit'])
            self.assertAlmostEqual(next(e for e in data['events'] if e['id']=='damp')['start'],damp['damp'])
        render.with_page(ROOT/'examples/resonance',check)
