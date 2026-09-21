#!/usr/bin/env python3
"""Validate a Skill Improver self-improvement promotion receipt."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

SHA_RE = re.compile(r"^[0-9a-f]{64}$")
DECISIONS = {"promote", "reject", "hold"}
GATE_STATUSES = {"pass", "pass-with-warnings", "fail", "insufficient-evidence", "not-run"}


def _sha(value: Any) -> bool:
    return isinstance(value, str) and bool(SHA_RE.fullmatch(value))


def validate(data: Any) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(data, dict):
        return {"status": "fail", "errors": ["receipt must be a JSON object"], "warnings": [], "checks": {}}
    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    for field in ("run_id", "generation_id"):
        if not isinstance(data.get(field), str) or not data.get(field, "").strip():
            errors.append(f"{field} must be a non-empty string")
    sha_fields = (
        "controller_identity_sha256",
        "baseline_identity_sha256",
        "candidate_identity_sha256",
        "evaluator_identity_sha256",
        "last_known_good_identity_sha256",
    )
    for field in sha_fields:
        if not _sha(data.get(field)):
            errors.append(f"{field} must be lowercase 64-hex")
    controller = data.get("controller_identity_sha256")
    candidate = data.get("candidate_identity_sha256")
    if _sha(controller) and _sha(candidate) and controller == candidate:
        errors.append("controller_identity_sha256 must differ from candidate_identity_sha256")
    depth = data.get("max_self_recursion_depth")
    if not isinstance(depth, int) or isinstance(depth, bool) or depth < 1:
        errors.append("max_self_recursion_depth must be an integer >= 1")
    if isinstance(depth, int) and depth > 1:
        warnings.append("self recursion depth > 1 requires explicit justification; default is 1")
    for field in ("controller_unchanged", "evaluator_unchanged", "candidate_frozen", "external_validation_surface"):
        if not isinstance(data.get(field), bool):
            errors.append(f"{field} must be boolean")
    gate = data.get("gate_status")
    if gate not in GATE_STATUSES:
        errors.append(f"gate_status must be one of {sorted(GATE_STATUSES)}")
    decision = data.get("decision")
    if decision not in DECISIONS:
        errors.append(f"decision must be one of {sorted(DECISIONS)}")
    promoted = data.get("promoted_identity_sha256")
    if decision == "promote":
        if gate not in {"pass", "pass-with-warnings"}:
            errors.append("decision=promote requires a passing gate_status")
        for field in ("controller_unchanged", "evaluator_unchanged", "candidate_frozen", "external_validation_surface"):
            if data.get(field) is not True:
                errors.append(f"decision=promote requires {field}=true")
        if not _sha(promoted):
            errors.append("decision=promote requires promoted_identity_sha256")
        elif _sha(candidate) and promoted != candidate:
            errors.append("promoted_identity_sha256 must equal candidate_identity_sha256")
    else:
        if promoted not in (None, ""):
            warnings.append("non-promote decision should not declare promoted_identity_sha256")
    checks = {
        "controller_candidate_separated": bool(_sha(controller) and _sha(candidate) and controller != candidate),
        "recursion_depth": depth,
        "gate_status": gate,
        "decision": decision,
        "promotion_identity_matches_candidate": bool(decision == "promote" and _sha(promoted) and promoted == candidate),
    }
    return {"status": "pass" if not errors else "fail", "errors": errors, "warnings": warnings, "checks": checks}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("receipt")
    ap.add_argument("--json", dest="json_output")
    args = ap.parse_args()
    try:
        data = json.loads(Path(args.receipt).read_text(encoding="utf-8"))
        report = validate(data)
    except Exception as exc:
        report = {"status": "fail", "errors": [str(exc)], "warnings": [], "checks": {}}
    payload = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.json_output:
        Path(args.json_output).write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
