from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import package_skill  # noqa: E402
from package_skill import package  # noqa: E402
from _swp_common import sha256_file  # noqa: E402


class PackageHardeningTests(unittest.TestCase):
    def test_receipt_describes_exact_committed_package(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            output = base / "skill.zip"
            receipt = base / "receipt.json"
            result = package(ROOT, output, receipt)
            self.assertEqual("pass", result["status"])
            self.assertEqual(result["package_sha256"], sha256_file(output))
            written = json.loads(receipt.read_text(encoding="utf-8"))
            self.assertEqual(result["package_sha256"], written["package_sha256"])
            self.assertEqual(str(output.resolve()), written["output"])

    def test_receipt_commit_failure_restores_last_good_package_and_receipt(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            output = base / "skill.zip"
            receipt = base / "receipt.json"
            output.write_bytes(b"last-good-package")
            receipt.write_text('{"last_good":true}\n', encoding="utf-8")
            output_before = output.read_bytes()
            receipt_before = receipt.read_bytes()
            real_replace = package_skill.os.replace

            def fail_receipt_commit(src, dst):
                if Path(dst) == receipt.resolve():
                    raise OSError("injected receipt commit failure")
                return real_replace(src, dst)

            with patch.object(package_skill.os, "replace", side_effect=fail_receipt_commit):
                result = package(ROOT, output, receipt)

            self.assertEqual("failed_recovered", result["status"])
            self.assertEqual(output_before, output.read_bytes())
            self.assertEqual(receipt_before, receipt.read_bytes())

    def test_output_and_receipt_alias_blocks_before_write(self):
        with tempfile.TemporaryDirectory() as td:
            same = Path(td) / "same.zip"
            result = package(ROOT, same, same)
            self.assertEqual("blocked", result["status"])
            self.assertEqual("OUTPUT_RECEIPT_ALIAS", result["code"])
            self.assertFalse(same.exists())


if __name__ == "__main__":
    unittest.main()
