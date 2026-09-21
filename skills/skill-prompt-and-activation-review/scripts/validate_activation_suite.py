#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

TARGET_SKILL = "skill-prompt-and-activation-review"
ALLOWED_STATUS = {"planned", "measured"}
ALLOWED_GROUPS = {"activation", "non-activation", "ambiguous", "boundary", "adversarial", "holdout"}
ALLOWED_ROUTES = {
    "activate", "do-not-activate", "conditional", "activate-constrained", "split-handoff",
    "reject-scope-weakening", "reject-fabricated-evidence", "reject-ownership-expansion",
}
ALLOWED_TYPES = {"should_activate", "should_not_activate", "ambiguous", "edge_case", "regression", "adversarial"}
GROUP_TO_TYPE = {
    "activation": "should_activate", "non-activation": "should_not_activate", "ambiguous": "ambiguous",
    "boundary": "edge_case", "adversarial": "adversarial", "holdout": "regression",
}
ALLOWED_TIERS = {"L2-focused", "L3-harness", "L5-holdout"}
ALLOWED_VISIBILITY = {"candidate-visible", "evaluator-only"}
CONTRACT_ID = re.compile(r"^[A-Z]{2,5}-\d{3}$")


def _error(errors, code, subject, **evidence):
    errors.append({"code": code, "subject": subject, "evidence": evidence})


def validate_suite(data: dict, require_holdout: bool = True) -> dict:
    errors = []
    scenarios = data.get("scenarios")
    if not isinstance(data.get("suite_version"), str) or not data["suite_version"].strip():
        _error(errors, "suite/version", "suite_version")
    if data.get("target_skill") != TARGET_SKILL:
        _error(errors, "suite/target-skill", "target_skill", target_skill=data.get("target_skill"))
    if data.get("status") not in ALLOWED_STATUS:
        _error(errors, "suite/status", "status", status=data.get("status"))
    if not isinstance(scenarios, list) or not scenarios:
        _error(errors, "suite/scenarios", "scenarios")
        scenarios = []

    ids, groups, types = [], {}, {}
    for index, scenario in enumerate(scenarios):
        subject = scenario.get("id") if isinstance(scenario, dict) else f"index:{index}"
        if not isinstance(scenario, dict):
            _error(errors, "scenario/object", subject)
            continue
        scenario_id = scenario.get("id")
        ids.append(scenario_id)
        if not isinstance(scenario_id, str) or not scenario_id.strip():
            _error(errors, "scenario/id", subject)
        group = scenario.get("group")
        groups[group] = groups.get(group, 0) + 1
        if group not in ALLOWED_GROUPS:
            _error(errors, "scenario/group", subject, group=group)
        prompt = scenario.get("prompt")
        if not isinstance(prompt, str) or not prompt.strip():
            _error(errors, "scenario/prompt", subject)
        route = scenario.get("expected_route")
        if route not in ALLOWED_ROUTES:
            _error(errors, "scenario/expected-route", subject, expected_route=route)
        contract_ids = scenario.get("contract_ids")
        if not isinstance(contract_ids, list) or not contract_ids:
            _error(errors, "scenario/contract-ids", subject)
        elif any(not isinstance(value, str) or not CONTRACT_ID.fullmatch(value) for value in contract_ids):
            _error(errors, "scenario/contract-id-format", subject, contract_ids=contract_ids)

        harness_type = scenario.get("type")
        types[harness_type] = types.get(harness_type, 0) + 1
        if harness_type not in ALLOWED_TYPES:
            _error(errors, "scenario/harness-type", subject, type=harness_type)
        category = scenario.get("category")
        if category != harness_type:
            _error(errors, "scenario/category-type-mismatch", subject, category=category, type=harness_type)
        expected_type = GROUP_TO_TYPE.get(group)
        if expected_type and harness_type != expected_type:
            _error(errors, "scenario/group-type-mismatch", subject, group=group, type=harness_type, expected_type=expected_type)
        expected_behavior = scenario.get("expected_behavior")
        if not isinstance(expected_behavior, str) or not expected_behavior.strip():
            _error(errors, "scenario/expected-behavior", subject)
        criteria = scenario.get("acceptance_criteria")
        if not isinstance(criteria, list) or not criteria or any(not isinstance(v, str) or not v.strip() for v in criteria):
            _error(errors, "scenario/acceptance-criteria", subject)
        tier = scenario.get("evaluation_tier")
        if tier not in ALLOWED_TIERS:
            _error(errors, "scenario/evaluation-tier", subject, evaluation_tier=tier)
        visibility = scenario.get("visibility")
        if visibility not in ALLOWED_VISIBILITY:
            _error(errors, "scenario/visibility", subject, visibility=visibility)
        if visibility == "evaluator-only":
            _error(errors, "scenario/bundled-evaluator-only", subject, visibility=visibility)

    clean_ids = [value for value in ids if isinstance(value, str) and value]
    if len(clean_ids) != len(set(clean_ids)):
        _error(errors, "suite/unique-ids", "scenarios", ids=clean_ids)

    required_groups = {"activation", "non-activation", "ambiguous", "boundary", "adversarial"}
    if require_holdout:
        required_groups.add("holdout")
    for group in sorted(required_groups):
        if groups.get(group, 0) == 0:
            _error(errors, "suite/missing-group", group)

    for harness_type in ("should_activate", "should_not_activate", "ambiguous", "edge_case"):
        if types.get(harness_type, 0) == 0:
            _error(errors, "suite/missing-harness-type", harness_type)

    return {
        "status": "fail" if errors else "pass",
        "suite_version": data.get("suite_version"),
        "scenario_count": len(scenarios),
        "group_counts": {str(k): v for k, v in sorted(groups.items(), key=lambda item: str(item[0]))},
        "type_counts": {str(k): v for k, v in sorted(types.items(), key=lambda item: str(item[0]))},
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the portable activation scenario suite and domain routing semantics.")
    parser.add_argument("suite")
    parser.add_argument("--allow-no-holdout", action="store_true")
    parser.add_argument("--json")
    args = parser.parse_args()
    path = Path(args.suite)
    data = json.loads(path.read_text(encoding="utf-8"))
    report = validate_suite(data, require_holdout=not args.allow_no_holdout)
    payload = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.json:
        Path(getattr(args, "json")).write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
