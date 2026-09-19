#!/usr/bin/env python3
"""Validate the machine-readable package architecture review contract."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "1.0.0"
RUBRIC_VERSION = "2.0.0"
DECISIONS = {"keep_unified", "split", "extract_mode", "create_router", "merge_resources", "no_change"}
OBSERVATION_KINDS = {"mechanical", "declared-contract", "behavioral", "supplied", "derived"}
CONFIDENCE = {"low", "medium", "high"}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate(data: Any) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(data, dict):
        return {"status": "fail", "errors": ["report root must be an object"], "warnings": []}

    if data.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    if data.get("rubric_version") != RUBRIC_VERSION:
        errors.append(f"rubric_version must be {RUBRIC_VERSION}")

    target = data.get("target")
    if not isinstance(target, dict):
        errors.append("target must be an object")
    else:
        if not _nonempty(target.get("name")):
            errors.append("target.name is required")
        identity = target.get("package_identity_sha256")
        if not isinstance(identity, str) or not SHA256_RE.fullmatch(identity):
            errors.append("target.package_identity_sha256 must be a lowercase 64-character SHA-256")

    if not _nonempty(data.get("mode")):
        errors.append("mode is required")

    snapshot = data.get("evidence_snapshot")
    if not isinstance(snapshot, dict):
        errors.append("evidence_snapshot must be an object")
    else:
        identity = snapshot.get("identity")
        if not isinstance(identity, str) or not SHA256_RE.fullmatch(identity):
            errors.append("evidence_snapshot.identity must be a lowercase 64-character SHA-256")
        if not _nonempty(snapshot.get("source")):
            errors.append("evidence_snapshot.source is required")

    observations = data.get("observations")
    observation_ids: set[str] = set()
    if not isinstance(observations, list):
        errors.append("observations must be a list")
        observations = []
    for i, item in enumerate(observations):
        if not isinstance(item, dict):
            errors.append(f"observations[{i}] must be an object")
            continue
        oid = item.get("id")
        if not _nonempty(oid):
            errors.append(f"observations[{i}].id is required")
        elif oid in observation_ids:
            errors.append(f"duplicate observation id: {oid}")
        else:
            observation_ids.add(oid)
        if item.get("kind") not in OBSERVATION_KINDS:
            errors.append(f"observations[{i}].kind is unsupported")
        if not _nonempty(item.get("claim")):
            errors.append(f"observations[{i}].claim is required")
        if not isinstance(item.get("evidence"), list) or not item.get("evidence"):
            errors.append(f"observations[{i}].evidence must be a non-empty list")

    judgments = data.get("judgments")
    judgment_ids: set[str] = set()
    if not isinstance(judgments, list):
        errors.append("judgments must be a list")
        judgments = []
    for i, item in enumerate(judgments):
        if not isinstance(item, dict):
            errors.append(f"judgments[{i}] must be an object")
            continue
        jid = item.get("id")
        if not _nonempty(jid):
            errors.append(f"judgments[{i}].id is required")
        elif jid in judgment_ids:
            errors.append(f"duplicate judgment id: {jid}")
        else:
            judgment_ids.add(jid)
        if not _nonempty(item.get("claim")):
            errors.append(f"judgments[{i}].claim is required")
        refs = item.get("evidence_ids")
        if not isinstance(refs, list) or not refs:
            errors.append(f"judgments[{i}].evidence_ids must be a non-empty list")
        elif any(ref not in observation_ids for ref in refs):
            errors.append(f"judgments[{i}].evidence_ids must reference observation ids")
        if item.get("confidence") not in CONFIDENCE:
            errors.append(f"judgments[{i}].confidence must be low, medium, or high")

    decision = data.get("decision")
    all_ids = observation_ids | judgment_ids
    if not isinstance(decision, dict):
        errors.append("decision must be an object")
    else:
        if decision.get("choice") not in DECISIONS:
            errors.append("decision.choice must be one of: " + ", ".join(sorted(DECISIONS)))
        refs = decision.get("evidence_ids")
        if not isinstance(refs, list) or not refs:
            errors.append("decision.evidence_ids must be a non-empty list")
        elif any(ref not in all_ids for ref in refs):
            errors.append("decision.evidence_ids contains unknown ids")
        alternatives = decision.get("alternatives_considered")
        if not isinstance(alternatives, list):
            errors.append("decision.alternatives_considered must be a list")
        elif any(item not in DECISIONS for item in alternatives):
            errors.append("decision.alternatives_considered contains unsupported decisions")
        if not _nonempty(decision.get("tie_breaker_used")):
            errors.append("decision.tie_breaker_used is required")

    if not isinstance(data.get("recommendations"), list):
        errors.append("recommendations must be a list")
    measured = data.get("measured")
    if not isinstance(measured, dict):
        errors.append("measured must be an object")
    else:
        if not isinstance(measured.get("commands"), list):
            errors.append("measured.commands must be a list")
        if not isinstance(measured.get("behavioral_scenarios_executed"), bool):
            errors.append("measured.behavioral_scenarios_executed must be boolean")
    if not isinstance(data.get("residual_risks"), list):
        errors.append("residual_risks must be a list")

    if not errors and not observations:
        warnings.append("report has no observations")
    return {"status": "pass" if not errors else "fail", "errors": errors, "warnings": warnings}


def main() -> int:
    parser = argparse.ArgumentParser(description="validate architecture review JSON")
    parser.add_argument("report", help="path to JSON report")
    args = parser.parse_args()
    path = Path(args.report)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        result = {"status": "fail", "errors": [f"report not found: {path}"], "warnings": []}
    except json.JSONDecodeError as exc:
        result = {"status": "fail", "errors": [f"invalid JSON: {exc}"], "warnings": []}
    else:
        result = validate(data)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
