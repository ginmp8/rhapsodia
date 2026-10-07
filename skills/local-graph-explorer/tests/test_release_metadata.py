"""The package VERSION is the independent oracle for render receipts."""
import importlib.util
import json
from pathlib import Path
import re
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('release_viewer', ROOT / 'scripts/graph_explorer.py')
VIEWER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VIEWER)

class ReleaseMetadataTests(unittest.TestCase):
    def test_receipt_and_embedded_config_match_package_version(self):
        expected = (ROOT / 'VERSION').read_text(encoding='utf-8').strip()
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / 'graph.html'
            receipt = VIEWER.render(ROOT / 'examples/basic-view.json', out, ROOT / 'assets/graph-viewer.html', 'builtin', 'auto', None)
            self.assertEqual(receipt['viewer_version'], expected)
            match = re.search(r'const VIEWER_CONFIG=(\{[^\n]*\});', out.read_text(encoding='utf-8'))
            self.assertIsNotNone(match)
            self.assertEqual(json.loads(match.group(1))['viewer_version'], expected)

if __name__ == '__main__':
    unittest.main()
