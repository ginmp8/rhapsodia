#!/usr/bin/env python3
"""Validate Prompt Architect prompt-contract JSON using only the Python standard library."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ALLOWED_MODES = {"create", "improve", "review-only", "validation-only", "package-guidance"}
ALLOWED_AUTHORITY = {"explicit", "source-required", "inferred", "optional"}
ALLOWED_STATUS = {"preserve", "clarify", "change", "remove", "blocked"}
ALLOWED_FREEZE = {"frozen", "planned", "not-applicable"}
ALLOWED_CLAIM = {"structural", "behavioral", "runtime"}
ALLOWED_CITATIONS = {"required", "optional", "forbidden", "not-applicable"}


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate a Prompt Architect prompt contract.")
    ap.add_argument("contract")
    args = ap.parse_args()
    path = Path(args.contract)
    errors: list[str] = []
    warnings: list[str] = []

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(json.dumps({"status": "fail", "errors": [f"invalid JSON: {exc}"], "warnings": []}, indent=2))
        return 1

    if data.get("contract_version") != 1:
        errors.append("contract_version must be 1")

    target = data.get("target")
    if not isinstance(target, dict):
        errors.append("target must be an object")
    else:
        for key in ("name", "kind", "executor", "language"):
            if not isinstance(target.get(key), str) or not target.get(key, "").strip():
                errors.append(f"target.{key} must be a non-empty string")

    if data.get("mode") not in ALLOWED_MODES:
        errors.append("mode is invalid")

    inputs = data.get("inputs")
    if not isinstance(inputs, dict):
        errors.append("inputs must be an object")
    else:
        for key in ("available", "tools", "sources"):
            if not isinstance(inputs.get(key), list):
                errors.append(f"inputs.{key} must be a list")

    requirements = data.get("requirements")
    seen_ids: set[str] = set()
    if not isinstance(requirements, list) or not requirements:
        errors.append("requirements must be a non-empty list")
    else:
        for i, req in enumerate(requirements):
            prefix = f"requirements[{i}]"
            if not isinstance(req, dict):
                errors.append(f"{prefix} must be an object")
                continue
            rid = req.get("id")
            if not isinstance(rid, str) or not rid.strip():
                errors.append(f"{prefix}.id must be a non-empty string")
            elif rid in seen_ids:
                errors.append(f"duplicate requirement id: {rid}")
            else:
                seen_ids.add(rid)
            if not isinstance(req.get("text"), str) or not req.get("text", "").strip():
                errors.append(f"{prefix}.text must be a non-empty string")
            if req.get("authority") not in ALLOWED_AUTHORITY:
                errors.append(f"{prefix}.authority is invalid")
            if not isinstance(req.get("protected"), bool):
                errors.append(f"{prefix}.protected must be boolean")
            if not isinstance(req.get("source"), str) or not req.get("source", "").strip():
                errors.append(f"{prefix}.source must be a non-empty string")
            if req.get("status") not in ALLOWED_STATUS:
                errors.append(f"{prefix}.status is invalid")
            if req.get("protected") is True and req.get("status") in {"change", "remove"} and not str(req.get("reason", "")).strip():
                errors.append(f"{prefix} changes/removes a protected requirement without a reason")

    output = data.get("output")
    if not isinstance(output, dict):
        errors.append("output must be an object")
    else:
        for key in ("format", "language", "citations", "ordering", "unknown_or_error_behavior"):
            if not isinstance(output.get(key), str) or not output.get(key, "").strip():
                errors.append(f"output.{key} must be a non-empty string")
        if output.get("citations") not in ALLOWED_CITATIONS:
            errors.append("output.citations is invalid")
        if not isinstance(output.get("sections"), list):
            errors.append("output.sections must be a list")

    if not isinstance(data.get("success_criteria"), list) or not data.get("success_criteria"):
        errors.append("success_criteria must be a non-empty list")
    if not isinstance(data.get("assumptions"), list):
        errors.append("assumptions must be a list")
    if not isinstance(data.get("unresolved_conflicts"), list):
        errors.append("unresolved_conflicts must be a list")

    validation = data.get("validation")
    if not isinstance(validation, dict):
        errors.append("validation must be an object")
    else:
        if validation.get("freeze_state") not in ALLOWED_FREEZE:
            errors.append("validation.freeze_state is invalid")
        if validation.get("claim_level") not in ALLOWED_CLAIM:
            errors.append("validation.claim_level is invalid")
        if validation.get("claim_level") in {"behavioral", "runtime"} and validation.get("freeze_state") != "frozen":
            errors.append("behavioral/runtime claim_level requires validation.freeze_state=frozen")
        if validation.get("claim_level") == "behavioral" and not str(validation.get("suite_id", "")).strip():
            errors.append("behavioral claim_level requires validation.suite_id")
        if validation.get("claim_level") == "runtime" and not str(validation.get("suite_id", "")).strip():
            errors.append("runtime claim_level requires validation.suite_id")

    blocked = [r for r in requirements or [] if isinstance(r, dict) and r.get("status") == "blocked"] if isinstance(requirements, list) else []
    if blocked and data.get("mode") in {"create", "improve"}:
        warnings.append("contract contains blocked requirements; final prompt should not silently resolve them")

    status = "fail" if errors else ("warn" if warnings else "pass")
    print(json.dumps({"status": status, "errors": errors, "warnings": warnings}, indent=2, ensure_ascii=False, sort_keys=True))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
