from __future__ import annotations

import copy
import json
import subprocess
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
WORKFLOW = handoff.workflow_id_for("synthetic-demo-feature")
PRIVACY = {
    "classification": "internal",
    "contains_personal_data": False,
    "contains_third_party_data": False,
    "contains_confidential_data": False,
    "contains_secrets": False,
    "redactions_applied": [],
    "redaction_method": "none",
    "intended_audience": ["sdd-maintainers"],
    "allowed_destinations": ["local", "internal"],
    "purpose": "synthetic contract validation",
    "retention_days": 30,
    "evidence_ref_visibility": "opaque",
    "external_share_allowed": False,
}
PAYLOADS = {
 "nomia_to_mago":{"feature_key":"demo-feature","outcome":"Governed capability","scope_summary":"Bounded scope","owner":"delivery-role","business_priority":{"level":"high","owner":"nomia","source":"fixture://governance","observed_at":NOW.isoformat()},"dependencies":[],"governance_readiness":"ready","candidate_spec_id":SPEC,"candidate_spec_id_provenance":"fixture://registry"},
 "mago_to_magia":{"spec_id":SPEC,"planning_state":"ready","planning_evidence":"manifest.yaml","requirement_refs":["REQ-001"],"acceptance_criteria_refs":["AC-001"],"task_ids":["task001"],"validation_refs":["VAL-001"],"technical_criticality":{"level":"high","owner":"mago","rationale":"contract impact"},"execution_sequence":{"rank":10,"lane":"fixed_date","owner":"mago","rationale":["dependency-safe"]},"readiness":"ready"},
 "magia_to_mago":{"spec_id":SPEC,"execution_state":"done","validation_state":"passed","evidence_reference":"validation-evidence.md","deviations":[],"planning_change_required":False},
 "mago_to_nomia":{"spec_id":SPEC,"planning_state":"done","planning_evidence":"manifest.yaml","dependency_summary":{"blocked":[],"unknown":[]},"technical_risk_summary":{"level":"low","residual":[]},"forecast_impact":{"kind":"none","evidence":[]}},
 "magia_to_nomia":{"spec_id":SPEC,"execution_state":"done","validation_state":"passed","evidence_reference":"validation-evidence.md","delivery_impacts":[]},
}

