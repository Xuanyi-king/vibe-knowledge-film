import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
from engine import render as r

class RenderTests(unittest.TestCase):
    def test_determinism_failure_is_an_error(self):
        class Page:
            def evaluate(self, code): return 1
        counter = iter(range(100))
        with patch.object(r, 'with_page', side_effect=lambda p, fn: fn(Page())), patch.object(r, 'shot', side_effect=lambda p,t: str(next(counter)).encode()):
            with self.assertRaisesRegex(RuntimeError, 'determin'):
                r.det(Path('.'), n=3)

    def test_invalid_clip_rejected_before_encoder(self):
        class Page:
            def evaluate(self, code): return 2 if code == 'END' else 30
        with patch.object(r, 'with_page', side_effect=lambda p,fn: fn(Page())), patch.object(r.subprocess, 'Popen') as popen, patch.object(r, 'shot', return_value=b'frame'):
            for a,b in [(-1,1),(1,1),(2,3),(1,float('nan'))]:
                with self.subTest(a=a,b=b), self.assertRaises(ValueError): r.frames(Path('.'), Path('bad.mp4'),a,b)
            popen.assert_not_called()

    def test_encoder_failure_preserves_existing_output(self):
        # A real child process accepts stdin then fails: exercises wait/cleanup, not a mocked exit.
        import subprocess, sys
        real_popen = subprocess.Popen
        class Page:
            def evaluate(self, code): return 1
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'raw.mp4'; out.write_bytes(b'previous good film')
            def failed_encoder(*args, **kw):
                return real_popen([sys.executable,'-c','import sys; sys.stdin.buffer.read(); sys.exit(7)'],**kw)
            with patch.object(r,'with_page',side_effect=lambda p,fn:fn(Page())), patch.object(r,'shot',return_value=b'frame'), patch.object(r.subprocess,'Popen',side_effect=failed_encoder):
                with self.assertRaises((RuntimeError, subprocess.CalledProcessError)): r.frames(Path(d),out)
            self.assertEqual(out.read_bytes(),b'previous good film')
            self.assertEqual(list(Path(d).iterdir()),[out])

class ServerPathsTest(unittest.TestCase):
    def test_url_encoded_asset_names_work(self):
        import urllib.error, urllib.parse, urllib.request
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);name='图像 space.txt';(p/name).write_bytes(b'local asset')
            srv,url=r.serve(p)
            try:
                try:
                    with urllib.request.urlopen(url+urllib.parse.quote(name)) as response:data=response.read()
                except urllib.error.HTTPError as exc:data=f'HTTP {exc.code}'.encode()
                self.assertEqual(data,b'local asset')
            finally:srv.shutdown();srv.server_close()

    def test_encoded_parent_path_cannot_escape_project(self):
        import urllib.error, urllib.request
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'project';p.mkdir();(p.parent/'outside.txt').write_bytes(b'private fixture')
            srv,url=r.serve(p)
            try:
                with self.assertRaises(urllib.error.HTTPError):urllib.request.urlopen(url+'%2e%2e/outside.txt')
            finally:srv.shutdown();srv.server_close()

class ParallelTests(unittest.TestCase):
    def test_failed_worker_does_not_skip_waiting_for_other_workers(self):
        from unittest.mock import MagicMock
        first, second = MagicMock(), MagicMock()
        first.wait.return_value=1; second.wait.return_value=0
        first.poll.return_value=1; second.poll.return_value=0
        with tempfile.TemporaryDirectory() as d:
            p=Path(d); (p/'renders').mkdir()
            with patch.object(r,'with_page',return_value=(1,30)), patch.object(r.subprocess,'Popen',side_effect=[first,second]):
                with self.assertRaises((SystemExit, RuntimeError)): r.frames_parallel(p,p/'renders/raw.mp4',2)
            first.wait.assert_called_once(); second.wait.assert_called_once()
            self.assertEqual(list((p/'renders').iterdir()),[])

