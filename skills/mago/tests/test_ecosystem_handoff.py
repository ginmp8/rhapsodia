import copy
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import ecosystem_handoff as handoff

NOW = datetime(2026, 7, 22, 12, 0, tzinfo=timezone.utc)
SPEC = "spec-2026-07-22-demo-feature"
PAYLOADS = {
 "nomia_to_mago":{"feature_key":"demo-feature","outcome":"Governed capability","scope_summary":"Bounded scope","owner":"delivery-owner","business_priority":{"level":"high","owner":"nomia","source":"fixture://governance","observed_at":NOW.isoformat()},"dependencies":[],"governance_readiness":"ready","candidate_spec_id":SPEC,"candidate_spec_id_provenance":"fixture://registry"},
 "mago_to_magia":{"spec_id":SPEC,"planning_state":"ready","planning_evidence":"manifest.yaml","requirement_refs":["REQ-001"],"acceptance_criteria_refs":["AC-001"],"task_ids":["task001"],"validation_refs":["VAL-001"],"technical_criticality":{"level":"high","owner":"mago","rationale":"contract impact"},"execution_sequence":{"rank":10,"lane":"fixed_date","owner":"mago","rationale":["dependency-safe"]},"readiness":"ready"},
 "magia_to_mago":{"spec_id":SPEC,"execution_state":"done","validation_state":"passed","evidence_reference":"validation-evidence.md","deviations":[],"planning_change_required":False},
 "mago_to_nomia":{"spec_id":SPEC,"planning_state":"done","planning_evidence":"manifest.yaml","dependency_summary":{"blocked":[],"unknown":[]},"technical_risk_summary":{"level":"low","residual":[]},"forecast_impact":{"kind":"none","evidence":[]}},
 "magia_to_nomia":{"spec_id":SPEC,"execution_state":"done","validation_state":"passed","evidence_reference":"validation-evidence.md","delivery_impacts":[]},
}

