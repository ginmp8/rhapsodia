#!/usr/bin/env python3
"""Shared canonical governance, state, projection, and handoff contracts for nomia."""

from __future__ import annotations

import re
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from ecosystem_handoff import validate_envelope as validate_ecosystem_envelope

from nomia_utils import (
    is_legacy_spec_id,
    parse_spec_id,
    validate_id_provenance,
    validate_spec_id_format,
)

PROFILE_VALUES = {"unknown", "quick", "standard", "governed"}
LIFECYCLE_VALUES = {"unknown", "intake", "triage", "commit", "track", "decide", "close"}
GOVERNANCE_STATES = {
    "unknown",
    "intake",
    "triage",
    "planned",
    "ready",
    "in_progress",
    "blocked",
    "validating",
    "releasable",
    "released",
    "closed",
    "canceled",
    "superseded",
}
PLANNING_STATES = {"unknown", "not_started", "planned", "ready", "blocked", "complete"}
EXECUTION_STATES = {"unknown", "not_started", "ready", "in_progress", "blocked", "complete"}
VALIDATION_STATES = {"unknown", "not_started", "in_progress", "blocked", "passed", "failed"}
RELEASE_STATES = {"unknown", "not_released", "releasable", "released", "closed", "canceled", "superseded"}
HANDOFF_DIRECTIONS = {"nomia_to_mago", "mago_to_nomia", "magia_to_nomia", "nomia_to_stakeholder"}
FEATURE_KEY_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FORBIDDEN_NOMIA_TO_MAGO_KEYS = {
    "architecture",
    "architecture_decision",
    "design",
    "implementation",
    "implementation_tasks",
    "tasks",
    "code",
    "tests",
}

STATE_VALUES_BY_DIMENSION = {
    "planning": PLANNING_STATES,
    "execution": EXECUTION_STATES,
    "validation": VALIDATION_STATES,
}


def is_missing(value: Any) -> bool:
    return value in (None, "", "unknown") or value == []


def parse_timestamp(value: Any) -> datetime | None:
    if value in (None, "", "unknown"):
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, date):
        return datetime(value.year, value.month, value.day, tzinfo=timezone.utc)
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def validate_non_unknown_enum(label: str, value: Any, allowed: set[str]) -> list[str]:
    text = str(value or "unknown")
    if text not in allowed:
        return [f"{label} is invalid; expected one of {sorted(allowed)}"]
    if text == "unknown":
        return [f"{label} must be resolved for a canonical governed record"]
    return []


def validate_technical_state(dimension: str, item: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(item, dict):
        return [f"technical_state.{dimension} must be a mapping"]
    allowed = STATE_VALUES_BY_DIMENSION[dimension]
    state = str(item.get("state") or "unknown")
    if state not in allowed:
        errors.append(f"technical_state.{dimension}.state is invalid; expected one of {sorted(allowed)}")
        return errors
    source = item.get("source")
    observed_at = item.get("observed_at")
    if state != "unknown":
        if is_missing(source):
            errors.append(f"technical_state.{dimension}.source is required for non-unknown state")
        if parse_timestamp(observed_at) is None:
            errors.append(f"technical_state.{dimension}.observed_at is required and must be ISO-8601 for non-unknown state")
    elif source not in (None, "", "unknown") or observed_at not in (None, "", "unknown"):
        errors.append(f"technical_state.{dimension} must not attach evidence to unknown state")
    return errors


def validate_release_state(release: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(release, dict):
        return ["release must be a mapping"]
    state = str(release.get("state") or "unknown")
    if state not in RELEASE_STATES:
        errors.append(f"release.state is invalid; expected one of {sorted(RELEASE_STATES)}")
        return errors
    evidence = release.get("evidence")
    if evidence is not None and not isinstance(evidence, list):
        errors.append("release.evidence must be a list")
    if state in {"releasable", "released", "closed"} and not evidence:
        errors.append(f"release.evidence is required when release.state is {state}")
    if state in {"released", "closed"} and parse_timestamp(release.get("released_at")) is None:
        errors.append(f"release.released_at is required and must be ISO-8601 when release.state is {state}")
    return errors


def nested_forbidden_keys(value: Any, prefix: str = "payload") -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key)
            current = f"{prefix}.{key_text}"
            if key_text in FORBIDDEN_NOMIA_TO_MAGO_KEYS:
                errors.append(f"{current} is technical content outside nomia authority")
            errors.extend(nested_forbidden_keys(child, current))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(nested_forbidden_keys(child, f"{prefix}[{index}]"))
    return errors


def validate_candidate_spec_identity(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    candidate = payload.get("candidate_spec_id")
    if candidate in (None, ""):
        return errors
    if is_legacy_spec_id(candidate):
        errors.append("payload.candidate_spec_id uses a legacy ULID identity and cannot be accepted")
        return errors
    if validate_spec_id_format(candidate):
        errors.append("payload.candidate_spec_id must use spec-YYYY-MM-DD-feature-key")
        return errors
    provenance_error = validate_id_provenance(
        payload.get("candidate_spec_id_provenance"),
        id_value=candidate,
        field_name="payload.candidate_spec_id_provenance",
    )
    if provenance_error:
        errors.append(provenance_error)
    feature_key = payload.get("feature_key")
    if isinstance(feature_key, str) and FEATURE_KEY_RE.fullmatch(feature_key):
        parsed = parse_spec_id(str(candidate))
        if parsed["feature_key"] != feature_key:
            errors.append("payload.candidate_spec_id feature-key does not match payload.feature_key")
    return errors


def validate_handoff_envelope(env: Any, as_of: datetime) -> dict[str, Any]:
    """Validate strict current handoffs through the local ecosystem contract."""
    return validate_ecosystem_envelope(
        env,
        root=Path(__file__).resolve().parents[1],
        operation="any",
        as_of=as_of,
    )
