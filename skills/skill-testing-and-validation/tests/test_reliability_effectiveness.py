from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from assess_stability import classify_stability  # noqa: E402
from environment_fingerprint import fingerprint  # noqa: E402
from evidence_identity import tree_identity  # noqa: E402
from package_skill import package as package_skill  # noqa: E402
from run_gate import make_receipt  # noqa: E402


class ReliabilityEffectivenessTests(unittest.TestCase):
    def test_tree_identity_ignores_runtime_cache(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            src = root / "a.py"
            src.write_text("x = 1\n", encoding="utf-8")
            first = tree_identity(root)
            cache = root / "__pycache__"
            cache.mkdir()
            (cache / "a.pyc").write_bytes(b"runtime")
            self.assertEqual(first, tree_identity(root))
            src.write_text("x = 2\n", encoding="utf-8")
            self.assertNotEqual(first["sha256"], tree_identity(root)["sha256"])

    def test_environment_context_is_bounded(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            result = fingerprint(Path(td), [])
        self.assertEqual(1, result["fingerprint_version"])
        self.assertEqual({"locale", "timezone", "python_hash_seed", "ci"}, set(result["execution_context"]))
        serialized = json.dumps(result).lower()
        for forbidden in ("password", "secret", "token"):
            self.assertNotIn(forbidden, serialized)

    def test_gate_receipt_records_material_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            target = root / "value.txt"
            target.write_text("before\n", encoding="utf-8")
            argv = [sys.executable, "-c", "from pathlib import Path; Path('value.txt').write_text('after\\n')"]
            receipt, _ = make_receipt(root, "test", argv, True, 30)
            self.assertTrue(receipt["target_mutated"])
            self.assertNotEqual(receipt["target_identity"], receipt["target_identity_after"])

    def test_stability_is_separate_from_gate_status(self) -> None:
        stable = [
            {"status": "pass", "exit_code": 0, "classification": "test", "target_mutated": False},
            {"status": "pass", "exit_code": 0, "classification": "test", "target_mutated": False},
        ]
        mixed = [stable[0], {"status": "fail", "exit_code": 1, "classification": "test", "target_mutated": False}]
        blocked = [stable[0], {"status": "blocked", "exit_code": None, "classification": "environment", "target_mutated": False}]
        self.assertEqual(("stable", "pass"), classify_stability(stable))
        self.assertEqual(("unstable", "mixed"), classify_stability(mixed))
        self.assertEqual(("inconclusive", "blocked"), classify_stability(blocked))

    def test_packager_rejects_output_inside_target(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "demo-skill"
            root.mkdir()
            (root / "SKILL.md").write_text("---\nname: demo-skill\ndescription: package integrity test\n---\n", encoding="utf-8")
            result = package_skill(root, root / "skill.zip")
            self.assertFalse(result["passed"])
            self.assertTrue(any("inside target" in item.lower() for item in result["errors"]))

    def test_cli_rejects_package_report_alias(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "demo-skill"
            root.mkdir()
            (root / "SKILL.md").write_text("---\nname: demo-skill\ndescription: package alias test\n---\n", encoding="utf-8")
            output = base / "skill.zip"
            proc = subprocess.run(
                [sys.executable, str(SCRIPTS / "package_skill.py"), str(root), str(output), "--report", str(output)],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(0, proc.returncode)
            if output.exists():
                self.assertTrue(zipfile.is_zipfile(output))


if __name__ == "__main__":
    unittest.main()
