import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import ecosystem_handoff as handoff

NOW = datetime(2026, 7, 22, 12, 0, tzinfo=timezone.utc)
SPEC = "spec-2026-07-22-demo-feature"

PAYLOADS = {
    "nomia_to_mago": {
        "feature_key": "demo-feature",
        "outcome": "Deliver a governed capability",
        "scope_summary": "Bounded business scope",
        "owner": "delivery-owner",
        "business_priority": "high",
        "dependencies": [],
        "governance_readiness": "ready",
        "candidate_spec_id": SPEC,
        "candidate_spec_id_provenance": "registry/demo-feature",
    },
    "mago_to_magia": {
        "spec_id": SPEC,
        "planning_state": "ready",
        "planning_evidence": "manifest.yaml",
        "requirement_refs": ["REQ-001"],
        "acceptance_criteria_refs": ["AC-001"],
        "task_ids": ["task001"],
        "validation_refs": ["VAL-001"],
        "technical_criticality": "high",
        "execution_sequence": {"rank": 10, "rationale": ["dependency-safe"]},
        "readiness": "ready",
    },
    "magia_to_mago": {
        "spec_id": SPEC,
        "execution_state": "done",
        "validation_state": "passed",
        "evidence_reference": "validation-evidence.md",
        "deviations": [],
        "planning_change_required": False,
    },
    "mago_to_nomia": {
        "spec_id": SPEC,
        "planning_state": "done",
        "planning_evidence": "manifest.yaml",
        "dependency_summary": {"blocked": [], "unknown": []},
        "technical_risk_summary": {"level": "low", "residual": []},
        "forecast_impact": {"kind": "none", "evidence": []},
    },
    "magia_to_nomia": {
        "spec_id": SPEC,
        "execution_state": "done",
        "validation_state": "passed",
        "evidence_reference": "validation-evidence.md",
        "delivery_impacts": [],
    },
    "nomia_to_stakeholder": {
        "audience": "delivery-leadership",
        "summary": "Current governed status",
        "unknowns": [],
        "decision_needed": "none",
        "evidence_references": ["governance-evidence.yaml"],
    },
}


