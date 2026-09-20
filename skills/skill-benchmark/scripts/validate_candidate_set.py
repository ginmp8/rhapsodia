from __future__ import annotations
import argparse,json,sys
from pathlib import Path
def validate(d):
 e=[];rows=d.get("candidates")
 if not isinstance(rows,list) or not rows:return ["candidates:invalid"]
 ids=[];keys=("baseline_id","evaluator_id","scenario_set_id")
 refs={}
 for i,r in enumerate(rows):
  if not isinstance(r,dict):e.append(f"candidate[{i}]:invalid");continue
  cid=r.get("candidate_id");ids.append(cid)
  if not cid:e.append(f"candidate[{i}].candidate_id:missing")
  for k in keys:
   if not r.get(k):e.append(f"candidate[{i}].{k}:missing")
   elif k not in refs:refs[k]=r[k]
   elif refs[k]!=r[k]:e.append(f"comparability:{k}:mismatch")
  if not isinstance(r.get("metrics",{}),dict):e.append(f"candidate[{i}].metrics:invalid")
 if len(ids)!=len(set(ids)):e.append("candidate_id:duplicate")
 return sorted(set(e))
def main():
 p=argparse.ArgumentParser();p.add_argument("input");a=p.parse_args();d=json.loads(Path(a.input).read_text());e=validate(d);print(json.dumps({"status":"pass" if not e else "fail","errors":e},indent=2,sort_keys=True));return 0 if not e else 2
if __name__=="__main__":sys.exit(main())
