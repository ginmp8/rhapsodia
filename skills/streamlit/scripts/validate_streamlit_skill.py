#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REQUIRED = [
    "SKILL.md",
    "agents/openai.yaml",
    "references/app-architecture.md",
    "references/data-caching-connections.md",
    "references/ui-interaction.md",
    "references/llm-chat.md",
    "references/testing-validation.md",
    "references/deployment-security.md",
    "references/source-hygiene.md",
    "examples/request-patterns.md",
    "evals/activation-scenarios.json",
    "assets/templates/app_skeleton.py",
    "assets/templates/review_report.md.template",
]

LOCAL_REF = re.compile(r"`((?:references|examples|evals|assets|scripts|agents)/[^`]+)`")
PROHIBITED = [
    "Comprehensive assistance with Streamlit development, generated from official documentation",
    "This skill includes comprehensive documentation organized into focused categories",
    "Last updated: Based on Streamlit documentation as of October 2025",
]


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    sys.exit(1)


def main() -> None:
    if len(sys.argv) != 2:
        fail("usage: validate_streamlit_skill.py <skill-root>")
    root = Path(sys.argv[1]).resolve()
    skill_md = root / "SKILL.md"
    if not skill_md.exists():
        fail("SKILL.md is missing")

    for rel in REQUIRED:
        if not (root / rel).exists():
            fail(f"missing required file: {rel}")

    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---\nname: streamlit\n"):
        fail("frontmatter must start with name: streamlit")
    if "description:" not in text.split("---", 2)[1]:
        fail("frontmatter description missing")
    for phrase in PROHIBITED:
        if phrase in text:
            fail(f"copied upstream phrase detected: {phrase}")

    for match in LOCAL_REF.finditer(text):
        rel = match.group(1)
        if not (root / rel).exists():
            fail(f"broken local reference in SKILL.md: {rel}")

    scenarios = json.loads((root / "evals/activation-scenarios.json").read_text(encoding="utf-8"))
    types = {item.get("type") for item in scenarios.get("scenarios", [])}
    required_types = {"should_activate", "should_not_activate", "ambiguous", "edge_case", "adversarial"}
    missing = required_types - types
    if missing:
        fail(f"scenario types missing: {sorted(missing)}")
    for item in scenarios.get("scenarios", []):
        if not item.get("id") or not item.get("prompt") or not item.get("expected_behavior"):
            fail("scenario missing id, prompt, or expected_behavior")
        if not item.get("acceptance_criteria"):
            fail(f"scenario missing acceptance_criteria: {item.get('id')}")

    print("PASS: streamlit skill structure is valid")


if __name__ == "__main__":
    main()
