#!/usr/bin/env python3
"""Compare normalized Mago intent with read-only Magia evidence without claiming runtime proof."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

STATUSES = {"pass", "fail", "blocked", "not_run", "unknown"}

def keyed(items):
    return {item["id"]: item for item in items if isinstance(item, dict) and item.get("id")}

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--plan", required=True)
    ap.add_argument("--evidence", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
    evidence = json.loads(Path(args.evidence).read_text(encoding="utf-8"))
    errors = []
    if plan.get("kind") != "mago-plan-envelope": errors.append("invalid plan kind")
    if evidence.get("kind") != "magia-evidence-envelope": errors.append("invalid evidence kind")
    if evidence.get("authoritative_for_runtime") is not True: errors.append("Magia envelope must declare runtime authority")
    if not evidence.get("provenance"): errors.append("Magia evidence provenance is required")
    requirements = keyed(plan.get("requirements", [])); tasks = keyed(plan.get("tasks", [])); acceptance = keyed(plan.get("acceptance", []))
    e_reqs = keyed(evidence.get("requirements", [])); e_tasks = keyed(evidence.get("tasks", [])); e_acceptance = keyed(evidence.get("acceptance", []))
    result = {
        "kind": "mago-planning-reconciliation",
        "authoritative": False,
        "runtime_proof_authored_by_mago": False,
        "spec_id": plan.get("spec_id"),
        "evidence_provenance": evidence.get("provenance", []),
        "implemented_as_planned": [],
        "implementation_deviation": [],
        "unmet_acceptance_criteria": [],
        "obsolete_planned_task": [],
        "newly_discovered_work": evidence.get("newly_discovered_work", []),
        "required_planning_revision": evidence.get("required_planning_revision", []),
        "no_change_convergence": False,
        "errors": errors,
    }
    for rid, expected in requirements.items():
        actual = e_reqs.get(rid)
        if actual and actual.get("status") == "implemented" and actual.get("behavior") == expected.get("behavior"):
            result["implemented_as_planned"].append(rid)
        elif actual:
            result["implementation_deviation"].append({"id": rid, "planned": expected.get("behavior"), "observed": actual.get("behavior")})
    for aid in acceptance:
        actual = e_acceptance.get(aid, {})
        status = actual.get("status", "unknown")
        if status not in STATUSES: errors.append(f"invalid acceptance status for {aid}: {status}")
        if status != "pass": result["unmet_acceptance_criteria"].append({"id": aid, "status": status})
    for tid, expected in tasks.items():
        actual = e_tasks.get(tid, {})
        if actual.get("status") == "obsolete" or expected.get("obsolete") is True:
            result["obsolete_planned_task"].append(tid)
    result["no_change_convergence"] = not any([
        result["implementation_deviation"], result["unmet_acceptance_criteria"], result["obsolete_planned_task"],
        result["newly_discovered_work"], result["required_planning_revision"], errors,
    ])
    out = Path(args.output).resolve()
    plan_path = Path(args.plan).resolve(); evidence_path = Path(args.evidence).resolve()
    if out in {plan_path, evidence_path}: raise SystemExit("output must not overwrite plan or Magia evidence")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1

if __name__ == "__main__": raise SystemExit(main())
