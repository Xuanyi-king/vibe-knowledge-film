"""Synthetic pipeline fixtures only: never the unavailable Shape of Luck master."""
import copy,json,subprocess,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
from scipy.io import wavfile
from scripts import analyze_music as A,prepare_music as P
from engine import render,score_audio

ROOT=Path(__file__).resolve().parents[1]

class SignatureMusicTest(unittest.TestCase):
    def fixture(self,p):
        folder=p/'assets/private-music';folder.mkdir(parents=True)
        src=folder/'fixture.wav';sr=12000;t=np.arange(sr*3)/sr
        wavfile.write(src,sr,(.08*np.sin(2*np.pi*330*t)).astype(np.float32))
        proof=folder/'rights.txt';proof.write_text('Generated test sine, CC0; test use/edit/reuse/publication permitted.')
        annotations={'source_sha256':A.digest(src),'reviewer':'synthetic fixture ground truth, not subjective listening',
            'master':{'id':'pipeline-test-only','kind':'independent-music','music_only':True,
                      'reviewer':'fixture generator','evidence':'Analytically generated sine, no old SFX'},
            'sections':[{'id':name,'start':i,'end':i+1,'roles':[name],'verified':True}
                        for i,name in enumerate(['question','reveal','close'])]}
        index=folder/'index.json';A.analyze_file(src,index,annotations)
        return {'mode':'signature','end':2,'src':src.relative_to(p).as_posix(),'source_sha256':A.digest(src),
            'signature':{'id':'pipeline-test-only','required':True,'index':index.relative_to(p).as_posix(),'index_sha256':A.digest(index)},
            'rights':{'scope':'embed','statement':proof.read_text(),'allows_edit':True,
                      'evidence':{'src':proof.relative_to(p).as_posix(),'sha256':A.digest(proof)}},
            'clips':[{'id':'first','start':0,'role':'question'}, {'id':'last','start':1,'role':'close'}],
            'anchors':[{'id':'contact','clip':'first','source_time':.6}]}

    def prepare(self,p,cfg):
        (p/'music.json').write_text(json.dumps(cfg),encoding='utf-8');return P.prepare(p)

    def test_lock_never_falls_back_and_index_reuses_analysis(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);cfg=self.fixture(p)
            with patch.object(A,'analyze',side_effect=AssertionError('DSP must not run for each film')):
                plan=self.prepare(p,cfg)
            self.assertEqual(plan['selected'],'signature');self.assertEqual(plan['signature']['id'],'pipeline-test-only')
            self.assertEqual(plan['events'][1]['sound']['trim'],2)
            self.assertEqual(plan['source']['sha256'],cfg['source_sha256'])
            for change in [{'mode':'original'},{'mode':'custom'},{'src':'assets/missing.wav'},
                           {'rights':{'scope':'platform-only'}},{'signature':{**cfg['signature'],'required':False}}]:
                with self.subTest(change=change),self.assertRaises(ValueError):self.prepare(p,{**cfg,**change})
            self.assertEqual(json.loads((p/'assets/music-plan.json').read_text()),plan)

    def test_source_index_annotations_and_plan_changes_are_bound(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);cfg=self.fixture(p);old=self.prepare(p,cfg)
            changed=copy.deepcopy(cfg);changed['clips'][0]['role']='reveal';changed['anchors'][0]['source_time']=1.6
            new=self.prepare(p,changed)
            self.assertNotEqual(old['events'][0]['sound']['trim'],new['events'][0]['sound']['trim'])
            self.assertAlmostEqual(new['anchors']['contact'],.6)
            for edit in ['anchor','range','reuse','identity','annotation']:
                bad=copy.deepcopy(cfg)
                if edit=='anchor':bad['anchors'][0]['source_time']=2.8
                if edit=='range':bad['clips'][0].update(source_in=2.8,duration=1)
                if edit=='reuse':bad['clips'][1]['role']='question'
                if edit=='identity':bad['signature']['id']='shape-of-luck'
                if edit=='annotation':
                    path=p/bad['signature']['index'];index=json.loads(path.read_text());index['annotations']['sections'][0]['end']=.9
                    path.write_text(json.dumps(index));bad['signature']['index_sha256']=A.digest(path)
                with self.subTest(edit=edit),self.assertRaises(ValueError):self.prepare(p,bad)
            cfg=self.fixture_reset_index(p,cfg)
            cfg['clips'][1]['role']='question';cfg['allow_source_reuse']=True;cfg['rights']['allows_loop']=True
            self.assertEqual(len(self.prepare(p,cfg)['events']),2)
            audio=p/cfg['src'];audio.write_bytes(audio.read_bytes()+b'changed')
            with self.assertRaisesRegex(ValueError,'fingerprint'):self.prepare(p,cfg)
            cfg['source_sha256']=A.digest(audio)
            with self.assertRaisesRegex(ValueError,'stale'):self.prepare(p,cfg)

    def fixture_reset_index(self,p,cfg):
        # Rebuild the original fixture index after a deliberately corrupted copy.
        import shutil
        shutil.rmtree(p/'assets/private-music');return self.fixture(p)

    def test_long_story_windows_and_explicit_silence(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);cfg=self.fixture(p)
            for end in [120,180]:
                cfg.update(end=end,clips=[{'id':'a','start':0,'role':'question'},
                    {'id':'reading','start':1,'duration':end-2,'silence':True,'reason':'read and reason'},
                    {'id':'b','start':end-1,'role':'close'}],anchors=[])
                r=self.prepare(p,cfg);self.assertEqual(len(r['events']),2)
                self.assertEqual(r['events'][-1]['start'],end-1)
                self.assertEqual(r['silences'][0]['reason'],'read and reason')

    def test_unreviewed_mix_stale_algorithm_and_missing_rights_fail(self):
        from scripts import signature_music
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);cfg=self.fixture(p);index_path=p/cfg['signature']['index']
            original=json.loads(index_path.read_text())['annotations']
            for edit in ['mix','unheard','sections']:
                notes=copy.deepcopy(original)
                if edit=='mix':notes['master']['kind']='reference-mix'
                if edit=='unheard':notes['master']['music_only']=False
                if edit=='sections':
                    for section in notes['sections']:section['verified']=False
                A.analyze_file(p/cfg['src'],index_path,notes);cfg['signature']['index_sha256']=A.digest(index_path)
                with self.subTest(edit=edit),self.assertRaises(ValueError):self.prepare(p,cfg)
            A.analyze_file(p/cfg['src'],index_path,original);cfg['signature']['index_sha256']=A.digest(index_path)
            with patch.object(signature_music,'analysis_identity',return_value=('changed algorithm','','')):
                with self.assertRaisesRegex(ValueError,'stale'):self.prepare(p,cfg)
            (p/cfg['rights']['evidence']['src']).unlink()
            with self.assertRaisesRegex(ValueError,'fingerprint'):self.prepare(p,cfg)

    def test_director_intent_and_fade_claims_cannot_be_ignored(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);cfg=self.fixture(p)
            bad=copy.deepcopy(cfg);del bad['clips'][0]['role']
            with self.assertRaisesRegex(ValueError,'role|section|cut'):self.prepare(p,bad)
            bad=copy.deepcopy(cfg)
            bad['clips'][0].update(fade_in=.3,fade_out=.3,gain=[[0,0],[.01,.2],[.99,.2],[1,0]])
            with self.assertRaisesRegex(ValueError,'fade'):self.prepare(p,bad)
            bad['clips'][0]['gain']=[[0,0],[.3,.2],[.7,.2],[1,0]]
            self.assertTrue(self.prepare(p,bad)['events'])
            for clip in bad['clips']:clip['gain']=0
            with self.assertRaisesRegex(ValueError,'silent'):self.prepare(p,bad)

    def test_music_duck_and_silence_leave_sfx_and_ambience_intact(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);cfg=self.fixture(p)
            cfg['clips'][0]['gain']=[[0,0],[.05,.25],[.3,.25],[.4,0],[.8,0],[.9,.25],[1,0]]
            plan=self.prepare(p,cfg)
            music=[{**e,'end':e['start']+e['duration']} for e in plan['events']]
            sfx={'id':'contact','start':.6,'end':.8,'sound':{'kind':'impact','gain':.1,'track':'sfx'}}
            ambience={'id':'room','start':0,'end':2,'sound':{'kind':'whoosh','gain':.01,'track':'ambience'}}
            spec={'version':1,'end':2,'events':music+[sfx,ambience]}
            mix,stems,_=score_audio.render(spec,p)
            _,without,_=score_audio.render({**spec,'events':[sfx,ambience]},p)
            self.assertTrue(np.array_equal(stems['sfx'],without['sfx']))
            self.assertTrue(np.allclose(mix,sum(stems.values())))
            a,b=int(.5*48000),int(.75*48000)
            self.assertEqual(np.abs(stems['music'][a:b]).max(),0)
            self.assertGreater(np.abs(stems['sfx'][a:b]).max(),.001)
            self.assertGreater(np.abs(stems['ambience']).max(),0)

    def test_loader_rejects_changed_index_and_rights_before_seek(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);cfg=self.fixture(p);self.prepare(p,cfg)
            (p/'index.html').write_text('<canvas id="stage"></canvas><script src="/engine/vk.js"></script><script type="module" src="film.js"></script>')
            (p/'film.js').write_text("import {MUSIC} from './assets/music-plan.mjs';VK.film({dur:2,grain:0,draw(){}});")
            render.with_page(p,lambda pg:self.assertTrue(pg.evaluate('READY')))
            for name in [cfg['signature']['index'],cfg['rights']['evidence']['src']]:
                path=p/name;data=path.read_bytes();path.write_bytes(data+b' ')
                with self.assertRaisesRegex(RuntimeError,'music binding fingerprint'):render.with_page(p,lambda pg:None)
                path.write_bytes(data)

    def test_series_scaffold_is_locked_while_old_worlds_stay_compatible(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'series'
            subprocess.run([sys.executable,str(ROOT/'scripts/new_film.py'),str(p),'--world','custom',
                            '--duration','150','--series','shape-of-luck'],check=True,capture_output=True)
            cfg=json.loads((p/'music.json').read_text());self.assertEqual(cfg['signature']['id'],'shape-of-luck')
            self.assertTrue(cfg['signature']['required']);self.assertIn('MUSIC.events',(p/'film.js').read_text())
            with self.assertRaises(ValueError):P.prepare(p)

    def test_synthetic_master_stems_and_real_aac_delivery(self):
        from scripts import produce
        with tempfile.TemporaryDirectory(prefix="series 音频 space '") as d:
            p=Path(d);cfg=self.fixture(p)
            cfg['clips'][0]['gain']=[[0,0],[.1,.2],[.3,.2],[.4,0],[.8,0],[.9,.2],[1,0]]
            (p/'music.json').write_text(json.dumps(cfg),encoding='utf-8')
            (p/'index.html').write_text('<canvas id="stage"></canvas><script src="/engine/vk.js"></script><script type="module" src="film.js"></script>')
            (p/'film.js').write_text("""import {MUSIC,anchor} from './assets/music-plan.mjs';
              import {score} from '/engine/vk-motion.mjs';import {visualChecks} from '/engine/vk-checks.mjs';
              const s=score({end:2,events:[...MUSIC.events,
                {id:'contact',start:anchor('contact'),duration:.2,sound:{kind:'impact',gain:.1}},
                {id:'room',start:0,duration:2,sound:{kind:'whoosh',gain:.01,track:'ambience'}}]});
              window.VK_SCORE=s;let x=0;
              window.VK_CHECKS=visualChecks(s,[{id:'contact-position',event:'contact',min:5.99,max:6.01,measure:()=>x}]);
              VK.film({dur:2,grain:0,draw(fr,t){x=t*10;fr.rect(x,10,20,20,{fill:'#abc'})}});""")
            r=produce.produce(p,chunk=1)
            self.assertEqual(r['status'],'technical_complete_needs_subjective_review')
            samples={}
            for name in ['music','sfx','ambience','score']:
                sr,x=wavfile.read(p/f'audio/{name}.wav');self.assertEqual(sr,48000)
                self.assertGreater(np.abs(x).max(),0);samples[name]=x
            a,b=int(.5*sr),int(.75*sr)
            self.assertEqual(np.abs(samples['music'][a:b]).max(),0)
            self.assertGreater(np.abs(samples['sfx'][a:b]).max(),0)
            master=json.loads((p/'review/mastering.json').read_text())
            self.assertLessEqual(master['encoded']['true_peak_dbtp'],-1.5)
            self.assertIsNotNone(master['encoded']['integrated_lufs'])
            self.assertEqual(json.loads((p/'audio/sync.json').read_text())['failed'],[])
            protected=['renders/final.mp4','review/production.json','review/production-cache.json','audio/events.json']
            old={name:(p/name).read_bytes() for name in protected}
            draft=produce.produce(p,mode='draft',preview=('--stills',.6))
            self.assertNotIn('sound',draft['stages'])
            for name,data in old.items():self.assertEqual((p/name).read_bytes(),data)
            delayed=p/'review/delayed-aac.mp4'
            subprocess.run(['ffmpeg','-v','error','-y','-i',str(p/'renders/final.mp4'),
                '-af','adelay=50:all=1','-c:v','copy','-c:a','aac','-shortest',str(delayed)],check=True)
            offset=score_audio.delay(score_audio.decode(p/'audio/score.wav'),score_audio.decode(delayed),48000)
            self.assertAlmostEqual(offset['lag_seconds'],.05,delta=.002)
            self.assertGreater(abs(offset['lag_seconds']),1/30,'real AAC shift must exceed a frame and be detected')
            print('SYNTHETIC pipeline-test-only:',json.dumps({'duration':2,'master':master['encoded'],
                'stem_peak_pcm':{name:int(np.abs(x.astype(np.int64)).max()) for name,x in samples.items()},
                'music_peak_in_duck':int(np.abs(samples['music'][a:b]).max()),
                'sfx_peak_in_duck':int(np.abs(samples['sfx'][a:b]).max()),'delayed_aac':offset,
                'subjective_listening':'not performed'}))

if __name__=='__main__':unittest.main()
