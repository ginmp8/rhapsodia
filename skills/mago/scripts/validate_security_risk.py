#!/usr/bin/env python3
"""Validate Mago security/risk planning.

Contract v1 remains accepted for legacy packages. Contract v2 adds deterministic
relational checks across assets, trust boundaries, threats, abuse cases,
controls, residual risks, validation expectations, and review authority.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

LEGACY_REQUIRED_HEADINGS = (
    "## Scope",
    "## Data Classification and Assets",
    "## Threat Actors and Trust Boundaries",
    "## Misuse and Abuse Cases",
    "## Planned Controls",
    "## Risks and Residual Risk",
    "## Validation Expectations for Magia",
    "## Required Review",
)
LEGACY_REQUIRED_TERMS = (
    "Control owner:",
    "Control validation:",
    "Residual risk:",
    "Risk authority:",
    "Security reviewer:",
    "Compliance reviewer:",
)
V2_SECTIONS: dict[str, tuple[str, tuple[str, ...]]] = {
    "## Assets and Data Classification": (
        "ASSET",
        ("Classification", "Sensitive data or secrets", "Retention and logging constraints"),
    ),
    "## Trust Boundaries": (
        "BOUNDARY",
        ("Source", "Destination", "Authentication", "Authorization"),
    ),
    "## Threats": (
        "THREAT",
        ("Assets", "Trust boundaries", "Threat actor", "Likelihood", "Impact", "Security domains"),
    ),
    "## Misuse and Abuse Cases": (
        "ABUSE",
        ("Threats", "Observable misuse", "Expected prevention or detection"),
    ),
    "## Planned Controls": (
        "CONTROL",
        ("Threats", "Abuse cases", "Owner", "Validation", "Failure behavior"),
    ),
    "## Risks and Residual Risk": (
        "RISK",
        (
            "Threats",
            "Controls",
            "Residual likelihood",
            "Residual impact",
            "Risk authority",
            "Status",
            "Acceptance evidence",
        ),
    ),
    "## Validation Expectations for Magia": (
        "SECVAL",
        ("Controls", "Threats", "Test type", "Expected evidence", "Sensitive logging check"),
    ),
}
V2_REQUIRED_HEADINGS = ("## Scope", *V2_SECTIONS.keys(), "## Required Review")
V2_REQUIRED_REVIEW_FIELDS = (
    "Security reviewer",
    "Compliance reviewer",
    "Review evidence required before handoff closure",
)
TOKEN_RE = re.compile(r"<[A-Za-z0-9_|. -]+>")
UNRESOLVED_RE = re.compile(r"(?im)^(?:-\s+[^:]+:\s*|\s*)(?:`?unknown`?|TBD|TO[D]O|not assessed|replace with actua" r"l)\s*$")
RECORD_RE = re.compile(r"^###\s+([A-Z]+-\d{3})\s+-\s+(.+?)\s*$")
FIELD_RE = re.compile(r"^-\s+([^:]+):\s*(.*?)\s*$")
ID_RE = re.compile(r"\b(?:ASSET|BOUNDARY|THREAT|ABUSE|CONTROL|RISK|SECVAL)-\d{3}\b")
VALID_CLASSIFICATIONS = {"public", "internal", "confidential", "restricted"}
VALID_LEVELS = {"low", "medium", "high", "critical"}
VALID_FAILURE = {"fail_closed", "deny", "quarantine", "alert", "rate_limit", "isolate"}
VALID_RISK_STATUS = {"unresolved", "review_required", "accepted_by_authority", "mitigated"}


def section_content(text: str, heading: str) -> str:
    lines = text.splitlines()
    try:
        start = next(index for index, line in enumerate(lines) if line.strip() == heading)
    except StopIteration:
        return ""
    collected: list[str] = []
    for line in lines[start + 1 :]:
        if line.startswith("## "):
            break
        collected.append(line)
    return "\n".join(collected).strip()


def unresolved_errors(path: Path, text: str) -> list[str]:
    errors: list[str] = []
    tokens = sorted(set(TOKEN_RE.findall(text)))
    if tokens:
        errors.append(f"{path}: contains unresolved template token(s): {', '.join(tokens)}")
    unresolved = sorted(set(match.group(0) for match in UNRESOLVED_RE.finditer(text)))
    if unresolved:
        errors.append(f"{path}: contains unresolved value(s): {', '.join(unresolved)}")
    if "accepted by Mago" in text or "Mago accepts" in text:
        errors.append(f"{path}: Mago must not author business or residual-risk acceptance")
    return errors


def validate_legacy(path: Path, text: str) -> list[str]:
    errors: list[str] = []
    headings = {line.strip() for line in text.splitlines() if line.startswith("## ")}
    for heading in LEGACY_REQUIRED_HEADINGS:
        if heading not in headings:
            errors.append(f"{path}: missing heading `{heading}`")
        elif not section_content(text, heading):
            errors.append(f"{path}: section `{heading}` must contain explicit planning content")
    for term in LEGACY_REQUIRED_TERMS:
        if term not in text:
            errors.append(f"{path}: missing required field `{term}`")
    errors.extend(unresolved_errors(path, text))
    return errors


def parse_fields(lines: list[str]) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in lines:
        match = FIELD_RE.match(line.strip())
        if match:
            fields[match.group(1).strip()] = match.group(2).strip()
    return fields


def parse_records(path: Path, text: str, heading: str, prefix: str) -> tuple[dict[str, dict[str, Any]], list[str]]:
    content = section_content(text, heading)
    errors: list[str] = []
    records: dict[str, dict[str, Any]] = {}
    current_id: str | None = None
    current_title = ""
    current_lines: list[str] = []

    def flush() -> None:
        nonlocal current_id, current_title, current_lines
        if current_id is None:
            return
        if current_id in records:
            errors.append(f"{path}: duplicate security record id `{current_id}`")
        else:
            records[current_id] = {"title": current_title, "fields": parse_fields(current_lines)}
        current_id = None
        current_title = ""
        current_lines = []

    for line in content.splitlines():
        match = RECORD_RE.match(line.strip())
        if match:
            flush()
            record_id = match.group(1)
            if not record_id.startswith(prefix + "-"):
                errors.append(f"{path}: `{heading}` contains unexpected record id `{record_id}`")
            current_id = record_id
            current_title = match.group(2).strip()
        elif current_id is not None:
            current_lines.append(line)
        elif line.strip():
            errors.append(f"{path}: content before first {prefix} record in `{heading}`")
    flush()
    if not records:
        errors.append(f"{path}: `{heading}` requires at least one {prefix} record")
    return records, errors


def refs(value: str, prefix: str) -> set[str]:
    return {item for item in ID_RE.findall(value or "") if item.startswith(prefix + "-")}


def require_refs(
    path: Path,
    records: dict[str, dict[str, Any]],
    field: str,
    prefix: str,
    targets: dict[str, dict[str, Any]],
    errors: list[str],
) -> None:
    for record_id, record in records.items():
        selected = refs(record["fields"].get(field, ""), prefix)
        if not selected:
            errors.append(f"{path}: `{record_id}` field `{field}` must reference at least one {prefix} id")
        for reference in sorted(selected):
            if reference not in targets:
                errors.append(f"{path}: `{record_id}` references unknown `{reference}` in `{field}`")


def validate_v2(path: Path, text: str) -> list[str]:
    errors: list[str] = []
    headings = {line.strip() for line in text.splitlines() if line.startswith("## ")}
    for heading in V2_REQUIRED_HEADINGS:
        if heading not in headings:
            errors.append(f"{path}: missing v2 heading `{heading}`")
        elif not section_content(text, heading):
            errors.append(f"{path}: v2 section `{heading}` must contain explicit planning content")
    if errors:
        errors.extend(unresolved_errors(path, text))
        return errors

    all_records: dict[str, dict[str, Any]] = {}
    by_prefix: dict[str, dict[str, dict[str, Any]]] = {}
    for heading, (prefix, required_fields) in V2_SECTIONS.items():
        records, record_errors = parse_records(path, text, heading, prefix)
        errors.extend(record_errors)
        by_prefix[prefix] = records
        for record_id, record in records.items():
            if record_id in all_records:
                errors.append(f"{path}: duplicate id across security sections: `{record_id}`")
            all_records[record_id] = record
            for field in required_fields:
                value = record["fields"].get(field, "").strip()
                if not value:
                    errors.append(f"{path}: `{record_id}` missing required field `{field}`")

    review_fields = parse_fields(section_content(text, "## Required Review").splitlines())
    for field in V2_REQUIRED_REVIEW_FIELDS:
        if not review_fields.get(field, "").strip():
            errors.append(f"{path}: Required Review missing `{field}`")

    assets = by_prefix.get("ASSET", {})
    boundaries = by_prefix.get("BOUNDARY", {})
    threats = by_prefix.get("THREAT", {})
    abuses = by_prefix.get("ABUSE", {})
    controls = by_prefix.get("CONTROL", {})
    risks = by_prefix.get("RISK", {})
    validations = by_prefix.get("SECVAL", {})

    require_refs(path, threats, "Assets", "ASSET", assets, errors)
    require_refs(path, threats, "Trust boundaries", "BOUNDARY", boundaries, errors)
    require_refs(path, abuses, "Threats", "THREAT", threats, errors)
    require_refs(path, controls, "Threats", "THREAT", threats, errors)
    require_refs(path, controls, "Abuse cases", "ABUSE", abuses, errors)
    require_refs(path, controls, "Validation", "SECVAL", validations, errors)
    require_refs(path, risks, "Threats", "THREAT", threats, errors)
    require_refs(path, risks, "Controls", "CONTROL", controls, errors)
    require_refs(path, validations, "Controls", "CONTROL", controls, errors)
    require_refs(path, validations, "Threats", "THREAT", threats, errors)

    for asset_id, record in assets.items():
        classification = record["fields"].get("Classification", "").lower()
        if classification not in VALID_CLASSIFICATIONS:
            errors.append(f"{path}: `{asset_id}` Classification must be one of {sorted(VALID_CLASSIFICATIONS)}")

    for threat_id, record in threats.items():
        for field in ("Likelihood", "Impact"):
            value = record["fields"].get(field, "").lower()
            if value not in VALID_LEVELS:
                errors.append(f"{path}: `{threat_id}` {field} must be one of {sorted(VALID_LEVELS)}")

    for control_id, record in controls.items():
        failure = record["fields"].get("Failure behavior", "").lower()
        if failure not in VALID_FAILURE:
            errors.append(f"{path}: `{control_id}` Failure behavior must be one of {sorted(VALID_FAILURE)}")
        if record["fields"].get("Owner", "").lower() in {"mago", "none", "n/a"}:
            errors.append(f"{path}: `{control_id}` needs a downstream technical owner, not Mago/none")

    for risk_id, record in risks.items():
        for field in ("Residual likelihood", "Residual impact"):
            value = record["fields"].get(field, "").lower()
            if value not in VALID_LEVELS:
                errors.append(f"{path}: `{risk_id}` {field} must be one of {sorted(VALID_LEVELS)}")
        status = record["fields"].get("Status", "").lower()
        if status not in VALID_RISK_STATUS:
            errors.append(f"{path}: `{risk_id}` Status must be one of {sorted(VALID_RISK_STATUS)}")
        authority = record["fields"].get("Risk authority", "").lower()
        if authority in {"mago", "none", "n/a"}:
            errors.append(f"{path}: `{risk_id}` needs an external risk authority")
        evidence = record["fields"].get("Acceptance evidence", "").strip().lower()
        if status == "accepted_by_authority" and evidence in {"", "none", "n/a", "not required"}:
            errors.append(f"{path}: `{risk_id}` accepted risk requires concrete Acceptance evidence")

    control_threats = {control_id: refs(record["fields"].get("Threats", ""), "THREAT") for control_id, record in controls.items()}
    control_abuses = {control_id: refs(record["fields"].get("Abuse cases", ""), "ABUSE") for control_id, record in controls.items()}
    validation_controls = {val_id: refs(record["fields"].get("Controls", ""), "CONTROL") for val_id, record in validations.items()}
    validation_threats = {val_id: refs(record["fields"].get("Threats", ""), "THREAT") for val_id, record in validations.items()}

    for threat_id, threat in threats.items():
        linked_controls = [control_id for control_id, selected in control_threats.items() if threat_id in selected]
        if not linked_controls:
            errors.append(f"{path}: `{threat_id}` has no planned control")
            continue
        linked_validations = [
            val_id
            for val_id, selected_threats in validation_threats.items()
            if threat_id in selected_threats and validation_controls.get(val_id, set()).intersection(linked_controls)
        ]
        if not linked_validations:
            errors.append(f"{path}: `{threat_id}` has no validation linked through its controls")

        asset_ids = refs(threat["fields"].get("Assets", ""), "ASSET")
        restricted = any(assets[item]["fields"].get("Classification", "").lower() == "restricted" for item in asset_ids if item in assets)
        high_impact = threat["fields"].get("Impact", "").lower() in {"high", "critical"}
        if restricted or high_impact:
            protective = {
                controls[item]["fields"].get("Failure behavior", "").lower()
                for item in linked_controls
                if item in controls
            }
            if not protective.intersection({"fail_closed", "deny", "quarantine", "isolate"}):
                errors.append(f"{path}: `{threat_id}` affects restricted/high-impact scope but has no fail-closed protective control")

    for abuse_id in abuses:
        if not any(abuse_id in selected for selected in control_abuses.values()):
            errors.append(f"{path}: `{abuse_id}` has no planned control")

    for control_id, control in controls.items():
        selected_validations = refs(control["fields"].get("Validation", ""), "SECVAL")
        reverse = {val_id for val_id, selected in validation_controls.items() if control_id in selected}
        if selected_validations != reverse.intersection(selected_validations):
            missing_reverse = sorted(selected_validations - reverse)
            if missing_reverse:
                errors.append(f"{path}: `{control_id}` validation link is not reciprocal for {missing_reverse}")

    sensitive_threats: set[str] = set()
    for threat_id, threat in threats.items():
        for asset_id in refs(threat["fields"].get("Assets", ""), "ASSET"):
            classification = assets.get(asset_id, {}).get("fields", {}).get("Classification", "").lower()
            if classification in {"confidential", "restricted"}:
                sensitive_threats.add(threat_id)
    for validation_id, validation in validations.items():
        if refs(validation["fields"].get("Threats", ""), "THREAT").intersection(sensitive_threats):
            logging_check = validation["fields"].get("Sensitive logging check", "").strip().lower()
            if logging_check in {"", "none", "n/a", "not required"}:
                errors.append(f"{path}: `{validation_id}` covers sensitive data and requires a Sensitive logging check")

    errors.extend(unresolved_errors(path, text))
    return errors


def contract_version(text: str) -> int:
    match = re.search(r"(?im)^-\s*Contract version:\s*(\d+)\s*$", text)
    return int(match.group(1)) if match else 1


def validate(path: Path, require_v2: bool = False) -> list[str]:
    if not path.is_file():
        return [f"{path}: missing file"]
    if path.name != "security-and-risk-considerations.md":
        return [f"{path}: expected security-and-risk-considerations.md"]
    text = path.read_text(encoding="utf-8-sig")
    version = contract_version(text)
    if require_v2 and version < 2:
        return [f"{path}: security contract version 2 is required"]
    if version == 1:
        return validate_legacy(path, text)
    if version == 2:
        return validate_v2(path, text)
    return [f"{path}: unsupported security contract version {version}"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate MAGO security and risk planning artifacts.")
    parser.add_argument("paths", nargs="+")
    parser.add_argument("--require-v2", action="store_true")
    args = parser.parse_args(argv)
    errors: list[str] = []
    for raw in args.paths:
        errors.extend(validate(Path(raw).resolve(), require_v2=args.require_v2))
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"FAILED: {len(errors)} errors, 0 warnings")
        return 1
    print(f"OK: validated {len(args.paths)} security/risk artifact(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
