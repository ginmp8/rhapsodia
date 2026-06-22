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
    "scripts/validate_skill_package.py",
    "scripts/package_skill.py",
]

BANNED_NAMES = {".git", "__pycache__", ".pytest_cache", ".mypy_cache"}
BANNED_MARKERS = ["TO" + "DO", "FIX" + "ME", "INS" + "ERT ", "T" + "BD", "Lorem" + " ipsum"]
BANNED_SUFFIXES = {".pyc", ".pyo", ".zip"}
TEXT_SUFFIXES = {".md", ".json", ".yaml", ".yml", ".py", ".template", ".txt"}
PORTUGUESE_MARKERS = [
    "Re" + "vise ", "Que" + "ro ", "Fa" + "ca", "Mon" + "te ", "Imple" + "mente",
    "Cr" + "ie ", "Es" + "se ", "Ol" + "he ", "Ga" + "ranta ", "segu" + "ranca",
    "regres" + "soes", "corre" + "cao", "opera" + "cao", "autenti" + "cacao",
    "autoriza" + "cao", "mensa" + "geria", "ban" + "co", "cada" + "stro",
    "con" + "ta", "produ" + "to", "co" + "digo", "na" + "o ", "veredi" + "to",
    "lac" + "unas", "pergun" + "tas", "trata" + "mento", "resu" + "mo",
    "se" + "nha", "cha" + "ve", "inje" + "cao",
]


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def text_files(root: Path):
    for path in root.rglob("*"):
        if path.is_file() and (path.suffix in TEXT_SUFFIXES or path.name.endswith(".template")):
            yield path


def main() -> int:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd().resolve()
    if not root.exists() or not root.is_dir():
        fail(f"target is not a directory: {root}")

    skill_files = list(root.glob("SKILL.md"))
    if len(skill_files) != 1:
        fail("package must include exactly one root SKILL.md")

    for path in root.rglob("*"):
        rel = path.relative_to(root)
        if path.is_symlink():
            fail(f"symlink is not allowed in package: {rel}")
        if any(part in BANNED_NAMES for part in rel.parts):
            fail(f"banned generated/cache path included: {rel}")
        if path.is_file() and path.suffix in BANNED_SUFFIXES:
            fail(f"banned generated/package file included: {rel}")

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
    description = re.search(r"description:\s*(.*)", fm)
    if not description or len(description.group(1).strip()) < 80:
        fail("frontmatter description is missing or too short")

    for path in text_files(root):
        text = path.read_text(encoding="utf-8", errors="ignore")
        rel = path.relative_to(root)
        for marker in BANNED_MARKERS:
            if marker in text and not path.name.endswith(".template"):
                fail(f"unfinished marker {marker!r} found in {rel}")
        non_ascii = sorted({ch for ch in text if ord(ch) > 127})
        if non_ascii:
            fail(f"non-ASCII text found in {rel}: {''.join(non_ascii[:20])}")
        found_markers = sorted({marker for marker in PORTUGUESE_MARKERS if marker in text})
        if found_markers:
            fail(f"non-English marker found in {rel}: {', '.join(found_markers[:10])}")

    data = json.loads((root / "evals/activation-scenarios.json").read_text(encoding="utf-8"))
    scenarios = data.get("scenarios", [])
    if len(scenarios) < 8:
        fail("activation scenario suite must include at least eight scenarios")
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
