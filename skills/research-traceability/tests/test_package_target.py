from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts' / 'package_target.py'


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class PackageTargetTests(unittest.TestCase):
    def test_same_source_produces_same_archive_bytes(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            target = base / 'demo'
            target.mkdir()
            (target / 'SKILL.md').write_text(
                '---\nname: demo\ndescription: Demo target used for deterministic packaging tests.\n---\n\n# Demo\n',
                encoding='utf-8'
            )
            (target / 'agents').mkdir()
            (target / 'agents' / 'openai.yaml').write_text(
                'interface:\n  display_name: "Demo"\n  short_description: "Demo target"\n',
                encoding='utf-8'
            )

            outputs = []
            for name in ['one', 'two']:
                out_dir = base / name
                out_dir.mkdir()
                package = out_dir / 'skill.zip'
                receipt = out_dir / 'receipt.json'
                result = subprocess.run([
                    sys.executable, str(SCRIPT), '--target', str(target),
                    '--output', str(package), '--receipt', str(receipt)
                ], capture_output=True, text=True, check=False)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertTrue(package.exists())
                self.assertTrue(receipt.exists())
                outputs.append(package)

            self.assertEqual(digest(outputs[0]), digest(outputs[1]))


if __name__ == '__main__':
    unittest.main()
