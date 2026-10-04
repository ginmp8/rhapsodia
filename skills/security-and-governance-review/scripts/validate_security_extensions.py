#!/usr/bin/env python3
"""Validate optional security/governance report extensions using stdlib only."""
from __future__ import annotations
import argparse, json
from pathlib import Path

EFFECTIVENESS={"declared","statically-present","behaviorally-demonstrated","runtime-observed"}
LAYERS={"structural","behavioral","runtime","external_current"}
ACTIONS={"read","write","execute","delete","send","publish","schedule","deploy","approve","delegate"}
COMPONENT_KINDS={"agent","model","prompt","policy","tool","mcp-server","connector","plugin","dependency","memory-store","retrieval-store","runtime-config"}
MAPPING_TYPES={"coverage","threat-technique","control-family","regulatory-reference"}
CLAIM_LEVELS={"mapped-only","supports-assessment"}
STRONG_COMPLIANCE={"compliant","non-compliant"}


def validate(data: object) -> list[str]:
    if not isinstance(data, dict): return ["report root must be an object"]
    errors=[]
    controls=data.get("control_evidence",{}).get("controls",[]) if isinstance(data.get("control_evidence",{}),dict) else []
    seen=set()
    for i,c in enumerate(controls):
        if not isinstance(c,dict): errors.append(f"control_evidence.controls[{i}] must be object"); continue
        cid=c.get("id")
        if not cid or cid in seen: errors.append(f"control_evidence.controls[{i}] id missing/duplicate")
        seen.add(cid)
        eff=c.get("effectiveness")
        if eff not in EFFECTIVENESS: errors.append(f"control {cid} invalid effectiveness")
        refs=c.get("evidence_refs",[])
        layers={r.get("layer") for r in refs if isinstance(r,dict)}
        if any(layer not in LAYERS for layer in layers): errors.append(f"control {cid} invalid evidence layer")
        if eff=="behaviorally-demonstrated" and "behavioral" not in layers: errors.append(f"control {cid} behaviorally-demonstrated requires behavioral evidence")
        if eff=="runtime-observed" and "runtime" not in layers: errors.append(f"control {cid} runtime-observed requires runtime evidence")
    inv=data.get("agent_inventory")
    if inv is not None:
        if not isinstance(inv,dict): errors.append("agent_inventory must be object")
        else:
            ids=set()
            for i,c in enumerate(inv.get("components",[])):
                if not isinstance(c,dict): errors.append(f"agent_inventory.components[{i}] must be object"); continue
                cid=c.get("id"); kind=c.get("kind"); ident=c.get("identity")
                if not cid or cid in ids: errors.append(f"agent_inventory.components[{i}] id missing/duplicate")
                ids.add(cid)
                if kind not in COMPONENT_KINDS: errors.append(f"component {cid} invalid kind")
                if not isinstance(ident,dict) or not any(ident.get(k) for k in ("version","sha256","locator","declared")): errors.append(f"component {cid} requires identity")
    auth=data.get("authority_boundaries",{}).get("records",[]) if isinstance(data.get("authority_boundaries",{}),dict) else []
    for i,r in enumerate(auth):
        if not isinstance(r,dict): errors.append(f"authority_boundaries.records[{i}] must be object"); continue
        if r.get("action") not in ACTIONS: errors.append(f"authority record {i} invalid action")
        for key in ("actor","resource_scope","authorization_source","approval","audit_receipt","failure_behavior","rollback_containment"):
            if not r.get(key): errors.append(f"authority record {i} missing {key}")
    for i,m in enumerate(data.get("framework_mappings",[]) or []):
        if not isinstance(m,dict): errors.append(f"framework_mappings[{i}] must be object"); continue
        for key in ("framework","source_locator","source_version_or_date","mapping_type","claim_level"):
            if not m.get(key): errors.append(f"framework_mappings[{i}] missing {key}")
        if m.get("mapping_type") not in MAPPING_TYPES: errors.append(f"framework_mappings[{i}] invalid mapping_type")
        if m.get("claim_level") not in CLAIM_LEVELS: errors.append(f"framework_mappings[{i}] invalid claim_level")
        if "severity_override" in m or "classification_override" in m: errors.append(f"framework_mappings[{i}] must not override SGR severity/classification")
    cc=data.get("compliance_context")
    if cc is not None:
        if not isinstance(cc,dict): errors.append("compliance_context must be object")
        elif cc.get("conclusion") in STRONG_COMPLIANCE:
            for key in ("jurisdiction","actor_role","provision_or_policy","effective_date_or_version","authoritative_source"):
                if not cc.get(key): errors.append(f"strong compliance conclusion requires {key}")
    return errors


def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument("report"); ap.add_argument("--json",dest="json_output")
    args=ap.parse_args()
    try: data=json.loads(Path(args.report).read_text(encoding="utf-8")); errors=validate(data)
    except Exception as exc: errors=[f"invalid JSON: {exc}"]
    result={"status":"fail" if errors else "pass","errors":errors}
    text=json.dumps(result,indent=2,sort_keys=True)+"\n"
    if args.json_output: Path(args.json_output).write_text(text,encoding="utf-8")
    else: print(text,end="")
    return 1 if errors else 0
if __name__=="__main__": raise SystemExit(main())
