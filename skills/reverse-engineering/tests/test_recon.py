"""Offline functional and adversarial tests for bounded static inspection."""
import contextlib
import io
import json
import os
from pathlib import Path
import struct
import sys
import tarfile
import tempfile
import unittest
import warnings
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import recon


class ReconTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'sample'
        self.source.mkdir()
        self.limits = recon.Limits()

    def write(self, name, content):
        path = self.source / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content.encode() if isinstance(content, str) else content)
        return path

    def zip(self, name, content):
        path = self.root / 'sample.zip'
        with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as archive:
            for key, value in content.items():
                archive.writestr(key, value)
        return path

    def read_inventory(self, path=None, limits=None):
        with recon.Reader(path or self.source, limits or self.limits) as reader:
            return recon.inventory(reader)

    def test_source_inventory_and_digest(self):
        p = self.write('src/main.ts', 'import x from "./util";')
        inv = self.read_inventory()
        self.assertTrue(inv['complete'])
        self.assertEqual(inv['file_count'], 1)
        self.assertEqual(inv['files'][0]['kind'], 'text-by-name')
        self.assertEqual(len(inv['files'][0]['sha256']), 64)
        self.assertEqual(inv['files'][0]['size'], p.stat().st_size)

    def test_zip_reads_members_without_extracting(self):
        target = self.zip('z', {'pkg/a.ts': 'const x = 1;', 'pkg/b.txt': 'readme'})
        inv = self.read_inventory(target)
        self.assertTrue(inv['complete'])
        self.assertEqual({f['path'] for f in inv['files']}, {'pkg/a.ts', 'pkg/b.txt'})
        self.assertFalse((self.root / 'pkg').exists())

    def test_archive_profile_apk_and_nuget(self):
        target = self.zip('apk', {'AndroidManifest.xml': 'manifest', 'classes.dex': b'dex\n035\0'})
        self.assertEqual(self.read_inventory(target)['package_kind'], 'android-apk')
        target2 = self.root / 'nuspec.zip'
        with zipfile.ZipFile(target2, 'w') as z:
            z.writestr('tool.nuspec', '<package/>')
        self.assertEqual(self.read_inventory(target2)['package_kind'], 'nuget-package')

    def test_zip_rejects_path_traversal(self):
        target = self.zip('escape', {'../untrusted.sh': 'echo unsafe'})
        with self.assertRaisesRegex(recon.IntakeError, 'unsafe archive path'):
            with recon.Reader(target, self.limits):
                pass

    def test_zip_rejects_absolute_drive_and_backslash(self):
        for key in ('/abs/a', 'C:/a', 'folder\\a', './../a'):
            with self.subTest(key=key):
                self.assertRaises(recon.IntakeError, recon.safe_archive_name, key)

    def test_zip_rejects_duplicate_names(self):
        target = self.root / 'duplicate.zip'
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', UserWarning)
            with zipfile.ZipFile(target, 'w') as z:
                z.writestr('same.txt', 'a')
                z.writestr('same.txt', 'b')
        with self.assertRaisesRegex(recon.IntakeError, 'duplicate'):
            with recon.Reader(target, self.limits):
                pass

    def test_zip_skips_symlink_and_marks_partial(self):
        target = self.root / 'links.zip'
        info = zipfile.ZipInfo('alias')
        info.create_system = 3
        info.external_attr = (0o120777 << 16)
        with zipfile.ZipFile(target, 'w') as z:
            z.writestr(info, 'private/file')
        inv = self.read_inventory(target)
        self.assertFalse(inv['complete'])
        self.assertEqual(inv['files'][0]['reason'], 'symlink-not-read')

    def test_zip_ratio_bomb_skipped(self):
        target = self.zip('ratio', {'incompressible-looking.txt': 'A' * 20000})
        inv = self.read_inventory(target)
        self.assertFalse(inv['complete'])
        self.assertEqual(inv['files'][0]['reason'], 'suspicious-compression-ratio')

    def test_tar_dot_prefix(self):
        target = self.root / 'sample.tar.gz'
        with tarfile.open(target, 'w:gz') as tar:
            payload = b'hello'
            info = tarfile.TarInfo('./pkg/data.txt')
            info.size = len(payload)
            tar.addfile(info, io.BytesIO(payload))
        inv = self.read_inventory(target)
        self.assertTrue(inv['complete'])
        self.assertEqual(inv['files'][0]['path'], 'pkg/data.txt')

    def test_tar_hardlink_is_not_followed(self):
        target = self.root / 'hardlinks.tar'
        with tarfile.open(target, 'w') as tar:
            info = tarfile.TarInfo('hard')
            info.type = tarfile.LNKTYPE
            info.linkname = '/private'
            tar.addfile(info)
        inv = self.read_inventory(target)
        self.assertFalse(inv['complete'])
        self.assertEqual(inv['files'][0]['reason'], 'non-regular-entry-not-read')

    def test_directory_symlink_skipped(self):
        self.write('good.txt', 'good')
        (self.source / 'link.txt').symlink_to('/etc/hosts')
        inv = self.read_inventory()
        self.assertEqual(inv['file_count'], 1)
        self.assertFalse(inv['complete'])
        self.assertTrue(any('non-regular' in s for s in inv['notes']))

    def test_default_skips_node_modules(self):
        self.write('node_modules/foo/index.js', 'module.exports=1')
        self.write('src/index.js', 'a=1')
        with recon.Reader(self.source, self.limits) as r:
            inv = recon.inventory(r)
        self.assertFalse(inv['complete'])
        self.assertEqual(inv['file_count'], 1)
        with recon.Reader(self.source, self.limits, include_dependencies=True) as r:
            full = recon.inventory(r)
        self.assertTrue(full['complete'])
        self.assertEqual(full['file_count'], 2)

    def test_over_budget_is_unknown_not_clean(self):
        self.write('a.txt', 'abcd')
        self.write('b.txt', 'abcd')
        inv = self.read_inventory(limits=recon.Limits(max_item_bytes=4, max_total_bytes=5))
        self.assertFalse(inv['complete'])
        self.assertEqual(sum(e['status'] == 'ok' for e in inv['files']), 1)
        self.assertEqual(sum(e['status'] == 'skipped' for e in inv['files']), 1)

    def test_file_count_limit_reports_truncation(self):
        self.write('a.txt', 'a')
        self.write('b.txt', 'b')
        inv = self.read_inventory(limits=recon.Limits(max_files=1))
        self.assertFalse(inv['complete'])
        self.assertEqual(inv['file_count'], 1)

    def test_fingerprint_real_headers(self):
        test_data = {b'\x7fELF' + b'\x00'*100: 'elf', b'\x00asm\x01\x00\x00\x00': 'wasm',
                     b'SQLite format 3\0' + b'0'*50: 'sqlite', b'%PDF-1.7': 'pdf',
                     b'\x89PNG\r\n\x1a\n'+b'0'*10: 'png', b'\xca\xfe\xba\xbe\x00\x00\x00\x3d': 'java-class-candidate', b'\xca\xfe\xba\xbe': 'java-class-or-mach-o-fat'}
        for data, kind in test_data.items():
            with self.subTest(kind=kind):
                self.assertEqual(recon.detect_format(data, 'blob.bin'), kind)

    def test_managed_pe_marker_not_filename_only(self):
        payload = bytearray(600)
        payload[0:2] = b'MZ'
        struct.pack_into('<I', payload, 0x3C, 128)
        payload[128:132] = b'PE\x00\x00'
        struct.pack_into('<H', payload, 148, 240)
        struct.pack_into('<H', payload, 152, 0x10B)
        struct.pack_into('<II', payload, 152 + 96 + 14 * 8, 0x2100, 0x48)
        self.assertEqual(recon.detect_format(bytes(payload), 'sample.dll'), 'managed-pe')
        payload[152 + 96 + 14 * 8:152 + 96 + 14 * 8 + 8] = b'\x00' * 8
        self.assertEqual(recon.detect_format(bytes(payload), 'sample.dll'), 'pe-or-dos')
        self.assertNotEqual(recon.detect_format(b'not executable', 'sample.dll'), 'managed-pe')

    def test_search_line_anchor_and_secret_redaction(self):
        self.write('config.py', 'api_key = "someReallySecretValue"\nfeature = 1\n')
        with recon.Reader(self.source, self.limits) as r:
            result = recon.search(r, 'API_KEY', self.limits, case_sensitive=False)
        self.assertTrue(result['complete'])
        self.assertEqual(result['matches'][0]['line'], 1)
        self.assertNotIn('someReallySecretValue', result['matches'][0]['snippet'])
        self.assertEqual(len(result['matches'][0]['artifact_sha256']), 64)

    def test_search_limit_and_text_cap_are_partial(self):
        self.write('doc.md', 'needle\nneedle\nneedle\n')
        with recon.Reader(self.source, self.limits) as r:
            result = recon.search(r, 'needle', recon.Limits(max_matches=2), case_sensitive=False)
        self.assertFalse(result['complete'])
        self.assertEqual(len(result['matches']), 2)
        with recon.Reader(self.source, self.limits) as r:
            result = recon.search(r, 'needle', recon.Limits(max_text_bytes=4), case_sensitive=False)
        self.assertFalse(result['complete'])
        self.assertTrue(result['truncated_text_files'])

    def test_large_minified_line_does_not_claim_graph_coverage(self):
        self.write('main.js', ' ' * (recon.MAX_LEXICAL_LINE + 1) + 'import "./other";')
        self.write('other.js', 'const x=1;')
        with recon.Reader(self.source, self.limits) as r:
            result = recon.graph(r, self.limits)
        self.assertFalse(result['complete'])
        self.assertIn('main.js', result['truncated_sources'])
        self.assertEqual(result['edge_count'], 0)

    def test_js_graph_exact_and_heuristic_resolution(self):
        self.write('src/main.ts', 'import util from "./util";\nconst req = require("./worker.js");\nimport x from "external-pkg";')
        self.write('src/util.ts', 'export const util=1')
        self.write('src/worker.ts', 'export const worker=1')
        with recon.Reader(self.source, self.limits) as r:
            result = recon.graph(r, self.limits)
        self.assertTrue(result['complete'])
        self.assertEqual(result['edge_count'], 2)
        self.assertEqual(result['unresolved_count'], 1)
        self.assertTrue(any(e['target'] == 'src/worker.ts' and e['resolution'] == 'heuristic' for e in result['edges']))

    def test_csharp_project_reference_and_python_relative(self):
        self.write('app/App.csproj', '<ProjectReference Include="..\\Lib\\Lib.csproj" />')
        self.write('Lib/Lib.csproj', '<Project></Project>')
        self.write('py/mod.py', 'from .utils import helper\n')
        self.write('py/utils.py', 'def helper(): pass')
        with recon.Reader(self.source, self.limits) as r:
            result = recon.graph(r, self.limits)
        self.assertEqual(result['edge_count'], 2)
        self.assertTrue(any(e['kind'] == 'project-reference' for e in result['edges']))

    def test_symbol_candidates_csharp_js_python_go_rust(self):
        self.write('a/Widget.cs', 'public sealed class Widget {}\npublic async Task<int> LoadAsync() => 1;')
        self.write('a/mod.ts', 'export const createServer = (\nexport interface ServerOptions {}')
        self.write('py/functions.py', 'async def do_work(): pass')
        self.write('go/service.go', 'func (s *Service) Run() {}')
        self.write('rs/lib.rs', 'pub fn process(arg: u32) {}')
        with recon.Reader(self.source, self.limits) as r:
            result = recon.symbols(r, self.limits, None, 100)
        self.assertTrue(result['complete'])
        names = {item['name'] for item in result['symbols']}
        self.assertTrue({'Widget', 'LoadAsync', 'createServer', 'ServerOptions', 'do_work', 'Run', 'process'} <= names)
        self.assertTrue(all(item['candidate'] for item in result['symbols']))
        with recon.Reader(self.source, self.limits) as r:
            filtered = recon.symbols(r, self.limits, 'createServer', 100)
        self.assertEqual([item['name'] for item in filtered['symbols']], ['createServer'])

    def test_symbol_limit_is_partial(self):
        self.write('many.py', '\n'.join(f'def f{i}(): pass' for i in range(5)))
        with recon.Reader(self.source, self.limits) as r:
            result = recon.symbols(r, self.limits, None, 2)
        self.assertFalse(result['complete'])
        self.assertEqual(result['symbol_count'], 2)

    def test_graph_focus_ambiguous_rejected(self):
        self.write('a/index.ts', 'export const x=1')
        self.write('b/index.ts', 'export const x=1')
        with recon.Reader(self.source, self.limits) as r:
            with self.assertRaisesRegex(recon.IntakeError, 'focus must resolve uniquely'):
                recon.graph(r, self.limits, focus='index.ts')

    def test_graph_focus_unique(self):
        self.write('src/main.ts', 'import x from "./b"')
        self.write('src/b.ts', 'const a=1')
        with recon.Reader(self.source, self.limits) as r:
            result = recon.graph(r, self.limits, focus='src/main.ts', depth=1)
        self.assertEqual(result['node_count'], 2)
        self.assertEqual(result['edge_count'], 1)

    def test_diff_normalizes_version_root(self):
        a = self.root / 'old.zip'
        b = self.root / 'new.zip'
        with zipfile.ZipFile(a, 'w') as z:
            z.writestr('oldroot/a.txt', 'old')
            z.writestr('oldroot/keep.txt', 'same')
        with zipfile.ZipFile(b, 'w') as z:
            z.writestr('newroot/a.txt', 'new')
            z.writestr('newroot/keep.txt', 'same')
            z.writestr('newroot/add.txt', 'added')
        result = recon.diff_targets(a, b, self.limits, 1, False)
        self.assertTrue(result['complete'])
        self.assertEqual(result['modified'], ['a.txt'])
        self.assertEqual(result['added'], ['add.txt'])
        self.assertEqual(result['unchanged_count'], 1)

    def test_diff_partial_does_not_claim_equality(self):
        a, b = self.root / 'a', self.root / 'b'
        a.mkdir(); b.mkdir()
        (a / 'x.txt').write_text('1234567')
        (b / 'x.txt').write_text('1234567')
        result = recon.diff_targets(a, b, recon.Limits(max_item_bytes=3), 0, False)
        self.assertFalse(result['complete'])
        self.assertEqual(result['unknown'], ['x.txt'])

    def test_binary_strings_find_offsets_and_cap(self):
        p = self.root / 'blob.bin'
        p.write_bytes(b'hello_one\x00password=TOPSECRET42\x00' + b'xabcd\x00' * 100)
        with recon.Reader(p, self.limits) as r:
            result = recon.binary_strings(r, self.limits, 5, 2)
        self.assertFalse(result['complete'])
        self.assertEqual(result['strings'][0]['offset'], 0)
        self.assertEqual(len(result['strings']), 2)
        self.assertNotIn('TOPSECRET42', json.dumps(result['strings']))

    def test_no_target_execution(self):
        attack = self.root / 'executed.txt'
        self.write('do_not_run.py', f'open({str(attack)!r}, "w").write("bad")')
        with recon.Reader(self.source, self.limits) as r:
            recon.inventory(r)
        self.assertFalse(attack.exists())

    def test_emit_creates_new_file_never_overwrites(self):
        p = self.root / 'result.json'
        recon.emit({'a': 1}, str(p), [self.source])
        with self.assertRaises(FileExistsError):
            recon.emit({'a': 2}, str(p), [self.source])
        self.assertEqual(json.loads(p.read_text()), {'a': 1})

    def test_emit_refuses_write_in_analyzed_directory(self):
        p = self.source / 'result.json'
        with self.assertRaisesRegex(recon.IntakeError, 'inside analyzed directory'):
            recon.emit({'a': 1}, str(p), [self.source])
        self.assertFalse(p.exists())

    def test_malformed_literal_rejected(self):
        self.write('x.md', 'some text')
        with recon.Reader(self.source, self.limits) as r:
            with self.assertRaises(recon.IntakeError):
                recon.search(r, 'a\nb', self.limits, case_sensitive=True)


if __name__ == '__main__':
    unittest.main()
