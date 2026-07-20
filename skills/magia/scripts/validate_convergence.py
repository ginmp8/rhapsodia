#!/usr/bin/env python3
"""Validate requirement-to-evidence convergence records."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

STATUSES = {"satisfied", "partially_satisfied", "unsatisfied", "obsolete", "unverified", "out_of_scope", "planning_change_required"}
BLOCKING = {"partially_satisfied", "unsatisfied", "unverified", "planning_change_required"}
HANDOFFS = {"none", "mago", "nomia", "both"}
REQUIRED_ITEM_FIELDS = {"id", "requirement", "acceptance_criteria", "tasks", "changed_files", "checks", "evidence", "status", "reason", "handoff"}


def validate_convergence(data: Any) -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["convergence root must be an object"], {}
    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    scope_type = data.get("scope_type")
    if scope_type not in {"adhoc", "planned"}:
        errors.append("scope_type must be adhoc or planned")
    modified_files = data.get("modified_files")
    items = data.get("items")
    if not isinstance(modified_files, list) or not all(isinstance(x, str) and x.strip() for x in modified_files):
        errors.append("modified_files must be an array of non-empty paths")
        modified_files = []
    if not isinstance(items, list) or not items:
        errors.append("items must be a non-empty array")
        items = []

    seen_ids: set[str] = set()
    linked_files: set[str] = set()
    counts = {status: 0 for status in sorted(STATUSES)}
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append(f"items[{index}] must be an object")
            continue
        missing = REQUIRED_ITEM_FIELDS - set(item)
        sid = item.get("id") or f"index {index}"
        if missing:
            errors.append(f"item {sid} missing fields: {sorted(missing)}")
        if not isinstance(item.get("id"), str) or not item.get("id", "").strip():
            errors.append(f"items[{index}].id must be non-empty")
        elif item["id"] in seen_ids:
            errors.append(f"duplicate item id: {item['id']}")
        else:
            seen_ids.add(item["id"])
        status = item.get("status")
        if status not in STATUSES:
            errors.append(f"item {sid} has invalid status: {status}")
        else:
            counts[status] += 1
        handoff = item.get("handoff")
        if handoff not in HANDOFFS:
            errors.append(f"item {sid} has invalid handoff: {handoff}")
        for field in ("acceptance_criteria", "tasks", "changed_files", "checks", "evidence"):
            if not isinstance(item.get(field), list):
                errors.append(f"item {sid} {field} must be an array")
        files = item.get("changed_files") if isinstance(item.get("changed_files"), list) else []
        checks = item.get("checks") if isinstance(item.get("checks"), list) else []
        evidence = item.get("evidence") if isinstance(item.get("evidence"), list) else []
        linked_files.update(value for value in files if isinstance(value, str))
        if status == "satisfied":
            if not isinstance(item.get("requirement"), str) or not item.get("requirement", "").strip():
                errors.append(f"satisfied item {sid} requires requirement text")
            if not item.get("acceptance_criteria"):
                errors.append(f"satisfied item {sid} requires acceptance criteria")
            if scope_type == "planned" and not item.get("tasks"):
                errors.append(f"planned satisfied item {sid} requires task ids")
            if files and not checks:
                errors.append(f"satisfied item {sid} with changed files requires checks")
            if files and not evidence:
                errors.append(f"satisfied item {sid} with changed files requires evidence")
        if status in {"obsolete", "out_of_scope", "partially_satisfied", "unsatisfied", "unverified", "planning_change_required"}:
            if not isinstance(item.get("reason"), str) or not item.get("reason", "").strip():
                errors.append(f"item {sid} status {status} requires a reason")
        if status == "planning_change_required" and handoff not in {"mago", "both"}:
            errors.append(f"item {sid} planning change requires Mago handoff")

    unlinked = sorted(set(modified_files) - linked_files)
    if unlinked:
        errors.append(f"modified files are not linked to convergence items: {unlinked}")
    blocking_count = sum(counts[status] for status in BLOCKING)
    summary = {
        "counts": counts,
        "blocking_count": blocking_count,
        "unlinked_files": unlinked,
        "completion_allowed": not errors and blocking_count == 0,
        "final_status": "satisfied" if not errors and blocking_count == 0 else "blocked",
    }
    return errors, summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate MAGIA convergence JSON.")
    parser.add_argument("--input", required=True, help="Convergence JSON path.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable result.")
    args = parser.parse_args(argv)
    try:
        payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
        errors, summary = validate_convergence(payload)
        result = {"status": "pass" if not errors else "fail", "errors": errors, "summary": summary}
    except Exception as exc:  # noqa: BLE001
        result = {"status": "fail", "errors": [str(exc)], "summary": {}}
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"status: {result['status']}")
        for error in result["errors"]:
            print(f"error: {error}")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
