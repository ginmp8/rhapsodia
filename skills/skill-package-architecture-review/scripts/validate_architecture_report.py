#!/usr/bin/env python3
"""Validate machine-readable package architecture review contracts."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

CURRENT_SCHEMA_VERSION = "2.0.0"
CURRENT_RUBRIC_VERSION = "3.0.0"
LEGACY_SCHEMA_VERSION = "1.0.0"
LEGACY_RUBRIC_VERSION = "2.0.0"
DECISIONS = {"keep_unified", "split", "extract_mode", "create_router", "merge_resources", "no_change"}
OBSERVATION_KINDS = {"mechanical", "declared-contract", "behavioral", "supplied", "derived"}
CONFIDENCE = {"low", "medium", "high"}
ARCHITECTURE_SCOPES = {"single_skill", "skill_family", "plugin_package"}
ACTIVATION_STATUSES = {"distinct", "overlap", "partial", "unknown"}
HISTORY_STATUSES = {"observed", "partial", "not-inspected", "unknown"}
TRUST_STATUSES = {"observed", "partial", "unknown"}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _string_list(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def _nonnegative_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _validate_evidence_records(
    records: Any,
    label: str,
    all_ids: set[str],
    errors: list[str],
    *,
    claim_field: str,
    surfaces: bool = False,
) -> None:
    if not isinstance(records, list):
        errors.append(f"{label} must be a list")
        return
    seen: set[str] = set()
    for i, item in enumerate(records):
        if not isinstance(item, dict):
            errors.append(f"{label}[{i}] must be an object")
            continue
        rid = item.get("id")
        if not _nonempty(rid):
            errors.append(f"{label}[{i}].id is required")
        elif rid in seen:
            errors.append(f"duplicate {label} id: {rid}")
        else:
            seen.add(rid)
        if not _nonempty(item.get(claim_field)):
            errors.append(f"{label}[{i}].{claim_field} is required")
        refs = item.get("evidence_ids")
        if not isinstance(refs, list) or not refs:
            errors.append(f"{label}[{i}].evidence_ids must be a non-empty list")
        elif any(ref not in all_ids for ref in refs):
            errors.append(f"{label}[{i}].evidence_ids contains unknown ids")
        if surfaces and not _string_list(item.get("affected_surfaces")):
            errors.append(f"{label}[{i}].affected_surfaces must be a list of strings")


def validate(data: Any) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(data, dict):
        return {"status": "fail", "errors": ["report root must be an object"], "warnings": []}

    schema = data.get("schema_version")
    rubric = data.get("rubric_version")
    if schema == CURRENT_SCHEMA_VERSION:
        if rubric != CURRENT_RUBRIC_VERSION:
            errors.append(f"rubric_version must be {CURRENT_RUBRIC_VERSION} for schema {CURRENT_SCHEMA_VERSION}")
        contract = "current"
    elif schema == LEGACY_SCHEMA_VERSION:
        if rubric != LEGACY_RUBRIC_VERSION:
            errors.append(f"rubric_version must be {LEGACY_RUBRIC_VERSION} for legacy schema {LEGACY_SCHEMA_VERSION}")
        contract = "legacy"
        warnings.append("legacy report contract accepted; current architecture-scope/activation/evolution/trust fields are unavailable")
    else:
        errors.append(
            f"schema_version must be {CURRENT_SCHEMA_VERSION} (current) or {LEGACY_SCHEMA_VERSION} (legacy)"
        )
        contract = "unknown"

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
    if contract == "current" and data.get("architecture_scope") not in ARCHITECTURE_SCOPES:
        errors.append("architecture_scope must be one of: " + ", ".join(sorted(ARCHITECTURE_SCOPES)))

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

    all_ids = observation_ids | judgment_ids

    if contract == "current":
        activation = data.get("activation_evidence")
        if not isinstance(activation, dict):
            errors.append("activation_evidence must be an object")
        else:
            if activation.get("status") not in ACTIVATION_STATUSES:
                errors.append("activation_evidence.status is unsupported")
            if not _string_list(activation.get("signals")):
                errors.append("activation_evidence.signals must be a list of strings")
            if not _nonempty(activation.get("catalog_scope")):
                errors.append("activation_evidence.catalog_scope is required")

        topology = data.get("context_topology")
        required_topology = {
            "skill_md_line_count",
            "direct_declared_resource_count",
            "reference_chain_max_depth",
            "nested_reference_edge_count",
        }
        if not isinstance(topology, dict):
            errors.append("context_topology must be an object")
        else:
            for field in sorted(required_topology):
                if not _nonnegative_int(topology.get(field)):
                    errors.append(f"context_topology.{field} must be a non-negative integer")

        _validate_evidence_records(
            data.get("quality_scenarios"), "quality_scenarios", all_ids, errors, claim_field="stimulus", surfaces=True
        )
        _validate_evidence_records(
            data.get("sensitivity_points"), "sensitivity_points", all_ids, errors, claim_field="claim"
        )
        _validate_evidence_records(
            data.get("tradeoff_points"), "tradeoff_points", all_ids, errors, claim_field="claim"
        )

        evolution = data.get("evolution_evidence")
        if not isinstance(evolution, dict):
            errors.append("evolution_evidence must be an object")
        else:
            if evolution.get("history_status") not in HISTORY_STATUSES:
                errors.append("evolution_evidence.history_status is unsupported")
            if not isinstance(evolution.get("change_coupling"), list):
                errors.append("evolution_evidence.change_coupling must be a list")
            if not _string_list(evolution.get("change_radius_notes")):
                errors.append("evolution_evidence.change_radius_notes must be a list of strings")

        trust = data.get("trust_boundary_map")
        if not isinstance(trust, dict):
            errors.append("trust_boundary_map must be an object")
        else:
            if trust.get("status") not in TRUST_STATUSES:
                errors.append("trust_boundary_map.status is unsupported")
            for field in (
                "executable_resources",
                "network_requirements",
                "filesystem_write_requirements",
                "external_tool_requirements",
            ):
                if not _string_list(trust.get(field)):
                    errors.append(f"trust_boundary_map.{field} must be a list of strings")
            if not isinstance(trust.get("security_handoff_required"), bool):
                errors.append("trust_boundary_map.security_handoff_required must be boolean")

        if not _string_list(data.get("evidence_gaps")):
            errors.append("evidence_gaps must be a list of strings")

    decision = data.get("decision")
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
    return {
        "status": "pass" if not errors else "fail",
        "contract": contract,
        "errors": errors,
        "warnings": warnings,
    }


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
