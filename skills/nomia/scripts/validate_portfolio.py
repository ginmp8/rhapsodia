#!/usr/bin/env python3
"""Validate nomia portfolio.yaml and portfolio.md artifacts."""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path
from typing import Any

from nomia_utils import (
    find_unresolved_template_tokens_in_text,
    has_unresolved_template_token,
    is_iso_date,
    is_missing,
    load_yaml_mapping,
    parse_iso_date,
    scan_unresolved_template_tokens,
    unique,
    validate_spec_id_format,
)

VALID_PRIORITY = {"unknown", "low", "medium", "high", "urgent"}
VALID_URGENCY = {"unknown", "low", "medium", "high", "immediate"}
VALID_IMPACT = {"unknown", "low", "medium", "high", "critical"}
VALID_RISK = {"unknown", "low", "medium", "high", "critical"}
VALID_STATE = {"unknown", "intake", "triage", "planned", "in_progress", "blocked", "at_risk", "done", "canceled"}
VALID_CONFIDENCE = {"unknown", "low", "medium", "high"}
TERMINAL_STATES = {"done", "canceled"}
REQUIRED_MD_HEADINGS = [
    "# Portfolio",
    "## Summary",
    "## Items",
    "## Blocked",
    "## Risks",
    "## Replans",
]
REQUIRED_YAML_KEYS = ["schema_version", "portfolio_id", "updated_at", "items", "blocked", "risks", "replans"]
FLAG_KEYS = ["blocked", "overdue", "replanned", "missing_owner", "at_risk", "multi_repo"]



def validate_enum(label: str, value: Any, valid_values: set[str], errors: list[str]) -> None:
    if value in (None, ""):
        return
    if has_unresolved_template_token(value):
        return
    if str(value) not in valid_values:
        errors.append(f"`{label}` must be one of {sorted(valid_values)}")


def item_key(item: dict[str, Any], index: int) -> str:
    for key in ("spec_id", "feature_key", "title"):
        value = item.get(key)
        if value not in (None, ""):
            return str(value)
    return f"items[{index}]"


def flag_values(flags: dict[str, Any], key: str) -> set[str]:
    value = flags.get(key)
    if not isinstance(value, list):
        return set()
    return {str(item) for item in value}


def validate_spec_id(label: str, value: Any, errors: list[str]) -> None:
    error = validate_spec_id_format(value)
    if error:
        errors.append(f"`{label}` {error}")


