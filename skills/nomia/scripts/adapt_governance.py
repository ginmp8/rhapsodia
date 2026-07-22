#!/usr/bin/env python3
"""Adapt read-only legacy nomia governance facts into a canonical schema-version-2 ops record."""

from __future__ import annotations

import argparse
import copy
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml  # type: ignore

from governance_contract import GOVERNANCE_STATES, LIFECYCLE_VALUES, PROFILE_VALUES
from nomia_utils import atomic_write_text, is_legacy_spec_id, load_yaml_mapping, validate_spec_id_format
from validate_ops import validate
from write_ops_scaffold import render

# Only governance-owned fields may be extracted. Technical state and release truth
# must arrive through current attributed evidence, never through legacy inference.
COPYABLE_SECTIONS = {
    "request",
    "ownership",
    "planning",
    "business_priority",
    "blockers",
    "risks",
    "risk_history",
    "replanning",
    "tags",
    "repos",
    "links",
    "timestamps",
}


def iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def deep_merge_known(target: dict[str, Any], source: dict[str, Any]) -> None:
    """Merge source keys only where the canonical scaffold already defines them."""
    for key, value in source.items():
        if key not in target:
            continue
        if isinstance(target[key], dict) and isinstance(value, dict):
            deep_merge_known(target[key], value)
        else:
            target[key] = copy.deepcopy(value)


def adapt(
    legacy: dict[str, Any],
    *,
    source_path: str,
    observed_at: str,
    spec_id: str,
    spec_id_provenance: str,
    profile: str,
    lifecycle: str,
    governance_status: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    if validate_spec_id_format(spec_id):
        raise ValueError("spec_id must use spec-YYYY-MM-DD-feature-key")
    if is_legacy_spec_id(spec_id):
        raise ValueError("legacy ULID spec_id cannot be used as canonical identity")

    canonical = yaml.safe_load(
        render(spec_id, spec_id_provenance, profile, lifecycle, governance_status)
    )
    assert isinstance(canonical, dict)

    copied: list[str] = []
    ignored: list[str] = []
    legacy = copy.deepcopy(legacy)
    if "priority" in legacy:
        raise ValueError("generic priority is unsupported; the Nomia source owner must provide business_priority explicitly")
    for section, value in legacy.items():
        if section in COPYABLE_SECTIONS and section in canonical:
            if isinstance(canonical[section], dict) and isinstance(value, dict):
                deep_merge_known(canonical[section], value)
            elif isinstance(canonical[section], list) and isinstance(value, list):
                canonical[section] = copy.deepcopy(value)
            copied.append(section)
        elif section not in {"schema_version", "spec_id", "spec_id_provenance", "status"}:
            ignored.append(section)

    legacy_status = legacy.get("status") if isinstance(legacy.get("status"), dict) else {}
    for key in ("summary", "updated_at", "confidence", "evidence_summary", "manual", "inferred"):
        if key in legacy_status and key in canonical["status"]:
            canonical["status"][key] = copy.deepcopy(legacy_status[key])
    canonical["status"]["state"] = governance_status

    canonical["provenance"] = {
        "updated_at": observed_at,
        "facts": {
            "legacy_source": source_path,
            "legacy_schema_version": legacy.get("schema_version", "unknown"),
            "legacy_spec_id": legacy.get("spec_id"),
            "canonical_spec_id": spec_id,
            "canonical_spec_id_provenance": spec_id_provenance,
        },
        "changes": [
            {
                "field": "schema_version",
                "from": legacy.get("schema_version", "unknown"),
                "to": 2,
                "actor": "governance-adapt",
                "changed_at": observed_at,
                "source": source_path,
                "rationale": "canonicalize governance facts without carrying legacy identity or technical authority",
                "affected_commitments": [],
            },
            {
                "field": "spec_id",
                "from": legacy.get("spec_id"),
                "to": spec_id,
                "actor": "governance-adapt",
                "changed_at": observed_at,
                "source": spec_id_provenance,
                "rationale": "use externally supplied current identity; legacy identity remains evidence only",
                "affected_commitments": [],
            },
        ],
    }

    report = {
        "status": "adapted",
        "source": source_path,
        "observed_at": observed_at,
        "legacy_spec_id": legacy.get("spec_id"),
        "canonical_spec_id": spec_id,
        "copied_sections": sorted(copied),
        "ignored_sections": sorted(ignored),
        "technical_state_policy": "unknown-until-current-attributed-evidence",
        "release_state_policy": "unknown-until-current-release-evidence",
    }
    return canonical, report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Adapt a read-only legacy nomia ops record into canonical schema_version 2."
    )
    parser.add_argument("legacy_path", help="Read-only legacy YAML input.")
    parser.add_argument("output_path", help="Destination for the canonical YAML output.")
    parser.add_argument("--spec-id", required=True, help="Externally supplied canonical spec id.")
    parser.add_argument("--spec-id-provenance", required=True, help="Evidence reference for the canonical spec id.")
    parser.add_argument("--profile", required=True, choices=sorted(PROFILE_VALUES - {"unknown"}))
    parser.add_argument("--lifecycle", required=True, choices=sorted(LIFECYCLE_VALUES - {"unknown"}))
    parser.add_argument("--governance-status", required=True, choices=sorted(GOVERNANCE_STATES - {"unknown"}))
    parser.add_argument("--observed-at", default=iso_now(), help="ISO-8601 adaptation evidence timestamp.")
    parser.add_argument("--report", help="Optional JSON adaptation report path.")
    parser.add_argument("--force", action="store_true", help="Overwrite output if it exists.")
    parser.add_argument("--dry-run", action="store_true", help="Validate the adapted record without committing the destination.")
    args = parser.parse_args(argv)

    source = Path(args.legacy_path).resolve()
    output = Path(args.output_path).resolve()
    if source == output:
        print("ERROR: legacy input is read-only; output must use a different path")
        return 1
    if output.exists() and not args.force:
        print(f"ERROR: destination already exists: {output}")
        return 1

    try:
        legacy = load_yaml_mapping(source)
        canonical, report = adapt(
            legacy,
            source_path=str(source),
            observed_at=args.observed_at,
            spec_id=args.spec_id,
            spec_id_provenance=args.spec_id_provenance,
            profile=args.profile,
            lifecycle=args.lifecycle,
            governance_status=args.governance_status,
        )
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 1

    output.parent.mkdir(parents=True, exist_ok=True)
    rendered = yaml.safe_dump(canonical, sort_keys=False, allow_unicode=True)
    fd, temporary_name = tempfile.mkstemp(prefix=f".{output.name}.", suffix=".tmp", dir=output.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            stream.write(rendered)
            stream.flush()
            os.fsync(stream.fileno())
        errors, warnings = validate(temporary, require_canonical=True)
        if errors:
            print("ERROR: adapted output failed canonical validation")
            for error in errors:
                print(f"- {error}")
            return 1
        if not args.dry_run:
            os.replace(temporary, output)
    finally:
        temporary.unlink(missing_ok=True)

    report["validation"] = {"status": "pass", "warnings": warnings}
    report["committed"] = not args.dry_run
    if args.report:
        report_path = Path(args.report).resolve()
        report_path.parent.mkdir(parents=True, exist_ok=True)
        atomic_write_text(report_path, json.dumps(report, indent=2, sort_keys=True) + "\n")

    action = "validated dry-run" if args.dry_run else "adapted"
    print(f"OK: {action} {source} -> {output}")
    for warning in warnings:
        print(f"WARNING: {warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
