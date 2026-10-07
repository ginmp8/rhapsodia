"""Optional real-browser tests. No network required; HTML is loaded inline.

Set LOCAL_GRAPH_BROWSER to a Chromium executable, or install Playwright's browser
separately. These tests report skipped, never passed, when capability is absent.
"""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('browser_viewer',ROOT/'scripts/graph_explorer.py');viewer=importlib.util.module_from_spec(spec);spec.loader.exec_module(viewer)
HAS_BROWSER=bool(importlib.util.find_spec('playwright'))
BROWSER=os.environ.get('LOCAL_GRAPH_BROWSER') or shutil.which('chromium') or shutil.which('google-chrome')

@unittest.skipUnless(HAS_BROWSER and BROWSER,'optional Playwright/Chromium unavailable')
class BrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from playwright.sync_api import sync_playwright
        cls.temp=tempfile.TemporaryDirectory();cls.root=Path(cls.temp.name)
        viewer.render(ROOT/'examples/fieldwork-view.json',cls.root/'graph.html',ROOT/'assets/graph-viewer.html','builtin','auto',None)
        cls.html=(cls.root/'graph.html').read_text();cls.playwright=sync_playwright().start()
        cls.browser=cls.playwright.chromium.launch(headless=True,executable_path=BROWSER,args=['--no-sandbox'])
    @classmethod
    def tearDownClass(cls):cls.browser.close();cls.playwright.stop();cls.temp.cleanup()
    def setUp(self):
        self.context=self.browser.new_context(viewport={'width':1440,'height':1000},accept_downloads=True)
        self.page=self.context.new_page();self.errors=[];self.requests=[]
        self.page.on('pageerror',lambda e:self.errors.append(str(e)));self.page.on('request',lambda r:self.requests.append(r.url))
        self.page.set_content(self.html,wait_until='networkidle')
    def tearDown(self):
        self.assertEqual(self.errors,[]);self.assertEqual(self.requests,[]);self.context.close()
    def test_offline_actual_render(self):
        self.assertEqual(self.page.locator('.node').count(),19);self.assertIn('24 / 24',self.page.locator('#counts').inner_text())
    def test_search_filter(self):
        self.page.locator('#search').fill('Water');self.page.wait_for_function("document.querySelectorAll('.node').length===3")
        self.assertIn('3 / 19',self.page.locator('#counts').inner_text())
    def test_select_and_evidence(self):
        self.page.locator('.node[data-node="project:river"]').click();self.assertIn('River water study',self.page.locator('#inspector').inner_text());self.assertIn('example://fieldwork/synthetic',self.page.locator('#inspector').inner_text())
    def test_path_and_focus(self):
        self.page.select_option('#path-from','person:ana');self.page.select_option('#path-to','document:report');self.page.locator('#path-button').click();self.assertIn('Directed shortest path: 4',self.page.locator('#message').inner_text())
        self.page.locator('#focus-button').click();self.assertLess(self.page.locator('.node').count(),19)
    def test_table(self):
        self.page.locator('[data-view="table"]').click();self.assertEqual(self.page.locator('#table-content tbody tr').count(),19);self.page.locator('#table-content button').first.click();self.assertNotIn('Select an entity',self.page.locator('#inspector-content').inner_text())
    def test_timeline_and_matrix(self):
        self.page.locator('[data-view="timeline"]').click();self.assertEqual(self.page.locator('.timeline-item').count(),10)
        self.page.locator('[data-view="matrix"]').click();self.assertEqual(self.page.locator('.matrix-table tr').count(),20)
    def test_numeric_summary(self):
        self.page.locator('[data-view="summary"]').click();self.page.select_option('#numeric-property','budget');self.assertIn('74,000',self.page.locator('#summary-content').inner_text())
    def test_state_roundtrip(self):
        self.page.select_option('#layout','grid');state=self.page.evaluate('LocalGraphView.getState()');positions=self.page.evaluate('LocalGraphView.getPositions()');self.page.select_option('#layout','circular');self.page.evaluate('(s)=>LocalGraphView.restoreState(s)',state)
        self.assertEqual(self.page.evaluate('LocalGraphView.getPositions()'),positions)
    def test_keyboard_and_reduced_motion(self):
        node=self.page.locator('.node').first;node.focus();node.press('Enter');self.assertNotIn('Select an entity',self.page.locator('#inspector-content').inner_text());self.page.emulate_media(reduced_motion='reduce');self.assertTrue(self.page.evaluate("matchMedia('(prefers-reduced-motion: reduce)').matches"))
    def test_mobile_no_document_overflow(self):
        self.page.set_viewport_size({'width':390,'height':844});self.page.wait_for_timeout(50);self.assertTrue(self.page.evaluate('document.documentElement.scrollWidth<=innerWidth'))
    def test_export_download(self):
        with self.page.expect_download() as event:self.page.locator('#export-button').click()
        event.value.save_as(self.root/'view.json');data=json.loads((self.root/'view.json').read_text());self.assertEqual(len(data['nodes']),19);self.assertFalse(data['metadata']['complete_database'])
    def test_deterministic_positions(self):
        a=self.page.evaluate('LocalGraphView.getPositions()');self.page.locator('#reset-button').click();self.assertEqual(a,self.page.evaluate('LocalGraphView.getPositions()'))
    def test_hostile_label_is_text(self):
        data=json.loads((ROOT/'examples/fieldwork-view.json').read_text());data['nodes'][0]['label']='</script><script>window.XSS=1</script>'
        self.page.locator('#import-file').set_input_files({'name':'hostile.json','mimeType':'application/json','buffer':json.dumps(data).encode()});self.page.wait_for_function("document.getElementById('message').textContent.includes('Local GraphView loaded')")
        self.assertIsNone(self.page.evaluate('window.XSS'));self.assertEqual(self.page.locator('.node').count(),19)

if __name__=='__main__':unittest.main()
