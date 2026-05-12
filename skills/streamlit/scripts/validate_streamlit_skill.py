#!/usr/bin/env python3
"""Validate the Streamlit skill package structure."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REQUIRED = [
    "SKILL.md",
    "agents/openai.yaml",
    "references/reference-map.md",
    "references/architecture-and-state.md",
    "references/api-decision-guide.md",
    "references/api-catalog.md",
    "references/data-caching-connections.md",
    "references/ui-data-visualization.md",
    "references/llm-chat-ai.md",
    "references/testing-validation.md",
    "references/deployment-security.md",
    "references/production-review-rubric.md",
    "references/troubleshooting.md",
    "references/recipes.md",
    "references/source-hygiene.md",
    "examples/request-patterns.md",
    "evals/activation-scenarios.json",
    "assets/templates/app_skeleton.py",
    "assets/templates/review_report.md.template",
]

FORBIDDEN_MARKERS = [
    "Comprehensive assistance with Streamlit development" + ", generated from official documentation covering 317 pages",
    "Last updated: Based on Streamlit documentation" + " as of October 2025",
    "SKILL.md" + ".backup",
]


def fail(msg: str) -> int:
    print(f"FAIL: {msg}")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("target", nargs="?", default=".")
    args = parser.parse_args()
    root = Path(args.target).resolve()

    if not (root / "SKILL.md").exists():
        return fail("missing SKILL.md")

    missing = [p for p in REQUIRED if not (root / p).exists()]
    if missing:
        return fail("missing required files: " + ", ".join(missing))

    skill = (root / "SKILL.md").read_text(encoding="utf-8")
    if not skill.startswith("---\nname: streamlit\n"):
        return fail("frontmatter must start with name: streamlit")
    if "description:" not in skill.split("---", 2)[1]:
        return fail("frontmatter missing description")
    if len(skill.splitlines()) > 320:
        return fail("SKILL.md is too long for a control plane")

    all_text = "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in root.rglob("*") if p.is_file())
    for marker in FORBIDDEN_MARKERS:
        if marker in all_text:
            return fail(f"forbidden copied marker found: {marker}")

    if "st.cache_data" not in all_text or "st.cache_resource" not in all_text:
        return fail("cache guidance missing")
    if "st.session_state" not in all_text:
        return fail("session state guidance missing")
    if "st.chat_message" not in all_text or "st.chat_input" not in all_text:
        return fail("chat guidance missing")
    if "st.data_editor" not in all_text:
        return fail("data editor guidance missing")
    if "st.file_uploader" not in all_text:
        return fail("file upload guidance missing")

    scenario_path = root / "evals/activation-scenarios.json"
    try:
        data = json.loads(scenario_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return fail(f"invalid activation-scenarios.json: {exc}")
    scenarios = data.get("scenarios", [])
    if len(scenarios) < 8:
        return fail("expected at least 8 activation scenarios")
    types = {s.get("type") for s in scenarios}
    required_types = {"should_activate", "should_not_activate", "ambiguous", "edge_case"}
    if not required_types.issubset(types):
        return fail("activation scenarios must include should_activate, should_not_activate, ambiguous, and edge_case")

    py_files = list((root / "scripts").glob("*.py")) + list((root / "assets" / "templates").glob("*.py"))
    for path in py_files:
        compile(path.read_text(encoding="utf-8"), str(path), "exec")

    print("PASS: streamlit skill structure is valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