def validate_yaml(path: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if not path.exists():
        return [f"missing required file: {path}"], warnings

    try:
        data = load_yaml_mapping(path)
    except Exception as exc:
        return [f"{path}: {exc}"], warnings

    errors.extend(scan_unresolved_template_tokens(data))

    for key in REQUIRED_YAML_KEYS:
        if key not in data:
            errors.append(f"{path}: missing required key `{key}`")

    if data.get("schema_version") != 1:
        errors.append(f"{path}: `schema_version` must be 1")

    if not is_iso_date(data.get("updated_at")):
        errors.append(f"{path}: `updated_at` must use YYYY-MM-DD format")
    elif is_missing(data.get("updated_at")):
        warnings.append(f"{path}: `updated_at` is missing")

    items = data.get("items")
    if not isinstance(items, list):
        errors.append(f"{path}: `items` must be a list")
        items = []

    for key in ("blocked", "risks", "replans"):
        if key in data and not isinstance(data.get(key), list):
            errors.append(f"{path}: `{key}` must be a list")

    raw_flags = data.get("flags")
    if raw_flags is None:
        warnings.append(f"{path}: optional delivery field missing: `flags`")
        flags: dict[str, Any] = {}
    elif not isinstance(raw_flags, dict):
        errors.append(f"{path}: `flags` must be a mapping")
        flags = {}
    else:
        flags = raw_flags
        for key in FLAG_KEYS:
            if key not in flags:
                warnings.append(f"{path}: optional delivery field missing: `flags.{key}`")
            elif not isinstance(flags.get(key), list):
                errors.append(f"{path}: `flags.{key}` must be a list")

    seen_specs: set[str] = set()
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append(f"{path}: `items[{index}]` must be a mapping")
            continue

        current_key = item_key(item, index)
        spec_id = item.get("spec_id")
        validate_spec_id(f"items[{index}].spec_id", spec_id, errors)
        if spec_id not in (None, ""):
            if str(spec_id) in seen_specs:
                warnings.append(f"{path}: duplicate portfolio item for `{spec_id}`")
            seen_specs.add(str(spec_id))

        validate_enum(f"items[{index}].state", item.get("state"), VALID_STATE, errors)
        validate_enum(f"items[{index}].priority", item.get("priority"), VALID_PRIORITY, errors)
        validate_enum(f"items[{index}].urgency", item.get("urgency"), VALID_URGENCY, errors)
        validate_enum(f"items[{index}].impact", item.get("impact"), VALID_IMPACT, errors)
        validate_enum(f"items[{index}].risk", item.get("risk"), VALID_RISK, errors)
        validate_enum(f"items[{index}].confidence", item.get("confidence"), VALID_CONFIDENCE, errors)

        repos = item.get("candidate_impacted_repos", item.get("repos", []))
        if repos in (None, ""):
            repos = []
        if not isinstance(repos, list):
            errors.append(f"{path}: `items[{index}].candidate_impacted_repos` must be a list")
            repos = []

        if is_missing(item.get("owner")):
            warnings.append(f"{path}: `items[{index}]` is missing owner")
            if current_key not in flag_values(flags, "missing_owner"):
                warnings.append(f"{path}: `{current_key}` should appear in `flags.missing_owner`")

        target_date = item.get("target_date")
        if not is_iso_date(target_date):
            errors.append(f"{path}: `items[{index}].target_date` must use YYYY-MM-DD format")
        target = parse_iso_date(target_date)
        if target and target < date.today() and str(item.get("state", "")) not in TERMINAL_STATES:
            warnings.append(f"{path}: `items[{index}]` appears overdue")
            if current_key not in flag_values(flags, "overdue"):
                warnings.append(f"{path}: `{current_key}` should appear in `flags.overdue`")

        state = str(item.get("state", "unknown"))
        risk = str(item.get("risk", "unknown"))
        if state == "blocked" and current_key not in flag_values(flags, "blocked"):
            warnings.append(f"{path}: `{current_key}` should appear in `flags.blocked`")
        if (state == "at_risk" or risk in {"high", "critical"}) and current_key not in flag_values(flags, "at_risk"):
            warnings.append(f"{path}: `{current_key}` should appear in `flags.at_risk`")
        if len(repos) > 1 and current_key not in flag_values(flags, "multi_repo"):
            warnings.append(f"{path}: `{current_key}` should appear in `flags.multi_repo`")

    for index, entry in enumerate(data.get("blocked") or []):
        if not isinstance(entry, dict):
            errors.append(f"{path}: `blocked[{index}]` must be a mapping")
            continue
        validate_spec_id(f"blocked[{index}].spec_id", entry.get("spec_id"), errors)
        if entry.get("needed_by") not in (None, "") and not is_iso_date(entry.get("needed_by")):
            errors.append(f"{path}: `blocked[{index}].needed_by` must use YYYY-MM-DD format")

    for index, risk in enumerate(data.get("risks") or []):
        if not isinstance(risk, dict):
            errors.append(f"{path}: `risks[{index}]` must be a mapping")
            continue
        validate_enum(f"risks[{index}].severity", risk.get("severity"), VALID_RISK, errors)

    for index, replan in enumerate(data.get("replans") or []):
        if not isinstance(replan, dict):
            errors.append(f"{path}: `replans[{index}]` must be a mapping")
            continue
        validate_spec_id(f"replans[{index}].spec_id", replan.get("spec_id"), errors)
        if not is_iso_date(replan.get("date")):
            errors.append(f"{path}: `replans[{index}].date` must use YYYY-MM-DD format")
        replan_key = str(replan.get("spec_id") or replan.get("feature_key") or "")
        if replan_key and replan_key not in flag_values(flags, "replanned"):
            warnings.append(f"{path}: `{replan_key}` should appear in `flags.replanned`")

    return errors, warnings


def validate_markdown(path: Path) -> tuple[list[str], list[str]]:
    if not path.exists():
        return [f"missing required file: {path}"], []
    text = path.read_text(encoding="utf-8")
    lines = {line.strip() for line in text.splitlines()}
    errors = [f"{path}: missing heading `{heading}`" for heading in REQUIRED_MD_HEADINGS if heading not in lines]
    tokens = find_unresolved_template_tokens_in_text(text)
    if tokens:
        errors.append(f"{path}: contains unresolved template token(s): {', '.join(tokens)}")
    warnings = [f"{path}: contains unresolved unknown placeholder text"] if "Unknown." in text else []
    return errors, warnings



def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Validate nomia portfolio artifacts.")
    parser.add_argument("--portfolio-yaml", default="portfolio.yaml")
    parser.add_argument("--portfolio-md", default="portfolio.md")
    args = parser.parse_args(argv)

    errors, warnings = validate_yaml(Path(args.portfolio_yaml).resolve())
    md_errors, md_warnings = validate_markdown(Path(args.portfolio_md).resolve())
    errors.extend(md_errors)
    warnings.extend(md_warnings)
    errors = unique(errors)
    warnings = unique(warnings)

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
        print("OK: validated nomia portfolio artifacts")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
