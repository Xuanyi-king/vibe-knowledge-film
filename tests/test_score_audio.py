import importlib.util
import tempfile
from pathlib import Path
import unittest
import numpy as np
from engine import audio

ROOT=Path(__file__).resolve().parents[1]

class ScoreAudioTest(unittest.TestCase):
    def load(self):
        self.assertTrue((ROOT/'engine/score_audio.py').exists(),'shared-score sound renderer missing')
        from engine import score_audio
        return score_audio

    def spec(self):
        return {'version':1,'end':2,'fps':30,'events':[
            {'id':'hit','start':.25,'end':1.5,'action':'collision','intensity':.6,
             'sound':{'kind':'impact','material':'metal','pan':-.5}},
            {'id':'rub','start':1,'end':1.7,'action':'sliding','speed':.5,
             'sound':{'kind':'friction','material':'felt','gain':.2}},
            {'id':'note','start':.1,'end':.8,'sound':{'kind':'pluck','midi':60,'track':'music','gain':.05}}]}

    def test_materials_repeat_order_independent_and_stems_sum(self):
        m=self.load();s=self.spec();x,stems,report=m.render(s,ROOT)
        self.assertEqual(x.shape,(96000,2));self.assertTrue(np.isfinite(x).all())
        self.assertGreater(np.max(np.abs(x)),.01)
        self.assertTrue(np.allclose(x,sum(stems.values())))
        s['events'].reverse();again,_,_=m.render(s,ROOT)
        self.assertTrue(np.allclose(x,again,atol=1e-14))
        self.assertEqual(report['events'][0]['scheduled_sample'],12000)
        a=m.voice(self.spec()['events'][0],audio.SR,ROOT)
        wood=self.spec()['events'][0];wood['sound']['material']='wood'
        self.assertFalse(np.allclose(a,m.voice(wood,audio.SR,ROOT)))
        self.assertEqual(float(np.max(np.abs(stems['sfx'][:12000]))),0)

    def test_automation_silence_samples_and_invalid_events(self):
        m=self.load();s=self.spec();s['silence']=[[1.8,2]]
        s['tracks']={'sfx':{'gain':[[0,1],[1.2,1],[1.3,0]]}}
        x,stems,_=m.render(s,ROOT)
        self.assertLess(float(np.max(np.abs(stems['sfx'][int(1.4*audio.SR):]))),1e-10)
        self.assertEqual(float(np.max(np.abs(x[int(1.82*audio.SR):]))),0)
        for e in [{'id':'bad','start':3,'end':4,'sound':{'kind':'impact'}},
                  {'id':'bad','start':0,'end':1,'sound':{'kind':'unknown'}}]:
            with self.assertRaises(ValueError):m.render({'version':1,'end':2,'events':[e]},ROOT)
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);audio.write_wav(p/'hit.wav',np.ones((4800,2))*.1)
            e={'id':'sample','start':.5,'end':.6,'sound':{'kind':'sample','src':'hit.wav','license':'user-owned','anchor':.02}}
            x,_,r=m.render({'version':1,'end':1,'events':[e]},p)
            self.assertEqual(r['events'][0]['scheduled_sample'],23040)
            self.assertGreater(np.abs(x[23040:24000]).max(),0)
            e['sound']['pan']=-1
            left=m.voice(e,48000,p)
            self.assertLess(np.abs(left[:,1]).max(),1e-10)
            self.assertGreater(np.abs(left[:,0]).max(),.01)
            del e['sound']['license']
            with self.assertRaisesRegex(ValueError,'license'):m.render({'version':1,'end':1,'events':[e]},p)

    def test_encoded_sync_detects_delay_instead_of_assuming_aac_offset(self):
        m=self.load();rng=np.random.default_rng(3);a=rng.normal(size=12000)
        b=np.r_[np.zeros(321),a,np.zeros(100)]
        measured=m.delay(a,b,48000,max_seconds=.02)
        self.assertAlmostEqual(measured['lag_seconds'],321/48000,places=6)
        self.assertGreater(measured['correlation'],.999)
        with self.assertRaisesRegex(ValueError,'silent'):m.delay(np.zeros(100),np.zeros(100),48000)
