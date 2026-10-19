"""Independent energy-integral and finite-difference checks of the film model."""
import importlib.util
import math
from pathlib import Path
import unittest
from scipy.integrate import quad

ROOT = Path(__file__).resolve().parents[1]
from engine import render


class PhysicsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = render.with_page(ROOT / 'examples/descent_studio', lambda pg: pg.evaluate('''() => {
          const p=PHYS, times=[.03,.15,.3,.5], eps=1e-5;
          return {g:p.g,X:p.X,Y:p.Y,a:p.a,theta:p.theta,Tc:p.Tc,Ts:p.Ts,L:p.L,Lc:p.Lc,
            endpoints:['c','s'].map(k=>p.sample(k,100)),
            samples:['c','s'].flatMap(k=>times.map(t=>({kind:k,t,
              before:p.sample(k,t-eps),at:p.sample(k,t),after:p.sample(k,t+eps)})))};
        }'''))

    def test_travel_time_from_energy_integral(self):
        p=self.data
        self.assertEqual((p['g'],p['X'],p['Y']),(9.81,1,.6))
        # Independently integrate ds / sqrt(2 g y); avoid the removable cusp
        # singularity by supplying its limit. This does not reuse film time().
        a,g,q=p['a'],p['g'],p['theta']
        def ds(u): return math.hypot(a*(1-math.cos(u)),a*math.sin(u))
        def integrand(u):
            return math.sqrt(a/g) if abs(u)<1e-6 else ds(u)/math.sqrt(2*g*a*(1-math.cos(u)))
        time=quad(integrand,0,q)[0]
        self.assertAlmostEqual(time,p['Tc'],places=9)
        self.assertAlmostEqual(quad(ds,0,q)[0],p['Lc'],places=9)
        straight=quad(lambda u: p['L']/math.sqrt(2*g*p['Y']*u),0,1)[0]
        self.assertAlmostEqual(straight,p['Ts'],places=9)
        self.assertLess(p['Tc'],p['Ts'])
        self.assertGreater(p['Lc'],p['L'])

    def test_positions_speed_and_arrivals(self):
        p=self.data
        for endpoint in p['endpoints']:
            self.assertAlmostEqual(endpoint['x'],p['X'],places=10)
            self.assertAlmostEqual(endpoint['y'],p['Y'],places=10)
        for s in p['samples']:
            with self.subTest(kind=s['kind'],t=s['t']):
                velocity=math.hypot(s['after']['x']-s['before']['x'],s['after']['y']-s['before']['y'])/2e-5
                self.assertAlmostEqual(velocity,s['at']['v'],places=7)
                self.assertAlmostEqual(s['at']['v']**2,2*p['g']*s['at']['y'],places=9)
                self.assertAlmostEqual(math.hypot(s['at']['tx'],s['at']['ty']),1,places=10)


if __name__ == '__main__': unittest.main()
