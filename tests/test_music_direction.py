import json,subprocess,tempfile,unittest
import sys
from pathlib import Path
import numpy as np
from scipy.io import wavfile
from scripts import analyze_music as A

class MusicDirectionTest(unittest.TestCase):
    def prepare(self, module, project, config):
        (project/'music.json').write_text(json.dumps(config),encoding='utf-8')
        return module.prepare(project,config)

    def signal(self,p,bpm=100):
        sr=12000;x=np.zeros(sr*12,dtype=np.float32)
        for t in np.arange(.2,11.9,60/bpm):
            i=round(t*sr);x[i:i+180]+=.5*np.hanning(180)
        wavfile.write(p,sr,x)

    def test_multiple_tempi_and_resampling_reanalyzed_not_assumed(self):
        for bpm in [84,120,150]:
            with tempfile.TemporaryDirectory() as d:
                p=Path(d)/'x.wav';self.signal(p,bpm)
                r=A.analyze_file(p,Path(d)/'a.json')
                self.assertTrue(any(abs(c['bpm']-bpm)<2 for c in r['tempo_candidates']),r['tempo_candidates'])
                self.assertTrue(any(abs(c['bpm']-bpm)<3 for c in r['envelope_tempo_candidates']),r['envelope_tempo_candidates'])
                self.assertFalse(r['grid_verified']);self.assertIsNone(r['downbeats'])
                self.assertIn('envelope_autocorrelation',r['methods'])

    def test_content_cache_and_manual_annotations_are_bound_to_source(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);audio=p/'x.wav';out=p/'a.json';self.signal(audio)
            r=A.analyze_file(audio,out);same=A.analyze_file(audio,out)
            self.assertEqual(r['identity'],same['identity'])
            edit={'source_sha256':r['source_sha256'],'reviewer':'fixture ground truth',
                  'beats':[.2,.8,1.4],'downbeats':[.2],'phrases':[{'time':.2,'label':'open'}]}
            fixed=A.analyze_file(audio,out,annotations=edit)
            self.assertFalse(fixed['grid_verified']);self.assertTrue(fixed['annotated_points_verified']);self.assertEqual(fixed['beats'],edit['beats'])
            self.signal(audio,120)
            with self.assertRaisesRegex(ValueError,'source'):A.analyze_file(audio,out,annotations=edit)
            changed=A.analyze_file(audio,out);self.assertNotEqual(changed['identity'],r['identity'])

    def test_corrupt_source_preserves_previous_analysis(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);audio=p/'x.wav';out=p/'a.json';self.signal(audio);A.analyze_file(audio,out);old=out.read_bytes()
            audio.write_bytes(b'bad audio')
            with self.assertRaises((RuntimeError,subprocess.CalledProcessError)):A.analyze_file(audio,out)
            self.assertEqual(out.read_bytes(),old)

    def test_actual_speed_change_has_a_new_period_and_identity(self):
        from scipy.signal import resample_poly
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);audio=p/'x.wav';out=p/'a.json';self.signal(audio,100)
            a=A.analyze_file(audio,out);sr,x=wavfile.read(audio)
            wavfile.write(audio,sr,resample_poly(x,4,5)) # duration contracts; actual tempo 125, pitch changes
            b=A.analyze_file(audio,out)
            self.assertNotEqual(a['identity'],b['identity']);self.assertAlmostEqual(b['duration'],9.6,places=3)
            self.assertTrue(any(abs(c['bpm']-125)<2 for c in b['tempo_candidates']))

    def test_external_clip_mapping_fallback_and_source_change(self):
        from scripts import prepare_music as P
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'assets').mkdir();audio=p/'assets/music.wav';self.signal(audio)
            cfg={'mode':'custom','src':'assets/music.wav','end':4,'rights':{'scope':'embed','statement':'Original test signal; CC0'},
                 'source_sha256':A.digest(audio),
                 'clips':[{'id':'bed','start':0,'source_in':.2,'duration':4,'fade_in':.2,'fade_out':.4}],
                 'anchors':[{'id':'discovery','clip':'bed','source_time':1.4,'purpose':'reveal'}]}
            r=self.prepare(P,p,cfg);self.assertEqual(r['selected'],'custom');self.assertAlmostEqual(r['anchors']['discovery'],1.2)
            self.assertEqual(r['events'][0]['sound']['trim'],.2);self.assertEqual(r['events'][0]['sound']['kind'],'sample')
            self.assertTrue((p/'assets/music-plan.mjs').exists())
            self.assertEqual(self.prepare(P,p,{'mode':'signature','end':4})['selected'],'original')
            self.assertEqual(self.prepare(P,p,{**cfg,'mode':'signature','rights':{'scope':'platform-only','statement':'platform library only'}})['selected'],'platform-later')
            cfg['clips'][0]['duration']=20
            old=(p/'assets/music-plan.json').read_bytes()
            with self.assertRaises(ValueError):self.prepare(P,p,cfg)
            self.assertEqual((p/'assets/music-plan.json').read_bytes(),old)

    def test_prepared_loader_rejects_replaced_music_before_seek(self):
        from scripts import prepare_music as P
        from engine import render
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'assets').mkdir();audio=p/'assets/music.wav';self.signal(audio)
            self.prepare(P,p,{'mode':'custom','src':'assets/music.wav','source_sha256':A.digest(audio),'end':2,'rights':{'scope':'embed','statement':'CC0 test signal'},
                         'clips':[{'id':'bed','start':0,'source_in':0,'duration':2}],
                         'anchors':[{'id':'reveal','clip':'bed','source_time':1}]})
            (p/'index.html').write_text('''<canvas id="stage"></canvas><script src="/engine/vk.js"></script>
              <script type="module">import {MUSIC,anchor} from './assets/music-plan.mjs';
              import {score} from '/engine/vk-motion.mjs';window.VK_SCORE=score({end:2,events:[...MUSIC.events,{id:'reveal',start:anchor('reveal')}]});
              VK.film({dur:2,grain:0,draw(fr,t){fr.rect(t*10,0,20,20,{fill:'#ddd'})}});</script>''')
            def inspect(pg):
                self.assertEqual(pg.evaluate('VK_SCORE.event("reveal").start'),1)
                a=render.shot(pg,1);render.shot(pg,0);self.assertEqual(a,render.shot(pg,1))
            render.with_page(p,inspect)
            original=json.loads((p/'music.json').read_text())
            for edit in [{'mode':'original'},{'mode':'signature','rights':{'scope':'platform-only'}}]:
                (p/'music.json').write_text(json.dumps(edit))
                with self.assertRaisesRegex(RuntimeError,'music config fingerprint'):render.with_page(p,lambda pg:None)
            self.prepare(P,p,original)
            self.signal(audio,120)
            with self.assertRaisesRegex(RuntimeError,'music source fingerprint'):render.with_page(p,lambda pg:None)

    def test_explicit_crossfade_and_reuse_permissions(self):
        from scripts import prepare_music as P
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'assets').mkdir();audio=p/'assets/music.wav';self.signal(audio)
            cfg={'mode':'custom','src':'assets/music.wav','source_sha256':A.digest(audio),'end':8,
                 'rights':{'scope':'embed','statement':'CC0 generated signal'},
                 'clips':[{'id':'a','start':0,'source_in':0,'duration':4,'fade_out':.5},
                          {'id':'b','start':3.5,'source_in':4,'duration':4,'fade_in':.5}]}
            self.assertEqual(len(self.prepare(P,p,cfg)['events']),2)
            cfg['clips'][1]['start']=3
            with self.assertRaisesRegex(ValueError,'crossfade'):self.prepare(P,p,cfg)
            cfg['clips'][1].update(start=3.5,source_in=0)
            with self.assertRaisesRegex(ValueError,'repeated source'):self.prepare(P,p,cfg)
            cfg['allow_source_reuse']=True
            with self.assertRaisesRegex(ValueError,'permission'):self.prepare(P,p,cfg)
            cfg['rights']['allows_loop']=True
            self.assertEqual(len(self.prepare(P,p,cfg)['events']),2)

    def test_optional_production_prepares_and_encodes_existing_sample_path(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'assets').mkdir();audio=p/'assets/music.wav';self.signal(audio)
            cfg={'mode':'custom','src':'assets/music.wav','source_sha256':A.digest(audio),'end':2,
                 'rights':{'scope':'embed','statement':'CC0 generated test signal'},
                 'clips':[{'id':'bed','start':0,'source_in':0,'duration':2}],
                 'anchors':[{'id':'reveal','clip':'bed','source_time':.8}]}
            (p/'music.json').write_text(json.dumps(cfg))
            (p/'index.html').write_text('''<canvas id="stage"></canvas><script src="/engine/vk.js"></script>
              <script type="module">import {MUSIC,anchor} from './assets/music-plan.mjs';
              import {score} from '/engine/vk-motion.mjs';import {visualChecks} from '/engine/vk-checks.mjs';
              const s=score({end:2,events:[...MUSIC.events,{id:'reveal',start:anchor('reveal')}]});window.VK_SCORE=s;
              let x=0;window.VK_CHECKS=visualChecks(s,[{id:'arrival',event:'reveal',min:7.99,max:8.01,measure:()=>x}]);
              VK.film({dur:2,grain:0,draw(fr,t){x=t*10;fr.rect(x,0,20,20,{fill:'#ddd'})}});</script>''')
            html=(p/'index.html').read_text()
            (p/'film.js').write_text(html.split('<script type="module">')[1].split('</script>')[0])
            (p/'index.html').write_text('<canvas id="stage"></canvas><script src="/engine/vk.js"></script><script type="module" src="film.js"></script>')
            root=Path(__file__).resolve().parents[1]
            r=subprocess.run([sys.executable,str(root/'scripts/produce.py'),str(p),'--chunk','1'],capture_output=True,text=True,timeout=300)
            self.assertEqual(r.returncode,0,r.stdout+r.stderr)
            status=json.loads((p/'review/production.json').read_text())
            self.assertIn('music_preparation',status['stages'])
            self.assertEqual(status['status'],'technical_complete_needs_subjective_review')
            self.assertEqual(json.loads((p/'audio/sync.json').read_text())['failed'],[])
            self.assertTrue(json.loads((p/'review/visual-sync.json').read_text())['passed'])
