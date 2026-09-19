#!/usr/bin/env python3
"""Derive and validate privacy metadata; verify supplied source-handoff lineage evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None

ROOT = Path(__file__).resolve().parents[1]
HID = re.compile(r"^handoff-[0-9a-f]{16}$")
LABELS = {
    "classification": "Classification",
    "contains_personal_data": "Contains Personal Data",
    "contains_third_party_data": "Contains Third-Party Data",
    "contains_confidential_data": "Contains Confidential Data",
    "contains_secrets": "Contains Secrets",
    "redactions_applied": "Redactions Applied",
    "redaction_method": "Redaction Method",
    "intended_audience": "Intended Audience",
    "allowed_destinations": "Allowed Destinations",
    "purpose": "Purpose",
    "retention_days": "Retention Days",
    "external_share_allowed": "External Share Allowed",
    "source_handoff_id": "Source Handoff ID",
    "source_reference": "Source Reference",
    "transformations": "Transformations",
}
INHERITED_KEYS = (
    "classification",
    "contains_personal_data",
    "contains_third_party_data",
    "contains_confidential_data",
    "contains_secrets",
    "redactions_applied",
    "redaction_method",
    "intended_audience",
    "allowed_destinations",
    "purpose",
    "retention_days",
    "external_share_allowed",
)


def contract(root: Path = ROOT) -> dict[str, Any]:
    return json.loads((root / "references/artifact-privacy-contract.json").read_text(encoding="utf-8"))


def handoff_id_for(envelope: dict[str, Any]) -> str:
    data = {key: value for key, value in envelope.items() if key != "handoff_id"}
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":")).encode()
    return "handoff-" + hashlib.sha256(canonical).hexdigest()[:16]


def derive(env: dict[str, Any]) -> dict[str, Any]:
    privacy = env.get("privacy_handling") or {}
    handoff_id = env.get("handoff_id")
    out = {key: privacy.get(key) for key in INHERITED_KEYS}
    out.update(
        source_handoff_id=handoff_id,
        source_reference=f"handoff:{handoff_id}" if handoff_id else str((env.get("provenance") or {}).get("source") or "unknown"),
        transformations=["inherited-from-handoff"],
    )
    return out


def validate_block(value: Any, root: Path = ROOT) -> list[str]:
    policy = contract(root)
    errors: list[str] = []
    if not isinstance(value, dict):
        return ["privacy metadata must be a mapping"]

    required = set(policy["required_fields"])
    errors += [f"missing privacy.{key}" for key in sorted(required - set(value))]
    errors += [f"unknown privacy.{key}" for key in sorted(set(value) - required)]

    if value.get("classification") not in policy["classification"]:
        errors.append("invalid privacy.classification")
    if value.get("redaction_method") not in policy["redaction_method"]:
        errors.append("invalid privacy.redaction_method")

    for key in (
        "contains_personal_data",
        "contains_third_party_data",
        "contains_confidential_data",
        "contains_secrets",
        "external_share_allowed",
    ):
        if not isinstance(value.get(key), bool):
            errors.append(f"invalid privacy.{key}")

    for key in ("redactions_applied", "intended_audience", "allowed_destinations", "transformations"):
        item = value.get(key)
        if not isinstance(item, list) or any(not isinstance(entry, str) or not entry.strip() for entry in item or []):
            errors.append(f"invalid privacy.{key}")

    destinations = value.get("allowed_destinations")
    if isinstance(destinations, list) and set(destinations) - set(policy["allowed_destinations"]):
        errors.append("invalid privacy.allowed_destinations")

    retention = value.get("retention_days")
    if isinstance(retention, bool) or not isinstance(retention, int) or not 0 <= retention <= policy["max_retention_days"]:
        errors.append(
            f"invalid privacy.retention_days; durable artifacts are capped at {policy['max_retention_days']} days"
        )

    if not isinstance(value.get("purpose"), str) or not value["purpose"].strip():
        errors.append("invalid privacy.purpose")

    handoff_id = value.get("source_handoff_id")
    source_reference = str(value.get("source_reference") or "").strip()
    if handoff_id not in (None, ""):
        if HID.fullmatch(str(handoff_id)) is None:
            errors.append("invalid privacy.source_handoff_id")
        expected_reference = f"handoff:{handoff_id}"
        if source_reference != expected_reference:
            errors.append("privacy.source_reference must match source_handoff_id")
    elif not source_reference:
        errors.append("privacy lineage requires source_handoff_id or source_reference")

    if value.get("contains_secrets") is True:
        errors.append("privacy secrets must be removed")

    sensitive = any(
        value.get(key) is True
        for key in ("contains_personal_data", "contains_third_party_data", "contains_confidential_data")
    )
    if sensitive and (not value.get("redactions_applied") or value.get("redaction_method") == "none"):
        errors.append("privacy sensitive content requires redaction")

    destination_set = set(destinations or [])
    if destination_set & {"approved-vendor", "public"} and value.get("external_share_allowed") is not True:
        errors.append("privacy external destination denied")
    if "public" in destination_set and (value.get("classification") != "public" or sensitive):
        errors.append("privacy public projection denied")

    return list(dict.fromkeys(errors))


def verify_source_handoff(value: Any, envelope: Any) -> list[str]:
    """Verify declared lineage against a supplied source handoff without requiring a global handoff store."""
    if not isinstance(value, dict):
        return ["privacy metadata must be a mapping"]
    if not isinstance(envelope, dict):
        return ["source handoff must be a JSON object"]

    errors: list[str] = []
    declared_id = value.get("source_handoff_id")
    actual_id = envelope.get("handoff_id")
    if declared_id in (None, ""):
        return ["verified handoff lineage requires privacy.source_handoff_id"]
    if actual_id != declared_id:
        errors.append("privacy source handoff id does not match supplied source")
    if HID.fullmatch(str(actual_id or "")) is None or actual_id != handoff_id_for(envelope):
        errors.append("privacy source handoff integrity check failed")
    if value.get("source_reference") != f"handoff:{declared_id}":
        errors.append("privacy source reference does not resolve to declared handoff id")

    source_privacy = envelope.get("privacy_handling")
    if not isinstance(source_privacy, dict):
        errors.append("source handoff is missing privacy_handling")
        return list(dict.fromkeys(errors))

    artifact_retention = value.get("retention_days")
    source_retention = source_privacy.get("retention_days")
    if (
        isinstance(artifact_retention, int)
        and not isinstance(artifact_retention, bool)
        and isinstance(source_retention, int)
        and not isinstance(source_retention, bool)
        and artifact_retention > source_retention
    ):
        errors.append("privacy retention may not exceed verified source handoff retention")

    if value.get("transformations") == ["inherited-from-handoff"]:
        for key in INHERITED_KEYS:
            if value.get(key) != source_privacy.get(key):
                errors.append(f"privacy.{key} does not match exact inherited source metadata")

    return list(dict.fromkeys(errors))


def parse_md(text: str) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, label in LABELS.items():
        match = re.search(rf"^- {re.escape(label)}:\s*(.+?)\s*$", text, re.M)
        if not match:
            continue
        raw = match.group(1).strip().strip("`")
        if raw.lower() in {"true", "false"}:
            out[key] = raw.lower() == "true"
        elif key == "retention_days" and raw.isdigit():
            out[key] = int(raw)
        elif key in {"redactions_applied", "intended_audience", "allowed_destinations", "transformations"}:
            out[key] = [item.strip() for item in raw.strip("[]").split(",") if item.strip()]
        else:
            out[key] = None if key == "source_handoff_id" and raw.lower() in {"null", "none"} else raw
    return out


def template_errors(text: str) -> list[str]:
    errors = [] if "## Privacy and Sharing" in text else ["missing Privacy and Sharing heading"]
    errors += [
        f"missing privacy template field {label}"
        for label in LABELS.values()
        if not re.search(rf"^- {re.escape(label)}:\s*.+$", text, re.M)
    ]
    return errors


markdown_template_errors = template_errors


def load_artifact(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()
    if suffix == ".json":
        data = json.loads(text)
        return data.get("privacy", data)
    if suffix in {".yaml", ".yml"}:
        if yaml is None:
            raise RuntimeError("PyYAML is required")
        data = yaml.safe_load(text)
        return data.get("privacy") if isinstance(data, dict) else None
    return parse_md(text)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path")
    parser.add_argument("--template", action="store_true")
    parser.add_argument("--derive-handoff", action="store_true")
    parser.add_argument("--source-handoff")
    parser.add_argument("--output")
    args = parser.parse_args(argv)
    path = Path(args.path).resolve()

    source_envelope: dict[str, Any] | None = None
    if args.derive_handoff:
        source_envelope = json.loads(path.read_text(encoding="utf-8"))
        value = derive(source_envelope)
        errors = validate_block(value)
        errors += verify_source_handoff(value, source_envelope)
        if not errors and args.output:
            Path(args.output).write_text(json.dumps({"privacy": value}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    elif args.template and path.suffix.lower() == ".md":
        value = None
        errors = template_errors(path.read_text(encoding="utf-8"))
    elif args.template:
        value = None
        if yaml is None:
            raise SystemExit("PyYAML is required")
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        block = data.get("privacy") if isinstance(data, dict) else None
        errors = [] if isinstance(block, dict) and set(contract()["required_fields"]) <= set(block) else ["template privacy block is incomplete"]
    else:
        value = load_artifact(path)
        errors = validate_block(value)
        if args.source_handoff:
            source_envelope = json.loads(Path(args.source_handoff).read_text(encoding="utf-8"))
            errors += verify_source_handoff(value, source_envelope)

    errors = list(dict.fromkeys(errors))
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        return 1

    if isinstance(value, dict) and value.get("source_handoff_id") and source_envelope is None:
        print(f"OK: artifact privacy structure validated; source handoff authenticity not verified: {path}")
    else:
        print(f"OK: artifact privacy validated: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
