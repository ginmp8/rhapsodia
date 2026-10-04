#!/usr/bin/env python3
import copy, importlib.util, unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('v2',R/'scripts'/'validate_perceptual_artifact.py')
v=importlib.util.module_from_spec(s); assert s.loader; s.loader.exec_module(v)

def req():
 return {
  'contract':'perceptual-review-request/v2','review_id':'r2','artifact_kind':'rendered-ui','artifact_profile':{'name':'ui','version':'1'},
  'reference':{'identity':'ref','identity_kind':'semantic','dimensions':{'width':1280,'height':720}},
  'candidate':{'identity':'cand','identity_kind':'semantic','dimensions':{'width':1280,'height':720}},
  'intended_state':{'reference':'loaded fixture a','candidate':'loaded fixture a'},
  'capture_context':{'reference_manifest_identity':'cap:r','candidate_manifest_identity':'cap:c','normalization_policy_identity':'norm:v1','comparison_keys':['viewport','theme'],'reference_facts':{'viewport':'1280x720','theme':'light'},'candidate_facts':{'viewport':'1280x720','theme':'light'}},
  'comparison_scope':['main'],
  'rubric':{'identity':'rubric:v1','version':'1','criteria':[{'id':'structure','category':'structure','required':True,'description':'structure preserved','evidence_types':['visual']}]},
  'gate_policy':{'identity':'gate:v1','blocking_severities':['blocking','high'],'max_medium_findings':0,'minimum_confidence':'medium','low_confidence_action':'inconclusive','require_finding_evidence':True,'require_required_criterion_evidence':True,'required_trials':1,'require_agreement':False,'disagreement_action':'inconclusive'},
  'evaluator_protocol':{'identity':'eval:v1','kind':'model','mode':'pairwise-criteria','required_capability':'image-capable-review','order_swap_required':False}
 }

def res(q=None):
 q=q or req()
 return {
  'contract':'perceptual-review-result/v2','review_id':q['review_id'],'request_digest':v.ident(q),'reference_identity':q['reference']['identity'],'candidate_identity':q['candidate']['identity'],'rubric_identity':q['rubric']['identity'],'gate_policy_identity':q['gate_policy']['identity'],'evaluator_protocol_identity':q['evaluator_protocol']['identity'],
  'state_alignment':'matched','verdict':'pass','review_executed':True,'trial_count':1,'agreement':'not-required',
  'criteria_results':[{'criterion_id':'structure','status':'pass','confidence':'high','evidence_refs':['img:r','img:c']}],
  'findings':[],'supplemental_measurements':[],'evidence_refs':['img:r','img:c'],'uncertainty_reasons':[],'limitations':[],
  'recapture':{'required':False,'reason':''},'policy_decision':{'outcome':'pass','reasons':['required-criteria-passed']}
 }

def codes(report): return {x['code'] for x in report['errors']}

class V2Tests(unittest.TestCase):
 def test_request_valid(self): self.assertEqual(v.validate(req())['status'],'pass')
 def test_result_requires_request(self): self.assertIn('E_REQUEST_REQUIRED', codes(v.validate(res())))
 def test_result_cross_bound_valid(self):
  q=req(); self.assertEqual(v.validate(res(q),q)['status'],'pass')
 def test_digest_binding(self):
  q=req(); d=res(q); d['request_digest']='0'*64; self.assertIn('E_REQUEST_DIGEST',codes(v.validate(d,q)))
 def test_candidate_binding(self):
  q=req(); d=res(q); d['candidate_identity']='other'; self.assertIn('E_BINDING',codes(v.validate(d,q)))
 def test_capture_drift_cannot_match(self):
  q=req(); q['capture_context']['candidate_facts']['theme']='dark'; d=res(q); self.assertIn('E_CAPTURE_ALIGNMENT',codes(v.validate(d,q)))
 def test_required_criterion(self):
  q=req(); d=res(q); d['criteria_results']=[]; self.assertIn('E_REQUIRED_CRITERION',codes(v.validate(d,q)))
 def test_confidence_floor(self):
  q=req(); d=res(q); d['criteria_results'][0]['confidence']='low'; self.assertIn('E_POLICY_CONFIDENCE',codes(v.validate(d,q)))
 def test_magnitude_is_not_severity(self):
  q=req(); d=res(q); d['findings']=[{'region':'main','criterion_id':'structure','category':'structure','difference':'large harmless texture change','difference_type':'texture','perceptual_magnitude':'large','impact_severity':'low','confidence':'high','evidence_refs':['diff:1']}]
  self.assertEqual(v.validate(d,q)['status'],'pass')
 def test_blocking_small_finding_blocks_pass(self):
  q=req(); d=res(q); d['findings']=[{'region':'label','criterion_id':'structure','category':'structure','difference':'single critical digit differs','difference_type':'text','perceptual_magnitude':'tiny','impact_severity':'blocking','confidence':'high','evidence_refs':['diff:digit']}]
  self.assertIn('E_POLICY_BLOCKING',codes(v.validate(d,q)))
 def test_invalid_requires_recapture(self):
  q=req(); q['intended_state']['candidate']='loading'; d=res(q); d['state_alignment']='mismatched'; d['verdict']='invalid'; d['review_executed']=False; d['criteria_results']=[]; d['evidence_refs']=[]; d['recapture']={'required':False,'reason':''}; d['policy_decision']={'outcome':'invalid','reasons':['state-mismatch']}
  self.assertIn('E_RECAPTURE',codes(v.validate(d,q)))
 def test_inconclusive_requires_uncertainty(self):
  q=req(); d=res(q); d['verdict']='inconclusive'; d['policy_decision']={'outcome':'inconclusive','reasons':['low-confidence']}; self.assertIn('E_UNCERTAINTY_REASON',codes(v.validate(d,q)))
 def test_threshold_measurement_binds_policy(self):
  q=req(); d=res(q); d['supplemental_measurements']=[{'method':'pixel-diff','intended_property':'raster delta','scope':'main','value':0.001,'threshold':0.01,'outcome':'informational','evidence_ref':'metric:1'}]
  self.assertIn('E_MEASUREMENT_POLICY',codes(v.validate(d,q)))
 def test_agreement_policy(self):
  q=req(); q['gate_policy']['require_agreement']=True; q['gate_policy']['required_trials']=2; d=res(q); d['trial_count']=2; d['agreement']='disagreement'; self.assertIn('E_POLICY_AGREEMENT',codes(v.validate(d,q)))
 def test_locator_bounds(self):
  q=req(); d=res(q); d['findings']=[{'region':'main','locator':{'kind':'normalized-bbox','x':.9,'y':.9,'width':.2,'height':.2},'criterion_id':'structure','category':'structure','difference':'offset','difference_type':'move','perceptual_magnitude':'small','impact_severity':'low','confidence':'high','evidence_refs':['diff:1']}]
  self.assertIn('E_LOCATOR_BOUNDS',codes(v.validate(d,q)))

if __name__=='__main__': unittest.main()
