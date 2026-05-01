#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

REQUIRED_FILES = [
    "SKILL.md",
    "references/planning-execution-handoff.md",
    "references/common-planning.md",
    "references/artifacts/templates-and-status.md",
    "references/modes/define.md",
    "references/modes/define-tasks.md",
    "references/modes/refine.md",
    "references/modes/reshape-tasks.md",
    "assets/templates/tasks.md.template",
]

REQUIRED_PHRASES = {
    "SKILL.md": [
        "planning boundary is an authoring boundary",
        "implementation-required tasks are valid planning outputs",
    ],
    "references/planning-execution-handoff.md": [
        "A MAGO planning boundary is not an implementation prohibition",
        "Do not label a task `blocked` merely because it requires code",
    ],
    "references/artifacts/templates-and-status.md": [
        "Execution Handoff Consistency",
        "do not mark a task blocked merely because it requires implementation",
    ],
    "assets/templates/tasks.md.template": [
        "Implementation-required tasks are valid planning outputs",
        "repository_relative_module_or_boundary_to_change",
    ],
}

FORBIDDEN_PHRASES = [
    "requires product implementation; " + "this package is planning-only",
    "requires product implementation; " + "repository is planning-only",
    "requires implementation " + "therefore blocked",
    "requires product implementation " + "therefore blocked",
    "implementation is forbidden because " + "this is a MAGO package",
    "implementation is forbidden because " + "this is a mago package",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    errors: list[str] = []

    for rel in REQUIRED_FILES:
        path = root / rel
        if not path.exists():
            errors.append(f"missing required handoff file: {rel}")

    for rel, phrases in REQUIRED_PHRASES.items():
        path = root / rel
        if not path.exists():
            continue
        content = read(path)
        for phrase in phrases:
            if phrase not in content:
                errors.append(f"{rel}: missing required phrase {phrase!r}")

    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in {".git", "__pycache__", ".pytest_cache"} for part in path.parts):
            continue
        if path.suffix.lower() not in {".md", ".template", ".json", ".yaml", ".yml", ".py"}:
            continue
        try:
            content = read(path)
        except UnicodeDecodeError:
            continue
        lower = content.lower()
        for phrase in FORBIDDEN_PHRASES:
            if phrase.lower() in lower:
                errors.append(f"{path.relative_to(root)}: forbidden phrase {phrase!r}")

    if errors:
        print("FAIL planning-execution handoff contract")
        for error in errors:
            print(f"- {error}")
        return 1

    print("PASS planning-execution handoff contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
