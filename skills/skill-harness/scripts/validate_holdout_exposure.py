#!/usr/bin/env python3
"""Validate holdout exposure lineage and blind-claim eligibility."""
from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
import json
from pathlib import Path
from typing import Any
from _harness_common import canonical_json_sha256, dump_json


def validate(data: Any) -> dict[str, Any]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return {"status": "fail", "errors": ["ledger must be a JSON object"]}
    if set(data) - {"ledger_version", "holdout_identity", "lineages"}:
        errors.append("ledger contains unknown top-level properties")
    if data.get("ledger_version") != 1:
        errors.append("ledger_version must be 1")
    if not isinstance(data.get("holdout_identity"), str) or not data.get("holdout_identity", "").strip():
        errors.append("holdout_identity must be non-empty")
    rows = data.get("lineages")
    if not isinstance(rows, list) or not rows:
        errors.append("lineages must be a non-empty array")
        rows = []
    ids: set[str] = set()
    blind_eligible = 0
    for i, row in enumerate(rows):
        loc = f"lineages[{i}]"
        allowed = {"lineage_id", "candidate_identity", "holdout_executed", "feedback_revealed_to_mutator", "used_for_mutation", "blind_claim_eligible", "notes"}
        if not isinstance(row, dict):
            errors.append(f"{loc} must be an object")
            continue
        if set(row) - allowed:
            errors.append(f"{loc} contains unknown properties")
        lid = row.get("lineage_id")
        if not isinstance(lid, str) or not lid.strip():
            errors.append(f"{loc}.lineage_id must be non-empty")
        elif lid in ids:
            errors.append(f"duplicate lineage_id: {lid}")
        else:
            ids.add(lid)
        if not isinstance(row.get("candidate_identity"), str) or not row.get("candidate_identity", "").strip():
            errors.append(f"{loc}.candidate_identity must be non-empty")
        for field in ("holdout_executed", "feedback_revealed_to_mutator", "used_for_mutation", "blind_claim_eligible"):
            if not isinstance(row.get(field), bool):
                errors.append(f"{loc}.{field} must be boolean")
        invalidated = row.get("feedback_revealed_to_mutator") is True or row.get("used_for_mutation") is True
        if invalidated and row.get("blind_claim_eligible") is not False:
            errors.append(f"{loc}.blind_claim_eligible must be false after holdout feedback informs mutation")
        if not row.get("holdout_executed") and row.get("blind_claim_eligible") is True:
            errors.append(f"{loc}.blind_claim_eligible cannot be true before the holdout is executed")
        if row.get("blind_claim_eligible") is True:
            blind_eligible += 1
    return {"status": "pass" if not errors else "fail", "identity_sha256": canonical_json_sha256(data), "errors": errors, "lineage_count": len(ids), "blind_eligible_count": blind_eligible}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("ledger")
    ap.add_argument("--json", dest="json_out")
    args = ap.parse_args()
    try:
        report = validate(json.loads(Path(args.ledger).read_text(encoding="utf-8")))
    except Exception as exc:
        report = {"status": "fail", "errors": [str(exc)]}
    dump_json(report, args.json_out)
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
