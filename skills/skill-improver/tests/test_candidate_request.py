import importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location("m",ROOT/"scripts/validate_candidate_request.py");m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def req():return {"request_version":1,"candidate_id":"C7","operator":"transformation-merge","base_parent_id":"C3","donor_parent_ids":["C5"],"transformation_ids":["T2","T8"],"reason":"complementary"}
def test_valid():assert m.validate(req())==[]
def test_self_parent():
 d=req();d["candidate_id"]="C3";assert "candidate:self_parent" in m.validate(d)
