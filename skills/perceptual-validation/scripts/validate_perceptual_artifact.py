#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from typing import Any
ARTIFACTS={"screenshot","rendered-ui","page-render","pdf-page","slide","chart","diagram","image","other"}
CATEGORIES={"content-presence","structure","layout","alignment","spacing","typography","hierarchy","component-shape","chart-encoding","diagram-relations","other"}
ALIGN={"matched","mismatched","unknown"}; VERDICTS={"pass","fail","invalid","blocked","inconclusive"}; SEVERITY={"blocking","high","medium","low"}; CONF={"high","medium","low"}
REQUEST_FIELDS={"contract","review_id","artifact_kind","reference_identity","candidate_identity","reference_state","candidate_state","comparison_scope","rubric_categories","evaluator_identity","required_capability"}
RESULT_FIELDS={"contract","review_id","request_identity","reference_identity","candidate_identity","evaluator_identity","state_alignment","verdict","review_executed","findings","evidence_refs"}
FINDING_FIELDS={"region","category","difference","severity","confidence"}
def ne(v:Any)->bool:return isinstance(v,str) and bool(v.strip())
def sl(v:Any)->bool:return isinstance(v,list) and all(ne(x) for x in v)
def dg(c,p,m):return {"code":c,"path":p,"message":m}
def unknown(d,allowed,path,e):
 if isinstance(d,dict):
  for k in sorted(set(d)-allowed):e.append(dg("E_SCHEMA_ADDITIONAL_PROPERTY",f"{path}.{k}","property is not allowed by the schema"))
def dup(v,path,e):
 if isinstance(v,list) and all(isinstance(x,str) for x in v) and len(v)!=len(set(v)):e.append(dg("E_DUPLICATE",path,"items must be unique"))
def ident(d):return hashlib.sha256(json.dumps(d,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def request(d):
 e=[]
 unknown(d,REQUEST_FIELDS,"$",e)
 for f in ("review_id","reference_identity","candidate_identity","reference_state","candidate_state","evaluator_identity","required_capability"):
  if not ne(d.get(f)):e.append(dg("E_REQUIRED",f"$.{f}","must be non-empty"))
 if d.get("artifact_kind") not in ARTIFACTS:e.append(dg("E_ARTIFACT","$.artifact_kind",f"must be one of {sorted(ARTIFACTS)}"))
 for f in ("comparison_scope","rubric_categories"):
  if not sl(d.get(f)) or not d.get(f):e.append(dg("E_LIST",f"$.{f}","must be a non-empty string array"))
  else:dup(d.get(f),f"$.{f}",e)
 cats=set(d.get("rubric_categories",[]))-CATEGORIES
 if cats:e.append(dg("E_CATEGORY","$.rubric_categories",f"unsupported categories: {sorted(cats)}"))
 return e
def result(d):
 e=[]
 unknown(d,RESULT_FIELDS,"$",e)
 for f in ("review_id","request_identity","reference_identity","candidate_identity","evaluator_identity"):
  if not ne(d.get(f)):e.append(dg("E_REQUIRED",f"$.{f}","must be non-empty"))
 a=d.get("state_alignment"); v=d.get("verdict"); executed=d.get("review_executed")
 if a not in ALIGN:e.append(dg("E_ALIGNMENT","$.state_alignment",f"must be one of {sorted(ALIGN)}"))
 if v not in VERDICTS:e.append(dg("E_VERDICT","$.verdict",f"must be one of {sorted(VERDICTS)}"))
 if not isinstance(executed,bool):e.append(dg("E_EXECUTED","$.review_executed","must be boolean"))
 findings=d.get("findings")
 if not isinstance(findings,list):e.append(dg("E_FINDINGS","$.findings","must be an array")); findings=[]
 for i,f in enumerate(findings):
  if not isinstance(f,dict):e.append(dg("E_FINDING",f"$.findings[{i}]","must be an object"));continue
  unknown(f,FINDING_FIELDS,f"$.findings[{i}]",e)
  for k in ("region","category","difference"):
   if not ne(f.get(k)):e.append(dg("E_FINDING",f"$.findings[{i}].{k}","must be non-empty"))
  if f.get("severity") not in SEVERITY:e.append(dg("E_FINDING",f"$.findings[{i}].severity",f"must be one of {sorted(SEVERITY)}"))
  if f.get("confidence") not in CONF:e.append(dg("E_FINDING",f"$.findings[{i}].confidence",f"must be one of {sorted(CONF)}"))
 if not sl(d.get("evidence_refs")):e.append(dg("E_EVIDENCE","$.evidence_refs","must be a string array"))
 else:dup(d.get("evidence_refs"),"$.evidence_refs",e)
 if v in {"pass","fail"} and (a!="matched" or executed is not True):e.append(dg("E_VERDICT_STATE","$.verdict","pass/fail require matched state and executed review"))
 if v=="invalid" and a!="mismatched":e.append(dg("E_INVALID_STATE","$.verdict","invalid requires state_alignment=mismatched"))
 if v=="fail" and not findings:e.append(dg("E_FAIL_FINDINGS","$.findings","fail requires at least one finding"))
 if v=="pass" and any(isinstance(f,dict) and f.get("severity") in {"blocking","high"} for f in findings):e.append(dg("E_PASS_FINDINGS","$.findings","pass cannot contain blocking/high findings"))
 if v in {"blocked","inconclusive"} and executed is False and a=="matched": pass
 return e
def validate(d:Any):
 if not isinstance(d,dict):return {"validator":"perceptual-artifact-validator/v1","status":"fail","artifact_sha256":None,"errors":[dg("E_ROOT","$","must be object")]}
 c=d.get("contract")
 if c=="perceptual-review-request/v1":e=request(d)
 elif c=="perceptual-review-result/v1":e=result(d)
 else:e=[dg("E_CONTRACT","$.contract","must be perceptual-review-request/v1 or perceptual-review-result/v1")]
 return {"validator":"perceptual-artifact-validator/v1","status":"pass" if not e else "fail","artifact_sha256":ident(d),"errors":e}
def main():
 ap=argparse.ArgumentParser();ap.add_argument("artifact");ap.add_argument("--json",dest="out");a=ap.parse_args()
 try:r=validate(json.loads(Path(a.artifact).read_text()))
 except Exception as x:r={"validator":"perceptual-artifact-validator/v1","status":"fail","artifact_sha256":None,"errors":[dg("E_PARSE","$",str(x))]}
 s=json.dumps(r,indent=2)+"\n";print(s,end="")
 if a.out:Path(a.out).write_text(s)
 return 0 if r["status"]=="pass" else 1
if __name__=="__main__":raise SystemExit(main())
