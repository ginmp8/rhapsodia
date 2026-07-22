#!/usr/bin/env python3
"""Build and validate local Nomia/Mago/Magia ecosystem handoff envelopes."""

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
SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
FEATURE_KEY_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SPEC_ID_RE = re.compile(r"^spec-(\d{4}-\d{2}-\d{2})-([a-z0-9]+(?:-[a-z0-9]+)*)$")


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


def package_role(root: Path | None = None) -> str:
    package_root = (root or root_for_script()).resolve()
    direct = package_root.name.lower()
    if direct in {"nomia", "mago", "magia"}:
        return direct
    release_path = package_root / "release.json"
    if release_path.is_file():
        try:
            release_name = str(json.loads(release_path.read_text(encoding="utf-8")).get("name") or "").lower()
            if release_name in {"nomia", "mago", "magia"}:
                return release_name
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


def contract_errors(contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if contract.get("schema_version") != "1.0.0":
        errors.append("contract schema_version must be 1.0.0")
    if contract.get("contract_id") != "nomia-mago-magia-handoff-v1":
        errors.append("contract_id must be nomia-mago-magia-handoff-v1")
    envelope = contract.get("envelope")
    roles = contract.get("roles")
    directions = contract.get("directions")
    mappings = contract.get("state_mapping")
    if not isinstance(envelope, dict):
        errors.append("contract envelope must be an object")
    if not isinstance(roles, dict):
        errors.append("contract roles must be an object")
        roles = {}
    if not isinstance(directions, dict) or not directions:
        errors.append("contract directions must be a non-empty object")
        directions = {}
    if not isinstance(mappings, dict) or not SEMVER_RE.fullmatch(str(mappings.get("version") or "")):
        errors.append("state_mapping.version must be semantic versioning")
    for role in ("nomia", "mago", "magia"):
        item = roles.get(role)
        if not isinstance(item, dict):
            errors.append(f"missing role contract: {role}")
            continue
        for field in ("produces", "consumes"):
            if not isinstance(item.get(field), list):
                errors.append(f"roles.{role}.{field} must be a list")
    for direction, item in directions.items():
        if not isinstance(item, dict):
            errors.append(f"directions.{direction} must be an object")
            continue
        producer = item.get("producer")
        consumer = item.get("consumer")
        if producer not in roles:
            errors.append(f"directions.{direction}.producer is invalid")
        if consumer not in {*roles, "stakeholder"}:
            errors.append(f"directions.{direction}.consumer is invalid")
        if producer in roles and direction not in roles[producer].get("produces", []):
            errors.append(f"direction {direction} is not declared under producer {producer}")
        if consumer in roles and direction not in roles[consumer].get("consumes", []):
            errors.append(f"direction {direction} is not declared under consumer {consumer}")
        if not isinstance(item.get("required_payload"), list) or not item.get("required_payload"):
            errors.append(f"directions.{direction}.required_payload must be non-empty")
    return errors


def normalize_legacy(envelope: dict[str, Any], contract: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    normalized = json.loads(json.dumps(envelope))
    warnings: list[str] = []
    direction = str(normalized.get("direction") or "")
    direction_contract = (contract.get("directions") or {}).get(direction) or {}
    producer = direction_contract.get("producer")
    consumer = direction_contract.get("consumer")
    if normalized.get("schema_version") == contract.get("schema_version"):
        return normalized, warnings
    warnings.append("legacy envelope accepted only for compatibility migration; rebuild with contract v1")
    normalized["schema_version"] = "legacy-v0"
    normalized.setdefault("source_skill", producer)
    normalized.setdefault("source_version", "legacy")
    normalized.setdefault("target_skill", consumer)
    provenance = normalized.get("provenance")
    legacy_source = normalized.get("source")
    if not isinstance(provenance, dict):
        provenance = {
            "source": str(legacy_source or provenance or "unknown"),
            "authority": str(producer or "unknown"),
            "evidence_refs": [str(provenance)] if provenance not in (None, "", "unknown") else [],
        }
    normalized["provenance"] = provenance
    if not isinstance(normalized.get("freshness"), dict):
        normalized["freshness"] = {"max_age_days": normalized.get("freshness_days")}
    normalized.setdefault("unknowns", [])
    conflicts: list[str] = []
    if normalized.get("conflict"):
        conflicts.append("legacy top-level conflict flag")
    payload = normalized.get("payload") if isinstance(normalized.get("payload"), dict) else {}
    if payload.get("conflict"):
        conflicts.append("legacy payload conflict flag")
    normalized.setdefault("conflicts", conflicts)
    if direction == "nomia_to_mago" and "governance_readiness" not in payload and "readiness" in payload:
        payload["governance_readiness"] = payload.get("readiness")
    normalized["payload"] = payload
    return normalized, warnings


def recursive_forbidden(value: Any, forbidden: set[str], prefix: str = "payload") -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            current = f"{prefix}.{key}"
            if str(key) in forbidden:
                errors.append(f"{current} is outside producer authority")
            errors.extend(recursive_forbidden(child, forbidden, current))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(recursive_forbidden(child, forbidden, f"{prefix}[{index}]"))
    return errors


def validate_envelope(
    envelope: Any,
    *,
    as_of: datetime | None = None,
    role: str | None = None,
    operation: str = "any",
    allow_legacy: bool = False,
    root: Path | None = None,
) -> dict[str, Any]:
    contract = load_contract(root)
    reasons: list[str] = []
    warnings: list[str] = []
    if not isinstance(envelope, dict):
        return {"status": "rejected", "direction": None, "reasons": ["handoff envelope must be a mapping"], "warnings": []}
    native = envelope.get("schema_version") == contract.get("schema_version")
    if not native and not allow_legacy:
        reasons.append("invalid schema_version; contract v1 is required")
        normalized = dict(envelope)
    else:
        normalized, migration_warnings = normalize_legacy(envelope, contract)
        warnings.extend(migration_warnings)
    direction = normalized.get("direction")
    directions = contract.get("directions") or {}
    direction_contract = directions.get(str(direction))
    if not isinstance(direction_contract, dict):
        reasons.append("invalid direction")
        direction_contract = {}
    producer = direction_contract.get("producer")
    consumer = direction_contract.get("consumer")

    if native:
        for field in (contract.get("envelope") or {}).get("required_fields", []):
            if field not in normalized or normalized.get(field) in (None, ""):
                reasons.append(f"missing {field}")
        if normalized.get("source_skill") != producer:
            reasons.append("invalid source_skill for direction")
        if normalized.get("target_skill") != consumer:
            reasons.append("invalid target_skill for direction")
        if SEMVER_RE.fullmatch(str(normalized.get("source_version") or "")) is None:
            reasons.append("invalid source_version")
    else:
        for field in (contract.get("envelope") or {}).get("legacy_required_fields", []):
            if field not in envelope or envelope.get(field) in (None, "", []):
                reasons.append(f"missing {field}")

    selected_role = role or package_role(root)
    if operation == "produce" and selected_role != producer:
        reasons.append(f"invalid producer role; {producer} owns {direction}")
    if operation == "consume" and selected_role != consumer:
        reasons.append(f"invalid consumer role; {consumer} consumes {direction}")
    if operation not in {"any", "produce", "consume"}:
        reasons.append("invalid operation")

    observed_at = parse_time(normalized.get("observed_at"))
    if observed_at is None:
        reasons.append("invalid observed_at")
    freshness = normalized.get("freshness")
    max_age_days = freshness.get("max_age_days") if isinstance(freshness, dict) else None
    if not isinstance(max_age_days, int) or max_age_days < 0:
        reasons.append("invalid freshness.max_age_days")
    stale = False
    check_time = as_of or datetime.now(timezone.utc)
    if observed_at is not None and isinstance(max_age_days, int):
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
        if not isinstance(provenance.get("evidence_refs"), list):
            reasons.append("invalid provenance.evidence_refs")

    for field in ("unknowns", "conflicts"):
        if not isinstance(normalized.get(field), list):
            reasons.append(f"invalid {field}")
    payload = normalized.get("payload")
    if not isinstance(payload, dict):
        reasons.append("invalid payload")
        payload = {}

    required_key = "required_payload" if native else "legacy_required_payload"
    required_payload = direction_contract.get(required_key) or direction_contract.get("required_payload") or []
    for field in required_payload:
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
    enum_contract = direction_contract.get("enum_payload") if native else direction_contract.get("legacy_enum_payload", direction_contract.get("enum_payload"))
    for field, allowed in (enum_contract or {}).items():
        if field in payload and payload.get(field) not in allowed:
            reasons.append(f"invalid payload.{field}")
    forbidden_reasons = recursive_forbidden(payload, set(direction_contract.get("forbidden_payload_keys") or []))
    if direction == "nomia_to_mago":
        forbidden_reasons = [reason.replace("outside producer authority", "outside nomia authority") for reason in forbidden_reasons]
    reasons.extend(forbidden_reasons)

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
    if direction == "mago_to_nomia" and native:
        source_state = payload.get("planning_state")
        expected = (mapping.get("mago_planning_to_nomia") or {}).get(source_state)
        if payload.get("mapping_version") != mapping_version:
            reasons.append("invalid payload.mapping_version")
        if expected is None or payload.get("nomia_planning_state") != expected:
            reasons.append("invalid payload.nomia_planning_state projection")
    if direction == "magia_to_nomia" and native:
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
    blocking = [
        reason
        for reason in reasons
        if reason.startswith(("invalid", "missing"))
        or "outside producer authority" in reason
        or "outside nomia authority" in reason
        or "does not match" in reason
    ]
    readiness = payload.get("governance_readiness", payload.get("readiness"))
    if blocking:
        status = "rejected"
    elif "conflicting evidence" in reasons:
        status = "conflicting"
    elif stale:
        status = "stale"
    elif readiness in {"draft", "unknown", False}:
        status = "draft"
    else:
        status = "accepted"
    return {
        "status": status,
        "direction": direction,
        "schema_version": normalized.get("schema_version"),
        "compatibility": "native-v1" if native else "legacy-v0",
        "reasons": reasons,
        "warnings": warnings,
        "source_skill": normalized.get("source_skill"),
        "target_skill": normalized.get("target_skill"),
    }


def apply_state_projection(direction: str, payload: dict[str, Any], contract: dict[str, Any]) -> dict[str, Any]:
    result = json.loads(json.dumps(payload))
    mapping = contract.get("state_mapping") or {}
    version = mapping.get("version")
    if direction == "mago_to_nomia":
        source = result.get("planning_state")
        result["nomia_planning_state"] = (mapping.get("mago_planning_to_nomia") or {}).get(source)
        result["mapping_version"] = version
    elif direction == "magia_to_nomia":
        execution = result.get("execution_state")
        validation = result.get("validation_state")
        result["nomia_execution_state"] = (mapping.get("magia_execution_to_nomia") or {}).get(execution)
        result["nomia_validation_state"] = (mapping.get("magia_validation_to_nomia") or {}).get(validation)
        result["mapping_version"] = version
    return result


def build_envelope(
    *,
    direction: str,
    payload: dict[str, Any],
    source: str,
    authority: str,
    evidence_refs: list[str],
    observed_at: str,
    freshness_days: int,
    unknowns: list[str] | None = None,
    conflicts: list[str] | None = None,
    root: Path | None = None,
) -> dict[str, Any]:
    contract = load_contract(root)
    direction_contract = (contract.get("directions") or {}).get(direction)
    if not isinstance(direction_contract, dict):
        raise ValueError(f"unsupported direction: {direction}")
    role = package_role(root)
    if direction_contract.get("producer") != role:
        raise ValueError(f"{role} cannot produce {direction}; owner is {direction_contract.get('producer')}")
    mapped_payload = apply_state_projection(direction, payload, contract)
    envelope = {
        "schema_version": contract["schema_version"],
        "direction": direction,
        "source_skill": role,
        "source_version": package_version(root),
        "target_skill": direction_contract["consumer"],
        "observed_at": observed_at,
        "provenance": {
            "source": source,
            "authority": authority,
            "evidence_refs": list(evidence_refs),
        },
        "freshness": {"max_age_days": freshness_days},
        "payload": mapped_payload,
        "unknowns": list(unknowns or []),
        "conflicts": list(conflicts or []),
    }
    canonical = json.dumps(envelope, sort_keys=True, separators=(",", ":")).encode("utf-8")
    envelope["handoff_id"] = "handoff-" + hashlib.sha256(canonical).hexdigest()[:16]
    result = validate_envelope(envelope, role=role, operation="produce", root=root)
    if result["status"] not in {"accepted", "draft"}:
        raise ValueError("cannot build invalid handoff: " + "; ".join(result["reasons"]))
    return envelope


def emit_json(data: dict[str, Any], output: str | None) -> None:
    text = json.dumps(data, indent=2, sort_keys=True) + "\n"
    if output:
        atomic_write_text(Path(output), text)
    print(text, end="")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build or validate a local ecosystem handoff envelope.")
    sub = parser.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build", help="Build a contract-v1 envelope owned by the current package.")
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

    validate = sub.add_parser("validate", help="Validate an incoming or outgoing envelope.")
    validate.add_argument("--input", required=True)
    validate.add_argument("--operation", choices=["any", "produce", "consume"], default="consume")
    validate.add_argument("--as-of", default=datetime.now(timezone.utc).replace(microsecond=0).isoformat())
    validate.add_argument("--allow-legacy", action="store_true")
    validate.add_argument("--json-output")

    contract = sub.add_parser("contract", help="Validate the local contract file.")
    contract.add_argument("--json-output")

    args = parser.parse_args(argv)
    root = root_for_script()
    try:
        if args.command == "build":
            payload = load_json_object(Path(args.payload), "payload")
            envelope = build_envelope(
                direction=args.direction,
                payload=payload,
                source=args.source,
                authority=args.authority,
                evidence_refs=args.evidence_ref,
                observed_at=args.observed_at,
                freshness_days=args.freshness_days,
                unknowns=args.unknown,
                conflicts=args.conflict,
                root=root,
            )
            emit_json(envelope, args.output)
            return 0
        if args.command == "validate":
            envelope = load_json_object(Path(args.input), "handoff envelope")
            as_of = parse_time(args.as_of)
            if as_of is None:
                raise ValueError("--as-of must be ISO-8601")
            result = validate_envelope(
                envelope,
                as_of=as_of,
                role=package_role(root),
                operation=args.operation,
                allow_legacy=args.allow_legacy,
                root=root,
            )
            emit_json(result, args.json_output)
            return 0 if result["status"] in {"accepted", "draft"} else 1
        errors = contract_errors(load_contract(root))
        result = {"status": "pass" if not errors else "fail", "errors": errors, "role": package_role(root)}
        emit_json(result, args.json_output)
        return 0 if not errors else 1
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, indent=2, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
