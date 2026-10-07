"""Independent local-viewer contract and HTTP authorization regression tests."""
import base64
import hashlib
import http.client
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import threading
import unittest

ROOT=Path(os.environ.get('GRAPH_SECURITY_TARGET',Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(ROOT/'scripts'))
import graph_access
import graph_engine


def fixture(profile='local-live', script='window.unitProbe=1;'):
    digest=base64.b64encode(hashlib.sha256(script.encode()).digest()).decode()
    policy=("default-src 'none'; base-uri 'none'; script-src 'sha256-"+digest+"'; script-src-attr 'none'; style-src 'unsafe-inline'; img-src data: blob:; font-src 'none'; connect-src 'self'; object-src 'none'; frame-src 'none'; worker-src 'none'; media-src 'none'; form-action 'none'")
    return ('<!doctype html><html><head><meta charset="utf-8"><meta http-equiv="Content-Security-Policy" content="'+policy+'">'
            '<meta name="local-graph-security-profile" content="'+profile+'"><meta name="local-graph-runtime-version" content="1"></head><body>'
            '<script id="local-graph-session" type="application/json">{}</script><script>'+script+'</script></body></html>')


class LiveSecurityTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.db=self.root/'graph.db';graph_engine.init_db(self.db)
        self.page=self.root/'live.html';self.page.write_text(fixture(),encoding='utf-8')
        self.servers=[]

    def tearDown(self):
        for server in self.servers:server.server_close()
        self.temp.cleanup()

    def make(self, **kwargs):
        server=graph_access.make_server(self.db,self.page,0,**kwargs)
        self.servers.append(server)
        return server

    def test_valid_live_profile(self):
        self.assertEqual(self.make().server_address[0],'127.0.0.1')

    def test_offline_not_silently_upgraded(self):
        self.page.write_text(fixture('offline'))
        with self.assertRaises(ValueError):self.make()

    def test_extended_does_not_receive_database_capability(self):
        self.page.write_text(fixture('extended'))
        with self.assertRaises(ValueError):self.make()

    def test_legacy_custom_page_refused(self):
        self.page.write_text('<html><head></head><body>custom</body></html>')
        with self.assertRaises(ValueError):self.make()

    def test_unlisted_script_refused(self):
        self.page.write_text(fixture().replace('</body>','<script>window.extra=1;</script></body>'))
        with self.assertRaises(ValueError):self.make()

    def test_remote_script_refused(self):
        self.page.write_text(fixture().replace('</body>','<script src="https://example.invalid/code.js"></script></body>'))
        with self.assertRaises(ValueError):self.make()

    def test_inline_handler_refused(self):
        self.page.write_text(fixture().replace('<body>','<body onload="window.extra=1">'))
        with self.assertRaises(ValueError):self.make()

    def test_late_policy_refused(self):
        self.page.write_text(fixture().replace('<head>','<head><script>window.early=1;</script>'))
        with self.assertRaises(ValueError):self.make()

    def test_existing_session_refused(self):
        self.page.write_text(fixture().replace('type="application/json">{}','type="application/json">{"token":"old"}'))
        with self.assertRaises(ValueError):self.make()

    def test_policy_weakening_refused(self):
        for old,new in [("connect-src 'self'","connect-src *"),("base-uri 'none'","base-uri 'self'"),("script-src-attr 'none'","script-src-attr 'unsafe-inline'")]:
            with self.subTest(old=old):
                self.page.write_text(fixture().replace(old,new))
                with self.assertRaises(ValueError):self.make()

    def test_expected_hash_mismatch_refused(self):
        with self.assertRaises(ValueError):self.make(viewer_sha256='0'*64)

    def test_expected_hash_can_pin_page(self):
        digest=hashlib.sha256(self.page.read_bytes()).hexdigest()
        self.assertEqual(self.make(viewer_sha256=digest).viewer_sha256,digest)

    def test_http_controls_and_authorized_query(self):
        before=self.db.read_bytes();page_before=self.page.read_bytes()
        server=self.make();thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        def request(method,path='/',body=None,headers=None):
            client=http.client.HTTPConnection('127.0.0.1',server.server_port,timeout=3)
            try:
                client.request(method,path,body,headers or {})
                response=client.getresponse();content=response.read()
                return response.status,dict(response.getheaders()),content
            finally:client.close()
        try:
            status,headers,body=request('GET')
            self.assertEqual(status,200)
            self.assertIn("frame-ancestors 'none'",headers['Content-Security-Policy'])
            script_policy=re.search(r'(?:^|;)\s*script-src\s+([^;]+)',headers['Content-Security-Policy']).group(1)
            self.assertNotIn('unsafe-inline',script_policy)
            self.assertEqual(headers['Referrer-Policy'],'no-referrer')
            self.assertEqual(headers['Cache-Control'],'no-store')
            self.assertNotIn('Access-Control-Allow-Origin',headers)
            slot=re.search(r'<script id="local-graph-session" type="application/json">(.*?)</script>',body.decode()).group(1)
            token=json.loads(slot)['token']
            good={'Content-Type':'application/json','X-Local-Graph-Token':token,'Origin':f'http://127.0.0.1:{server.server_port}','Sec-Fetch-Site':'same-origin'}
            status,_,result=request('POST','/api/query',json.dumps({'operation':'stats'}),good)
            self.assertEqual(status,200,result)
            self.assertEqual(json.loads(result)['status'],'pass')
            for change in [{'Host':'evil.invalid'},{'Origin':'null'},{'Origin':'https://example.invalid'},{'Sec-Fetch-Site':'cross-site'},{'X-Local-Graph-Token':'wrong'}]:
                with self.subTest(change=change):
                    status,_,result=request('POST','/api/query','{}',{**good,**change})
                    self.assertEqual(status,403)
                    self.assertNotIn(token.encode(),result)
            self.assertEqual(request('POST','/api/query','{}',{**good,'Content-Type':'text/plain'})[0],415)
            self.assertEqual(request('POST','/api/query','{}',{**good,'Transfer-Encoding':'chunked'})[0],400)
            self.assertEqual(request('OPTIONS','/api/query')[0],403)
            self.assertEqual(request('GET','/other')[0],404)
            self.assertEqual(request('GET','/',headers={'Sec-Fetch-Site':'cross-site'})[0],403)
        finally:
            server.shutdown();thread.join(timeout=5)
        self.assertEqual(self.db.read_bytes(),before)
        self.assertEqual(self.page.read_bytes(),page_before)

if __name__=='__main__':unittest.main()
