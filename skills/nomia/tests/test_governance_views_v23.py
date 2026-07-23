import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("project_governance_views_v23", ROOT / "scripts" / "project_governance_views.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class GovernanceViewV23Tests(unittest.TestCase):
    def record(self):
        return {
            "privacy": {"classification":"internal","contains_personal_data":False,"contains_third_party_data":False,"contains_confidential_data":False,"contains_secrets":False,"redactions_applied":[],"redaction_method":"none","intended_audience":["governance"],"allowed_destinations":["local"],"purpose":"test","retention_days":0,"external_share_allowed":False,"source_handoff_id":None,"source_reference":"fixture://test","transformations":["synthetic"]},
            "spec_id": "spec-2026-07-21-governance-view",
            "request": {"title": "Governance view", "requester": "Ops", "context": "Need a decision"},
            "ownership": {"owner": "Delivery", "stakeholders": ["Risk"], "decision_maker": "Sponsor"},
            "planning": {"target_date": "2026-08-01"},
            "business_priority": {"level": "high", "impact": "high"},
            "status": {"state": "planned", "summary": "Awaiting decision", "updated_at": "2026-07-21", "confidence": "medium"},
            "blockers": [],
            "risks": [{"summary": "Policy deadline"}],
            "links": {"external": []},
            "governance": {"profile": "governed", "lifecycle": "decide", "status": "planned"},
            "technical_state": {
                "planning": {"state": "not_started", "source": "mago/pending", "observed_at": "2026-07-21"},
                "execution": {"state": "unknown", "source": None, "observed_at": None},
                "validation": {"state": "unknown", "source": None, "observed_at": None},
            },
            "release": {"state": "unknown", "released_at": None, "evidence": []},
            "dependencies": [],
            "decision": {"state": "pending", "current": "Approve governed intake", "evidence": ["decision-request-1"]},
            "handoffs": {"mago": {"state": "draft"}, "magia": {"state": "unknown"}},
            "provenance": {"updated_at": "2026-07-21T10:00:00+00:00", "facts": {}, "changes": []},
        }

    def test_lifecycle_status_keeps_authorities_separate(self):
        views = mod.build_views(self.record(), "ops.yaml", "2026-07-21T12:00:00+00:00")
        status = views["lifecycle_status"]
        self.assertEqual(status["state_authority"]["planning"], "mago")
        self.assertEqual(status["state_authority"]["validation"], "magia")
        self.assertEqual(status["technical_certification"], "not_provided_by_nomia")
        self.assertEqual(status["next_responsible_skill"], "nomia")

    def test_decision_ready_brief_does_not_manufacture_recommendation(self):
        views = mod.build_views(self.record(), "ops.yaml", "2026-07-21T12:00:00+00:00")
        brief = views["decision_ready_brief"]
        self.assertEqual(brief["decision_required"], "Approve governed intake")
        self.assertEqual(brief["authority_required"], "Sponsor")
        self.assertIn("does not manufacture", brief["note"])

    def test_external_partner_view_excludes_audit_and_technical_detail(self):
        views = mod.build_views(self.record(), "ops.yaml", "2026-07-21T12:00:00+00:00")
        external = views["audience_views"]["external_partner"]
        self.assertEqual(external["status"], "blocked")
        self.assertIn("not allowed", external["reason"])
        self.assertNotIn("request", external)

    def test_engineering_view_keeps_boundary_visible(self):
        views = mod.build_views(self.record(), "ops.yaml", "2026-07-21T12:00:00+00:00")
        engineering = views["audience_views"]["engineering"]
        self.assertIn("Mago", engineering["boundary"])
        self.assertIn("Magia", engineering["boundary"])


if __name__ == "__main__":
    unittest.main()
