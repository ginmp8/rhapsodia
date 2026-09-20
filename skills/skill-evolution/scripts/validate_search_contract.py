from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ALLOWED_DIRECTIONS = {"maximize", "minimize"}
ALLOWED_OPERATORS = {"transformation-merge", "backcross", "repair-crossover", "bounded-mutation"}


def validate(data: dict) -> list[str]:
    errors: list[str] = []
    for key in ("contract_version", "search_id", "target_identity", "budget", "hard_gates", "objectives", "evaluation_identity", "allowed_operators"):
        if key not in data:
            errors.append(f"missing:{key}")
    if errors:
        return errors
    if data["contract_version"] != 1:
        errors.append("contract_version:unsupported")
    if not isinstance(data["search_id"], str) or not data["search_id"].strip():
        errors.append("search_id:invalid")
    if not isinstance(data["target_identity"], str) or not data["target_identity"].strip():
        errors.append("target_identity:invalid")
    budget = data.get("budget", {})
    required_budget = ("initial_variants", "max_active_candidates", "max_total_candidates", "finalists", "stagnant_rounds", "max_recombination_proposals_per_round")
    for key in required_budget:
        value = budget.get(key)
        if not isinstance(value, int) or value <= 0:
            errors.append(f"budget.{key}:invalid")
    if all(isinstance(budget.get(k), int) for k in ("max_active_candidates", "max_total_candidates", "finalists")):
        if budget["max_active_candidates"] > budget["max_total_candidates"]:
            errors.append("budget:active_exceeds_total")
        if budget["finalists"] > budget["max_active_candidates"]:
            errors.append("budget:finalists_exceed_active")
        if budget["max_total_candidates"] > 20:
            errors.append("budget:max_total_candidates_exceeds_20")
    hard_gates = data.get("hard_gates")
    if not isinstance(hard_gates, list) or not hard_gates or len(set(hard_gates)) != len(hard_gates):
        errors.append("hard_gates:invalid")
    objectives = data.get("objectives")
    names: list[str] = []
    if not isinstance(objectives, list) or not objectives:
        errors.append("objectives:invalid")
    else:
        for i, obj in enumerate(objectives):
            if not isinstance(obj, dict) or not isinstance(obj.get("name"), str) or obj.get("direction") not in ALLOWED_DIRECTIONS:
                errors.append(f"objectives[{i}]:invalid")
            else:
                names.append(obj["name"])
        if len(names) != len(set(names)):
            errors.append("objectives:duplicate_name")
    evaluation = data.get("evaluation_identity", {})
    if not isinstance(evaluation, dict) or not evaluation.get("evaluator_id") or not evaluation.get("scenario_set_id"):
        errors.append("evaluation_identity:invalid")
    operators = data.get("allowed_operators")
    if not isinstance(operators, list) or not operators:
        errors.append("allowed_operators:invalid")
    else:
        unknown = sorted(set(operators) - ALLOWED_OPERATORS)
        if unknown:
            errors.append("allowed_operators:unknown:" + ",".join(unknown))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("contract")
    parser.add_argument("--json-output")
    args = parser.parse_args()
    data = json.loads(Path(args.contract).read_text(encoding="utf-8"))
    errors = validate(data)
    result = {"status": "pass" if not errors else "fail", "errors": errors}
    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.json_output:
        Path(args.json_output).write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if not errors else 2


if __name__ == "__main__":
    sys.exit(main())
