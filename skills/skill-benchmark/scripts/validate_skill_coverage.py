#!/usr/bin/env python3
"""Validate constraint-level Skill Coverage evidence and compute test-adequacy metrics."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from _common import dump_json

SHA_RE = re.compile(r"^[0-9a-f]{64}$")
STATUSES = {"not_applicable", "uncovered", "covered_pass", "covered_fail"}


def validate(data: Any) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(data, dict):
        return {"status": "fail", "errors": ["coverage evidence must be an object"], "warnings": []}
    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    for field in ("skill_identity_sha256", "constraint_set_sha256"):
        value = data.get(field)
        if not isinstance(value, str) or not SHA_RE.fullmatch(value):
            errors.append(f"{field} must be lowercase 64-hex")
    constraints = data.get("constraints")
    results = data.get("results")
    if not isinstance(constraints, list) or not constraints:
        errors.append("constraints must be a non-empty array")
        constraints = []
    if not isinstance(results, list):
        errors.append("results must be an array")
        results = []
    cids: set[str] = set()
    for i, row in enumerate(constraints):
        if not isinstance(row, dict):
            errors.append(f"constraint[{i}] must be an object")
            continue
        cid = row.get("id")
        if not isinstance(cid, str) or not cid.strip():
            errors.append(f"constraint[{i}].id must be non-empty")
            continue
        if cid in cids:
            errors.append(f"duplicate constraint id: {cid}")
        cids.add(cid)
        for field in ("source", "condition", "expected_behavior"):
            if not isinstance(row.get(field), str) or not row.get(field, "").strip():
                errors.append(f"{cid}.{field} must be non-empty text")
    statuses: dict[str, str] = {}
    for i, row in enumerate(results):
        if not isinstance(row, dict):
            errors.append(f"result[{i}] must be an object")
            continue
        cid = row.get("constraint_id")
        status = row.get("status")
        if cid not in cids:
            errors.append(f"result[{i}].constraint_id does not resolve: {cid!r}")
            continue
        if cid in statuses:
            errors.append(f"duplicate result for constraint: {cid}")
        if status not in STATUSES:
            errors.append(f"{cid}.status must be one of {sorted(STATUSES)}")
        else:
            statuses[cid] = status
    missing = sorted(cids - set(statuses))
    if missing:
        errors.append("missing results for constraints: " + ", ".join(missing))
    counts = {status: sum(1 for v in statuses.values() if v == status) for status in sorted(STATUSES)}
    applicable = len(cids) - counts["not_applicable"]
    covered = counts["covered_pass"] + counts["covered_fail"]
    coverage = None if applicable == 0 else covered / applicable
    adherence = None if covered == 0 else counts["covered_pass"] / covered
    if applicable == 0:
        warnings.append("all constraints are not_applicable; coverage is undefined")
    return {
        "status": "fail" if errors else "pass",
        "errors": errors,
        "warnings": warnings,
        "metrics": {
            "constraint_count": len(cids),
            "applicable_count": applicable,
            "covered_count": covered,
            "coverage": coverage,
            "covered_adherence": adherence,
            "status_counts": counts,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--coverage", required=True)
    parser.add_argument("--json-output")
    args = parser.parse_args()
    try:
        data = json.loads(Path(args.coverage).read_text(encoding="utf-8"))
        report = validate(data)
    except Exception as exc:
        report = {"status": "fail", "errors": [str(exc)], "warnings": []}
    dump_json(report, args.json_output)
    if args.json_output:
        dump_json(report)
    return 1 if report.get("status") == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
