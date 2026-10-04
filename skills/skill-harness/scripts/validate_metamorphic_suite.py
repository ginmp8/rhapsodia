#!/usr/bin/env python3
"""Validate metamorphic-suite structure and measured-result completeness."""
from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
import json
from pathlib import Path
from typing import Any
from _harness_common import canonical_json_sha256, dump_json

RELATIONS = {"same-routing", "same-hard-gates", "same-core-semantics", "equivalent-outcome", "monotonic", "custom"}


def validate(data: Any) -> dict[str, Any]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return {"status": "fail", "errors": ["suite must be a JSON object"], "metrics": {}}
    if set(data) - {"suite_version", "target_skill", "status", "groups"}:
        errors.append("suite contains unknown top-level properties")
    if data.get("suite_version") != 1:
        errors.append("suite_version must be 1")
    if not isinstance(data.get("target_skill"), str) or not data.get("target_skill", "").strip():
        errors.append("target_skill must be a non-empty string")
    status = data.get("status")
    if status not in {"planned", "measured"}:
        errors.append("status must be planned or measured")
    groups = data.get("groups")
    if not isinstance(groups, list) or not groups:
        errors.append("groups must be a non-empty array")
        groups = []
    group_ids: set[str] = set()
    variant_ids: set[str] = set()
    measured_results = 0
    for i, group in enumerate(groups):
        loc = f"groups[{i}]"
        if not isinstance(group, dict):
            errors.append(f"{loc} must be an object")
            continue
        if set(group) - {"id", "base_case_id", "relation", "custom_relation", "evaluator_identity", "variants"}:
            errors.append(f"{loc} contains unknown properties")
        gid = group.get("id")
        if not isinstance(gid, str) or not gid.strip():
            errors.append(f"{loc}.id must be non-empty")
        elif gid in group_ids:
            errors.append(f"duplicate group id: {gid}")
        else:
            group_ids.add(gid)
        if not isinstance(group.get("base_case_id"), str) or not group.get("base_case_id", "").strip():
            errors.append(f"{loc}.base_case_id must be non-empty")
        relation = group.get("relation")
        if relation not in RELATIONS:
            errors.append(f"{loc}.relation must be one of {sorted(RELATIONS)}")
        if relation == "custom" and (not isinstance(group.get("custom_relation"), str) or not group.get("custom_relation", "").strip()):
            errors.append(f"{loc}.custom_relation is required for custom relation")
        variants = group.get("variants")
        if not isinstance(variants, list) or not variants:
            errors.append(f"{loc}.variants must be non-empty")
            continue
        for j, row in enumerate(variants):
            vloc = f"{loc}.variants[{j}]"
            if not isinstance(row, dict):
                errors.append(f"{vloc} must be an object")
                continue
            if set(row) - {"id", "transformation", "result", "evidence_identity"}:
                errors.append(f"{vloc} contains unknown properties")
            vid = row.get("id")
            if not isinstance(vid, str) or not vid.strip():
                errors.append(f"{vloc}.id must be non-empty")
            elif vid in variant_ids:
                errors.append(f"duplicate variant id: {vid}")
            else:
                variant_ids.add(vid)
            if not isinstance(row.get("transformation"), str) or not row.get("transformation", "").strip():
                errors.append(f"{vloc}.transformation must be non-empty")
            if status == "measured":
                if row.get("result") not in {"pass", "fail"}:
                    errors.append(f"{vloc}.result must be pass or fail for measured suites")
                else:
                    measured_results += 1
                if not isinstance(row.get("evidence_identity"), str) or not row.get("evidence_identity", "").strip():
                    errors.append(f"{vloc}.evidence_identity is required for measured suites")
    metrics = {"group_count": len(group_ids), "variant_count": len(variant_ids), "measured_result_count": measured_results}
    return {"status": "pass" if not errors else "fail", "identity_sha256": canonical_json_sha256(data), "errors": errors, "metrics": metrics}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("suite")
    ap.add_argument("--json", dest="json_out")
    args = ap.parse_args()
    try:
        report = validate(json.loads(Path(args.suite).read_text(encoding="utf-8")))
    except Exception as exc:
        report = {"status": "fail", "errors": [str(exc)], "metrics": {}}
    dump_json(report, args.json_out)
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
