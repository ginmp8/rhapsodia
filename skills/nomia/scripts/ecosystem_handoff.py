#!/usr/bin/env python3
"""Build and validate strict, privacy-minimized ecosystem handoffs."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CONTRACT_FILE = "references/ecosystem-handoff-contract.json"
COMPATIBILITY_FILE = "references/ecosystem-compatibility.json"
PRIORITY_FILE = "references/priority-contract.json"
ROLES = {"nomia", "mago", "magia"}
SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
FEATURE_KEY_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SPEC_ID_RE = re.compile(r"^spec-(\d{4}-\d{2}-\d{2})-([a-z0-9]+(?:-[a-z0-9]+)*)$")
HANDOFF_ID_RE = re.compile(r"^handoff-[0-9a-f]{16}$")
WORKFLOW_ID_RE = re.compile(r"^workflow-[0-9a-f]{16}$")
PRIVATE_REF_RE = re.compile(r"(?i)(?:/home/|/users/|\\\\|https?://(?:[^/]+\.)?(?:internal|corp|local)(?:[/:]|$)|(?:^|/)private(?:/|$))")
EXIT_CODES = {"accepted": 0, "error": 2, "draft": 3, "stale": 4, "conflicting": 5, "rejected": 6}


def validation_exit_code(status: str, *, allow_draft: bool = False) -> int:
    return 0 if status == "draft" and allow_draft else EXIT_CODES.get(status, 2)


def reason_code(reason: str) -> str:
    rules = (
        ("missing", "HANDOFF_MISSING_FIELD"),
        ("invalid schema_version", "HANDOFF_INVALID_SCHEMA"),
        ("invalid ecosystem_release", "HANDOFF_INVALID_ECOSYSTEM_RELEASE"),
        ("incompatible source_version", "HANDOFF_INCOMPATIBLE_SOURCE_VERSION"),
        ("invalid handoff_id", "HANDOFF_INVALID_ID"),
        ("invalid workflow_id", "HANDOFF_INVALID_WORKFLOW_ID"),
        ("invalid causation_id", "HANDOFF_INVALID_CAUSATION_ID"),
        ("contains_secrets", "HANDOFF_SECRET_EXPOSURE"),
        ("public destination", "HANDOFF_PUBLIC_DESTINATION_DENIED"),
        ("privacy_handling", "HANDOFF_INVALID_PRIVACY"),
        ("evidence is stale", "HANDOFF_STALE"),
        ("timestamp is in the future", "HANDOFF_FUTURE_OBSERVED_AT"),
        ("exceeds contract maximum", "HANDOFF_FRESHNESS_EXCEEDS_MAX"),
        ("evidence_refs must contain", "HANDOFF_EMPTY_EVIDENCE_REFS"),
        ("invalid provenance.authority", "HANDOFF_INVALID_PROVENANCE_AUTHORITY"),
        ("outside producer authority", "HANDOFF_OUTSIDE_AUTHORITY"),
        ("outside nomia authority", "HANDOFF_OUTSIDE_AUTHORITY"),
        ("is not declared for", "HANDOFF_UNKNOWN_PAYLOAD_FIELD"),
        ("invalid payload.candidate_spec_id", "HANDOFF_INVALID_CANDIDATE_SPEC_ID"),
        ("conflicting evidence", "HANDOFF_CONFLICTING"),
        ("invalid source_skill", "HANDOFF_INVALID_SOURCE_SKILL"),
        ("invalid target_skill", "HANDOFF_INVALID_TARGET_SKILL"),
        ("invalid producer role", "HANDOFF_INVALID_PRODUCER_ROLE"),
        ("invalid consumer role", "HANDOFF_INVALID_CONSUMER_ROLE"),
    )
    for fragment, code in rules:
        if reason.startswith(fragment) or fragment in reason:
            return code
    return "HANDOFF_INVALID_FIELD" if reason.startswith("invalid") else "HANDOFF_REJECTED"


def root_for_script() -> Path:
    return Path(__file__).resolve().parents[1]


def atomic_write_text(path: Path, text: str) -> None:
    path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def load_json_object(path: Path, label: str) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value


def _load(relative: str, label: str, root: Path | None) -> dict[str, Any]:
    return load_json_object((root or root_for_script()).resolve() / relative, label)


def load_contract(root: Path | None = None) -> dict[str, Any]:
    return _load(CONTRACT_FILE, "ecosystem handoff contract", root)


def load_compatibility(root: Path | None = None) -> dict[str, Any]:
    return _load(COMPATIBILITY_FILE, "ecosystem compatibility manifest", root)


def load_priority_contract(root: Path | None = None) -> dict[str, Any]:
    return _load(PRIORITY_FILE, "ecosystem priority contract", root)


def package_role(root: Path | None = None) -> str:
    base = (root or root_for_script()).resolve()
    if base.name.lower() in ROLES:
        return base.name.lower()
    try:
        name = str(load_json_object(base / "release.json", "release metadata").get("name", "")).lower()
        if name in ROLES:
            return name
    except (OSError, ValueError, json.JSONDecodeError):
        pass
    raise ValueError(f"unsupported package role: {base.name}")


def package_version(root: Path | None = None) -> str:
    base = (root or root_for_script()).resolve()
    path = base / "VERSION"
    version = path.read_text(encoding="utf-8").strip() if path.is_file() else str(load_json_object(base / "release.json", "release metadata").get("version", ""))
    if SEMVER_RE.fullmatch(version) is None:
        raise ValueError(f"package version is not stable semantic versioning: {version}")
    return version


def parse_time(value: Any) -> datetime | None:
    if value in (None, "", "unknown"):
        return None
    try:
        parsed = value if isinstance(value, datetime) else datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def valid_spec_id(value: Any) -> bool:
    match = SPEC_ID_RE.fullmatch(str(value or ""))
    if not match:
        return False
    try:
        datetime.strptime(match.group(1), "%Y-%m-%d")
        return True
    except ValueError:
        return False


def contract_errors(contract: dict[str, Any], root: Path | None = None) -> list[str]:
    errors: list[str] = []
    compatibility, priority = load_compatibility(root), load_priority_contract(root)
    if contract.get("schema_version") != "3.0.0": errors.append("contract schema_version must be 3.0.0")
    if contract.get("contract_id") != "nomia-mago-magia-handoff-v3": errors.append("contract_id must be nomia-mago-magia-handoff-v3")
    if contract.get("ecosystem_release") != compatibility.get("ecosystem_release"): errors.append("handoff ecosystem_release must match compatibility manifest")
    policy = contract.get("compatibility")
    if not isinstance(policy, dict) or policy.get("classification") != "breaking-no-legacy": errors.append("handoff compatibility must be breaking-no-legacy")
    elif policy.get("legacy_read_support") is not False: errors.append("handoff legacy_read_support must be false")

    envelope, roles, directions, mapping = (contract.get(k) for k in ("envelope", "roles", "directions", "state_mapping"))
    if not isinstance(envelope, dict):
        errors.append("contract envelope must be an object"); envelope = {}
    required = set(envelope.get("required_fields") or [])
    for field in ("schema_version", "ecosystem_release", "source_skill", "source_version", "target_skill", "workflow_id", "privacy_handling", "handoff_id", "payload"):
        if field not in required: errors.append(f"envelope.required_fields missing {field}")
    freshness = envelope.get("freshness_policy")
    if not isinstance(freshness, dict): errors.append("envelope.freshness_policy must be an object")
    else:
        if not isinstance(freshness.get("max_age_days"), int) or freshness["max_age_days"] <= 0: errors.append("envelope.freshness_policy.max_age_days must be a positive integer")
        if not isinstance(freshness.get("max_future_skew_seconds"), int) or freshness["max_future_skew_seconds"] < 0: errors.append("envelope.freshness_policy.max_future_skew_seconds must be a non-negative integer")
        if not isinstance(freshness.get("min_evidence_refs"), int) or freshness["min_evidence_refs"] < 1: errors.append("envelope.freshness_policy.min_evidence_refs must be at least 1")
    privacy = envelope.get("privacy_handling")
    if not isinstance(privacy, dict): errors.append("envelope.privacy_handling must be an object")
    else:
        expected_types = {"required_fields": list, "enum_fields": dict, "boolean_fields": list, "list_fields": list, "allowed_destinations": list}
        for field, expected in expected_types.items():
            if not isinstance(privacy.get(field), expected): errors.append(f"envelope.privacy_handling.{field} has invalid type")
    if "causation_id" not in (envelope.get("optional_fields") or []): errors.append("envelope.optional_fields must include causation_id")

    if not isinstance(roles, dict): errors.append("contract roles must be an object"); roles = {}
    if not isinstance(directions, dict) or not directions: errors.append("contract directions must be a non-empty object"); directions = {}
    if set(directions) != set(compatibility.get("required_directions") or []): errors.append("handoff directions must exactly match compatibility manifest")
    if not isinstance(mapping, dict) or mapping.get("version") != "2.0.0": errors.append("state_mapping.version must be 2.0.0")
    for role in ROLES:
        item = roles.get(role)
        if not isinstance(item, dict): errors.append(f"missing role contract: {role}"); continue
        for field in ("produces", "consumes"):
            if not isinstance(item.get(field), list): errors.append(f"roles.{role}.{field} must be a list")
    for direction, item in directions.items():
        if not isinstance(item, dict): errors.append(f"directions.{direction} must be an object"); continue
        producer, consumer = item.get("producer"), item.get("consumer")
        if producer not in roles or consumer not in roles: errors.append(f"directions.{direction} producer/consumer is invalid"); continue
        if direction not in roles[producer].get("produces", []): errors.append(f"direction {direction} missing from producer {producer}")
        if direction not in roles[consumer].get("consumes", []): errors.append(f"direction {direction} missing from consumer {consumer}")
        if not item.get("required_payload") or not isinstance(item.get("required_payload"), list): errors.append(f"directions.{direction}.required_payload must be non-empty")
        if not isinstance(item.get("optional_payload"), list): errors.append(f"directions.{direction}.optional_payload must be a list")
    if priority.get("contract_id") != "nomia-mago-magia-priority-v2": errors.append("priority contract id mismatch")
    if priority.get("ecosystem_release") != compatibility.get("ecosystem_release"): errors.append("priority ecosystem_release must match compatibility manifest")
    return errors


def recursive_forbidden(value: Any, forbidden: set[str], prefix: str = "payload") -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            current = f"{prefix}.{key}"
            if str(key) in forbidden | {"priority", "order_hint"}: errors.append(f"{current} is outside producer authority")
            errors.extend(recursive_forbidden(child, forbidden, current))
    elif isinstance(value, list):
        for index, child in enumerate(value): errors.extend(recursive_forbidden(child, forbidden, f"{prefix}[{index}]"))
    return errors


def workflow_id_for(seed: str) -> str:
    seed = str(seed or "").strip()
    if not seed: raise ValueError("workflow seed must be non-empty")
    return "workflow-" + hashlib.sha256(seed.encode()).hexdigest()[:16]


def privacy_errors(value: Any, contract: dict[str, Any], evidence_refs: list[str]) -> list[str]:
    policy = ((contract.get("envelope") or {}).get("privacy_handling") or {})
    if not isinstance(value, dict): return ["invalid privacy_handling; expected object"]
    errors: list[str] = []
    required = set(policy.get("required_fields") or [])
    errors += [f"missing privacy_handling.{field}" for field in sorted(required) if value.get(field) is None]
    errors += [f"invalid privacy_handling field: {field}" for field in sorted(set(value) - required)]
    for field, allowed in (policy.get("enum_fields") or {}).items():
        if value.get(field) not in allowed: errors.append(f"invalid privacy_handling.{field}")
    for field in policy.get("boolean_fields") or []:
        if not isinstance(value.get(field), bool): errors.append(f"invalid privacy_handling.{field}; expected boolean")
    for field in policy.get("list_fields") or []:
        item = value.get(field)
        if not isinstance(item, list) or any(not isinstance(entry, str) or not entry.strip() for entry in item): errors.append(f"invalid privacy_handling.{field}; expected non-empty strings")
    destinations = value.get("allowed_destinations")
    if isinstance(destinations, list) and set(destinations) - set(policy.get("allowed_destinations") or []): errors.append("invalid privacy_handling.allowed_destinations")
    retention = value.get("retention_days")
    if isinstance(retention, bool) or not isinstance(retention, int) or not 0 <= retention <= int(policy.get("max_retention_days", 3650)): errors.append("invalid privacy_handling.retention_days")
    if not isinstance(value.get("purpose"), str) or not value["purpose"].strip(): errors.append("invalid privacy_handling.purpose")
    if value.get("contains_secrets") is True: errors.append("privacy_handling contains_secrets must be false")
    sensitive = any(value.get(field) is True for field in ("contains_personal_data", "contains_third_party_data", "contains_confidential_data"))
    if sensitive and (not value.get("redactions_applied") or value.get("redaction_method") == "none"): errors.append("privacy_handling sensitive content requires redactions")
    if value.get("classification") == "public":
        if sensitive: errors.append("privacy_handling public classification cannot contain sensitive data")
        if value.get("evidence_ref_visibility") not in {"opaque", "public"}: errors.append("privacy_handling public classification requires opaque or public evidence refs")
    if "public" in (destinations or []) and (value.get("classification") != "public" or value.get("external_share_allowed") is not True): errors.append("privacy_handling public destination is denied")
    if value.get("external_share_allowed") is True and value.get("classification") != "public": errors.append("privacy_handling external_share_allowed requires public classification")
    if value.get("evidence_ref_visibility") == "public" and any(PRIVATE_REF_RE.search(str(ref)) for ref in evidence_refs): errors.append("privacy_handling public evidence references contain private location")
    return errors


def handoff_id_for(envelope: dict[str, Any]) -> str:
    data = {key: value for key, value in envelope.items() if key != "handoff_id"}
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":")).encode()
    return "handoff-" + hashlib.sha256(canonical).hexdigest()[:16]


def validate_priority_objects(payload: dict[str, Any], direction: str, priority: dict[str, Any], *, as_of: datetime, future_skew_seconds: int) -> list[str]:
    errors: list[str] = []
    concepts = priority.get("concepts") or {}
    if direction == "nomia_to_mago":
        item = payload.get("business_priority")
        if not isinstance(item, dict): return ["invalid payload.business_priority"]
        if item.get("level") not in ((concepts.get("business_priority") or {}).get("values") or []): errors.append("invalid payload.business_priority.level")
        if item.get("owner") != "nomia": errors.append("invalid payload.business_priority.owner")
        if item.get("level") != "unknown":
            if item.get("source") in (None, "", "unknown"): errors.append("missing payload.business_priority.source")
            observed = parse_time(item.get("observed_at"))
            if observed is None: errors.append("invalid payload.business_priority.observed_at")
            elif (observed - as_of).total_seconds() > future_skew_seconds: errors.append("invalid payload.business_priority.observed_at; timestamp is in the future")
    elif direction == "mago_to_magia":
        criticality, sequence = payload.get("technical_criticality"), payload.get("execution_sequence")
        if not isinstance(criticality, dict): errors.append("invalid payload.technical_criticality")
        else:
            if criticality.get("level") not in ((concepts.get("technical_criticality") or {}).get("values") or []): errors.append("invalid payload.technical_criticality.level")
            if criticality.get("owner") != "mago": errors.append("invalid payload.technical_criticality.owner")
            if criticality.get("rationale") in (None, "", []): errors.append("missing payload.technical_criticality.rationale")
        if not isinstance(sequence, dict): errors.append("invalid payload.execution_sequence")
        else:
            if sequence.get("lane") not in ((concepts.get("execution_sequence") or {}).get("lanes") or []): errors.append("invalid payload.execution_sequence.lane")
            if not isinstance(sequence.get("rank"), int) or sequence["rank"] < 0: errors.append("invalid payload.execution_sequence.rank")
            if sequence.get("owner") != "mago": errors.append("invalid payload.execution_sequence.owner")
            if sequence.get("rationale") in (None, "", []): errors.append("missing payload.execution_sequence.rationale")
    return errors


def _payload_errors(payload: dict[str, Any], direction: str, item: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in item.get("required_payload", []):
        if payload.get(field) in (None, ""): errors.append(f"missing payload.{field}")
    for category, expected in (("list_payload", list), ("object_payload", dict), ("boolean_payload", bool)):
        for field in item.get(category, []):
            if field in payload and not isinstance(payload[field], expected): errors.append(f"invalid payload.{field}")
    for field, allowed in (item.get("enum_payload") or {}).items():
        if field in payload and payload[field] not in allowed: errors.append(f"invalid payload.{field}")
    declared = set(item.get("required_payload") or []) | set(item.get("optional_payload") or [])
    for category in ("list_payload", "object_payload", "boolean_payload"): declared.update(item.get(category) or [])
    declared.update((item.get("enum_payload") or {}).keys())
    errors += [f"invalid payload field: payload.{field} is not declared for {direction}" for field in sorted(set(payload) - declared)]
    forbidden = recursive_forbidden(payload, set(item.get("forbidden_payload_keys") or []))
    if direction == "nomia_to_mago": forbidden = [error.replace("outside producer authority", "outside nomia authority") for error in forbidden]
    return errors + forbidden


def _projection_errors(direction: str, payload: dict[str, Any], contract: dict[str, Any]) -> list[str]:
    mapping, errors = contract.get("state_mapping") or {}, []
    version = str(mapping.get("version") or "")
    if direction == "mago_to_nomia":
        expected = (mapping.get("mago_planning_to_nomia") or {}).get(payload.get("planning_state"))
        if payload.get("mapping_version") != version: errors.append("invalid payload.mapping_version")
        if expected is None or payload.get("nomia_planning_state") != expected: errors.append("invalid payload.nomia_planning_state projection")
    elif direction == "magia_to_nomia":
        execution = (mapping.get("magia_execution_to_nomia") or {}).get(payload.get("execution_state"))
        validation = (mapping.get("magia_validation_to_nomia") or {}).get(payload.get("validation_state"))
        if payload.get("mapping_version") != version: errors.append("invalid payload.mapping_version")
        if execution is None or payload.get("nomia_execution_state") != execution: errors.append("invalid payload.nomia_execution_state projection")
        if validation is None or payload.get("nomia_validation_state") != validation: errors.append("invalid payload.nomia_validation_state projection")
    return errors


def validate_envelope(envelope: Any, *, as_of: datetime | None = None, role: str | None = None, operation: str = "any", root: Path | None = None) -> dict[str, Any]:
    contract, compatibility, priority = load_contract(root), load_compatibility(root), load_priority_contract(root)
    if not isinstance(envelope, dict):
        return {"status": "rejected", "direction": None, "reasons": ["handoff envelope must be a mapping"], "reason_codes": ["HANDOFF_INVALID_FIELD"], "warnings": []}
    value, reasons = dict(envelope), []
    if value.get("schema_version") != contract.get("schema_version"): reasons.append("invalid schema_version; contract v3 is required")
    if value.get("ecosystem_release") != compatibility.get("ecosystem_release"): reasons.append("invalid ecosystem_release")
    direction = str(value.get("direction") or "")
    item = (contract.get("directions") or {}).get(direction)
    if not isinstance(item, dict): reasons.append("invalid direction"); item = {}
    producer, consumer = item.get("producer"), item.get("consumer")
    envelope_contract = contract.get("envelope") or {}
    for field in envelope_contract.get("required_fields", []):
        if value.get(field) in (None, ""): reasons.append(f"missing {field}")
    allowed = set(envelope_contract.get("required_fields") or []) | set(envelope_contract.get("optional_fields") or [])
    reasons += [f"invalid envelope field: {field}" for field in sorted(set(value) - allowed)]
    if WORKFLOW_ID_RE.fullmatch(str(value.get("workflow_id") or "")) is None: reasons.append("invalid workflow_id")
    causation = value.get("causation_id")
    if causation not in (None, "") and HANDOFF_ID_RE.fullmatch(str(causation)) is None: reasons.append("invalid causation_id")
    if value.get("source_skill") != producer: reasons.append("invalid source_skill for direction")
    if value.get("target_skill") != consumer: reasons.append("invalid target_skill for direction")
    source_version = str(value.get("source_version") or "")
    if SEMVER_RE.fullmatch(source_version) is None: reasons.append("invalid source_version")
    elif source_version != str((compatibility.get("packages") or {}).get(str(producer), "")): reasons.append("incompatible source_version")
    handoff_id = str(value.get("handoff_id") or "")
    if HANDOFF_ID_RE.fullmatch(handoff_id) is None or handoff_id != handoff_id_for(value): reasons.append("invalid handoff_id")
    selected_role = role or package_role(root)
    if operation == "produce" and selected_role != producer: reasons.append(f"invalid producer role; {producer} owns {direction}")
    if operation == "consume" and selected_role != consumer: reasons.append(f"invalid consumer role; {consumer} consumes {direction}")
    if operation not in {"any", "produce", "consume"}: reasons.append("invalid operation")

    observed, check_time = parse_time(value.get("observed_at")), as_of or datetime.now(timezone.utc)
    if observed is None: reasons.append("invalid observed_at")
    freshness = value.get("freshness")
    max_age = freshness.get("max_age_days") if isinstance(freshness, dict) else None
    freshness_policy = envelope_contract.get("freshness_policy") or {}
    max_allowed, skew, min_refs = int(freshness_policy.get("max_age_days", 365)), int(freshness_policy.get("max_future_skew_seconds", 300)), int(freshness_policy.get("min_evidence_refs", 1))
    if isinstance(max_age, bool) or not isinstance(max_age, int) or max_age < 0: reasons.append("invalid freshness.max_age_days")
    elif max_age > max_allowed: reasons.append(f"invalid freshness.max_age_days; exceeds contract maximum {max_allowed}")
    stale = False
    if observed is not None:
        if (observed - check_time).total_seconds() > skew: reasons.append("invalid observed_at; timestamp is in the future")
        elif isinstance(max_age, int):
            stale = (check_time - observed).total_seconds() / 86400 > max_age
            if stale: reasons.append("evidence is stale")

    provenance = value.get("provenance")
    refs: list[str] = []
    if not isinstance(provenance, dict): reasons.append("invalid provenance")
    else:
        for field in envelope_contract.get("provenance_required_fields", []):
            if provenance.get(field) in (None, ""): reasons.append(f"missing provenance.{field}")
        raw_refs = provenance.get("evidence_refs")
        if not isinstance(raw_refs, list): reasons.append("invalid provenance.evidence_refs")
        elif len(raw_refs) < min_refs or not all(isinstance(ref, str) and ref.strip() for ref in raw_refs): reasons.append(f"invalid provenance.evidence_refs; evidence_refs must contain at least {min_refs} non-empty item(s)")
        else: refs = raw_refs
        if producer and provenance.get("authority") != producer: reasons.append("invalid provenance.authority")
    reasons.extend(privacy_errors(value.get("privacy_handling"), contract, refs))
    for field in ("unknowns", "conflicts"):
        entries = value.get(field)
        if not isinstance(entries, list): reasons.append(f"invalid {field}")
        elif not all(isinstance(entry, str) and entry.strip() for entry in entries): reasons.append(f"invalid {field}; entries must be non-empty strings")

    payload = value.get("payload")
    if not isinstance(payload, dict): reasons.append("invalid payload"); payload = {}
    reasons.extend(_payload_errors(payload, direction, item))
    reasons.extend(validate_priority_objects(payload, direction, priority, as_of=check_time, future_skew_seconds=skew))
    if payload.get("spec_id") is not None and not valid_spec_id(payload["spec_id"]): reasons.append("invalid payload.spec_id")
    candidate = payload.get("candidate_spec_id")
    if candidate not in (None, ""):
        if not valid_spec_id(candidate): reasons.append("invalid payload.candidate_spec_id")
        if payload.get("candidate_spec_id_provenance") in (None, "", "unknown"): reasons.append("missing payload.candidate_spec_id_provenance")
        match = SPEC_ID_RE.fullmatch(str(candidate))
        if match and isinstance(payload.get("feature_key"), str) and match.group(2) != payload["feature_key"]: reasons.append("payload.candidate_spec_id feature-key does not match payload.feature_key")
    if payload.get("feature_key") is not None and FEATURE_KEY_RE.fullmatch(str(payload["feature_key"])) is None: reasons.append("invalid payload.feature_key")
    reasons.extend(_projection_errors(direction, payload, contract))
    if isinstance(value.get("conflicts"), list) and value["conflicts"]: reasons.append("conflicting evidence")

    blocking = any(reason.startswith(("invalid", "missing", "incompatible", "privacy_handling")) or "outside producer authority" in reason or "outside nomia authority" in reason or "does not match" in reason for reason in reasons)
    readiness = payload.get("governance_readiness", payload.get("readiness"))
    status = "rejected" if blocking else "conflicting" if "conflicting evidence" in reasons else "stale" if stale else "draft" if readiness in {"draft", "unknown", False} else "accepted"
    return {"status": status, "direction": direction, "schema_version": value.get("schema_version"), "compatibility": "native-v3", "reasons": reasons, "reason_codes": list(dict.fromkeys(map(reason_code, reasons))), "warnings": [], "source_skill": value.get("source_skill"), "target_skill": value.get("target_skill")}


def apply_state_projection(direction: str, payload: dict[str, Any], contract: dict[str, Any]) -> dict[str, Any]:
    result = json.loads(json.dumps(payload))
    mapping, version = contract.get("state_mapping") or {}, (contract.get("state_mapping") or {}).get("version")
    if direction == "mago_to_nomia":
        result.update(nomia_planning_state=(mapping.get("mago_planning_to_nomia") or {}).get(result.get("planning_state")), mapping_version=version)
    elif direction == "magia_to_nomia":
        result.update(nomia_execution_state=(mapping.get("magia_execution_to_nomia") or {}).get(result.get("execution_state")), nomia_validation_state=(mapping.get("magia_validation_to_nomia") or {}).get(result.get("validation_state")), mapping_version=version)
    return result


def build_envelope(*, direction: str, payload: dict[str, Any], source: str, authority: str, evidence_refs: list[str], observed_at: str, freshness_days: int, workflow_id: str, privacy_handling: dict[str, Any], causation_id: str | None = None, unknowns: list[str] | None = None, conflicts: list[str] | None = None, root: Path | None = None) -> dict[str, Any]:
    contract, compatibility = load_contract(root), load_compatibility(root)
    item = (contract.get("directions") or {}).get(direction)
    if not isinstance(item, dict): raise ValueError(f"unsupported direction: {direction}")
    role = package_role(root)
    if item.get("producer") != role: raise ValueError(f"{role} cannot produce {direction}; owner is {item.get('producer')}")
    envelope = {
        "schema_version": contract["schema_version"], "ecosystem_release": compatibility["ecosystem_release"], "direction": direction,
        "source_skill": role, "source_version": package_version(root), "target_skill": item["consumer"], "workflow_id": workflow_id,
        "observed_at": observed_at, "privacy_handling": json.loads(json.dumps(privacy_handling)),
        "provenance": {"source": source, "authority": authority, "evidence_refs": list(evidence_refs)}, "freshness": {"max_age_days": freshness_days},
        "payload": apply_state_projection(direction, payload, contract), "unknowns": list(unknowns or []), "conflicts": list(conflicts or []),
    }
    if causation_id: envelope["causation_id"] = causation_id
    envelope["handoff_id"] = handoff_id_for(envelope)
    result = validate_envelope(envelope, role=role, operation="produce", root=root)
    if result["status"] not in {"accepted", "draft"}: raise ValueError("cannot build invalid handoff: " + "; ".join(result["reasons"]))
    return envelope


def emit_json(data: dict[str, Any], output: str | None) -> None:
    text = json.dumps(data, indent=2, sort_keys=True) + "\n"
    if output: atomic_write_text(Path(output), text)
    print(text, end="")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build")
    for flag in ("direction", "payload", "source", "authority", "workflow-id", "privacy", "output"): build.add_argument(f"--{flag}", required=True)
    build.add_argument("--evidence-ref", action="append", default=[]); build.add_argument("--observed-at", default=datetime.now(timezone.utc).replace(microsecond=0).isoformat()); build.add_argument("--freshness-days", type=int, default=30); build.add_argument("--causation-id"); build.add_argument("--unknown", action="append", default=[]); build.add_argument("--conflict", action="append", default=[])
    validate = commands.add_parser("validate"); validate.add_argument("--input", required=True); validate.add_argument("--operation", choices=("any", "produce", "consume"), default="consume"); validate.add_argument("--as-of", default=datetime.now(timezone.utc).replace(microsecond=0).isoformat()); validate.add_argument("--json-output"); validate.add_argument("--allow-draft", action="store_true")
    workflow = commands.add_parser("workflow-id"); workflow.add_argument("--seed", required=True)
    contract = commands.add_parser("contract"); contract.add_argument("--json-output")
    args, root = parser.parse_args(argv), root_for_script()
    try:
        if args.command == "build":
            envelope = build_envelope(direction=args.direction, payload=load_json_object(Path(args.payload), "payload"), source=args.source, authority=args.authority, evidence_refs=args.evidence_ref, observed_at=args.observed_at, freshness_days=args.freshness_days, workflow_id=args.workflow_id, privacy_handling=load_json_object(Path(args.privacy), "privacy_handling"), causation_id=args.causation_id, unknowns=args.unknown, conflicts=args.conflict, root=root)
            emit_json(envelope, args.output); return 0
        if args.command == "workflow-id": emit_json({"workflow_id": workflow_id_for(args.seed)}, None); return 0
        if args.command == "validate":
            as_of = parse_time(args.as_of)
            if as_of is None: raise ValueError("--as-of must be ISO-8601")
            result = validate_envelope(load_json_object(Path(args.input), "handoff envelope"), as_of=as_of, role=package_role(root), operation=args.operation, root=root)
            emit_json(result, args.json_output); return validation_exit_code(result["status"], allow_draft=args.allow_draft)
        errors = contract_errors(load_contract(root), root)
        result = {"status": "pass" if not errors else "fail", "errors": errors, "role": package_role(root)}
        emit_json(result, args.json_output); return 0 if not errors else 1
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, indent=2, sort_keys=True)); return 2


if __name__ == "__main__":
    raise SystemExit(main())
