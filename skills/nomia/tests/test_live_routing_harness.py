from __future__ import annotations
import importlib.util,json,tempfile,unittest
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
S=importlib.util.spec_from_file_location('live',ROOT/'scripts/live_routing_harness.py'); assert S and S.loader
m=importlib.util.module_from_spec(S); S.loader.exec_module(m)
class LiveRoutingHarnessTests(unittest.TestCase):
 def roots(self): return {r:ROOT.parent/r for r in m.ROLES}
 def observations(self,req,direct=False):
  rows=[]
  for s in req['scenarios']:
   seq=list(s['expected_owner_sequence']); hand=[]
   if direct and s['id']==req['scenarios'][0]['id']: seq=['nomia','magia']; hand=['nomia_to_magia']
   changed = direct and s['id']==req['scenarios'][0]['id']; rows.append({'id':s['id'],'observed_first_owner':seq[0] if changed else s['expected_first_owner'],'observed_owner_sequence':seq,'mode_selected':None,'handoff_sequence':hand,'explanation_category':'fixture'})
  return {'evidence_kind':'fixture','model':{'provider':'fixture','name':'deterministic','version':'1','host':'unit-test'},'run_at':datetime.now(timezone.utc).isoformat(),'results':rows}
 def test_prepare_and_fixture_evaluate(self):
  roots=self.roots(); req=m.prepare(roots); corpus,digest=m.corpus_for(roots); result=m.evaluate(req,self.observations(req),corpus,digest)
  self.assertEqual(result['metrics']['scenario_accuracy'],1.0); self.assertFalse(result['claims']['live_routing_measured']); self.assertEqual(m.validate_result(result,digest),[])
 def test_direct_nomia_to_magia_is_reported(self):
  roots=self.roots(); req=m.prepare(roots); corpus,digest=m.corpus_for(roots); result=m.evaluate(req,self.observations(req,True),corpus,digest)
  self.assertTrue(result['forbidden_direct_handoff_scenarios']); self.assertTrue(any('forbidden direct' in x for x in m.validate_result(result,digest)))
 def test_corpus_hash_mismatch_is_rejected(self):
  roots=self.roots(); req=m.prepare(roots); req['corpus_sha256']='0'*64; corpus,digest=m.corpus_for(roots)
  with self.assertRaises(ValueError): m.evaluate(req,self.observations(req),corpus,digest)
 def test_live_claim_requires_live_evidence_kind(self):
  roots=self.roots(); req=m.prepare(roots); corpus,digest=m.corpus_for(roots); result=m.evaluate(req,self.observations(req),corpus,digest); result['claims']['live_routing_measured']=True
  self.assertTrue(any('claim/evidence-kind' in x for x in m.validate_result(result,digest)))
if __name__=='__main__': unittest.main()
