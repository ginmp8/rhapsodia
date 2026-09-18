#!/usr/bin/env python3
"""Evaluate Nomia governance transitions, metrics, confidence, risk trend, and handoffs."""
from __future__ import annotations
import argparse, json, sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from governance_contract import validate_handoff_envelope
from nomia_utils import atomic_write_text
from validate_ops import validate as validate_ops_file

try:
    import yaml
except ImportError as exc:
    raise SystemExit("PyYAML is required to evaluate Nomia governance records") from exc

TRANSITIONS={
 "unknown":{"intake","triage"}, "intake":{"triage","blocked","canceled","superseded"},
 "triage":{"planned","blocked","canceled","superseded"}, "planned":{"ready","blocked","canceled","superseded"},
 "ready":{"in_progress","blocked","canceled","superseded"}, "in_progress":{"blocked","validating","releasable","canceled","superseded"},
 "blocked":{"triage","planned","ready","in_progress","validating","releasable","canceled","superseded"},
 "validating":{"blocked","releasable","in_progress","canceled","superseded"},
 "releasable":{"released","blocked","canceled","superseded"}, "released":{"closed","canceled","superseded"},
 "closed":set(), "canceled":set(), "superseded":set()
}
SEVERITY={"unknown":0,"low":1,"medium":2,"high":3,"critical":4}
DIRECTIONS={"nomia_to_mago","mago_to_nomia","magia_to_nomia","nomia_to_stakeholder"}


def parse_time(value: Any) -> datetime|None:
    if value in (None,"","unknown"): return None
    if isinstance(value,datetime): return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value,date): return datetime(value.year,value.month,value.day,tzinfo=timezone.utc)
    text=str(value).replace("Z","+00:00")
    try:
        dt=datetime.fromisoformat(text)
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except ValueError:
        return None

def days_between(start: Any, end: Any) -> float|None:
    a=parse_time(start); b=parse_time(end)
    return round((b-a).total_seconds()/86400,3) if a and b else None

def get(data: dict[str,Any], path: str, default: Any=None) -> Any:
    cur: Any=data
    for part in path.split('.'):
        if not isinstance(cur,dict): return default
        cur=cur.get(part,default)
    return cur

def metric(value: Any, missing: list[str], evidence: list[str]) -> dict[str,Any]:
    return {"value":value,"missing_evidence":missing,"evidence":evidence}