class EcosystemHandoffTests(unittest.TestCase):
    def role(self):
        return ROOT.name

    def build(self, direction):
        return handoff.build_envelope(
            direction=direction,
            payload=PAYLOADS[direction],
            source="source-artifact",
            authority=self.role(),
            evidence_refs=["evidence-1"],
            observed_at=NOW.isoformat(),
            freshness_days=30,
            root=ROOT,
        )

    def test_contract_is_valid(self):
        self.assertEqual(handoff.contract_errors(handoff.load_contract(ROOT)), [])

    def test_role_can_build_every_owned_direction(self):
        contract = handoff.load_contract(ROOT)
        for direction in contract["roles"][self.role()]["produces"]:
            with self.subTest(direction=direction):
                envelope = self.build(direction)
                result = handoff.validate_envelope(
                    envelope,
                    as_of=NOW,
                    role=self.role(),
                    operation="produce",
                    root=ROOT,
                )
                self.assertEqual(result["status"], "accepted", result)
                self.assertEqual(envelope["source_skill"], self.role())

    def test_role_cannot_build_foreign_direction(self):
        contract = handoff.load_contract(ROOT)
        foreign = next(
            direction
            for direction, item in contract["directions"].items()
            if item["producer"] != self.role()
        )
        with self.assertRaises(ValueError):
            self.build(foreign)

    def test_consumer_accepts_peer_envelope(self):
        contract = handoff.load_contract(ROOT)
        incoming = contract["roles"][self.role()]["consumes"]
        if not incoming:
            self.skipTest("role has no incoming directions")
        direction = incoming[0]
        producer = contract["directions"][direction]["producer"]
        envelope = {
            "schema_version": contract["schema_version"],
            "direction": direction,
            "source_skill": producer,
            "source_version": "1.0.0",
            "target_skill": self.role(),
            "observed_at": NOW.isoformat(),
            "provenance": {"source": "peer-artifact", "authority": producer, "evidence_refs": ["evidence"]},
            "freshness": {"max_age_days": 30},
            "payload": handoff.apply_state_projection(direction, PAYLOADS[direction], contract),
            "unknowns": [],
            "conflicts": [],
        }
        result = handoff.validate_envelope(
            envelope,
            as_of=NOW,
            role=self.role(),
            operation="consume",
            root=ROOT,
        )
        self.assertEqual(result["status"], "accepted", result)

    def test_state_mapping_is_explicit(self):
        contract = handoff.load_contract(ROOT)
        mago = handoff.apply_state_projection("mago_to_nomia", PAYLOADS["mago_to_nomia"], contract)
        magia = handoff.apply_state_projection("magia_to_nomia", PAYLOADS["magia_to_nomia"], contract)
        self.assertEqual(mago["nomia_planning_state"], "complete")
        self.assertEqual(mago["mapping_version"], "1.0.0")
        self.assertEqual(magia["nomia_execution_state"], "complete")
        self.assertEqual(magia["nomia_validation_state"], "passed")

    def test_tampered_projection_is_rejected(self):
        contract = handoff.load_contract(ROOT)
        direction = "mago_to_nomia"
        payload = handoff.apply_state_projection(direction, PAYLOADS[direction], contract)
        payload["nomia_planning_state"] = "ready"
        envelope = {
            "schema_version": contract["schema_version"],
            "direction": direction,
            "source_skill": "mago",
            "source_version": "3.1.0",
            "target_skill": "nomia",
            "observed_at": NOW.isoformat(),
            "provenance": {"source": "manifest.yaml", "authority": "mago", "evidence_refs": ["validation.md"]},
            "freshness": {"max_age_days": 30},
            "payload": payload,
            "unknowns": [],
            "conflicts": [],
        }
        result = handoff.validate_envelope(envelope, as_of=NOW, role="nomia", operation="consume", root=ROOT)
        self.assertEqual(result["status"], "rejected")
        self.assertTrue(any("projection" in reason for reason in result["reasons"]))

    def test_forbidden_authority_content_is_rejected(self):
        contract = handoff.load_contract(ROOT)
        direction = "nomia_to_mago"
        payload = dict(PAYLOADS[direction])
        payload["tasks"] = ["implement database"]
        envelope = {
            "schema_version": contract["schema_version"],
            "direction": direction,
            "source_skill": "nomia",
            "source_version": "3.1.0",
            "target_skill": "mago",
            "observed_at": NOW.isoformat(),
            "provenance": {"source": "governance-evidence.yaml", "authority": "nomia", "evidence_refs": ["decision"]},
            "freshness": {"max_age_days": 30},
            "payload": payload,
            "unknowns": [],
            "conflicts": [],
        }
        result = handoff.validate_envelope(envelope, as_of=NOW, role="mago", operation="consume", root=ROOT)
        self.assertEqual(result["status"], "rejected")
        self.assertTrue(any("outside nomia authority" in reason for reason in result["reasons"]))

    def test_stale_and_conflicting_evidence_do_not_pass(self):
        contract = handoff.load_contract(ROOT)
        direction = next(iter(contract["directions"]))
        item = contract["directions"][direction]
        envelope = {
            "schema_version": contract["schema_version"],
            "direction": direction,
            "source_skill": item["producer"],
            "source_version": "1.0.0",
            "target_skill": item["consumer"],
            "observed_at": (NOW - timedelta(days=10)).isoformat(),
            "provenance": {"source": "source", "authority": item["producer"], "evidence_refs": ["evidence"]},
            "freshness": {"max_age_days": 1},
            "payload": handoff.apply_state_projection(direction, PAYLOADS[direction], contract),
            "unknowns": [],
            "conflicts": [],
        }
        stale = handoff.validate_envelope(envelope, as_of=NOW, role=item["consumer"], operation="consume", root=ROOT)
        self.assertEqual(stale["status"], "stale")
        envelope["observed_at"] = NOW.isoformat()
        envelope["conflicts"] = ["two sources disagree"]
        conflicting = handoff.validate_envelope(envelope, as_of=NOW, role=item["consumer"], operation="consume", root=ROOT)
        self.assertEqual(conflicting["status"], "conflicting")

    def test_legacy_nomia_envelope_requires_explicit_compatibility(self):
        legacy = {
            "direction": "nomia_to_mago",
            "source": "governance-evidence.yaml",
            "observed_at": NOW.isoformat(),
            "provenance": "decision-1",
            "freshness_days": 30,
            "payload": {
                "feature_key": "demo-feature",
                "outcome": "Outcome",
                "scope_summary": "Scope",
                "owner": "owner",
                "dependencies": [],
                "readiness": "ready",
            },
        }
        strict = handoff.validate_envelope(legacy, as_of=NOW, role="mago", operation="consume", root=ROOT)
        compatible = handoff.validate_envelope(
            legacy,
            as_of=NOW,
            role="mago",
            operation="consume",
            allow_legacy=True,
            root=ROOT,
        )
        self.assertEqual(strict["status"], "rejected")
        self.assertEqual(compatible["status"], "accepted")
        self.assertTrue(compatible["warnings"])

    def test_cli_round_trip_for_owned_direction(self):
        contract = handoff.load_contract(ROOT)
        direction = contract["roles"][self.role()]["produces"][0]
        with tempfile.TemporaryDirectory() as tmp:
            payload_path = Path(tmp) / "payload.json"
            output_path = Path(tmp) / "handoff.json"
            payload_path.write_text(json.dumps(PAYLOADS[direction]), encoding="utf-8")
            envelope = self.build(direction)
            handoff.atomic_write_text(output_path, json.dumps(envelope))
            loaded = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(loaded["direction"], direction)
            self.assertTrue(loaded["handoff_id"].startswith("handoff-"))


if __name__ == "__main__":
    unittest.main()
