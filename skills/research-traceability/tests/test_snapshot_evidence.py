from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts' / 'snapshot_evidence.py'


class SnapshotEvidenceTests(unittest.TestCase):
    def test_capture_and_verify_then_detect_change(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            source = base / 'source'
            source.mkdir()
            (source / 'report.md').write_text('frozen evidence', encoding='utf-8')
            snapshot = base / 'snapshot'
            manifest = base / 'manifest.json'

            capture = subprocess.run([
                sys.executable, str(SCRIPT), 'capture',
                '--root', str(source), '--path', 'report.md',
                '--snapshot-dir', str(snapshot), '--manifest', str(manifest)
            ], capture_output=True, text=True, check=False)
            self.assertEqual(capture.returncode, 0, capture.stdout + capture.stderr)
            self.assertTrue(manifest.exists())

            verify = subprocess.run([
                sys.executable, str(SCRIPT), 'verify', '--manifest', str(manifest)
            ], capture_output=True, text=True, check=False)
            self.assertEqual(verify.returncode, 0, verify.stdout + verify.stderr)

            (source / 'report.md').write_text('changed evidence', encoding='utf-8')
            changed = subprocess.run([
                sys.executable, str(SCRIPT), 'verify', '--manifest', str(manifest)
            ], capture_output=True, text=True, check=False)
            self.assertNotEqual(changed.returncode, 0)
            report = json.loads(changed.stdout)
            self.assertEqual(report['source_changed'], ['report.md'])


if __name__ == '__main__':
    unittest.main()
