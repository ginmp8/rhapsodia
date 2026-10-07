"""Pointer-driven node positioning, separate from graph facts and canvas pan.

Uses an independent tiny multigraph, real browser input and world/screen geometry.
Optional browser dependencies are test-only; none are required by the viewer.
LOCAL_GRAPH_TEST_ROOT may point at an immutable baseline for paired evaluation.
"""
import copy
import importlib.util
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
if importlib.util.find_spec('playwright'):
    from playwright.sync_api import expect

ROOT = Path(os.environ.get('LOCAL_GRAPH_TEST_ROOT', Path(__file__).resolve().parents[1]))
SPEC = importlib.util.spec_from_file_location('drag_viewer', ROOT / 'scripts/graph_explorer.py')
VIEWER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VIEWER)
BROWSER = os.environ.get('LOCAL_GRAPH_BROWSER') or shutil.which('chromium') or shutil.which('google-chrome')
DATA = {
    'schema_version': 'graph-view-v1',
    'nodes': [
        {'id': 'a', 'kind': 'person', 'label': 'Alpha'},
        {'id': 'b', 'kind': 'project', 'label': 'Beta'},
        {'id': 'c', 'kind': 'place', 'label': 'Gamma'},
        {'id': 'd', 'kind': 'place', 'label': 'Delta'},
    ],
    'edges': [
        {'id': 'ab1', 'source': 'a', 'target': 'b', 'relation': 'owns', 'directed': True},
        {'id': 'ab2', 'source': 'a', 'target': 'b', 'relation': 'reviews', 'directed': True},
        {'id': 'aloop', 'source': 'a', 'target': 'a', 'relation': 'checks', 'directed': True},
        {'id': 'cd', 'source': 'c', 'target': 'd', 'relation': 'links', 'directed': False},
    ],
    'metadata': {'layout_hint': 'grid', 'complete_database': False},
}

