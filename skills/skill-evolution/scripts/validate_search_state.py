from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

VALID_STATUS = {"planned", "generated", "evaluating", "active", "rejected", "finalist", "terminal"}


def validate(contract: dict, state: dict) -> list[str]:
    errors: list[str] = []
    if state.get("state_version") != 1:
        errors.append("state_version:unsupported")
    if state.get("search_id") != contract.get("search_id"):
        errors.append("search_id:mismatch")
    candidates = state.get("candidates")
    if not isinstance(candidates, list):
        return errors + ["candidates:invalid"]
    budget = contract.get("budget", {})
    if len(candidates) > budget.get("max_total_candidates", 0):
        errors.append("candidates:budget_exceeded")
    ids = [c.get("candidate_id") for c in candidates if isinstance(c, dict)]
    if len(ids) != len(set(ids)) or any(not isinstance(x, str) or not x for x in ids):
        errors.append("candidate_id:invalid_or_duplicate")
    by_id = {c.get("candidate_id"): c for c in candidates if isinstance(c, dict) and c.get("candidate_id")}
    active = [c for c in candidates if isinstance(c, dict) and c.get("status") in {"active", "finalist"}]
    if len(active) > budget.get("max_active_candidates", 0):
        errors.append("candidates:active_budget_exceeded")
    hard_gate_names = set(contract.get("hard_gates", []))
    objective_names = {o.get("name") for o in contract.get("objectives", []) if isinstance(o, dict)}
    for cid, c in by_id.items():
        if c.get("status") not in VALID_STATUS:
            errors.append(f"candidate:{cid}:status_invalid")
        if c.get("operator") and c.get("operator") not in contract.get("allowed_operators", []):
            errors.append(f"candidate:{cid}:operator_not_allowed")
        parents = c.get("parent_ids", [])
        if not isinstance(parents, list):
            errors.append(f"candidate:{cid}:parent_ids_invalid")
            continue
        if cid in parents:
            errors.append(f"candidate:{cid}:self_parent")
        for p in parents:
            if p != contract.get("baseline_candidate_id") and p not in by_id:
                errors.append(f"candidate:{cid}:unknown_parent:{p}")
        gates = c.get("hard_gates", {})
        if gates and not isinstance(gates, dict):
            errors.append(f"candidate:{cid}:hard_gates_invalid")
        elif isinstance(gates, dict):
            unknown = set(gates) - hard_gate_names
            if unknown:
                errors.append(f"candidate:{cid}:unknown_gates:{','.join(sorted(unknown))}")
        metrics = c.get("metrics", {})
        if metrics and not isinstance(metrics, dict):
            errors.append(f"candidate:{cid}:metrics_invalid")
        elif isinstance(metrics, dict):
            unknown = set(metrics) - objective_names
            if unknown:
                errors.append(f"candidate:{cid}:unknown_metrics:{','.join(sorted(unknown))}")
    # lineage cycle detection among concrete candidates
    visiting: set[str] = set()
    visited: set[str] = set()
    def dfs(node: str) -> None:
        if node in visiting:
            errors.append(f"lineage:cycle:{node}")
            return
        if node in visited:
            return
        visiting.add(node)
        for p in by_id[node].get("parent_ids", []):
            if p in by_id:
                dfs(p)
        visiting.remove(node)
        visited.add(node)
    for cid in by_id:
        dfs(cid)
    finalists = state.get("finalists", [])
    if not isinstance(finalists, list):
        errors.append("finalists:invalid")
    else:
        if len(finalists) > budget.get("finalists", 0):
            errors.append("finalists:budget_exceeded")
        for cid in finalists:
            if cid not in by_id:
                errors.append(f"finalists:unknown:{cid}")
    return sorted(set(errors))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", required=True)
    parser.add_argument("--state", required=True)
    parser.add_argument("--json-output")
    args = parser.parse_args()
    contract = json.loads(Path(args.contract).read_text(encoding="utf-8"))
    state = json.loads(Path(args.state).read_text(encoding="utf-8"))
    errors = validate(contract, state)
    result = {"status": "pass" if not errors else "fail", "errors": errors}
    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.json_output:
        Path(args.json_output).write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if not errors else 2


if __name__ == "__main__":
    sys.exit(main())