class EcosystemHandoffTests(unittest.TestCase):
 def role(self): return ROOT.name
 def build(self,direction): return handoff.build_envelope(direction=direction,payload=PAYLOADS[direction],source='fixture://source',authority=self.role(),evidence_refs=['fixture://evidence'],observed_at=NOW.isoformat(),freshness_days=30,workflow_id=WORKFLOW,privacy_handling=PRIVACY,root=ROOT)
 def peer_envelope(self,direction):
  contract=handoff.load_contract(ROOT); compatibility=handoff.load_compatibility(ROOT); item=contract['directions'][direction]
  envelope={'schema_version':contract['schema_version'],'ecosystem_release':compatibility['ecosystem_release'],'direction':direction,'source_skill':item['producer'],'source_version':compatibility['packages'][item['producer']],'target_skill':item['consumer'],'workflow_id':WORKFLOW,'observed_at':NOW.isoformat(),'privacy_handling':copy.deepcopy(PRIVACY),'provenance':{'source':'fixture://peer','authority':item['producer'],'evidence_refs':['fixture://evidence']},'freshness':{'max_age_days':30},'payload':handoff.apply_state_projection(direction,copy.deepcopy(PAYLOADS[direction]),contract),'unknowns':[],'conflicts':[]}
  envelope['handoff_id']=handoff.handoff_id_for(envelope); return envelope
 def validate(self,env,role=None,operation='consume'): return handoff.validate_envelope(env,as_of=NOW,role=role or self.role(),operation=operation,root=ROOT)
 def test_contract_is_valid(self): self.assertEqual(handoff.contract_errors(handoff.load_contract(ROOT),ROOT),[])
 def test_role_builds_owned_directions(self):
  contract=handoff.load_contract(ROOT)
  for direction in contract['roles'][self.role()]['produces']:
   with self.subTest(direction=direction): self.assertEqual(self.validate(self.build(direction),operation='produce')['status'],'accepted')
 def test_role_cannot_build_foreign_direction(self):
  contract=handoff.load_contract(ROOT); foreign=next(k for k,v in contract['directions'].items() if v['producer']!=self.role())
  with self.assertRaises(ValueError): self.build(foreign)
 def test_consumer_accepts_peer_envelope(self):
  contract=handoff.load_contract(ROOT)
  for direction in contract['roles'][self.role()]['consumes']:
   with self.subTest(direction=direction): self.assertEqual(self.validate(self.peer_envelope(direction))['status'],'accepted')
 def test_state_mapping_is_explicit(self):
  contract=handoff.load_contract(ROOT); m=handoff.apply_state_projection('mago_to_nomia',PAYLOADS['mago_to_nomia'],contract); x=handoff.apply_state_projection('magia_to_nomia',PAYLOADS['magia_to_nomia'],contract)
  self.assertEqual((m['nomia_planning_state'],m['mapping_version']),('complete','2.0.0')); self.assertEqual((x['nomia_execution_state'],x['nomia_validation_state']),('complete','passed'))
 def test_future_timestamp_is_rejected(self):
  env=self.peer_envelope(handoff.load_contract(ROOT)['roles'][self.role()]['consumes'][0]); env['observed_at']=(NOW+timedelta(minutes=10)).isoformat(); env['handoff_id']=handoff.handoff_id_for(env)
  result=self.validate(env); self.assertEqual(result['status'],'rejected'); self.assertIn('HANDOFF_FUTURE_OBSERVED_AT',result['reason_codes'])
 def test_empty_evidence_refs_are_rejected(self):
  env=self.peer_envelope(handoff.load_contract(ROOT)['roles'][self.role()]['consumes'][0]); env['provenance']['evidence_refs']=[]; env['handoff_id']=handoff.handoff_id_for(env)
  result=self.validate(env); self.assertEqual(result['status'],'rejected'); self.assertIn('HANDOFF_EMPTY_EVIDENCE_REFS',result['reason_codes'])
 def test_undeclared_payload_field_is_rejected(self):
  env=self.peer_envelope(handoff.load_contract(ROOT)['roles'][self.role()]['consumes'][0]); env['payload']['solution_outline']={}; env['handoff_id']=handoff.handoff_id_for(env)
  result=self.validate(env); self.assertEqual(result['status'],'rejected'); self.assertIn('HANDOFF_UNKNOWN_PAYLOAD_FIELD',result['reason_codes'])
 def test_generic_priority_is_rejected_recursively(self):
  env=self.peer_envelope('nomia_to_mago'); env['payload']['nested']={'priority':'urgent'}; env['handoff_id']=handoff.handoff_id_for(env)
  result=self.validate(env,role='mago'); self.assertEqual(result['status'],'rejected'); self.assertIn('HANDOFF_OUTSIDE_AUTHORITY',result['reason_codes'])
 def test_tampered_projection_and_handoff_id_are_rejected(self):
  env=self.peer_envelope('mago_to_nomia'); env['payload']['nomia_planning_state']='ready'
  result=handoff.validate_envelope(env,as_of=NOW,role='nomia',operation='consume',root=ROOT)
  self.assertEqual(result['status'],'rejected'); self.assertTrue(any('projection' in r or 'handoff_id' in r for r in result['reasons']))
 def test_stale_and_conflicting_evidence_do_not_pass(self):
  direction=handoff.load_contract(ROOT)['roles'][self.role()]['consumes'][0]; env=self.peer_envelope(direction); env['observed_at']=(NOW-timedelta(days=10)).isoformat(); env['freshness']={'max_age_days':1}; env['handoff_id']=handoff.handoff_id_for(env)
  self.assertEqual(self.validate(env)['status'],'stale')
  env=self.peer_envelope(direction); env['conflicts']=['sources disagree']; env['handoff_id']=handoff.handoff_id_for(env)
  result=self.validate(env); self.assertEqual(result['status'],'conflicting'); self.assertIn('HANDOFF_CONFLICTING',result['reason_codes'])
 def test_missing_privacy_metadata_is_rejected(self):
  env=self.peer_envelope(handoff.load_contract(ROOT)['roles'][self.role()]['consumes'][0]); del env['privacy_handling']; env['handoff_id']=handoff.handoff_id_for(env)
  result=self.validate(env); self.assertEqual(result['status'],'rejected'); self.assertIn('HANDOFF_MISSING_FIELD',result['reason_codes'])
 def test_secret_transport_is_rejected(self):
  env=self.peer_envelope(handoff.load_contract(ROOT)['roles'][self.role()]['consumes'][0]); env['privacy_handling']['contains_secrets']=True; env['handoff_id']=handoff.handoff_id_for(env)
  result=self.validate(env); self.assertEqual(result['status'],'rejected'); self.assertIn('HANDOFF_SECRET_EXPOSURE',result['reason_codes'])
 def test_workflow_lineage_is_required(self):
  env=self.peer_envelope(handoff.load_contract(ROOT)['roles'][self.role()]['consumes'][0]); env['workflow_id']='workflow-invalid'; env['handoff_id']=handoff.handoff_id_for(env)
  result=self.validate(env); self.assertEqual(result['status'],'rejected'); self.assertIn('HANDOFF_INVALID_WORKFLOW_ID',result['reason_codes'])
 def test_contract_v2_is_rejected(self):
  env=self.peer_envelope(handoff.load_contract(ROOT)['roles'][self.role()]['consumes'][0]); env['schema_version']='2.0.0'; env['handoff_id']=handoff.handoff_id_for(env)
  result=self.validate(env); self.assertEqual(result['status'],'rejected'); self.assertIn('HANDOFF_INVALID_SCHEMA',result['reason_codes'])
 def test_exit_code_matrix(self):
  expected={'accepted':0,'error':2,'draft':3,'stale':4,'conflicting':5,'rejected':6}
  for status,code in expected.items(): self.assertEqual(handoff.validation_exit_code(status),code)
  self.assertEqual(handoff.validation_exit_code('draft',allow_draft=True),0)
 def test_draft_consume_requires_explicit_allow(self):
  env=self.peer_envelope('nomia_to_mago'); env['payload']['governance_readiness']='draft'; env['handoff_id']=handoff.handoff_id_for(env)
  with tempfile.TemporaryDirectory() as tmp:
   source=Path(tmp)/'draft.json'; source.write_text(json.dumps(env),encoding='utf-8')
   base=[sys.executable,'-B',str(ROOT/'scripts/ecosystem_handoff.py'),'validate','--input',str(source),'--operation','consume','--as-of',NOW.isoformat()]
   if self.role()=='mago':
    blocked=subprocess.run(base,text=True,capture_output=True,check=False); self.assertEqual(blocked.returncode,3,blocked.stdout+blocked.stderr)
    inspected=subprocess.run(base+['--allow-draft'],text=True,capture_output=True,check=False); self.assertEqual(inspected.returncode,0,inspected.stdout+inspected.stderr)
 def test_mixed_source_version_is_rejected(self):
  direction=handoff.load_contract(ROOT)['roles'][self.role()]['consumes'][0]; env=self.peer_envelope(direction); env['source_version']='1.5.0'; env['handoff_id']=handoff.handoff_id_for(env)
  self.assertEqual(self.validate(env)['status'],'rejected')

 def test_content_privacy_and_rank_semantics(self):
  env=self.peer_envelope('magia_to_mago'); env['unknowns']=['Contact person@internal.invalid']; env['handoff_id']=handoff.handoff_id_for(env); result=handoff.validate_envelope(env,as_of=NOW,operation='any',root=ROOT); self.assertIn('HANDOFF_PRIVACY_CONTRADICTION_PERSONAL',result['reason_codes']); self.assertNotIn('person@',json.dumps(result))
  env=self.peer_envelope('magia_to_mago'); env['provenance']['evidence_refs']=['/home/example/private.log']; env['handoff_id']=handoff.handoff_id_for(env); result=handoff.validate_envelope(env,as_of=NOW,operation='any',root=ROOT); self.assertIn('HANDOFF_PRIVATE_REFERENCE_EXPOSURE',result['reason_codes']); self.assertNotIn('/home/example',json.dumps(result))
  secret='token=' + ''.join(('abcd','efgh','ijkl','mnop','qrs')); env=self.peer_envelope('magia_to_mago'); env['unknowns']=[secret]; env['handoff_id']=handoff.handoff_id_for(env); result=handoff.validate_envelope(env,as_of=NOW,operation='any',root=ROOT); self.assertIn('HANDOFF_SECRET_EXPOSURE',result['reason_codes']); self.assertNotIn(secret[6:18],json.dumps(result))
  env=self.peer_envelope('mago_to_magia'); env['payload']['readiness']='draft'; env['payload']['execution_sequence']['rank']=None; env['handoff_id']=handoff.handoff_id_for(env); self.assertEqual(handoff.validate_envelope(env,as_of=NOW,operation='any',root=ROOT)['status'],'draft'); env['payload']['readiness']='ready'; env['handoff_id']=handoff.handoff_id_for(env); self.assertEqual(handoff.validate_envelope(env,as_of=NOW,operation='any',root=ROOT)['status'],'rejected')
 def test_artifact_privacy_lineage(self):
  import validate_artifact_privacy as ap
  env=self.peer_envelope('magia_to_mago'); block=ap.derive(env); self.assertEqual(block['source_handoff_id'],env['handoff_id']); self.assertEqual(ap.validate_block(block,ROOT),[]); block['allowed_destinations']=['public']; self.assertIn('privacy external destination denied',ap.validate_block(block,ROOT)); block=ap.derive(env); block['contains_personal_data']=True; self.assertIn('privacy sensitive content requires redaction',ap.validate_block(block,ROOT))

if __name__=='__main__': unittest.main()
