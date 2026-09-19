#!/usr/bin/env python3
"""Validate the decision-variance control contract for karpathy-guidelines."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REQUIRED_SKILL_REFS = {
    "references/decision-variance-model.md",
    "evals/decision-variance-scenarios.json",
    "scripts/validate_decision_variance.py",
}

REQUIRED_REFERENCE_MARKERS = {
    "## Control classes",
    "## Classification test",
    "## Mixed decisions",
    "## Heuristic defaults and tie-breakers",
    "## Judgment rubric",
    "## Subjective review",
    "## Evidence precedence",
    "## Anti-patterns",
    "Do not manufacture determinism.",
    "independent evaluation",
}

REQUIRED_CLASSES = {
    "mechanical": 2,
    "heuristic": 2,
    "judgment": 2,
    "subjective": 2,
    "mixed": 2,
    "anti_overcontrol": 1,
    "external_nondeterminism": 1,
}


def fail(message: str) -> int:
    print(f"FAIL: {message}")
    return 1


def main() -> int:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd().resolve()
    skill_path = root / "SKILL.md"
    ref_path = root / "references" / "decision-variance-model.md"
    eval_path = root / "evals" / "decision-variance-scenarios.json"

    for path in [skill_path, ref_path, eval_path]:
        if not path.is_file():
            return fail(f"missing required file: {path.relative_to(root).as_posix()}")

    skill_text = skill_path.read_text(encoding="utf-8")
    missing_refs = sorted(ref for ref in REQUIRED_SKILL_REFS if ref not in skill_text)
    if missing_refs:
        return fail("SKILL.md missing decision-variance references: " + ", ".join(missing_refs))

    ref_text = ref_path.read_text(encoding="utf-8")
    missing_markers = sorted(marker for marker in REQUIRED_REFERENCE_MARKERS if marker not in ref_text)
    if missing_markers:
        return fail("decision-variance reference missing sections: " + ", ".join(missing_markers))

    for term in ["Mechanical", "Heuristic", "Judgment", "Subjective"]:
        if term not in ref_text:
            return fail(f"decision-variance reference missing control class: {term}")

    try:
        data = json.loads(eval_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return fail(f"decision-variance scenario JSON is invalid: {exc}")

    if data.get("target_skill") != "karpathy-guidelines":
        return fail("decision-variance target_skill must be karpathy-guidelines")
    if data.get("status") != "planned":
        return fail("decision-variance scenarios must remain planned until executed")
    scenarios = data.get("scenarios")
    if not isinstance(scenarios, list):
        return fail("decision-variance scenarios must be a list")

    counts = {key: 0 for key in REQUIRED_CLASSES}
    seen: set[str] = set()
    required_fields = {"id", "class", "prompt", "expected_behavior", "acceptance_criteria", "measured"}
    for item in scenarios:
        if not isinstance(item, dict):
            return fail("each decision-variance scenario must be an object")
        missing = required_fields - set(item)
        if missing:
            return fail(f"scenario {item.get('id', '<missing>')} missing fields: {sorted(missing)}")
        scenario_id = item["id"]
        if scenario_id in seen:
            return fail(f"duplicate scenario id: {scenario_id}")
        seen.add(scenario_id)
        scenario_class = item["class"]
        if scenario_class not in counts:
            return fail(f"scenario {scenario_id} has unsupported class: {scenario_class}")
        counts[scenario_class] += 1
        if item["measured"] is not None:
            return fail(f"scenario {scenario_id} has measured evidence in a planned suite")
        criteria = item["acceptance_criteria"]
        if not isinstance(criteria, list) or not criteria or any(not isinstance(x, str) or not x.strip() for x in criteria):
            return fail(f"scenario {scenario_id} must have non-empty string acceptance_criteria")

    too_few = {key: counts[key] for key, minimum in REQUIRED_CLASSES.items() if counts[key] < minimum}
    if too_few:
        return fail(f"decision-variance scenario coverage below minimum: {too_few}")

    print("PASS: decision-variance contract is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
