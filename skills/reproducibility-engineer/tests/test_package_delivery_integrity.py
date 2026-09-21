from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "package_target.py"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)


def make_skill(base: Path) -> Path:
    skill = base / "demo-skill"
    skill.mkdir()
    (skill / "SKILL.md").write_text(
        "---\nname: demo-skill\ndescription: Deterministic demo skill used to test package delivery integrity.\n---\n\n# Demo\n\nDo the deterministic thing.\n",
        encoding="utf-8",
    )
    return skill


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


class PackageDeliveryIntegrityTests(unittest.TestCase):
    def test_package_and_receipt_alias_is_rejected_without_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            skill = make_skill(base)
            output = base / "skill.zip"
            receipt = base / "receipt.json"
            output.write_bytes(b"last-good")
            try:
                os.link(output, receipt)
            except OSError:
                self.skipTest("hard links are unavailable in this environment")
            before = output.read_bytes()
            result = run("--target", str(skill), "--output", str(output), "--json", str(receipt))
            self.assertEqual(result.returncode, 1)
            report = json.loads(result.stdout)
            self.assertEqual(report["code"], "output/target-alias")
            self.assertEqual(output.read_bytes(), before)
            self.assertEqual(receipt.read_bytes(), before)

    def test_symlink_output_resolving_to_non_zip_is_rejected(self) -> None:
        if not hasattr(os, "symlink"):
            self.skipTest("symlinks are unavailable in this environment")
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            skill = make_skill(base)
            marker = base / "marker.env"
            marker.write_bytes(b"keep-me")
            output = base / "skill.zip"
            try:
                output.symlink_to(marker)
            except OSError:
                self.skipTest("symlink creation is unavailable in this environment")
            result = run("--target", str(skill), "--output", str(output))
            self.assertEqual(result.returncode, 1)
            report = json.loads(result.stdout)
            self.assertEqual(report["code"], "output/resolved-extension")
            self.assertEqual(marker.read_bytes(), b"keep-me")
            self.assertTrue(output.is_symlink())

    def test_success_receipt_matches_committed_package(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            skill = make_skill(base)
            output = base / "skill.zip"
            receipt = base / "receipt.json"
            result = run("--target", str(skill), "--output", str(output), "--json", str(receipt))
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            self.assertTrue(output.is_file())
            self.assertTrue(receipt.is_file())
            report = json.loads(receipt.read_text(encoding="utf-8"))
            self.assertEqual(report["status"], "pass")
            self.assertEqual(report["stage"], "committed")
            self.assertEqual(report["package_sha256"], sha256(output))
            self.assertTrue(report["output_preserved_on_failure"])
            with zipfile.ZipFile(output, "r") as zf:
                self.assertIsNone(zf.testzip())
                self.assertIn("demo-skill/SKILL.md", zf.namelist())

    def test_validation_failure_preserves_existing_package_and_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            skill = base / "demo-skill"
            skill.mkdir()
            (skill / "SKILL.md").write_text(
                "---\nname: Demo Skill\ndescription: Deliberately invalid demo package used to test failure preservation.\n---\n\n# Demo\n",
                encoding="utf-8",
            )
            output = base / "skill.zip"
            receipt = base / "receipt.json"
            output.write_bytes(b"old-package")
            receipt.write_text('{"status":"pass","old":true}\n', encoding="utf-8")
            old_output = output.read_bytes()
            old_receipt = receipt.read_bytes()
            result = run("--target", str(skill), "--output", str(output), "--json", str(receipt))
            self.assertEqual(result.returncode, 1)
            self.assertEqual(output.read_bytes(), old_output)
            self.assertEqual(receipt.read_bytes(), old_receipt)
            failure = json.loads(result.stdout)
            self.assertEqual(failure["stage"], "validation")


if __name__ == "__main__":
    unittest.main()
