#!/usr/bin/env python3
"""Validate Nomia's machine-readable assurance and evidence traceability contract."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from nomia_utils import atomic_write_text

EVIDENCE_STATUSES = {"measured", "observed", "planned"}
CRITICAL_GATES = {f"G{index}" for index in range(1, 9)}
REQUIRED_FIELDS = {
    "id",
    "statement",
    "evidence_status",
    "critical_gates",
    "artifacts",
    "validators",
    "ledger_gates",
    "limitations",
}


def load_contract(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("assurance contract must be a JSON object")
    return data


def validate_assurance_contract(root: Path, contract_path: Path | None = None) -> dict[str, Any]:
    root = root.resolve()
    path = (contract_path or root / "references" / "assurance-contract.json").resolve()
    errors: list[str] = []
    warnings: list[str] = []
    try:
        contract = load_contract(path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return {"status": "fail", "errors": [str(exc)], "warnings": [], "claim_count": 0}
    if contract.get("schema_version") != 1:
        errors.append("assurance contract schema_version must be 1")
    if contract.get("skill") != "nomia":
        errors.append("assurance contract skill must be nomia")
    claims = contract.get("claims")
    if not isinstance(claims, list) or not claims:
        return {"status": "fail", "errors": errors + ["assurance contract claims must be a non-empty list"], "warnings": warnings, "claim_count": 0}

    seen: set[str] = set()
    gate_coverage: set[str] = set()
    evidence_counts: Counter[str] = Counter()
    for index, claim in enumerate(claims):
        if not isinstance(claim, dict):
            errors.append(f"claim {index} must be an object")
            continue
        claim_id = claim.get("id", index)
        missing = sorted(REQUIRED_FIELDS - set(claim))
        if missing:
            errors.append(f"claim {claim_id} missing fields: {', '.join(missing)}")
        if not isinstance(claim_id, str) or not claim_id:
            errors.append(f"claim {index} id is required")
        elif claim_id in seen:
            errors.append(f"duplicate assurance claim id: {claim_id}")
        else:
            seen.add(claim_id)
        statement = claim.get("statement")
        if not isinstance(statement, str) or len(statement.strip()) < 40:
            errors.append(f"claim {claim_id} statement is too short")
        status = claim.get("evidence_status")
        if status not in EVIDENCE_STATUSES:
            errors.append(f"claim {claim_id} has invalid evidence_status: {status}")
        else:
            evidence_counts[status] += 1
        critical = claim.get("critical_gates")
        if not isinstance(critical, list) or not all(item in CRITICAL_GATES for item in critical):
            errors.append(f"claim {claim_id} critical_gates must contain only G1..G8")
        else:
            gate_coverage.update(critical)
        for field in ("artifacts", "validators", "ledger_gates", "limitations"):
            value = claim.get(field)
            if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
                errors.append(f"claim {claim_id} {field} must be a string list")
        for rel in claim.get("artifacts", []) + claim.get("validators", []):
            candidate = (root / rel).resolve()
            try:
                candidate.relative_to(root)
            except ValueError:
                errors.append(f"claim {claim_id} path escapes skill root: {rel}")
                continue
            if not candidate.is_file():
                errors.append(f"claim {claim_id} references missing file: {rel}")
        if status == "measured" and not claim.get("validators"):
            errors.append(f"measured claim {claim_id} requires at least one validator")
        if status == "measured" and not claim.get("ledger_gates"):
            errors.append(f"measured claim {claim_id} requires at least one ledger gate")
        if status == "planned" and claim.get("ledger_gates"):
            warnings.append(f"planned claim {claim_id} has ledger gates; ensure they do not imply behavioral measurement")
        if "activation precision" in str(statement).lower() and status != "planned":
            errors.append(f"claim {claim_id} activation precision must remain planned without executed results")

    missing_critical = sorted(CRITICAL_GATES - gate_coverage)
    if missing_critical:
        errors.append(f"assurance contract does not cover critical gates: {', '.join(missing_critical)}")
    return {
        "target": str(root),
        "contract": str(path),
        "status": "pass" if not errors else "fail",
        "claim_count": len(claims),
        "evidence_counts": dict(sorted(evidence_counts.items())),
        "critical_gate_coverage": sorted(gate_coverage),
        "errors": errors,
        "warnings": warnings,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Nomia assurance traceability.")
    parser.add_argument("--target", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--contract")
    parser.add_argument("--json-output")
    args = parser.parse_args(argv)
    result = validate_assurance_contract(Path(args.target), Path(args.contract) if args.contract else None)
    if args.json_output:
        output = Path(args.json_output).resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        atomic_write_text(output, json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"status: {result['status']}")
    print(f"claim_count: {result['claim_count']}")
    print(f"critical_gate_coverage: {','.join(result.get('critical_gate_coverage', []))}")
    for warning in result.get("warnings", []):
        print(f"WARNING: {warning}")
    for error in result.get("errors", []):
        print(f"ERROR: {error}")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
