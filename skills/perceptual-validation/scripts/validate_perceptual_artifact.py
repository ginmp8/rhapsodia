#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path
from typing import Any

ARTIFACTS={"screenshot","rendered-ui","page-render","pdf-page","slide","chart","diagram","image","other"}
CATEGORIES={"content-presence","structure","layout","alignment","spacing","typography","hierarchy","component-shape","chart-encoding","diagram-relations","other"}
PROFILES={"ui","document-page-slide","chart","diagram","general-image","custom"}
PROFILE_ARTIFACTS={
 "ui":{"screenshot","rendered-ui","page-render","image"},
 "document-page-slide":{"page-render","pdf-page","slide","image","screenshot"},
 "chart":{"chart","image","screenshot","rendered-ui"},
 "diagram":{"diagram","image","screenshot"},
 "general-image":{"image","screenshot"},
 "custom":ARTIFACTS,
}
ALIGN={"matched","mismatched","unknown"}; VERDICTS={"pass","fail","invalid","blocked","inconclusive"}
SEVERITY={"blocking","high","medium","low"}; CONF={"high","medium","low"}; CONF_RANK={"low":0,"medium":1,"high":2}
MAGNITUDE={"tiny","small","medium","large"}; AGREEMENT={"not-required","agreement","disagreement","unknown"}
CRITERION_STATUS={"pass","fail","inconclusive","not-reviewed"}
EVIDENCE_TYPES={"visual","content","geometry","measurement","relation","human"}
DIFF_TYPES={"presence","text","move","resize","style","alignment","spacing","shape","encoding","relation","color","texture","other"}
LOCATOR_KINDS={"label","normalized-bbox","page","slide","component","selector","other"}
IDENTITY_KINDS={"sha256","semantic","external"}
EVALUATOR_KINDS={"human","model","hybrid"}
EVALUATOR_MODES={"pairwise-criteria","single-review-criteria","human-review-criteria","hybrid-criteria","custom"}

REQUEST_V1_FIELDS={"contract","review_id","artifact_kind","reference_identity","candidate_identity","reference_state","candidate_state","comparison_scope","rubric_categories","evaluator_identity","required_capability"}
RESULT_V1_FIELDS={"contract","review_id","request_identity","reference_identity","candidate_identity","evaluator_identity","state_alignment","verdict","review_executed","findings","evidence_refs"}
FINDING_V1_FIELDS={"region","category","difference","severity","confidence"}
REQUEST_V2_FIELDS={"contract","review_id","artifact_kind","artifact_profile","reference","candidate","intended_state","capture_context","comparison_scope","rubric","gate_policy","evaluator_protocol"}
RESULT_V2_FIELDS={"contract","review_id","request_digest","reference_identity","candidate_identity","rubric_identity","gate_policy_identity","evaluator_protocol_identity","state_alignment","verdict","review_executed","trial_count","agreement","order_swap_performed","criteria_results","findings","supplemental_measurements","evidence_refs","uncertainty_reasons","limitations","recapture","policy_decision"}

def ne(v:Any)->bool:return isinstance(v,str) and bool(v.strip())
def sl(v:Any)->bool:return isinstance(v,list) and all(ne(x) for x in v)
def dg(c,p,m,severity="error"):return {"code":c,"path":p,"message":m,"severity":severity}
def unknown(d,allowed,path,e):
 if isinstance(d,dict):
  for k in sorted(set(d)-allowed):e.append(dg("E_SCHEMA_ADDITIONAL_PROPERTY",f"{path}.{k}","property is not allowed by the contract"))
def dup(v,path,e):
 if isinstance(v,list) and all(isinstance(x,str) for x in v) and len(v)!=len(set(v)):e.append(dg("E_DUPLICATE",path,"items must be unique"))
