#!/usr/bin/env python3
"""Validate final Skill Booster promotion attestation and exact artifact identities."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

IDENTITY_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
PASS_STATES = {"pass", "pass-with-warnings", "not-applicable"}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def manifest_identity(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    digest = data.get("candidate_sha256")
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise ValueError("candidate manifest lacks candidate_sha256")
    return f"sha256:{digest}"


def valid_identity(value: Any) -> bool:
    return isinstance(value, str) and bool(IDENTITY_RE.fullmatch(value))


def validate(data: Any, candidate_manifest: Path | None = None, archive: Path | None = None) -> dict:
    errors: list[str] = []
    if not isinstance(data, dict):
        return {"status": "fail", "errors": ["[ROOT] attestation must be an object"]}
    if data.get("schema_version") != 1:
        errors.append("[SCHEMA] schema_version must be 1")
    for field in ("controller_identity", "baseline_identity", "candidate_identity", "evaluator_set_identity", "source_set_identity"):
        if not valid_identity(data.get(field)):
            errors.append(f"[IDENTITY] {field} must be sha256:<64hex>")
    decision = data.get("decision")
    if not isinstance(decision, dict):
        errors.append("[DECISION] decision must be an object")
        decision = {}
    if decision.get("target_promotion") not in {"accept", "reject"}:
        errors.append("[DECISION] target_promotion must be accept or reject")
    if decision.get("workflow_policy_promotion") not in {"unchanged", "recommend-review"}:
        errors.append("[DECISION] workflow_policy_promotion must remain separate from target promotion")
    if decision.get("approved_candidate_identity") != data.get("candidate_identity"):
        errors.append("[CANDIDATE] approved_candidate_identity must equal candidate_identity")
    evidence = data.get("evidence")
    if not isinstance(evidence, dict):
        errors.append("[EVIDENCE] evidence must be an object")
        evidence = {}
    required = ("run_state", "validation_receipt", "change_gate", "portability", "traceability", "integration")
    for key in required:
        row = evidence.get(key)
        if not isinstance(row, dict):
            errors.append(f"[EVIDENCE] {key} evidence is required")
            continue
        if not isinstance(row.get("identity"), str) or not row["identity"].strip():
            errors.append(f"[EVIDENCE] {key}.identity is required")
        if row.get("status") not in PASS_STATES:
            errors.append(f"[EVIDENCE] {key}.status is not promotion-safe")
    delivery = data.get("delivery")
    if not isinstance(delivery, dict):
        errors.append("[DELIVERY] delivery must be an object")
        delivery = {}
    package_required = delivery.get("package_required")
    if not isinstance(package_required, bool):
        errors.append("[DELIVERY] package_required must be boolean")
    package_identity = delivery.get("package_sha256")
    if package_required and not valid_identity(package_identity):
        errors.append("[DELIVERY] package_sha256 is required when package_required=true")
    if candidate_manifest:
        expected = manifest_identity(candidate_manifest)
        if data.get("candidate_identity") != expected:
            errors.append("[CANDIDATE] attested candidate differs from candidate manifest")
    if archive:
        expected = f"sha256:{sha256_file(archive)}"
        if package_identity != expected:
            errors.append("[DELIVERY] attested package hash differs from archive bytes")
    if decision.get("target_promotion") == "accept" and errors:
        pass
    return {"status": "pass" if not errors else "fail", "errors": errors}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Skill Booster promotion attestation.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--candidate-manifest")
    parser.add_argument("--archive")
    parser.add_argument("--json")
    args = parser.parse_args()
    try:
        report = validate(
            json.loads(Path(args.input).read_text(encoding="utf-8")),
            Path(args.candidate_manifest) if args.candidate_manifest else None,
            Path(args.archive) if args.archive else None,
        )
    except Exception as exc:
        report = {"status": "fail", "errors": [f"[EXCEPTION] {exc}"]}
    rendered = json.dumps(report, indent=2, ensure_ascii=False)
    print(rendered)
    if args.json:
        Path(args.json).write_text(rendered + "\n", encoding="utf-8")
    return 0 if report.get("status") == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
