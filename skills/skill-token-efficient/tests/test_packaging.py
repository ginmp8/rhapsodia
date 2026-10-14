"""Regression: deterministic ZIP ordering and receipt integrity."""
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


class PackagingTests(unittest.TestCase):
    def test_package_sort_and_hash(self):
        with tempfile.TemporaryDirectory() as dest:
            out=Path(dest)/'skill.zip'
            receipt=Path(dest)/'receipt.json'
            proc=subprocess.run([sys.executable, '-S', str(ROOT/'scripts/package_skill.py'),
                                '--target',str(ROOT),'--output',str(out),'--receipt',str(receipt),'--validate'],
                               text=True,capture_output=True)
            self.assertEqual(proc.returncode,0,proc.stderr)
            data=json.loads(receipt.read_text())
            self.assertEqual(data['status'],'pass')
            self.assertEqual(hashlib.sha256(out.read_bytes()).hexdigest(),data['package_sha256'])
            with zipfile.ZipFile(out) as z:
                names=z.namelist()
                self.assertEqual(names,sorted(names))
                self.assertEqual(names.count('SKILL.md'),1)
                self.assertTrue(all(x.date_time==(1980,1,1,0,0,0) for x in z.infolist()))
                self.assertNotIn('__pycache__', ' '.join(names))


if __name__=='__main__':unittest.main()
