#!/usr/bin/env python3
"""Validate a Nomia canonical governance record and generate deterministic projections."""
from __future__ import annotations
import argparse, json, sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any
try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required to project Nomia governance views") from exc

PROFILES={"unknown","quick","standard","governed"}
LIFECYCLE={"unknown","intake","triage","commit","track","decide","close"}
GOV_STATES={"unknown","intake","triage","planned","ready","in_progress","blocked","validating","releasable","released","closed","canceled","superseded"}
TECH_STATES={"unknown","not_started","planned","ready","in_progress","blocked","passed","failed","complete"}
RELEASE_STATES={"unknown","not_released","releasable","released","closed","canceled","superseded"}


def json_safe(value: Any) -> Any:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [json_safe(v) for v in value]
    return value


def missing(v: Any) -> bool:
    return v is None or v == "" or v == "unknown" or v == []

def dotted(data: dict[str,Any], path: str, default: Any=None) -> Any:
    cur: Any=data
    for part in path.split('.'):
        if not isinstance(cur,dict): return default
        cur=cur.get(part,default)
    return cur

def validate_record(data: dict[str,Any]) -> tuple[list[str],list[str]]:
    errors=[]; warnings=[]
    if not isinstance(data,dict): return ["record must be a YAML mapping"],warnings
    for key in ("request","ownership","planning","priority","status","blockers","risks","links"):
        if key not in data: errors.append(f"missing canonical section: {key}")
    gov=data.get("governance") or {}
    if gov:
        if gov.get("profile","unknown") not in PROFILES: errors.append("governance.profile is invalid")
        if gov.get("lifecycle","unknown") not in LIFECYCLE: errors.append("governance.lifecycle is invalid")
        if gov.get("status","unknown") not in GOV_STATES: errors.append("governance.status is invalid")
    tech=data.get("technical_state") or {}
    for dim in ("planning","execution","validation"):
        item=tech.get(dim) or {}
        state=item.get("state","unknown")
        if state not in TECH_STATES: errors.append(f"technical_state.{dim}.state is invalid")
        if state != "unknown" and missing(item.get("source")): errors.append(f"technical_state.{dim}.source is required for non-unknown state")
    release=data.get("release") or {}
    rstate=release.get("state","unknown")
    if rstate not in RELEASE_STATES: errors.append("release.state is invalid")
    if rstate == "released" and not release.get("evidence"): errors.append("release.evidence is required when released")
    prov=data.get("provenance") or {}
    if prov and not isinstance(prov.get("facts",{}),dict): errors.append("provenance.facts must be a mapping")
    for field in ("request.requester","ownership.owner","planning.target_date","status.updated_at"):
        if missing(dotted(data,field)): warnings.append(f"unknown fact: {field}")
    return errors,warnings

def evidence_age(data: dict[str,Any], today: date) -> tuple[list[str],list[str]]:
    stale=[]; conflicts=[]
    facts=dotted(data,"provenance.facts",{}) or {}
    for field,meta in facts.items():
        if not isinstance(meta,dict): continue
        if meta.get("conflict"): conflicts.append(field)
        observed=meta.get("observed_at"); max_age=meta.get("max_age_days")
        if observed and isinstance(max_age,int):
            try:
                age=(today-date.fromisoformat(str(observed)[:10])).days
                if age>max_age: stale.append(field)
            except ValueError: conflicts.append(f"{field}:invalid_observed_at")
    return sorted(stale),sorted(conflicts)

def canonical_state(data: dict[str,Any]) -> str:
    return str(dotted(data,"governance.status") or dotted(data,"status.state") or "unknown")

def safe_completion(data: dict[str,Any]) -> dict[str,str]:
    return {
      "planning": str(dotted(data,"technical_state.planning.state") or "unknown"),
      "execution": str(dotted(data,"technical_state.execution.state") or "unknown"),
      "validation": str(dotted(data,"technical_state.validation.state") or "unknown"),
      "release": str(dotted(data,"release.state") or "unknown"),
    }

def list_summary(items: Any, field: str="summary") -> list[str]:
    out=[]
    for item in items or []:
        if isinstance(item,dict): out.append(str(item.get(field) or item.get("id") or "unknown"))
        elif item not in (None,""): out.append(str(item))
    return out

