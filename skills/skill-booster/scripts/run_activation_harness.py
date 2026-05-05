#!/usr/bin/env python3
"""Validate skill-booster activation scenario coverage deterministically.

This harness checks scenario schema, coverage classes, and expected-behavior
contracts. It does not call an LLM or claim behavioral activation precision.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

SCENARIO_TYPES = {"should_activate", "should_not_activate", "ambiguous", "edge_case"}
EXPECTED_PREFIX_BY_TYPE = {
    "should_activate": ("activate",),
    "should_not_activate": ("do_not_activate",),
    "ambiguous": ("clarify_or_", "activate only"),
    "edge_case": ("activate_and_refuse", "refuse", "activate"),
}
MIN_TOTAL = 8


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        raise SystemExit(f"failed to read scenarios: {path}: {exc}") from exc


def validate(data: Any) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(data, dict):
        return {"status": "fail", "errors": ["root must be an object"], "warnings": warnings}

    scenarios = data.get("scenarios")
    if not isinstance(scenarios, list):
        return {"status": "fail", "errors": ["scenarios must be a list"], "warnings": warnings}

    seen_ids: set[str] = set()
    type_counts: Counter[str] = Counter()
    for index, scenario in enumerate(scenarios):
        label = f"scenario[{index}]"
        if not isinstance(scenario, dict):
            errors.append(f"{label}: must be an object")
            continue

        sid = scenario.get("id")
        if not isinstance(sid, str) or not sid.strip():
            errors.append(f"{label}: id is required")
            sid = label
        elif sid in seen_ids:
            errors.append(f"{sid}: duplicate id")
        else:
            seen_ids.add(sid)
        label = str(sid)

        stype = scenario.get("type")
        if stype not in SCENARIO_TYPES:
            errors.append(f"{label}: type must be one of {sorted(SCENARIO_TYPES)}")
            continue
        type_counts[str(stype)] += 1

        prompt = scenario.get("prompt")
        if not isinstance(prompt, str) or len(prompt.strip()) < 12:
            errors.append(f"{label}: prompt is missing or too short")

        expected = scenario.get("expected_behavior")
        prefixes = EXPECTED_PREFIX_BY_TYPE[str(stype)]
        if not isinstance(expected, str) or not expected.strip().startswith(prefixes):
            errors.append(f"{label}: expected_behavior is inconsistent with type {stype}")

        criteria = scenario.get("acceptance_criteria")
        if not isinstance(criteria, list) or not criteria:
            errors.append(f"{label}: acceptance_criteria must be a non-empty list")
        elif not all(isinstance(item, str) and item.strip() for item in criteria):
            errors.append(f"{label}: acceptance_criteria entries must be non-empty strings")

    missing_types = sorted(SCENARIO_TYPES - set(type_counts))
    if missing_types:
        errors.append(f"missing scenario type coverage: {missing_types}")
    if len(scenarios) < MIN_TOTAL:
        warnings.append(f"scenario count {len(scenarios)} is below recommended minimum {MIN_TOTAL}")

    return {
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "warnings": warnings,
        "scenario_count": len(scenarios),
        "type_counts": dict(sorted(type_counts.items())),
        "note": "schema and coverage harness only; no live LLM activation was executed",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate activation scenario schema and coverage.")
    parser.add_argument("--scenarios", required=True, help="Path to activation-scenarios.json")
    parser.add_argument("--json", action="store_true", help="Write JSON result to stdout")
    parser.add_argument("--report", help="Optional JSON report path")
    args = parser.parse_args(argv)

    result = validate(load_json(Path(args.scenarios)))
    text = json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True)
    if args.report:
        Path(args.report).parent.mkdir(parents=True, exist_ok=True)
        Path(args.report).write_text(text + "\n", encoding="utf-8")
    if args.json or not args.report:
        print(text)
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