def compute_metrics(data: dict[str,Any], as_of: datetime) -> dict[str,Any]:
    ts=data.get("timestamps") or {}; state=str(get(data,"governance.status") or get(data,"status.state") or "unknown")
    out={}
    out["intake_age_days"]=metric(days_between(ts.get("intake_at"),as_of), [] if ts.get("intake_at") else ["timestamps.intake_at"], ["timestamps.intake_at"] if ts.get("intake_at") else [])
    out["time_in_current_state_days"]=metric(days_between(ts.get("state_entered_at"),as_of), [] if ts.get("state_entered_at") else ["timestamps.state_entered_at"], ["timestamps.state_entered_at"] if ts.get("state_entered_at") else [])
    blocked=days_between(ts.get("blocked_since"),as_of) if state=="blocked" else 0.0
    out["blocked_duration_days"]=metric(blocked, [] if state!="blocked" or ts.get("blocked_since") else ["timestamps.blocked_since"], ["timestamps.blocked_since"] if ts.get("blocked_since") else [])
    target=get(data,"planning.target_date"); actual=ts.get("closed_at") or ts.get("released_at") or as_of
    out["target_date_variance_days"]=metric(days_between(target,actual), [] if target else ["planning.target_date"], ["planning.target_date"] if target else [])
    pairs={
      "decision_latency_days":("decision_requested_at","decision_at"),
      "planning_lead_time_days":("planning_started_at","planning_ready_at"),
      "execution_lead_time_days":("execution_started_at","execution_completed_at"),
      "stakeholder_response_age_days":("stakeholder_requested_at","stakeholder_responded_at")}
    for name,(a,b) in pairs.items():
        miss=[f"timestamps.{x}" for x in (a,b) if not ts.get(x)]
        out[name]=metric(days_between(ts.get(a),ts.get(b)),miss,[f"timestamps.{a}",f"timestamps.{b}"] if not miss else [])
    validation_at=get(data,"technical_state.validation.observed_at") or ts.get("validation_observed_at")
    out["validation_age_days"]=metric(days_between(validation_at,as_of),[] if validation_at else ["technical_state.validation.observed_at"],["technical_state.validation.observed_at"] if validation_at else [])
    deps=data.get("dependencies") or []
    if deps:
        score=0; exposed=[]
        for dep in deps:
            if not isinstance(dep,dict): continue
            sev=SEVERITY.get(str(dep.get("severity","unknown")),0)
            if dep.get("status") in {"blocked","at_risk","unknown"}: score+=max(1,sev); exposed.append(dep.get("id") or dep.get("summary") or "unknown")
        out["dependency_exposure"] = metric({"score":score,"exposed":exposed},[],["dependencies"])
    else: out["dependency_exposure"]=metric(None,["dependencies"],[])
    history=data.get("risk_history") or []
    if len(history)>=2:
        ordered=sorted([x for x in history if isinstance(x,dict) and parse_time(x.get("date"))],key=lambda x:parse_time(x["date"]))
        if len(ordered)>=2:
            prev=SEVERITY.get(str(ordered[-2].get("severity","unknown")),0); cur=SEVERITY.get(str(ordered[-1].get("severity","unknown")),0)
            trend="increasing" if cur>prev else "decreasing" if cur<prev else "stable"
            out["risk_trend"]=metric(trend,[],["risk_history"])
        else: out["risk_trend"]=metric(None,["two valid risk_history entries"],[])
    else: out["risk_trend"]=metric(None,["two risk_history entries"],[])
    out["delivery_confidence"]=confidence(data)
    return out

def confidence(data: dict[str,Any]) -> dict[str,Any]:
    reasons=[]; score=4
    for path in ("request.requester","ownership.owner","planning.target_date","status.updated_at"):
        if get(data,path) in (None,"","unknown"): score-=1; reasons.append(f"missing:{path}")
    state=str(get(data,"governance.status") or get(data,"status.state") or "unknown")
    if state=="blocked": score-=2; reasons.append("blocked")
    risks=data.get("risks") or []
    maxrisk=max([SEVERITY.get(str(r.get("severity","unknown")),0) for r in risks if isinstance(r,dict)] or [0])
    if maxrisk>=3: score-=2; reasons.append("high_or_critical_risk")
    facts=get(data,"provenance.facts",{}) or {}
    if any(isinstance(v,dict) and v.get("conflict") for v in facts.values()): score-=2; reasons.append("conflicting_evidence")
    label="high" if score>=4 else "medium" if score>=2 else "low" if reasons else "unknown"
    return metric(label,[],["canonical evidence completeness","blockers","risks","provenance conflicts"]+reasons)

def validate_transition(old: str,new: str) -> dict[str,Any]:
    if old not in TRANSITIONS or new not in TRANSITIONS: return {"status":"rejected","reasons":["unknown state"]}
    if new in TRANSITIONS[old]: return {"status":"accepted","reasons":[]}
    if old==new: return {"status":"accepted","reasons":["no-op transition"]}
    return {"status":"rejected","reasons":[f"transition {old}->{new} is not permitted without a new governance decision/reopen record"]}

def load_mapping(path: Path) -> dict[str,Any]:
    data=yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data,dict): raise ValueError("input must be a mapping")
    return data

