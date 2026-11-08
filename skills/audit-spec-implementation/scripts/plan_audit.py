#!/usr/bin/env python3
"""Deterministic proposal for spec-conformance specialist routing.

Never invokes a skill or executes a repository. A planned delegate is not proof
that the host loaded or ran it; the coordinator must record actual invocation.
"""
import argparse
import json
import sys
from pathlib import Path

STAGE_NAMES = ("criteria", "implementation", "causal", "verification", "parity")
REGISTRY = Path(__file__).resolve().parents[1] / "references" / "skill-dispatch.json"


def plan(request, registry=None):
    if not isinstance(request, dict):
        raise ValueError("request must be an object")
    if registry is None:
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    stages = registry["stages"]
    if [s["id"] for s in stages] != list(STAGE_NAMES):
        raise ValueError("unexpected stage registry identity/order")
    selected = request.get("selected_stages", list(STAGE_NAMES))
    if not isinstance(selected, list) or not selected or len(set(selected)) != len(selected) or any(s not in STAGE_NAMES for s in selected):
        raise ValueError("selected_stages must contain unique, known stage names")
    available = request.get("available_skills", [])
    unusable = request.get("unusable_skills", [])
    risk = request.get("risk_factors", [])
    if any(not isinstance(x, list) or not all(isinstance(t, str) for t in x) for x in (available, unusable, risk)):
        raise ValueError("available_skills, unusable_skills, risk_factors must be string lists")
    available = set(available) - set(unusable)
    risky = set(risk) & set(registry["causal_risk_factors"])
    parity = request.get("needs_parity", False)
    if not isinstance(parity, bool):
        raise ValueError("needs_parity must be boolean")
    authorization = request.get("authorized_test_execution", False)
    if not isinstance(authorization, bool):
        raise ValueError("authorized_test_execution must be boolean")
    missing_identity = [key for key in ("base_sha", "head_sha") if not isinstance(request.get(key), str) or not request[key].strip()]
    output = {
        "schema_version": "audit-plan/v1",
        "target": {"base_sha": request.get("base_sha"), "head_sha": request.get("head_sha")},
        "status": "blocked" if missing_identity else "planned",
        "issues": [f"Missing frozen {name}: no conclusion or source-specific proof allowed" for name in missing_identity],
        "authorized_test_execution": authorization,
        "stages": [],
        "notice": "This is a routing proposal only; no external skill was invoked and no test was executed."
    }
    for stage in stages:
        sid = stage["id"]
        required = sid in selected and (stage["required"] or (sid == "causal" and bool(risky)) or (sid == "parity" and parity))
        external = next((n for n in stage["external"] if n in available), None)
        if sid not in selected or (not required):
            route = {"stage": sid, "status": "skipped", "delegate": None, "route_type": "not-applicable", "actually_invoked": False}
        elif missing_identity:
            route = {"stage": sid, "status": "blocked", "delegate": None, "route_type": "blocked", "actually_invoked": False}
        else:
            route = {"stage": sid, "status": "planned", "delegate": external or stage["adapter"],
                     "route_type": "external-skill-proposed" if external else "local-adapter-proposed", "actually_invoked": False}
        if sid == "verification":
            route["test_execution_permitted"] = authorization
            route["test_execution_observed"] = False
        output["stages"].append(route)
    if "criteria" not in selected:
        output["issues"].append("Partial stage selection; no full conformance verdict is permitted")
    if risk and set(risk) - set(registry["causal_risk_factors"]):
        output["issues"].append("Unrecognized risk factors retained for human review")
    return output


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("request", help="JSON request with immutable target identity and available skill IDs")
    ap.add_argument("--output", help="Optional output file; stdout otherwise")
    args = ap.parse_args(argv)
    try:
        document = json.loads(Path(args.request).read_text(encoding="utf-8"))
        result = plan(document)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as ex:
        print(f"Invalid audit planning input: {ex}", file=sys.stderr)
        return 2
    text = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0 if result["status"] == "planned" else 3


if __name__ == "__main__":
    sys.exit(main())
