from __future__ import annotations
import copy,sys,tempfile,unittest
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'scripts'))
import ecosystem_handoff as handoff
import handoff_ledger as ledger
NOW=datetime(2026,7,22,12,0,tzinfo=timezone.utc); WORKFLOW=handoff.workflow_id_for('synthetic-ledger-test')
PRIVACY={'classification':'internal','contains_personal_data':False,'contains_third_party_data':False,'contains_confidential_data':False,'contains_secrets':False,'redactions_applied':[],'redaction_method':'none','intended_audience':['sdd-maintainers'],'allowed_destinations':['local'],'purpose':'synthetic ledger validation','retention_days':30,'evidence_ref_visibility':'opaque','external_share_allowed':False}
PAYLOADS={'nomia':('nomia_to_mago',{'feature_key':'ledger-test','outcome':'test','scope_summary':'synthetic','owner':'delivery-role','business_priority':{'level':'medium','owner':'nomia','source':'fixture://governance','observed_at':NOW.isoformat()},'dependencies':[],'governance_readiness':'ready'}),'mago':('mago_to_magia',{'spec_id':'spec-2026-07-22-ledger-test','planning_state':'ready','planning_evidence':'fixture://manifest','requirement_refs':['REQ-001'],'acceptance_criteria_refs':['AC-001'],'task_ids':['task001'],'validation_refs':['VAL-001'],'technical_criticality':{'level':'normal','owner':'mago','rationale':'fixture'},'execution_sequence':{'rank':1,'lane':'standard','owner':'mago','rationale':['fixture']},'readiness':'ready'}),'magia':('magia_to_mago',{'spec_id':'spec-2026-07-22-ledger-test','execution_state':'done','validation_state':'passed','evidence_reference':'fixture://validation','deviations':[],'planning_change_required':False})}
class LedgerTests(unittest.TestCase):
 def envelope(self):
  direction,payload=PAYLOADS[ROOT.name]
  return handoff.build_envelope(direction=direction,payload=copy.deepcopy(payload),source='fixture://source',authority=ROOT.name,evidence_refs=['fixture://evidence'],observed_at=NOW.isoformat(),freshness_days=30,workflow_id=WORKFLOW,privacy_handling=PRIVACY,root=ROOT)
 def test_lifecycle_and_idempotency(self):
  data=ledger.empty_ledger(WORKFLOW); env=self.envelope()
  data,idem=ledger.record(data,env,'created',NOW.isoformat()); self.assertFalse(idem)
  data,idem=ledger.record(data,env,'created',NOW.isoformat()); self.assertTrue(idem); self.assertEqual(len(data['events']),1)
  for state in ('accepted','consumed','replayed','consumed'):
   data,idem=ledger.record(data,env,state,NOW.isoformat()); self.assertFalse(idem)
  self.assertEqual(ledger.validate(data),[])
 def test_invalid_transition_and_workflow_fail(self):
  data=ledger.empty_ledger(WORKFLOW); env=self.envelope()
  with self.assertRaises(ValueError): ledger.record(data,env,'consumed',NOW.isoformat())
  env['workflow_id']=handoff.workflow_id_for('other'); env['handoff_id']=handoff.handoff_id_for(env)
  with self.assertRaises(ValueError): ledger.record(data,env,'created',NOW.isoformat())
if __name__=='__main__': unittest.main()
