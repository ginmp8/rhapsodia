from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from _common import dump_json, evaluation_identity_matches, metric_value


def _evaluation(c: dict) -> dict:
    value = c.get("evaluation")
    return value if isinstance(value, dict) else {}


def _gate_pass(c: dict, gates: list[str]) -> bool:
    values = _evaluation(c).get("hard_gates", {})
    return isinstance(values, dict) and all(values.get(g) == "pass" for g in gates)


def _comparable(c: dict, contract: dict) -> bool:
    if not evaluation_identity_matches(c, contract):
        return False
    evaluation = _evaluation(c)
    metrics = evaluation.get("metrics", {})
    if not isinstance(metrics, dict):
        return False
    return all(metric_value(metrics.get(o["name"])) is not None for o in contract.get("objectives", []))


def _margin(obj: dict, a_uncertainty: float, b_uncertainty: float) -> float:
    return float(obj.get("min_delta", 0.0)) + a_uncertainty + b_uncertainty


def _dominates(a: dict, b: dict, objectives: list[dict]) -> bool:
    am = _evaluation(a).get("metrics", {})
    bm = _evaluation(b).get("metrics", {})
    strictly_better = False
    for obj in objectives:
        name = obj["name"]
        av = metric_value(am.get(name))
        bv = metric_value(bm.get(name))
        if av is None or bv is None:
            return False
        a_value, a_uncertainty = av
        b_value, b_uncertainty = bv
        margin = _margin(obj, a_uncertainty, b_uncertainty)
        if obj["direction"] == "maximize":
            if b_value - a_value > margin:
                return False
            if a_value - b_value >= margin and margin > 0:
                strictly_better = True
            elif a_value > b_value and margin == 0:
                strictly_better = True
        else:
            if a_value - b_value > margin:
                return False
            if b_value - a_value >= margin and margin > 0:
                strictly_better = True
            elif a_value < b_value and margin == 0:
                strictly_better = True
    return strictly_better


def _jaccard_distance(a: dict, b: dict) -> float:
    sa = set(a.get("transformation_ids", []))
    sb = set(b.get("transformation_ids", []))
    if not sa and not sb:
        return 0.0
    return 1.0 - (len(sa & sb) / len(sa | sb))


def _uncertainty(c: dict, objectives: list[dict]) -> float:
    metrics = _evaluation(c).get("metrics", {})
    total = 0.0
    for obj in objectives:
        parsed = metric_value(metrics.get(obj["name"]))
        if parsed is None:
            return float("inf")
        total += parsed[1]
    return total


def _novelty_against_selected(candidate: dict, selected: list[dict]) -> float:
    if not selected:
        return 1.0
    return min(_jaccard_distance(candidate, other) for other in selected)


def select(contract: dict, state: dict) -> dict:
    gates = contract["hard_gates"]
    objectives = contract["objectives"]
    candidates = [
        c for c in state.get("candidates", [])
        if isinstance(c, dict) and c.get("status") in {"active", "finalist"}
    ]

    incompatible = sorted(c["candidate_id"] for c in candidates if not _comparable(c, contract))
    comparable = [c for c in candidates if c["candidate_id"] not in set(incompatible)]
    eliminated = sorted(c["candidate_id"] for c in comparable if not _gate_pass(c, gates))
    eligible = [c for c in comparable if _gate_pass(c, gates)]

    frontier: list[dict] = []
    for c in eligible:
        if not any(_dominates(other, c, objectives) for other in eligible if other is not c):
            frontier.append(c)
    frontier.sort(key=lambda c: c["candidate_id"])

    cap = contract["budget"]["max_active_candidates"]
    preserve_roles = list(contract.get("preserve_roles", []))
    selected: list[dict] = []

    for role in preserve_roles:
        matches = sorted((c for c in eligible if c.get("role") == role), key=lambda c: (_uncertainty(c, objectives), c["candidate_id"]))
        for c in matches:
            if c not in selected and len(selected) < cap:
                selected.append(c)

    remaining_frontier = [c for c in frontier if c not in selected]
    while remaining_frontier and len(selected) < cap:
        remaining_frontier.sort(
            key=lambda c: (
                -_novelty_against_selected(c, selected),
                _uncertainty(c, objectives),
                c["candidate_id"],
            )
        )
        selected.append(remaining_frontier.pop(0))

    if len(selected) < cap:
        remaining = [c for c in eligible if c not in selected]
        remaining.sort(
            key=lambda c: (
                sum(1 for other in eligible if other is not c and _dominates(other, c, objectives)),
                -_novelty_against_selected(c, selected),
                _uncertainty(c, objectives),
                c["candidate_id"],
            )
        )
        for c in remaining:
            if len(selected) >= cap:
                break
            selected.append(c)

    novelty = {
        c["candidate_id"]: round(_novelty_against_selected(c, [x for x in selected if x is not c]), 12)
        for c in selected
    }

    return {
        "status": "pass",
        "eligible": sorted(c["candidate_id"] for c in eligible),
        "incompatible_evidence": incompatible,
        "eliminated_hard_gate": eliminated,
        "pareto_frontier": sorted(c["candidate_id"] for c in frontier),
        "selected_survivors": [c["candidate_id"] for c in selected],
        "derived_novelty": novelty,
        "selection_policy": contract.get("selection_policy", {}),
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
    rendered = dump_json(result)
    if args.json_output:
        Path(args.json_output).write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