def build_views(data: dict[str,Any], source: str, generated_at: str) -> dict[str,Any]:
    today=date.fromisoformat(generated_at[:10]); stale,conflicts=evidence_age(data,today)
    state=canonical_state(data); owner=dotted(data,"ownership.owner") or "unknown"; target=dotted(data,"planning.target_date") or "unknown"
    blockers=list_summary(data.get("blockers")); risks=list_summary(data.get("risks")); deps=list_summary(data.get("dependencies"),"summary")
    completion=safe_completion(data)
    flags=[]
    if stale: flags.append("stale="+",".join(stale))
    if conflicts: flags.append("conflict="+",".join(conflicts))
    unknown=[f for f in ("request.requester","ownership.owner","planning.target_date","status.updated_at") if missing(dotted(data,f))]
    if unknown: flags.append("unknown="+",".join(unknown))
    detail="; ".join(flags) if flags else "evidence current"
    top_issue=(blockers or risks or ["none evidenced"])[0]
    one=f"{state} | owner={owner} | target={target} | issue={top_issue} | {detail}"
    common={"authority":"canonical_projection","source":source,"generated_at":generated_at,"state":state,"owner":owner,"target_date":target,"unknown_fields":unknown,"stale_fields":stale,"conflicting_fields":conflicts,"technical_state":completion}
    operational={**common,"summary":dotted(data,"status.summary") or "unknown","blockers":blockers,"risks":risks,"dependencies":deps,"next_governance_action":dotted(data,"decision.current") or "unknown"}
    stakeholder={**common,"request":dotted(data,"request.title") or "unknown","impact":dotted(data,"priority.impact") or "unknown","decision_needed":dotted(data,"decision.current") or "unknown","stakeholders":dotted(data,"ownership.stakeholders",[]) or []}
    executive={**common,"priority":dotted(data,"priority.level") or "unknown","confidence":dotted(data,"status.confidence") or "unknown","material_risks":risks,"release_state":completion["release"],"completion_claim_supported": completion["validation"]=="passed" and completion["release"] in {"released","closed"}}
    audit={**common,"record":data,"projection_rule":"deterministic-v1"}
    return {"one_line":one,"operational_summary":operational,"stakeholder_brief":stakeholder,"executive_summary":executive,"audit_record":audit}

def adapter(name: str, data: dict[str,Any], views: dict[str,Any], source: str, generated_at: str) -> dict[str,Any]:
    common={"authority":"non_authoritative_projection","format":name,"source":source,"generated_at":generated_at,"unknown_fields":views["audit_record"]["unknown_fields"],"stale_fields":views["audit_record"]["stale_fields"]}
    mapped={
      "lightweight_proposal":{"title":dotted(data,"request.title"),"rationale":dotted(data,"request.context"),"status":canonical_state(data)},
      "roadmap_item":{"title":dotted(data,"request.title"),"owner":dotted(data,"ownership.owner"),"target_date":dotted(data,"planning.target_date"),"status":canonical_state(data)},
      "status_report":views["operational_summary"],
      "decision_log":{"state":dotted(data,"decision.state"),"decision":dotted(data,"decision.current"),"changes":dotted(data,"provenance.changes",[]) or []},
      "release_note_input":{"title":dotted(data,"request.title"),"release_state":dotted(data,"release.state"),"evidence":dotted(data,"release.evidence",[]) or []},
      "spec_kit_reference":{"spec_id":data.get("spec_id"),"governance_state":canonical_state(data),"planning_reference":dotted(data,"technical_state.planning.source")},
      "openspec_reference":{"change_reference":(dotted(data,"links.external",[]) or [None])[0],"governance_state":canonical_state(data),"proposal_summary":dotted(data,"request.context")},
      "kiro_reference":{"spec_reference":data.get("spec_id"),"governance_state":canonical_state(data),"review_required":dotted(data,"governance.profile") == "governed"},
    }[name]
    represented=set(json.dumps(mapped,sort_keys=True).lower().replace('"','').split())
    canonical={"request","ownership","planning","priority","status","blockers","risks","dependencies","decision","handoffs","release","provenance","technical_state"}
    lossy=sorted(k for k in canonical if k not in represented)
    return {**common,"mapped":mapped,"lossy_fields":lossy}

def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("record")
    p.add_argument("--output-dir")
    p.add_argument("--adapter", choices=["lightweight_proposal","roadmap_item","status_report","decision_log","release_note_input","spec_kit_reference","openspec_reference","kiro_reference"])
    p.add_argument("--generated-at", default=datetime.now(timezone.utc).replace(microsecond=0).isoformat())
    args=p.parse_args(); path=Path(args.record).resolve()
    data=yaml.safe_load(path.read_text(encoding="utf-8"))
    errors,warnings=validate_record(data)
    if errors:
        for e in errors: print(f"ERROR: {e}",file=sys.stderr)
        return 1
    views=build_views(data,str(path),args.generated_at)
    payload=adapter(args.adapter,data,views,str(path),args.generated_at) if args.adapter else views
    if args.output_dir:
        out=Path(args.output_dir); out.mkdir(parents=True,exist_ok=True)
        for name,value in (payload.items() if isinstance(payload,dict) and not args.adapter else [(args.adapter or "projection",payload)]):
            (out/f"{name}.json").write_text(json.dumps(json_safe(value),indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(json_safe({"status":"pass","warnings":warnings,"output":payload}),indent=2,sort_keys=True))
    return 0
if __name__=="__main__": sys.exit(main())
