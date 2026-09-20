#!/usr/bin/env python3
"""Validate the frozen MAGIA booster activation corpus as structural evidence only."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ALLOWED_CATEGORIES = {"should_activate", "should_not_activate", "ambiguous", "edge_case"}
REQUIRED_FIELDS = {"id", "type", "category", "prompt", "expected_behavior", "acceptance_criteria"}
DEFAULT_RELATIVE_SUITE = "evals/booster-activation-scenarios.json"

REQUIRED_ACCEPTANCE_MARKERS = {
    "classification matches MAGIA scope",
    "authority boundaries remain intact",
    "validation evidence is not fabricated",
}


def _read(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, [f"missing booster activation scenario suite: {path}"]
    except Exception as exc:  # noqa: BLE001
        return None, [f"booster activation scenario suite is invalid JSON: {exc}"]
    if not isinstance(payload, dict):
        return None, ["booster activation scenario suite root must be an object"]
    return payload, []


def validate(path: Path) -> dict[str, Any]:
    path = path.resolve()
    payload, errors = _read(path)
    category_counts = {category: 0 for category in sorted(ALLOWED_CATEGORIES)}
    seen: set[str] = set()
    scenarios: list[Any] = []
    if payload is not None:
        raw = payload.get("scenarios")
        if not isinstance(raw, list) or not raw:
            errors.append("booster activation scenario suite must contain a non-empty scenarios array")
        else:
            scenarios = raw
            for index, scenario in enumerate(scenarios):
                if not isinstance(scenario, dict):
                    errors.append(f"scenario at index {index} must be an object")
                    continue
                sid = scenario.get("id") or f"index {index}"
                missing = REQUIRED_FIELDS - set(scenario)
                if missing:
                    errors.append(f"scenario {sid} missing fields: {sorted(missing)}")
                if not isinstance(scenario.get("id"), str) or not scenario.get("id", "").strip():
                    errors.append(f"scenario {sid} must have a non-empty string id")
                elif scenario["id"] in seen:
                    errors.append(f"duplicate scenario id: {scenario['id']}")
                else:
                    seen.add(scenario["id"])
                category = scenario.get("category")
                stype = scenario.get("type")
                if category not in ALLOWED_CATEGORIES:
                    errors.append(f"scenario {sid} has invalid category: {category}")
                else:
                    category_counts[category] += 1
                if stype != category:
                    errors.append(f"scenario {sid} type/category mismatch: {stype} != {category}")
                if not isinstance(scenario.get("prompt"), str) or not scenario.get("prompt", "").strip():
                    errors.append(f"scenario {sid} must have a non-empty prompt")
                if not isinstance(scenario.get("expected_behavior"), str) or not scenario.get("expected_behavior", "").strip():
                    errors.append(f"scenario {sid} must have non-empty expected_behavior")
                criteria = scenario.get("acceptance_criteria")
                if not isinstance(criteria, list) or not criteria or not all(isinstance(item, str) and item.strip() for item in criteria):
                    errors.append(f"scenario {sid} must have non-empty string acceptance_criteria")
                else:
                    missing_markers = sorted(REQUIRED_ACCEPTANCE_MARKERS - set(criteria))
                    if missing_markers:
                        errors.append(f"scenario {sid} missing acceptance markers: {missing_markers}")
    missing_categories = sorted(category for category, count in category_counts.items() if count == 0)
    if missing_categories:
        errors.append(f"booster activation suite missing required categories: {missing_categories}")

    sha256 = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
    return {
        "status": "pass" if not errors else "fail",
        "evidence_kind": "structural_scenario_validation",
        "behavior_measured": False,
        "scenario_count": len(scenarios),
        "category_counts": category_counts,
        "suite_sha256": sha256,
        "errors": errors,
        "limitations": [
            "This gate validates corpus structure and authority/evidence invariants only.",
            "Activation precision, recall, output conformance, and adversarial robustness require independent live-model observations.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        default=str(Path(__file__).resolve().parents[1] / DEFAULT_RELATIVE_SUITE),
    )
    parser.add_argument("--json-output")
    args = parser.parse_args(argv)
    result = validate(Path(args.input))
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.json_output:
        output = Path(args.json_output).resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
