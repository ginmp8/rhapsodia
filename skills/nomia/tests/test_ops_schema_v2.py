import tempfile
import unittest
from pathlib import Path

from validate_ops import validate
from write_ops_scaffold import render


class OpsSchemaV2Tests(unittest.TestCase):
    def test_repository_scaffold_is_schema_v2_and_canonical(self):
        text = render(
            "spec-2026-07-20-demo-feature",
            "registry/spec-2026-07-20-demo-feature.yaml",
            "governed",
            "triage",
            "triage",
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ops.yaml"
            path.write_text(text, encoding="utf-8")
            errors, warnings = validate(path, require_canonical=True)
        self.assertEqual(errors, [])
        self.assertTrue(any("provenance.updated_at is missing" in warning for warning in warnings))

    def test_status_must_mirror_governance_status(self):
        text = render(
            "spec-2026-07-20-demo-feature",
            "registry/spec-2026-07-20-demo-feature.yaml",
            "standard",
            "track",
            "in_progress",
        ).replace("status:\n  state: in_progress", "status:\n  state: blocked", 1)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ops.yaml"
            path.write_text(text, encoding="utf-8")
            errors, _ = validate(path, require_canonical=True)
        self.assertTrue(any("must mirror" in error for error in errors))

    def test_legacy_schema_is_not_canonical(self):
        text = render("spec-2026-07-20-demo-feature", "registry/evidence").replace("schema_version: 2", "schema_version: 1", 1)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ops.yaml"
            path.write_text(text, encoding="utf-8")
            errors, _ = validate(path, require_canonical=True)
        self.assertTrue(any("requires `schema_version: 2`" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
