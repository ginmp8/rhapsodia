#!/usr/bin/env python3
"""Validate the structural completeness of a Skill Quality Review Markdown report."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REQUIRED_HEADINGS = [
    "Executive Summary",
    "Scope and Evidence",
    "Reconstructed Skill Contract",
    "Canonical Source Map",
    "Behavioral Invariants",
    "Legacy and Compatibility Assessment",
    "Scorecard",
    "Findings",
    "Validation Gaps",
    "Correction Input",
    "Final Verdict",
]
FINDING_HEADING_RE = re.compile(r"^###\s+(F-\d{3,})\s+-\s+", re.MULTILINE)
REQUIRED_FINDING_FIELDS = [
    "Severity",
    "Category",
    "Evidence status",
    "Location",
    "Expectation",
    "Evidence",
    "Failure path",
    "Impact",
    "Root cause",
    "Smallest fix",
    "Acceptance criteria",
    "Validation",
    "Correction priority",
    "Dependencies",
]
LEGACY_CATEGORY_RE = re.compile(
    r"\*\*Category:\*\*\s*(?:Legacy|Compatibility|Migration|Ownership|Runtime coupling|Structural noise)",
    re.IGNORECASE,
)
LEGACY_REQUIRED_FINDING_FIELDS = [
    "Legacy classification",
    "Canonical source",
]
LEGACY_AUDIT_MATRIX_HEADINGS = [
    "Legacy Classification Matrix",
    "Ownership Matrix",
    "Compatibility Matrix",
    "Runtime Coupling Matrix",
]


CORRECTION_REQUIRED = [
    "Objective",
    "Writable Scope",
    "Read-only / Protected Scope",
    "Preserve",
    "Non-goals",
    "Legacy and Compatibility Constraints",
    "Required Fixes",
    "Validation Sequence",
    "Completion Report",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a skill review Markdown report.")
    parser.add_argument("report", help="Path to the Markdown report")
    parser.add_argument("--json-out", help="Optional JSON validation output")
    return parser.parse_args()


def section_between(text: str, start_heading: str, end_heading: str | None = None) -> str:
    match = re.search(rf"^##\s+{re.escape(start_heading)}\s*$", text, re.MULTILINE | re.IGNORECASE)
    if not match:
        return ""
    start = match.end()
    if end_heading:
        end_match = re.search(rf"^##\s+{re.escape(end_heading)}\s*$", text[start:], re.MULTILINE | re.IGNORECASE)
        if end_match:
            return text[start:start + end_match.start()]
    return text[start:]


def strip_fenced_code(text: str) -> str:
    output: list[str] = []
    in_fence = False
    fence_marker = ""
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith(("```", "~~~")):
            marker = stripped[:3]
            if not in_fence:
                in_fence = True
                fence_marker = marker
            elif marker == fence_marker:
                in_fence = False
                fence_marker = ""
            output.append("")
            continue
        output.append("" if in_fence else line)
    return "\n".join(output)


def finding_blocks(text: str) -> list[tuple[str, str]]:
    matches = list(FINDING_HEADING_RE.finditer(text))
    blocks: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        blocks.append((match.group(1), text[match.start():end]))
    return blocks


def validate(text: str) -> dict[str, object]:
    errors: list[str] = []
    warnings: list[str] = []

    if not re.search(r"^#\s+Skill Quality Review\s*$", text, re.MULTILINE | re.IGNORECASE):
        errors.append("Missing top-level '# Skill Quality Review' heading.")

    for heading in REQUIRED_HEADINGS:
        if not re.search(rf"^##\s+{re.escape(heading)}\s*$", text, re.MULTILINE | re.IGNORECASE):
            errors.append(f"Missing required section: {heading}")

    semantic_text = strip_fenced_code(text)
    blocks = finding_blocks(semantic_text)
    if not blocks:
        warnings.append("No F-### finding blocks were found. This is valid only when the report explicitly states that no material findings exist.")
    for finding_id, block in blocks:
        for field in REQUIRED_FINDING_FIELDS:
            if not re.search(rf"\*\*{re.escape(field)}:\*\*", block, re.IGNORECASE):
                errors.append(f"{finding_id} is missing field: {field}")
        if LEGACY_CATEGORY_RE.search(block):
            for field in LEGACY_REQUIRED_FINDING_FIELDS:
                if not re.search(rf"\*\*{re.escape(field)}:\*\*", block, re.IGNORECASE):
                    errors.append(f"{finding_id} is a legacy finding missing field: {field}")
            classification = re.search(
                r"\*\*Legacy classification:\*\*\s*`?([a-z-]+)`?",
                block,
                re.IGNORECASE,
            )
            allowed = {"current", "migration-only", "obsolete", "duplicate", "contradictory", "noise", "blocked"}
            if classification and classification.group(1).lower() not in allowed:
                errors.append(f"{finding_id} has invalid legacy classification: {classification.group(1)}")

    legacy_mode = bool(re.search(r"Mode:\s*`?legacy-audit`?", text, re.IGNORECASE))
    if legacy_mode:
        for heading in LEGACY_AUDIT_MATRIX_HEADINGS:
            if not re.search(rf"^###\s+{re.escape(heading)}\s*$", text, re.MULTILINE | re.IGNORECASE):
                errors.append(f"legacy-audit report is missing matrix: {heading}")

    correction = section_between(text, "Correction Input", "Final Verdict")
    if correction:
        for heading in CORRECTION_REQUIRED:
            if not re.search(rf"^##\s+{re.escape(heading)}\s*$", correction, re.MULTILINE | re.IGNORECASE):
                errors.append(f"Correction Input is missing subsection: {heading}")
        if "```" not in correction:
            warnings.append("Correction Input is not fenced as a copy-paste-ready block.")

    if re.search(r"\b(100% activation|bug[- ]free|fully validated|production[- ]ready|free of legacy|no legacy exists)\b", text, re.IGNORECASE):
        warnings.append("Report contains a strong readiness or quality claim; verify that executed evidence supports it.")

    verdict_match = re.search(r"Verdict:\s*(.+)", text, re.IGNORECASE)
    if verdict_match and "READY" in verdict_match.group(1).upper():
        if re.search(r"🔴\s*`?BLOCKER`?|🟠\s*`?MAJOR`?", text):
            warnings.append("READY-like verdict appears alongside BLOCKER or MAJOR text; verify gate consistency.")

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "finding_count": len(blocks),
    }


def main() -> int:
    args = parse_args()
    path = Path(args.report).expanduser().resolve()
    if not path.is_file():
        print(f"ERROR: report not found: {path}", file=sys.stderr)
        return 2
    text = path.read_text(encoding="utf-8", errors="replace")
    result = validate(text)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if args.json_out:
        output = Path(args.json_out).expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
