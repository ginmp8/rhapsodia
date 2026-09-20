from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _gate_pass(c: dict, gates: list[str]) -> bool:
    values = c.get("hard_gates", {})
    return all(values.get(g) == "pass" for g in gates)


def _comparable(a: dict, b: dict, objectives: list[dict]) -> bool:
    am, bm = a.get("metrics", {}), b.get("metrics", {})
    return all(o["name"] in am and o["name"] in bm for o in objectives)


def _dominates(a: dict, b: dict, objectives: list[dict]) -> bool:
    if not _comparable(a, b, objectives):
        return False
    better = False
    for obj in objectives:
        n, d = obj["name"], obj["direction"]
        av, bv = a["metrics"][n], b["metrics"][n]
        if d == "maximize":
            if av < bv:
                return False
            better |= av > bv
        else:
            if av > bv:
                return False
            better |= av < bv
    return better


def select(contract: dict, state: dict) -> dict:
    gates = contract["hard_gates"]
    objectives = contract["objectives"]
    candidates = [c for c in state.get("candidates", []) if c.get("status") not in {"rejected", "terminal"}]
    eligible = [c for c in candidates if _gate_pass(c, gates)]
    eliminated = sorted(c["candidate_id"] for c in candidates if c not in eligible)
    frontier = []
    for c in eligible:
        if not any(_dominates(other, c, objectives) for other in eligible if other is not c):
            frontier.append(c)
    frontier.sort(key=lambda c: (-(float(c.get("novelty", 0.0))), c["candidate_id"]))
    cap = contract["budget"]["max_active_candidates"]
    preserve_roles = set(contract.get("preserve_roles", []))
    selected: list[dict] = []
    for c in frontier:
        if c.get("role") in preserve_roles and c not in selected:
            selected.append(c)
    for c in frontier:
        if c not in selected and len(selected) < cap:
            selected.append(c)
    if len(selected) < cap:
        remaining = [c for c in eligible if c not in selected]
        # least dominated, then novelty, then stable id
        remaining.sort(key=lambda c: (
            sum(1 for other in eligible if other is not c and _dominates(other, c, objectives)),
            -float(c.get("novelty", 0.0)),
            c["candidate_id"],
        ))
        for c in remaining:
            if len(selected) >= cap:
                break
            selected.append(c)
    return {
        "status": "pass",
        "eligible": sorted(c["candidate_id"] for c in eligible),
        "eliminated_hard_gate": eliminated,
        "pareto_frontier": sorted(c["candidate_id"] for c in frontier),
        "selected_survivors": [c["candidate_id"] for c in selected],
        "selection_policy": contract.get("selection_policy", "pareto-then-novelty"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", required=True)
    parser.add_argument("--state", required=True)
    parser.add_argument("--json-output")
    args = parser.parse_args()
    contract = json.loads(Path(args.contract).read_text(encoding="utf-8"))
    state = json.loads(Path(args.state).read_text(encoding="utf-8"))
    result = select(contract, state)
    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.json_output:
        Path(args.json_output).write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    sys.exit(main())
