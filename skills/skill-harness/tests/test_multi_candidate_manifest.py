import importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location("m",ROOT/"scripts/validate_multi_candidate_manifest.py");m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def row(cid,n):return {"candidate_id":cid,"candidate_identity":cid+"hash","run_id":f"R{n}","work_dir":f"/tmp/w{n}","evaluator_id":"E","scenario_set_id":"S","holdout_blind":True,"candidate_saw_evaluator_only_assets":False}
def test_valid():assert m.validate({"runs":[row("C1",1),row("C2",2)]})==[]
def test_shared_workdir():
 d={"runs":[row("C1",1),row("C2",2)]};d["runs"][1]["work_dir"]=d["runs"][0]["work_dir"];assert "work_dir:shared" in m.validate(d)
