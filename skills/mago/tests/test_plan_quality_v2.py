from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_plan_quality import validate_package  # noqa: E402

GOLDEN = ROOT / "examples" / "golden" / "governed-quality-v2"


class PlanQualityV2Tests(unittest.TestCase):
    def copy(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp = tempfile.TemporaryDirectory(prefix="mago-quality-v2-")
        package = Path(temp.name) / "package"
        shutil.copytree(GOLDEN, package)
        return temp, package

    def test_v2_golden_passes(self) -> None:
        self.assertEqual(validate_package(GOLDEN, require_v2=True), [])

    def test_v1_golden_remains_compatible(self) -> None:
        legacy = ROOT / "examples" / "golden" / "governed-quality"
        self.assertEqual(validate_package(legacy, require_v2=False), [])

    def test_missing_criticality_is_rejected(self) -> None:
        temp, package = self.copy()
        try:
            path = package / "prd.md"
            path.write_text(path.read_text().replace("- Criticality: high\n", ""), encoding="utf-8")
            errors = validate_package(package, require_v2=True)
            self.assertTrue(any("Criticality" in error for error in errors), errors)
        finally:
            temp.cleanup()

    def test_high_requirement_requires_recovery_path(self) -> None:
        temp, package = self.copy()
        try:
            path = package / "prd.md"
            path.write_text(path.read_text().replace("- Path: recovery", "- Path: boundary"), encoding="utf-8")
            errors = validate_package(package, require_v2=True)
            self.assertTrue(any("requires a linked recovery" in error for error in errors), errors)
        finally:
            temp.cleanup()

    def test_every_acceptance_requires_validation_coverage(self) -> None:
        temp, package = self.copy()
        try:
            path = package / "validation.md"
            text = path.read_text()
            start = text.index("### VAL-003")
            path.write_text(text[:start], encoding="utf-8")
            errors = validate_package(package, require_v2=True)
            self.assertTrue(any("coverage for every AC" in error for error in errors), errors)
        finally:
            temp.cleanup()

    def test_v2_validation_requires_evidence_capture(self) -> None:
        temp, package = self.copy()
        try:
            path = package / "validation.md"
            path.write_text(path.read_text().replace("- Evidence capture:", "- Evidence omitted:", 1), encoding="utf-8")
            errors = validate_package(package, require_v2=True)
            self.assertTrue(any("Evidence capture" in error for error in errors), errors)
        finally:
            temp.cleanup()


if __name__ == "__main__":
    unittest.main()
