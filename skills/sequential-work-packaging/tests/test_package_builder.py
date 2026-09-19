from __future__ import annotations

import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from package_skill import package  # noqa: E402
from verify_evals import verify  # noqa: E402


class PackageBuilderTests(unittest.TestCase):
    def test_frozen_evals_verify(self):
        self.assertEqual("pass", verify(ROOT)["status"])

    def test_deterministic_zip(self):
        with tempfile.TemporaryDirectory() as td:
            a = Path(td) / "a.zip"
            b = Path(td) / "b.zip"
            ra = package(ROOT, a)
            rb = package(ROOT, b)
            self.assertEqual("pass", ra["status"])
            self.assertEqual(ra["package_sha256"], rb["package_sha256"])
            with zipfile.ZipFile(a) as zf:
                names = zf.namelist()
            self.assertTrue(all(name.startswith("sequential-work-packaging/") for name in names))
            self.assertIn("sequential-work-packaging/SKILL.md", names)


if __name__ == "__main__":
    unittest.main()
