#!/usr/bin/env python3
"""Validate that MAGIA remains self-contained and respects execution/governance boundaries."""

from __future__ import annotations

import re
import sys
from pathlib import Path

from magia_utils import dedupe_preserve_order, posix_rel, print_errors

SKILL_ROOT = Path(__file__).resolve().parents[1]
THIS_FILE = Path(__file__).resolve()
TEXT_SUFFIXES = {".md", ".py", ".yaml", ".yml", ".json", ".template", ".txt"}

# Conceptual references and handoffs are allowed. Runtime imports, direct skill paths,
# and execution of another skill's scripts are not.
EXTERNAL_SKILLS = ("mago", "nomia")
HARD_PATTERNS: list[tuple[str, re.Pattern[str]]] = []
for skill_name in EXTERNAL_SKILLS:
    HARD_PATTERNS.extend(
        [
            (f"external {skill_name} skill URI", re.compile(rf"skills://{skill_name}(?:/|\b)", re.IGNORECASE)),
            (f"external {skill_name} skill path", re.compile(rf"\.github[/\\]skills[/\\]{skill_name}(?:[/\\]|\b)", re.IGNORECASE)),
            (f"relative external {skill_name} path", re.compile(rf"\.\.[/\\]{skill_name}(?:[/\\]|\b)", re.IGNORECASE)),
            (f"external {skill_name} script import", re.compile(rf"^\s*(?:from|import)\s+.*\b{skill_name}\b", re.IGNORECASE | re.MULTILINE)),
            (f"external {skill_name} script execution", re.compile(rf"(?:python|python3|py)\s+.*{skill_name}[/\\].*\.py", re.IGNORECASE)),
        ]
    )

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
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        if path.resolve() == THIS_FILE or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        paths.append(path)
    return sorted(paths)


def rel(path: Path) -> str:
    return posix_rel(path, SKILL_ROOT)


def collect_errors() -> list[str]:
    errors: list[str] = []
    artifact_patterns = [
        (name, re.compile(rf"(?<![\w.-]){re.escape(name)}(?![\w.-])", re.IGNORECASE))
        for name in DOWNSTREAM_ARTIFACTS
    ]
    mode_patterns = [
        (name, re.compile(rf"(?<![\w.-]){re.escape(name)}(?![\w.-])", re.IGNORECASE))
        for name in DOWNSTREAM_MODES
    ]
    claim_patterns = [(claim, re.compile(re.escape(claim), re.IGNORECASE)) for claim in INVALID_CLAIMS]
    retired_name = "magi" + "arca"

    for path in iter_skill_files():
        text = path.read_text(encoding="utf-8-sig")
        lowered = text.lower()
        if retired_name in lowered:
            line_no = lowered[: lowered.index(retired_name)].count("\n") + 1
            errors.append(f"{rel(path)}:{line_no}: retired governance identifier")

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

    return dedupe_preserve_order(errors)


def main() -> int:
    errors = collect_errors()
    if errors:
        print_errors(errors)
        return 1
    print("OK: boundary checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
