#!/usr/bin/env python3
"""Validate semantic quality fields for governed Mago planning packages.

This deterministic gate checks explicit evidence, failure/recovery behavior,
acceptance-path diversity, design alternatives, and reproducible validation
procedures. It does not judge product desirability or prove runtime outcomes.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

HEADING_RE = re.compile(r"^###\s+((?:REQ|NFR|AC|DECISION|OPTION|VAL)-\d{3})\s+-\s+(.+?)\s*$")
FIELD_RE = re.compile(r"^-\s+([^:]+):\s*(.*?)\s*$")
REF_RE = re.compile(r"\b(?:REQ|NFR|AC|DECISION|OPTION|VAL)-\d{3}\b")
NORMATIVE_RE = re.compile(r"\b(?:MUST|MUST NOT|SHALL|SHALL NOT|SHOULD|SHOULD NOT|MAY)\b")
VALID_PATHS = {"normal", "boundary", "error", "abuse", "recovery", "operational"}
VALID_CRITICALITY = {"low", "medium", "high", "critical"}
VAGUE_RE = re.compile(r"(?i)\b(?:works correctly|as expected|test everything|verify it works|appropriate tests)\b")


class QualityError(RuntimeError):
    pass


def read(path: Path) -> str:
    if not path.is_file() or path.is_symlink():
        raise QualityError(f"required regular file is missing: {path}")
    return path.read_text(encoding="utf-8-sig")


def section(text: str, heading: str) -> str:
    lines = text.splitlines()
    try:
        start = next(index for index, line in enumerate(lines) if line.strip() == heading)
    except StopIteration:
        return ""
    level = len(heading) - len(heading.lstrip("#"))
    collected: list[str] = []
    for line in lines[start + 1 :]:
        stripped = line.lstrip()
        if stripped.startswith("#"):
            current_level = len(stripped) - len(stripped.lstrip("#"))
            if current_level <= level:
                break
        collected.append(line)
    return "\n".join(collected).strip()


def records(text: str, prefix: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    current_id: str | None = None
    current_title = ""
    current_lines: list[str] = []

    def flush() -> None:
        nonlocal current_id, current_title, current_lines
        if current_id is None:
            return
        fields: dict[str, str] = {}
        for line in current_lines:
            match = FIELD_RE.match(line.strip())
            if match:
                fields[match.group(1).strip()] = match.group(2).strip()
        result[current_id] = {
            "title": current_title,
            "body": "\n".join(current_lines).strip(),
            "fields": fields,
        }
        current_id = None
        current_title = ""
        current_lines = []

    for line in text.splitlines():
        match = HEADING_RE.match(line.strip())
        if match:
            flush()
            record_id = match.group(1)
            if record_id.startswith(prefix + "-"):
                current_id = record_id
                current_title = match.group(2).strip()
        elif current_id is not None:
            current_lines.append(line)
    flush()
    return result


def references(value: str, prefix: str) -> set[str]:
    return {item for item in REF_RE.findall(value or "") if item.startswith(prefix + "-")}


def require_fields(path: Path, items: dict[str, dict[str, Any]], names: tuple[str, ...], errors: list[str]) -> None:
    for item_id, item in items.items():
        for name in names:
            value = item["fields"].get(name, "").strip()
            if not value:
                errors.append(f"{path}: `{item_id}` missing quality field `{name}`")
            elif VAGUE_RE.search(value):
                errors.append(f"{path}: `{item_id}` field `{name}` is not observable/reproducible: {value!r}")


def validate_prd(path: Path, errors: list[str], *, require_v2: bool = False, security_triggered: bool = False) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    text = read(path)
    requirements = records(text, "REQ")
    nfrs = records(text, "NFR")
    acceptance = records(text, "AC")
    if not requirements:
        errors.append(f"{path}: governed quality gate requires at least one REQ record")
    if not acceptance:
        errors.append(f"{path}: governed quality gate requires at least one AC record")
    require_fields(path, requirements, ("Evidence basis", "Failure/recovery behavior", "Verification"), errors)
    if require_v2:
        require_fields(path, requirements, ("Criticality", "Criticality basis"), errors)
        if not re.search(r"(?m)^quality_contract:\s*2\s*$", text):
            errors.append(f"{path}: governed quality v2 requires frontmatter `quality_contract: 2`")
    require_fields(path, acceptance, ("Requirements", "Path"), errors)

    for req_id, req in requirements.items():
        if not NORMATIVE_RE.search(req["body"]):
            errors.append(f"{path}: `{req_id}` must contain a normative obligation")
        selected = references(req["fields"].get("Verification", ""), "AC")
        if not selected:
            errors.append(f"{path}: `{req_id}` Verification must reference AC ids")
        for ac_id in selected:
            if ac_id not in acceptance:
                errors.append(f"{path}: `{req_id}` references unknown acceptance `{ac_id}`")

    paths: set[str] = set()
    paths_by_requirement: dict[str, set[str]] = {req_id: set() for req_id in requirements}
    for ac_id, ac in acceptance.items():
        selected_requirements = references(ac["fields"].get("Requirements", ""), "REQ")
        if not selected_requirements:
            errors.append(f"{path}: `{ac_id}` must reference at least one REQ")
        for req_id in selected_requirements:
            if req_id not in requirements:
                errors.append(f"{path}: `{ac_id}` references unknown requirement `{req_id}`")
        path_kind = ac["fields"].get("Path", "").lower()
        if path_kind not in VALID_PATHS:
            errors.append(f"{path}: `{ac_id}` Path must be one of {sorted(VALID_PATHS)}")
        else:
            paths.add(path_kind)
            for req_id in selected_requirements:
                if req_id in paths_by_requirement:
                    paths_by_requirement[req_id].add(path_kind)
        if "Scenario:" not in ac["body"] or "Given " not in ac["body"] or "When " not in ac["body"] or "Then " not in ac["body"]:
            errors.append(f"{path}: `{ac_id}` requires a complete observable Gherkin scenario")

    if "normal" not in paths:
        errors.append(f"{path}: governed acceptance must include a normal path")
    if not paths.intersection({"boundary", "error", "recovery", "abuse"}):
        errors.append(f"{path}: governed acceptance must include a boundary, error, recovery, or abuse path")

    if require_v2:
        for req_id, req in requirements.items():
            criticality = req["fields"].get("Criticality", "").strip().lower()
            if criticality not in VALID_CRITICALITY:
                errors.append(f"{path}: `{req_id}` Criticality must be one of {sorted(VALID_CRITICALITY)}")
                continue
            req_paths = paths_by_requirement.get(req_id, set())
            if "normal" not in req_paths:
                errors.append(f"{path}: `{req_id}` requires a linked normal acceptance path")
            if criticality in {"medium", "high", "critical"} and not req_paths.intersection({"boundary", "error", "recovery", "abuse", "operational"}):
                errors.append(f"{path}: `{req_id}` {criticality} criticality requires a linked non-happy acceptance path")
            if criticality in {"high", "critical"} and "recovery" not in req_paths:
                errors.append(f"{path}: `{req_id}` {criticality} criticality requires a linked recovery acceptance path")
            if criticality == "critical" and "error" not in req_paths:
                errors.append(f"{path}: `{req_id}` critical criticality requires a linked error acceptance path")
            if criticality == "critical" and security_triggered and "abuse" not in req_paths:
                errors.append(f"{path}: `{req_id}` critical security requirement requires a linked abuse acceptance path")

    nfr_section = section(text, "## Non-Functional Requirements")
    if not nfrs and "Not applicable:" not in nfr_section:
        errors.append(f"{path}: governed PRD requires measurable NFR records or an evidence-backed Not applicable rationale")
    require_fields(path, nfrs, ("Metric", "Threshold", "Validation"), errors)
    for nfr_id, nfr in nfrs.items():
        if not references(nfr["fields"].get("Validation", ""), "VAL"):
            errors.append(f"{path}: `{nfr_id}` Validation must reference VAL ids")
    return requirements, nfrs, acceptance


def validate_design(path: Path, errors: list[str], *, require_v2: bool = False) -> tuple[dict[str, Any], dict[str, Any]]:
    text = read(path)
    decisions = records(text, "DECISION")
    options = records(text, "OPTION")
    if not decisions:
        errors.append(f"{path}: governed quality gate requires at least one DECISION record")
    if len(options) < 2:
        errors.append(f"{path}: governed design requires at least two explicit OPTION records")
    require_fields(path, options, ("Benefits", "Costs", "Failure modes", "Operational impact"), errors)
    require_fields(path, decisions, ("Requirements", "Selected option", "Rationale", "Consequences"), errors)
    if require_v2:
        require_fields(path, decisions, ("Rollback or reversibility",), errors)
    for decision_id, decision in decisions.items():
        selected = references(decision["fields"].get("Selected option", ""), "OPTION")
        if len(selected) != 1:
            errors.append(f"{path}: `{decision_id}` must select exactly one OPTION id")
        for option_id in selected:
            if option_id not in options:
                errors.append(f"{path}: `{decision_id}` selects unknown option `{option_id}`")
    return decisions, options


def validate_validation(
    path: Path,
    requirements: dict[str, Any],
    acceptance: dict[str, Any],
    nfrs: dict[str, Any],
    errors: list[str],
    *,
    require_v2: bool = False,
) -> dict[str, Any]:
    text = read(path)
    validations = records(text, "VAL")
    if not validations:
        errors.append(f"{path}: governed quality gate requires at least one VAL record")
    required_validation_fields = [
        "Requirements", "Acceptance", "Tasks", "Environment",
        "Command or procedure", "Expected", "Failure disposition",
    ]
    if require_v2:
        required_validation_fields.extend(["Evidence capture", "Residual risk disposition"])
    require_fields(path, validations, tuple(required_validation_fields), errors)
    for val_id, validation in validations.items():
        for prefix, field, targets in (
            ("REQ", "Requirements", requirements),
            ("AC", "Acceptance", acceptance),
        ):
            selected = references(validation["fields"].get(field, ""), prefix)
            if not selected:
                errors.append(f"{path}: `{val_id}` field `{field}` must reference {prefix} ids")
            for selected_id in selected:
                if selected_id not in targets:
                    errors.append(f"{path}: `{val_id}` references unknown `{selected_id}`")
        if not re.search(r"\btask\d{3}\b", validation["fields"].get("Tasks", "")):
            errors.append(f"{path}: `{val_id}` Tasks must reference taskNNN ids")

    for nfr_id, nfr in nfrs.items():
        for val_id in references(nfr["fields"].get("Validation", ""), "VAL"):
            if val_id not in validations:
                errors.append(f"{path}: `{nfr_id}` references unknown validation `{val_id}`")
    if require_v2:
        covered_acceptance: set[str] = set()
        for validation in validations.values():
            covered_acceptance.update(references(validation["fields"].get("Acceptance", ""), "AC"))
        missing_acceptance = sorted(set(acceptance) - covered_acceptance)
        if missing_acceptance:
            errors.append(f"{path}: quality v2 requires validation coverage for every AC; missing {missing_acceptance}")
    return validations


def validate_package(package: Path, *, require_v2: bool = False) -> list[str]:
    errors: list[str] = []
    if not package.is_dir() or package.is_symlink():
        return [f"{package}: package must be a non-symlink directory"]
    try:
        security_triggered = (package / "security-and-risk-considerations.md").is_file()
        requirements, nfrs, acceptance = validate_prd(
            package / "prd.md", errors, require_v2=require_v2, security_triggered=security_triggered
        )
        validate_design(package / "technical-design.md", errors, require_v2=require_v2)
        validate_validation(
            package / "validation.md", requirements, acceptance, nfrs, errors, require_v2=require_v2
        )
    except QualityError as exc:
        errors.append(str(exc))
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate governed Mago plan quality fields.")
    parser.add_argument("package")
    parser.add_argument("--require-v2", action="store_true", help="Require criticality-calibrated governed quality contract v2.")
    args = parser.parse_args(argv)
    package = Path(args.package).resolve()
    errors = validate_package(package, require_v2=args.require_v2)
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"FAILED: {len(errors)} quality error(s)")
        return 1
    print(f"OK: governed plan quality contract {'v2' if args.require_v2 else 'v1-compatible'} passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
