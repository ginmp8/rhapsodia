import importlib.util
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


evaluate = load("evaluate_governance_hardening", ROOT / "scripts" / "evaluate_governance.py")
project = load("project_governance_views_hardening", ROOT / "scripts" / "project_governance_views.py")
AS_OF = datetime(2026, 7, 20, tzinfo=timezone.utc)


class GovernanceContractHardeningTests(unittest.TestCase):
    def canonical_record(self):
        return {
            "schema_version": 2,
            "spec_id": "spec-2026-07-20-demo",
            "spec_id_provenance": "registry/spec-2026-07-20-demo.yaml",
            "request": {"title": "Demo", "requester": "Requester", "context": "Outcome"},
            "ownership": {"owner": "Owner", "stakeholders": ["Ops"]},
            "planning": {"target_date": "2026-08-01"},
            "priority": {"level": "high", "impact": "high"},
            "status": {"state": "in_progress", "summary": "Building", "updated_at": "2026-07-20", "confidence": "medium"},
            "blockers": [],
            "risks": [],
            "links": {"external": []},
            "governance": {"profile": "standard", "lifecycle": "track", "status": "in_progress"},
            "technical_state": {
                "planning": {"state": "ready", "source": "mago/spec", "observed_at": "2026-07-20T10:00:00+00:00"},
                "execution": {"state": "in_progress", "source": "magia/notes", "observed_at": "2026-07-20T11:00:00+00:00"},
                "validation": {"state": "unknown", "source": None, "observed_at": None},
            },
            "release": {"state": "unknown", "released_at": None, "evidence": []},
            "dependencies": [],
            "decision": {"state": "unknown", "current": None, "evidence": []},
            "handoffs": {"mago": {"state": "accepted", "source": "roadmap.yaml", "observed_at": "2026-07-20"}, "magia": {"state": "unknown", "source": None, "observed_at": None}},
            "provenance": {"updated_at": "2026-07-20T12:00:00+00:00", "facts": {}, "changes": []},
        }

    def test_projection_rejects_cross_dimension_states(self):
        cases = [
            ("planning", "passed"),
            ("execution", "failed"),
            ("validation", "complete"),
        ]
        for dimension, state in cases:
            with self.subTest(dimension=dimension, state=state):
                record = self.canonical_record()
                record["technical_state"][dimension] = {
                    "state": state,
                    "source": "evidence",
                    "observed_at": "2026-07-20T10:00:00+00:00",
                }
                errors, _ = project.validate_record(record)
                self.assertTrue(any(f"technical_state.{dimension}.state" in error for error in errors))

    def test_projection_rejects_legacy_or_missing_governance_state(self):
        record = self.canonical_record()
        record["status"]["state"] = "done"
        record["governance"]["status"] = "unknown"
        errors, _ = project.validate_record(record)
        self.assertTrue(any("governance.status" in error for error in errors))
        self.assertTrue(any("status.state conflicts" in error for error in errors))

    def test_non_unknown_technical_state_requires_observed_at(self):
        record = self.canonical_record()
        record["technical_state"]["execution"]["observed_at"] = None
        errors, _ = project.validate_record(record)
        self.assertTrue(any("execution.observed_at" in error for error in errors))

    def handoff(self):
        return {
            "direction": "nomia_to_mago",
            "source": "roadmap.yaml",
            "observed_at": "2026-07-20T12:00:00+00:00",
            "provenance": "decision-1",
            "freshness_days": 30,
            "payload": {
                "feature_key": "demo-feature",
                "outcome": "Outcome",
                "scope_summary": "Scope",
                "owner": "unknown",
                "dependencies": [],
                "readiness": "ready",
                "candidate_spec_id": "spec-2026-07-20-demo-feature",
                "candidate_spec_id_provenance": "registry/spec-2026-07-20-demo-feature.yaml",
            },
        }

    def test_handoff_rejects_malformed_candidate_spec_id(self):
        envelope = self.handoff()
        envelope["payload"]["candidate_spec_id"] = "not-a-canonical-spec-id"
        self.assertEqual(evaluate.validate_handoff(envelope, AS_OF)["status"], "rejected")

    def test_handoff_rejects_legacy_ulid_candidate_spec_id(self):
        envelope = self.handoff()
        envelope["payload"]["candidate_spec_id"] = "spec-2026-07-20-demo-feature--" + "01arz3ndektsv4rrffq69g5fav"
        self.assertEqual(evaluate.validate_handoff(envelope, AS_OF)["status"], "rejected")

    def test_handoff_rejects_feature_key_mismatch(self):
        envelope = self.handoff()
        envelope["payload"]["candidate_spec_id"] = "spec-2026-07-20-other-feature"
        result = evaluate.validate_handoff(envelope, AS_OF)
        self.assertEqual(result["status"], "rejected")
        self.assertTrue(any("does not match" in reason for reason in result["reasons"]))

    def test_handoff_rejects_technical_content(self):
        envelope = self.handoff()
        envelope["payload"]["tasks"] = ["Implement database migration"]
        result = evaluate.validate_handoff(envelope, AS_OF)
        self.assertEqual(result["status"], "rejected")
        self.assertTrue(any("outside nomia authority" in reason for reason in result["reasons"]))

    def test_mago_handoff_rejects_invalid_planning_state(self):
        envelope = {
            "direction": "mago_to_nomia",
            "source": "mago/spec",
            "observed_at": "2026-07-20T12:00:00+00:00",
            "provenance": "mago-evidence",
            "freshness_days": 30,
            "payload": {
                "spec_id": "spec-2026-07-20-demo-feature",
                "planning_state": "passed",
                "planning_evidence": "spec/validation.md",
            },
        }
        self.assertEqual(evaluate.validate_handoff(envelope, AS_OF)["status"], "rejected")


if __name__ == "__main__":
    unittest.main()
