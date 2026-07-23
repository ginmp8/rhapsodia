#!/usr/bin/env python3
"""Build and validate strict Nomia/Mago/Magia ecosystem handoff envelopes."""
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
SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
FEATURE_KEY_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SPEC_ID_RE = re.compile(r"^spec-(\d{4}-\d{2}-\d{2})-([a-z0-9]+(?:-[a-z0-9]+)*)$")
HANDOFF_ID_RE = re.compile(r"^handoff-[0-9a-f]{16}$")
VALIDATION_EXIT_CODES = {"accepted": 0, "error": 2, "draft": 3, "stale": 4, "conflicting": 5, "rejected": 6}


def validation_exit_code(status: str, *, allow_draft: bool = False) -> int:
    if status == "draft" and allow_draft:
        return 0
    return VALIDATION_EXIT_CODES.get(status, 2)


def reason_code(reason: str) -> str:
    rules = (
        ("invalid schema_version", "HANDOFF_INVALID_SCHEMA"),
        ("invalid ecosystem_release", "HANDOFF_INVALID_ECOSYSTEM_RELEASE"),
        ("incompatible source_version", "HANDOFF_INCOMPATIBLE_SOURCE_VERSION"),
        ("invalid handoff_id", "HANDOFF_INVALID_ID"),
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
        if fragment in reason:
            return code
    if reason.startswith("missing"):
        return "HANDOFF_MISSING_FIELD"
    if reason.startswith("invalid"):
        return "HANDOFF_INVALID_FIELD"
    return "HANDOFF_REJECTED"


def root_for_script() -> Path:
    return Path(__file__).resolve().parents[1]


def atomic_write_text(path: Path, text: str) -> None:
    path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def load_json_object(path: Path, label: str) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{label} must be a JSON object")
    return data


def load_contract(root: Path | None = None) -> dict[str, Any]:
    base = (root or root_for_script()).resolve()
    return load_json_object(base / CONTRACT_FILE, "ecosystem handoff contract")


def load_compatibility(root: Path | None = None) -> dict[str, Any]:
    base = (root or root_for_script()).resolve()
    return load_json_object(base / COMPATIBILITY_FILE, "ecosystem compatibility manifest")


def load_priority_contract(root: Path | None = None) -> dict[str, Any]:
    base = (root or root_for_script()).resolve()
    return load_json_object(base / PRIORITY_FILE, "ecosystem priority contract")


def package_role(root: Path | None = None) -> str:
    package_root = (root or root_for_script()).resolve()
    direct = package_root.name.lower()
    if direct in {"nomia", "mago", "magia"}:
        return direct
    release_path = package_root / "release.json"
    if release_path.is_file():
        try:
            name = str(json.loads(release_path.read_text(encoding="utf-8")).get("name") or "").lower()
            if name in {"nomia", "mago", "magia"}:
                return name
        except (OSError, ValueError, TypeError):
            pass
    skill_path = package_root / "SKILL.md"
    if skill_path.is_file():
        match = re.search(r"(?m)^name:\s*[\"']?([a-z0-9-]+)", skill_path.read_text(encoding="utf-8"))
        if match and match.group(1).lower() in {"nomia", "mago", "magia"}:
            return match.group(1).lower()
    raise ValueError(f"unsupported package role: {package_root.name}")


def package_version(root: Path | None = None) -> str:
    base = (root or root_for_script()).resolve()
    version_file = base / "VERSION"
    if version_file.is_file():
        version = version_file.read_text(encoding="utf-8").strip()
    else:
        release = load_json_object(base / "release.json", "release metadata")
        version = str(release.get("version") or "")
    if SEMVER_RE.fullmatch(version) is None:
        raise ValueError(f"package version is not stable semantic versioning: {version}")
    return version


def parse_time(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        parsed = value
    elif value in (None, "", "unknown"):
        return None
    else:
        try:
            parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError:
            return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def valid_spec_id(value: Any) -> bool:
    match = SPEC_ID_RE.fullmatch(str(value or ""))
    if match is None:
        return False
    try:
        datetime.strptime(match.group(1), "%Y-%m-%d")
    except ValueError:
        return False
    return True


def contract_errors(contract: dict[str, Any], root: Path | None = None) -> list[str]:
    errors: list[str] = []
    compatibility = load_compatibility(root)
    priority = load_priority_contract(root)
    if contract.get("schema_version") != "2.0.0":
        errors.append("contract schema_version must be 2.0.0")
    if contract.get("contract_id") != "nomia-mago-magia-handoff-v2":
        errors.append("contract_id must be nomia-mago-magia-handoff-v2")
    if contract.get("ecosystem_release") != compatibility.get("ecosystem_release"):
        errors.append("handoff ecosystem_release must match compatibility manifest")
    policy = contract.get("compatibility")
    if not isinstance(policy, dict) or policy.get("classification") != "breaking-no-legacy":
        errors.append("handoff compatibility must be breaking-no-legacy")
    elif policy.get("legacy_read_support") is not False:
        errors.append("handoff legacy_read_support must be false")
    envelope = contract.get("envelope")
    roles = contract.get("roles")
    directions = contract.get("directions")
    mappings = contract.get("state_mapping")
    if not isinstance(envelope, dict):
        errors.append("contract envelope must be an object")
        envelope = {}
    required = set(envelope.get("required_fields") or [])
    for field in ("schema_version","ecosystem_release","source_skill","source_version","target_skill","handoff_id","payload"):
        if field not in required:
            errors.append(f"envelope.required_fields missing {field}")
    freshness_policy = envelope.get("freshness_policy")
    if not isinstance(freshness_policy, dict):
        errors.append("envelope.freshness_policy must be an object")
    else:
        if not isinstance(freshness_policy.get("max_age_days"), int) or freshness_policy.get("max_age_days", 0) <= 0:
            errors.append("envelope.freshness_policy.max_age_days must be a positive integer")
        if not isinstance(freshness_policy.get("max_future_skew_seconds"), int) or freshness_policy.get("max_future_skew_seconds", -1) < 0:
            errors.append("envelope.freshness_policy.max_future_skew_seconds must be a non-negative integer")
        if not isinstance(freshness_policy.get("min_evidence_refs"), int) or freshness_policy.get("min_evidence_refs", 0) < 1:
            errors.append("envelope.freshness_policy.min_evidence_refs must be at least 1")
    if not isinstance(roles, dict):
        errors.append("contract roles must be an object")
        roles = {}
    if not isinstance(directions, dict) or not directions:
        errors.append("contract directions must be a non-empty object")
        directions = {}
    expected_directions = set(compatibility.get("required_directions") or [])
    if set(directions) != expected_directions:
        errors.append("handoff directions must exactly match compatibility manifest")
    if not isinstance(mappings, dict) or mappings.get("version") != "2.0.0":
        errors.append("state_mapping.version must be 2.0.0")
    for role in ("nomia","mago","magia"):
        item = roles.get(role)
        if not isinstance(item, dict):
            errors.append(f"missing role contract: {role}")
            continue
        for field in ("produces","consumes"):
            if not isinstance(item.get(field), list):
                errors.append(f"roles.{role}.{field} must be a list")
    for direction, item in directions.items():
        if not isinstance(item, dict):
            errors.append(f"directions.{direction} must be an object")
            continue
        producer, consumer = item.get("producer"), item.get("consumer")
        if producer not in roles or consumer not in roles:
            errors.append(f"directions.{direction} producer/consumer is invalid")
            continue
        if direction not in roles[producer].get("produces", []):
            errors.append(f"direction {direction} missing from producer {producer}")
        if direction not in roles[consumer].get("consumes", []):
            errors.append(f"direction {direction} missing from consumer {consumer}")
        if not isinstance(item.get("required_payload"), list) or not item.get("required_payload"):
            errors.append(f"directions.{direction}.required_payload must be non-empty")
        if not isinstance(item.get("optional_payload"), list):
            errors.append(f"directions.{direction}.optional_payload must be a list")
    if priority.get("contract_id") != "nomia-mago-magia-priority-v2":
        errors.append("priority contract id mismatch")
    if priority.get("ecosystem_release") != compatibility.get("ecosystem_release"):
        errors.append("priority ecosystem_release must match compatibility manifest")
    return errors


def recursive_forbidden(value: Any, forbidden: set[str], prefix: str = "payload") -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            current = f"{prefix}.{key}"
            if str(key) in forbidden or str(key) in {"priority", "order_hint"}:
                errors.append(f"{current} is outside producer authority")
            errors.extend(recursive_forbidden(child, forbidden, current))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(recursive_forbidden(child, forbidden, f"{prefix}[{index}]"))
    return errors


def handoff_id_for(envelope: dict[str, Any]) -> str:
    canonical_data = {key: value for key, value in envelope.items() if key != "handoff_id"}
    canonical = json.dumps(canonical_data, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "handoff-" + hashlib.sha256(canonical).hexdigest()[:16]


def validate_priority_objects(payload: dict[str, Any], direction: str, priority: dict[str, Any], *, as_of: datetime, future_skew_seconds: int) -> list[str]:
    errors: list[str] = []
    concepts = priority.get("concepts") or {}
    if direction == "nomia_to_mago":
        item = payload.get("business_priority")
        if not isinstance(item, dict):
            return ["invalid payload.business_priority"]
        allowed = ((concepts.get("business_priority") or {}).get("values") or [])
        if item.get("level") not in allowed:
            errors.append("invalid payload.business_priority.level")
        if item.get("owner") != "nomia":
            errors.append("invalid payload.business_priority.owner")
        if item.get("level") != "unknown":
            if item.get("source") in (None, "", "unknown"):
                errors.append("missing payload.business_priority.source")
            priority_observed_at = parse_time(item.get("observed_at"))
            if priority_observed_at is None:
                errors.append("invalid payload.business_priority.observed_at")
            elif (priority_observed_at - as_of).total_seconds() > future_skew_seconds:
                errors.append("invalid payload.business_priority.observed_at; timestamp is in the future")
    if direction == "mago_to_magia":
        criticality = payload.get("technical_criticality")
        sequence = payload.get("execution_sequence")
        if not isinstance(criticality, dict):
            errors.append("invalid payload.technical_criticality")
        else:
            allowed = ((concepts.get("technical_criticality") or {}).get("values") or [])
            if criticality.get("level") not in allowed:
                errors.append("invalid payload.technical_criticality.level")
            if criticality.get("owner") != "mago":
                errors.append("invalid payload.technical_criticality.owner")
            if criticality.get("rationale") in (None, "", []):
                errors.append("missing payload.technical_criticality.rationale")
        if not isinstance(sequence, dict):
            errors.append("invalid payload.execution_sequence")
        else:
            allowed = ((concepts.get("execution_sequence") or {}).get("lanes") or [])
            if sequence.get("lane") not in allowed:
                errors.append("invalid payload.execution_sequence.lane")
            if not isinstance(sequence.get("rank"), int) or sequence.get("rank") < 0:
                errors.append("invalid payload.execution_sequence.rank")
            if sequence.get("owner") != "mago":
                errors.append("invalid payload.execution_sequence.owner")
            if sequence.get("rationale") in (None, "", []):
                errors.append("missing payload.execution_sequence.rationale")
    return errors


def validate_envelope(envelope: Any, *, as_of: datetime | None = None, role: str | None = None, operation: str = "any", root: Path | None = None) -> dict[str, Any]:
    contract = load_contract(root)
    compatibility = load_compatibility(root)
    priority = load_priority_contract(root)
    reasons: list[str] = []
    if not isinstance(envelope, dict):
        return {"status":"rejected","direction":None,"reasons":["handoff envelope must be a mapping"],"reason_codes":["HANDOFF_INVALID_FIELD"],"warnings":[]}
    normalized = dict(envelope)
    if normalized.get("schema_version") != contract.get("schema_version"):
        reasons.append("invalid schema_version; contract v2 is required")
    if normalized.get("ecosystem_release") != compatibility.get("ecosystem_release"):
        reasons.append("invalid ecosystem_release")
    direction = normalized.get("direction")
    direction_contract = (contract.get("directions") or {}).get(str(direction))
    if not isinstance(direction_contract, dict):
        reasons.append("invalid direction")
        direction_contract = {}
    producer, consumer = direction_contract.get("producer"), direction_contract.get("consumer")
    for field in (contract.get("envelope") or {}).get("required_fields", []):
        if field not in normalized or normalized.get(field) in (None, ""):
            reasons.append(f"missing {field}")
    if normalized.get("source_skill") != producer:
        reasons.append("invalid source_skill for direction")
    if normalized.get("target_skill") != consumer:
        reasons.append("invalid target_skill for direction")
    source_version = str(normalized.get("source_version") or "")
    if SEMVER_RE.fullmatch(source_version) is None:
        reasons.append("invalid source_version")
    elif source_version != str((compatibility.get("packages") or {}).get(str(producer)) or ""):
        reasons.append("incompatible source_version")
    handoff_id = str(normalized.get("handoff_id") or "")
    if HANDOFF_ID_RE.fullmatch(handoff_id) is None or handoff_id != handoff_id_for(normalized):
        reasons.append("invalid handoff_id")
    selected_role = role or package_role(root)
    if operation == "produce" and selected_role != producer:
        reasons.append(f"invalid producer role; {producer} owns {direction}")
    if operation == "consume" and selected_role != consumer:
        reasons.append(f"invalid consumer role; {consumer} consumes {direction}")
    if operation not in {"any","produce","consume"}:
        reasons.append("invalid operation")
    observed_at = parse_time(normalized.get("observed_at"))
    if observed_at is None:
        reasons.append("invalid observed_at")
    freshness = normalized.get("freshness")
    max_age_days = freshness.get("max_age_days") if isinstance(freshness, dict) else None
    freshness_policy = (contract.get("envelope") or {}).get("freshness_policy") or {}
    maximum_age_days = int(freshness_policy.get("max_age_days", 365))
    future_skew_seconds = int(freshness_policy.get("max_future_skew_seconds", 300))
    minimum_evidence_refs = int(freshness_policy.get("min_evidence_refs", 1))
    if not isinstance(max_age_days, int) or max_age_days < 0:
        reasons.append("invalid freshness.max_age_days")
    elif max_age_days > maximum_age_days:
        reasons.append(f"invalid freshness.max_age_days; exceeds contract maximum {maximum_age_days}")
    stale = False
    check_time = as_of or datetime.now(timezone.utc)
    if observed_at is not None:
        if (observed_at - check_time).total_seconds() > future_skew_seconds:
            reasons.append("invalid observed_at; timestamp is in the future")
        elif isinstance(max_age_days, int):
            stale = (check_time - observed_at).total_seconds() / 86400 > max_age_days
            if stale:
                reasons.append("evidence is stale")
    provenance = normalized.get("provenance")
    if not isinstance(provenance, dict):
        reasons.append("invalid provenance")
    else:
        for field in (contract.get("envelope") or {}).get("provenance_required_fields", []):
            if field not in provenance or provenance.get(field) in (None, ""):
                reasons.append(f"missing provenance.{field}")
        evidence_refs = provenance.get("evidence_refs")
        if not isinstance(evidence_refs, list):
            reasons.append("invalid provenance.evidence_refs")
        elif len(evidence_refs) < minimum_evidence_refs or not all(isinstance(ref, str) and ref.strip() for ref in evidence_refs):
            reasons.append(f"invalid provenance.evidence_refs; evidence_refs must contain at least {minimum_evidence_refs} non-empty item(s)")
        if producer and provenance.get("authority") != producer:
            reasons.append("invalid provenance.authority")
    for field in ("unknowns","conflicts"):
        value = normalized.get(field)
        if not isinstance(value, list):
            reasons.append(f"invalid {field}")
        elif not all(isinstance(item, str) and item.strip() for item in value):
            reasons.append(f"invalid {field}; entries must be non-empty strings")
    payload = normalized.get("payload")
    if not isinstance(payload, dict):
        reasons.append("invalid payload")
        payload = {}
    for field in direction_contract.get("required_payload", []):
        if field not in payload or payload.get(field) in (None, ""):
            reasons.append(f"missing payload.{field}")
    for field in direction_contract.get("list_payload", []):
        if field in payload and not isinstance(payload.get(field), list):
            reasons.append(f"invalid payload.{field}")
    for field in direction_contract.get("object_payload", []):
        if field in payload and not isinstance(payload.get(field), dict):
            reasons.append(f"invalid payload.{field}")
    for field in direction_contract.get("boolean_payload", []):
        if field in payload and not isinstance(payload.get(field), bool):
            reasons.append(f"invalid payload.{field}")
    for field, allowed in (direction_contract.get("enum_payload") or {}).items():
        if field in payload and payload.get(field) not in allowed:
            reasons.append(f"invalid payload.{field}")
    declared_payload_fields = set(direction_contract.get("required_payload") or [])
    declared_payload_fields.update(direction_contract.get("optional_payload") or [])
    for category in ("list_payload", "object_payload", "boolean_payload"):
        declared_payload_fields.update(direction_contract.get(category) or [])
    declared_payload_fields.update((direction_contract.get("enum_payload") or {}).keys())
    for extra_field in sorted(set(payload) - declared_payload_fields):
        reasons.append(f"invalid payload field: payload.{extra_field} is not declared for {direction}")
    forbidden = recursive_forbidden(payload, set(direction_contract.get("forbidden_payload_keys") or []))
    if direction == "nomia_to_mago":
        forbidden = [item.replace("outside producer authority", "outside nomia authority") for item in forbidden]
    reasons.extend(forbidden)
    reasons.extend(validate_priority_objects(payload, str(direction), priority, as_of=check_time, future_skew_seconds=future_skew_seconds))
    spec_id = payload.get("spec_id")
    if spec_id is not None and not valid_spec_id(spec_id):
        reasons.append("invalid payload.spec_id")
    candidate = payload.get("candidate_spec_id")
    if candidate not in (None, ""):
        if not valid_spec_id(candidate):
            reasons.append("invalid payload.candidate_spec_id")
        if payload.get("candidate_spec_id_provenance") in (None, "", "unknown"):
            reasons.append("missing payload.candidate_spec_id_provenance")
        feature_key = payload.get("feature_key")
        match = SPEC_ID_RE.fullmatch(str(candidate))
        if match is not None and isinstance(feature_key, str) and match.group(2) != feature_key:
            reasons.append("payload.candidate_spec_id feature-key does not match payload.feature_key")
    feature_key = payload.get("feature_key")
    if feature_key is not None and FEATURE_KEY_RE.fullmatch(str(feature_key)) is None:
        reasons.append("invalid payload.feature_key")
    mapping = contract.get("state_mapping") or {}
    mapping_version = str(mapping.get("version") or "")
    if direction == "mago_to_nomia":
        expected = (mapping.get("mago_planning_to_nomia") or {}).get(payload.get("planning_state"))
        if payload.get("mapping_version") != mapping_version:
            reasons.append("invalid payload.mapping_version")
        if expected is None or payload.get("nomia_planning_state") != expected:
            reasons.append("invalid payload.nomia_planning_state projection")
    if direction == "magia_to_nomia":
        execution_expected = (mapping.get("magia_execution_to_nomia") or {}).get(payload.get("execution_state"))
        validation_expected = (mapping.get("magia_validation_to_nomia") or {}).get(payload.get("validation_state"))
        if payload.get("mapping_version") != mapping_version:
            reasons.append("invalid payload.mapping_version")
        if execution_expected is None or payload.get("nomia_execution_state") != execution_expected:
            reasons.append("invalid payload.nomia_execution_state projection")
        if validation_expected is None or payload.get("nomia_validation_state") != validation_expected:
            reasons.append("invalid payload.nomia_validation_state projection")
    conflicts = normalized.get("conflicts") if isinstance(normalized.get("conflicts"), list) else []
    if conflicts:
        reasons.append("conflicting evidence")
    blocking = [reason for reason in reasons if reason.startswith(("invalid","missing","incompatible")) or "outside producer authority" in reason or "outside nomia authority" in reason or "does not match" in reason]
    readiness = payload.get("governance_readiness", payload.get("readiness"))
    if blocking:
        status = "rejected"
    elif "conflicting evidence" in reasons:
        status = "conflicting"
    elif stale:
        status = "stale"
    elif readiness in {"draft","unknown",False}:
        status = "draft"
    else:
        status = "accepted"
    return {"status":status,"direction":direction,"schema_version":normalized.get("schema_version"),"compatibility":"native-v2","reasons":reasons,"reason_codes":list(dict.fromkeys(reason_code(reason) for reason in reasons)),"warnings":[],"source_skill":normalized.get("source_skill"),"target_skill":normalized.get("target_skill")}


def apply_state_projection(direction: str, payload: dict[str, Any], contract: dict[str, Any]) -> dict[str, Any]:
    result = json.loads(json.dumps(payload))
    mapping = contract.get("state_mapping") or {}
    version = mapping.get("version")
    if direction == "mago_to_nomia":
        result["nomia_planning_state"] = (mapping.get("mago_planning_to_nomia") or {}).get(result.get("planning_state"))
        result["mapping_version"] = version
    elif direction == "magia_to_nomia":
        result["nomia_execution_state"] = (mapping.get("magia_execution_to_nomia") or {}).get(result.get("execution_state"))
        result["nomia_validation_state"] = (mapping.get("magia_validation_to_nomia") or {}).get(result.get("validation_state"))
        result["mapping_version"] = version
    return result


def build_envelope(*, direction: str, payload: dict[str, Any], source: str, authority: str, evidence_refs: list[str], observed_at: str, freshness_days: int, unknowns: list[str] | None = None, conflicts: list[str] | None = None, root: Path | None = None) -> dict[str, Any]:
    contract = load_contract(root)
    compatibility = load_compatibility(root)
    direction_contract = (contract.get("directions") or {}).get(direction)
    if not isinstance(direction_contract, dict):
        raise ValueError(f"unsupported direction: {direction}")
    role = package_role(root)
    if direction_contract.get("producer") != role:
        raise ValueError(f"{role} cannot produce {direction}; owner is {direction_contract.get('producer')}")
    mapped_payload = apply_state_projection(direction, payload, contract)
    envelope = {
        "schema_version":contract["schema_version"],
        "ecosystem_release":compatibility["ecosystem_release"],
        "direction":direction,
        "source_skill":role,
        "source_version":package_version(root),
        "target_skill":direction_contract["consumer"],
        "observed_at":observed_at,
        "provenance":{"source":source,"authority":authority,"evidence_refs":list(evidence_refs)},
        "freshness":{"max_age_days":freshness_days},
        "payload":mapped_payload,
        "unknowns":list(unknowns or []),
        "conflicts":list(conflicts or []),
    }
    envelope["handoff_id"] = handoff_id_for(envelope)
    result = validate_envelope(envelope, role=role, operation="produce", root=root)
    if result["status"] not in {"accepted","draft"}:
        raise ValueError("cannot build invalid handoff: " + "; ".join(result["reasons"]))
    return envelope


def emit_json(data: dict[str, Any], output: str | None) -> None:
    text = json.dumps(data, indent=2, sort_keys=True) + "\n"
    if output:
        atomic_write_text(Path(output), text)
    print(text, end="")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build or validate a strict ecosystem handoff envelope.")
    sub = parser.add_subparsers(dest="command", required=True)
    build = sub.add_parser("build", help="Build a contract-v2 envelope owned by the current package.")
    build.add_argument("--direction", required=True)
    build.add_argument("--payload", required=True)
    build.add_argument("--source", required=True)
    build.add_argument("--authority", required=True)
    build.add_argument("--evidence-ref", action="append", default=[])
    build.add_argument("--observed-at", default=datetime.now(timezone.utc).replace(microsecond=0).isoformat())
    build.add_argument("--freshness-days", type=int, default=30)
    build.add_argument("--unknown", action="append", default=[])
    build.add_argument("--conflict", action="append", default=[])
    build.add_argument("--output", required=True)
    validate = sub.add_parser("validate", help="Validate an incoming or outgoing contract-v2 envelope.")
    validate.add_argument("--input", required=True)
    validate.add_argument("--operation", choices=["any","produce","consume"], default="consume")
    validate.add_argument("--as-of", default=datetime.now(timezone.utc).replace(microsecond=0).isoformat())
    validate.add_argument("--json-output")
    validate.add_argument("--allow-draft", action="store_true", help="Treat a structurally valid draft as successful inspection; never use this flag to authorize mutation.")
    contract = sub.add_parser("contract", help="Validate local handoff, priority, and compatibility contracts.")
    contract.add_argument("--json-output")
    args = parser.parse_args(argv)
    root = root_for_script()
    try:
        if args.command == "build":
            payload = load_json_object(Path(args.payload), "payload")
            envelope = build_envelope(direction=args.direction,payload=payload,source=args.source,authority=args.authority,evidence_refs=args.evidence_ref,observed_at=args.observed_at,freshness_days=args.freshness_days,unknowns=args.unknown,conflicts=args.conflict,root=root)
            emit_json(envelope, args.output)
            return 0
        if args.command == "validate":
            envelope = load_json_object(Path(args.input), "handoff envelope")
            as_of = parse_time(args.as_of)
            if as_of is None:
                raise ValueError("--as-of must be ISO-8601")
            result = validate_envelope(envelope, as_of=as_of, role=package_role(root), operation=args.operation, root=root)
            emit_json(result, args.json_output)
            return validation_exit_code(result["status"], allow_draft=args.allow_draft)
        errors = contract_errors(load_contract(root), root)
        result = {"status":"pass" if not errors else "fail","errors":errors,"role":package_role(root)}
        emit_json(result, args.json_output)
        return 0 if not errors else 1
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"status":"error","error":str(exc)}, indent=2, sort_keys=True))
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
