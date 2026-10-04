from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from _evidence_common import dump_json, evaluation_identity_matches, expand_evidence_contract, metric_value, validate_evaluation_extensions, validate_evidence_profile_config
from validate_evidence_aware_search_state import validate as validate_state


def _evaluation(c: dict) -> dict:
    value = c.get("evaluation")
    return value if isinstance(value, dict) else {}


def _gate_pass(c: dict, gates: list[str]) -> bool:
    values = _evaluation(c).get("hard_gates", {})
    return isinstance(values, dict) and all(values.get(g) == "pass" for g in gates)


def _required_slices_pass(c: dict, contract: dict) -> bool:
    required = contract.get("required_evaluation_slices", [])
    if not required:
        return True
    values = _evaluation(c).get("slices", {})
    return isinstance(values, dict) and all(values.get(name) == "pass" for name in required)


def _stability_pass(c: dict, contract: dict) -> bool:
    policy = contract.get("selection_policy", {}).get("stability_policy")
    if not isinstance(policy, dict) or policy.get("id") in {None, "none-v1"}:
        return True
    if policy.get("id") != "minimum-win-rate-v1":
        return False
    stability = _evaluation(c).get("stability")
    if not isinstance(stability, dict):
        return False
    return (
        stability.get("method_id") == policy.get("method_id")
        and isinstance(stability.get("win_rate"), (int, float))
        and not isinstance(stability.get("win_rate"), bool)
        and float(stability["win_rate"]) >= float(policy.get("minimum_win_rate", 1.0))
        and isinstance(stability.get("resamples"), int)
        and not isinstance(stability.get("resamples"), bool)
        and stability["resamples"] >= int(policy.get("minimum_resamples", 1))
    )


def _complexity_pass(c: dict, contract: dict) -> bool:
    policy = contract.get("complexity_policy")
    if not isinstance(policy, dict):
        return True
    limits = policy.get("limits", {})
    metrics = _evaluation(c).get("metrics", {})
    if not isinstance(limits, dict) or not isinstance(metrics, dict):
        return False
    for name, limit in limits.items():
        parsed = metric_value(metrics.get(name))
        if parsed is None or parsed[0] > float(limit):
            return False
    return True


def _comparable(c: dict, contract: dict) -> bool:
    if not evaluation_identity_matches(c, contract):
        return False
    evaluation = _evaluation(c)
    metrics = evaluation.get("metrics", {})
    if not isinstance(metrics, dict):
        return False
    if not all(metric_value(metrics.get(o["name"])) is not None for o in contract.get("objectives", [])):
        return False
    return not validate_evaluation_extensions(contract, evaluation)


def _evidence_eligible(c: dict, contract: dict) -> bool:
    allowed = set(contract.get("selection_policy", {}).get("eligible_evidence_types", []))
    return _evaluation(c).get("evidence_type") in allowed


def _holdout_failed(c: dict, contract: dict) -> bool:
    policy = contract.get("selection_policy", {}).get("holdout_failure_policy")
    return policy == "eliminate-blind-fail" and _evaluation(c).get("holdout_status") == "blind-fail"


def _same_comparison_level(a: dict, b: dict, contract: dict) -> bool:
    policy = contract.get("selection_policy", {}).get("comparison_level_policy")
    if policy == "same-level":
        return _evaluation(a).get("level") == _evaluation(b).get("level")
    return True


def _margin(obj: dict, a_uncertainty: float, b_uncertainty: float) -> float:
    return float(obj.get("min_delta", 0.0)) + a_uncertainty + b_uncertainty


def _dominates(a: dict, b: dict, objectives: list[dict], contract: dict) -> bool:
    if not _same_comparison_level(a, b, contract):
        return False
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


def _label_set(candidate: dict, contract: dict) -> set[str]:
    novelty = contract.get("selection_policy", {}).get("novelty_policy", {})
    if novelty.get("id") == "behavior-label-jaccard-v1":
        descriptor = _evaluation(candidate).get("behavior_descriptor", {})
        labels = descriptor.get("labels", []) if isinstance(descriptor, dict) else []
        return {x for x in labels if isinstance(x, str)}
    return {x for x in candidate.get("transformation_ids", []) if isinstance(x, str)}


def _jaccard_distance(a: dict, b: dict, contract: dict) -> float:
    sa = _label_set(a, contract)
    sb = _label_set(b, contract)
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


def _novelty_against_selected(candidate: dict, selected: list[dict], contract: dict) -> float:
    if not selected:
        return 1.0
    return min(_jaccard_distance(candidate, other, contract) for other in selected)


def _scenario_elites(candidates: list[dict], contract: dict) -> list[dict]:
    policy = contract.get("selection_policy", {}).get("frontier_policy")
    if not isinstance(policy, dict) or policy.get("id") != "aggregate-plus-scenario-elites-v1":
        return []
    direction = policy.get("scenario_direction")
    delta = float(policy.get("scenario_min_delta", 0.0))
    elites: dict[str, dict] = {}
    levels = sorted({_evaluation(c).get("level") for c in candidates})
    for level in levels:
        peers = [c for c in candidates if _evaluation(c).get("level") == level]
        scenario_names = sorted({name for c in peers for name in _evaluation(c).get("scenario_scores", {})})
        for scenario in scenario_names:
            scored = []
            for c in peers:
                raw = _evaluation(c).get("scenario_scores", {}).get(scenario)
                if isinstance(raw, (int, float)) and not isinstance(raw, bool):
                    scored.append((float(raw), c))
            if not scored:
                continue
            best = max(v for v, _ in scored) if direction == "maximize" else min(v for v, _ in scored)
            for value, c in scored:
                qualifies = value >= best - delta if direction == "maximize" else value <= best + delta
                if qualifies:
                    elites[c["candidate_id"]] = c
    return [elites[cid] for cid in sorted(elites)]


