from __future__ import annotations
import argparse,json,sys
from pathlib import Path
def validate(d):
 e=[];runs=d.get("runs")
 if not isinstance(runs,list) or not runs:return ["runs:invalid"]
 cand=set();runids=set();work=set();refs={}
 for i,r in enumerate(runs):
  for k in ("candidate_id","candidate_identity","run_id","work_dir","evaluator_id","scenario_set_id"):
   if not r.get(k):e.append(f"run[{i}].{k}:missing")
  if r.get("candidate_id") in cand:e.append("candidate_id:duplicate")
  cand.add(r.get("candidate_id"))
  if r.get("run_id") in runids:e.append("run_id:duplicate")
  runids.add(r.get("run_id"))
  if r.get("work_dir") in work:e.append("work_dir:shared")
  work.add(r.get("work_dir"))
  for k in ("evaluator_id","scenario_set_id"):
   if r.get(k) and k not in refs:refs[k]=r[k]
   elif r.get(k) and refs[k]!=r[k]:e.append(f"comparability:{k}:mismatch")
  if r.get("holdout_blind") is True and r.get("candidate_saw_evaluator_only_assets") is not False:e.append(f"run[{i}]:holdout_leakage")
 return sorted(set(e))
def main():
 p=argparse.ArgumentParser();p.add_argument("manifest");a=p.parse_args();d=json.loads(Path(a.manifest).read_text());e=validate(d);print(json.dumps({"status":"pass" if not e else "fail","errors":e},indent=2,sort_keys=True));return 0 if not e else 2
if __name__=="__main__":sys.exit(main())