class BrowserTests(unittest.TestCase):
    def test_capture_timeout_reports_last_successful_seek_state_without_retry(self):
        # Inject only the expensive compositor timeout. Real page, seek, fonts,
        # project server and diagnostics must run, with no second JS probe.
        from playwright.sync_api import Page, TimeoutError as CaptureTimeout
        def check(pg):
            with patch.object(Page,'screenshot',side_effect=CaptureTimeout('injected compositor stall')) as capture, patch.object(pg,'evaluate',wraps=pg.evaluate) as evaluate:
                with self.assertRaisesRegex(RuntimeError,'frame capture timeout') as error:
                    r.shot(pg,.125)
                message=str(error.exception)
                for text in ['0.125','browser','fonts','loaded','canvas','ready','request_failures','capture-1']:
                    self.assertIn(text,message)
                capture.assert_called_once()
                self.assertEqual(evaluate.call_count,1,'a stalled renderer must not receive another diagnostic JS call')
        self.page("VK.film({dur:1,grain:0,meta:{title:'capture-1'},draw(fr,t){fr.rect(t*10,40,80,80,{fill:'#abc'})}})",check)

    def test_real_failed_request_is_retained_for_render_diagnostics(self):
        def check(pg):
            pg.route('**/diagnostic-font.woff2',lambda route:route.abort('failed'))
            pg.evaluate("fetch('diagnostic-font.woff2').catch(()=>null)")
            failures=getattr(pg,'_vk_request_failures',[])
            self.assertTrue(any('diagnostic-font.woff2' in x for x in failures),failures)
        self.page('VK.film({dur:.1,draw(){}})',check)

    def test_resume_rejects_inputs_in_generated_directories(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'review').mkdir();(p/'renders').mkdir()
            (p/'review/labels.md').write_text('input')
            (p/'film.js').write_text("fetch('review/labels.md').then(r=>r.text()).then(()=>VK.film({dur:.1,draw(){}}))")
            (p/'index.html').write_text('<canvas id="stage"></canvas><script src="/engine/vk.js"></script><script src="film.js"></script>')
            with self.assertRaisesRegex(ValueError,'generated folders'):
                r.frames_resume(p,p/'renders/raw.mp4')

    def page(self, code, callback):
        from playwright.sync_api import BrowserType
        original=BrowserType.launch
        def launch(browser,*a,**kw):
            if os.environ.get('VK_BROWSER'):
                kw.pop('channel',None); kw['executable_path']=os.environ['VK_BROWSER']
            return original(browser,*a,**kw)
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            (p/'film.js').write_text(code,encoding='utf8')
            (p/'index.html').write_text('<canvas id="stage"></canvas><script src="/engine/vk.js"></script><script src="film.js"></script>')
            with patch.object(BrowserType,'launch',launch): return r.with_page(p,callback)

    def test_event_draw_errors_are_not_swallowed(self):
        self.page("VK.film({dur:.2,grain:0,draw(fr,t){if(t>.1)throw Error('broken shot');fr.sfx(0,'tick');}})",
                  lambda pg: self.assertRaisesRegex(Exception,'broken shot',pg.evaluate,'events()'))

    def test_event_scan_includes_end_without_exceeding_duration(self):
        def check(pg):
            ev=pg.evaluate('events()')
            self.assertEqual(ev[-1][0],.05)
            self.assertTrue(all(0 <= e[0] <= .05 for e in ev))
        self.page("VK.film({dur:.05,draw(fr,t){if(t>.05)throw Error('outside film interval');fr.sfx(t,'tick');}})",check)

    def test_startup_script_error_reports_cause_without_ready(self):
        from playwright.sync_api import Page
        original = Page.wait_for_function
        def bounded(page, expression, **kwargs):
            kwargs['timeout'] = 2000
            return original(page, expression, **kwargs)
        with patch.object(Page, 'wait_for_function', bounded):
            with self.assertRaisesRegex(Exception, 'startup broken'):
                self.page("throw Error('startup broken')", lambda pg: None)

    def test_startup_network_error_names_failed_local_asset(self):
        from playwright.sync_api import Page
        original=Page.goto
        def routed(pg,*args,**kw):
            pg.route('**/startup-font.woff2',lambda route:route.abort('connectionrefused'))
            return original(pg,*args,**kw)
        with patch.object(Page,'goto',routed):
            with self.assertRaisesRegex(RuntimeError,'failed assets:.*startup-font.woff2'):
                self.page("new FontFace('Broken','url(startup-font.woff2)').load().catch(e=>window.READY_ERROR=String(e));",lambda pg:None)

    def test_events_preserve_seek_pixels_and_repeatability(self):
        def check(pg):
            before=r.shot(pg,.04)
            a=pg.evaluate('events()'); b=pg.evaluate('events()')
            self.assertEqual(a,b); self.assertEqual(len(a),1)
            self.assertEqual(before,r.shot(pg,.04))
        self.page("VK.film({dur:.2,grain:0,draw(fr,t){fr.rect(t*100,0,50,50,{fill:'#abc'});fr.sfx(.1,'tick');}})",check)

if __name__=='__main__': unittest.main()

class ModuleMimeTest(unittest.TestCase):
    def test_javascript_mime_is_explicit_even_when_os_mapping_is_plain_text(self):
        import mimetypes,urllib.request
        mimetypes.init()
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'film.mjs').write_text('export const x=1;');(p/'film.js').write_text('window.x=1;')
            with patch.dict(mimetypes.types_map,{'.mjs':'text/plain','.js':'text/plain'}):
                srv,url=r.serve(p)
                try:
                    for name in ['film.mjs','film.js','engine/vk-motion.mjs']:
                        with urllib.request.urlopen(url+name) as response:
                            self.assertIn(response.headers.get_content_type(),['text/javascript','application/javascript'],name)
                finally:srv.shutdown();srv.server_close()
