from __future__ import annotations

import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from package_skill import REQUIRED_GATE_NAMES, tree_digest, validate_and_package
from validate_skill_package import validate_package


def passing_evidence(root: Path) -> dict[str, object]:
    return {
        "schema_version": 1,
        "target_tree_sha256": tree_digest(root),
        "gates": [
            {
                "name": name,
                "command": ["isolated-runner", name],
                "returncode": 0,
                "stdout": "pass",
                "stderr": "",
            }
            for name in REQUIRED_GATE_NAMES
        ],
    }


class PackagingSecurityTests(unittest.TestCase):

    def test_packaging_requires_external_validation_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "skill.zip"
            result = validate_and_package(ROOT, output)
            self.assertEqual(result.status, "fail")
            self.assertFalse(output.exists())
            self.assertIn("never executes validator code", result.gates[0].stderr)

    def test_valid_external_evidence_packages_without_subprocess_execution(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            temp = Path(tmp)
            evidence = temp / "evidence.json"
            evidence.write_text(json.dumps(passing_evidence(ROOT)), encoding="utf-8")
            output = temp / "skill.zip"

            with patch("package_skill.subprocess.run", side_effect=AssertionError("subprocess must not run")):
                result = validate_and_package(ROOT, output, evidence)

            self.assertEqual(result.status, "pass")
            self.assertTrue(output.is_file())
            with zipfile.ZipFile(output) as archive:
                self.assertIn("nomia/SKILL.md", archive.namelist())

    def test_stale_tree_digest_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            temp = Path(tmp)
            payload = passing_evidence(ROOT)
            payload["target_tree_sha256"] = "0" * 64
            evidence = temp / "evidence.json"
            evidence.write_text(json.dumps(payload), encoding="utf-8")
            output = temp / "skill.zip"

            result = validate_and_package(ROOT, output, evidence)

            self.assertEqual(result.status, "fail")
            self.assertFalse(output.exists())
            self.assertIn("does not match the current target tree", result.gates[0].stderr)

    def test_symlink_in_package_tree_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as outside_tmp:
            root = Path(tmp)
            (root / "SKILL.md").write_text("sample", encoding="utf-8")
            outside = Path(outside_tmp) / "secret.txt"
            outside.write_text("must not be packaged", encoding="utf-8")
            link = root / "linked-secret.txt"
            try:
                link.symlink_to(outside)
            except (OSError, NotImplementedError) as exc:
                self.skipTest(f"symlink creation is unavailable: {exc}")

            with self.assertRaisesRegex(ValueError, "symbolic links are not allowed"):
                tree_digest(root)
            errors = validate_package(root)
            self.assertTrue(any("symbolic link is not allowed" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
