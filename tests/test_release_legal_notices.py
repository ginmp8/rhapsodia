"""Ensure consolidated MIT notices remain present in full and standalone distributions."""
from __future__ import annotations
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
NAMES = ("code-review", "domain-modeling", "grill-me", "grill-with-docs",
         "grilling", "retro", "wayfinder")
NOTICE = ROOT / "licenses" / "third-party" / "mattpocock-skills-MIT.txt"


class CentralLicenseTests(unittest.TestCase):
    def test_repository_has_one_verbatim_mit_notice(self):
        raw = NOTICE.read_bytes()
        self.assertTrue(raw.startswith(b"MIT License\n\nCopyright (c) 2026 Matt Pocock"))
        self.assertIn(b"The above copyright notice and this permission notice", raw)
        self.assertIn(b"THE SOFTWARE IS PROVIDED", raw)
        self.assertEqual(raw.count(b"Copyright (c) 2026 Matt Pocock"), 1)
        import runpy
        include = runpy.run_path(str(ROOT / "scripts/package_policy.py"))["include"]
        self.assertTrue(include(NOTICE, ROOT))
        for name in NAMES:
            with self.subTest(skill=name):
                root = ROOT / "skills" / name
                self.assertFalse((root / "LICENSE-MIT").exists())
                source = (root / "SOURCE.md").read_text(encoding="utf-8")
                self.assertIn("licenses/third-party/mattpocock-skills-MIT.txt", source)
                self.assertIn("Reference Git blob SHA", source)
                self.assertIn("Copyright (c) 2026 Matt Pocock", source)
                self.assertEqual((root / "VERSION").read_text().strip(), "0.1.2")
                self.assertIn("## [0.1.2]", (root / "CHANGELOG.md").read_text())
        self.assertTrue((ROOT / "licenses" / "README.md").is_file())

    def test_all_standalone_archives_restore_full_notice(self):
        expected = NOTICE.read_bytes()
        with tempfile.TemporaryDirectory() as td:
            for name in NAMES:
                with self.subTest(skill=name):
                    output = Path(td) / (name + ".zip")
                    cmd = [sys.executable, "-B",
                           str(ROOT / "scripts/package_attributed_skill.py"),
                           "--skill", name, "--output", str(output)]
                    completed = subprocess.run(cmd, cwd=ROOT,
                                               capture_output=True, text=True,
                                               timeout=30, check=False)
                    self.assertEqual(completed.returncode, 0,
                                     completed.stderr + completed.stdout)
                    receipt = json.loads(completed.stdout)
                    self.assertEqual(receipt["skill"], name)
                    with ZipFile(output) as archive:
                        self.assertIsNone(archive.testzip())
                        self.assertEqual(archive.read(f"{name}/LICENSE-MIT"), expected)
                        self.assertIn(f"{name}/SKILL.md", archive.namelist())
                        self.assertIn(f"{name}/SOURCE.md", archive.namelist())
                        self.assertIn(f"{name}/agents/openai.yaml", archive.namelist())
                        self.assertIn(f"{name}/assets/icon.svg", archive.namelist())

    def test_archives_are_bitwise_deterministic(self):
        with tempfile.TemporaryDirectory() as td:
            a, b = Path(td) / "one.zip", Path(td) / "two.zip"
            cmd = [sys.executable, "-B", str(ROOT / "scripts/package_attributed_skill.py"),
                   "--skill", "wayfinder", "--output"]
            for out in (a, b):
                proc = subprocess.run(cmd + [str(out)], cwd=ROOT,
                                      capture_output=True, text=True, timeout=30)
                self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(a.read_bytes(), b.read_bytes())


if __name__ == "__main__":
    unittest.main()
