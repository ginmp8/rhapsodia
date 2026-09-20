from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from validate_skill_package import ValidationResult, validate_reproducibility_controls


class ValidationGateIntegrationTests(unittest.TestCase):
    def copy_skill(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp = tempfile.TemporaryDirectory()
        target = Path(temp.name) / "mago"
        shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
        return temp, target

    def test_reproducibility_controls_pass_current_package(self) -> None:
        result = ValidationResult()
        validate_reproducibility_controls(ROOT, result)
        self.assertEqual(result.status, "pass", result.errors)

    def test_artifact_matrix_gate_rejects_missing_artifact(self) -> None:
        temp, target = self.copy_skill()
        try:
            matrix = target / "references" / "artifact-decision-matrix.md"
            lines = matrix.read_text(encoding="utf-8").splitlines()
            matrix.write_text("\n".join(line for line in lines if "migration-strategy.md" not in line) + "\n", encoding="utf-8")
            result = ValidationResult()
            validate_reproducibility_controls(target, result)
            self.assertEqual(result.status, "fail")
            self.assertTrue(any("artifact decision matrix" in error for error in result.errors), result.errors)
        finally:
            temp.cleanup()

    def test_planning_experience_gate_rejects_lost_control_plane_route(self) -> None:
        temp, target = self.copy_skill()
        try:
            skill = target / "SKILL.md"
            text = skill.read_text(encoding="utf-8")
            text = text.replace("[getting started](references/getting-started.md)", "getting started")
            skill.write_text(text, encoding="utf-8")
            result = ValidationResult()
            validate_reproducibility_controls(target, result)
            self.assertEqual(result.status, "fail")
            self.assertTrue(any("planning experience" in error for error in result.errors), result.errors)
        finally:
            temp.cleanup()


if __name__ == "__main__":
    unittest.main()