def ident(d):return hashlib.sha256(json.dumps(d,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def nonempty_list(v):return isinstance(v,list) and bool(v) and all(ne(x) for x in v)
def fact_map(v):return isinstance(v,dict) and all(ne(k) and ne(val) for k,val in v.items())
def object_fields(d,allowed,path,e):
 if not isinstance(d,dict):e.append(dg("E_OBJECT",path,"must be an object"));return False
 unknown(d,allowed,path,e);return True

def request_v1(d):
 e=[];unknown(d,REQUEST_V1_FIELDS,"$",e)
 for f in ("review_id","reference_identity","candidate_identity","reference_state","candidate_state","evaluator_identity","required_capability"):
  if not ne(d.get(f)):e.append(dg("E_REQUIRED",f"$.{f}","must be non-empty"))
 if d.get("artifact_kind") not in ARTIFACTS:e.append(dg("E_ARTIFACT","$.artifact_kind",f"must be one of {sorted(ARTIFACTS)}"))
 for f in ("comparison_scope","rubric_categories"):
  if not sl(d.get(f)) or not d.get(f):e.append(dg("E_LIST",f"$.{f}","must be a non-empty string array"))
  else:dup(d.get(f),f"$.{f}",e)
 cats=set(d.get("rubric_categories",[]))-CATEGORIES
 if cats:e.append(dg("E_CATEGORY","$.rubric_categories",f"unsupported categories: {sorted(cats)}"))
 return e

def result_v1(d):
 e=[];unknown(d,RESULT_V1_FIELDS,"$",e)
 for f in ("review_id","request_identity","reference_identity","candidate_identity","evaluator_identity"):
  if not ne(d.get(f)):e.append(dg("E_REQUIRED",f"$.{f}","must be non-empty"))
 a=d.get("state_alignment");v=d.get("verdict");executed=d.get("review_executed")
 if a not in ALIGN:e.append(dg("E_ALIGNMENT","$.state_alignment",f"must be one of {sorted(ALIGN)}"))
 if v not in VERDICTS:e.append(dg("E_VERDICT","$.verdict",f"must be one of {sorted(VERDICTS)}"))
 if not isinstance(executed,bool):e.append(dg("E_EXECUTED","$.review_executed","must be boolean"))
 findings=d.get("findings")
 if not isinstance(findings,list):e.append(dg("E_FINDINGS","$.findings","must be an array"));findings=[]
 for i,f in enumerate(findings):
  if not isinstance(f,dict):e.append(dg("E_FINDING",f"$.findings[{i}]","must be an object"));continue
  unknown(f,FINDING_V1_FIELDS,f"$.findings[{i}]",e)
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
 return e

def _artifact_v2(obj,path,e):
 if not object_fields(obj,{"identity","identity_kind","dimensions"},path,e):return
 if not ne(obj.get("identity")):e.append(dg("E_REQUIRED",f"{path}.identity","must be non-empty"))
 k=obj.get("identity_kind")
 if k not in IDENTITY_KINDS:e.append(dg("E_IDENTITY_KIND",f"{path}.identity_kind",f"must be one of {sorted(IDENTITY_KINDS)}"))
 if k=="sha256" and (not ne(obj.get("identity")) or re.fullmatch(r"[a-f0-9]{64}",obj.get("identity","").lower()) is None):e.append(dg("E_SHA256_IDENTITY",f"{path}.identity","sha256 identity must be exactly 64 hexadecimal characters"))
 dims=obj.get("dimensions")
 if dims is not None:
  if object_fields(dims,{"width","height"},f"{path}.dimensions",e):
   for key in ("width","height"):
    if not isinstance(dims.get(key),int) or isinstance(dims.get(key),bool) or dims.get(key)<1:e.append(dg("E_DIMENSION",f"{path}.dimensions.{key}","must be an integer >= 1"))

def request_v2(d):
 e=[];unknown(d,REQUEST_V2_FIELDS,"$",e)
 if not ne(d.get("review_id")):e.append(dg("E_REQUIRED","$.review_id","must be non-empty"))
 kind=d.get("artifact_kind")
 if kind not in ARTIFACTS:e.append(dg("E_ARTIFACT","$.artifact_kind",f"must be one of {sorted(ARTIFACTS)}"))
 profile=d.get("artifact_profile")
 if object_fields(profile,{"name","version"},"$.artifact_profile",e):
  pname=profile.get("name")
  if pname not in PROFILES:e.append(dg("E_PROFILE","$.artifact_profile.name",f"must be one of {sorted(PROFILES)}"))
  if not ne(profile.get("version")):e.append(dg("E_REQUIRED","$.artifact_profile.version","must be non-empty"))
  if pname in PROFILE_ARTIFACTS and kind in ARTIFACTS and kind not in PROFILE_ARTIFACTS[pname]:e.append(dg("E_PROFILE_ARTIFACT","$.artifact_profile","profile is not compatible with artifact_kind"))
 _artifact_v2(d.get("reference"),"$.reference",e);_artifact_v2(d.get("candidate"),"$.candidate",e)
 state=d.get("intended_state")
 if object_fields(state,{"reference","candidate"},"$.intended_state",e):
  for key in ("reference","candidate"):
   if not ne(state.get(key)):e.append(dg("E_REQUIRED",f"$.intended_state.{key}","must be non-empty"))
 cap=d.get("capture_context")
 if object_fields(cap,{"reference_manifest_identity","candidate_manifest_identity","normalization_policy_identity","comparison_keys","reference_facts","candidate_facts"},"$.capture_context",e):
  for key in ("reference_manifest_identity","candidate_manifest_identity","normalization_policy_identity"):
   if not ne(cap.get(key)):e.append(dg("E_REQUIRED",f"$.capture_context.{key}","must be non-empty"))
  keys=cap.get("comparison_keys")
  if not isinstance(keys,list) or any(not ne(x) for x in keys):e.append(dg("E_CAPTURE_KEYS","$.capture_context.comparison_keys","must be a string array"))
  else:dup(keys,"$.capture_context.comparison_keys",e)
  for key in ("reference_facts","candidate_facts"):
   if not fact_map(cap.get(key)):e.append(dg("E_CAPTURE_FACTS",f"$.capture_context.{key}","must be an object with non-empty string keys and values"))
 scope=d.get("comparison_scope")
 if not nonempty_list(scope):e.append(dg("E_SCOPE","$.comparison_scope","must be a non-empty string array"))
 else:dup(scope,"$.comparison_scope",e)
 rubric=d.get("rubric")
 if object_fields(rubric,{"identity","version","criteria"},"$.rubric",e):
  if not ne(rubric.get("identity")):e.append(dg("E_REQUIRED","$.rubric.identity","must be non-empty"))
  if not ne(rubric.get("version")):e.append(dg("E_REQUIRED","$.rubric.version","must be non-empty"))
  criteria=rubric.get("criteria")
  if not isinstance(criteria,list) or not criteria:e.append(dg("E_RUBRIC","$.rubric.criteria","must be a non-empty array"));criteria=[]
  ids=[]
  for i,c in enumerate(criteria):
   p=f"$.rubric.criteria[{i}]"
   if not object_fields(c,{"id","category","required","description","evidence_types"},p,e):continue
   if not ne(c.get("id")):e.append(dg("E_CRITERION",f"{p}.id","must be non-empty"))
   else:ids.append(c["id"])
   if c.get("category") not in CATEGORIES:e.append(dg("E_CATEGORY",f"{p}.category",f"must be one of {sorted(CATEGORIES)}"))
   if not isinstance(c.get("required"),bool):e.append(dg("E_CRITERION",f"{p}.required","must be boolean"))
   if not ne(c.get("description")):e.append(dg("E_CRITERION",f"{p}.description","must be non-empty"))
   types=c.get("evidence_types")
   if not isinstance(types,list) or not types or any(x not in EVIDENCE_TYPES for x in types):e.append(dg("E_CRITERION_EVIDENCE",f"{p}.evidence_types",f"must contain values from {sorted(EVIDENCE_TYPES)}"))
   else:dup(types,f"{p}.evidence_types",e)
  if len(ids)!=len(set(ids)):e.append(dg("E_DUPLICATE","$.rubric.criteria","criterion ids must be unique"))
 policy=d.get("gate_policy")
 if object_fields(policy,{"identity","blocking_severities","max_medium_findings","minimum_confidence","low_confidence_action","require_finding_evidence","require_required_criterion_evidence","required_trials","require_agreement","disagreement_action"},"$.gate_policy",e):
  if not ne(policy.get("identity")):e.append(dg("E_REQUIRED","$.gate_policy.identity","must be non-empty"))
  sev=policy.get("blocking_severities")
  if not isinstance(sev,list) or not sev or any(x not in SEVERITY for x in sev):e.append(dg("E_POLICY","$.gate_policy.blocking_severities",f"must be a non-empty subset of {sorted(SEVERITY)}"))
  else:dup(sev,"$.gate_policy.blocking_severities",e)
  m=policy.get("max_medium_findings")
  if not isinstance(m,int) or isinstance(m,bool) or m<0:e.append(dg("E_POLICY","$.gate_policy.max_medium_findings","must be integer >= 0"))
  if policy.get("minimum_confidence") not in CONF:e.append(dg("E_POLICY","$.gate_policy.minimum_confidence",f"must be one of {sorted(CONF)}"))
  if policy.get("low_confidence_action")!="inconclusive":e.append(dg("E_POLICY","$.gate_policy.low_confidence_action","must be inconclusive"))
  if policy.get("disagreement_action")!="inconclusive":e.append(dg("E_POLICY","$.gate_policy.disagreement_action","must be inconclusive"))
  for key in ("require_finding_evidence","require_required_criterion_evidence","require_agreement"):
   if not isinstance(policy.get(key),bool):e.append(dg("E_POLICY",f"$.gate_policy.{key}","must be boolean"))
  trials=policy.get("required_trials")
  if not isinstance(trials,int) or isinstance(trials,bool) or trials<1:e.append(dg("E_POLICY","$.gate_policy.required_trials","must be integer >= 1"))
 proto=d.get("evaluator_protocol")
 if object_fields(proto,{"identity","kind","mode","required_capability","order_swap_required","implementation_identity","prompt_identity"},"$.evaluator_protocol",e):
  if not ne(proto.get("identity")):e.append(dg("E_REQUIRED","$.evaluator_protocol.identity","must be non-empty"))
  if proto.get("kind") not in EVALUATOR_KINDS:e.append(dg("E_EVALUATOR_PROTOCOL","$.evaluator_protocol.kind",f"must be one of {sorted(EVALUATOR_KINDS)}"))
  if proto.get("mode") not in EVALUATOR_MODES:e.append(dg("E_EVALUATOR_PROTOCOL","$.evaluator_protocol.mode",f"must be one of {sorted(EVALUATOR_MODES)}"))
  if not ne(proto.get("required_capability")):e.append(dg("E_REQUIRED","$.evaluator_protocol.required_capability","must be non-empty"))
  if not isinstance(proto.get("order_swap_required"),bool):e.append(dg("E_EVALUATOR_PROTOCOL","$.evaluator_protocol.order_swap_required","must be boolean"))
  for key in ("implementation_identity","prompt_identity"):
   if key in proto and not ne(proto.get(key)):e.append(dg("E_EVALUATOR_PROTOCOL",f"$.evaluator_protocol.{key}","must be non-empty when present"))
 return e

def _locator(f,path,e):
 loc=f.get("locator")
 if loc is None:return
 if not object_fields(loc,{"kind","label","index","x","y","width","height","value"},f"{path}.locator",e):return
 kind=loc.get("kind")
 if kind not in LOCATOR_KINDS:e.append(dg("E_LOCATOR",f"{path}.locator.kind",f"must be one of {sorted(LOCATOR_KINDS)}"));return
 if kind=="normalized-bbox":
  vals=[loc.get(k) for k in ("x","y","width","height")]
  valid=all(isinstance(v,(int,float)) and not isinstance(v,bool) for v in vals)
  if not valid:e.append(dg("E_LOCATOR_BOUNDS",f"{path}.locator","normalized-bbox requires numeric x,y,width,height"));return
  x,y,w,h=vals
  if x<0 or y<0 or w<=0 or h<=0 or x>1 or y>1 or w>1 or h>1 or x+w>1+1e-12 or y+h>1+1e-12:e.append(dg("E_LOCATOR_BOUNDS",f"{path}.locator","normalized-bbox must fit within normalized 0..1 bounds"))
 if kind in {"page","slide"} and (not isinstance(loc.get("index"),int) or isinstance(loc.get("index"),bool) or loc.get("index")<0):e.append(dg("E_LOCATOR",f"{path}.locator.index","page/slide locator requires index >= 0"))
 if kind in {"label","component","selector","other"} and not (ne(loc.get("label")) or ne(loc.get("value"))):e.append(dg("E_LOCATOR",f"{path}.locator","locator requires label or value"))

def result_v2_local(d):
 e=[];unknown(d,RESULT_V2_FIELDS,"$",e)
 for f in ("review_id","request_digest","reference_identity","candidate_identity","rubric_identity","gate_policy_identity","evaluator_protocol_identity"):
  if not ne(d.get(f)):e.append(dg("E_REQUIRED",f"$.{f}","must be non-empty"))
 if ne(d.get("request_digest")) and re.fullmatch(r"[a-f0-9]{64}",d.get("request_digest","").lower()) is None:e.append(dg("E_REQUEST_DIGEST","$.request_digest","must be a 64-character hexadecimal SHA-256 digest"))
 if d.get("state_alignment") not in ALIGN:e.append(dg("E_ALIGNMENT","$.state_alignment",f"must be one of {sorted(ALIGN)}"))
 if d.get("verdict") not in VERDICTS:e.append(dg("E_VERDICT","$.verdict",f"must be one of {sorted(VERDICTS)}"))
 if not isinstance(d.get("review_executed"),bool):e.append(dg("E_EXECUTED","$.review_executed","must be boolean"))
 tc=d.get("trial_count")
 if not isinstance(tc,int) or isinstance(tc,bool) or tc<0:e.append(dg("E_TRIAL_COUNT","$.trial_count","must be integer >= 0"))
 if d.get("agreement") not in AGREEMENT:e.append(dg("E_AGREEMENT","$.agreement",f"must be one of {sorted(AGREEMENT)}"))
 if "order_swap_performed" in d and not isinstance(d.get("order_swap_performed"),bool):e.append(dg("E_PROTOCOL_ORDER_SWAP","$.order_swap_performed","must be boolean when present"))
 criteria=d.get("criteria_results")
 if not isinstance(criteria,list):e.append(dg("E_CRITERIA_RESULTS","$.criteria_results","must be an array"));criteria=[]
 ids=[]
 for i,c in enumerate(criteria):
  p=f"$.criteria_results[{i}]"
  if not object_fields(c,{"criterion_id","status","confidence","evidence_refs"},p,e):continue
  if not ne(c.get("criterion_id")):e.append(dg("E_CRITERION_RESULT",f"{p}.criterion_id","must be non-empty"))
  else:ids.append(c["criterion_id"])
  if c.get("status") not in CRITERION_STATUS:e.append(dg("E_CRITERION_RESULT",f"{p}.status",f"must be one of {sorted(CRITERION_STATUS)}"))
  if c.get("confidence") not in CONF:e.append(dg("E_CRITERION_RESULT",f"{p}.confidence",f"must be one of {sorted(CONF)}"))
  refs=c.get("evidence_refs")
  if not isinstance(refs,list) or any(not ne(x) for x in refs):e.append(dg("E_EVIDENCE",f"{p}.evidence_refs","must be a string array"))
  else:dup(refs,f"{p}.evidence_refs",e)
 if len(ids)!=len(set(ids)):e.append(dg("E_DUPLICATE","$.criteria_results","criterion ids must be unique"))
 findings=d.get("findings")
 if not isinstance(findings,list):e.append(dg("E_FINDINGS","$.findings","must be an array"));findings=[]
 for i,f in enumerate(findings):
  p=f"$.findings[{i}]"
  if not object_fields(f,{"region","locator","criterion_id","category","difference","difference_type","perceptual_magnitude","impact_severity","confidence","uncertainty_reason","evidence_refs"},p,e):continue
  for key in ("region","criterion_id","category","difference"):
   if not ne(f.get(key)):e.append(dg("E_FINDING",f"{p}.{key}","must be non-empty"))
  if f.get("difference_type") not in DIFF_TYPES:e.append(dg("E_FINDING",f"{p}.difference_type",f"must be one of {sorted(DIFF_TYPES)}"))
  if f.get("perceptual_magnitude") not in MAGNITUDE:e.append(dg("E_FINDING",f"{p}.perceptual_magnitude",f"must be one of {sorted(MAGNITUDE)}"))
  if f.get("impact_severity") not in SEVERITY:e.append(dg("E_FINDING",f"{p}.impact_severity",f"must be one of {sorted(SEVERITY)}"))
  if f.get("confidence") not in CONF:e.append(dg("E_FINDING",f"{p}.confidence",f"must be one of {sorted(CONF)}"))
  if "uncertainty_reason" in f and not ne(f.get("uncertainty_reason")):e.append(dg("E_FINDING",f"{p}.uncertainty_reason","must be non-empty when present"))
  refs=f.get("evidence_refs")
  if not isinstance(refs,list) or any(not ne(x) for x in refs):e.append(dg("E_FINDING_EVIDENCE",f"{p}.evidence_refs","must be a string array"))
  else:dup(refs,f"{p}.evidence_refs",e)
  _locator(f,p,e)
 meas=d.get("supplemental_measurements")
 if not isinstance(meas,list):e.append(dg("E_MEASUREMENTS","$.supplemental_measurements","must be an array"));meas=[]
 for i,m in enumerate(meas):
  p=f"$.supplemental_measurements[{i}]"
  if not object_fields(m,{"method","version","intended_property","criterion_id","scope","value","threshold","policy_identity","outcome","evidence_ref"},p,e):continue
  for key in ("method","intended_property","scope","evidence_ref"):
   if not ne(m.get(key)):e.append(dg("E_MEASUREMENT",f"{p}.{key}","must be non-empty"))
  if "version" in m and not ne(m.get("version")):e.append(dg("E_MEASUREMENT",f"{p}.version","must be non-empty when present"))
  if "criterion_id" in m and not ne(m.get("criterion_id")):e.append(dg("E_MEASUREMENT",f"{p}.criterion_id","must be non-empty when present"))
  if m.get("outcome") not in {"pass","fail","informational"}:e.append(dg("E_MEASUREMENT",f"{p}.outcome","must be pass, fail, or informational"))
  if "threshold" in m and not ne(m.get("policy_identity")):e.append(dg("E_MEASUREMENT_POLICY",f"{p}.policy_identity","thresholded measurement requires policy_identity"))
 for key in ("evidence_refs","uncertainty_reasons","limitations"):
  v=d.get(key)
  if not isinstance(v,list) or any(not ne(x) for x in v):e.append(dg("E_LIST",f"$.{key}","must be a string array"))
  else:dup(v,f"$.{key}",e)
 rec=d.get("recapture")
 if object_fields(rec,{"required","reason"},"$.recapture",e):
  if not isinstance(rec.get("required"),bool):e.append(dg("E_RECAPTURE","$.recapture.required","must be boolean"))
  if not isinstance(rec.get("reason"),str):e.append(dg("E_RECAPTURE","$.recapture.reason","must be a string"))
 pd=d.get("policy_decision")
 if object_fields(pd,{"outcome","reasons"},"$.policy_decision",e):
  if pd.get("outcome") not in VERDICTS:e.append(dg("E_POLICY_DECISION","$.policy_decision.outcome",f"must be one of {sorted(VERDICTS)}"))
  if not nonempty_list(pd.get("reasons")):e.append(dg("E_POLICY_DECISION","$.policy_decision.reasons","must be a non-empty string array"))
 return e

def _capture_relation(req):
 state=req.get("intended_state",{})
 if ne(state.get("reference")) and ne(state.get("candidate")) and state.get("reference")!=state.get("candidate"):return "mismatched"
 cap=req.get("capture_context",{});keys=cap.get("comparison_keys",[]);rf=cap.get("reference_facts",{});cf=cap.get("candidate_facts",{})
 unknown=False
 if isinstance(keys,list):
  for key in keys:
   if key not in rf or key not in cf:unknown=True;continue
   if rf.get(key)!=cf.get(key):return "mismatched"
 return "unknown" if unknown else "compatible"

def cross_v2(result,req):
 e=[]
 if req is None:
  return [dg("E_REQUEST_REQUIRED","$","v2 result validation requires --request with perceptual-review-request/v2")]
 re=request_v2(req)
 if re:
  for item in re:e.append(dg("E_REQUEST_INVALID",item.get("path","$"),item.get("message","request is invalid")))
  return e
 if req.get("contract")!="perceptual-review-request/v2":return [dg("E_REQUEST_CONTRACT","$.contract","v2 result requires perceptual-review-request/v2")]
 expected=ident(req)
 if result.get("request_digest")!=expected:e.append(dg("E_REQUEST_DIGEST","$.request_digest",f"must equal canonical SHA-256 of request: {expected}"))
 bindings={
  "review_id":req.get("review_id"),"reference_identity":req.get("reference",{}).get("identity"),"candidate_identity":req.get("candidate",{}).get("identity"),
  "rubric_identity":req.get("rubric",{}).get("identity"),"gate_policy_identity":req.get("gate_policy",{}).get("identity"),"evaluator_protocol_identity":req.get("evaluator_protocol",{}).get("identity")}
 for field,expected_value in bindings.items():
  if result.get(field)!=expected_value:e.append(dg("E_BINDING",f"$.{field}",f"must match request value {expected_value!r}"))
 relation=_capture_relation(req)
 if result.get("state_alignment")=="matched" and relation in {"mismatched","unknown"}:e.append(dg("E_CAPTURE_ALIGNMENT","$.state_alignment",f"cannot be matched when declared capture/state relation is {relation}"))
 criteria=req.get("rubric",{}).get("criteria",[]);crit={c.get("id"):c for c in criteria if isinstance(c,dict) and ne(c.get("id"))};required={cid for cid,c in crit.items() if c.get("required") is True}
 cres=result.get("criteria_results",[]);byid={c.get("criterion_id"):c for c in cres if isinstance(c,dict) and ne(c.get("criterion_id"))}
 for cid in byid:
  if cid not in crit:e.append(dg("E_CRITERION_UNKNOWN","$.criteria_results",f"criterion {cid!r} is not in request rubric"))
 verdict=result.get("verdict");alignment=result.get("state_alignment");executed=result.get("review_executed")
 if verdict in {"pass","fail"}:
  if alignment!="matched" or executed is not True:e.append(dg("E_VERDICT_STATE","$.verdict","pass/fail require state_alignment=matched and review_executed=true"))
  missing=sorted(required-set(byid))
  if missing:e.append(dg("E_REQUIRED_CRITERION","$.criteria_results",f"missing required criteria: {missing}"))
 policy=req.get("gate_policy",{});minimum=CONF_RANK.get(policy.get("minimum_confidence"),0)
 if verdict in {"pass","fail"}:
  for cid in sorted(required & set(byid)):
   row=byid[cid]
   if row.get("status") in {"inconclusive","not-reviewed"}:e.append(dg("E_POLICY_CRITERION","$.criteria_results",f"required criterion {cid!r} is not conclusively reviewed"))
   if CONF_RANK.get(row.get("confidence"),-1)<minimum:e.append(dg("E_POLICY_CONFIDENCE","$.criteria_results",f"required criterion {cid!r} is below minimum confidence"))
   if policy.get("require_required_criterion_evidence") and not row.get("evidence_refs"):e.append(dg("E_CRITERION_EVIDENCE","$.criteria_results",f"required criterion {cid!r} requires evidence"))
  if not result.get("evidence_refs"):e.append(dg("E_EVIDENCE","$.evidence_refs","pass/fail require global evidence refs"))
  trials=result.get("trial_count")
  if not isinstance(trials,int) or trials<policy.get("required_trials",1):e.append(dg("E_POLICY_TRIALS","$.trial_count",f"requires at least {policy.get('required_trials',1)} trial(s)"))
  if policy.get("require_agreement") and result.get("agreement")!="agreement":e.append(dg("E_POLICY_AGREEMENT","$.agreement","pass/fail require agreement under the frozen gate policy"))
  proto=req.get("evaluator_protocol",{})
  if proto.get("order_swap_required") and result.get("order_swap_performed") is not True:e.append(dg("E_PROTOCOL_ORDER_SWAP","$.order_swap_performed","required evaluator protocol order swap was not recorded"))
 findings=result.get("findings",[]);blocking=set(policy.get("blocking_severities",[]));medium=0;fail_trigger=False
 for i,f in enumerate(findings if isinstance(findings,list) else []):
  if not isinstance(f,dict):continue
  cid=f.get("criterion_id");c=crit.get(cid)
  if c is None:e.append(dg("E_FINDING_CRITERION",f"$.findings[{i}].criterion_id",f"criterion {cid!r} is not in request rubric"))
  elif f.get("category")!=c.get("category"):e.append(dg("E_FINDING_CRITERION",f"$.findings[{i}].category",f"must equal rubric category {c.get('category')!r}"))
  if policy.get("require_finding_evidence") and not f.get("evidence_refs"):e.append(dg("E_FINDING_EVIDENCE",f"$.findings[{i}].evidence_refs","finding requires evidence under gate policy"))
  if verdict in {"pass","fail"} and CONF_RANK.get(f.get("confidence"),-1)<minimum:e.append(dg("E_POLICY_CONFIDENCE",f"$.findings[{i}].confidence","finding is below minimum confidence for pass/fail"))
  sev=f.get("impact_severity")
  if sev in blocking:fail_trigger=True
  if sev=="medium":medium+=1
 if verdict=="pass":
  if fail_trigger:e.append(dg("E_POLICY_BLOCKING","$.findings","pass is forbidden by a blocking finding severity"))
  if medium>policy.get("max_medium_findings",0):e.append(dg("E_POLICY_MEDIUM","$.findings",f"pass allows at most {policy.get('max_medium_findings',0)} medium findings"))
  for cid in required:
   if cid in byid and byid[cid].get("status")!="pass":e.append(dg("E_POLICY_CRITERION","$.criteria_results",f"pass requires required criterion {cid!r} status=pass"))
 if verdict=="fail":
  if any(isinstance(c,dict) and c.get("status")=="fail" for c in cres):fail_trigger=True
  if medium>policy.get("max_medium_findings",0):fail_trigger=True
  if not fail_trigger:e.append(dg("E_FAIL_BASIS","$.verdict","fail requires a failed criterion or policy-triggering finding"))
 if verdict=="invalid":
  if alignment!="mismatched":e.append(dg("E_INVALID_STATE","$.verdict","invalid requires state_alignment=mismatched"))
  rec=result.get("recapture",{})
  if not isinstance(rec,dict) or rec.get("required") is not True or not ne(rec.get("reason")):e.append(dg("E_RECAPTURE","$.recapture","invalid requires recapture.required=true and a non-empty reason"))
 if verdict in {"blocked","inconclusive"} and not (result.get("uncertainty_reasons") or result.get("limitations")):e.append(dg("E_UNCERTAINTY_REASON","$","blocked/inconclusive requires uncertainty_reasons or limitations"))
 pd=result.get("policy_decision",{})
 if isinstance(pd,dict) and pd.get("outcome")!=verdict:e.append(dg("E_POLICY_DECISION","$.policy_decision.outcome","must equal verdict"))
 for i,m in enumerate(result.get("supplemental_measurements",[]) if isinstance(result.get("supplemental_measurements"),list) else []):
  if not isinstance(m,dict):continue
  cid=m.get("criterion_id")
  if cid is not None and cid not in crit:e.append(dg("E_MEASUREMENT_CRITERION",f"$.supplemental_measurements[{i}].criterion_id",f"criterion {cid!r} is not in request rubric"))
  if "threshold" in m:
   if not ne(m.get("policy_identity")):e.append(dg("E_MEASUREMENT_POLICY",f"$.supplemental_measurements[{i}].policy_identity","thresholded measurement requires policy identity"))
   elif m.get("policy_identity")!=policy.get("identity"):e.append(dg("E_MEASUREMENT_POLICY",f"$.supplemental_measurements[{i}].policy_identity","must match request gate policy identity"))
 return e

def validate(d:Any,request:Any|None=None):
 if not isinstance(d,dict):return {"validator":"perceptual-artifact-validator/v2","status":"fail","contract":None,"artifact_sha256":None,"request_sha256":ident(request) if isinstance(request,dict) else None,"errors":[dg("E_ROOT","$","must be object")],"warnings":[]}
 c=d.get("contract")
 if c=="perceptual-review-request/v1":e=request_v1(d)
 elif c=="perceptual-review-result/v1":e=result_v1(d)
 elif c=="perceptual-review-request/v2":e=request_v2(d)
 elif c=="perceptual-review-result/v2":
  e=result_v2_local(d);e.extend(cross_v2(d,request))
 else:e=[dg("E_CONTRACT","$.contract","must be a supported perceptual-review request/result contract (v1 or v2)")]
 return {"validator":"perceptual-artifact-validator/v2","status":"pass" if not e else "fail","contract":c,"artifact_sha256":ident(d),"request_sha256":ident(request) if isinstance(request,dict) else None,"errors":e,"warnings":[]}

def main():
 ap=argparse.ArgumentParser();ap.add_argument("artifact");ap.add_argument("--request");ap.add_argument("--json",dest="out");a=ap.parse_args()
 try:
  data=json.loads(Path(a.artifact).read_text(encoding="utf-8"));request=json.loads(Path(a.request).read_text(encoding="utf-8")) if a.request else None;r=validate(data,request)
 except Exception as x:r={"validator":"perceptual-artifact-validator/v2","status":"fail","contract":None,"artifact_sha256":None,"request_sha256":None,"errors":[dg("E_PARSE","$",str(x))],"warnings":[]}
 s=json.dumps(r,indent=2,ensure_ascii=False)+"\n";print(s,end="")
 if a.out:Path(a.out).write_text(s,encoding="utf-8")
 return 0 if r["status"]=="pass" else 1
if __name__=="__main__":raise SystemExit(main())
