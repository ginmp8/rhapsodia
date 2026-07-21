#!/usr/bin/env python3
"""Shared canonical governance, state, projection, and handoff contracts for nomia."""

from __future__ import annotations

import re
from datetime import date, datetime, timezone
from typing import Any

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
    reasons: list[str] = []
    if not isinstance(env, dict):
        return {"status": "rejected", "reasons": ["handoff envelope must be a mapping"], "direction": None}

    direction = env.get("direction")
    if direction not in HANDOFF_DIRECTIONS:
        reasons.append("invalid direction")
    for field in ("source", "observed_at", "provenance", "freshness_days", "payload"):
        if env.get(field) in (None, "", []):
            reasons.append(f"missing {field}")

    observed = parse_timestamp(env.get("observed_at"))
    if env.get("observed_at") not in (None, "", "unknown") and observed is None:
        reasons.append("invalid observed_at")
    freshness = env.get("freshness_days")
    if not isinstance(freshness, int) or freshness < 0:
        reasons.append("invalid freshness_days")
    stale = False
    if observed is not None and isinstance(freshness, int):
        stale = (as_of - observed).total_seconds() / 86400 > freshness
        if stale:
            reasons.append("evidence is stale")

    payload = env.get("payload") if isinstance(env.get("payload"), dict) else {}
    required = {
        "nomia_to_mago": {"feature_key", "outcome", "scope_summary", "owner", "dependencies", "readiness"},
        "mago_to_nomia": {"spec_id", "planning_state", "planning_evidence"},
        "magia_to_nomia": {"evidence_reference"},
        "nomia_to_stakeholder": {"audience", "summary", "unknowns", "decision_needed"},
    }
    for field in required.get(str(direction), set()):
        if field not in payload or payload.get(field) in (None, ""):
            reasons.append(f"missing payload.{field}")

    if direction == "nomia_to_mago":
        feature_key = payload.get("feature_key")
        if not isinstance(feature_key, str) or FEATURE_KEY_RE.fullmatch(feature_key) is None:
            reasons.append("invalid payload.feature_key")
        if not isinstance(payload.get("dependencies"), list):
            reasons.append("invalid payload.dependencies")
        reasons.extend(validate_candidate_spec_identity(payload))
        reasons.extend(nested_forbidden_keys(payload))
    elif direction == "mago_to_nomia":
        spec_id = payload.get("spec_id")
        if is_legacy_spec_id(spec_id):
            reasons.append("payload.spec_id uses a legacy ULID identity")
        elif validate_spec_id_format(spec_id):
            reasons.append("invalid payload.spec_id")
        if str(payload.get("planning_state") or "unknown") not in PLANNING_STATES:
            reasons.append("invalid payload.planning_state")
    elif direction == "magia_to_nomia":
        if not ({"execution_state", "validation_state"} & set(payload)):
            reasons.append("missing execution_state or validation_state")
        if "execution_state" in payload and str(payload.get("execution_state")) not in EXECUTION_STATES:
            reasons.append("invalid payload.execution_state")
        if "validation_state" in payload and str(payload.get("validation_state")) not in VALIDATION_STATES:
            reasons.append("invalid payload.validation_state")
    elif direction == "nomia_to_stakeholder":
        if not isinstance(payload.get("unknowns"), list):
            reasons.append("invalid payload.unknowns")

    if env.get("conflict") or payload.get("conflict"):
        reasons.append("conflicting evidence")

    blocking = [
        reason
        for reason in reasons
        if reason.startswith(("invalid", "missing"))
        or "legacy ULID" in reason
        or "must use" in reason
        or "does not match" in reason
        or "outside nomia authority" in reason
        or "provenance" in reason
    ]
    if blocking:
        status = "rejected"
    elif "conflicting evidence" in reasons:
        status = "conflicting"
    elif stale:
        status = "stale"
    elif payload.get("readiness") in {"draft", "unknown", False}:
        status = "draft"
    else:
        status = "accepted"
    return {"status": status, "reasons": reasons, "direction": direction}
