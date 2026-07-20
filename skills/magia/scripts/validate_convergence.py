#!/usr/bin/env python3
"""Validate a MAGIA requirement-to-evidence convergence report."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

STATUSES = {
    "satisfied", "partially_satisfied", "unsatisfied", "obsolete",
    "unverified", "out_of_scope", "planning_change_required",
}
REQUIRED = {"id", "requirement", "acceptance_criteria", "tasks", "changed_files", "checks", "evidence", "status"}


def validate(payload: Any, require_complete: bool = False) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(payload, dict):
        return {"status": "fail", "errors": ["root must be an object"], "warnings": [], "counts": {}}
    profile = payload.get("profile")
    if profile not in {"quick", "standard", "governed"}:
        errors.append("profile must be quick, standard, or governed")
    items = payload.get("items")
    if not isinstance(items, list) or not items:
        errors.append("items must be a non-empty list")
        items = []
    seen: set[str] = set()
    counts: Counter[str] = Counter()
    for index, item in enumerate(items):
        label = f"item[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label} must be an object")
            continue
        missing = sorted(REQUIRED - set(item))
        if missing:
            errors.append(f"{label} missing fields: {missing}")
            continue
        item_id = item.get("id")
        if not isinstance(item_id, str) or not item_id.strip():
            errors.append(f"{label} id must be a non-empty string")
        elif item_id in seen:
            errors.append(f"duplicate item id: {item_id}")
        else:
            seen.add(item_id)
        status = item.get("status")
        if status not in STATUSES:
            errors.append(f"{item_id or label} invalid status: {status}")
        else:
            counts[status] += 1
        for field in ("acceptance_criteria", "tasks", "changed_files", "checks", "evidence"):
            value = item.get(field)
            if not isinstance(value, list) or not all(isinstance(entry, str) and entry.strip() for entry in value):
                errors.append(f"{item_id or label} {field} must be a string list")
        if profile == "governed" and status == "satisfied":
            for field in ("acceptance_criteria", "tasks", "changed_files", "checks", "evidence"):
                if not item.get(field):
                    errors.append(f"{item_id or label} governed satisfied item requires {field}")
        if status == "obsolete" and not str(item.get("notes", "")).strip():
            warnings.append(f"{item_id or label} obsolete item should cite superseding authority in notes")
        if status == "out_of_scope" and not str(item.get("notes", "")).strip():
            warnings.append(f"{item_id or label} out_of_scope item should explain exclusion in notes")

    blocking = sum(counts[name] for name in ("partially_satisfied", "unsatisfied", "unverified", "planning_change_required"))
    if require_complete and blocking:
        errors.append(f"complete convergence required but {blocking} blocking items remain")
    if profile == "governed" and counts["out_of_scope"]:
        warnings.append("governed out_of_scope items require owning-authority acceptance outside MAGIA")
    result_status = "fail" if errors else "pass_with_warnings" if warnings else "pass"
    return {
        "status": result_status,
        "errors": errors,
        "warnings": warnings,
        "counts": dict(sorted(counts.items())),
        "blocking_count": blocking,
        "item_count": len(items),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--require-complete", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args(argv)
    try:
        payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
        result = validate(payload, args.require_complete)
    except (OSError, json.JSONDecodeError) as exc:
        result = {"status": "fail", "errors": [str(exc)], "warnings": [], "counts": {}}
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if result["status"] in {"pass", "pass_with_warnings"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
