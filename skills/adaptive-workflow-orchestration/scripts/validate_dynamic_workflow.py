#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
def err(code,path,msg): return {"severity":"error","code":code,"path":path,"message":msg}
def validate(d):
 e=[]
 if d.get("contract")!="dynamic-workflow-plan/v1": e.append(err("E_CONTRACT","$.contract","must be dynamic-workflow-plan/v1"))
 stages=d.get("stages")
 if not isinstance(stages,list) or not stages: return {"status":"fail","errors":e+[err("E_STAGES","$.stages","must be non-empty")]}
 ids=[x.get("id") for x in stages if isinstance(x,dict)]
 if len(ids)!=len(set(ids)) or any(not isinstance(x,str) or not x for x in ids): e.append(err("E_STAGE_IDS","$.stages","stage ids must be unique non-empty strings"))
 known=set(ids); graph={}
 for i,s in enumerate(stages):
  if not isinstance(s,dict): e.append(err("E_STAGE","$.stages[%d]"%i,"must be object")); continue
  deps=s.get("depends_on",[]); graph[s.get("id")]=deps
  if any(x not in known for x in deps): e.append(err("E_DEP","$.stages[%d].depends_on"%i,"unknown dependency"))
  if s.get("effects")=="read-only" and s.get("write_set"): e.append(err("E_READONLY_WRITE","$.stages[%d].write_set"%i,"read-only stage must not write"))
  if s.get("effects")=="mutating" and not s.get("write_set"): e.append(err("E_MUTATION_SCOPE","$.stages[%d].write_set"%i,"mutating stage requires write_set"))
 b=d.get("budgets",{})
 for k in ("max_workers","max_parallel","max_total_agents","max_rounds"):
  if not isinstance(b.get(k),int) or b.get(k)<1: e.append(err("E_BUDGET","$.budgets."+k,"must be positive integer"))
 if all(isinstance(b.get(k),int) for k in ("max_workers","max_parallel","max_total_agents")):
  if b["max_parallel"]>b["max_workers"] or b["max_workers"]>b["max_total_agents"]: e.append(err("E_BUDGET_ORDER","$.budgets","require max_parallel <= max_workers <= max_total_agents"))
 for i,s in enumerate(stages):
  if isinstance(s,dict) and isinstance(s.get("max_parallel"),int) and isinstance(b.get("max_parallel"),int) and s["max_parallel"]>b["max_parallel"]: e.append(err("E_STAGE_PARALLEL","$.stages[%d].max_parallel"%i,"exceeds global max_parallel"))
 r=d.get("runtime",{})
 if r.get("plan_owner")!="runtime-script" or r.get("intermediate_state")!="runtime-external": e.append(err("E_RUNTIME_OWNER","$.runtime","hard runtime state must remain external to planner context"))
 caps=d.get("capabilities",{}).get("required",[])
 if r.get("resumption_semantics")=="durable-external" and "durable-state" not in caps: e.append(err("E_DURABLE_CAPABILITY","$.runtime.resumption_semantics","durable-external requires durable-state capability"))
 v=d.get("verification",{})
 if v.get("same_model_independence_claim") is not False: e.append(err("E_FALSE_INDEPENDENCE","$.verification.same_model_independence_claim","same-model isolation cannot be claimed as epistemic independence"))
 if v.get("oracle_priority")!="deterministic-first": e.append(err("E_ORACLE_PRIORITY","$.verification.oracle_priority","must be deterministic-first"))
 seen,temp=set(),set()
 def visit(n):
  if n in temp: return False
  if n in seen: return True
  temp.add(n)
  for x in graph.get(n,[]): 
   if not visit(x): return False
  temp.remove(n); seen.add(n); return True
 if any(not visit(n) for n in list(graph)): e.append(err("E_CYCLE","$.stages","dependency graph must be acyclic"))
 return {"status":"pass" if not e else "fail","errors":e}
def main():
 ap=argparse.ArgumentParser(); ap.add_argument("plan"); ap.add_argument("--json",dest="out"); a=ap.parse_args()
 try: d=json.loads(Path(a.plan).read_text(encoding="utf-8"))
 except Exception as x: print(json.dumps({"status":"fail","errors":[err("E_JSON","$",str(x))]},indent=2)); return 2
 r=validate(d); text=json.dumps(r,indent=2)
 if a.out: Path(a.out).write_text(text+"\n",encoding="utf-8")
 print(text); return 0 if r["status"]=="pass" else 1
if __name__=="__main__": raise SystemExit(main())
