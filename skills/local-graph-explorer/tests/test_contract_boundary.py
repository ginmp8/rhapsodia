"""The published GraphView schema is the independent cross-language oracle."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('boundary_viewer',ROOT/'scripts/graph_explorer.py');viewer=importlib.util.module_from_spec(spec);spec.loader.exec_module(viewer)

def data():
    return {'schema_version':'graph-view-v1','nodes':[{'id':'a','kind':'record','label':'Alpha','properties':None,'evidence':None}],'edges':[],'graph':None,'metadata':None,'query':None,'communities':None}

class BoundaryTests(unittest.TestCase):
    def test_nullable_fields_are_valid(self):
        self.assertEqual(viewer.validate_graphview(data()),[])
    def test_node_evidence_objects_required(self):
        d=data();d['nodes'][0]['evidence']=[None]
        self.assertTrue(viewer.validate_graphview(d))
    def test_aliases_strings_required(self):
        d=data();d['nodes'][0]['aliases']=[3]
        self.assertTrue(viewer.validate_graphview(d))
    def test_root_graph_object_required(self):
        d=data();d['graph']=[]
        self.assertTrue(viewer.validate_graphview(d))
    def test_edge_evidence_objects_required(self):
        d=data();d['edges']=[{'id':'e','source':'a','target':'a','relation':'loop','evidence':[None]}]
        self.assertTrue(viewer.validate_graphview(d))

BROWSER=os.environ.get('LOCAL_GRAPH_BROWSER') or shutil.which('chromium') or shutil.which('google-chrome')
@unittest.skipUnless(importlib.util.find_spec('playwright') and BROWSER,'optional browser unavailable')
class BrowserBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from playwright.sync_api import sync_playwright
        cls.pw=sync_playwright().start();cls.browser=cls.pw.chromium.launch(headless=True,executable_path=BROWSER,args=['--no-sandbox'])
    @classmethod
    def tearDownClass(cls):cls.browser.close();cls.pw.stop()
    def render(self,d):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'v.json';p.write_text(json.dumps(d));out=Path(td)/'v.html'
            r=viewer.render(p,out,ROOT/'assets/graph-viewer.html','builtin','auto',None)
            self.assertEqual(r['status'],'pass');return out.read_text()
    def test_nullable_fields_render_in_browser(self):
        ctx=self.browser.new_context();page=ctx.new_page()
        try:
            page.set_content(self.render(data()),wait_until='networkidle')
            self.assertEqual(page.locator('.node').count(),1)
            self.assertNotIn('Could not load',page.locator('#message').inner_text())
        finally:ctx.close()
    def test_unscored_evidence_is_unknown_not_silently_hidden(self):
        d=data();d['nodes'][0]['evidence']=[{'locator':'source:1','source_uri':42}]
        ctx=self.browser.new_context();page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        try:
            page.set_content(self.render(d),wait_until='networkidle')
            self.assertEqual(page.locator('.node').count(),1)
            page.get_by_text('Source and properties',exact=True).click()
            page.locator('#source-filter').fill('42');page.wait_for_timeout(200)
            self.assertEqual(page.locator('.node').count(),1);self.assertEqual(errors,[])
        finally:ctx.close()

if __name__=='__main__':unittest.main()
