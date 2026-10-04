#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path
def err(c,p,m): return {"severity":"error","code":c,"path":p,"message":m}
def validate(d):
 e=[]
 if d.get("contract")!="convergence-plan/v1": e.append(err("E_CONTRACT","$.contract","must be convergence-plan/v1"))
 if d.get("authority",{}).get("producer")!="magia": e.append(err("E_PRODUCER","$.authority.producer","canonical producer/repair owner must be magia"))
 cps=d.get("checkpoints",[]); gates=d.get("gates",[])
 if not cps: e.append(err("E_CHECKPOINTS","$.checkpoints","must be non-empty"))
 ids=[x.get("id") for x in cps if isinstance(x,dict)]; gids=[x.get("id") for x in gates if isinstance(x,dict)]
 if len(ids)!=len(set(ids)): e.append(err("E_CHECKPOINT_IDS","$.checkpoints","checkpoint ids must be unique"))
 if len(gids)!=len(set(gids)): e.append(err("E_GATE_IDS","$.gates","gate ids must be unique"))
 known=set(ids); gknown=set(gids); graph={}
 for i,c in enumerate(cps):
  deps=c.get("depends_on",[]); graph[c.get("id")]=deps
  if any(x not in known for x in deps): e.append(err("E_DEP","$.checkpoints[%d].depends_on"%i,"unknown checkpoint dependency"))
  if not c.get("reference_scope") or not c.get("oracle_identity"): e.append(err("E_ORACLE","$.checkpoints[%d]"%i,"reference_scope and frozen oracle_identity are required before production"))
  if any(x not in gknown for x in c.get("gate_ids",[])): e.append(err("E_GATE_REF","$.checkpoints[%d].gate_ids"%i,"unknown gate"))
 p=d.get("promotion",{})
 for k in ("requires_all_required_gates","gate_order_is_binding","accepted_feedback_only"):
  if p.get(k) is not True: e.append(err("E_PROMOTION","$.promotion."+k,"must be true"))
 if p.get("autonomy_policy")=="human-required":
  human={g.get("id") for g in gates if g.get("kind")=="human-approval" and g.get("required") is True}
  for i,c in enumerate(cps):
   if not human.intersection(c.get("gate_ids",[])): e.append(err("E_HUMAN_REQUIRED","$.checkpoints[%d].gate_ids"%i,"human-required policy needs a required human gate"))
 need=p.get("min_independent_adversarial_reviewers",0)
 for i,c in enumerate(cps):
  adv=[g for g in gates if g.get("id") in c.get("gate_ids",[]) and g.get("kind")=="adversarial-review" and g.get("required") is True]
  if len({g.get("evaluator_identity") for g in adv})<need: e.append(err("E_ADVERSARIAL_INDEPENDENCE","$.checkpoints[%d].gate_ids"%i,"not enough distinct required adversarial evaluator identities"))
 b=d.get("budgets",{})
 if isinstance(b.get("max_checkpoints"),int) and len(cps)>b["max_checkpoints"]: e.append(err("E_CHECKPOINT_BUDGET","$.checkpoints","exceeds max_checkpoints"))
 seen,temp=set(),set()
 def visit(n):
  if n in temp:return False
  if n in seen:return True
  temp.add(n)
  for x in graph.get(n,[]):
   if not visit(x):return False
  temp.remove(n);seen.add(n);return True
 if any(not visit(n) for n in list(graph)): e.append(err("E_CYCLE","$.checkpoints","checkpoint graph must be acyclic"))
 return {"status":"pass" if not e else "fail","errors":e}
def main():
 ap=argparse.ArgumentParser();ap.add_argument("plan");ap.add_argument("--json",dest="out");a=ap.parse_args()
 try:d=json.loads(Path(a.plan).read_text(encoding="utf-8"))
 except Exception as x: print(json.dumps({"status":"fail","errors":[err("E_JSON","$",str(x))]},indent=2));return 2
 r=validate(d);txt=json.dumps(r,indent=2)
 if a.out:Path(a.out).write_text(txt+"\n",encoding="utf-8")
 print(txt);return 0 if r["status"]=="pass" else 1
if __name__=="__main__":raise SystemExit(main())
