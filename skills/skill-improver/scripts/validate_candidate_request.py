from __future__ import annotations
import argparse,json,sys
from pathlib import Path
OPS={"transformation-merge","backcross","repair-crossover","bounded-mutation","canonical","evidence-driven","focused","novel-bounded"}
def validate(d):
 e=[]
 for k in ("request_version","candidate_id","operator","base_parent_id","transformation_ids","reason"):
  if k not in d:e.append(f"missing:{k}")
 if e:return e
 if d["request_version"]!=1:e.append("request_version:unsupported")
 for k in ("candidate_id","base_parent_id","reason"):
  if not isinstance(d.get(k),str) or not d[k].strip():e.append(f"{k}:invalid")
 if d.get("operator") not in OPS:e.append("operator:invalid")
 donors=d.get("donor_parent_ids",[])
 if not isinstance(donors,list) or any(not isinstance(x,str) or not x for x in donors):e.append("donor_parent_ids:invalid")
 if d.get("candidate_id") in [d.get("base_parent_id"),*donors]:e.append("candidate:self_parent")
 ts=d.get("transformation_ids")
 if not isinstance(ts,list) or any(not isinstance(x,str) or not x for x in ts) or len(ts)!=len(set(ts)):e.append("transformation_ids:invalid")
 return e
def main():
 p=argparse.ArgumentParser();p.add_argument("request");a=p.parse_args();d=json.loads(Path(a.request).read_text());e=validate(d);print(json.dumps({"status":"pass" if not e else "fail","errors":e},indent=2,sort_keys=True));return 0 if not e else 2
if __name__=="__main__":sys.exit(main())
