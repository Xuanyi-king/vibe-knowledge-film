import unittest
from pathlib import Path
from engine import render
ROOT=Path(__file__).resolve().parents[1]

class GeoTest(unittest.TestCase):
    def test_differential_scales_and_projection_library(self):
        self.assertTrue((ROOT/'engine/vk-geo.mjs').exists(),'reusable cartographic adapter missing')
        def check(pg):
            r=pg.evaluate('''async()=>{const G=await import('/engine/vk-geo.mjs');return [G.localScale(0,0),G.localScale(60,0),G.localScale(60,1)]}''')
            self.assertAlmostEqual(r[0]['area'],1)
            self.assertAlmostEqual(r[1]['x'],2);self.assertAlmostEqual(r[1]['y'],2);self.assertAlmostEqual(r[1]['area'],4)
            self.assertAlmostEqual(r[2]['x'],2);self.assertAlmostEqual(r[2]['y'],.5);self.assertAlmostEqual(r[2]['area'],1)
        render.with_page(ROOT/'examples/fold_C',check)

    @unittest.skipUnless((ROOT/'engine/vendor/geo/d3-geo.min.js').exists(),'optional geographic assets')
    def test_real_projection_and_land_orientation(self):
        def check(pg):
            r=pg.evaluate('''async()=>{const G=await import('/engine/vk-geo.mjs');const A=await G.loadAtlas();const p=G.cylindrical(0).scale(1).translate([0,0]);return {p:p([0,60]),area:A.d3.geoArea(A.land),count:A.land.features.length}}''')
            import math
            self.assertAlmostEqual(-r['p'][1],math.log(math.tan(math.pi/4+math.pi/6)))
            self.assertGreater(r['area'],2);self.assertLess(r['area'],5);self.assertGreater(r['count'],100)
        render.with_page(ROOT/'examples/fold_C',check)
