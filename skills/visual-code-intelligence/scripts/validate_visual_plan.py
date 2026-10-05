#!/usr/bin/env python3
import argparse, json, sys
from pathlib import Path

CURRENT_KINDS = {"source-code", "config-schema", "test", "runtime", "current-spec", "current-doc", "diff"}
HISTORICAL_KINDS = {"issue", "pr", "commit", "trace"}
INTENT_KINDS = {"user-requirement", "current-spec", "issue", "pr"}
VALID_MODES = {"change-review", "system-explanation", "code-archaeology", "visual-scratchpad"}
VALID_AUDIENCE = {"overview", "technical", "deep-dive"}
VALID_VISUALS = {"sequence", "flowchart", "state", "er", "architecture", "timeline", "change-map", "none"}
VALID_EVIDENCE = CURRENT_KINDS | HISTORICAL_KINDS | {"user-requirement", "other"}
VALID_CLAIM_KINDS = {"current-behavior", "requested-intent", "rationale", "risk", "invariant"}
VALID_CLASS = {"observed", "historical", "inferred"}
LENS_KINDS = {"implementation", "tests", "docs", "generated-lock", "config-build", "fixtures-snapshots", "rename-move", "formatting", "imports"}


def err(errors, code, message): errors.append({"code": code, "message": message})

def validate(plan):
    errors, warnings = [], []
    if plan.get("version") != "visual-code-intelligence/1": err(errors,"version","version must be visual-code-intelligence/1")
    if plan.get("mode") not in VALID_MODES: err(errors,"mode","invalid mode")
    if plan.get("audience") not in VALID_AUDIENCE: err(errors,"audience","invalid audience")
    scope = plan.get("scope") or {}
    if not isinstance(scope.get("target"), str) or not scope.get("target").strip(): err(errors,"scope/target","scope.target is required")

    evidence = plan.get("evidence") or []
    e_by_id = {}
    for e in evidence:
        eid = e.get("id")
        if not isinstance(eid,str) or not eid.startswith("E") or not eid[1:].isdigit(): err(errors,"evidence/id",f"invalid evidence id: {eid}"); continue
        if eid in e_by_id: err(errors,"evidence/duplicate",f"duplicate evidence id: {eid}")
        if e.get("kind") not in VALID_EVIDENCE: err(errors,"evidence/kind",f"invalid evidence kind for {eid}")
        if not isinstance(e.get("locator"),str) or not e.get("locator").strip(): err(errors,"evidence/locator",f"missing locator for {eid}")
        e_by_id[eid]=e

    claims = plan.get("claims") or []
    seen_claims=set()
    for c in claims:
        cid=c.get("id")
        if not isinstance(cid,str) or not cid.startswith("C") or not cid[1:].isdigit(): err(errors,"claim/id",f"invalid claim id: {cid}"); continue
        if cid in seen_claims: err(errors,"claim/duplicate",f"duplicate claim id: {cid}")
        seen_claims.add(cid)
        if c.get("kind") not in VALID_CLAIM_KINDS: err(errors,"claim/kind",f"invalid claim kind for {cid}")
        if c.get("classification") not in VALID_CLASS: err(errors,"claim/classification",f"invalid classification for {cid}")
        refs=c.get("evidence_ids") or []
        if not refs: err(errors,"claim/evidence",f"{cid} has no evidence")
        missing=[x for x in refs if x not in e_by_id]
        if missing: err(errors,"claim/evidence-ref",f"{cid} references missing evidence: {missing}")
        kinds={e_by_id[x]["kind"] for x in refs if x in e_by_id}
        if c.get("kind") in {"current-behavior","risk","invariant"} and c.get("classification") != "historical" and not (kinds & CURRENT_KINDS):
            err(errors,"claim/current-evidence",f"{cid} needs current evidence")
        if c.get("kind") == "requested-intent" and not (kinds & INTENT_KINDS):
            err(errors,"claim/intent-evidence",f"{cid} needs requirement/spec/issue/PR evidence")
        if c.get("classification") == "historical" and not (kinds & HISTORICAL_KINDS):
            err(errors,"claim/historical-evidence",f"{cid} is historical but lacks historical evidence")
        if c.get("kind") == "rationale" and c.get("classification") == "observed" and not (kinds & HISTORICAL_KINDS):
            warnings.append({"code":"claim/rationale-observed","message":f"{cid} observed rationale lacks explicit historical/decision evidence; consider inferred"})

    visuals=plan.get("visuals") or []
    if len(visuals) > 2: err(errors,"visual/count","at most two visuals are allowed by default")
    roles=[]
    for v in visuals:
        if v.get("type") not in VALID_VISUALS: err(errors,"visual/type",f"invalid visual type: {v.get('type')}")
        if v.get("role") not in {"primary","secondary"}: err(errors,"visual/role",f"invalid visual role: {v.get('role')}")
        roles.append(v.get("role"))
    if visuals and roles.count("primary") != 1: err(errors,"visual/primary","exactly one primary visual is required when visuals exist")
    if roles.count("secondary") > 1: err(errors,"visual/secondary","at most one secondary visual is allowed")

    changed=plan.get("changed_files") or []
    lenses=plan.get("file_lenses") or []
    if plan.get("mode") == "change-review" and changed:
        assigned=[]
        for lens in lenses:
            if lens.get("kind") not in LENS_KINDS: err(errors,"lens/kind",f"invalid lens kind: {lens.get('kind')}")
            assigned.extend(lens.get("paths") or [])
        missing=sorted(set(changed)-set(assigned)); extra=sorted(set(assigned)-set(changed))
        dup=sorted({p for p in assigned if assigned.count(p)>1})
        if missing: err(errors,"lens/missing",f"unassigned changed files: {missing}")
        if extra: err(errors,"lens/extra",f"lens paths not in changed_files: {extra}")
        if dup: err(errors,"lens/duplicate",f"files assigned more than once: {dup}")

    return errors,warnings

def main():
    p=argparse.ArgumentParser(description="Validate Visual Code Intelligence visual plans.")
    p.add_argument("plan")
    p.add_argument("--json", action="store_true", dest="as_json")
    args=p.parse_args()
    try:
        plan=json.loads(Path(args.plan).read_text(encoding="utf-8"))
    except Exception as ex:
        result={"status":"fail","errors":[{"code":"parse","message":str(ex)}],"warnings":[]}
        print(json.dumps(result,indent=2) if args.as_json else f"FAIL parse: {ex}")
        return 2
    errors,warnings=validate(plan)
    result={"status":"pass" if not errors else "fail","errors":errors,"warnings":warnings}
    if args.as_json: print(json.dumps(result,indent=2,sort_keys=True))
    else:
        print(result["status"].upper())
        for x in errors: print(f"ERROR {x['code']}: {x['message']}")
        for x in warnings: print(f"WARN {x['code']}: {x['message']}")
    return 0 if not errors else 1

if __name__ == "__main__":
    raise SystemExit(main())
