#!/usr/bin/env python3
"""Validate nomia ops.yaml delivery metadata."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from governance_contract import (
    GOVERNANCE_STATES,
    LIFECYCLE_VALUES,
    PROFILE_VALUES,
    validate_non_unknown_enum,
    validate_release_state,
    validate_technical_state,
)
from nomia_utils import (
    has_unresolved_template_token,
    is_iso_date,
    is_missing,
    load_yaml_mapping,
    scan_unresolved_template_tokens,
    unique,
    validate_id_provenance,
    validate_spec_id_format,
)

VALID_SOURCES = {
    "unknown",
    "github_issue",
    "chat",
    "email",
    "rough_demand",
    "roadmap",
    "support_ticket",
    "customer_request",
    "incident",
    "manual",
    "other",
}
VALID_BUCKETS = {
    "unknown",
    "customer_commitment",
    "revenue",
    "retention",
    "growth",
    "risk_reduction",
    "compliance",
    "platform",
    "maintenance",
    "support",
    "incident",
    "roadmap",
    "quality",
    "research",
    "other",
}
VALID_PRIORITY = {"unknown", "low", "medium", "high", "urgent"}
VALID_URGENCY = {"unknown", "low", "medium", "high", "immediate"}
VALID_IMPACT = {"unknown", "low", "medium", "high", "critical"}
VALID_RISK = {"unknown", "low", "medium", "high", "critical"}
LEGACY_VALID_STATE = {"unknown", "intake", "triage", "planned", "in_progress", "blocked", "at_risk", "done", "canceled"}
VALID_STATE = GOVERNANCE_STATES
VALID_COMMITMENT = {"unknown", "committed", "targeted", "tentative"}
VALID_CONFIDENCE = {"unknown", "low", "medium", "high"}
FORBIDDEN_SOURCE_OF_TRUTH_KEYS = {
    "branches",
    "pull_requests",
    "prs",
    "commits",
    "checks",
    "reviews",
    "review_status",
    "deployments",
    "deployment_state",
    "last_commit_age",
}
REPLAN_FIELDS_REQUIRING_FROM_TO = {
    "target_date",
    "planning.target_date",
    "sprint",
    "planning.sprint",
    "scope",
    "owner",
    "ownership.owner",
    "commitment",
    "planning.commitment",
}

REQUIRED_PATHS = [
    ("schema_version",),
    ("spec_id",),
    ("request",),
    ("request", "title"),
    ("request", "requester"),
    ("request", "requested_date"),
    ("request", "source"),
    ("ownership",),
    ("ownership", "owner"),
    ("ownership", "backup_owner"),
    ("ownership", "stakeholders"),
    ("planning",),
    ("planning", "sprint"),
    ("planning", "bucket"),
    ("planning", "target_date"),
    ("planning", "commitment"),
    ("priority",),
    ("priority", "level"),
    ("priority", "rationale"),
    ("status",),
    ("status", "state"),
    ("status", "summary"),
    ("status", "updated_at"),
    ("blockers",),
    ("replanning",),
    ("tags",),
    ("links",),
    ("links", "mago"),
    ("links", "magia"),
    ("links", "external"),
]
OPTIONAL_PATHS = [
    ("request", "context"),
    ("ownership", "decision_maker"),
    ("ownership", "watchers"),
    ("planning", "milestone"),
    ("planning", "rollout_target"),
    ("priority", "urgency"),
    ("priority", "impact"),
    ("priority", "risk"),
    ("priority", "cost_of_delay"),
    ("status", "confidence"),
    ("status", "evidence_summary"),
    ("status", "manual"),
    ("status", "manual", "summary"),
    ("status", "manual", "updated_at"),
    ("status", "manual", "source"),
    ("status", "inferred"),
    ("status", "inferred", "summary"),
    ("status", "inferred", "updated_at"),
    ("status", "inferred", "evidence"),
    ("risks",),
    ("repos",),
    ("repos", "candidate_impacted"),
    ("planning", "original_target_date"),
    ("planning", "committed_target_date"),
]

V2_REQUIRED_PATHS = [
    ("governance",),
    ("governance", "profile"),
    ("governance", "lifecycle"),
    ("governance", "status"),
    ("technical_state",),
    ("technical_state", "planning"),
    ("technical_state", "execution"),
    ("technical_state", "validation"),
    ("release",),
    ("dependencies",),
    ("decision",),
    ("handoffs",),
    ("provenance",),
    ("provenance", "updated_at"),
    ("provenance", "facts"),
    ("provenance", "changes"),
]


def path_name(path: tuple[str, ...]) -> str:
    return ".".join(path)


def get_path(data: dict[str, Any], path: tuple[str, ...]) -> tuple[bool, Any]:
    current: Any = data
    for part in path:
        if not isinstance(current, dict) or part not in current:
            return False, None
        current = current[part]
    return True, current


def as_map(data: dict[str, Any], key: str, errors: list[str]) -> dict[str, Any]:
    value = data.get(key)
    if isinstance(value, dict):
        return value
    if key in data:
        errors.append(f"`{key}` must be a mapping")
    return {}



def validate_enum(label: str, value: Any, valid_values: set[str], errors: list[str]) -> None:
    if value in (None, ""):
        return
    if has_unresolved_template_token(value):
        return
    if str(value) not in valid_values:
        errors.append(f"`{label}` must be one of {sorted(valid_values)}")


def validate_non_empty_string(label: str, value: Any, errors: list[str]) -> None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"`{label}` must be a non-empty string")


def validate_string_list(label: str, values: list[Any], errors: list[str]) -> None:
    for index, value in enumerate(values):
        validate_non_empty_string(f"{label}[{index}]", value, errors)


def validate_list_path(data: dict[str, Any], path: tuple[str, ...], errors: list[str]) -> list[Any]:
    exists, value = get_path(data, path)
    if not exists:
        return []
    if not isinstance(value, list):
        errors.append(f"`{path_name(path)}` must be a list")
        return []
    return value


def scan_for_forbidden_keys(value: Any, errors: list[str], prefix: tuple[str, ...] = ()) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key)
            if key_text in FORBIDDEN_SOURCE_OF_TRUTH_KEYS:
                errors.append(f"`{path_name(prefix + (key_text,))}` must not store execution source-of-truth fields")
            scan_for_forbidden_keys(child, errors, prefix + (key_text,))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            scan_for_forbidden_keys(child, errors, prefix + (str(index),))


def validate_replanning(data: dict[str, Any], errors: list[str], warnings: list[str]) -> None:
    replanning = validate_list_path(data, ("replanning",), errors)
    for index, entry in enumerate(replanning):
        label = f"`replanning[{index}]`"
        if not isinstance(entry, dict):
            errors.append(f"{label} must be a mapping")
            continue

        if not entry.get("date") or not is_iso_date(entry.get("date")):
            errors.append(f"{label}.date must use YYYY-MM-DD format")

        changed = entry.get("changed_fields")
        if not isinstance(changed, list) or not changed:
            errors.append(f"{label}.changed_fields must be a non-empty list")
            changed_values: set[str] = set()
        else:
            validate_string_list(f"replanning[{index}].changed_fields", changed, errors)
            changed_values = {str(item) for item in changed}

        for required_key in ("reason", "impact"):
            if is_missing(entry.get(required_key)):
                errors.append(f"{label} must include `{required_key}`")
            else:
                validate_non_empty_string(f"replanning[{index}].{required_key}", entry.get(required_key), errors)

        if changed_values & REPLAN_FIELDS_REQUIRING_FROM_TO:
            for required_key in ("from", "to"):
                if required_key not in entry or entry.get(required_key) in (None, ""):
                    errors.append(f"{label} changed a material field but omits `{required_key}`")

        decision_maker = entry.get("decision_maker")
        if decision_maker not in (None, "", "unknown"):
            validate_non_empty_string(f"replanning[{index}].decision_maker", decision_maker, errors)

        if changed_values & {"target_date", "planning.target_date"}:
            for value_key in ("from", "to"):
                value = entry.get(value_key)
                if value not in (None, "", "unknown") and not is_iso_date(value):
                    errors.append(f"{label}.{value_key} must use YYYY-MM-DD format for target_date changes")

        if is_missing(entry.get("decision_maker")):
            warnings.append(f"{label}.decision_maker is missing")


def validate_blockers_and_risks(data: dict[str, Any], errors: list[str]) -> None:
    for collection, date_key in (("blockers", "needed_by"), ("risks", None)):
        entries = validate_list_path(data, (collection,), errors)
        for index, entry in enumerate(entries):
            if not isinstance(entry, dict):
                errors.append(f"`{collection}[{index}]` must be a mapping")
                continue
            for required_key in ("id", "summary"):
                validate_non_empty_string(f"{collection}[{index}].{required_key}", entry.get(required_key), errors)
            owner = entry.get("owner")
            if owner not in (None, "", "unknown"):
                validate_non_empty_string(f"{collection}[{index}].owner", owner, errors)
            if date_key and entry.get(date_key) not in (None, "") and not is_iso_date(entry.get(date_key)):
                errors.append(f"`{collection}[{index}].{date_key}` must use YYYY-MM-DD format")
            if collection == "risks":
                validate_enum(f"risks[{index}].severity", entry.get("severity"), VALID_RISK, errors)


def validate_governed_extensions(
    data: dict[str, Any], errors: list[str], warnings: list[str], *, require_resolved: bool
) -> None:
    for required_path in V2_REQUIRED_PATHS:
        exists, _ = get_path(data, required_path)
        if not exists:
            errors.append(f"missing required key `{path_name(required_path)}` for schema_version 2")

    governance = as_map(data, "governance", errors)
    profile = governance.get("profile", "unknown")
    lifecycle = governance.get("lifecycle", "unknown")
    governance_status = governance.get("status", "unknown")
    if require_resolved:
        errors.extend(validate_non_unknown_enum("governance.profile", profile, PROFILE_VALUES))
        errors.extend(validate_non_unknown_enum("governance.lifecycle", lifecycle, LIFECYCLE_VALUES))
        errors.extend(validate_non_unknown_enum("governance.status", governance_status, GOVERNANCE_STATES))
    else:
        validate_enum("governance.profile", profile, PROFILE_VALUES, errors)
        validate_enum("governance.lifecycle", lifecycle, LIFECYCLE_VALUES, errors)
        validate_enum("governance.status", governance_status, GOVERNANCE_STATES, errors)

    status = data.get("status") if isinstance(data.get("status"), dict) else {}
    status_state = str(status.get("state") or "unknown")
    if governance_status not in (None, "") and status_state != str(governance_status):
        errors.append("`status.state` must mirror `governance.status` for schema_version 2")

    technical_state = data.get("technical_state")
    if not isinstance(technical_state, dict):
        errors.append("`technical_state` must be a mapping")
        technical_state = {}
    for dimension in ("planning", "execution", "validation"):
        errors.extend(validate_technical_state(dimension, technical_state.get(dimension)))

    errors.extend(validate_release_state(data.get("release")))
    for key in ("dependencies",):
        if not isinstance(data.get(key), list):
            errors.append(f"`{key}` must be a list")
    for key in ("decision", "handoffs", "provenance"):
        if not isinstance(data.get(key), dict):
            errors.append(f"`{key}` must be a mapping")
    provenance = data.get("provenance") if isinstance(data.get("provenance"), dict) else {}
    if not isinstance(provenance.get("facts"), dict):
        errors.append("`provenance.facts` must be a mapping")
    if not isinstance(provenance.get("changes"), list):
        errors.append("`provenance.changes` must be a list")
    if is_missing(provenance.get("updated_at")):
        warnings.append("provenance.updated_at is missing; canonical projections remain blocked")


def validate(path: Path, require_canonical: bool = False) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if not path.exists():
        return [f"missing required file: {path}"], warnings

    try:
        data = load_yaml_mapping(path)
    except Exception as exc:
        return [f"{path}: {exc}"], warnings

    errors.extend(scan_unresolved_template_tokens(data))

    for required_path in REQUIRED_PATHS:
        exists, _ = get_path(data, required_path)
        if not exists:
            errors.append(f"missing required key `{path_name(required_path)}`")

    schema_version = data.get("schema_version")
    if schema_version not in {1, 2}:
        errors.append("`schema_version` must be 1 (legacy validation-only) or 2 (canonical)")
    if require_canonical and schema_version != 2:
        errors.append("canonical validation requires `schema_version: 2`")

    spec_id = data.get("spec_id")
    spec_id_error = validate_spec_id_format(spec_id)
    if spec_id_error:
        errors.append("`spec_id` must be null for an off-repository draft or use spec-YYYY-MM-DD-feature-key format")
    provenance_error = validate_id_provenance(
        data.get("spec_id_provenance"), id_value=spec_id, field_name="spec_id_provenance"
    )
    if provenance_error:
        errors.append(f"`{provenance_error}`")

    request = as_map(data, "request", errors)
    ownership = as_map(data, "ownership", errors)
    planning = as_map(data, "planning", errors)
    priority = as_map(data, "priority", errors)
    status = as_map(data, "status", errors)
    links = as_map(data, "links", errors)
    repos = data.get("repos") if isinstance(data.get("repos"), dict) else {}

    for key in ("manual", "inferred"):
        if key in status and not isinstance(status.get(key), dict):
            errors.append(f"`status.{key}` must be a mapping")
    if "repos" in data and not isinstance(data.get("repos"), dict):
        errors.append("`repos` must be a mapping")

    for label, value in (
        ("request.requested_date", request.get("requested_date")),
        ("planning.target_date", planning.get("target_date")),
        ("planning.original_target_date", planning.get("original_target_date")),
        ("planning.committed_target_date", planning.get("committed_target_date")),
        ("status.updated_at", status.get("updated_at")),
        ("status.manual.updated_at", (status.get("manual") or {}).get("updated_at") if isinstance(status.get("manual"), dict) else None),
        ("status.inferred.updated_at", (status.get("inferred") or {}).get("updated_at") if isinstance(status.get("inferred"), dict) else None),
    ):
        if not is_iso_date(value):
            errors.append(f"`{label}` must use YYYY-MM-DD format")

    validate_enum("request.source", request.get("source"), VALID_SOURCES, errors)
    validate_enum("planning.bucket", planning.get("bucket"), VALID_BUCKETS, errors)
    validate_enum("planning.commitment", planning.get("commitment"), VALID_COMMITMENT, errors)
    validate_enum("priority.level", priority.get("level"), VALID_PRIORITY, errors)
    validate_enum("priority.urgency", priority.get("urgency"), VALID_URGENCY, errors)
    validate_enum("priority.impact", priority.get("impact"), VALID_IMPACT, errors)
    validate_enum("priority.risk", priority.get("risk"), VALID_RISK, errors)
    validate_enum(
        "status.state",
        status.get("state"),
        LEGACY_VALID_STATE if schema_version == 1 else VALID_STATE,
        errors,
    )
    if schema_version == 2:
        validate_governed_extensions(data, errors, warnings, require_resolved=spec_id not in (None, ""))
    validate_enum("status.confidence", status.get("confidence"), VALID_CONFIDENCE, errors)

    for key in ("blockers", "risks", "replanning", "tags"):
        validate_list_path(data, (key,), errors)
    for key in ("stakeholders", "watchers"):
        values = validate_list_path(data, ("ownership", key), errors)
        validate_string_list(f"ownership.{key}", values, errors)
    validate_list_path(data, ("repos", "candidate_impacted"), errors)
    evidence = validate_list_path(data, ("status", "inferred", "evidence"), errors)
    validate_string_list("status.inferred.evidence", evidence, errors)

    tags = validate_list_path(data, ("tags",), errors)
    validate_string_list("tags", tags, errors)

    if links:
        for key, value in links.items():
            if not isinstance(value, list):
                errors.append(f"`links.{key}` must be a list")
                continue
            validate_string_list(f"links.{key}", value, errors)

    candidate_repos = repos.get("candidate_impacted") if isinstance(repos, dict) else None
    if isinstance(candidate_repos, list):
        for index, repo in enumerate(candidate_repos):
            if not isinstance(repo, str) or not repo.strip():
                errors.append(f"`repos.candidate_impacted[{index}]` must be a non-empty string")

    if is_missing(ownership.get("owner")):
        warnings.append("owner is missing")
    if is_missing(ownership.get("stakeholders")):
        warnings.append("stakeholders are missing")
    if is_missing(planning.get("target_date")):
        warnings.append("target date is missing")
    if is_missing(planning.get("bucket")):
        warnings.append("planning bucket is unknown")
    if is_missing(priority.get("level")):
        warnings.append("priority level is unknown")

    replanning = data.get("replanning")
    replan_entries = replanning if isinstance(replanning, list) else []
    changed_target_date = any(
        isinstance(entry, dict)
        and isinstance(entry.get("changed_fields"), list)
        and {"target_date", "planning.target_date"} & {str(item) for item in entry.get("changed_fields", [])}
        for entry in replan_entries
    )
    baseline_date = planning.get("committed_target_date", planning.get("original_target_date"))
    target_date = planning.get("target_date")
    if (
        planning.get("commitment") == "committed"
        and baseline_date not in (None, "", "unknown")
        and target_date not in (None, "", "unknown")
        and str(baseline_date) != str(target_date)
        and not changed_target_date
    ):
        errors.append("committed target date changed without replanning history")

    scan_for_forbidden_keys(data, errors)
    validate_replanning(data, errors, warnings)
    validate_blockers_and_risks(data, errors)

    return errors, warnings



def qualify(message: str, path: Path) -> str:
    path_text = str(path)
    if path_text in message:
        return message
    return f"{path}: {message}"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Validate nomia ops.yaml.")
    parser.add_argument("path", nargs="?", default="ops.yaml", help="Path to ops.yaml.")
    parser.add_argument("--require-canonical", action="store_true", help="Require schema_version 2 and the governed canonical sections.")
    args = parser.parse_args(argv)

    target = Path(args.path).resolve()
    errors, warnings = validate(target, require_canonical=args.require_canonical)
    errors = unique([qualify(error, target) for error in errors])
    warnings = unique([qualify(warning, target) for warning in warnings])

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        for warning in warnings:
            print(f"WARNING: {warning}")
        print(f"FAILED: {len(errors)} errors, {len(warnings)} warnings")
        return 1

    for warning in warnings:
        print(f"WARNING: {warning}")
    if warnings:
        print(f"OK: completed with {len(warnings)} warnings")
    else:
        print("OK: validated ops.yaml")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
