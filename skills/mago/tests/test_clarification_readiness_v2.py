from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_clarification_readiness import validate_notes  # noqa: E402

GOLDEN = ROOT / "examples" / "golden" / "clarification-v2" / "notes.md"


class ClarificationReadinessV2Tests(unittest.TestCase):
    def copy(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp = tempfile.TemporaryDirectory(prefix="mago-clarification-v2-")
        notes = Path(temp.name) / "notes.md"
        shutil.copy2(GOLDEN, notes)
        return temp, notes

    def test_golden_handoff_passes(self) -> None:
        self.assertEqual(validate_notes(GOLDEN, require_v2=True, handoff=True), [])

    def test_legacy_notes_are_compatible_without_v2_requirement(self) -> None:
        with tempfile.TemporaryDirectory(prefix="mago-legacy-notes-") as temp:
            notes = Path(temp) / "notes.md"
            notes.write_text("# Notes\n\n## Assumptions\n", encoding="utf-8")
            self.assertEqual(validate_notes(notes), [])

    def test_open_blocker_blocks_handoff(self) -> None:
        temp, notes = self.copy()
        try:
            notes.write_text(notes.read_text().replace("- Status: resolved", "- Status: open", 1), encoding="utf-8")
            errors = validate_notes(notes, require_v2=True, handoff=True)
            self.assertTrue(any("handoff blocked" in error for error in errors), errors)
        finally:
            temp.cleanup()

    def test_open_high_assumption_blocks_handoff(self) -> None:
        temp, notes = self.copy()
        try:
            notes.write_text(notes.read_text().replace("- Status: confirmed", "- Status: open", 1), encoding="utf-8")
            errors = validate_notes(notes, require_v2=True, handoff=True)
            self.assertTrue(any("open high" in error for error in errors), errors)
        finally:
            temp.cleanup()

    def test_closed_record_requires_resolution_evidence(self) -> None:
        temp, notes = self.copy()
        try:
            text = notes.read_text()
            text = text.replace("- Resolution evidence: The current schema and compatibility contract preserve the key.\n", "")
            notes.write_text(text, encoding="utf-8")
            errors = validate_notes(notes, require_v2=True)
            self.assertTrue(any("Resolution evidence" in error for error in errors), errors)
        finally:
            temp.cleanup()

    def test_missing_owner_is_rejected(self) -> None:
        temp, notes = self.copy()
        try:
            notes.write_text(notes.read_text().replace("- Owner: Mago planner\n", "", 1), encoding="utf-8")
            errors = validate_notes(notes, require_v2=True)
            self.assertTrue(any("Owner" in error for error in errors), errors)
        finally:
            temp.cleanup()


if __name__ == "__main__":
    unittest.main()
