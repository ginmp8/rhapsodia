import importlib.util, json, tempfile, unittest
from datetime import date, datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("project_governance_views", ROOT/"scripts"/"project_governance_views.py")
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

class ProjectionTests(unittest.TestCase):
    def record(self):
        return {"privacy":{"classification":"internal","contains_personal_data":False,"contains_third_party_data":False,"contains_confidential_data":False,"contains_secrets":False,"redactions_applied":[],"redaction_method":"none","intended_audience":["governance"],"allowed_destinations":["local"],"purpose":"test","retention_days":0,"external_share_allowed":False,"source_handoff_id":None,"source_reference":"fixture://test","transformations":["synthetic"]},"spec_id":"spec-2026-07-20-demo","request":{"title":"Demo","requester":None,"context":"Outcome"},"ownership":{"owner":"Ana","stakeholders":["Ops"]},"planning":{"target_date":"2026-08-01"},"business_priority":{"level":"high","impact":"high"},"status":{"state":"in_progress","summary":"Building","updated_at":"2026-07-20","confidence":"medium"},"blockers":[],"risks":[],"links":{"external":[]},"governance":{"profile":"standard","lifecycle":"track","status":"in_progress"},"technical_state":{"planning":{"state":"ready","source":"mago/spec","observed_at":"2026-07-20"},"execution":{"state":"in_progress","source":"magia/notes","observed_at":"2026-07-20"},"validation":{"state":"unknown","source":None,"observed_at":None}},"release":{"state":"unknown","released_at":None,"evidence":[]},"dependencies":[],"decision":{"state":"unknown","current":None,"evidence":[]},"provenance":{"facts":{},"changes":[]}}
    def test_no_unsupported_completion_claim(self):
        views=mod.build_views(self.record(),"ops.yaml","2026-07-20T12:00:00+00:00")
        self.assertFalse(views["executive_summary"]["completion_claim_supported"])
        self.assertEqual(views["executive_summary"]["release_state"],"unknown")
    def test_unknowns_are_visible(self):
        views=mod.build_views(self.record(),"ops.yaml","2026-07-20T12:00:00+00:00")
        self.assertIn("request.requester", views["audit_record"]["unknown_fields"])
        self.assertIn("unknown=", views["one_line"])
    def test_adapter_is_non_authoritative_and_lossy(self):
        r=self.record(); v=mod.build_views(r,"ops.yaml","2026-07-20T12:00:00+00:00")
        a=mod.adapter("openspec_reference",r,v,"ops.yaml","2026-07-20T12:00:00+00:00")
        self.assertEqual(a["authority"],"non_authoritative_projection")
        self.assertTrue(a["lossy_fields"])

    def test_all_adapters_return_json_safe_values_for_yaml_dates(self):
        r=self.record()
        r["planning"]["target_date"]=date(2026,8,1)
        r["status"]["updated_at"]=date(2026,7,20)
        r["provenance"]["updated_at"]=datetime(2026,7,20,12,0,tzinfo=timezone.utc)
        views=mod.build_views(r,"ops.yaml","2026-07-20T12:00:00+00:00")
        names=["lightweight_proposal","roadmap_item","status_report","decision_log","release_note_input","spec_kit_reference","openspec_reference","kiro_reference"]
        for name in names:
            with self.subTest(adapter=name):
                payload=mod.adapter(name,r,views,"ops.yaml","2026-07-20T12:00:00+00:00")
                json.dumps(payload,sort_keys=True)

    def test_non_unknown_technical_state_requires_source(self):
        r=self.record(); r["technical_state"]["execution"]["source"]=None
        errors,_=mod.validate_record(r)
        self.assertTrue(any("execution.source" in e for e in errors))
if __name__=="__main__": unittest.main()
