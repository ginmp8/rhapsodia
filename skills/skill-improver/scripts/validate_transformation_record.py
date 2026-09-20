#!/usr/bin/env python3
"""Validate a portable Skill Improver transformation decision record."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

INTENTS = {"repair", "optimization", "experiment"}
STATUS = {"planned", "applied", "accepted", "rejected", "reverted"}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("record")
    args = p.parse_args()
    try:
        data = json.loads(Path(args.record).read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"status": "fail", "errors": [str(exc)]}, indent=2))
        return 1
    errors = []
    for field in ("transformation_id", "hypothesis_id", "parent_identity", "operation_summary", "expected_effect", "evaluator_identity"):
        if not isinstance(data.get(field), str) or not data.get(field, "").strip():
            errors.append(f"{field} is required")
    if data.get("change_intent") not in INTENTS:
        errors.append("change_intent is invalid")
    if data.get("status") not in STATUS:
        errors.append("status is invalid")
    for field in ("capability_refs", "files", "evidence_refs"):
        value = data.get(field)
        if not isinstance(value, list) or any(not isinstance(x, str) or not x for x in value):
            errors.append(f"{field} must be a list of non-empty strings")
    report = {"status": "fail" if errors else "pass", "errors": errors}
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
