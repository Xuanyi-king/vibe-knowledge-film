from pathlib import Path
import unittest
from engine import render
ROOT=Path(__file__).resolve().parents[1]
READY=(ROOT/'engine/vendor/three/three.module.min.js').exists()

class MirrorTest(unittest.TestCase):
    @unittest.skipUnless(READY,'optional Three.js portrait assets')
    def test_orientation_conditions_and_complete_story_replay(self):
        self.assertTrue((ROOT/'examples/mirror/index.html').exists(),'complete mirror film missing')
        if not (ROOT/'examples/mirror/assets/piano/bank.json').exists():self.skipTest('optional licensed piano bank: run prepare_instrument')
        def check(pg):
            self.assertEqual(pg.evaluate('END'),112)
            a=render.shot(pg,17);render.shot(pg,110);self.assertEqual(a,render.shot(pg,17))
            r=pg.evaluate('MIRROR.inspect()');self.assertEqual(r['pixelMirrorError'],0)
            self.assertEqual(r['study'],{'pairs':28,'selfMirror':20,'partnerOrdinary':19,'choices':5})
            for row in pg.evaluate('VK_CHECKS.list()'):
                render.shot(pg,row['time']);result=pg.evaluate('id=>VK_CHECKS.measure(id)',row['id']);self.assertTrue(result['passed'],result)
        render.with_page(ROOT/'examples/mirror',check)

    @unittest.skipUnless(READY,'optional Three.js portrait assets')
    def test_distance_changes_projection_not_face_geometry(self):
        self.assertTrue((ROOT/'examples/mirror/index.html').exists(),'controlled portrait scene missing')
        if not (ROOT/'examples/mirror/assets/piano/bank.json').exists():self.skipTest('optional licensed piano bank')
        def check(pg):
            render.shot(pg,56);far=pg.evaluate('MIRROR.inspect()')
            render.shot(pg,67);near=pg.evaluate('MIRROR.inspect()')
            self.assertAlmostEqual(far['distance'],1.5);self.assertAlmostEqual(near['distance'],.3048)
            self.assertEqual(far['geometryHash'],near['geometryHash'])
            self.assertAlmostEqual(far['cheekWidth'],near['cheekWidth'],places=5)
            self.assertGreater(near['noseWidth']/near['cheekWidth'],far['noseWidth']/far['cheekWidth']*1.02)
            self.assertEqual(near['glError'],0)
        render.with_page(ROOT/'examples/mirror',check)

    @unittest.skipUnless(READY,'optional Three.js portrait assets')
    def test_portrait_aspect_is_preserved_in_opening_and_ending(self):
        if not (ROOT/'examples/mirror/assets/piano/bank.json').exists():self.skipTest('optional licensed piano bank')
        def check(pg):
            pg.evaluate("""()=>{window._ratios=[];const original=CanvasRenderingContext2D.prototype.drawImage;CanvasRenderingContext2D.prototype.drawImage=function(image,...v){if(image.width===1122&&image.height===1402){const [sw,sh,dw,dh]=v.length===8?[v[2],v[3],v[6],v[7]]:v.length===4?[image.width,image.height,v[2],v[3]]:[image.width,image.height,image.width,image.height];window._ratios.push([dw/sw,dh/sh]);}return original.call(this,image,...v);};}""")
            for t in [6,17,100,110]:
                pg.evaluate('window._ratios=[]');render.shot(pg,t);ratios=pg.evaluate('window._ratios')
                self.assertGreaterEqual(len(ratios),2)
                for x,y in ratios:self.assertAlmostEqual(x,y,places=6,msg=f'{t}s stretched face: x={x}, y={y}')
        render.with_page(ROOT/'examples/mirror',check)
