#!/usr/bin/env python3
"""Validate optional executable consumer-contract evidence for ecosystem promotion."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

IDENTITY_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate(data: Any, require_all_pass: bool = False) -> dict:
    errors: list[str] = []
    if not isinstance(data, dict):
        return {"status": "fail", "errors": ["[ROOT] evidence must be an object"], "verification_count": 0}
    if data.get("schema_version") != 1:
        errors.append("[SCHEMA] schema_version must be 1")
    fingerprint = data.get("deployment_catalog_fingerprint")
    if not isinstance(fingerprint, str) or not IDENTITY_RE.fullmatch(fingerprint):
        errors.append("[CATALOG] deployment_catalog_fingerprint must be sha256:<64hex>")
    rows = data.get("verifications")
    if not isinstance(rows, list):
        errors.append("[VERIFICATIONS] verifications must be a list")
        rows = []
    seen: set[tuple[str, str, str, str, str]] = set()
    failed: list[str] = []
    for i, row in enumerate(rows):
        if not isinstance(row, dict):
            errors.append(f"[ROW] verifications[{i}] must be an object")
            continue
        fields = ("contract_id", "consumer_skill", "provider_skill", "consumer_version", "provider_version", "evidence_identity")
        for field in fields:
            if not nonempty(row.get(field)):
                errors.append(f"[ROW] verifications[{i}].{field} is required")
        if nonempty(row.get("evidence_identity")) and not IDENTITY_RE.fullmatch(row["evidence_identity"]):
            errors.append(f"[ROW] verifications[{i}].evidence_identity must be sha256:<64hex>")
        status = row.get("status")
        if status not in {"pass", "fail", "blocked"}:
            errors.append(f"[ROW] verifications[{i}].status is invalid")
        key = tuple(str(row.get(f, "")) for f in ("contract_id", "consumer_skill", "provider_skill", "consumer_version", "provider_version"))
        if key in seen:
            errors.append(f"[DUPLICATE] duplicate verification tuple at index {i}")
        seen.add(key)
        if status != "pass":
            failed.append(str(row.get("contract_id", i)))
    if require_all_pass and failed:
        errors.append("[CONTRACT_GATE] one or more required consumer-contract verifications did not pass: " + ", ".join(sorted(failed)))
    status = "pass" if not errors else "fail"
    return {"status": status, "errors": errors, "verification_count": len(rows), "nonpassing_contracts": sorted(failed)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate consumer-contract verification evidence.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--require-all-pass", action="store_true")
    parser.add_argument("--json")
    args = parser.parse_args()
    try:
        report = validate(json.loads(Path(args.input).read_text(encoding="utf-8")), args.require_all_pass)
    except Exception as exc:
        report = {"status": "fail", "errors": [f"[EXCEPTION] {exc}"], "verification_count": 0}
    rendered = json.dumps(report, indent=2, ensure_ascii=False)
    print(rendered)
    if args.json:
        Path(args.json).write_text(rendered + "\n", encoding="utf-8")
    return 0 if report.get("status") == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
