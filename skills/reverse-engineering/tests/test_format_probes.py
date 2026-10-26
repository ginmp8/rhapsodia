import json
from pathlib import Path
import sqlite3
import struct
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import format_probes as fp


class FormatTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)

    def test_wasm_metadata_and_exports(self):
        data=b'\x00asm\x01\x00\x00\x00' + b'\x07\x08\x01\x04main\x00\x00'
        parsed=fp.scan_wasm(data)
        self.assertEqual(parsed['version'],1)
        self.assertEqual(parsed['exports'][0]['name'],'main')

    def test_wasm_truncation_rejected(self):
        self.assertRaises(fp.ProbeError,fp.scan_wasm,b'\x00asm\x01\x00\x00\x00\x07\x99')

    def test_linux_elf_header(self):
        exe=Path('/bin/ls').resolve()
        if not exe.exists() or exe.read_bytes()[:4]!=b'\x7fELF':
            self.skipTest('no ELF executable on this host')
        probe=fp.inspect(exe,32*1048576)
        self.assertEqual(probe['details']['format'],'elf')
        self.assertTrue(probe['complete_read'])

    def test_sqlite_read_only_schema(self):
        db=self.root/'db.sqlite'
        with sqlite3.connect(db) as con:
            con.execute('CREATE TABLE demo(id INTEGER PRIMARY KEY, name TEXT)')
            con.execute("INSERT INTO demo(name) VALUES ('private')")
        result=fp.inspect(db,1048576)
        self.assertEqual(result['details']['format'],'sqlite')
        self.assertTrue(any(o['name']=='demo' for o in result['details']['schema_objects']))
        self.assertNotIn('private',json.dumps(result))

    def test_har_omits_secret_query(self):
        har={'log':{'entries':[{'request':{'method':'GET','url':'https://api.example.test/customer/123456?token=private'},
                                'response':{'status':201,'content':{'mimeType':'application/json'}}}]}}
        data=json.dumps(har).encode()
        out=fp.scan_har(data)
        self.assertEqual(out['requests'][0]['route'],'/customer/{id}')
        self.assertNotIn('token',json.dumps(out))
        self.assertEqual(out['requests'][0]['status'],201)

    def test_firmware_signature_is_candidate_only(self):
        result=fp.scan_firmware(b'xx' + b'\x1f\x8b\x08' + b'xxxx')
        self.assertEqual(result['candidate_regions'][0]['offset'],2)
        self.assertIn('candidates',result['coverage'])

    def test_byte_budget_reports_partial(self):
        f=self.root/'big.bin'
        f.write_bytes(b'G'* (2*1024*1024))
        probe=fp.inspect(f,1024*1024)
        self.assertFalse(probe['complete_read'])
        self.assertIsNone(probe['input']['sha256'])

    def test_no_symlink_open(self):
        f=self.root/'good.bin';f.write_bytes(b'sample')
        link=self.root/'link.bin';link.symlink_to(f)
        self.assertRaises(fp.ProbeError, fp.inspect,link,1024*1024)

if __name__=='__main__':
    unittest.main()
