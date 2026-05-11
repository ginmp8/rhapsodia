#!/usr/bin/env python3
"""Validate the context-architect skill package structure."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REQUIRED_FILES = [
    "SKILL.md",
    "agents/openai.yaml",
    "references/context-map-contract.md",
    "references/dependency-tracing.md",
    "references/change-sequencing.md",
    "references/risk-and-validation-checklist.md",
    "references/upstream-source.md",
    "assets/templates/context-map.md.template",
    "scripts/generate_context_map_skeleton.py",
    "scripts/package_skill.py",
    "evals/activation-scenarios.json",
]

FORBIDDEN_MARKERS = ["[" + "TO" + "DO", "TO" + "DO:", "example" + "_asset.txt", "api" + "_reference.md", "scripts/" + "ex" + "ample.py"]


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def parse_frontmatter(text: str) -> dict[str, str]:
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        fail("SKILL.md is missing YAML frontmatter")
    fields: dict[str, str] = {}
    for raw_line in match.group(1).splitlines():
        if not raw_line.strip():
            continue
        if ":" not in raw_line:
            fail(f"invalid frontmatter line: {raw_line}")
        key, value = raw_line.split(":", 1)
        fields[key.strip()] = value.strip().strip('"').strip("'")
    return fields


def main() -> int:
    if len(sys.argv) != 2:
        fail("usage: validate_context_architect_skill.py <skill_dir>")
    root = Path(sys.argv[1]).resolve()
    if not root.exists():
        fail(f"target does not exist: {root}")
    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            fail(f"missing required file: {rel}")
    skill_text = (root / "SKILL.md").read_text(encoding="utf-8")
    fields = parse_frontmatter(skill_text)
    if set(fields) != {"name", "description"}:
        fail("frontmatter must contain only name and description")
    if fields["name"] != "context-architect":
        fail("frontmatter name must be context-architect")
    if fields["description"] != fields["description"].lower():
        fail("frontmatter description must be lowercase")
    if len(fields["description"].split()) < 45:
        fail("frontmatter description is too short for reliable activation")
    scan_suffixes = {".md", ".yaml", ".json", ".template"}
    all_text = "\n".join(
        p.read_text(encoding="utf-8", errors="ignore")
        for p in root.rglob("*")
        if p.is_file() and p.suffix in scan_suffixes
    )
    for marker in FORBIDDEN_MARKERS:
        if marker in all_text:
            fail(f"forbidden scaffold marker remains: {marker}")
    scenarios = json.loads((root / "evals/activation-scenarios.json").read_text(encoding="utf-8"))
    if not isinstance(scenarios, dict) or "scenarios" not in scenarios:
        fail("activation scenario file must contain a scenarios array")
    ids = set()
    for scenario in scenarios["scenarios"]:
        for key in ["id", "type", "prompt", "expected_behavior"]:
            if key not in scenario:
                fail(f"scenario missing key {key}: {scenario}")
        if scenario["id"] in ids:
            fail(f"duplicate scenario id: {scenario['id']}")
        ids.add(scenario["id"])
    print("PASS: context-architect skill package is structurally valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
