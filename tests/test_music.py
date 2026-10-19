import unittest
import importlib.util
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]

class MusicTest(unittest.TestCase):
    def test_click_grid_and_silence_do_not_invent_downbeats(self):
        self.assertTrue((ROOT/'scripts/analyze_music.py').exists(),'music analysis missing')
        spec=importlib.util.spec_from_file_location('music',ROOT/'scripts/analyze_music.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        sr=12000;x=np.zeros(sr*8)
        for t in np.arange(.25,8,.5):
            i=int(t*sr);x[i:i+100]=np.hanning(100)
        r=m.analyze(x,sr)
        self.assertTrue(any(abs(c['bpm']-120)<3 for c in r['tempo_candidates']))
        self.assertGreaterEqual(len(r['onsets']),14)
        self.assertTrue(all(min(abs(t-a) for a in r['onsets'])<.04 for t in [.25,.75,1.25]))
        self.assertIsNone(r['downbeats']);self.assertFalse(r['grid_verified'])
        empty=m.analyze(np.zeros(sr),sr)
        self.assertEqual(empty['tempo_candidates'],[]);self.assertEqual(empty['onsets'],[])
