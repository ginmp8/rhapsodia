"""Host-independent format, offline and output-integrity regression checks."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('viewer',ROOT/'scripts/graph_explorer.py');viewer=importlib.util.module_from_spec(spec);spec.loader.exec_module(viewer)

class ExtendedExplorerTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.data=json.loads((ROOT/'examples/fieldwork-view.json').read_text());self.source=self.root/'source.json';self.save()
    def tearDown(self):self.temp.cleanup()
    def save(self):self.source.write_text(json.dumps(self.data),encoding='utf-8')
    def render(self,output=None,backend='auto'):
        return viewer.render(self.source,output or self.root/'out.html',ROOT/'assets/graph-viewer.html',backend,'auto',None)
    def test_offline_default(self):
        r=self.render();html=(self.root/'out.html').read_text();self.assertTrue(r['offline']);self.assertEqual(r['effective_backend'],'builtin-svg');self.assertNotIn('<script src=',html);self.assertNotIn('fonts.googleapis',html)
    def test_output_alias_does_not_change_source(self):
        before=self.source.read_bytes()
        with self.assertRaises(ValueError):self.render(self.source)
        self.assertEqual(before,self.source.read_bytes())
    def test_symlink_output_refused(self):
        link=self.root/'link.html';link.symlink_to(self.source)
        with self.assertRaises(ValueError):self.render(link)
    def test_nonfinite_rejected(self):
        self.data['nodes'][0]['properties']['value']=float('nan');self.save()
        with self.assertRaises(ValueError):self.render()
    def test_duplicate_json_key_rejected(self):
        self.source.write_text('{"schema_version":"graph-view-v1","schema_version":"other"}')
        with self.assertRaises(ValueError):self.render()
    def test_tokens_in_source_not_interpreted(self):
        self.data['nodes'][0]['label']='__VIEWER_CONFIG__ __VIEWER_SCRIPT__ __G6_SCRIPT__';self.save();self.render();out=(self.root/'out.html').read_text();self.assertIn('"label":"__VIEWER_CONFIG__ __VIEWER_SCRIPT__ __G6_SCRIPT__"',out)
    def test_g6_explicit_requires_local_file(self):
        with self.assertRaises(ValueError):self.render(backend='g6')
    def test_five_data_views(self):
        self.render();html=(self.root/'out.html').read_text()
        for v in ['graph','table','timeline','matrix','summary']:self.assertIn('id="'+v+'-view"',html)
    def test_fixed_assets_are_reproducible(self):
        a=self.render(self.root/'a.html');b=self.render(self.root/'b.html');self.assertEqual(a['sha256'],b['sha256'])
    def test_bounded_view_validation(self):
        bad={'schema_version':'graph-view-v1','nodes':[{}]*10001,'edges':[]};self.assertIn('bounded projection',' '.join(viewer.validate_graphview(bad)))

if __name__=='__main__':unittest.main()
