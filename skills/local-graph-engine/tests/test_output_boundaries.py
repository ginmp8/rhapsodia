"""Output safety oracles: exports must never overwrite their own evidence."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import graph
from graph_data import propose_mapping
from graph_common import canonical

class OutputBoundaries(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.db = self.root / 'graph.db'
    def tearDown(self):
        self.temp.cleanup()
    def arguments(self, *args):
        return graph.parser().parse_args(['--db', str(self.db), *map(str, args)])
    def test_patch_cannot_overwrite_mapping(self):
        source = self.root / 'rows.json'
        source.write_text('[{"id":1}]')
        mapping = self.root / 'mapping.json'
        mapping.write_text(canonical(propose_mapping([{'id':1}], 'demo')))
        before = mapping.read_bytes()
        with self.assertRaises(ValueError):
            graph.execute(self.arguments('ingest', source, '--mapping', mapping, '--patch-output', mapping))
        self.assertEqual(before, mapping.read_bytes())
        self.assertFalse(self.db.exists())
    def test_scan_output_cannot_replace_a_scanned_source(self):
        folder = self.root / 'sources'
        folder.mkdir()
        source = folder / 'notes.md'
        source.write_text('# Evidence\nThis must not be overwritten.')
        before = source.read_bytes()
        with self.assertRaises(ValueError):
            graph.execute(self.arguments('scan', folder, '--namespace', 'demo', '--patch-output', source))
        self.assertEqual(before, source.read_bytes())
        self.assertFalse(self.db.exists())
    def test_export_cannot_overwrite_query_file(self):
        source = self.root / 'rows.json'
        source.write_text('[{"id":1}]')
        graph.execute(self.arguments('ingest', source, '--namespace', 'demo'))
        request = self.root / 'request.json'
        request.write_text('{"operation":"subgraph"}')
        before = request.read_bytes()
        with self.assertRaises(ValueError):
            graph.execute(self.arguments('export', 'json', request, '--request', request))
        self.assertEqual(before, request.read_bytes())

if __name__ == '__main__': unittest.main()
