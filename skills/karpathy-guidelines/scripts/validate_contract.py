#!/usr/bin/env python3
"""Validate the karpathy-guidelines skill contract after package edits."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REQUIRED_SECTIONS = [
    "## Scope",
    "## Core rule",
    "## Mode-specific behavior",
    "## Operating workflow",
    "## Progressive loading",
    "## Output contracts",
    "## Validation checklist",
    "## Stop Conditions",
    "## Package maintenance",
    "## Supporting references",
]

REQUIRED_PATHS = [
    "references/coding-discipline.md",
    "references/context-and-evidence-policy.md",
    "references/response-contracts.md",
    "references/validation-and-stop-conditions.md",
    "references/activation-scenarios.md",
    "evals/activation-boundary-scenarios.json",
    "examples/hardening-scenarios.json",
    "assets/templates/implementation-response.md.template",
    "assets/templates/code-review-response.md.template",
    "scripts/package_skill.py",
]

REQUIRED_SCENARIO_CATEGORIES = {
    "should_activate": 5,
    "should_not_activate": 5,
    "ambiguous": 5,
    "edge_case": 5,
}

REQUIRED_CANONICAL_SCENARIO_TYPES = {
    "should_activate": 5,
    "should_not_activate": 5,
    "ambiguous": 5,
    "edge_case": 5,
    "regression": 2,
    "adversarial": 2,
}

VALID_CANONICAL_SCENARIO_TYPES = set(REQUIRED_CANONICAL_SCENARIO_TYPES)

MARKER_PATTERNS = [
    re.compile(r"\[" + "TO" + "DO", re.IGNORECASE),
    re.compile(r"\b" + "TO" + "DO" + r"\s*:", re.IGNORECASE),
    re.compile("replace with " + "actual", re.IGNORECASE),
    re.compile("this is a " + "placeholder", re.IGNORECASE),
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def fail(message: str) -> int:
    print(f"FAIL: {message}")
    return 1


def parse_frontmatter(text: str) -> dict[str, str] | None:
    match = re.match(r"^---\n(?P<body>.*?)\n---\n", text, re.S)
    if not match:
        return None
    data: dict[str, str] = {}
    for raw_line in match.group("body").splitlines():
        if not raw_line.strip():
            continue
        if ":" not in raw_line:
            return None
        key, value = raw_line.split(":", 1)
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def validate_frontmatter(text: str) -> str | None:
    data = parse_frontmatter(text)
    if data is None:
        return "missing or malformed frontmatter"
    if set(data) != {"name", "description"}:
        return f"frontmatter keys must be exactly name and description, found {sorted(data)}"
    if data["name"] != "karpathy-guidelines":
        return "frontmatter name must be karpathy-guidelines"
    if data["description"] != data["description"].lower():
        return "frontmatter description must be lowercase"
    if len(data["description"].split()) < 25:
        return "frontmatter description is too short for reliable activation"
    return None


def referenced_paths(skill_text: str) -> set[str]:
    refs = set(re.findall(r"`([^`]+\.(?:md|py|yaml|yml|json|template|txt))`", skill_text))
    refs.update(match for match in re.findall(r"\[[^\]]+\]\(([^)]+)\)", skill_text) if "://" not in match)
    return refs


def validate_scenarios(path: Path) -> str | None:
    try:
        data = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        return f"scenario json is invalid: {exc}"
    if not isinstance(data, list):
        return "scenario file must be a json list"
    seen_ids: set[str] = set()
    counts = {key: 0 for key in REQUIRED_SCENARIO_CATEGORIES}
    for item in data:
        if not isinstance(item, dict):
            return "each scenario must be an object"
        missing = {"id", "category", "prompt", "expected_activation", "expected_behavior", "actual_activation", "output_conforms", "quality_score", "needs_rework", "notes"} - set(item)
        if missing:
            return f"scenario {item.get('id', '<missing>')} missing fields {sorted(missing)}"
        if item["id"] in seen_ids:
            return f"duplicate scenario id {item['id']}"
        seen_ids.add(item["id"])
        category = item["category"]
        if category in counts:
            counts[category] += 1
        for measured_field in ["actual_activation", "output_conforms", "quality_score", "needs_rework"]:
            if item[measured_field] is not None:
                return f"scenario {item['id']} has measured field {measured_field}; planned suite values must remain null"
    too_few = {key: value for key, required in REQUIRED_SCENARIO_CATEGORIES.items() if (value := counts[key]) < required}
    if too_few:
        return f"scenario category counts below minimum: {too_few}"
    return None


def validate_canonical_scenario_suite(path: Path) -> str | None:
    try:
        data = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        return f"canonical scenario json is invalid: {exc}"
    if not isinstance(data, dict):
        return "canonical scenario suite must be a json object"
    if data.get("target_skill") != "karpathy-guidelines":
        return "canonical scenario suite target_skill must be karpathy-guidelines"
    if data.get("status") != "planned":
        return "canonical scenario suite status must be planned until scenario prompts are executed"
    scenarios = data.get("scenarios")
    if not isinstance(scenarios, list):
        return "canonical scenario suite scenarios must be a list"
    seen_ids: set[str] = set()
    counts = {key: 0 for key in REQUIRED_CANONICAL_SCENARIO_TYPES}
    required_fields = {"id", "type", "prompt", "expected_behavior", "acceptance_criteria"}
    measured_fields = {"actual_activation", "output_conforms", "quality_score", "needs_rework", "evaluator_decision"}
    for item in scenarios:
        if not isinstance(item, dict):
            return "each canonical scenario must be an object"
        missing = required_fields - set(item)
        if missing:
            return f"canonical scenario {item.get('id', '<missing>')} missing fields {sorted(missing)}"
        scenario_id = item["id"]
        if scenario_id in seen_ids:
            return f"duplicate canonical scenario id {scenario_id}"
        seen_ids.add(scenario_id)
        scenario_type = item["type"]
        if scenario_type not in VALID_CANONICAL_SCENARIO_TYPES:
            return f"canonical scenario {scenario_id} has unsupported type {scenario_type}"
        counts[scenario_type] += 1
        if not isinstance(item["acceptance_criteria"], list) or not item["acceptance_criteria"]:
            return f"canonical scenario {scenario_id} must have non-empty acceptance_criteria list"
        if any(not isinstance(value, str) or not value.strip() for value in item["acceptance_criteria"]):
            return f"canonical scenario {scenario_id} has blank acceptance criteria"
        for measured_field in measured_fields:
            if measured_field in item and item[measured_field] is not None:
                return f"canonical scenario {scenario_id} has measured field {measured_field}; planned suite values must remain null"
    too_few = {key: value for key, required in REQUIRED_CANONICAL_SCENARIO_TYPES.items() if (value := counts[key]) < required}
    if too_few:
        return f"canonical scenario type counts below minimum: {too_few}"
    return None


def scan_markers(skill_dir: Path) -> list[str]:
    hits: list[str] = []
    for path in sorted(skill_dir.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".md", ".py", ".json", ".yaml", ".yml", ".txt"}:
            continue
        rel = path.relative_to(skill_dir).as_posix()
        if rel.startswith("assets/templates/"):
            continue
        for idx, line in enumerate(read_text(path).splitlines(), start=1):
            if "re.compile" in line:
                continue
            if any(pattern.search(line) for pattern in MARKER_PATTERNS):
                hits.append(f"{rel}:{idx}")
    return hits


def main() -> int:
    skill_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return fail("SKILL.md is missing")
    text = read_text(skill_md)

    frontmatter_error = validate_frontmatter(text)
    if frontmatter_error:
        return fail(frontmatter_error)

    missing_sections = [section for section in REQUIRED_SECTIONS if section not in text]
    if missing_sections:
        return fail("missing sections: " + ", ".join(missing_sections))

    missing_paths = [ref for ref in REQUIRED_PATHS if not (skill_dir / ref).exists()]
    if missing_paths:
        return fail("missing required package resources: " + ", ".join(missing_paths))

    unresolved_refs = [ref for ref in referenced_paths(text) if not (skill_dir / ref).exists()]
    if unresolved_refs:
        return fail("referenced paths do not exist: " + ", ".join(sorted(unresolved_refs)))

    scenario_error = validate_scenarios(skill_dir / "examples" / "hardening-scenarios.json")
    if scenario_error:
        return fail(scenario_error)

    canonical_scenario_error = validate_canonical_scenario_suite(skill_dir / "evals" / "activation-boundary-scenarios.json")
    if canonical_scenario_error:
        return fail(canonical_scenario_error)

    marker_hits = scan_markers(skill_dir)
    if marker_hits:
        return fail("unresolved scaffold markers: " + ", ".join(marker_hits[:10]))

    print("PASS: karpathy-guidelines skill contract is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
