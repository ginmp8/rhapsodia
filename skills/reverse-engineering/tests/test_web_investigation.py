"""Bounded integration tests for optional browser investigation without network."""
import hashlib
import shutil
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'scripts'))
from behavior_lab import DataError
from web_investigator import checked_actions, inspect_browser, checked_fixture, browser_capabilities, safe_route
from web_audit import audit, read_pointer
from source_marker_scan import scan
from correlate_web_evidence import correlate, route_matches
from evidence_ir import ingest


class CoreTest(unittest.TestCase):
    def test_actions_fail_closed_and_path_validation(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'actions.json'
            for actions in ([{'type':'eval','code':'alert(1)'}],
                            [{'type':'goto','path':'//evil.invalid/'}],
                            [{'type':'goto','path':'/../secret.html'}],
                            [{'type':'scroll','selector':'body','pixels':999999}],
                            [{'type':'fill','selector':'#x'}]):
                p.write_text(json.dumps(actions))
                with self.assertRaises(DataError): checked_actions(p)
    def test_approval_required_before_browser_launch(self):
        with self.assertRaisesRegex(DataError,'authorization'):
            inspect_browser(mode='capture',origin='http://localhost:8080',actions=[])
        with self.assertRaisesRegex(DataError,'mutations-approved'):
            inspect_browser(mode='capture',origin='http://localhost:8080',
                            actions=[{'type':'click','selector':'button'}],authorized=True)
        with self.assertRaisesRegex(DataError,'nonlocal origin'):
            inspect_browser(mode='explore',origin='https://example.org',authorized=True)
    def test_fixture_traversal_and_symlink_prevention(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'index.html').write_text('<h1>ok</h1>')
            self.assertIn('ok',checked_fixture(root,'/index.html'))
            for v in ('/../outside.html','//bad','/a?secret=x'):
                with self.assertRaises(DataError):safe_route(v)
            (root/'link.html').symlink_to(root/'index.html')
            with self.assertRaisesRegex(DataError,'symlink'):
                checked_fixture(root,'/link.html')
    def test_finite_audit_pass_fail_unknown_and_type(self):
        trace={'mode':'web-investigation','schema_version':'1.0',
               'evidence_type':'trusted-offline-html-fixture','steps':[{'dom':{'horizontal_overflow':False}}]}
        pol=lambda op,exp,path='/steps/0/dom/horizontal_overflow':{
            'schema_version':'1.0','rules':[{'id':'r','path':path,'op':op,'expected':exp}]}
        self.assertEqual(audit(trace,pol('eq',False))['result'],'passed')
        self.assertEqual(audit(trace,pol('eq',True))['result'],'failed')
        self.assertEqual(audit(trace,pol('eq',True,'/missing'))['result'],'incomplete')
        self.assertEqual(audit(trace,pol('eq',0))['result'],'failed')
        with self.assertRaises(DataError):audit(trace,{'schema_version':'1.0','rules':[]})
        self.assertEqual(read_pointer({'a/b':['ok']},'/a~1b/0'),('ok',True))
    def test_openapi_route_correlation_never_claims_backend_execution(self):
        trace={'mode':'web-investigation','events':[
            {'kind':'request','method':'GET','path':'/orders/123','observed':True},
            {'kind':'request','method':'GET','path':'/secrets','observed':False}]}
        ops={'operations':[{'method':'GET','path':'/orders/{id}'},{'method':'POST','path':'/orders'}]}
        out=correlate(trace,ops)
        self.assertEqual(len(out['matches']),1)
        self.assertEqual(out['matches'][0]['level'],'inferred')
        self.assertEqual(len(out['unmatched_requests']),0)
        self.assertFalse(route_matches('/orders/1/private','/orders/{id}'))
    def test_scanner_redacted(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'file.py').write_text('key=\"AKIA7B9C8D1E2F3G4H5J\"\n')
            out=scan(root)
            self.assertEqual(len(out['findings']),1)
            self.assertEqual(out['findings'][0]['marker'],'[REDACTED]')
            self.assertNotIn('AKIA',json.dumps(out))
            self.assertFalse(out['truncated'])
    def test_fixture_graph_keeps_static_versus_fixture_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'trace.json'
            p.write_text(json.dumps({'mode':'web-investigation','evidence_type':'trusted-offline-html-fixture',
                                     'steps':[{'type':'click','index':0,'dom':{'text_sha256':'f'*64}}],
                                     'events':[]}))
            graph=ingest([p])['reports'][0]
            self.assertTrue(any(n['kind']=='dom-snapshot' and n['evidence_level']=='fixture_observed' for n in graph['nodes']))
            self.assertFalse(any(n['kind']=='browser-request' for n in graph['nodes']))


@unittest.skipUnless(browser_capabilities()['python_playwright'] and bool(browser_capabilities()['browser_candidates']),
                     'Playwright + Chromium are optional, not an implicit host contract')
class BrowserTest(unittest.TestCase):
    def test_synthetic_ui_actions_and_observed_dom(self):
        fixture=ROOT/'examples'/'web-fixture'
        actions=json.loads((ROOT/'examples'/'web-actions.json').read_text())
        out=inspect_browser(mode='capture',origin='http://localhost:8080',fixture_root=fixture,
                            actions=actions,authorized=True,mutations_approved=True,
                            browser_executable=Path(shutil.which(browser_capabilities()['browser_candidates'][0])))
        self.assertEqual(len(out['steps']),len(actions))
        self.assertEqual(out['steps'][3]['selected_text_sha256'],hashlib.sha256(b'Saved').hexdigest())
        self.assertEqual(out['steps'][6]['selected_text_sha256'],hashlib.sha256(b'Dropped').hexdigest())
        self.assertFalse(out['network_evidence'])
        self.assertEqual(out['events'],[])
        self.assertEqual(out['counters']['page_errors'],0)
    def test_explore_only_approved_html_links(self):
        result=inspect_browser(mode='explore',origin='http://localhost:8080',
                               fixture_root=ROOT/'examples'/'web-fixture',authorized=True,max_pages=2,
                               browser_executable=Path(shutil.which(browser_capabilities()['browser_candidates'][0])))
        self.assertEqual([a['path'] for a in result['pages']],['/index.html','/next.html'])
        self.assertTrue(result['links'])

if __name__=='__main__':unittest.main()
