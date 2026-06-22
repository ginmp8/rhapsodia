#!/usr/bin/env python3
"""Validate the bug-security-hunter skill package structure."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REQUIRED = [
    "SKILL.md",
    "agents/openai.yaml",
    "assets/icon.svg",
    "assets/templates/bug-hunt-report.md.template",
    "assets/templates/hypothesis-record.md.template",
    "examples/review-scenarios.md",
    "evals/activation-scenarios.json",
    "references/review-workflow.md",
    "references/pr-and-code-rubric.md",
    "references/async-flow-analysis.md",
    "references/security-threat-model.md",
    "references/csharp-dotnet-hotspots.md",
    "references/stress-harness.md",
    "references/output-contracts.md",
]

BANNED_NAMES = {".git", "__pycache__", ".pytest_cache", ".mypy_cache"}
BANNED_MARKERS = ["TO" + "DO", "FIX" + "ME", "INS" + "ERT ", "T" + "BD", "Lorem" + " ipsum"]


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def main() -> int:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd().resolve()
    if not root.exists() or not root.is_dir():
        fail(f"target is not a directory: {root}")

    skill_files = list(root.glob("SKILL.md"))
    if len(skill_files) != 1:
        fail("package must contain exactly one root SKILL.md")

    missing = [p for p in REQUIRED if not (root / p).exists()]
    if missing:
        fail("missing required files: " + ", ".join(missing))

    skill_text = (root / "SKILL.md").read_text(encoding="utf-8")
    frontmatter = re.match(r"^---\n(.*?)\n---\n", skill_text, re.S)
    if not frontmatter:
        fail("SKILL.md must start with YAML frontmatter")
    fm = frontmatter.group(1)
    if "name: bug-security-hunter" not in fm:
        fail("frontmatter name must be bug-security-hunter")
    if "description:" not in fm or len(re.search(r"description:\s*(.*)", fm).group(1)) < 80:
        fail("frontmatter description is missing or too short")

    for marker in BANNED_MARKERS:
        for path in root.rglob("*"):
            if path.is_file() and path.suffix not in {".svg"}:
                text = path.read_text(encoding="utf-8", errors="ignore")
                if marker in text and not path.name.endswith(".template"):
                    fail(f"unfinished marker {marker!r} found in {path.relative_to(root)}")

    for path in root.rglob("*"):
        if any(part in BANNED_NAMES for part in path.parts):
            fail(f"banned generated/cache path included: {path.relative_to(root)}")

    data = json.loads((root / "evals/activation-scenarios.json").read_text(encoding="utf-8"))
    scenarios = data.get("scenarios", [])
    if len(scenarios) < 6:
        fail("activation scenario suite must include at least six scenarios")
    types = {s.get("type") for s in scenarios}
    for required_type in {"activation", "non_activation", "ambiguous", "edge"}:
        if required_type not in types:
            fail(f"scenario type missing: {required_type}")

    referenced = set(re.findall(r"`([^`]+\.(?:md|json|template|py|yaml|svg))`", skill_text))
    for ref in referenced:
        if ref.startswith("../"):
            continue
        if not (root / ref).exists():
            fail(f"SKILL.md references missing local file: {ref}")

    print("PASS: bug-security-hunter package structure is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