def select(contract: dict, state: dict) -> dict:
    profile_errors = validate_evidence_profile_config(contract)
    state_errors = profile_errors + validate_state(contract, state)
    contract = expand_evidence_contract(contract)
    fatal_state_errors = [
        error for error in state_errors
        if not error.endswith(":evaluation_identity_mismatch")
    ]
    empty = {
        "eligible": [],
        "incompatible_evidence": [],
        "ineligible_evidence": [],
        "eliminated_holdout": [],
        "eliminated_hard_gate": [],
        "eliminated_required_slice": [],
        "eliminated_stability": [],
        "eliminated_complexity": [],
        "pareto_frontier": [],
        "scenario_elites": [],
        "selected_survivors": [],
        "derived_novelty": {},
        "selection_policy": contract.get("selection_policy", {}),
    }
    if fatal_state_errors:
        return {"status": "fail", "errors": fatal_state_errors, **empty}

    gates = contract["hard_gates"]
    objectives = contract["objectives"]
    candidates = [
        c for c in state.get("candidates", [])
        if isinstance(c, dict) and c.get("status") in {"evaluating", "active", "finalist"} and isinstance(c.get("evaluation"), dict)
    ]

    incompatible = sorted(c["candidate_id"] for c in candidates if not _comparable(c, contract))
    comparable = [c for c in candidates if c["candidate_id"] not in set(incompatible)]
    ineligible_evidence = sorted(c["candidate_id"] for c in comparable if not _evidence_eligible(c, contract))
    evidence_eligible = [c for c in comparable if c["candidate_id"] not in set(ineligible_evidence)]
    eliminated_holdout = sorted(c["candidate_id"] for c in evidence_eligible if _holdout_failed(c, contract))
    holdout_eligible = [c for c in evidence_eligible if c["candidate_id"] not in set(eliminated_holdout)]
    eliminated_gate = sorted(c["candidate_id"] for c in holdout_eligible if not _gate_pass(c, gates))
    gate_eligible = [c for c in holdout_eligible if c["candidate_id"] not in set(eliminated_gate)]
    eliminated_slice = sorted(c["candidate_id"] for c in gate_eligible if not _required_slices_pass(c, contract))
    slice_eligible = [c for c in gate_eligible if c["candidate_id"] not in set(eliminated_slice)]
    eliminated_stability = sorted(c["candidate_id"] for c in slice_eligible if not _stability_pass(c, contract))
    stable = [c for c in slice_eligible if c["candidate_id"] not in set(eliminated_stability)]
    eliminated_complexity = sorted(c["candidate_id"] for c in stable if not _complexity_pass(c, contract))
    eligible = [c for c in stable if c["candidate_id"] not in set(eliminated_complexity)]

    frontier: list[dict] = []
    for c in eligible:
        if not any(_dominates(other, c, objectives, contract) for other in eligible if other is not c):
            frontier.append(c)
    frontier.sort(key=lambda c: c["candidate_id"])
    scenario_elites = _scenario_elites(eligible, contract)
    selection_frontier = {c["candidate_id"]: c for c in frontier}
    selection_frontier.update({c["candidate_id"]: c for c in scenario_elites})

    cap = contract["budget"]["max_active_candidates"]
    preserve_roles = list(contract.get("preserve_roles", []))
    selected: list[dict] = []

    for role in preserve_roles:
        matches = sorted((c for c in eligible if c.get("role") == role), key=lambda c: (_uncertainty(c, objectives), c["candidate_id"]))
        for c in matches:
            if c not in selected and len(selected) < cap:
                selected.append(c)

    remaining_frontier = [c for c in selection_frontier.values() if c not in selected]
    while remaining_frontier and len(selected) < cap:
        remaining_frontier.sort(
            key=lambda c: (
                -_novelty_against_selected(c, selected, contract),
                _uncertainty(c, objectives),
                c["candidate_id"],
            )
        )
        selected.append(remaining_frontier.pop(0))

    if len(selected) < cap:
        remaining = [c for c in eligible if c not in selected]
        remaining.sort(
            key=lambda c: (
                sum(1 for other in eligible if other is not c and _dominates(other, c, objectives, contract)),
                -_novelty_against_selected(c, selected, contract),
                _uncertainty(c, objectives),
                c["candidate_id"],
            )
        )
        for c in remaining:
            if len(selected) >= cap:
                break
            selected.append(c)

    novelty = {
        c["candidate_id"]: round(_novelty_against_selected(c, [x for x in selected if x is not c], contract), 12)
        for c in selected
    }

    return {
        "status": "pass",
        "errors": [],
        "eligible": sorted(c["candidate_id"] for c in eligible),
        "incompatible_evidence": incompatible,
        "ineligible_evidence": ineligible_evidence,
        "eliminated_holdout": eliminated_holdout,
        "eliminated_hard_gate": eliminated_gate,
        "eliminated_required_slice": eliminated_slice,
        "eliminated_stability": eliminated_stability,
        "eliminated_complexity": eliminated_complexity,
        "pareto_frontier": sorted(c["candidate_id"] for c in frontier),
        "scenario_elites": sorted(c["candidate_id"] for c in scenario_elites),
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
    return 0 if result.get("status") == "pass" else 2


if __name__ == "__main__":
    sys.exit(main())