@unittest.skipUnless(BROWSER and importlib.util.find_spec('playwright'), 'Playwright/Chromium not available')
class NodeDragTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from playwright.sync_api import sync_playwright
        cls.tmp = tempfile.TemporaryDirectory()
        cls.folder = Path(cls.tmp.name)
        src = cls.folder / 'data.json'
        src.write_text(json.dumps(DATA), encoding='utf-8')
        out = cls.folder / 'graph.html'
        VIEWER.render(src, out, ROOT / 'assets/graph-viewer.html', 'builtin', 'auto', None)
        cls.html = out.read_text(encoding='utf-8')
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch(headless=True, executable_path=BROWSER, args=['--no-sandbox'])

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()
        cls.tmp.cleanup()

    def setUp(self):
        self.context = self.browser.new_context(viewport={'width': 1440, 'height': 1000}, has_touch=True, accept_downloads=True)
        self.page = self.context.new_page()
        self.errors, self.requests = [], []
        self.page.on('pageerror', lambda e: self.errors.append(str(e)))
        self.page.on('request', lambda r: self.requests.append(r.url))
        self.page.set_content(self.html, wait_until='networkidle')

    def tearDown(self):
        try:
            self.assertEqual(self.errors, [])
            self.assertEqual(self.requests, [])
        finally:
            self.context.close()

    def state(self):
        return self.page.evaluate('LocalGraphView.getState()')

    def positions(self):
        return self.page.evaluate('LocalGraphView.getPositions()')

    def node(self, node_id='a'):
        return self.page.locator('.node[data-node="' + node_id + '"]')

    def center(self, node_id='a'):
        box = self.node(node_id).locator('rect').first.bounding_box()
        self.assertIsNotNone(box)
        return box['x'] + box['width'] / 2, box['y'] + box['height'] / 2

    def drag_node(self, dx=65, dy=43, node_id='a', release=True):
        x, y = self.center(node_id)
        self.page.mouse.move(x, y)
        self.page.mouse.down()
        self.page.mouse.move(x + dx, y + dy, steps=6)
        if release:
            self.page.mouse.up()

    def test_mouse_drag_moves_only_target_and_keeps_viewport(self):
        before, camera = self.positions(), self.state()['viewport']
        self.drag_node()
        after = self.positions()
        self.assertNotEqual(after['a'], before['a'], 'dragging a node must move it')
        self.assertAlmostEqual(after['a']['x'] - before['a']['x'], 65 / camera['k'], delta=.03)
        self.assertAlmostEqual(after['a']['y'] - before['a']['y'], 43 / camera['k'], delta=.03)
        for key in ('b', 'c', 'd'):
            self.assertEqual(after[key], before[key])
        self.assertEqual(self.state()['viewport'], camera)
        self.assertIsNone(self.state()['selected'], 'a drag must not turn into an accidental click')

    def test_edges_parallel_and_self_loop_follow_during_drag(self):
        selector = '#graph-world > path:not(.edge-hit)'
        old = self.page.locator(selector).evaluate_all('(es)=>es.map(e=>e.getAttribute("d"))')
        self.drag_node(release=False)
        new = self.page.locator(selector).evaluate_all('(es)=>es.map(e=>e.getAttribute("d"))')
        hits = self.page.locator('.edge-hit').evaluate_all('(es)=>es.map(e=>e.getAttribute("d"))')
        self.page.mouse.up()
        for i in (0, 1, 2):
            self.assertNotEqual(old[i], new[i])
        self.assertNotEqual(new[0], new[1], 'parallel edges must remain separate')
        self.assertEqual(old[3], new[3], 'unrelated edge must not change')
        self.assertEqual(new, hits)

    def test_drag_respects_zoom_pan_and_css_scaling(self):
        state = self.state()
        state['viewport'] = {'x': 160, 'y': 140, 'k': .65}
        self.page.evaluate('(s)=>LocalGraphView.restoreState(s)', state)
        self.page.locator('#graph-svg').evaluate('(e)=>{e.style.transform="scale(.8)";e.style.transformOrigin="0 0";}')
        before = self.positions()['a']
        self.drag_node(dx=60, dy=40)
        after = self.positions()['a']
        self.assertAlmostEqual(after['x'] - before['x'], 60 / (.65 * .8), delta=.03)
        self.assertAlmostEqual(after['y'] - before['y'], 40 / (.65 * .8), delta=.03)

    def test_click_and_small_jitter_select_without_moving(self):
        before = self.positions()
        self.drag_node(dx=1, dy=1)
        self.assertEqual(self.positions(), before)
        self.assertEqual(self.state()['selected'], 'a')
        self.node('b').click()
        self.assertEqual(self.state()['selected'], 'b')

    def test_background_pan_does_not_move_nodes(self):
        before, camera = self.positions(), self.state()['viewport']
        box = self.page.locator('#graph-svg').bounding_box()
        x, y = box['x'] + 30, box['y'] + 100
        self.page.mouse.move(x, y)
        self.page.mouse.down()
        self.page.mouse.move(x + 40, y + 25, steps=4)
        self.page.mouse.up()
        self.assertEqual(self.positions(), before)
        after = self.state()['viewport']
        self.assertAlmostEqual(after['x'] - camera['x'], 40)
        self.assertAlmostEqual(after['y'] - camera['y'], 25)
        self.assertEqual(after['k'], camera['k'])

    def test_positions_survive_selection_theme_filter_and_other_views(self):
        self.drag_node()
        manual = self.positions()['a']
        self.node('b').click()
        self.page.select_option('#theme', 'dark')
        for view in ('table', 'timeline', 'matrix', 'summary', 'graph'):
            self.page.locator('[data-view="' + view + '"]').click()
        self.assertEqual(self.positions()['a'], manual)
        self.page.locator('#search').fill('Beta')
        expect(self.page.locator('.node')).to_have_count(1)
        self.page.locator('#search').fill('')
        expect(self.page.locator('.node')).to_have_count(4)
        self.assertEqual(self.positions()['a'], manual)

    def test_state_download_restore_and_reset(self):
        automatic = self.positions()
        self.drag_node()
        manual = self.positions()['a']
        self.page.select_option('#export-format', 'state')
        with self.page.expect_download() as event:
            self.page.locator('#export-button').click()
        target = self.folder / 'drag-state.json'
        event.value.save_as(target)
        state = json.loads(target.read_text(encoding='utf-8'))
        self.assertEqual(state.get('node_positions'), {'a': manual})
        self.page.locator('#reset-button').click()
        self.assertEqual(self.positions(), automatic)
        self.page.locator('#state-file').set_input_files(target)
        expect(self.page.locator('#message')).to_contain_text('View state restored')
        self.assertEqual(self.positions()['a'], manual)

    def test_legacy_state_without_coordinates_still_loads(self):
        legacy = self.state()
        legacy.pop('node_positions', None)
        before = self.positions()
        self.drag_node()
        self.page.evaluate('(s)=>LocalGraphView.restoreState(s)', legacy)
        self.assertEqual(self.positions(), before)

    def test_invalid_coordinates_are_rejected_without_partial_state_changes(self):
        state, positions = self.state(), self.positions()
        for bad in (None, [], {'missing': {'x': 3, 'y': 2}}, {'a': {'x': '3', 'y': 2}}, {'a': {'x': 1e12, 'y': 2}}, {'a': {'x': 2}}):
            with self.subTest(bad=bad):
                s = copy.deepcopy(state)
                s['search'] = 'Beta'
                s['node_positions'] = bad
                result = self.page.evaluate('(s)=>{try{LocalGraphView.restoreState(s);return "accepted";}catch(e){return e.message;}}', s)
                self.assertNotEqual(result, 'accepted')
                self.assertEqual(self.state(), state)
                self.assertEqual(self.positions(), positions)

    def test_layout_change_clears_manual_coordinates(self):
        self.page.select_option('#layout', 'circular')
        automatic = self.positions()
        self.drag_node(dx=-55, dy=35)
        self.assertNotEqual(self.positions(), automatic)
        self.page.select_option('#layout', 'grid')
        self.page.select_option('#layout', 'circular')
        self.assertEqual(self.positions(), automatic)
        self.assertEqual(self.state().get('node_positions'), {})

    def test_keyboard_nudges_keep_focus_and_update_geometry(self):
        self.node().focus()
        old = self.positions()['a']
        self.node().press('ArrowRight')
        self.node().press('Shift+ArrowDown')
        new = self.positions()['a']
        self.assertEqual(new['x'], old['x'] + 10)
        self.assertEqual(new['y'], old['y'] + 50)
        self.assertEqual(self.page.evaluate('document.activeElement.dataset.node'), 'a')
        self.node().press('Enter')
        self.assertEqual(self.state()['selected'], 'a')

    def test_cancel_restores_node_and_releases_gesture(self):
        original = self.positions()
        self.drag_node(release=False)
        self.assertNotEqual(self.positions(), original)
        self.page.keyboard.press('Escape')
        self.page.mouse.up()
        self.assertEqual(self.positions(), original)
        self.assertEqual(self.state().get('node_positions'), {})
        self.drag_node(dx=55, dy=35)
        self.assertNotEqual(self.positions(), original)

    def test_right_button_does_not_drag(self):
        old, state = self.positions(), self.state()['viewport']
        x, y = self.center()
        self.page.mouse.move(x, y)
        self.page.mouse.down(button='right')
        self.page.mouse.move(x + 50, y + 20, steps=3)
        self.page.mouse.up(button='right')
        self.assertEqual(self.positions(), old)
        self.assertEqual(self.state()['viewport'], state)

    def test_pointer_capture_keeps_drag_outside_canvas(self):
        old = self.positions()['a']
        x, y = self.center()
        camera = self.state()['viewport']
        box = self.page.locator('#graph-svg').bounding_box()
        finish_x, finish_y = box['x'] - 35, y + 25
        self.page.mouse.move(x, y)
        self.page.mouse.down()
        self.page.mouse.move(finish_x, finish_y, steps=6)
        self.page.mouse.up()
        new = self.positions()['a']
        self.assertAlmostEqual(new['x'] - old['x'], (finish_x - x) / camera['k'], delta=.03)
        self.assertAlmostEqual(new['y'] - old['y'], 25 / camera['k'], delta=.03)
        self.assertEqual(self.state()['viewport'], camera)

    def test_emulated_touch_moves_node(self):
        client = self.context.new_cdp_session(self.page)
        before, camera = self.positions()['a'], self.state()['viewport']
        x, y = self.center()
        def touch(kind, px=0, py=0):
            client.send('Input.dispatchTouchEvent', {'type': kind, 'touchPoints': [] if kind == 'touchEnd' else [{'x': px, 'y': py, 'id': 1}]})
        touch('touchStart', x, y)
        touch('touchMove', x + 25, y + 20)
        touch('touchMove', x + 55, y + 35)
        touch('touchEnd')
        after = self.positions()['a']
        self.assertAlmostEqual(after['x'] - before['x'], 55 / camera['k'], delta=.2)
        self.assertAlmostEqual(after['y'] - before['y'], 35 / camera['k'], delta=.2)
        self.assertEqual(self.state()['viewport'], camera)
        client.detach()

    def test_data_export_contains_no_presentation_coordinates(self):
        before = self.page.evaluate('LocalGraphView.getSnapshot()')
        self.drag_node()
        after = self.page.evaluate('LocalGraphView.getSnapshot()')
        self.assertEqual(after['nodes'], before['nodes'])
        self.assertEqual(after['edges'], before['edges'])
        self.assertNotIn('node_positions', after)
        self.assertIn('a', self.state().get('node_positions', {}))

    def test_svg_export_keeps_moved_position(self):
        self.drag_node()
        manual = self.positions()['a']
        self.page.select_option('#export-format', 'svg')
        with self.page.expect_download() as event:
            self.page.locator('#export-button').click()
        target = self.folder / 'drag-graph.svg'
        event.value.save_as(target)
        from xml.etree import ElementTree as ET
        root = ET.parse(target).getroot()
        group = next(e for e in root.iter() if e.attrib.get('data-node') == 'a')
        self.assertEqual(group.attrib['transform'], f'translate({manual["x"]},{manual["y"]})')

if __name__ == '__main__':
    unittest.main()
