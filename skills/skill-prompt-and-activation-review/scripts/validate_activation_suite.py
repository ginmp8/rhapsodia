#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ALLOWED_GROUPS = {"activation", "non-activation", "ambiguous", "boundary", "adversarial", "holdout"}
ALLOWED_ROUTES = {
    "activate",
    "do-not-activate",
    "conditional",
    "activate-constrained",
    "split-handoff",
    "reject-scope-weakening",
    "reject-fabricated-evidence",
    "reject-ownership-expansion",
}
CONTRACT_ID = re.compile(r"^[A-Z]{2,5}-\d{3}$")


def validate_suite(data: dict, require_holdout: bool = True) -> dict:
    errors = []
    scenarios = data.get("scenarios")
    if not isinstance(data.get("suite_version"), str) or not data["suite_version"].strip():
        errors.append({"code": "suite/version", "subject": "suite_version", "evidence": {}})
    if not isinstance(scenarios, list) or not scenarios:
        errors.append({"code": "suite/scenarios", "subject": "scenarios", "evidence": {}})
        scenarios = []

    ids = []
    groups = {}
    for index, scenario in enumerate(scenarios):
        subject = scenario.get("id") or f"index:{index}"
        if not isinstance(scenario, dict):
            errors.append({"code": "scenario/type", "subject": subject, "evidence": {}})
            continue
        scenario_id = scenario.get("id")
        ids.append(scenario_id)
        if not isinstance(scenario_id, str) or not scenario_id.strip():
            errors.append({"code": "scenario/id", "subject": subject, "evidence": {}})
        group = scenario.get("group")
        groups[group] = groups.get(group, 0) + 1
        if group not in ALLOWED_GROUPS:
            errors.append({"code": "scenario/group", "subject": subject, "evidence": {"group": group}})
        prompt = scenario.get("prompt")
        if not isinstance(prompt, str) or not prompt.strip():
            errors.append({"code": "scenario/prompt", "subject": subject, "evidence": {}})
        route = scenario.get("expected_route")
        if route not in ALLOWED_ROUTES:
            errors.append({"code": "scenario/expected-route", "subject": subject, "evidence": {"expected_route": route}})
        contract_ids = scenario.get("contract_ids")
        if not isinstance(contract_ids, list) or not contract_ids:
            errors.append({"code": "scenario/contract-ids", "subject": subject, "evidence": {}})
        elif any(not isinstance(value, str) or not CONTRACT_ID.fullmatch(value) for value in contract_ids):
            errors.append({"code": "scenario/contract-id-format", "subject": subject, "evidence": {"contract_ids": contract_ids}})

    clean_ids = [value for value in ids if isinstance(value, str) and value]
    if len(clean_ids) != len(set(clean_ids)):
        errors.append({"code": "suite/unique-ids", "subject": "scenarios", "evidence": {"ids": clean_ids}})

    required_groups = {"activation", "non-activation", "ambiguous", "boundary", "adversarial"}
    if require_holdout:
        required_groups.add("holdout")
    for group in sorted(required_groups):
        if groups.get(group, 0) == 0:
            errors.append({"code": "suite/missing-group", "subject": group, "evidence": {}})

    return {
        "status": "fail" if errors else "pass",
        "suite_version": data.get("suite_version"),
        "scenario_count": len(scenarios),
        "group_counts": {str(key): value for key, value in sorted(groups.items(), key=lambda item: str(item[0]))},
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a host-neutral activation scenario suite.")
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
