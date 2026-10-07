"""Security acceptance: independent requirements frozen before implementation."""
import base64
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import tempfile
import unittest

ROOT = Path(os.environ.get('GRAPH_SECURITY_TARGET', Path(__file__).resolve().parents[1]))
SPEC = importlib.util.spec_from_file_location('security_explorer', ROOT/'scripts/graph_explorer.py')
VIEWER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VIEWER)

class ExplorerSecurityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.output = self.root/'graph.html'
        self.source = ROOT/'examples/basic-view.json'
        self.template = ROOT/'assets/graph-viewer.html'
        self.bundle = self.root/'extra.js'
        self.bundle.write_text('window.G6={Graph:function(){}};', encoding='utf-8')
        self.digest = hashlib.sha256(self.bundle.read_bytes()).hexdigest()

    def tearDown(self):
        self.temp.cleanup()

    def render(self, **kwargs):
        return VIEWER.render(self.source, self.output, self.template, 'auto', 'auto', kwargs.pop('g6_js', None), **kwargs)

    def test_default_has_restrictive_csp_and_hashes(self):
        result = self.render()
        page = self.output.read_text(encoding='utf-8')
        policy = re.search(r'<meta http-equiv="Content-Security-Policy" content="([^"]+)"', page).group(1)
        self.assertIn("connect-src 'none'", policy)
        self.assertIn("base-uri 'none'", policy)
        self.assertIn("form-action 'none'", policy)
        scripts = re.findall(r'<script>([\s\S]*?)</script>', page)
        self.assertGreaterEqual(len(scripts), 4)
        for script in scripts:
            expected = base64.b64encode(hashlib.sha256(script.encode()).digest()).decode()
            self.assertIn("'sha256-"+expected+"'", policy)
        script_policy = re.search(r'(?:^|;)\s*script-src\s+([^;]+)', policy).group(1)
        self.assertNotIn('unsafe-inline', script_policy)
        self.assertNotIn('unsafe-eval', script_policy)
        self.assertTrue(result['offline'])
        self.assertEqual(result['security_profile'], 'offline')
        self.assertEqual(result['network_policy'], 'none')

    def test_extension_rejected_by_default_preserving_output(self):
        self.output.write_bytes(b'last-good')
        with self.assertRaises(ValueError):
            self.render(g6_js=self.bundle)
        self.assertEqual(self.output.read_bytes(), b'last-good')

    def test_template_rejected_by_default(self):
        self.template = self.root/'custom.html'
        self.template.write_text((ROOT/'assets/graph-viewer.html').read_text(), encoding='utf-8')
        with self.assertRaises(ValueError):
            self.render()
        self.assertFalse(self.output.exists())

    def test_extended_requires_hash(self):
        with self.assertRaises(ValueError):
            self.render(g6_js=self.bundle, security_profile='extended')
        self.assertFalse(self.output.exists())

    def test_wrong_hash_fails_without_write(self):
        with self.assertRaises(ValueError):
            self.render(g6_js=self.bundle, security_profile='extended', g6_sha256='0'*64)
        self.assertFalse(self.output.exists())

    def test_extended_is_honest_about_custom_code(self):
        result = self.render(g6_js=self.bundle, security_profile='extended', g6_sha256=self.digest)
        self.assertFalse(result['offline'])
        self.assertIsNone(result['network_required'])
        self.assertEqual(result['network_policy'], 'unverified')
        self.assertEqual(result['extensions'][0]['sha256'], self.digest)
        self.assertFalse(result['live_enabled'])

    def test_custom_template_requires_its_own_hash(self):
        self.template = self.root/'custom.html'
        self.template.write_text((ROOT/'assets/graph-viewer.html').read_text()+'<!-- custom -->', encoding='utf-8')
        with self.assertRaises(ValueError):
            self.render(security_profile='extended')
        digest = hashlib.sha256(self.template.read_bytes()).hexdigest()
        result = self.render(security_profile='extended', template_sha256=digest)
        self.assertFalse(result['offline'])
        self.assertEqual(result['extensions'][0]['sha256'], digest)

    def test_local_live_profile_separate_from_offline(self):
        result = self.render(security_profile='local-live')
        page = self.output.read_text()
        self.assertFalse(result['offline'])
        self.assertTrue(result['live_enabled'])
        self.assertIn("connect-src 'self'", page)
        self.assertIn('id="local-graph-session" type="application/json">{}</script>', page)
        self.assertIn('name="local-graph-security-profile" content="local-live"', page)

    def test_live_rejects_extensions(self):
        with self.assertRaises(ValueError):
            self.render(security_profile='local-live', g6_js=self.bundle, g6_sha256=self.digest)

    def test_unknown_profile_fails_closed(self):
        with self.assertRaises(ValueError):
            self.render(security_profile='unrestricted')

    def test_html_parser_escaped_input(self):
        data = json.loads(self.source.read_text())
        data['nodes'][0]['label'] = '<!--<script></script><script>window.BAD=1</script>'
        self.source = self.root/'data.json'
        self.source.write_text(json.dumps(data), encoding='utf-8')
        self.render()
        page = self.output.read_text()
        self.assertNotIn('<!--<script>', page)
        self.assertIn('\\u003c!--', page)

    def test_receipt_determinism(self):
        first = self.render()
        second = self.render()
        self.assertEqual(first, second)

if __name__ == '__main__':
    unittest.main()
