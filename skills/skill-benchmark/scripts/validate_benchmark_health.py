#!/usr/bin/env python3
"""Validate benchmark-suite health evidence independently of candidate performance."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from _common import dump_json

SHA_RE = re.compile(r"^[0-9a-f]{64}$")
SUITE_ROLES = {"diagnostic", "capability", "regression", "holdout"}
DISTRIBUTIONS = {"diagnostic-balanced", "production-representative", "custom"}
CHECK_STATES = {"pass", "review", "fail", "not-run"}
GRADER_TYPES = {"deterministic", "llm", "human", "mixed"}
SATURATION = {"active", "near-saturated", "saturated", "unknown"}
CONTAMINATION = {"low", "medium", "high", "unknown"}


def _valid_sha(value: Any) -> bool:
    return isinstance(value, str) and bool(SHA_RE.fullmatch(value))


def validate(data: Any) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(data, dict):
        return {"status": "fail", "errors": ["health evidence must be an object"], "warnings": [], "gate": "fail"}
    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if not _valid_sha(data.get("scenario_suite_sha256")):
        errors.append("scenario_suite_sha256 must be lowercase 64-hex")
    if data.get("suite_role") not in SUITE_ROLES:
        errors.append(f"suite_role must be one of {sorted(SUITE_ROLES)}")
    if data.get("distribution_profile") not in DISTRIBUTIONS:
        errors.append(f"distribution_profile must be one of {sorted(DISTRIBUTIONS)}")
    for field in ("isolation_status", "gaming_resistance"):
        if data.get(field) not in CHECK_STATES:
            errors.append(f"{field} must be one of {sorted(CHECK_STATES)}")
    if data.get("contamination_risk") not in CONTAMINATION:
        errors.append(f"contamination_risk must be one of {sorted(CONTAMINATION)}")
    if data.get("saturation_state") not in SATURATION:
        errors.append(f"saturation_state must be one of {sorted(SATURATION)}")
    dist_evidence = data.get("distribution_evidence_status", "not-run")
    if dist_evidence not in CHECK_STATES:
        errors.append("distribution_evidence_status has invalid value")

    grader = data.get("grader")
    if not isinstance(grader, dict):
        errors.append("grader must be an object")
        grader = {}
    grader_type = grader.get("type")
    if grader_type not in GRADER_TYPES:
        errors.append(f"grader.type must be one of {sorted(GRADER_TYPES)}")
    correctness = grader.get("correctness_status")
    if correctness not in CHECK_STATES:
        errors.append("grader.correctness_status has invalid value")
    calibration = grader.get("calibration_status", "not-run")
    if calibration not in CHECK_STATES:
        errors.append("grader.calibration_status has invalid value")
    if grader_type in {"llm", "mixed"}:
        if calibration == "pass" and not _valid_sha(grader.get("calibration_set_sha256")):
            errors.append("grader.calibration_set_sha256 is required when model-grader calibration_status=pass")
        agreement = grader.get("human_agreement")
        if agreement is not None and (not isinstance(agreement, (int, float)) or isinstance(agreement, bool) or not 0 <= agreement <= 1):
            errors.append("grader.human_agreement must be in 0..1 when present")
        for field in ("position_balanced", "length_controlled", "abstention_supported"):
            if field in grader and not isinstance(grader[field], bool):
                errors.append(f"grader.{field} must be boolean when present")

    tasks = data.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        errors.append("tasks must be a non-empty array")
        tasks = []
    seen: set[str] = set()
    task_failures = 0
    task_reviews = 0
    for index, task in enumerate(tasks):
        if not isinstance(task, dict):
            errors.append(f"task[{index}] must be an object")
            continue
        tid = task.get("id")
        if not isinstance(tid, str) or not tid.strip():
            errors.append(f"task[{index}].id must be non-empty")
        elif tid in seen:
            errors.append(f"duplicate task id: {tid}")
        else:
            seen.add(tid)
        for field in ("reference_solution_status", "grader_status", "ambiguity_status"):
            state = task.get(field)
            if state not in CHECK_STATES:
                errors.append(f"{tid or index}.{field} has invalid value")
            elif state == "fail":
                task_failures += 1
            elif state in {"review", "not-run"}:
                task_reviews += 1
        flaky = task.get("flakiness_rate")
        if flaky is not None and (not isinstance(flaky, (int, float)) or isinstance(flaky, bool) or not 0 <= flaky <= 1):
            errors.append(f"{tid or index}.flakiness_rate must be null or in 0..1")
        elif isinstance(flaky, (int, float)) and flaky > 0.05:
            task_reviews += 1

    if errors:
        gate = "fail"
    else:
        hard_fail = (
            task_failures > 0
            or data.get("isolation_status") == "fail"
            or data.get("gaming_resistance") == "fail"
            or data.get("contamination_risk") == "high"
            or correctness == "fail"
            or calibration == "fail"
        )
        review = (
            task_reviews > 0
            or data.get("isolation_status") in {"review", "not-run"}
            or data.get("gaming_resistance") in {"review", "not-run"}
            or data.get("contamination_risk") in {"medium", "unknown"}
            or correctness in {"review", "not-run"}
            or (grader_type in {"llm", "mixed"} and calibration in {"review", "not-run"})
            or (data.get("distribution_profile") == "production-representative" and dist_evidence != "pass")
            or (data.get("suite_role") == "capability" and data.get("saturation_state") in {"near-saturated", "saturated", "unknown"})
        )
        gate = "fail" if hard_fail else ("review" if review else "pass")
    strong_claim_eligible = gate == "pass"
    if data.get("distribution_profile") == "diagnostic-balanced":
        warnings.append("diagnostic-balanced suites support diagnostic metrics, not production prevalence claims")
    if data.get("suite_role") == "capability" and data.get("saturation_state") == "saturated":
        warnings.append("saturated capability suite should be refreshed or graduated to regression use")
    return {
        "status": "fail" if errors else "pass",
        "gate": gate,
        "strong_claim_eligible": strong_claim_eligible,
        "errors": errors,
        "warnings": warnings,
        "checks": {
            "task_count": len(tasks),
            "task_failures": task_failures,
            "task_reviews": task_reviews,
            "suite_role": data.get("suite_role"),
            "distribution_profile": data.get("distribution_profile"),
            "saturation_state": data.get("saturation_state"),
            "contamination_risk": data.get("contamination_risk"),
            "grader_type": grader_type,
            "grader_calibration_status": calibration,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--health", required=True)
    parser.add_argument("--json-output")
    args = parser.parse_args()
    try:
        data = json.loads(Path(args.health).read_text(encoding="utf-8"))
        report = validate(data)
    except Exception as exc:
        report = {"status": "fail", "gate": "fail", "errors": [str(exc)], "warnings": []}
    dump_json(report, args.json_output)
    if args.json_output:
        dump_json(report)
    return 1 if report.get("status") == "fail" or report.get("gate") == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