class EcosystemHandoffTests(unittest.TestCase):
 def role(self): return ROOT.name
 def build(self,direction): return handoff.build_envelope(direction=direction,payload=PAYLOADS[direction],source='fixture://source',authority=self.role(),evidence_refs=['fixture://evidence'],observed_at=NOW.isoformat(),freshness_days=30,root=ROOT)
 def peer_envelope(self,direction):
  contract=handoff.load_contract(ROOT); compatibility=handoff.load_compatibility(ROOT); item=contract['directions'][direction]
  envelope={'schema_version':contract['schema_version'],'ecosystem_release':compatibility['ecosystem_release'],'direction':direction,'source_skill':item['producer'],'source_version':compatibility['packages'][item['producer']],'target_skill':item['consumer'],'observed_at':NOW.isoformat(),'provenance':{'source':'fixture://peer','authority':item['producer'],'evidence_refs':['fixture://evidence']},'freshness':{'max_age_days':30},'payload':handoff.apply_state_projection(direction,PAYLOADS[direction],contract),'unknowns':[],'conflicts':[]}
  envelope['handoff_id']=handoff.handoff_id_for(envelope); return envelope
 def test_contract_is_valid(self): self.assertEqual(handoff.contract_errors(handoff.load_contract(ROOT),ROOT),[])
 def test_role_builds_owned_directions(self):
  contract=handoff.load_contract(ROOT)
  for direction in contract['roles'][self.role()]['produces']:
   with self.subTest(direction=direction): self.assertEqual(handoff.validate_envelope(self.build(direction),as_of=NOW,role=self.role(),operation='produce',root=ROOT)['status'],'accepted')
 def test_role_cannot_build_foreign_direction(self):
  contract=handoff.load_contract(ROOT); foreign=next(k for k,v in contract['directions'].items() if v['producer']!=self.role())
  with self.assertRaises(ValueError): self.build(foreign)
 def test_consumer_accepts_peer_envelope(self):
  contract=handoff.load_contract(ROOT)
  for direction in contract['roles'][self.role()]['consumes']:
   with self.subTest(direction=direction): self.assertEqual(handoff.validate_envelope(self.peer_envelope(direction),as_of=NOW,role=self.role(),operation='consume',root=ROOT)['status'],'accepted')
 def test_state_mapping_is_explicit(self):
  contract=handoff.load_contract(ROOT); m=handoff.apply_state_projection('mago_to_nomia',PAYLOADS['mago_to_nomia'],contract); x=handoff.apply_state_projection('magia_to_nomia',PAYLOADS['magia_to_nomia'],contract)
  self.assertEqual((m['nomia_planning_state'],m['mapping_version']),('complete','2.0.0')); self.assertEqual((x['nomia_execution_state'],x['nomia_validation_state']),('complete','passed'))
 def test_legacy_envelope_is_rejected_without_compatibility_mode(self):
  legacy={'direction':'nomia_to_mago','source':'old','observed_at':NOW.isoformat(),'freshness_days':30,'payload':{}}
  result=handoff.validate_envelope(legacy,as_of=NOW,role='mago',operation='consume',root=ROOT)
  self.assertEqual(result['status'],'rejected'); self.assertTrue(any('contract v2' in r for r in result['reasons']))
 def test_generic_priority_is_rejected_recursively(self):
  env=self.peer_envelope('nomia_to_mago'); env['payload']['nested']={'priority':'urgent'}; env['handoff_id']=handoff.handoff_id_for(env)
  result=handoff.validate_envelope(env,as_of=NOW,role='mago',operation='consume',root=ROOT)
  self.assertEqual(result['status'],'rejected'); self.assertTrue(any('priority' in r for r in result['reasons']))
 def test_generic_order_hint_is_rejected_recursively(self):
  env=self.peer_envelope('nomia_to_mago'); env['payload']['nested']={'order_hint':1}; env['handoff_id']=handoff.handoff_id_for(env)
  result=handoff.validate_envelope(env,as_of=NOW,role='mago',operation='consume',root=ROOT)
  self.assertEqual(result['status'],'rejected'); self.assertTrue(any('order_hint' in r for r in result['reasons']))
 def test_legacy_envelope_rejects_fake_compatibility_switch(self):
  legacy={'direction':'nomia_to_mago','source':'old','observed_at':NOW.isoformat(),'freshness_days':30,'compatibility_mode':True,'payload':{}}
  result=handoff.validate_envelope(legacy,as_of=NOW,role='mago',operation='consume',root=ROOT)
  self.assertEqual(result['status'],'rejected'); self.assertTrue(any('contract v2' in r for r in result['reasons']))
 def test_tampered_projection_and_handoff_id_are_rejected(self):
  env=self.peer_envelope('mago_to_nomia'); env['payload']['nomia_planning_state']='ready'
  result=handoff.validate_envelope(env,as_of=NOW,role='nomia',operation='consume',root=ROOT)
  self.assertEqual(result['status'],'rejected'); self.assertTrue(any('projection' in r or 'handoff_id' in r for r in result['reasons']))
 def test_stale_and_conflicting_evidence_do_not_pass(self):
  direction=handoff.load_contract(ROOT)['roles'][self.role()]['consumes'][0]; env=self.peer_envelope(direction); env['observed_at']=(NOW-timedelta(days=10)).isoformat(); env['freshness']={'max_age_days':1}; env['handoff_id']=handoff.handoff_id_for(env)
  self.assertEqual(handoff.validate_envelope(env,as_of=NOW,role=self.role(),operation='consume',root=ROOT)['status'],'stale')
  env['observed_at']=NOW.isoformat(); env['conflicts']=['sources disagree']; env['handoff_id']=handoff.handoff_id_for(env)
  self.assertEqual(handoff.validate_envelope(env,as_of=NOW,role=self.role(),operation='consume',root=ROOT)['status'],'conflicting')
 def test_mixed_source_version_is_rejected(self):
  direction=handoff.load_contract(ROOT)['roles'][self.role()]['consumes'][0]; env=self.peer_envelope(direction); env['source_version']='1.5.0'; env['handoff_id']=handoff.handoff_id_for(env)
  self.assertEqual(handoff.validate_envelope(env,as_of=NOW,role=self.role(),operation='consume',root=ROOT)['status'],'rejected')

if __name__=='__main__': unittest.main()
