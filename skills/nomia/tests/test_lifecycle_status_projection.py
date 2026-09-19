from __future__ import annotations
import copy,sys,unittest
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'scripts'))
import ecosystem_handoff as h, handoff_ledger as ledger, project_lifecycle_status as projection
NOW=datetime(2026,7,22,12,0,tzinfo=timezone.utc); WORKFLOW=h.workflow_id_for('synthetic-projection')
PRIVACY={'classification':'internal','contains_personal_data':False,'contains_third_party_data':False,'contains_confidential_data':False,'contains_secrets':False,'redactions_applied':[],'redaction_method':'none','intended_audience':['governance-role'],'allowed_destinations':['local'],'purpose':'synthetic projection','retention_days':30,'evidence_ref_visibility':'opaque','external_share_allowed':False}
def peer():
 c=h.load_contract(ROOT); compat=h.load_compatibility(ROOT); d=c['directions']['mago_to_nomia']; payload={'spec_id':'spec-2026-07-22-projection','planning_state':'ready','planning_evidence':'fixture://manifest','dependency_summary':{'blocked':[]},'technical_risk_summary':{'level':'low'},'forecast_impact':{'kind':'none'}}; payload=h.apply_state_projection('mago_to_nomia',payload,c)
 env={'schema_version':c['schema_version'],'ecosystem_release':compat['ecosystem_release'],'direction':'mago_to_nomia','source_skill':'mago','source_version':compat['packages']['mago'],'target_skill':'nomia','workflow_id':WORKFLOW,'observed_at':NOW.isoformat(),'privacy_handling':copy.deepcopy(PRIVACY),'provenance':{'source':'fixture://source','authority':'mago','evidence_refs':['opaque://evidence/1']},'freshness':{'max_age_days':30},'payload':payload,'unknowns':[],'conflicts':[]}; env['handoff_id']=h.handoff_id_for(env); return env
class ProjectionTests(unittest.TestCase):
 def test_projection_is_read_only_and_minimized(self):
  env=peer(); data=ledger.empty_ledger(WORKFLOW); data,_=ledger.record(data,env,'created',NOW.isoformat()); data,_=ledger.record(data,env,'accepted',NOW.isoformat())
  out=projection.project([env],data); self.assertEqual(out['authority'],'non_authoritative_projection'); self.assertEqual(out['current_owner'],'nomia'); self.assertEqual(out['pending_handoff'],env['handoff_id']); self.assertNotIn('opaque://evidence/1',str(out))
 def test_mixed_workflow_rejected(self):
  a=peer(); b=peer(); b['workflow_id']=h.workflow_id_for('other'); b['handoff_id']=h.handoff_id_for(b)
  with self.assertRaises(ValueError): projection.project([a,b])
if __name__=='__main__': unittest.main()
