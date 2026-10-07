"""Real Chromium checks for the finite, offline walkthrough and drag coexistence."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
ROOT=Path(os.environ.get('GRAPH_TARGET',Path(__file__).resolve().parents[1]))
spec=importlib.util.spec_from_file_location('walk_viewer',ROOT/'scripts/graph_explorer.py');V=importlib.util.module_from_spec(spec);spec.loader.exec_module(V)
DATA={'schema_version':'graph-view-v1','graph':{'label':'Walkthrough regression fixture'},'nodes':[{'id':k,'kind':'stage','label':label} for k,label in [('a','Start'),('b','Check B'),('c','Check C'),('d','Finish'),('x','Isolated')]],'edges':[{'id':i,'source':s,'target':t,'relation':'precedes','directed':True} for i,s,t in [('ab','a','b'),('ac','a','c'),('bd','b','d'),('cd','c','d')]],'metadata':{'complete_database':False,'layout_hint':'dagre'}}
@unittest.skipUnless(importlib.util.find_spec('playwright') and (os.environ.get('LOCAL_GRAPH_BROWSER') or shutil.which('chromium')), 'optional Playwright/Chromium browser tools unavailable')
class WalkthroughBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from playwright.sync_api import sync_playwright
        cls.tmp=tempfile.TemporaryDirectory();cls.folder=Path(cls.tmp.name);src=cls.folder/'view.json';src.write_text(json.dumps(DATA));out=cls.folder/'graph.html'
        V.render(src,out,ROOT/'assets/graph-viewer.html','builtin','auto',None);cls.html=out.read_text()
        cls.pw=sync_playwright().start();cls.browser=cls.pw.chromium.launch(headless=True,executable_path=os.environ.get('LOCAL_GRAPH_BROWSER') or shutil.which('chromium'),args=['--no-sandbox'])
    @classmethod
    def tearDownClass(cls):cls.browser.close();cls.pw.stop();cls.tmp.cleanup()
    def setUp(self):
        self.context=self.browser.new_context(viewport={'width':1440,'height':1000},accept_downloads=True);self.page=self.context.new_page();self.page.set_default_timeout(5000)
        self.errors=[];self.requests=[];self.page.on('pageerror',lambda e:self.errors.append(str(e)));self.page.on('request',lambda r:self.requests.append(r.url));self.page.set_content(self.html)
    def tearDown(self):
        try:self.assertEqual(self.errors,[]);self.assertEqual(self.requests,[])
        finally:self.context.close()
    def prepare(self,mode='downstream',start='a',target=''):
        self.page.select_option('#walk-mode',mode);self.page.select_option('#walk-from',start)
        if target:self.page.select_option('#walk-to',target)
        self.page.locator('#walk-prepare').click()
    def state(self):return self.page.evaluate('LocalGraphView.getWalkthrough()')
    def positions(self):return self.page.evaluate('LocalGraphView.getPositions()')
    def test_idle_and_projection_boundaries(self):
        self.assertEqual(self.state()['status'],'idle');self.assertIn('projection',self.page.locator('#walk-summary').inner_text().lower());self.assertEqual(self.page.locator('.node[data-boundary="entry"]').count(),1)
    def test_prepare_parallel_layers(self):
        self.prepare();self.assertEqual(self.state()['steps'],3);self.assertEqual(self.state()['step'],0);self.assertEqual(self.page.locator('.node[data-walk-state="current"]').count(),1)
        self.page.locator('#walk-next').click();self.assertEqual(self.page.locator('.node[data-walk-state="current"]').count(),2);self.assertIn('not runtime',self.page.locator('#walk-detail').inner_text())
    def test_previous_and_seek_preserve_geometry(self):
        before=self.positions();self.prepare();self.page.locator('#walk-next').click();self.page.locator('#walk-prev').click();self.assertEqual(self.state()['step'],0)
        self.page.locator('#walk-progress').fill('2');self.assertEqual(self.state()['step'],2);self.assertEqual(before,self.positions())
    def test_finite_playback_and_replay(self):
        self.prepare();self.page.select_option('#walk-speed','2');self.page.locator('#walk-play').click();self.page.wait_for_function("LocalGraphView.getWalkthrough().status==='ended'",timeout=5000)
        self.assertEqual(self.state()['step'],2);self.page.locator('#walk-play').click();self.assertEqual(self.state()['status'],'playing');self.page.locator('#walk-play').click();self.assertEqual(self.state()['status'],'paused')
    def test_pause_cancels_scheduled_step(self):
        self.prepare();self.page.locator('#walk-play').click();self.page.locator('#walk-play').click();step=self.state()['step'];self.page.wait_for_timeout(1150);self.assertEqual(self.state()['step'],step)
    def test_reduced_motion_manual_still_works(self):
        self.page.emulate_media(reduced_motion='reduce');self.prepare();self.assertTrue(self.page.locator('#walk-play').is_disabled());self.page.locator('#walk-next').click();self.assertEqual(self.state()['step'],1)
    def test_drag_during_play_does_not_reset_nodes(self):
        self.prepare();self.page.locator('#walk-play').click();before=self.positions();box=self.page.locator('.node[data-node="b"] rect').first.bounding_box();x,y=box['x']+box['width']/2,box['y']+box['height']/2
        self.page.mouse.move(x,y);self.page.mouse.down();self.page.mouse.move(x+40,y+25,steps=4);self.page.mouse.up();after=self.positions();self.assertNotEqual(before['b'],after['b']);self.page.wait_for_timeout(1100);self.assertEqual(self.positions()['b'],after['b'])
    def test_filter_invalidates_and_stops(self):
        self.prepare();self.page.locator('#walk-play').click();self.page.locator('#search').fill('Check B');self.page.wait_for_timeout(200);self.assertEqual(self.state()['status'],'idle');self.assertIn('changed',self.page.locator('#walk-status').inner_text().lower())
    def test_theme_retains_progress(self):
        self.prepare();self.page.locator('#walk-next').click();self.page.select_option('#theme','dark');self.assertEqual(self.state()['step'],1);self.assertEqual(self.page.locator('.node[data-walk-state="current"]').count(),2)
    def test_leaving_view_pauses(self):
        self.prepare();self.page.locator('#walk-play').click();self.page.locator('[data-view="table"]').click();self.assertEqual(self.state()['status'],'paused');self.page.locator('[data-view="graph"]').click();self.assertEqual(self.state()['status'],'paused')
    def test_path_and_upstream(self):
        self.prepare('path','a','d');self.assertEqual(self.state()['steps'],3);self.page.locator('#walk-next').click();self.assertEqual(self.page.locator('.node[data-walk-state="current"]').get_attribute('data-node'),'b')
        self.prepare('upstream','d');self.page.locator('#walk-next').click();self.assertEqual(self.page.locator('.node[data-walk-state="current"]').count(),2)
    def test_unreachable_does_not_keep_old_walkthrough(self):
        self.prepare();self.prepare('path','d','a');self.assertEqual(self.state()['status'],'idle');self.assertIn('No directed path',self.page.locator('#message').inner_text())
    def test_minimap_changes_camera_not_positions(self):
        before=self.positions();camera=self.page.evaluate('LocalGraphView.getState().viewport');self.page.locator('#walk-minimap').click(position={'x':25,'y':20});self.assertEqual(before,self.positions());self.assertNotEqual(camera,self.page.evaluate('LocalGraphView.getState().viewport'))
    def test_export_is_static_and_data_unchanged(self):
        before=self.page.evaluate('LocalGraphView.getSnapshot()');self.prepare();self.page.locator('#walk-next').click();self.assertEqual(before,self.page.evaluate('LocalGraphView.getSnapshot()'))
        self.page.select_option('#export-format','svg')
        with self.page.expect_download() as event:self.page.locator('#export-button').click()
        p=self.folder/'walk.svg';event.value.save_as(p);s=p.read_text();self.assertNotIn('data-walk-state',s);self.assertNotIn('data-journey-overlay',s);self.assertNotIn('<animate',s)
    def test_mobile_and_desktop_no_horizontal_overflow(self):
        self.prepare()
        for w,h in [(390,844),(1440,900),(1600,1000),(1920,1080)]:
            self.page.set_viewport_size({'width':w,'height':h});self.assertTrue(self.page.evaluate('document.documentElement.scrollWidth<=innerWidth'))
    def test_cycle_and_hostile_labels_are_text(self):
        data=json.loads(json.dumps(DATA));data['nodes'][1]['label']='</script><script>window.XSS=1</script>';data['edges'].append({'id':'db','source':'d','target':'b','relation':'revisits','directed':True})
        self.page.locator('#import-file').set_input_files({'name':'cycle.json','mimeType':'application/json','buffer':json.dumps(data).encode()});self.prepare();self.assertEqual(len(self.state()['cycles']),1);self.assertIsNone(self.page.evaluate('window.XSS'))
    def test_reset_clears_playback_not_graph_facts(self):
        self.prepare();self.page.locator('#walk-play').click();self.page.locator('#walk-reset').click();self.assertEqual(self.state()['status'],'idle');self.assertEqual(self.page.locator('.node').count(),5)

if __name__=='__main__':unittest.main()
