#!/usr/bin/env python3
"""Validate Magiarca activation scenario coverage."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

REQUIRED_CATEGORIES = [
    "should_activate",
    "should_not_activate",
    "ambiguous",
    "edge_case",
    "regression",
    "adversarial",
]
MIN_PER_CATEGORY = 5
CATEGORY_PREFIXES = {
    "should_activate": "A",
    "should_not_activate": "N",
    "ambiguous": "B",
    "edge_case": "E",
    "regression": "R",
    "adversarial": "X",
}

REQUIRED_BOUNDARY_TERMS = {
    "implementation": ["implement", "code", "unit test", "tests"],
    "mago": ["mago", "prd", "tasks"],
    "magia": ["magia", "execution"],
    "deployment": ["deploy", "deployment", "rollout"],
    "source_control": ["pull request", "commit", "branch"],
    "missing_inputs": ["missing", "absent", "unknown", "not known"],
    "path_boundary": ["outside", "path", "board root"],
    "evidence_invention": ["invent", "assume", "without evidence"],
}


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValueError(f"cannot read valid JSON from {path}: {exc}") from exc


def has_boundary(text: str, terms: list[str]) -> bool:
    lowered = text.lower()
    return any(term in lowered for term in terms)


def validate(path: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    data = load_json(path)
    if not isinstance(data, list):
        return {
            "status": "fail",
            "errors": ["scenario file must contain a JSON list"],
            "warnings": [],
            "counts": {},
            "activation_labels": {},
            "boundary_coverage": {},
        }

    counts: Counter[str] = Counter()
    labels: Counter[str] = Counter()
    seen_ids: set[str] = set()
    seen_prompts: set[str] = set()
    boundary_blob_parts: list[str] = []

    for index, item in enumerate(data):
        if not isinstance(item, dict):
            errors.append(f"scenario {index} must be an object")
            continue
        scenario_id = item.get("id")
        category = item.get("category")
        prompt = item.get("prompt")
        expected_activation = item.get("expected_activation")
        expected_behavior = item.get("expected_behavior")
        notes = item.get("notes")

        if not isinstance(scenario_id, str) or not re.fullmatch(r"[A-Z][A-Z0-9]*\d{3}", scenario_id):
            errors.append(f"scenario {index} has invalid id: {scenario_id!r}")
        elif scenario_id in seen_ids:
            errors.append(f"duplicate scenario id: {scenario_id}")
        else:
            seen_ids.add(scenario_id)

        if category not in REQUIRED_CATEGORIES:
            errors.append(f"scenario {scenario_id or index} has invalid category: {category!r}")
        else:
            counts[category] += 1
            expected_prefix = CATEGORY_PREFIXES[category]
            if isinstance(scenario_id, str) and not scenario_id.startswith(expected_prefix):
                errors.append(f"scenario {scenario_id or index} id must start with {expected_prefix} for category {category}")

        if not isinstance(prompt, str) or len(prompt.strip()) < 20:
            errors.append(f"scenario {scenario_id or index} prompt is too short")
        else:
            normalized_prompt = " ".join(prompt.lower().split())
            if normalized_prompt in seen_prompts:
                errors.append(f"scenario {scenario_id or index} duplicates an earlier prompt")
            seen_prompts.add(normalized_prompt)
        if not isinstance(expected_behavior, str) or len(expected_behavior.strip()) < 30:
            errors.append(f"scenario {scenario_id or index} expected_behavior is too short")
        if not isinstance(notes, str) or len(notes.strip()) < 3:
            errors.append(f"scenario {scenario_id or index} notes must describe the scenario purpose")

        if expected_activation not in (True, False, None):
            errors.append(f"scenario {scenario_id or index} expected_activation must be true, false, or null")
        else:
            labels[str(expected_activation).lower() if expected_activation is not None else "null"] += 1

        if category == "should_activate" and expected_activation is not True:
            errors.append(f"scenario {scenario_id or index} should_activate must expect activation true")
        if category == "should_not_activate" and expected_activation is not False:
            errors.append(f"scenario {scenario_id or index} should_not_activate must expect activation false")
        if category == "ambiguous" and expected_activation is not None:
            errors.append(f"scenario {scenario_id or index} ambiguous must expect activation null")
        if category in {"edge_case", "regression", "adversarial"} and expected_activation is False:
            warnings.append(f"scenario {scenario_id or index} is {category} with false activation; confirm it is not a should_not_activate case")

        boundary_blob_parts.extend(str(value) for value in [prompt, expected_behavior, notes] if isinstance(value, str))

    for category in REQUIRED_CATEGORIES:
        if counts[category] < MIN_PER_CATEGORY:
            errors.append(f"category {category} has {counts[category]}; expected at least {MIN_PER_CATEGORY}")

    boundary_blob = "\n".join(boundary_blob_parts)
    boundary_coverage = {name: has_boundary(boundary_blob, terms) for name, terms in REQUIRED_BOUNDARY_TERMS.items()}
    for name, covered in boundary_coverage.items():
        if not covered:
            warnings.append(f"boundary coverage not found: {name}")

    if not labels.get("true") or not labels.get("false") or not labels.get("null"):
        errors.append("expected_activation labels must include true, false, and null")

    return {
        "status": "pass" if not errors else "fail",
        "scenario_count": len(data),
        "errors": errors,
        "warnings": warnings,
        "counts": {category: counts[category] for category in REQUIRED_CATEGORIES},
        "activation_labels": dict(labels),
        "boundary_coverage": boundary_coverage,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Magiarca activation scenario coverage.")
    parser.add_argument("scenario_file", nargs="?", default=str(Path(__file__).resolve().parents[1] / "examples" / "activation-scenarios.json"))
    parser.add_argument("--json-output", help="Optional path for machine-readable results.")
    args = parser.parse_args(argv)

    try:
        result = validate(Path(args.scenario_file).resolve())
    except ValueError as exc:
        result = {
            "status": "fail",
            "errors": [str(exc)],
            "warnings": [],
            "counts": {},
            "activation_labels": {},
            "boundary_coverage": {},
        }

    if args.json_output:
        output = Path(args.json_output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"status: {result['status']}")
    print(f"scenario_count: {result.get('scenario_count', 0)}")
    for category, count in result.get("counts", {}).items():
        print(f"category {category}: {count}")
    for error in result.get("errors", []):
        print(f"ERROR: {error}")
    for warning in result.get("warnings", []):
        print(f"WARNING: {warning}")
    return 0 if result.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
