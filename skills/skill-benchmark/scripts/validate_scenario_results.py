#!/usr/bin/env python3
"""Validate behavioral scenario result JSON for skill-benchmark."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ALLOWED_CATEGORIES = {"should_activate", "should_not_activate", "ambiguous", "edge_case"}
REQUIRED_FIELDS = {"id", "category", "prompt", "expected_activation", "actual_activation", "output_conforms", "quality_score", "needs_rework"}


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except UnicodeDecodeError:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))


def is_bool_or_null(value: Any) -> bool:
    return value is None or isinstance(value, bool)


def validate_results(data: Any) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    checks: dict[str, Any] = {}

    if not isinstance(data, list):
        return {"status": "fail", "errors": ["scenario results must be a JSON array"], "warnings": [], "checks": {}}
    if not data:
        errors.append("scenario results array is empty")

    seen_ids: set[str] = set()
    categories: dict[str, int] = {}
    measured_rows = 0
    incomplete_rows = 0

    for index, item in enumerate(data):
        label = f"row {index}"
        if not isinstance(item, dict):
            errors.append(f"{label} must be an object")
            continue
        sid = item.get("id")
        label = str(sid or label)
        missing = sorted(REQUIRED_FIELDS - set(item))
        if missing:
            errors.append(f"{label} missing fields: {missing}")
        if not isinstance(sid, str) or not sid.strip():
            errors.append(f"{label} has invalid id")
        elif sid in seen_ids:
            errors.append(f"duplicate id: {sid}")
        else:
            seen_ids.add(sid)

        category = item.get("category")
        if category not in ALLOWED_CATEGORIES:
            errors.append(f"{label} has invalid category: {category!r}")
        else:
            categories[category] = categories.get(category, 0) + 1

        if not isinstance(item.get("prompt"), str) or not item.get("prompt", "").strip():
            errors.append(f"{label} prompt must be a non-empty string")
        if not isinstance(item.get("expected_activation"), bool):
            errors.append(f"{label} expected_activation must be boolean")
        if not is_bool_or_null(item.get("actual_activation")):
            errors.append(f"{label} actual_activation must be boolean or null")
        if not is_bool_or_null(item.get("output_conforms")):
            errors.append(f"{label} output_conforms must be boolean or null")
        if not is_bool_or_null(item.get("needs_rework")):
            errors.append(f"{label} needs_rework must be boolean or null")
        quality = item.get("quality_score")
        if quality is not None and (not isinstance(quality, (int, float)) or quality < 0 or quality > 5):
            errors.append(f"{label} quality_score must be null or a number from 0 to 5")

        actual = item.get("actual_activation")
        conforms = item.get("output_conforms")
        rework = item.get("needs_rework")
        if actual is None or conforms is None or rework is None:
            incomplete_rows += 1
        else:
            measured_rows += 1

    if incomplete_rows:
        warnings.append(f"{incomplete_rows} rows are incomplete and cannot support fully measured behavioral metrics")

    checks = {
        "row_count": len(data),
        "measured_rows": measured_rows,
        "incomplete_rows": incomplete_rows,
        "category_counts": categories,
        "ids_unique": len(seen_ids) == len([item for item in data if isinstance(item, dict) and isinstance(item.get("id"), str)]),
    }
    return {"status": "pass" if not errors else "fail", "errors": errors, "warnings": warnings, "checks": checks}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate skill-benchmark scenario result JSON.")
    parser.add_argument("--results", required=True, help="Path to scenario results JSON array.")
    parser.add_argument("--json-output", help="Optional path for JSON validation evidence.")
    args = parser.parse_args(argv)

    try:
        data = load_json(Path(args.results))
        result = validate_results(data)
    except Exception as exc:
        result = {"status": "fail", "errors": [str(exc)], "warnings": [], "checks": {}}

    if args.json_output:
        out = Path(args.json_output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"wrote {out}")

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
