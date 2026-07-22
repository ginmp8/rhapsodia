#!/usr/bin/env python3
"""Validate MAGIA planning-to-execution handoff rules."""

from __future__ import annotations

import argparse
from pathlib import Path

REQUIRED_FILES = [
    "references/ecosystem-handoff-contract.md",
    "references/ecosystem-handoff-contract.json",
    "scripts/ecosystem_handoff.py",
    "scripts/validate_ecosystem_handoff_contract.py",
]

REQUIRED_PHRASES = {
    "SKILL.md": [
        "Planning-origin artifacts are execution inputs, not runtime prohibitions",
        "Never use implementation requirement alone as the blocker",
        "MAGIA is independent",
        "ecosystem handoff contract",
        "scripts/ecosystem_handoff.py",
    ],
    "references/planning-handoff.md": [
        "Planning-origin artifacts are execution inputs for MAGIA",
        "Do not block merely because",
        "Return BLOCKED only when a concrete execution blocker",
        "## Typed Envelope Handoff",
        "mago_to_magia",
        "magia_to_mago",
        "magia_to_nomia",
    ],
    "references/modes/ralph.md": [
        "Planning-Origin Handoff",
        "Do not treat implementation requirement",
        "Unattended Loop Protocol",
    ],
    "references/common-execution.md": [
        "Planning-Origin Execution Inputs",
        "Planning authorship means the artifact was not implemented by its authoring workflow",
    ],
    "references/validation-and-closure.md": [
        "Invalid blockers include implementation being required",
        "A concrete execution blocker is required",
    ],
    "references/artifacts/execution-records.md": [
        "Planning-Origin Package Rules",
        "Do not write execution logs that classify implementation requirement",
    ],
}
BANNED = [
    "requires product implementation; this package is planning-only",
    "requires product implementation; this repository is planning-only",
    "implementation deferred due to planning-only package",
    "implementation is forbidden",
    "do not implement product code",
]


def collect_errors(root: Path) -> list[str]:
    errors: list[str] = []
    for rel in REQUIRED_FILES:
        if not (root / rel).is_file():
            errors.append(f"missing required ecosystem handoff file: {rel}")
    for rel, phrases in REQUIRED_PHRASES.items():
        path = root / rel
        if not path.is_file():
            errors.append(f"missing required file: {rel}")
            continue
        text = path.read_text(encoding="utf-8-sig")
        for phrase in phrases:
            if phrase not in text:
                errors.append(f"{rel} missing phrase: {phrase}")
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".md", ".txt", ".yaml", ".yml", ".json"}:
            text = path.read_text(encoding="utf-8-sig").lower()
            for phrase in BANNED:
                if phrase in text:
                    errors.append(f"{path.relative_to(root)} contains banned blocker phrase: {phrase}")
    return list(dict.fromkeys(errors))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate MAGIA planning handoff contract.")
    parser.add_argument("target", nargs="?", default=".")
    args = parser.parse_args(argv)
    errors = collect_errors(Path(args.target).resolve())
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("planning handoff contract: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
