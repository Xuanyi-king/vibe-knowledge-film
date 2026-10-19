"""Source edits with unchanged END/FPS must invalidate events and bound media."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from engine import render

ROOT=Path(__file__).resolve().parents[1]

class ProvenanceTest(unittest.TestCase):
    def make(self,p,duration=.4):
        (p/'renders').mkdir();(p/'audio').mkdir()
        (p/'index.html').write_text('<canvas id="stage"></canvas><script src="/engine/vk.js"></script><script src="film.js"></script>')
        (p/'film.js').write_text("import('./score.mjs').then(({SCORE})=>{window.VK_SCORE=SCORE;VK.film({dur:.4,grain:0,draw(fr,t){fr.rect(0,0,10,10,{fill:'#abc'})}})})")
        (p/'score.mjs').write_text("import {score} from '/engine/vk-motion.mjs';export const SCORE=score({end:.4,events:[{id:'tap',start:.1,duration:.2,sound:{kind:'impact',material:'wood'}}]})")
        if duration!=.4:
            for name in ['film.js','score.mjs']:
                file=p/name;file.write_text(file.read_text().replace('.4',str(duration)))
        render.frames(p,p/'renders/raw.mp4');render.events(p)

    def cli(self,name,p):
        script=ROOT/('engine/audio.py' if name=='audio' else 'scripts/check_av.py')
        return subprocess.run([sys.executable,str(script),str(p)],capture_output=True,text=True,encoding='utf-8')

    def test_source_edits_reject_old_events_and_old_encoded_check(self):
        for filename,old,new in [('film.js',"'#abc'","'#def'"),('score.mjs','start:.1','start:.2')]:
            with self.subTest(filename=filename),tempfile.TemporaryDirectory() as d:
                p=Path(d);self.make(p)
                good=self.cli('audio',p);self.assertEqual(good.returncode,0,good.stderr)
                self.assertEqual(self.cli('check',p).returncode,0)
                final=(p/'renders/final.mp4').read_bytes();wav=(p/'audio/score.wav').read_bytes()
                path=p/filename;path.write_text(path.read_text().replace(old,new))
                failed=self.cli('audio',p)
                self.assertNotEqual(failed.returncode,0,'edited source still accepted stale events')
                self.assertIn('stale',failed.stderr)
                self.assertEqual((p/'renders/final.mp4').read_bytes(),final)
                self.assertEqual((p/'audio/score.wav').read_bytes(),wav)
                failed=self.cli('check',p)
                self.assertNotEqual(failed.returncode,0,'encoding check accepted stale events')

    def test_reexported_events_cannot_bind_old_raw_or_tampered_payload(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);self.make(p)
            (p/'score.mjs').write_text((p/'score.mjs').read_text().replace('start:.1','start:.2'))
            render.events(p)
            failed=self.cli('audio',p)
            self.assertNotEqual(failed.returncode,0,'new events accepted old raw from another input version')
            self.assertIn('raw',failed.stderr)
            render.frames(p,p/'renders/raw.mp4')
            good=self.cli('audio',p);self.assertEqual(good.returncode,0,good.stderr)
            spec=json.loads((p/'audio/events.json').read_text());spec['score']['events'][0]['start']=.1
            (p/'audio/events.json').write_text(json.dumps(spec))
            failed=self.cli('audio',p)
            self.assertNotEqual(failed.returncode,0,'edited export accepted without re-exporting from source')

    def test_export_input_race_keeps_previous_event_file(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);self.make(p);before=(p/'audio/events.json').read_bytes()
            original=render.with_page
            def edited(proj,callback):
                (p/'film.js').write_text((p/'film.js').read_text()+'\n// edited during initialization')
                return original(proj,callback)
            with patch.object(render,'with_page',side_effect=edited),self.assertRaisesRegex(RuntimeError,'changed during export'):
                render.events(p)
            self.assertEqual((p/'audio/events.json').read_bytes(),before)

    def test_modified_reference_or_final_cannot_pass_encoding_check(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);self.make(p)
            good=self.cli('audio',p);self.assertEqual(good.returncode,0,good.stderr)
            wav=p/'audio/score.wav';original=wav.read_bytes();wav.write_bytes(original[:-2]+b'xx')
            bad=self.cli('check',p);self.assertEqual(bad.returncode,1)
            self.assertIn('reference',bad.stdout)
            self.assertTrue(json.loads((p/'audio/sync.json').read_text())['failed'])
            wav.write_bytes(original)
            final=p/'renders/final.mp4';final.write_bytes(final.read_bytes()+b'tampered')
            bad=self.cli('check',p);self.assertEqual(bad.returncode,1)
            self.assertIn('final',bad.stdout)

    def test_unversioned_events_require_reexport(self):
        from engine import provenance
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'film.js').write_text('// legacy')
            with self.assertRaisesRegex(RuntimeError,'unversioned.*events.json'):
                provenance.validate_events(p,{'end':1,'fps':30,'events':[]})

    def test_noninteger_frame_end_is_supported_by_serial_pipeline(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);self.make(p,.41)
            good=self.cli('audio',p)
            self.assertEqual(good.returncode,0,good.stderr)

    def test_decoder_failure_invalidates_previous_green_report(self):
        import runpy
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);self.make(p)
            self.assertEqual(self.cli('audio',p).returncode,0)
            self.assertEqual(self.cli('check',p).returncode,0)
            real_run=subprocess.run
            def broken(cmd,**kwargs):
                if 'f64le' in cmd:cmd=[sys.executable,'-c','import sys;sys.exit(7)']
                return real_run(cmd,**kwargs)
            with patch.object(subprocess,'run',side_effect=broken),patch.object(sys,'argv',['check_av.py',str(p)]):
                try:runpy.run_path(str(ROOT/'scripts/check_av.py'),run_name='__main__')
                except (SystemExit,subprocess.CalledProcessError):pass
            self.assertTrue(json.loads((p/'audio/sync.json').read_text())['failed'])

    def test_input_edit_during_encoding_check_cannot_publish_green(self):
        from scripts import check_av
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);self.make(p)
            self.assertEqual(self.cli('audio',p).returncode,0)
            decode=check_av.decode
            def editing_decode(path):
                (p/'film.js').write_text((p/'film.js').read_text()+'\n// input changed during decoding')
                return decode(path)
            with patch.object(check_av,'decode',side_effect=editing_decode):
                with self.assertRaisesRegex(RuntimeError,'changed during export'):
                    check_av.check(p,p/'renders/final.mp4')
            self.assertTrue(json.loads((p/'audio/sync.json').read_text())['failed'])
