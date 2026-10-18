import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
import http.server
import threading
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('comparison',ROOT/'scripts/compare_skill.py')
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)


class ComparisonTest(unittest.TestCase):
    def test_two_real_http_requests_preserve_usage_and_generated_sources(self):
        received=[]
        class Handler(http.server.BaseHTTPRequestHandler):
            def log_message(self,*args):pass
            def do_POST(self):
                payload=json.loads(self.rfile.read(int(self.headers['Content-Length'])));received.append(payload)
                data=json.dumps({'model':'fixture-id','usage':{'total_tokens':42},'choices':[{'message':{'content':json.dumps({'film_js':'VK.film({dur:6,draw(){}})'})}}]}).encode()
                self.send_response(200);self.end_headers();self.wfile.write(data)
        server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        try:
            with tempfile.TemporaryDirectory() as d:
                out=Path(d)/'probe';c.prepare(out,'fixture-id',1200)
                with patch.dict(os.environ,{'VK_MODEL_API_KEY':'unit-test-only','VK_MODEL_BASE_URL':f'http://127.0.0.1:{server.server_port}'}):c.run(out)
                self.assertEqual(len(received),2);self.assertEqual(received[0]['messages'][1],received[1]['messages'][1])
                report=json.loads((out/'manifest.json').read_text())
                self.assertEqual(report['status'],'generated_unreviewed')
                self.assertEqual(report['original']['usage']['total_tokens'],42)
                self.assertTrue((out/'upgraded/film.js').read_text().startswith('VK.film'))
        finally:server.shutdown();server.server_close();thread.join()

    def test_only_guidance_differs_and_missing_credentials_never_call_network(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'probe';c.prepare(out,'user-specified-id',1200)
            a,b=[json.loads((out/x/'request.json').read_text()) for x in ['original','upgraded']]
            self.assertEqual(a['messages'][1],b['messages'][1])
            self.assertNotEqual(a['messages'][0],b['messages'][0])
            self.assertEqual({k:v for k,v in a.items() if k!='messages'},{k:v for k,v in b.items() if k!='messages'})
            self.assertEqual(json.loads((out/'manifest.json').read_text())['status'],'prepared_not_run')
            with patch.dict(os.environ,{'VK_MODEL_API_KEY':'','DEEPSEEK_API_KEY':''}),patch.object(c.urllib.request,'urlopen') as net:
                with self.assertRaisesRegex(ValueError,'not configured'):c.run(out)
                net.assert_not_called()
            with self.assertRaisesRegex(ValueError,'not empty'):c.prepare(out,'x',1200)


if __name__=='__main__':unittest.main()
