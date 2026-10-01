#!/usr/bin/env python3
import importlib.util,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1];s=importlib.util.spec_from_file_location('v',R/'scripts'/'validate_perceptual_artifact.py');v=importlib.util.module_from_spec(s);assert s.loader;s.loader.exec_module(v)
def req():return {"contract":"perceptual-review-request/v1","review_id":"r1","artifact_kind":"rendered-ui","reference_identity":"sha:r","candidate_identity":"sha:c","reference_state":"loaded fixture a","candidate_state":"loaded fixture a","comparison_scope":["main"],"rubric_categories":["structure","spacing"],"evaluator_identity":"rubric:v1","required_capability":"image-capable-review"}
def res():return {"contract":"perceptual-review-result/v1","review_id":"r1","request_identity":"sha:q","reference_identity":"sha:r","candidate_identity":"sha:c","evaluator_identity":"rubric:v1","state_alignment":"matched","verdict":"pass","review_executed":True,"findings":[],"evidence_refs":["img:r","img:c"]}
class T(unittest.TestCase):
 def test_request(self):self.assertEqual(v.validate(req())["status"],"pass")
 def test_result(self):self.assertEqual(v.validate(res())["status"],"pass")
 def test_invalid_requires_mismatch(self):
  d=res();d["verdict"]="invalid";self.assertIn("E_INVALID_STATE",{x['code'] for x in v.validate(d)['errors']})
 def test_mismatch_is_not_fail(self):
  d=res();d["state_alignment"]="mismatched";d["verdict"]="fail";d["findings"]=[{"region":"main","category":"spacing","difference":"x","severity":"medium","confidence":"high"}];self.assertIn("E_VERDICT_STATE",{x['code'] for x in v.validate(d)['errors']})
 def test_fail_needs_finding(self):
  d=res();d["verdict"]="fail";self.assertIn("E_FAIL_FINDINGS",{x['code'] for x in v.validate(d)['errors']})
 def test_pass_rejects_high_finding(self):
  d=res();d["findings"]=[{"region":"main","category":"spacing","difference":"x","severity":"high","confidence":"high"}];self.assertIn("E_PASS_FINDINGS",{x['code'] for x in v.validate(d)['errors']})
if __name__=='__main__':unittest.main()
