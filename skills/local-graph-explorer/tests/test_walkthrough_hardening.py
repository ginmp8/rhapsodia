"""Additional acceptance from observed mobile overlap and stale-timer risks.
Oracles: non-overlapping DOM bounds, original edge direction, user gesture ownership.
"""
import test_walkthrough_browser as base
import unittest

@unittest.skipIf(getattr(base.WalkthroughBrowserTests, '__unittest_skip__', False), 'optional Playwright/Chromium browser tools unavailable')
class WalkthroughHardeningTests(unittest.TestCase):
    setUpClass = classmethod(base.WalkthroughBrowserTests.setUpClass.__func__)
    tearDownClass = classmethod(base.WalkthroughBrowserTests.tearDownClass.__func__)
    setUp = base.WalkthroughBrowserTests.setUp
    tearDown = base.WalkthroughBrowserTests.tearDown
    prepare = base.WalkthroughBrowserTests.prepare
    state = base.WalkthroughBrowserTests.state
    positions = base.WalkthroughBrowserTests.positions
    def test_mobile_sections_do_not_overlap(self):
        self.prepare(); self.page.set_viewport_size({'width':390,'height':844})
        self.page.wait_for_timeout(150)
        a=self.page.locator('#graph-help').bounding_box();b=self.page.locator('.filters').bounding_box()
        self.assertGreaterEqual(b['y']+1,a['y']+a['height'])
    def test_arriving_edges_keep_original_labels_and_direction(self):
        self.prepare('upstream','d');self.page.locator('#walk-next').click()
        self.assertIn('Check B',self.page.locator('#walk-detail').inner_text())
        self.assertIn('precedes',self.page.locator('#walk-detail').inner_text())
        self.assertIn('Finish',self.page.locator('#walk-detail').inner_text())
    def test_manual_zoom_releases_follow_without_stopping_play(self):
        self.prepare();self.page.locator('#walk-follow').check();self.page.locator('#walk-play').click()
        self.page.locator('#zoom-in').click();self.assertFalse(self.page.locator('#walk-follow').is_checked());self.assertEqual(self.state()['status'],'playing')
    def test_window_blur_stops_timer(self):
        self.prepare();self.page.locator('#walk-play').click();self.page.evaluate("window.dispatchEvent(new Event('blur'))")
        s=self.state();self.page.wait_for_timeout(1100);self.assertEqual(self.state()['step'],s['step']);self.assertEqual(self.state()['status'],'paused')
    def test_view_state_restore_stops_walkthrough(self):
        state=self.page.evaluate('LocalGraphView.getState()');self.prepare();self.page.locator('#walk-play').click()
        self.page.evaluate('s=>LocalGraphView.restoreState(s)',state);self.assertEqual(self.state()['status'],'idle')

if __name__=='__main__':unittest.main()
