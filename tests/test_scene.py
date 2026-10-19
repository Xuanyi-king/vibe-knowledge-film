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
            checks=pg.evaluate('VK_CHECKS.list()')
            self.assertTrue({'mallet-contact','felt-contact'}<={d['id'] for d in checks})
            for d in reversed(checks):
                render.shot(pg,d['time'])
                result=pg.evaluate('id=>VK_CHECKS.measure(id)',d['id'])
                self.assertTrue(result['passed'],result)
                self.assertTrue(result['has_sound'])
            self.assertEqual(pg.evaluate('SHOT.inspect(2).glError'),0)
        render.with_page(ROOT/'examples/resonance',check)
