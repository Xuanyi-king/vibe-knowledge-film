"""The complete theme-only creative example: actual drawn states and ending."""
from pathlib import Path
import unittest
from engine import render
ROOT=Path(__file__).resolve().parents[1]

class AtlasTest(unittest.TestCase):
    @unittest.skipUnless((ROOT/'engine/vendor/geo/d3-geo.min.js').exists(),'optional geographic assets')
    def test_complete_film_drawn_scale_layout_and_reverse_seek(self):
        def check(pg):
            self.assertEqual(pg.evaluate('END'),72)
            first=render.shot(pg,18)
            render.shot(pg,71)
            self.assertEqual(first,render.shot(pg,18))
            checks=pg.evaluate('VK_CHECKS.list()')
            self.assertTrue({'latitude-half','x-scale','angle-scale','four-area','one-area','end-complete'}<={c['id'] for c in checks})
            for row in reversed(checks):
                render.shot(pg,row['time'])
                result=pg.evaluate('id=>VK_CHECKS.measure(id)',row['id'])
                self.assertTrue(result['passed'],result)
        render.with_page(ROOT/'examples/atlas',check)
