#!/usr/bin/env python3
"""Select a MAGIA execution profile and validation checks from change facts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

GOVERNED_SIGNALS = {
    "public_contract", "event_contract", "schema_contract", "persistence", "migration", "authentication",
    "authorization", "secrets", "pii", "compliance", "concurrency", "performance", "messaging",
    "infrastructure", "cross_service", "cross_repository", "data_loss", "rollback_complexity",
}
SECURITY_SIGNALS = {"authentication", "authorization", "secrets", "pii", "compliance"}
CONTRACT_SIGNALS = {"public_contract", "event_contract", "schema_contract"}
OPERATIONAL_SIGNALS = {"messaging", "observability", "infrastructure", "cross_service", "cross_repository", "rollback_complexity"}
CODE_SUFFIXES = {".py", ".cs", ".fs", ".js", ".ts", ".tsx", ".java", ".go", ".rs", ".cpp", ".c", ".sql", ".sh", ".yaml", ".yml", ".json", ".toml"}


def select_profile(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise ValueError("change facts must be an object")
    file_types = data.get("file_types", [])
    components = data.get("components", [])
    signals = data.get("signals", {})
    if not isinstance(file_types, list) or not all(isinstance(x, str) for x in file_types):
        raise ValueError("file_types must be an array of strings")
    if not isinstance(components, list) or not all(isinstance(x, str) for x in components):
        raise ValueError("components must be an array of strings")
    if not isinstance(signals, dict) or not all(isinstance(k, str) and isinstance(v, bool) for k, v in signals.items()):
        raise ValueError("signals must be a boolean object")

    active = {key for key, value in signals.items() if value}
    reasons: list[str] = []
    code_changed = any(Path(value).suffix.lower() in CODE_SUFFIXES or value.lower() in CODE_SUFFIXES for value in file_types)
    multi_component = len(set(components)) > 1

    if active & GOVERNED_SIGNALS:
        profile = "governed"
        reasons.extend(sorted(active & GOVERNED_SIGNALS))
    elif code_changed or multi_component or signals.get("behavior_change", False):
        profile = "standard"
        reasons.extend([reason for reason, enabled in (("code_or_config_change", code_changed), ("multiple_components", multi_component), ("behavior_change", signals.get("behavior_change", False))) if enabled])
    else:
        profile = "quick"
        reasons.append("localized_reversible_low_risk")

    checks = {"targeted_tests"}
    docs: set[str] = set()
    if code_changed:
        checks.update({"build_or_compile", "lint_or_static_analysis"})
    if profile in {"standard", "governed"}:
        checks.update({"regression_check", "smoke_check"})
    if profile == "governed":
        checks.add("full_relevant_test_suite")
    if active & CONTRACT_SIGNALS:
        checks.add("contract_tests")
        docs.add("contract_change_note")
    if active & {"persistence", "migration", "data_loss"}:
        checks.add("migration_validation")
        docs.add("migration_execution_note")
    if active & SECURITY_SIGNALS:
        checks.add("security_checks")
        docs.add("security_risk_note")
    if active & {"concurrency", "performance"}:
        checks.add("performance_or_concurrency_checks")
    if active & OPERATIONAL_SIGNALS:
        checks.add("operational_verification")
        docs.update({"runbook", "observability_note"})
    if signals.get("planning_gap", False):
        docs.add("technical_gap_note")

    rollback = "simple_revert"
    if profile == "standard":
        rollback = "explicit_rollback_approach"
    if profile == "governed":
        rollback = "validated_per_component_or_repository_rollback"

    return {
        "profile": profile,
        "reasons": reasons,
        "required_checks": sorted(checks),
        "documentation_triggers": sorted(docs),
        "rollback_expectation": rollback,
        "run_state_required": profile == "governed" or signals.get("interruptible", False) or signals.get("cross_repository", False),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Select MAGIA profile and checks from change facts JSON.")
    parser.add_argument("--input", required=True, help="JSON file with file_types, components, and boolean signals.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable result.")
    args = parser.parse_args(argv)
    try:
        payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
        result = {"status": "pass", **select_profile(payload)}
    except Exception as exc:  # noqa: BLE001
        result = {"status": "fail", "errors": [str(exc)]}
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"status: {result['status']}")
        if result["status"] == "pass":
            print(f"profile: {result['profile']}")
            for check in result["required_checks"]:
                print(f"check: {check}")
        else:
            for error in result["errors"]:
                print(f"error: {error}")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
