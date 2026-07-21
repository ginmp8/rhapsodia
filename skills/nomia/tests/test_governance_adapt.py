import contextlib
import io
import tempfile
import unittest
from pathlib import Path

import yaml

from adapt_governance import adapt, main
from validate_ops import validate


class GovernanceAdaptTests(unittest.TestCase):
    def legacy(self):
        return {
            "schema_version": 1,
            "spec_id": "spec-2026-04-20-demo--" + "01ARZ3NDEKTSV4RRFFQ69G5FAV",
            "request": {"title": "Demo", "requester": "product", "requested_date": "2026-04-20", "source": "manual"},
            "ownership": {"owner": "team-a", "backup_owner": None, "stakeholders": []},
            "planning": {"sprint": None, "bucket": "roadmap", "target_date": None, "commitment": "tentative"},
            "priority": {"level": "medium", "rationale": "legacy evidence"},
            "status": {"state": "done", "summary": "legacy summary", "updated_at": "2026-04-21"},
            "blockers": [], "replanning": [], "tags": [],
            "links": {"mago": [], "magia": [], "external": []},
            "technical_state": {"validation": {"state": "passed"}},
        }

    def test_adapt_preserves_governance_facts_but_not_technical_truth(self):
        canonical, report = adapt(
            self.legacy(),
            source_path="legacy.yaml",
            observed_at="2026-07-20T12:00:00Z",
            spec_id="spec-2026-07-20-demo",
            spec_id_provenance="registry/spec-2026-07-20-demo.yaml",
            profile="governed",
            lifecycle="triage",
            governance_status="triage",
        )
        self.assertEqual(canonical["request"]["title"], "Demo")
        self.assertEqual(canonical["technical_state"]["validation"]["state"], "unknown")
        self.assertEqual(canonical["governance"]["status"], "triage")
        self.assertEqual(report["legacy_spec_id"], self.legacy()["spec_id"])

    def test_adapt_output_passes_canonical_validator(self):
        canonical, _ = adapt(
            self.legacy(),
            source_path="legacy.yaml",
            observed_at="2026-07-20T12:00:00Z",
            spec_id="spec-2026-07-20-demo",
            spec_id_provenance="registry/spec-2026-07-20-demo.yaml",
            profile="standard",
            lifecycle="intake",
            governance_status="intake",
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ops.yaml"
            path.write_text(yaml.safe_dump(canonical, sort_keys=False), encoding="utf-8")
            errors, _ = validate(path, require_canonical=True)
        self.assertEqual(errors, [])

    def test_cli_refuses_source_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "legacy.yaml"
            source.write_text(yaml.safe_dump(self.legacy()), encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                rc = main([
                    str(source), str(source),
                "--spec-id", "spec-2026-07-20-demo",
                "--spec-id-provenance", "registry/spec-2026-07-20-demo.yaml",
                    "--profile", "standard", "--lifecycle", "intake", "--governance-status", "intake",
                ])
        self.assertEqual(rc, 1)


if __name__ == "__main__":
    unittest.main()
