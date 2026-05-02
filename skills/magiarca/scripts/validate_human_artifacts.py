#!/usr/bin/env python3
"""Validate Magiarca markdown artifacts that rely on canonical headings and resolved placeholders."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from magiarca_utils import find_unresolved_template_tokens_in_text, unique


REQUIRED_HEADINGS_BY_NAME = {
    "status.md": ["# Status", "## Summary", "## Current State", "## Manual Status", "## Inferred Status", "## Risks And Blockers", "## Next Steps", "## Unknowns"],
    "stakeholder-brief.md": ["# Stakeholder Brief", "## Summary", "## Decision Needed", "## Impact", "## Timing", "## Risks"],
    "replanning.md": ["# Replanning", "## Entries"],
    "roadmap.md": ["# Roadmap", "## Context", "## Themes", "## Sequencing", "## Dependencies", "## Risks", "## Open Decisions"],
    "rfc-proposals.md": ["# RFC Proposals", "## Entries"],
    "governance-decisions.md": ["# Governance Decisions", "## Entries"],
}
FIELD_RE = re.compile(r"^- ([^:]+):\s*(.*)$")
GOVERNANCE_DECISION_HEADING_RE = re.compile(r"^### \d{4}-\d{2}-\d{2} - .+")
GOVERNANCE_DECISION_REQUIRED_FIELDS = [
    "Status",
    "Decision",
    "Context",
    "Reason",
    "Alternatives",
    "Impact",
    "Decision Maker",
    "Links",
    "Supersedes",
]
GOVERNANCE_DECISION_STATUSES = {"accepted", "superseded", "deprecated", "corrected"}
RFC_HEADING_RE = re.compile(r"^### [a-z0-9]+(?:-[a-z0-9]+)* - .+")
RFC_REQUIRED_FIELDS = [
    "Status",
    "Impact",
    "Driver",
    "Approvers",
    "Contributors",
    "Informed",
    "Due Date",
    "Background",
    "Assumptions",
    "Decision Criteria",
    "Options",
    "Recommendation",
    "Outcome",
    "Links",
]
RFC_STATUSES = {"draft", "in_review", "accepted", "rejected", "deferred", "superseded"}
RFC_IMPACTS = {"high", "medium", "low"}


def parse_entry_fields(lines: list[str]) -> tuple[dict[str, str], list[str]]:
    fields: dict[str, str] = {}
    field_order: list[str] = []
    for line in lines:
        match = FIELD_RE.match(line.strip())
        if match:
            field_name = match.group(1)
            fields[field_name] = match.group(2).strip()
            field_order.append(field_name)
    return fields, field_order


def validate_required_fields(
    path: Path,
    heading: str,
    fields: dict[str, str],
    field_order: list[str],
    required_fields: list[str],
) -> list[str]:
    errors: list[str] = []
    for field in required_fields:
        if field not in fields:
            errors.append(f"{path}: `{heading}` missing field `{field}`")
        elif fields[field] == "":
            errors.append(f"{path}: `{heading}` field `{field}` is empty")

    expected_order = [field for field in required_fields if field in fields]
    actual_required_order = [field for field in field_order if field in required_fields]
    if actual_required_order != expected_order:
        errors.append(f"{path}: `{heading}` fields must follow canonical order")
    return errors


def validate_governance_decision_entries(path: Path, text: str) -> list[str]:
    errors: list[str] = []
    lines = text.splitlines()
    entry_indexes = [index for index, line in enumerate(lines) if line.startswith("### ")]
    if not entry_indexes:
        return errors

    for position, start in enumerate(entry_indexes):
        end = entry_indexes[position + 1] if position + 1 < len(entry_indexes) else len(lines)
        heading = lines[start].strip()
        if not GOVERNANCE_DECISION_HEADING_RE.match(heading):
            errors.append(f"{path}: governance decision entry heading must be `### YYYY-MM-DD - Title`: {heading}")
        if heading.endswith("?"):
            errors.append(f"{path}: governance decision entry title must record the decision, not ask a question: {heading}")

        fields, field_order = parse_entry_fields(lines[start + 1 : end])
        errors.extend(validate_required_fields(path, heading, fields, field_order, GOVERNANCE_DECISION_REQUIRED_FIELDS))
        status = fields.get("Status", "")
        if status and status not in GOVERNANCE_DECISION_STATUSES:
            errors.append(f"{path}: `{heading}` Status must be one of {sorted(GOVERNANCE_DECISION_STATUSES)}")

    return errors


def validate_rfc_entries(path: Path, text: str) -> list[str]:
    errors: list[str] = []
    lines = text.splitlines()
    entry_indexes = [index for index, line in enumerate(lines) if line.startswith("### ")]
    if not entry_indexes:
        return errors

    for position, start in enumerate(entry_indexes):
        end = entry_indexes[position + 1] if position + 1 < len(entry_indexes) else len(lines)
        heading = lines[start].strip()
        if not RFC_HEADING_RE.match(heading):
            errors.append(f"{path}: RFC entry heading must be `### proposal-id - Title`: {heading}")

        fields, field_order = parse_entry_fields(lines[start + 1 : end])
        errors.extend(validate_required_fields(path, heading, fields, field_order, RFC_REQUIRED_FIELDS))

        status = fields.get("Status", "")
        if status and status not in RFC_STATUSES:
            errors.append(f"{path}: `{heading}` Status must be one of {sorted(RFC_STATUSES)}")

        impact = fields.get("Impact", "")
        if impact and impact not in RFC_IMPACTS:
            errors.append(f"{path}: `{heading}` Impact must be one of {sorted(RFC_IMPACTS)}")

        options = fields.get("Options", "")
        option_count = len([option for option in options.split(";") if option.strip()])
        if options and options != "none" and option_count < 2:
            errors.append(f"{path}: `{heading}` Options must include at least two options")

    return errors


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return [f"{path}: missing file"]

    headings = REQUIRED_HEADINGS_BY_NAME.get(path.name)
    if headings is None:
        return [f"{path}: unsupported Magiarca human artifact `{path.name}`"]

    text = path.read_text(encoding="utf-8")
    lines = {line.strip() for line in text.splitlines()}
    for heading in headings:
        if heading not in lines:
            errors.append(f"{path}: missing heading `{heading}`")

    tokens = find_unresolved_template_tokens_in_text(text)
    if tokens:
        errors.append(f"{path}: contains unresolved template token(s): {', '.join(tokens)}")

    if path.name == "governance-decisions.md":
        errors.extend(validate_governance_decision_entries(path, text))
    if path.name == "rfc-proposals.md":
        errors.extend(validate_rfc_entries(path, text))

    return errors


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Validate Magiarca human markdown artifacts.")
    parser.add_argument("paths", nargs="+", help="Path(s) to Magiarca markdown artifacts.")
    args = parser.parse_args(argv)

    errors: list[str] = []
    for raw_path in args.paths:
        errors.extend(validate(Path(raw_path).resolve()))

    errors = unique(errors)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"FAILED: {len(errors)} errors, 0 warnings")
        return 1

    print(f"OK: validated {len(args.paths)} artifact(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
