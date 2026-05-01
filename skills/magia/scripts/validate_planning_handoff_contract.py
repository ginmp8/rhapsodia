#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

REQUIRED_PHRASES = {
    "SKILL.md": [
        "artifacts are execution inputs, not runtime prohibitions",
        "never use implementation requirement alone as the blocker",
    ],
    "references/planning-handoff.md": [
        "Planning-origin artifacts are execution inputs for MAGIA",
        "Do not block merely because",
        "Return BLOCKED only when a concrete execution blocker",
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
        "concrete execution blocker",
    ],
    "references/artifacts/execution-records.md": [
        "Planning-Origin Package Rules",
        "Do not write execution logs that classify implementation requirement",
    ],
}

BANNED_UNQUALIFIED = [
    "requires product implementation; this package is planning-only",
    "requires product implementation; this repository is planning-only",
    "implementation deferred due to planning-only package",
    "implementation is forbidden",
    "do not implement product code",
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate MAGIA planning handoff hardening rules.")
    parser.add_argument("target", nargs="?", default=".", help="MAGIA skill root")
    args = parser.parse_args()
    root = Path(args.target).resolve()
    errors: list[str] = []

    for rel, phrases in REQUIRED_PHRASES.items():
        path = root / rel
        if not path.exists():
            errors.append(f"missing required file: {rel}")
            continue
        content = path.read_text(encoding="utf-8", errors="replace")
        for phrase in phrases:
            if phrase not in content:
                errors.append(f"{rel} missing phrase: {phrase}")

    for path in root.rglob("*"):
        if path.is_dir() or path.suffix.lower() not in {".md", ".txt", ".yaml", ".yml", ".json"}:
            continue
        content = path.read_text(encoding="utf-8", errors="replace").lower()
        for banned in BANNED_UNQUALIFIED:
            if banned.lower() in content:
                errors.append(f"{path.relative_to(root)} contains banned blocker phrase: {banned}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("planning handoff contract: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
