import hashlib,io,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
from scipy.io import wavfile
from engine import render
ROOT=Path(__file__).resolve().parents[1]

class MusicTest(unittest.TestCase):
    def source(self):
        sr=48000;t=np.arange(sr)/sr;b=io.BytesIO();wavfile.write(b,sr,(np.sin(2*np.pi*440*t)*.2).astype(np.float32));return b.getvalue()

    def test_prepared_notes_pitch_cache_and_source_identity(self):
        from scripts.prepare_instrument import prepare
        from engine.score_audio import decode
        data=self.source();sha=hashlib.sha256(data).hexdigest()
        spec={'version':1,'license':'test generated sine / original test asset', 'sources':[{'midi':69,'url':'https://example.invalid/A4.wav','sha256':sha}], 'notes':[69,71],'max_seconds':.8}
        with tempfile.TemporaryDirectory() as d,patch('scripts.prepare_instrument.fetch',return_value=data) as f:
            root=Path(d);a=prepare(root,spec);p=root/a['notes']['71']['src'];raw=decode(p).mean(axis=1)
            freqs=np.fft.rfftfreq(len(raw),1/48000);peak=freqs[np.argmax(abs(np.fft.rfft(raw)))];self.assertAlmostEqual(peak,493.88,delta=2)
            stamp=p.stat().st_mtime_ns;b=prepare(root,spec);self.assertEqual(a,b);self.assertEqual(stamp,p.stat().st_mtime_ns)
            p.write_bytes(b'broken');prepare(root,spec);self.assertGreater(p.stat().st_size,100)
            damaged=dict(a);damaged['notes']={};(root/'assets/piano/bank.json').write_text(json.dumps(damaged))
            repaired=prepare(root,spec);self.assertEqual(set(repaired['notes']),{'69','71'},'empty cached descriptor must be rebuilt')
            spec['max_seconds']=.6;c=prepare(root,spec);self.assertNotEqual(c['identity'],a['identity'])
            self.assertTrue((root/'assets/piano/bank.json').is_file())

    def test_bad_download_or_escape_preserves_previous_bank(self):
        from scripts.prepare_instrument import prepare
        data=self.source();spec={'version':1,'license':'test', 'sources':[{'midi':69,'url':'https://example.invalid/A4.wav','sha256':hashlib.sha256(data).hexdigest()}], 'notes':[69]}
        with tempfile.TemporaryDirectory() as d,patch('scripts.prepare_instrument.fetch',return_value=data):
            root=Path(d);prepare(root,spec);p=root/'assets/piano/bank.json';old=p.read_bytes()
            spec['sources'][0]['sha256']='0'*64
            with self.assertRaisesRegex(ValueError,'SHA256'):prepare(root,spec)
            self.assertEqual(p.read_bytes(),old)
            with self.assertRaisesRegex(ValueError,'inside'):prepare(root,spec,out='../escape')
            spec['license']=''
            with self.assertRaisesRegex(ValueError,'license'):prepare(root,spec)

    def test_phrase_uses_shared_tempo_with_rests_and_release(self):
        self.assertTrue((ROOT/'engine/vk-music.mjs').exists(),'reusable phrase adapter missing')
        def check(pg):
            r=pg.evaluate('''async()=>{const M=await import('/engine/vk-motion.mjs'),P=await import('/engine/vk-music.mjs');const S=M.score({end:8,tempo:[{beat:0,bpm:120},{beat:4,bpm:60}]});const bank={notes:{60:{src:'assets/piano/60.flac',duration:4,license:'test'}}};const events=P.phrase(S,{id:'answer',beat:3,notes:[[0,60,2,.5],[2,null,1]],instrument:bank,tail:.3});let bad=false;try{P.phrase(S,{id:'bad',beat:0,notes:[[0,61,1]],instrument:bank})}catch(e){bad=true}return {events,bad}}''')
            e=r['events'];self.assertEqual(len(e),1);self.assertAlmostEqual(e[0]['start'],1.5);self.assertAlmostEqual(e[0]['duration'],1.8)
            self.assertEqual(e[0]['sound']['src'],'assets/piano/60.flac');self.assertEqual(e[0]['sound']['track'],'music');self.assertEqual(e[0]['sound']['gain'],.5);self.assertTrue(r['bad'])
        render.with_page(ROOT/'examples/fold_C',check)
