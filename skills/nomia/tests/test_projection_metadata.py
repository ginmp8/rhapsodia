import tempfile
import unittest
from pathlib import Path

from validate_projection_metadata import validate


class ProjectionMetadataTests(unittest.TestCase):
    def test_valid_metadata_passes(self):
        text = """# Status\n\n## Projection Metadata\n\n- Authority: nomia-projection\n- Generated From: ops.yaml\n- Generated At: 2026-07-20T12:00:00Z\n- Evidence As Of: 2026-07-20T11:55:00Z\n"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "status.md"
            path.write_text(text, encoding="utf-8")
            errors = validate(path)
        self.assertEqual(errors, [])

    def test_missing_metadata_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "status.md"
            path.write_text("# Status\n", encoding="utf-8")
            errors = validate(path)
        self.assertTrue(any("Projection Metadata" in error for error in errors))

    def test_unknown_evidence_timestamp_fails(self):
        text = """# Status\n\n## Projection Metadata\n\n- Authority: nomia-projection\n- Generated From: ops.yaml\n- Generated At: 2026-07-20T12:00:00Z\n- Evidence As Of: unknown\n"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "status.md"
            path.write_text(text, encoding="utf-8")
            errors = validate(path)
        self.assertTrue(any("Evidence As Of" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
