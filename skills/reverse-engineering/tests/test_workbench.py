import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'scripts'))
from workbench import analyze
from test_semantic_decoders import cli_pe_fixture, wasm_fixture
from test_web_and_dex import android_fixture

class PipelineTests(unittest.TestCase):
    def test_mixed_archive_independently_analyzed(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);zpath=root/'mixed.zip'
            with zipfile.ZipFile(zpath,'w',compression=zipfile.ZIP_STORED) as z:
                z.writestr('app.dll',cli_pe_fixture())
                z.writestr('app.wasm',wasm_fixture())
                z.writestr('classes.dex',android_fixture())
                z.writestr('src/module.ts','import { x } from "./other"; app.get("/health",handler);')
                z.writestr('capture.har',json.dumps({'log':{'entries':[{'request':{'method':'GET','url':'https://site.invalid/items/123456'},'response':{'status':200}}]}}))
                z.writestr('app.js.map',json.dumps({'version':3,'sources':['app.ts'],'names':[],'mappings':'AAAA'}))
            result=analyze(zpath)
            self.assertTrue(result['complete'],result['errors'])
            self.assertEqual(result['analyzed'],6)
            self.assertEqual(result['formats']['dotnet-cli'],1)
            self.assertEqual(result['formats']['wasm'],1)
            self.assertEqual(result['formats']['dex'],1)
            self.assertEqual(result['formats']['javascript'],1)
            self.assertEqual(result['formats']['har'],1)
            self.assertEqual(result['formats']['source-map'],1)
            self.assertFalse((root/'classes.dex').exists(),'no extraction should occur')
    def test_missing_byte_budget_declared_partial(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'files';path.mkdir()
            (path/'a.wasm').write_bytes(wasm_fixture())
            (path/'b.wasm').write_bytes(wasm_fixture())
            out=analyze(path,max_items=1)
            self.assertFalse(out['complete'])
            self.assertEqual(out['analyzed'],1)
            self.assertTrue(out['skipped'])
    def test_corrupt_target_does_not_fabricate_success(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'broken.dex';p.write_bytes(b'dex\n035\0' + b'0'*8)
            out=analyze(p)
            self.assertFalse(out['complete'])
            self.assertTrue(out['errors'])
            self.assertEqual(out['analyzed'],0)
    def test_zip_expansion_limit_is_not_full_success(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'bomb.zip'
            with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED) as z:
                z.writestr('inflate.ts','// hello'+('A'*45000))
            result=analyze(path)
            self.assertFalse(result['complete'])
            self.assertTrue(any('expansion' in x['reason'] for x in result['skipped']))
    def test_unrecognized_single_file_not_success(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'file.opaque';path.write_bytes(b'some data')
            result=analyze(path)
            self.assertFalse(result['complete'])
            self.assertEqual(result['analyzed'],0)
    def test_bad_source_map_does_not_raise(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'broken.map';path.write_text('null')
            result=analyze(path)
            self.assertFalse(result['complete'])
            self.assertEqual(len(result['errors']),1)
    def test_fat_macho_router(self):
        from workbench import route
        self.assertEqual(route('fat.bin',b'\xca\xfe\xba\xbe\x00\x00\x00\x02'),'mach-o-fat')
        self.assertEqual(route('java.class',b'\xca\xfe\xba\xbe\x00\x00\x00\x3d'),'jvm')
    def test_no_supported_file_mark_as_unknown(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'mystery.bin';p.write_bytes(b'not a format')
            out=analyze(p)
            self.assertEqual(out['analyzed'],0)
            self.assertEqual(out['matched_candidates'],0)

if __name__=='__main__': unittest.main()
