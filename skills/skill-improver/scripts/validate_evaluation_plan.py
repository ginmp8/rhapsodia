#!/usr/bin/env python3
"""Validate the portable Skill Improver evaluation-plan contract."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

VALID_CLAIMS = {"repair", "hardening", "behavioral-improvement", "reliability-improvement"}
VALID_VISIBILITY = {"mutator-visible", "read-only", "controller-only"}
VALID_KINDS = {"hard-gate", "optimize"}
VALID_DIRECTIONS = {"higher-is-better", "lower-is-better"}
REQUIRED_PARTITIONS = {
    "diagnostic": "mutator-visible",
    "regression": "read-only",
    "promotion_holdout": "controller-only",
}
REQUIRED_HARD_GATES = {"activation", "safety", "compatibility"}
REQUIRED_RUNTIME_FIELDS = {"model", "host_or_harness", "toolset", "environment"}
REQUIRED_CAPABILITY_SURFACES = {"network", "filesystem_write", "secrets", "external_tools"}


def _obj(value: Any, subject: str, errors: list[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(f"{subject}:expected-object")
        return {}
    return value


def validate_plan(data: Any) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(data, dict):
        return {"status": "fail", "errors": ["root:expected-object"], "warnings": []}

    if data.get("plan_version") != 1:
        errors.append("plan_version:expected-1")
    claim = data.get("claim")
    if claim not in VALID_CLAIMS:
        errors.append("claim:invalid")

    arms = _obj(data.get("arms"), "arms", errors)
    for name in ("parent", "candidate"):
        arm = _obj(arms.get(name), f"arms.{name}", errors)
        if arm.get("enabled") is not True:
            errors.append(f"arms.{name}.enabled:must-be-true")
    no_skill = _obj(arms.get("no_skill"), "arms.no_skill", errors)
    if claim in {"behavioral-improvement", "reliability-improvement"} and no_skill.get("enabled") is not True:
        errors.append("arms.no_skill.enabled:required-for-improvement-claim")

    partitions = _obj(data.get("partitions"), "partitions", errors)
    for name, expected_visibility in REQUIRED_PARTITIONS.items():
        partition = _obj(partitions.get(name), f"partitions.{name}", errors)
        visibility = partition.get("visibility")
        if visibility not in VALID_VISIBILITY:
            errors.append(f"partitions.{name}.visibility:invalid")
        elif visibility != expected_visibility:
            errors.append(f"partitions.{name}.visibility:expected-{expected_visibility}")

    dimensions = data.get("dimensions")
    dimension_ids: set[str] = set()
    hard_gates: set[str] = set()
    optimize_count = 0
    if not isinstance(dimensions, list) or not dimensions:
        errors.append("dimensions:expected-non-empty-list")
    else:
        for idx, raw in enumerate(dimensions):
            item = _obj(raw, f"dimensions[{idx}]", errors)
            did = item.get("id")
            if not isinstance(did, str) or not did.strip():
                errors.append(f"dimensions[{idx}].id:required")
                continue
            if did in dimension_ids:
                errors.append(f"dimensions[{idx}].id:duplicate:{did}")
            dimension_ids.add(did)
            kind = item.get("kind")
            if kind not in VALID_KINDS:
                errors.append(f"dimensions[{idx}].kind:invalid")
            if kind == "hard-gate":
                hard_gates.add(did)
            if kind == "optimize":
                optimize_count += 1
                if item.get("direction") not in VALID_DIRECTIONS:
                    errors.append(f"dimensions[{idx}].direction:invalid")
    missing_hard_gates = sorted(REQUIRED_HARD_GATES - hard_gates)
    if missing_hard_gates:
        errors.append("dimensions:missing-hard-gates:" + ",".join(missing_hard_gates))
    if optimize_count == 0:
        errors.append("dimensions:at-least-one-optimize-dimension-required")

    stochastic = _obj(data.get("stochastic"), "stochastic", errors)
    strong_claim = stochastic.get("strong_claim") is True
    trials = stochastic.get("trials_per_case")
    if strong_claim and (not isinstance(trials, int) or isinstance(trials, bool) or trials < 2):
        errors.append("stochastic.trials_per_case:must-be-at-least-2-for-strong-claim")
    reliability = stochastic.get("binary_reliability_metrics")
    if strong_claim and isinstance(reliability, list):
        missing = {"pass@k", "pass^k"} - {str(x) for x in reliability}
        if missing:
            warnings.append("stochastic.binary_reliability_metrics:missing:" + ",".join(sorted(missing)))

    runtime = _obj(data.get("runtime_identity"), "runtime_identity", errors)
    runtime_fields = runtime.get("fields")
    if runtime.get("required_when_material") is not True:
        errors.append("runtime_identity.required_when_material:must-be-true")
    if not isinstance(runtime_fields, list):
        errors.append("runtime_identity.fields:expected-list")
    else:
        missing = REQUIRED_RUNTIME_FIELDS - {str(x) for x in runtime_fields}
        if missing:
            errors.append("runtime_identity.fields:missing:" + ",".join(sorted(missing)))

    capability = _obj(data.get("capability_delta"), "capability_delta", errors)
    if capability.get("required") is not True:
        errors.append("capability_delta.required:must-be-true")
    surfaces = capability.get("surfaces")
    if not isinstance(surfaces, list):
        errors.append("capability_delta.surfaces:expected-list")
    else:
        missing = REQUIRED_CAPABILITY_SURFACES - {str(x) for x in surfaces}
        if missing:
            errors.append("capability_delta.surfaces:missing:" + ",".join(sorted(missing)))
    if capability.get("new_authority_requires_explicit_authorization") is not True:
        errors.append("capability_delta.new_authority_requires_explicit_authorization:must-be-true")

    contamination = _obj(data.get("contamination"), "contamination", errors)
    if contamination.get("status") not in {"unassessed", "clear", "suspected", "confirmed"}:
        errors.append("contamination.status:invalid")
    if contamination.get("holdout_access_evidence_required_for_promotion") is not True:
        errors.append("contamination.holdout_access_evidence_required_for_promotion:must-be-true")

    acceptance = _obj(data.get("acceptance"), "acceptance", errors)
    for field in (
        "require_all_hard_gates",
        "require_no_new_capability_without_authorization",
        "require_promotion_holdout_for_behavioral_promotion",
        "scalar_score_is_not_sufficient",
    ):
        if acceptance.get(field) is not True:
            errors.append(f"acceptance.{field}:must-be-true")

    return {
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "warnings": warnings,
        "summary": {
            "claim": claim,
            "arms": sorted(arms.keys()) if isinstance(arms, dict) else [],
            "dimension_ids": sorted(dimension_ids),
            "hard_gates": sorted(hard_gates),
            "strong_stochastic_claim": strong_claim,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Skill Improver evaluation-plan JSON.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.input.read_text(encoding="utf-8"))
        result = validate_plan(data)
    except Exception as exc:
        result = {"status": "fail", "errors": [f"input:{exc}"], "warnings": []}
    payload = json.dumps(result, indent=2, sort_keys=True)
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 0 if result.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
