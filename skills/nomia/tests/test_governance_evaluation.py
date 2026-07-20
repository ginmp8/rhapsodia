import importlib.util, unittest
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("evaluate_governance", ROOT/"scripts"/"evaluate_governance.py")
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
ASOF=datetime(2026,7,20,tzinfo=timezone.utc)
class EvaluationTests(unittest.TestCase):
    def base(self):
        return {"request":{"requester":"A"},"ownership":{"owner":"B"},"planning":{"target_date":"2026-07-25"},"status":{"state":"blocked","updated_at":"2026-07-19"},"governance":{"status":"blocked"},"risks":[{"severity":"high"}],"dependencies":[{"id":"dep","status":"blocked","severity":"high"}],"timestamps":{"intake_at":"2026-07-01","state_entered_at":"2026-07-10","blocked_since":"2026-07-15","decision_requested_at":"2026-07-11","decision_at":"2026-07-13"},"risk_history":[{"date":"2026-07-01","severity":"medium"},{"date":"2026-07-19","severity":"high"}],"provenance":{"facts":{}}}
    def test_transition_contract(self):
        self.assertEqual(mod.validate_transition("ready","in_progress")["status"],"accepted")
        self.assertEqual(mod.validate_transition("closed","in_progress")["status"],"rejected")
    def test_metrics_do_not_invent_missing_times(self):
        m=mod.compute_metrics(self.base(),ASOF)
        self.assertEqual(m["blocked_duration_days"]["value"],5.0)
        self.assertIsNone(m["execution_lead_time_days"]["value"])
        self.assertTrue(m["execution_lead_time_days"]["missing_evidence"])
        self.assertEqual(m["risk_trend"]["value"],"increasing")
    def test_confidence_is_evidence_based(self):
        c=mod.confidence(self.base())
        self.assertEqual(c["value"],"low")
        self.assertIn("blocked",c["evidence"])
    def test_handoff_requires_provenance(self):
        env={"direction":"nomia_to_mago","source":"roadmap.yaml","observed_at":"2026-07-20","provenance":"decision-1","freshness_days":30,"payload":{"feature_key":"f","outcome":"o","scope_summary":"s","owner":"unknown","dependencies":[],"readiness":"ready","candidate_spec_id":"spec-2026-07-20-f"}}
        self.assertEqual(mod.validate_handoff(env,ASOF)["status"],"rejected")
        env["payload"]["candidate_spec_id_provenance"]="registry"
        self.assertEqual(mod.validate_handoff(env,ASOF)["status"],"accepted")
if __name__=="__main__": unittest.main()
