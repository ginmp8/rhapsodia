#!/usr/bin/env python3
"""Validate the canonical Prompt Architect scenario-suite v2 contract."""
from __future__ import annotations
import argparse, json, re
from pathlib import Path

TYPES={"should_activate","should_not_activate","ambiguous","edge_case","regression","adversarial"}
GROUPS={"activation","non-activation","ambiguous","boundary","adversarial","holdout"}
ROUTES={"activate","do-not-activate","conditional","activate-constrained","split-handoff","reject-scope-weakening","reject-fabricated-evidence","reject-ownership-expansion"}
CONTRACT_ID=re.compile(r"^[A-Z]{2,5}-\d{3}$")


def validate(data:dict)->list[str]:
    errors=[]
    if data.get("schema_version") != 2: errors.append("schema_version must be 2")
    if not isinstance(data.get("suite_version"),str) or not data["suite_version"].strip(): errors.append("suite_version must be a non-empty string")
    for key in ("suite_id","target_identity","status"):
        if not isinstance(data.get(key),str) or not data[key].strip(): errors.append(f"{key} must be a non-empty string")
    contracts=data.get("contracts")
    if not isinstance(contracts,dict) or not contracts: errors.append("contracts must be a non-empty object")
    else:
        for cid,desc in contracts.items():
            if not CONTRACT_ID.fullmatch(str(cid)): errors.append(f"invalid contract id: {cid}")
            if not isinstance(desc,str) or not desc.strip(): errors.append(f"contract {cid} description must be non-empty")
    scenarios=data.get("scenarios")
    if not isinstance(scenarios,list) or not scenarios:
        errors.append("scenarios must be a non-empty list"); return errors
    ids=set()
    for i,s in enumerate(scenarios):
        p=f"scenarios[{i}]"
        if not isinstance(s,dict): errors.append(f"{p} must be an object"); continue
        sid=s.get("id")
        if not isinstance(sid,str) or not sid.strip(): errors.append(f"{p}.id must be non-empty")
        elif sid in ids: errors.append(f"duplicate scenario id: {sid}")
        else: ids.add(sid)
        if s.get("type") not in TYPES: errors.append(f"{p}.type is invalid")
        if s.get("group") not in GROUPS: errors.append(f"{p}.group is invalid")
        if s.get("expected_route") not in ROUTES: errors.append(f"{p}.expected_route is invalid")
        for key in ("prompt","expected_behavior"):
            if not isinstance(s.get(key),str) or not s[key].strip(): errors.append(f"{p}.{key} must be non-empty")
        ac=s.get("acceptance_criteria")
        if not isinstance(ac,list) or not ac or any(not isinstance(x,str) or not x.strip() for x in ac): errors.append(f"{p}.acceptance_criteria must be a non-empty string list")
        cids=s.get("contract_ids")
        if not isinstance(cids,list) or not cids: errors.append(f"{p}.contract_ids must be non-empty")
        else:
            for cid in cids:
                if not isinstance(cid,str) or not CONTRACT_ID.fullmatch(cid): errors.append(f"{p}.contract_ids contains invalid id")
                elif isinstance(contracts,dict) and cid not in contracts: errors.append(f"{p}.contract_ids references unknown {cid}")
    return errors


def main()->int:
    ap=argparse.ArgumentParser(description="Validate a Prompt Architect scenario suite v2.")
    ap.add_argument("suite")
    args=ap.parse_args()
    try: data=json.loads(Path(args.suite).read_text(encoding="utf-8"))
    except Exception as exc:
        print(json.dumps({"status":"fail","format":"unknown","errors":[f"invalid JSON: {exc}"],"warnings":[]},indent=2)); return 1
    errors=validate(data)
    print(json.dumps({"status":"fail" if errors else "pass","format":"v2","errors":errors,"warnings":[]},indent=2,ensure_ascii=False,sort_keys=True))
    return 1 if errors else 0
if __name__ == "__main__": raise SystemExit(main())
