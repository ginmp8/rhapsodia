#!/usr/bin/env python3
"""Validate Magiarca reporting Markdown artifacts."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from magiarca_utils import find_unresolved_template_tokens_in_text, unique


FEATURE_REPORT_HEADINGS = [
    ("# Feature Report",),
    ("## Summary",),
    ("## Delivered Scope",),
    ("## Evidence",),
    ("## Validation", "## Validation Evidence"),
    ("## Rollout", "## Rollout And Rollback"),
    ("## Risks And Limitations",),
    ("## Follow-ups",),
]
RELEASE_NOTES_HEADINGS = [
    ("# Release Notes",),
    ("## Summary",),
    ("## User Impact",),
    ("## Changes",),
    ("## Rollout", "## Availability And Rollout"),
    ("## Validation", "## Validation Status"),
    ("## Known Limitations",),
]
INTERNAL_NOTES_HEADINGS = [("# Internal Notes",), ("## Summary",), ("## Internal Details",), ("## Follow-ups",)]

EVIDENCE_STATUS_RE = re.compile(
    r"\b(evidence status|deployment evidence|release evidence|rollout evidence|validation evidence|"
    r"unknown|draft|pending|not recorded|not available|not released|not deployed|no evidence|"
    r"passed|failed|blocked|completed|validated|verified|tested|manual test|unit test|"
    r"integration test|e2e|smoke test|test run|validation run)\b",
    re.I,
)
UNCERTAIN_STATUS_RE = re.compile(
    r"\b(unknown|draft|pending|not recorded|not available|not released|not deployed|no evidence)\b",
    re.I,
)
EXPLICIT_RELEASE_EVIDENCE_RE = re.compile(
    r"\b(evidence:|deployment evidence|release evidence|rollout evidence|deployment record|"
    r"release record|rollout record|deploy id|deployment id|change ticket|release ticket|"
    r"ops\.yaml|execution evidence)\b",
    re.I,
)
RELEASE_CLAIM_RE = re.compile(
    r"\b(available|released|shipped|deployed|rolled out|rollout complete|enabled|production|"
    r"generally available|ga\b|live)\b",
    re.I,
)
PR_MERGE_RE = re.compile(r"\b(merged pull request|pull request merged|merged pr|pr merged)\b", re.I)
STAKEHOLDER_AUDIENCE_RE = re.compile(
    r"\b(stakeholders?|users?|customers?|support|customer-facing|operations|ops|tech leads?|onboarding|admins?)\b",
    re.I,
)
INTERNAL_ONLY_RE = re.compile(
    r"\b(internal-only|do not share|private link|private ticket|private slack|secret|credential|"
    r"password|token|api key|private key)\b",
    re.I,
)
STAKEHOLDER_TECH_DETAIL_RE = re.compile(
    r"\b(stack trace|raw log|debug log|commit hash|branch name|pull request|merged pr|"
    r"database migration id|private dashboard|internal ticket|incident channel)\b",
    re.I,
)
SOURCE_OF_TRUTH_RE = re.compile(
    r"\b(branches?|pull requests?|prs?|commits?|checks?|review status|last commit age)\b",
    re.I,
)
SECRET_VALUE_RE = re.compile(
    r"(?i)\b(password|token|api[_ -]?key|secret|credential|private[_ -]?key)\b\s*[:=]\s*\S+"
)


def has_heading(text: str, heading: str) -> bool:
    return any(line.strip() == heading for line in text.splitlines())


def has_any_heading(text: str, headings: tuple[str, ...]) -> bool:
    return any(has_heading(text, heading) for heading in headings)


def heading_label(headings: tuple[str, ...]) -> str:
    return headings[0] if len(headings) == 1 else " or ".join(f"`{heading}`" for heading in headings)


def heading_level(line: str) -> int | None:
    stripped = line.strip()
    if not stripped.startswith("#"):
        return None
    marker = stripped.split(" ", 1)[0]
    if marker and set(marker) == {"#"}:
        return len(marker)
    return None


def section_body(text: str, heading: str) -> str:
    lines = text.splitlines()
    start: int | None = None
    level: int | None = None
    for index, line in enumerate(lines):
        if line.strip() == heading:
            start = index + 1
            level = heading_level(line)
            break
    if start is None:
        return ""

    end = len(lines)
    for index in range(start, len(lines)):
        next_level = heading_level(lines[index])
        if next_level is not None and level is not None and next_level <= level:
            end = index
            break
    return "\n".join(lines[start:end]).strip()


def first_section_body(text: str, headings: tuple[str, ...]) -> tuple[str, str]:
    for heading in headings:
        body = section_body(text, heading)
        if body:
            return heading, body
        if has_heading(text, heading):
            return heading, ""
    return headings[0], ""


def is_empty_or_unknown(text: str) -> bool:
    normalized = re.sub(r"[\s.\-:]+", " ", text).strip().lower()
    return normalized in {"", "unknown", "unknown unknown"} or normalized.startswith("unknown ")


def validate_markdown(path: Path, headings: list[tuple[str, ...]], required: bool) -> tuple[str, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if not path.exists():
        if required:
            errors.append(f"missing required file: {path}")
        return "", errors, warnings

    text = path.read_text(encoding="utf-8")
    for heading_group in headings:
        if not has_any_heading(text, heading_group):
            errors.append(f"{path}: missing heading {heading_label(heading_group)}")

    if SECRET_VALUE_RE.search(text):
        errors.append(f"{path}: appears to contain a secret or credential value")

    tokens = find_unresolved_template_tokens_in_text(text)
    if tokens:
        errors.append(f"{path}: contains unresolved template token(s): {', '.join(tokens)}")

    if "Unknown." in text or "- Unknown." in text:
        warnings.append(f"{path}: contains unresolved unknown placeholder text")

    if SOURCE_OF_TRUTH_RE.search(text):
        warnings.append(f"{path}: may contain manually maintained branch, PR, commit, check, or review state")

    return text, errors, warnings


def validate_audience(path: Path, text: str, stakeholder_only: bool) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if not has_heading(text, "## Audience"):
        return errors, warnings

    audience = section_body(text, "## Audience")

    if is_empty_or_unknown(audience):
        warnings.append(f"{path}: `## Audience` does not identify intended readers")
        return errors, warnings

    if not STAKEHOLDER_AUDIENCE_RE.search(audience):
        warnings.append(f"{path}: `## Audience` does not clearly identify human readers")

    if stakeholder_only and re.search(r"\b(internal|engineers only|developers only|repo maintainers)\b", audience, re.I):
        errors.append(f"{path}: release notes audience must be stakeholder-facing, not internal-only")

    return errors, warnings


def validate_evidence_section(path: Path, text: str, headings: tuple[str, ...], label: str) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    heading, body = first_section_body(text, headings)

    if is_empty_or_unknown(body):
        warnings.append(f"{path}: `{heading}` has no concrete {label}; keep status explicitly unknown if evidence is absent")
        return errors, warnings

    if not EVIDENCE_STATUS_RE.search(body):
        errors.append(f"{path}: `{heading}` must summarize {label} or mark status as unknown, draft, pending, or not recorded")

    if PR_MERGE_RE.search(body) and RELEASE_CLAIM_RE.search(body):
        errors.append(f"{path}: `{heading}` treats PR merge as release evidence")

    return errors, warnings


def validate_rollout_evidence(path: Path, text: str, headings: tuple[str, ...]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    heading, body = first_section_body(text, headings)

    if RELEASE_CLAIM_RE.search(body) and not EXPLICIT_RELEASE_EVIDENCE_RE.search(body):
        errors.append(f"{path}: `{heading}` claims release or availability without explicit deployment evidence")

    if not RELEASE_CLAIM_RE.search(body) and not UNCERTAIN_STATUS_RE.search(body):
        warnings.append(f"{path}: `{heading}` should state rollout status or mark it unknown/draft")

    return errors, warnings


def validate_feature_report(path: Path, text: str) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    audience_errors, audience_warnings = validate_audience(path, text, stakeholder_only=False)
    errors.extend(audience_errors)
    warnings.extend(audience_warnings)

    for heading, label in (
        (("## Evidence",), "delivery evidence"),
        (("## Validation", "## Validation Evidence"), "validation evidence"),
        (("## Rollout", "## Rollout And Rollback"), "rollout, deployment, and rollback evidence"),
    ):
        section_errors, section_warnings = validate_evidence_section(path, text, heading, label)
        errors.extend(section_errors)
        warnings.extend(section_warnings)

    _, rollout = first_section_body(text, ("## Rollout", "## Rollout And Rollback"))
    if "rollback" not in rollout.lower():
        errors.append(f"{path}: rollout section must include rollback notes")
    rollout_errors, rollout_warnings = validate_rollout_evidence(path, text, ("## Rollout", "## Rollout And Rollback"))
    errors.extend(rollout_errors)
    warnings.extend(rollout_warnings)

    for heading in ("## Delivered Scope",):
        if is_empty_or_unknown(section_body(text, heading)):
            warnings.append(f"{path}: `{heading}` is still unknown")

    if INTERNAL_ONLY_RE.search(text):
        warnings.append(f"{path}: contains internal-only or sensitive markers; move private detail to internal-notes.md")

    return errors, warnings


def validate_release_notes(path: Path, text: str, internal_exists: bool) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    audience_errors, audience_warnings = validate_audience(path, text, stakeholder_only=True)
    errors.extend(audience_errors)
    warnings.extend(audience_warnings)

    for heading, label in (
        (("## Rollout", "## Availability And Rollout"), "release or deployment evidence"),
        (("## Validation", "## Validation Status"), "validation evidence"),
    ):
        section_errors, section_warnings = validate_evidence_section(path, text, heading, label)
        errors.extend(section_errors)
        warnings.extend(section_warnings)

    if INTERNAL_ONLY_RE.search(text):
        errors.append(f"{path}: release notes contain internal-only or sensitive language")

    if STAKEHOLDER_TECH_DETAIL_RE.search(text):
        errors.append(f"{path}: release notes contain internal implementation detail that belongs in internal-notes.md")

    if PR_MERGE_RE.search(text) and RELEASE_CLAIM_RE.search(text):
        errors.append(f"{path}: PR merge is not production release evidence")

    if not internal_exists and re.search(r"\b(internal risk|operational watchpoint|private reference)\b", text, re.I):
        warnings.append(f"{path}: internal details are present but internal-notes.md was not provided")

    rollout_errors, rollout_warnings = validate_rollout_evidence(path, text, ("## Rollout", "## Availability And Rollout"))
    errors.extend(rollout_errors)
    warnings.extend(rollout_warnings)

    for heading in ("## User Impact", "## Changes", "## Known Limitations"):
        if is_empty_or_unknown(section_body(text, heading)):
            warnings.append(f"{path}: `{heading}` is still unknown")

    return errors, warnings


def validate_internal_notes(path: Path, text: str) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if SECRET_VALUE_RE.search(text):
        errors.append(f"{path}: internal notes must not contain secret or credential values")

    if re.search(r"\b(full raw log|complete raw log|entire log)\b", text, re.I):
        warnings.append(f"{path}: internal notes should summarize logs instead of storing full raw output")

    return errors, warnings


def required_by_mode(mode: str) -> tuple[bool, bool]:
    if mode == "feature-report":
        return True, False
    if mode == "release-notes":
        return False, True
    return True, True



def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Validate Magiarca reporting artifacts.")
    parser.add_argument("--feature-report", default="feature-report.md")
    parser.add_argument("--release-notes", default="release-notes.md")
    parser.add_argument("--internal-notes", default="internal-notes.md")
    parser.add_argument("--mode", choices=("feature-report", "release-notes", "all"), default="all")
    parser.add_argument(
        "--require-release-notes",
        action="store_true",
        help="Backward-compatible alias for requiring release-notes.md.",
    )
    args = parser.parse_args(argv)

    errors: list[str] = []
    warnings: list[str] = []

    require_feature, require_release = required_by_mode(args.mode)
    if args.require_release_notes:
        require_release = True

    feature_path = Path(args.feature_report).resolve()
    release_path = Path(args.release_notes).resolve()
    internal_path = Path(args.internal_notes).resolve()
    internal_exists = internal_path.exists()

    feature_text, report_errors, report_warnings = validate_markdown(
        feature_path, FEATURE_REPORT_HEADINGS, require_feature
    )
    errors.extend(report_errors)
    warnings.extend(report_warnings)
    if feature_text and not find_unresolved_template_tokens_in_text(feature_text):
        feature_errors, feature_warnings = validate_feature_report(feature_path, feature_text)
        errors.extend(feature_errors)
        warnings.extend(feature_warnings)

    release_text, release_errors, release_warnings = validate_markdown(
        release_path, RELEASE_NOTES_HEADINGS, require_release
    )
    errors.extend(release_errors)
    warnings.extend(release_warnings)
    if release_text and not find_unresolved_template_tokens_in_text(release_text):
        notes_errors, notes_warnings = validate_release_notes(release_path, release_text, internal_exists)
        errors.extend(notes_errors)
        warnings.extend(notes_warnings)

    internal_text, internal_errors, internal_warnings = validate_markdown(
        internal_path, INTERNAL_NOTES_HEADINGS, False
    )
    errors.extend(internal_errors)
    warnings.extend(internal_warnings)
    if internal_text:
        notes_errors, notes_warnings = validate_internal_notes(internal_path, internal_text)
        errors.extend(notes_errors)
        warnings.extend(notes_warnings)

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
        print("OK: validated Magiarca reporting artifacts")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
