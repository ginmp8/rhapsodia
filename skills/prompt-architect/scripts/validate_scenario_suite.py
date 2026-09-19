#!/usr/bin/env python3
"""Validate Prompt Architect scenario-suite JSON, including legacy v1 suites."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

GROUPS = {"activation", "non-activation", "core", "boundary", "ambiguous", "conflict", "regression", "adversarial", "runtime", "holdout"}
PRIORITIES = {"low", "medium", "high", "critical"}
ACTIVATION = {"yes", "no", "ambiguous", "not-applicable"}
LEGACY_TYPES = {"should_activate", "should_not_activate", "ambiguous", "edge_case", "regression", "adversarial"}


def validate_v2(data: dict, errors: list[str], warnings: list[str]) -> None:
    if data.get("schema_version") != 2:
        errors.append("schema_version must be 2")
    if not isinstance(data.get("suite_id"), str) or not data.get("suite_id", "").strip():
        errors.append("suite_id must be a non-empty string")
    if not isinstance(data.get("target_identity"), str) or not data.get("target_identity", "").strip():
        errors.append("target_identity must be a non-empty string")
    scenarios = data.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        errors.append("scenarios must be a non-empty list")
        return
    ids: set[str] = set()
    for i, s in enumerate(scenarios):
        p = f"scenarios[{i}]"
        if not isinstance(s, dict):
            errors.append(f"{p} must be an object")
            continue
        sid = s.get("id")
        if not isinstance(sid, str) or not sid.strip():
            errors.append(f"{p}.id must be a non-empty string")
        elif sid in ids:
            errors.append(f"duplicate scenario id: {sid}")
        else:
            ids.add(sid)
        if s.get("group") not in GROUPS:
            errors.append(f"{p}.group is invalid")
        if s.get("priority") not in PRIORITIES:
            errors.append(f"{p}.priority is invalid")
        if not isinstance(s.get("input"), str) or not s.get("input", "").strip():
            errors.append(f"{p}.input must be a non-empty string")
        expected = s.get("expected")
        if not isinstance(expected, dict):
            errors.append(f"{p}.expected must be an object")
            continue
        if expected.get("activation") not in ACTIVATION:
            errors.append(f"{p}.expected.activation is invalid")
        for key in ("hard_gates", "observables", "forbidden"):
            value = expected.get(key)
            if not isinstance(value, list):
                errors.append(f"{p}.expected.{key} must be a list")
        if not expected.get("hard_gates") and not expected.get("observables"):
            warnings.append(f"{p} has no hard gates or observables")
        if s.get("group") == "holdout":
            warnings.append(f"{p} is stored in the visible package; treat it as authoring coverage, not a genuine hidden holdout")


def validate_legacy(data: dict, errors: list[str], warnings: list[str]) -> None:
    scenarios = data.get("scenarios")
    if not isinstance(data.get("suite_name"), str) or not data.get("suite_name", "").strip():
        errors.append("legacy suite_name must be a non-empty string")
    if not isinstance(scenarios, list) or not scenarios:
        errors.append("legacy scenarios must be a non-empty list")
        return
    ids: set[str] = set()
    for i, s in enumerate(scenarios):
        p = f"scenarios[{i}]"
        if not isinstance(s, dict):
            errors.append(f"{p} must be an object")
            continue
        sid = s.get("id")
        if not isinstance(sid, str) or not sid.strip():
            errors.append(f"{p}.id must be a non-empty string")
        elif sid in ids:
            errors.append(f"duplicate scenario id: {sid}")
        else:
            ids.add(sid)
        if s.get("type") not in LEGACY_TYPES:
            errors.append(f"{p}.type is invalid")
        if not isinstance(s.get("prompt"), str) or not s.get("prompt", "").strip():
            errors.append(f"{p}.prompt must be a non-empty string")
        if not isinstance(s.get("expected_behavior"), str) or not s.get("expected_behavior", "").strip():
            errors.append(f"{p}.expected_behavior must be a non-empty string")
        ac = s.get("acceptance_criteria")
        if not isinstance(ac, list) or not ac:
            errors.append(f"{p}.acceptance_criteria must be a non-empty list")
    warnings.append("legacy scenario-suite format accepted for compatibility; new reusable suites should use schema_version=2")


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate a Prompt Architect scenario suite.")
    ap.add_argument("suite")
    args = ap.parse_args()
    path = Path(args.suite)
    errors: list[str] = []
    warnings: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(json.dumps({"status": "fail", "format": "unknown", "errors": [f"invalid JSON: {exc}"], "warnings": []}, indent=2))
        return 1

    if data.get("schema_version") == 2:
        fmt = "v2"
        validate_v2(data, errors, warnings)
    else:
        fmt = "legacy-v1"
        validate_legacy(data, errors, warnings)

    status = "fail" if errors else ("warn" if warnings else "pass")
    print(json.dumps({"status": status, "format": fmt, "errors": errors, "warnings": warnings}, indent=2, ensure_ascii=False, sort_keys=True))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
