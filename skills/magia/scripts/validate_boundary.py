#!/usr/bin/env python3
"""Validate that MAGIA remains self-contained."""

from __future__ import annotations

import re
import sys
from pathlib import Path

from magia_utils import dedupe_preserve_order, posix_rel, print_errors


SKILL_ROOT = Path(__file__).resolve().parents[1]
THIS_FILE = Path(__file__).resolve()

TEXT_SUFFIXES = {".md", ".py", ".yaml", ".yml", ".template", ".txt"}

HARD_PATTERNS = [
    ("external skill URI", re.compile(r"skills://magiarca", re.IGNORECASE)),
    ("external skill path", re.compile(r"\.github[/\\]skills[/\\]magiarca", re.IGNORECASE)),
    ("relative external skill path", re.compile(r"\.\.[/\\]magiarca", re.IGNORECASE)),
    ("external script import", re.compile(r"^\s*(?:from|import)\s+.*magiarca", re.IGNORECASE | re.MULTILINE)),
    ("external script execution", re.compile(r"(?:python|python3|py)\s+.*magiarca[/\\].*\.py", re.IGNORECASE)),
]

DOWNSTREAM_ARTIFACTS = [
    "ops.yaml",
    "status.md",
    "stakeholder-brief.md",
    "replanning.md",
    "roadmap.yaml",
    "roadmap.md",
    "rfc-proposals.md",
    "adr-records.md",
    "feature-map.yaml",
    "feature-report.md",
    "release-notes.md",
    "internal-notes.md",
    "portfolio.md",
    "portfolio.yaml",
]

DOWNSTREAM_MODES = [
    "delivery-intake",
    "delivery-triage",
    "delivery-status",
    "delivery-replan",
    "delivery-portfolio",
    "roadmap-define",
    "roadmap-refine",
    "roadmap-to-specs",
    "rfc-proposal",
    "adr-record",
    "feature-report",
    "release-notes",
    "validate-contracts",
    "normalize-human-artifacts",
]

INVALID_CLAIMS = [
    "PR merge is proof of production release",
    "passing tests are proof of business acceptance",
    "completed execution is stakeholder communication readiness",
]


def iter_skill_files() -> list[Path]:
    paths: list[Path] = []
    for path in SKILL_ROOT.rglob("*"):
        if not path.is_file():
            continue
        if "__pycache__" in path.parts:
            continue
        if path.resolve() == THIS_FILE:
            continue
        if path.suffix.lower() in TEXT_SUFFIXES:
            paths.append(path)
    return sorted(paths)


def rel(path: Path) -> str:
    return posix_rel(path, SKILL_ROOT)


def collect_errors() -> list[str]:
    errors: list[str] = []
    files = iter_skill_files()
    artifact_patterns = [
        (name, re.compile(rf"(?<![\w.-]){re.escape(name)}(?![\w.-])", re.IGNORECASE))
        for name in DOWNSTREAM_ARTIFACTS
    ]
    mode_patterns = [
        (name, re.compile(rf"(?<![\w.-]){re.escape(name)}(?![\w.-])", re.IGNORECASE))
        for name in DOWNSTREAM_MODES
    ]
    claim_patterns = [
        (claim, re.compile(re.escape(claim), re.IGNORECASE))
        for claim in INVALID_CLAIMS
    ]

    for path in files:
        text = path.read_text(encoding="utf-8")

        for label, pattern in HARD_PATTERNS:
            for match in pattern.finditer(text):
                line_no = text.count("\n", 0, match.start()) + 1
                errors.append(f"{rel(path)}:{line_no}: hard coupling: {label}")

        for name, pattern in artifact_patterns:
            for match in pattern.finditer(text):
                line_no = text.count("\n", 0, match.start()) + 1
                errors.append(f"{rel(path)}:{line_no}: downstream-owned artifact reference: {name}")

        for name, pattern in mode_patterns:
            for match in pattern.finditer(text):
                line_no = text.count("\n", 0, match.start()) + 1
                errors.append(f"{rel(path)}:{line_no}: downstream-owned mode reference: {name}")

        for claim, pattern in claim_patterns:
            for match in pattern.finditer(text):
                line_no = text.count("\n", 0, match.start()) + 1
                errors.append(f"{rel(path)}:{line_no}: invalid evidence claim: {claim}")

    return errors


def main() -> int:
    errors = dedupe_preserve_order(collect_errors())
    if errors:
        print_errors(errors)
        return 1

    print("OK: boundary checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
