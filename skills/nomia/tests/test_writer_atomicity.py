from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import append_governance_decision_entry
import nomia_utils
import normalize_human_artifacts
import update_template_lists
import upsert_rfc_entry


class WriterAtomicityTests(unittest.TestCase):
    def assert_failed_replace_preserves(self, path: Path, operation) -> None:
        original = path.read_bytes()
        with patch.object(nomia_utils.os, "replace", side_effect=OSError("simulated replace failure")):
            with self.assertRaises(OSError):
                operation()
        self.assertEqual(path.read_bytes(), original)
        self.assertEqual(list(path.parent.glob(f".{path.name}.*.tmp")), [])

    def test_rfc_upsert_preserves_original_on_replace_failure(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "rfc-proposals.md"
            path.write_text("# RFC Proposals\n\n## Entries\n\nNo RFC proposals recorded.\n", encoding="utf-8")
            self.assert_failed_replace_preserves(
                path,
                lambda: upsert_rfc_entry.upsert_entry(path, "safe-package", "### safe-package - Safe package\n\n- Status: draft\n"),
            )

    def test_governance_append_preserves_original_on_replace_failure(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "governance-decisions.md"
            path.write_text("# Governance Decisions\n\n## Entries\n\nNo governance decisions recorded.\n", encoding="utf-8")
            self.assert_failed_replace_preserves(
                path,
                lambda: append_governance_decision_entry.append_entry(path, "### 2026-07-21 - Decision\n\n- Status: accepted\n"),
            )

    def test_structured_writer_preserves_original_on_replace_failure(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "artifact.json"
            path.write_text('{"before": true}\n', encoding="utf-8")
            self.assert_failed_replace_preserves(path, lambda: update_template_lists.write_artifact(path, {"after": True}))

    def test_markdown_normalizer_preserves_original_on_replace_failure(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "status.md"
            path.write_text("# Status   \n", encoding="utf-8")
            self.assert_failed_replace_preserves(path, lambda: normalize_human_artifacts.normalize_markdown(path, False))


if __name__ == "__main__":
    unittest.main()