def handoff_diagnostics(result: dict[str,Any]) -> dict[str,Any]:
    """Add non-authoritative, human-actionable remediation to a contract result."""
    reasons=[str(x) for x in result.get("reasons",[])]; missing=[]; remediation=[]
    for reason in reasons:
        if reason.startswith("missing "):
            field=reason.removeprefix("missing ")
            missing.append(field)
            remediation.append(f"supply {field} from its authoritative source")
        elif reason == "evidence is stale":
            remediation.append("refresh the evidence, observed_at, and freshness window before retrying")
        elif reason == "conflicting evidence":
            remediation.append("reconcile the conflicting sources and preserve the unresolved conflict until authority resolves it")
        elif "outside nomia authority" in reason:
            remediation.append("remove technical planning or execution content and route it to Mago or Magia")
        elif "legacy ULID" in reason:
            remediation.append("replace the legacy identifier with the canonical date-and-feature-key identifier from Mago")
        elif reason.startswith("invalid "):
            remediation.append(f"correct {reason.removeprefix('invalid ')} according to the typed handoff contract")
        elif "does not match" in reason:
            remediation.append("align the candidate identity with the supplied feature key and provenance")
        elif "must use" in reason:
            remediation.append("use the authority-owned canonical identity or source required by the contract")
    status=str(result.get("status","rejected"))
    if status == "accepted":
        next_action="deliver the accepted payload to the declared recipient; acceptance does not certify technical completion"
    elif status == "draft":
        next_action="preserve the draft and complete the stated readiness evidence before requesting acceptance"
    elif status in {"stale","conflicting","rejected"}:
        next_action="apply the remediation without changing authority, then re-run handoff validation"
    else:
        next_action="review the contract result before changing governance state"
    enriched=dict(result)
    enriched.update({
        "missing_fields": sorted(set(missing)),
        "remediation": list(dict.fromkeys(remediation)),
        "next_action": next_action,
        "authority_note": "Nomia validates governance transfer only; Mago owns planning and Magia owns execution evidence.",
    })
    return enriched


def validate_handoff(env: dict[str,Any], as_of: datetime) -> dict[str,Any]:
    """Validate a typed handoff and return contract-safe diagnostics."""
    return handoff_diagnostics(validate_handoff_envelope(env, as_of))

def json_safe(v: Any) -> Any:
    if isinstance(v,(date,datetime)): return v.isoformat()
    if isinstance(v,dict): return {str(k):json_safe(x) for k,x in v.items()}
    if isinstance(v,list): return [json_safe(x) for x in v]
    return v

def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("record",nargs="?")
    p.add_argument("--as-of",default=datetime.now(timezone.utc).replace(microsecond=0).isoformat())
    p.add_argument("--transition",nargs=2,metavar=("FROM","TO"))
    p.add_argument("--handoff")
    p.add_argument("--json-output")
    args=p.parse_args(); as_of=parse_time(args.as_of)
    if not as_of: print("ERROR: invalid --as-of",file=sys.stderr); return 2
    if args.transition: result=validate_transition(*args.transition)
    elif args.handoff: result=validate_handoff(load_mapping(Path(args.handoff)),as_of)
    elif args.record:
        record_path=Path(args.record).resolve(); data=load_mapping(record_path)
        if data.get("schema_version") != 2:
            result={"status":"rejected","reasons":["metrics require canonical schema_version 2; adapt legacy governance first"]}
        else:
            errors,warnings=validate_ops_file(record_path,require_canonical=True)
            result={"status":"pass","warnings":warnings,"metrics":compute_metrics(data,as_of)} if not errors else {"status":"rejected","reasons":errors}
    else: print("ERROR: record, --transition, or --handoff is required",file=sys.stderr); return 2
    text=json.dumps(json_safe(result),indent=2,sort_keys=True)+"\n"
    if args.json_output: atomic_write_text(Path(args.json_output), text)
    print(text,end="")
    return 0 if result.get("status") in {"pass", "accepted", "draft"} else 1
if __name__=="__main__": sys.exit(main())
