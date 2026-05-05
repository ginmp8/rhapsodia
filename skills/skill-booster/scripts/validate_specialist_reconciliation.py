#!/usr/bin/env python3
"""Validate Skill Booster specialist sequence reconciliation evidence."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

DEFAULT_REQUIRED_SPECIALISTS = [
    "skill-creator-juiced",
    "skill-benchmark",
    "skill-harness",
    "skill-hypothesis-discovery",
    "skill-improver",
    "skill-change-gate",
    "skill-package-architecture-review",
    "context-architect",
    "skill-prompt-and-activation-review",
    "prompt-architect",
    "skill-consistency-repair",
    "documentation-quality",
    "karpathy-guidelines",
    "security-and-governance-review",
    "skill-testing-and-validation",
    "skill-cleanup-and-simplification",
    "skill-token-efficient",
    "post-compression skill-testing-and-validation",
    "skill-hardening",
    "final skill-change-gate",
    "final skill-benchmark",
    "final skill-improver",
    "final skill-token-efficient",
]

STATUS_FIELDS = {
    "invoked": "invoked_specialists",
    "checklist_only": "checklist_only",
    "blocked": "blocked",
    "unavailable": "unavailable",
    "not_applicable": "not_applicable",
    "not_run": "not_run",
}

PASSING_STATUSES = {"invoked", "blocked", "unavailable", "not_applicable"}


def load_names(value: Any) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise TypeError("status fields must be lists")
    names: list[str] = []
    for item in value:
        if isinstance(item, str):
            names.append(item.strip())
        elif isinstance(item, dict):
            name = item.get("name") or item.get("specialist") or item.get("pass")
            if not isinstance(name, str):
                raise TypeError("dict entries must include string name, specialist, or pass")
            names.append(name.strip())
        else:
            raise TypeError("status entries must be strings or objects")
    return [name for name in names if name]


def validate(data: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    required = load_names(data.get("required_specialists")) or DEFAULT_REQUIRED_SPECIALISTS
    available = set(load_names(data.get("available_specialists")))
    assume_required_available = bool(data.get("assume_required_available", False))

    buckets: dict[str, list[str]] = {}
    for status, field in STATUS_FIELDS.items():
        try:
            buckets[status] = load_names(data.get(field))
        except TypeError as exc:
            errors.append(f"invalid {field}: {exc}")
            buckets[status] = []

    required_set = set(required)
    if len(required_set) != len(required):
        errors.append("required_specialists contains duplicate entries")

    classified: dict[str, list[str]] = {}
    for status, names in buckets.items():
        for name in names:
            classified.setdefault(name, []).append(status)
            if name not in required_set:
                warnings.append(f"classified specialist not in required sequence: {name}")

    missing = [name for name in required if name not in classified]
    if missing:
        errors.append("required specialists missing explicit classification: " + ", ".join(missing))

    duplicates = {name: statuses for name, statuses in classified.items() if len(statuses) > 1}
    if duplicates:
        rendered = "; ".join(f"{name}={statuses}" for name, statuses in sorted(duplicates.items()))
        errors.append("specialists classified in multiple buckets: " + rendered)

    if buckets["not_run"]:
        errors.append("not_run specialists block finalization: " + ", ".join(buckets["not_run"]))

    # Checklist-only is an advisory classification. It may not satisfy a required explicit sequence
    # unless the same specialist is declared unavailable or blocked, which would be a duplicate and
    # is intentionally rejected above. This prevents checklist-only from masquerading as execution.
    if buckets["checklist_only"]:
        errors.append("checklist_only does not satisfy an explicit required sequence: " + ", ".join(buckets["checklist_only"]))

    if assume_required_available:
        available |= required_set
    if available:
        not_invoked_available = [name for name in required if name in available and name not in set(buckets["invoked"])]
        allowed_missing = set(buckets["blocked"]) | set(buckets["not_applicable"])
        violating = [name for name in not_invoked_available if name not in allowed_missing]
        if violating:
            errors.append("available required specialists were not invoked or explicitly blocked/not-applicable: " + ", ".join(violating))

    satisfied = [name for name in required if classified.get(name, [None])[0] in PASSING_STATUSES]
    finalization_allowed = not errors and len(satisfied) == len(required)
    return {
        "status": "pass" if finalization_allowed else "fail",
        "finalization_allowed": finalization_allowed,
        "required_count": len(required),
        "invoked_count": len([name for name in buckets["invoked"] if name in required_set]),
        "checklist_only_count": len([name for name in buckets["checklist_only"] if name in required_set]),
        "blocked_count": len([name for name in buckets["blocked"] if name in required_set]),
        "unavailable_count": len([name for name in buckets["unavailable"] if name in required_set]),
        "not_applicable_count": len([name for name in buckets["not_applicable"] if name in required_set]),
        "not_run_count": len([name for name in buckets["not_run"] if name in required_set]),
        "missing": missing,
        "errors": errors,
        "warnings": sorted(set(warnings)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Skill Booster specialist reconciliation JSON.")
    parser.add_argument("--ledger", required=True, help="JSON file with required/invoked/checklist/blocked specialist buckets")
    parser.add_argument("--json", dest="json_output", help="Optional output report path")
    args = parser.parse_args()
    try:
        data = json.loads(Path(args.ledger).read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise TypeError("ledger root must be a JSON object")
        report = validate(data)
    except Exception as exc:
        report = {"status": "fail", "finalization_allowed": False, "errors": [str(exc)], "warnings": []}
    text = json.dumps(report, indent=2, ensure_ascii=False)
    print(text)
    if args.json_output:
        Path(args.json_output).write_text(text + "\n", encoding="utf-8")
    return 0 if report.get("status") == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
