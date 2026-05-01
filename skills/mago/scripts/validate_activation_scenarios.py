#!/usr/bin/env python3
"""Validate MAGO activation and boundary scenarios with deterministic routing checks."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

REQUIRED_MODES = {
    "adapt",
    "define-product",
    "define-tasks",
    "define",
    "discovery",
    "order",
    "prepare-define",
    "refine-product",
    "refine-tasks",
    "refine",
    "reshape-tasks",
    "technical-design",
    "complexity-reduction",
}
REQUIRED_KEYS = {"id", "case_type", "prompt", "expected_activation", "expected_mode", "expected_boundary"}
CASE_TYPES = {"should_activate", "should_not_activate", "ambiguous", "edge_case", "regression", "adversarial"}
NEGATED_EXECUTION_PATTERNS = (
    "without implement",
    "do not implement",
    "not implement",
    "without running tests",
    "do not run tests",
    "not run tests",
    "without runtime evidence",
    "do not claim runtime evidence",
    "do not run tests or claim runtime evidence",
    "keep implementation tasks out",
    "implementation plan at approach level",
    "do not collect runtime evidence",
    "without product code",
    "do not change product code",
)
GOVERNANCE_TERMS = ("release notes", "stakeholder", "delivery status", "governance", "portfolio reporting")
EXECUTION_TERMS = (
    "implement",
    "implementation diff",
    "implementation code",
    "run tests",
    "execute task",
    "deploy",
    "runtime evidence",
    "product code",
    "mark validation evidence as complete",
)


def load_suite(root: Path) -> dict[str, Any]:
    path = root / "examples" / "activation-scenarios.json"
    return json.loads(path.read_text(encoding="utf-8"))


def has_any(text: str, terms: tuple[str, ...]) -> bool:
    return any(term in text for term in terms)


def has_execution_request(text: str) -> bool:
    if any(pattern in text for pattern in NEGATED_EXECUTION_PATTERNS):
        sanitized = text
        for pattern in sorted(NEGATED_EXECUTION_PATTERNS, key=len, reverse=True):
            sanitized = sanitized.replace(pattern, "")
        return has_any(sanitized, EXECUTION_TERMS)
    return has_any(text, EXECUTION_TERMS) or bool(re.search(r"\bimplement\b", text))


def classify_prompt(prompt: str) -> tuple[bool | str, str | None]:
    text = " ".join(prompt.lower().replace("-", " ").split())
    if has_execution_request(text) or has_any(text, GOVERNANCE_TERMS):
        return False, None
    if "technical design" in text or ("architecture" in text and "spec" in text):
        return True, "technical-design"

    if ("complexity reduction" in text or "simplification" in text or "simplify" in text or "de abstract" in text or "de abstraction" in text or "unnecessary abstraction" in text or "over engineered" in text or "overengineered" in text or "refactoring plan" in text) and ("plan" in text or "spec" in text or "strategy" in text or "technical" in text or "create" in text):
        return True, "complexity-reduction"
    if "reshape" in text and "task" in text:
        return True, "reshape-tasks"
    product_only = "product only" in text or "product documentation" in text or "product docs" in text
    task_only = "task only" in text or "tasks.md" in text or "task planning only" in text
    if task_only and "refine" in text:
        return True, "refine-tasks"
    if task_only and "define" in text:
        return True, "define-tasks"
    if product_only and "refine" in text:
        return True, "refine-product"
    if product_only and "define" in text:
        return True, "define-product"
    if "refine" in text and "task" in text and "product" not in text:
        return True, "refine-tasks"
    if "define" in text and "task" in text and "product" not in text:
        return True, "define-tasks"
    if "refine" in text and "product" in text:
        return True, "refine-product"
    if "define" in text and "product" in text:
        return True, "define-product"
    if "seed" in text and ("define" in text or "package shell" in text or "shells" in text):
        return True, "prepare-define"
    if "prepare define" in text:
        return True, "prepare-define"
    if "order" in text or "backlog" in text or "define queue" in text:
        return True, "order"
    if "discover" in text or "discovery" in text:
        return True, "discovery"
    if "adapt" in text or "legacy" in text or "drift" in text:
        return True, "adapt"
    if "refine" in text and "package" in text:
        return True, "refine"
    if "define" in text and ("spec" in text or "package" in text):
        return True, "define"
    if "docs" in text or "documentation" in text or "planning" in text or "package" in text or "roadmap" in text:
        return "ambiguous", None
    return "ambiguous", None


def validate(root: Path) -> dict[str, Any]:
    errors: list[str] = []
    scenario_results: list[dict[str, Any]] = []
    try:
        payload = load_suite(root)
    except FileNotFoundError:
        return {"status": "fail", "errors": ["missing examples/activation-scenarios.json"]}
    except json.JSONDecodeError as exc:
        return {"status": "fail", "errors": [f"invalid activation scenario JSON: {exc}"]}

    scenarios = payload.get("scenarios")
    if not isinstance(scenarios, list):
        return {"status": "fail", "errors": ["scenarios must be a list"]}

    seen_ids: set[str] = set()
    expected_modes: set[str] = set()
    activation_matches = 0
    mode_matches = 0
    boundary_cases = {"positive": 0, "negative": 0, "ambiguous": 0}
    case_types = {case_type: 0 for case_type in sorted(CASE_TYPES)}

    for index, scenario in enumerate(scenarios, start=1):
        if not isinstance(scenario, dict):
            errors.append(f"scenario {index} must be an object")
            continue
        missing = REQUIRED_KEYS - set(scenario)
        if missing:
            errors.append(f"scenario {index} missing keys: {sorted(missing)}")
            continue
        scenario_id = scenario["id"]
        if scenario_id in seen_ids:
            errors.append(f"duplicate scenario id: {scenario_id}")
        seen_ids.add(scenario_id)
        case_type = scenario["case_type"]
        if case_type not in CASE_TYPES:
            errors.append(f"{scenario_id}: unsupported case_type {case_type!r}")
        else:
            case_types[case_type] += 1
        prompt = scenario["prompt"]
        expected_activation = scenario["expected_activation"]
        expected_mode = scenario["expected_mode"]
        expected_boundary = scenario["expected_boundary"]
        if expected_mode is not None:
            expected_modes.add(expected_mode)
        if expected_activation is True:
            boundary_cases["positive"] += 1
        elif expected_activation is False:
            boundary_cases["negative"] += 1
        elif expected_activation == "ambiguous":
            boundary_cases["ambiguous"] += 1
        else:
            errors.append(f"{scenario_id}: expected_activation must be true, false, or ambiguous")
        if not isinstance(expected_boundary, str) or len(expected_boundary.split()) < 4:
            errors.append(f"{scenario_id}: expected_boundary is too vague")
        actual_activation, actual_mode = classify_prompt(str(prompt))
        activation_ok = actual_activation == expected_activation
        mode_ok = actual_mode == expected_mode
        if activation_ok:
            activation_matches += 1
        if mode_ok:
            mode_matches += 1
        if not activation_ok:
            errors.append(f"{scenario_id}: activation mismatch expected={expected_activation!r} actual={actual_activation!r}")
        if not mode_ok:
            errors.append(f"{scenario_id}: mode mismatch expected={expected_mode!r} actual={actual_mode!r}")
        scenario_results.append(
            {
                "id": scenario_id,
                "case_type": case_type,
                "expected_activation": expected_activation,
                "actual_activation": actual_activation,
                "expected_mode": expected_mode,
                "actual_mode": actual_mode,
                "activation_ok": activation_ok,
                "mode_ok": mode_ok,
            }
        )

    missing_modes = sorted(REQUIRED_MODES - expected_modes)
    if missing_modes:
        errors.append(f"activation suite does not cover modes: {missing_modes}")
    for case_name, count in boundary_cases.items():
        if count == 0:
            errors.append(f"activation suite missing {case_name} boundary case")
    minimum_case_counts = {"should_activate": 5, "should_not_activate": 5, "ambiguous": 5, "edge_case": 3, "regression": 2, "adversarial": 2}
    for case_name, minimum in minimum_case_counts.items():
        if case_types.get(case_name, 0) < minimum:
            errors.append(f"activation suite needs at least {minimum} {case_name} scenarios, found {case_types.get(case_name, 0)}")

    total = len(scenario_results)
    metrics = {
        "scenario_count": total,
        "activation_accuracy": activation_matches / total if total else 0.0,
        "mode_accuracy": mode_matches / total if total else 0.0,
        "covered_modes": sorted(expected_modes),
        "boundary_cases": boundary_cases,
        "case_types": case_types,
        "measurement_kind": "deterministic_static_oracle",
    }
    return {
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "metrics": metrics,
        "results": scenario_results,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate MAGO activation scenario routing and coverage.")
    parser.add_argument("target", nargs="?", default=str(Path(__file__).resolve().parents[1]), help="MAGO skill root")
    parser.add_argument("--json-output", help="Optional path for a JSON report")
    args = parser.parse_args(argv)

    root = Path(args.target).resolve()
    report = validate(root)
    if args.json_output:
        output = Path(args.json_output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"wrote {output}")
    metrics = report.get("metrics", {})
    print(f"status: {report['status']}")
    if metrics:
        print(f"scenario_count: {metrics.get('scenario_count')}")
        print(f"activation_accuracy: {metrics.get('activation_accuracy'):.3f}")
        print(f"mode_accuracy: {metrics.get('mode_accuracy'):.3f}")
        print(f"measurement_kind: {metrics.get('measurement_kind')}")
    for error in report.get("errors", []):
        print(f"error: {error}")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
