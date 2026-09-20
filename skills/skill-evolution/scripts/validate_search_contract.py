from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from _common import dump_json

SUPPORTED_VERSION = 3
ALLOWED_DIRECTIONS = {"maximize", "minimize"}
ALLOWED_OPERATORS = {"transformation-merge", "backcross", "repair-crossover", "bounded-mutation"}
ALLOWED_TRANSFORMATION_STATUS = {"proposed", "accepted", "validated", "rejected", "deprecated"}
ALLOWED_LEVELS = {"L0-structural", "L1-deterministic", "L2-focused", "L3-harness", "L4-benchmark", "L5-holdout"}


def validate(data: dict) -> list[str]:
    errors: list[str] = []
    required = (
        "contract_version",
        "search_id",
        "target_identity",
        "target_class",
        "baseline_candidate_id",
        "canonical_candidate_id",
        "input_identities",
        "interfaces",
        "budget",
        "hard_gates",
        "objectives",
        "evaluation_identity",
        "allowed_evaluation_levels",
        "allowed_operators",
        "selection_policy",
        "capability_invariants",
        "transformation_registry",
    )
    for key in required:
        if key not in data:
            errors.append(f"missing:{key}")
    if errors:
        return sorted(set(errors))

    if data["contract_version"] != SUPPORTED_VERSION:
        if data["contract_version"] in {1, 2}:
            errors.append("contract_version:upgrade_required_v3")
        else:
            errors.append("contract_version:unsupported")

    for key in ("search_id", "target_identity", "target_class", "baseline_candidate_id", "canonical_candidate_id"):
        if not isinstance(data.get(key), str) or not data[key].strip():
            errors.append(f"{key}:invalid")
    if data.get("baseline_candidate_id") == data.get("canonical_candidate_id"):
        errors.append("candidate_ids:baseline_equals_canonical")


    input_identities = data.get("input_identities")
    if not isinstance(input_identities, dict):
        errors.append("input_identities:invalid")
    else:
        for key in ("capability_map_id", "hypothesis_pool_id", "transformation_registry_id", "evaluation_plan_id"):
            if not isinstance(input_identities.get(key), str) or not input_identities[key].strip():
                errors.append(f"input_identities.{key}:invalid")

    interfaces = data.get("interfaces")
    if not isinstance(interfaces, dict):
        errors.append("interfaces:invalid")
    else:
        for key in ("mutation_interface_id", "evaluation_interface_id"):
            if not isinstance(interfaces.get(key), str) or not interfaces[key].strip():
                errors.append(f"interfaces.{key}:invalid")

    budget = data.get("budget", {})
    required_budget = (
        "initial_variants",
        "max_active_candidates",
        "max_total_candidates",
        "finalists",
        "stagnant_rounds",
        "max_recombination_proposals_per_round",
    )
    if not isinstance(budget, dict):
        errors.append("budget:invalid")
    else:
        for key in required_budget:
            value = budget.get(key)
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                errors.append(f"budget.{key}:invalid")
        if all(isinstance(budget.get(k), int) and not isinstance(budget.get(k), bool) for k in ("max_active_candidates", "max_total_candidates", "finalists", "initial_variants")):
            if budget["max_active_candidates"] > budget["max_total_candidates"]:
                errors.append("budget:active_exceeds_total")
            if budget["finalists"] > budget["max_active_candidates"]:
                errors.append("budget:finalists_exceed_active")
            if budget["initial_variants"] > budget["max_active_candidates"]:
                errors.append("budget:initial_variants_exceed_active")
            if budget["max_total_candidates"] > 20:
                errors.append("budget:max_total_candidates_exceeds_20")

    hard_gates = data.get("hard_gates")
    if not isinstance(hard_gates, list) or not hard_gates or any(not isinstance(x, str) or not x for x in hard_gates) or len(set(hard_gates)) != len(hard_gates):
        errors.append("hard_gates:invalid")

    objectives = data.get("objectives")
    names: list[str] = []
    if not isinstance(objectives, list) or not objectives:
        errors.append("objectives:invalid")
    else:
        for i, obj in enumerate(objectives):
            if not isinstance(obj, dict) or not isinstance(obj.get("name"), str) or not obj.get("name"):
                errors.append(f"objectives[{i}]:invalid")
                continue
            if obj.get("direction") not in ALLOWED_DIRECTIONS:
                errors.append(f"objectives[{i}].direction:invalid")
            min_delta = obj.get("min_delta", 0)
            if not isinstance(min_delta, (int, float)) or isinstance(min_delta, bool) or min_delta < 0:
                errors.append(f"objectives[{i}].min_delta:invalid")
            names.append(obj["name"])
        if len(names) != len(set(names)):
            errors.append("objectives:duplicate_name")

    evaluation = data.get("evaluation_identity", {})
    if not isinstance(evaluation, dict):
        errors.append("evaluation_identity:invalid")
    else:
        for key in ("evaluator_id", "scenario_set_id", "policy_id"):
            if not isinstance(evaluation.get(key), str) or not evaluation[key].strip():
                errors.append(f"evaluation_identity.{key}:invalid")

    levels = data.get("allowed_evaluation_levels")
    if not isinstance(levels, list) or not levels or len(levels) != len(set(levels)):
        errors.append("allowed_evaluation_levels:invalid")
    elif set(levels) - ALLOWED_LEVELS:
        errors.append("allowed_evaluation_levels:unknown:" + ",".join(sorted(set(levels) - ALLOWED_LEVELS)))

    operators = data.get("allowed_operators")
    if not isinstance(operators, list) or not operators:
        errors.append("allowed_operators:invalid")
    else:
        unknown = sorted(set(operators) - ALLOWED_OPERATORS)
        if unknown:
            errors.append("allowed_operators:unknown:" + ",".join(unknown))
        if len(operators) != len(set(operators)):
            errors.append("allowed_operators:duplicate")

    policy = data.get("selection_policy")
    if not isinstance(policy, dict):
        errors.append("selection_policy:invalid")
    else:
        if policy.get("id") != "pareto-then-novelty-v3":
            errors.append("selection_policy.id:unsupported")
        if policy.get("eligible_evidence_types") != ["measured", "supplied"]:
            errors.append("selection_policy.eligible_evidence_types:invalid")
        if policy.get("comparison_level_policy") != "same-level":
            errors.append("selection_policy.comparison_level_policy:invalid")
        if policy.get("holdout_failure_policy") != "eliminate-blind-fail":
            errors.append("selection_policy.holdout_failure_policy:invalid")
        novelty = policy.get("novelty_policy")
        if not isinstance(novelty, dict) or novelty.get("id") != "transformation-jaccard-v1" or novelty.get("source") != "derived":
            errors.append("selection_policy.novelty_policy:invalid")
        if policy.get("uncertainty_policy") != "margin-plus-min-delta-v1":
            errors.append("selection_policy.uncertainty_policy:invalid")

    invariants = data.get("capability_invariants")
    if not isinstance(invariants, list) or any(not isinstance(x, str) or not x for x in invariants) or len(invariants) != len(set(invariants)):
        errors.append("capability_invariants:invalid")

    registry = data.get("transformation_registry")
    ids: list[str] = []
    by_id: dict[str, dict] = {}
    if not isinstance(registry, list) or not registry:
        errors.append("transformation_registry:invalid")
    else:
        for i, item in enumerate(registry):
            if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not item.get("id"):
                errors.append(f"transformation_registry[{i}]:invalid")
                continue
            tid = item["id"]
            ids.append(tid)
            by_id[tid] = item
            if item.get("status") not in ALLOWED_TRANSFORMATION_STATUS:
                errors.append(f"transformation:{tid}:status_invalid")
            for field in ("depends_on", "conflicts_with", "capability_effects", "violates_invariants"):
                value = item.get(field, [])
                if not isinstance(value, list) or any(not isinstance(x, str) or not x for x in value) or len(value) != len(set(value)):
                    errors.append(f"transformation:{tid}:{field}_invalid")
            if tid in item.get("depends_on", []):
                errors.append(f"transformation:{tid}:self_dependency")
            if tid in item.get("conflicts_with", []):
                errors.append(f"transformation:{tid}:self_conflict")
            unknown_invariants = set(item.get("violates_invariants", [])) - set(invariants if isinstance(invariants, list) else [])
            if unknown_invariants:
                errors.append(f"transformation:{tid}:unknown_invariants:{','.join(sorted(unknown_invariants))}")
        if len(ids) != len(set(ids)):
            errors.append("transformation_registry:duplicate_id")

        known = set(ids)
        for tid, item in by_id.items():
            for dep in item.get("depends_on", []):
                if dep not in known:
                    errors.append(f"transformation:{tid}:unknown_dependency:{dep}")
                if dep in item.get("conflicts_with", []):
                    errors.append(f"transformation:{tid}:dependency_conflict:{dep}")
            for conflict in item.get("conflicts_with", []):
                if conflict not in known:
                    errors.append(f"transformation:{tid}:unknown_conflict:{conflict}")

        visiting: set[str] = set()
        visited: set[str] = set()

        def dfs(tid: str) -> None:
            if tid in visiting:
                errors.append(f"transformation_dependency_cycle:{tid}")
                return
            if tid in visited or tid not in by_id:
                return
            visiting.add(tid)
            for dep in by_id[tid].get("depends_on", []):
                dfs(dep)
            visiting.remove(tid)
            visited.add(tid)

        for tid in by_id:
            dfs(tid)

    preserve_roles = data.get("preserve_roles", [])
    if not isinstance(preserve_roles, list) or any(not isinstance(x, str) or not x for x in preserve_roles) or len(preserve_roles) != len(set(preserve_roles)):
        errors.append("preserve_roles:invalid")

    return sorted(set(errors))


def _diagnostics(errors: list[str]) -> list[dict]:
    diagnostics = []
    for error in errors:
        parts = error.split(":", 1)
        diagnostics.append({
            "code": error.replace(":", "."),
            "subject": parts[0],
            "evidence": error,
        })
    return diagnostics


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("contract")
    parser.add_argument("--json-output")
    args = parser.parse_args()
    try:
        data = json.loads(Path(args.contract).read_text(encoding="utf-8"))
        errors = validate(data)
    except (OSError, json.JSONDecodeError) as exc:
        errors = [f"contract:unreadable:{exc.__class__.__name__}"]
    result = {
        "status": "pass" if not errors else "fail",
        "contract_version": SUPPORTED_VERSION,
        "errors": errors,
        "diagnostics": _diagnostics(errors),
    }
    rendered = dump_json(result)
    if args.json_output:
        Path(args.json_output).write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if not errors else 2


if __name__ == "__main__":
    sys.exit(main())
