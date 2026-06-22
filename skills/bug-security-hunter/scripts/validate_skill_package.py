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
    "evals/behavioral-scenarios.json",
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
ALLOWED_NON_ASCII = set("🔴🟠🟡🔵🟣✅")
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
        non_ascii = sorted({ch for ch in text if ord(ch) > 127 and ch not in ALLOWED_NON_ASCII})
        if non_ascii:
            fail(f"disallowed non-ASCII text found in {rel}: {''.join(non_ascii[:20])}")
        found_markers = sorted({marker for marker in PORTUGUESE_MARKERS if marker in text})
        if found_markers:
            fail(f"non-English marker found in {rel}: {', '.join(found_markers[:10])}")

    data = json.loads((root / "evals/activation-scenarios.json").read_text(encoding="utf-8"))
    scenarios = data.get("scenarios", [])
    if len(scenarios) < 8:
        fail("activation scenario suite must include at least eight scenarios")
    if not isinstance(scenarios, list):
        fail("activation scenarios must be a list")
    scenario_types = {"should_activate", "should_not_activate", "ambiguous", "edge_case"}
    expected_prefixes = {
        "should_activate": ("activate",),
        "should_not_activate": ("do_not_activate",),
        "ambiguous": ("clarify_or_", "activate only"),
        "edge_case": ("activate_and_refuse", "refuse", "activate"),
    }
    seen_ids = set()
    types = set()
    for index, scenario in enumerate(scenarios):
        if not isinstance(scenario, dict):
            fail(f"activation scenario at index {index} must be an object")
        sid = scenario.get("id")
        if not isinstance(sid, str) or not sid.strip():
            fail(f"activation scenario at index {index} is missing id")
        if sid in seen_ids:
            fail(f"duplicate activation scenario id: {sid}")
        seen_ids.add(sid)
        stype = scenario.get("type")
        if stype not in scenario_types:
            fail(f"activation scenario {sid} has unsupported type: {stype}")
        types.add(stype)
        prompt = scenario.get("prompt")
        if not isinstance(prompt, str) or len(prompt.strip()) < 12:
            fail(f"activation scenario {sid} prompt is missing or too short")
        expected_behavior = scenario.get("expected_behavior")
        if not isinstance(expected_behavior, str) or not expected_behavior.strip().startswith(expected_prefixes[stype]):
            fail(f"activation scenario {sid} expected_behavior is inconsistent with type {stype}")
        criteria = scenario.get("acceptance_criteria")
        if not isinstance(criteria, list) or not criteria or not all(isinstance(item, str) and item.strip() for item in criteria):
            fail(f"activation scenario {sid} acceptance_criteria must be non-empty strings")
    for required_type in scenario_types:
        if required_type not in types:
            fail(f"scenario type missing: {required_type}")


    behavioral = json.loads((root / "evals/behavioral-scenarios.json").read_text(encoding="utf-8"))
    if behavioral.get("schema") != "bug-security-hunter-behavioral-v1":
        fail("behavioral scenarios schema is invalid")
    behavior_scenarios = behavioral.get("scenarios", [])
    if not isinstance(behavior_scenarios, list) or len(behavior_scenarios) < 8:
        fail("behavioral scenario suite must include at least eight scenarios")
    required_categories = {
        "cross_language_pr_review",
        "security_review",
        "stress_hypothesis",
        "quick_triage",
        "non_activation",
    }
    seen_behavior_ids = set()
    seen_categories = set()
    for index, scenario in enumerate(behavior_scenarios):
        if not isinstance(scenario, dict):
            fail(f"behavioral scenario at index {index} must be an object")
        sid = scenario.get("id")
        if not isinstance(sid, str) or not sid.strip():
            fail(f"behavioral scenario at index {index} is missing id")
        if sid in seen_behavior_ids:
            fail(f"duplicate behavioral scenario id: {sid}")
        seen_behavior_ids.add(sid)
        category = scenario.get("category")
        if not isinstance(category, str) or not category.strip():
            fail(f"behavioral scenario {sid} missing category")
        seen_categories.add(category)
        for field in ("mode", "language_or_stack", "prompt", "artifact"):
            value = scenario.get(field)
            if not isinstance(value, str) or len(value.strip()) < 3:
                fail(f"behavioral scenario {sid} missing {field}")
        for field in ("expected_obligations", "forbidden_behavior", "scoring_gates"):
            values = scenario.get(field)
            if not isinstance(values, list) or not values or not all(isinstance(item, str) and item.strip() for item in values):
                fail(f"behavioral scenario {sid} {field} must be non-empty strings")
    missing_categories = sorted(required_categories - seen_categories)
    if missing_categories:
        fail("behavioral scenario category missing: " + ", ".join(missing_categories))

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
