from __future__ import annotations
import argparse,json,sys
from pathlib import Path

DIRS={"maximize","minimize"}

def validate(d):
    e=[]
    for k in ("handoff_version","contract_version","search_id","mode","target_identity","baseline_candidate_id","canonical_candidate_id","evaluation_identity","hard_gates","objectives","budget","mutation_interface","evaluation_interface","allowed_operators","preserve_roles","selection_policy"):
        if k not in d:e.append(f"missing:{k}")
    if e:return e
    if d["handoff_version"]!=1:e.append("handoff_version:unsupported")
    if d["contract_version"]!=1:e.append("contract_version:unsupported")
    if d["mode"]!="evolutionary-optimization":e.append("mode:invalid")
    b=d.get("budget",{})
    for k in ("initial_variants","max_active_candidates","max_total_candidates","finalists","stagnant_rounds","max_recombination_proposals_per_round"):
        if not isinstance(b.get(k),int) or b[k]<=0:e.append(f"budget.{k}:invalid")
    if isinstance(b.get("max_total_candidates"),int) and b["max_total_candidates"]>20:e.append("budget:max_total_candidates_exceeds_20")
    if isinstance(b.get("finalists"),int) and isinstance(b.get("max_active_candidates"),int) and b["finalists"]>b["max_active_candidates"]:e.append("budget:finalists_exceed_active")
    ev=d.get("evaluation_identity",{})
    if not isinstance(ev,dict) or not ev.get("evaluator_id") or not ev.get("scenario_set_id"):e.append("evaluation_identity:invalid")
    gates=d.get("hard_gates")
    if not isinstance(gates,list) or not gates or len(gates)!=len(set(gates)):e.append("hard_gates:invalid")
    objs=d.get("objectives")
    if not isinstance(objs,list) or not objs:e.append("objectives:invalid")
    else:
        names=[]
        for i,o in enumerate(objs):
            if not isinstance(o,dict) or not o.get("name") or o.get("direction") not in DIRS:e.append(f"objectives[{i}]:invalid")
            else:names.append(o["name"])
        if len(names)!=len(set(names)):e.append("objectives:duplicate")
    for k in ("mutation_interface","evaluation_interface"):
        v=d.get(k,{})
        if not isinstance(v,dict) or not v.get("owner") or not v.get("contract"):e.append(f"{k}:invalid")
    return e

def main():
    p=argparse.ArgumentParser();p.add_argument("handoff");p.add_argument("--json-output");a=p.parse_args()
    d=json.loads(Path(a.handoff).read_text(encoding="utf-8"));e=validate(d);r={"status":"pass" if not e else "fail","errors":e};s=json.dumps(r,indent=2,sort_keys=True)
    if a.json_output:Path(a.json_output).write_text(s+"\n",encoding="utf-8")
    print(s);return 0 if not e else 2
if __name__=="__main__":sys.exit(main())
