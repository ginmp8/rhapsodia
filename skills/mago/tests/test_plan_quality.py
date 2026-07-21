from __future__ import annotations

import shutil
import tempfile
import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from validate_plan_quality import validate_package
GOLDEN = ROOT / "examples" / "golden" / "governed-quality"


class PlanQualityTests(unittest.TestCase):
    def copy_golden(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp = tempfile.TemporaryDirectory(prefix="mago-plan-quality-")
        package = Path(temp.name) / "package"
        shutil.copytree(GOLDEN, package)
        return temp, package

    def test_governed_quality_golden_passes(self) -> None:
        self.assertEqual(validate_package(GOLDEN), [])

    def test_requirement_without_evidence_basis_is_rejected(self) -> None:
        temp, package = self.copy_golden()
        try:
            path = package / "prd.md"
            path.write_text(path.read_text(encoding="utf-8").replace("- Evidence basis: current export contract and repository handler inspection\n", ""), encoding="utf-8")
            errors = validate_package(package)
            self.assertTrue(any("missing quality field `Evidence basis`" in error for error in errors), errors)
        finally:
            temp.cleanup()

    def test_acceptance_requires_failure_or_boundary_path(self) -> None:
        temp, package = self.copy_golden()
        try:
            path = package / "prd.md"
            path.write_text(path.read_text(encoding="utf-8").replace("- Path: abuse", "- Path: normal"), encoding="utf-8")
            errors = validate_package(package)
            self.assertTrue(any("boundary, error, recovery, or abuse path" in error for error in errors), errors)
        finally:
            temp.cleanup()

    def test_design_requires_two_explicit_options(self) -> None:
        temp, package = self.copy_golden()
        try:
            path = package / "technical-design.md"
            text = path.read_text(encoding="utf-8")
            start = text.index("### OPTION-001")
            end = text.index("### OPTION-002")
            path.write_text(text[:start] + text[end:], encoding="utf-8")
            errors = validate_package(package)
            self.assertTrue(any("at least two explicit OPTION" in error for error in errors), errors)
        finally:
            temp.cleanup()

    def test_validation_requires_reproducible_procedure(self) -> None:
        temp, package = self.copy_golden()
        try:
            path = package / "validation.md"
            path.write_text(path.read_text(encoding="utf-8").replace("- Command or procedure: run the export API and worker contract/integration suite with omitted and selected fields", "- Command or procedure: verify it works"), encoding="utf-8")
            errors = validate_package(package)
            self.assertTrue(any("not observable/reproducible" in error for error in errors), errors)
        finally:
            temp.cleanup()

    def test_nfr_requires_metric_threshold_and_validation(self) -> None:
        temp, package = self.copy_golden()
        try:
            path = package / "prd.md"
            path.write_text(path.read_text(encoding="utf-8").replace("- Threshold: at most 25 milliseconds for 100 requested identifiers\n", ""), encoding="utf-8")
            errors = validate_package(package)
            self.assertTrue(any("NFR-001` missing quality field `Threshold`" in error for error in errors), errors)
        finally:
            temp.cleanup()


if __name__ == "__main__":
    unittest.main()
