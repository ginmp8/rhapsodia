import importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location("m",ROOT/"scripts/validate_candidate_set.py");m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def row(cid):return {"candidate_id":cid,"baseline_id":"B","evaluator_id":"E","scenario_set_id":"S","metrics":{"q":1}}
def test_valid():assert m.validate({"candidates":[row("C1"),row("C2")]})==[]
def test_evaluator_mismatch():
 d={"candidates":[row("C1"),row("C2")]};d["candidates"][1]["evaluator_id"]="E2";assert "comparability:evaluator_id:mismatch" in m.validate(d)
