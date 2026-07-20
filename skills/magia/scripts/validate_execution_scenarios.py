#!/usr/bin/env python3
"""Validate the frozen MAGIA execution scenario suite."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

REQUIRED_CATEGORIES = {
    "safe_change", "localized_bug_fix", "ambiguous_bug", "behavior_preserving_refactor", "complexity_reduction",
    "api_contract", "event_contract", "database_migration", "authorization", "secret_exposure", "concurrency",
    "performance", "multi_repository_rollout", "multi_repository_partial_failure", "interrupted_resume",
    "repository_drift", "rollback", "mago_package", "planning_gap", "nomia_misroute", "spec_kit_adapter",
    "kiro_bug_adapter", "openspec_delta_adapter", "post_implementation_convergence", "activation",
    "non_activation", "ambiguous_routing", "edge_routing", "adversarial_routing",
}
PROFILES = {"quick", "standard", "governed", "route"}
REQUIRED_FIELDS = {"id", "category", "profile", "input", "expected"}


def validate_suite(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["scenario suite root must be an object"]
    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if data.get("frozen") is not True:
        errors.append("frozen must be true")
    scenarios = data.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        return errors + ["scenarios must be a non-empty array"]
    seen: set[str] = set()
    categories: set[str] = set()
    for index, item in enumerate(scenarios):
        if not isinstance(item, dict):
            errors.append(f"scenarios[{index}] must be an object")
            continue
        missing = REQUIRED_FIELDS - set(item)
        sid = item.get("id") or f"index {index}"
        if missing:
            errors.append(f"scenario {sid} missing fields: {sorted(missing)}")
        if item.get("id") in seen:
            errors.append(f"duplicate scenario id: {item.get('id')}")
        elif isinstance(item.get("id"), str):
            seen.add(item["id"])
        if item.get("profile") not in PROFILES:
            errors.append(f"scenario {sid} has invalid profile")
        if not isinstance(item.get("input"), str) or not item.get("input", "").strip():
            errors.append(f"scenario {sid} input must be non-empty")
        if not isinstance(item.get("expected"), list) or not item.get("expected") or not all(isinstance(x, str) and x.strip() for x in item.get("expected", [])):
            errors.append(f"scenario {sid} expected must be a non-empty string array")
        if isinstance(item.get("category"), str):
            categories.add(item["category"])
    missing_categories = sorted(REQUIRED_CATEGORIES - categories)
    if missing_categories:
        errors.append(f"missing required categories: {missing_categories}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate frozen MAGIA execution scenarios.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        data = json.loads(Path(args.input).read_text(encoding="utf-8"))
        errors = validate_suite(data)
    except Exception as exc:  # noqa: BLE001
        errors = [str(exc)]
    result = {"status": "pass" if not errors else "fail", "errors": errors}
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"status: {result['status']}")
        for error in errors:
            print(f"error: {error}")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
