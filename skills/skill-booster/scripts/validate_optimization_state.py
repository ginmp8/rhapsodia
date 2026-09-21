#!/usr/bin/env python3
"""Validate Skill Booster optimization state artifacts.

This validates canonical optimization-state interchange shape and cross-artifact identity/reference integrity. It does
not score semantic quality, require evolutionary search state, or prove behavioral improvement.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

TARGET_CLASSES = {
    "deterministic-tool", "code-engineering", "research-analytic",
    "orchestration-meta", "subjective-design", "mixed-other",
}
CAPABILITY_KINDS = {
    "activation", "behavior", "validation", "delivery", "governance",
    "portability", "evidence", "architecture", "documentation", "security", "other",
}
CAPABILITY_STATUS = {"current", "unknown", "blocked", "deprecated", "migration-only"}
CHANGE_INTENTS = {"repair", "optimization", "experiment"}
TRANSFORMATION_STATUS = {"planned", "applied", "accepted", "rejected", "reverted"}
EVAL_LEVELS = {
    "L0-structural", "L1-deterministic", "L2-focused",
    "L3-harness", "L4-benchmark", "L5-holdout",
}
EVAL_STATUS = {"planned", "pass", "fail", "blocked", "not-run", "not-applicable"}
EXPERIMENT_RESULTS = {"planned", "pass", "fail", "inconclusive", "rejected", "accepted"}
EXPERIMENT_DECISIONS = {"pending", "accept", "reject", "repair", "gather-evidence", "stop"}
GATE_STATUS = {"planned", "pass", "pass-with-warnings", "fail", "blocked", "insufficient-evidence", "not-run"}
FINALIST_HOLDOUT_POLICIES = {"not-required", "blind-pass-required"}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require(cond: bool, errors: list[str], code: str, message: str) -> None:
    if not cond:
        errors.append(f"[{code}] {message}")


def nonempty_str(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def string_list(value: Any) -> bool:
    return isinstance(value, list) and all(nonempty_str(x) for x in value)


def validate_capability_map(data: Any) -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []
    require(isinstance(data, dict), errors, "ROOT", "capability map must be an object")
    if not isinstance(data, dict):
        return errors, {}
    require(data.get("schema_version") == 1, errors, "SCHEMA", "capability map schema_version must be 1")
    target = data.get("target")
    require(isinstance(target, dict), errors, "TARGET", "capability map target must be an object")
    if isinstance(target, dict):
        require(nonempty_str(target.get("name")), errors, "TARGET_NAME", "target.name is required")
        require(nonempty_str(target.get("identity")), errors, "TARGET_ID", "target.identity is required")
        require(target.get("class") in TARGET_CLASSES, errors, "TARGET_CLASS", "target.class is invalid")
    caps = data.get("capabilities")
    require(isinstance(caps, list), errors, "CAP_LIST", "capabilities must be a list")
    ids: set[str] = set()
    if isinstance(caps, list):
        for i, cap in enumerate(caps):
            subject = f"capabilities[{i}]"
            require(isinstance(cap, dict), errors, "CAP_TYPE", f"{subject} must be an object")
            if not isinstance(cap, dict):
                continue
            cid = cap.get("id")
            require(nonempty_str(cid), errors, "CAP_ID", f"{subject}.id is required")
            if nonempty_str(cid):
                require(cid not in ids, errors, "CAP_DUP", f"duplicate capability id {cid}")
                ids.add(cid)
            require(nonempty_str(cap.get("name")), errors, "CAP_NAME", f"{subject}.name is required")
            require(cap.get("kind") in CAPABILITY_KINDS, errors, "CAP_KIND", f"{subject}.kind is invalid")
            require(nonempty_str(cap.get("owner")), errors, "CAP_OWNER", f"{subject}.owner is required")
            require(cap.get("status") in CAPABILITY_STATUS, errors, "CAP_STATUS", f"{subject}.status is invalid")
            for field in ("resources", "consumers", "validators", "evidence_refs", "invariants"):
                require(string_list(cap.get(field)), errors, "CAP_LIST_FIELD", f"{subject}.{field} must be a list of non-empty strings")
    return errors, {"target_identity": target.get("identity") if isinstance(target, dict) else None, "capability_ids": ids}


def validate_transformations(data: Any) -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []
    require(isinstance(data, dict), errors, "ROOT", "transformation registry must be an object")
    if not isinstance(data, dict):
        return errors, {}
    require(data.get("schema_version") == 1, errors, "SCHEMA", "transformation registry schema_version must be 1")
    target_identity = data.get("target_identity")
    require(nonempty_str(target_identity), errors, "TARGET_ID", "target_identity is required")
    items = data.get("transformations")
    require(isinstance(items, list), errors, "TRANSFORM_LIST", "transformations must be a list")
    ids: set[str] = set()
    cap_refs: set[str] = set()
    if isinstance(items, list):
        for i, item in enumerate(items):
            subject = f"transformations[{i}]"
            require(isinstance(item, dict), errors, "TRANSFORM_TYPE", f"{subject} must be an object")
            if not isinstance(item, dict):
                continue
            tid = item.get("id")
            require(nonempty_str(tid), errors, "TRANSFORM_ID", f"{subject}.id is required")
            if nonempty_str(tid):
                require(tid not in ids, errors, "TRANSFORM_DUP", f"duplicate transformation id {tid}")
                ids.add(tid)
            require(item.get("change_intent") in CHANGE_INTENTS, errors, "CHANGE_INTENT", f"{subject}.change_intent is invalid")
            require(item.get("status") in TRANSFORMATION_STATUS, errors, "TRANSFORM_STATUS", f"{subject}.status is invalid")
            for field in ("capability_refs", "files", "evaluator_refs", "depends_on", "conflicts_with", "evidence_refs"):
                require(string_list(item.get(field)), errors, "TRANSFORM_LIST_FIELD", f"{subject}.{field} must be a list of non-empty strings")
            baseline_refs = item.get("baseline_refs")
            parent_refs = item.get("parent_candidate_ids")
            require(
                string_list(baseline_refs) or string_list(parent_refs),
                errors,
                "TRANSFORM_BASELINE_REFS",
                f"{subject} requires baseline_refs (preferred) or parent_candidate_ids (compatibility)",
            )
            if baseline_refs is not None:
                require(string_list(baseline_refs), errors, "TRANSFORM_BASELINE_REFS", f"{subject}.baseline_refs must be a list of non-empty strings")
            if parent_refs is not None:
                require(string_list(parent_refs), errors, "TRANSFORM_PARENT_REFS", f"{subject}.parent_candidate_ids must be a list of non-empty strings when present")
            for field in ("capability_effects", "violates_invariants", "addresses"):
                if field in item:
                    require(string_list(item.get(field)), errors, "TRANSFORM_EVOLUTION_FIELD", f"{subject}.{field} must be a list of non-empty strings when present")
            for field in ("operation_summary", "expected_effect"):
                require(nonempty_str(item.get(field)), errors, "TRANSFORM_TEXT", f"{subject}.{field} is required")
            if string_list(item.get("capability_refs")):
                cap_refs.update(item["capability_refs"])
    return errors, {"target_identity": target_identity, "transformation_ids": ids, "capability_refs": cap_refs}


def validate_experiments(data: Any) -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []
    require(isinstance(data, dict), errors, "ROOT", "experiment registry must be an object")
    if not isinstance(data, dict):
        return errors, {}
    require(data.get("schema_version") == 1, errors, "SCHEMA", "experiment registry schema_version must be 1")
    target = data.get("target")
    require(isinstance(target, dict), errors, "TARGET", "experiment target must be an object")
    target_identity = None
    if isinstance(target, dict):
        target_identity = target.get("identity")
        require(nonempty_str(target_identity), errors, "TARGET_ID", "experiment target.identity is required")
        require(target.get("class") in TARGET_CLASSES, errors, "TARGET_CLASS", "experiment target.class is invalid")
    items = data.get("experiments")
    require(isinstance(items, list), errors, "EXPERIMENT_LIST", "experiments must be a list")
    ids: set[str] = set()
    transform_refs: set[str] = set()
    if isinstance(items, list):
        for i, item in enumerate(items):
            subject = f"experiments[{i}]"
            require(isinstance(item, dict), errors, "EXPERIMENT_TYPE", f"{subject} must be an object")
            if not isinstance(item, dict):
                continue
            eid = item.get("id")
            require(nonempty_str(eid), errors, "EXPERIMENT_ID", f"{subject}.id is required")
            if nonempty_str(eid):
                require(eid not in ids, errors, "EXPERIMENT_DUP", f"duplicate experiment id {eid}")
                ids.add(eid)
            require(string_list(item.get("parent_candidate_ids")), errors, "EXPERIMENT_PARENTS", f"{subject}.parent_candidate_ids must be a list of non-empty strings")
            require(nonempty_str(item.get("candidate_id")), errors, "CANDIDATE_ID", f"{subject}.candidate_id is required")
            require(nonempty_str(item.get("candidate_identity")), errors, "CANDIDATE_IDENTITY", f"{subject}.candidate_identity is required")
            require(string_list(item.get("transformation_ids")), errors, "TRANSFORM_REFS", f"{subject}.transformation_ids must be a list of non-empty strings")
            if string_list(item.get("transformation_ids")):
                transform_refs.update(item["transformation_ids"])
            require(nonempty_str(item.get("evaluator_identity")), errors, "EVALUATOR_ID", f"{subject}.evaluator_identity is required")
            require(nonempty_str(item.get("scenario_identity")), errors, "SCENARIO_ID", f"{subject}.scenario_identity is required")
            require(item.get("evaluation_level") in EVAL_LEVELS, errors, "EVAL_LEVEL", f"{subject}.evaluation_level is invalid")
            require(item.get("gate_status") in GATE_STATUS, errors, "GATE_STATUS", f"{subject}.gate_status is invalid")
            require(item.get("result") in EXPERIMENT_RESULTS, errors, "RESULT", f"{subject}.result is invalid")
            require(item.get("decision") in EXPERIMENT_DECISIONS, errors, "DECISION", f"{subject}.decision is invalid")
            require(isinstance(item.get("metrics"), list), errors, "METRICS", f"{subject}.metrics must be a list")
            require(string_list(item.get("evidence_refs")), errors, "EVIDENCE_REFS", f"{subject}.evidence_refs must be a list of non-empty strings")
    return errors, {"target_identity": target_identity, "experiment_ids": ids, "transformation_refs": transform_refs}


def validate_evaluation_plan(data: Any) -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []
    require(isinstance(data, dict), errors, "ROOT", "evaluation plan must be an object")
    if not isinstance(data, dict):
        return errors, {}
    require(data.get("schema_version") == 2, errors, "SCHEMA", "evaluation plan schema_version must be 2")
    target_identity = data.get("target_identity")
    require(nonempty_str(target_identity), errors, "TARGET_ID", "evaluation target_identity is required")
    levels = data.get("levels")
    require(isinstance(levels, list), errors, "LEVELS", "levels must be a list")
    seen: list[str] = []
    if isinstance(levels, list):
        for i, level in enumerate(levels):
            subject = f"levels[{i}]"
            require(isinstance(level, dict), errors, "LEVEL_TYPE", f"{subject} must be an object")
            if not isinstance(level, dict):
                continue
            lid = level.get("id")
            require(lid in EVAL_LEVELS, errors, "LEVEL_ID", f"{subject}.id is invalid")
            if lid in EVAL_LEVELS:
                require(lid not in seen, errors, "LEVEL_DUP", f"duplicate evaluation level {lid}")
                seen.append(lid)
            require(isinstance(level.get("required"), bool), errors, "LEVEL_REQUIRED", f"{subject}.required must be boolean")
            require(level.get("status") in EVAL_STATUS, errors, "LEVEL_STATUS", f"{subject}.status is invalid")
            require(string_list(level.get("checks")), errors, "LEVEL_CHECKS", f"{subject}.checks must be a list of non-empty strings")
    canonical = ["L0-structural", "L1-deterministic", "L2-focused", "L3-harness", "L4-benchmark", "L5-holdout"]
    if seen:
        indices = [canonical.index(x) for x in seen if x in canonical]
        require(indices == sorted(indices), errors, "LEVEL_ORDER", "evaluation levels must follow L0 through L5 order")
    require(isinstance(data.get("promotion"), dict), errors, "PROMOTION", "promotion must be an object")
    finalist_policy = data.get("finalist_policy")
    if finalist_policy is not None:
        require(isinstance(finalist_policy, dict), errors, "FINALIST_POLICY", "finalist_policy must be an object when present")
    if isinstance(finalist_policy, dict):
        minimum_level = finalist_policy.get("minimum_evaluation_level")
        holdout_policy = finalist_policy.get("holdout_policy")
        require(minimum_level in EVAL_LEVELS, errors, "FINALIST_LEVEL", "finalist_policy.minimum_evaluation_level is invalid")
        require(holdout_policy in FINALIST_HOLDOUT_POLICIES, errors, "FINALIST_HOLDOUT", "finalist_policy.holdout_policy is invalid")
        if minimum_level in EVAL_LEVELS and seen:
            require(minimum_level in seen, errors, "FINALIST_LEVEL", "finalist minimum evaluation level must exist in levels")
        if holdout_policy == "blind-pass-required":
            require(minimum_level == "L5-holdout", errors, "FINALIST_HOLDOUT", "blind-pass-required finalist policy requires L5-holdout")
    return errors, {"target_identity": target_identity, "levels": seen, "finalist_policy": finalist_policy}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--capability-map")
    parser.add_argument("--transformation-registry")
    parser.add_argument("--experiment-registry")
    parser.add_argument("--evaluation-plan")
    parser.add_argument("--json")
    args = parser.parse_args()

    specs = [
        ("capability_map", args.capability_map, validate_capability_map),
        ("transformation_registry", args.transformation_registry, validate_transformations),
        ("experiment_registry", args.experiment_registry, validate_experiments),
        ("evaluation_plan", args.evaluation_plan, validate_evaluation_plan),
    ]
    if not any(path for _, path, _ in specs):
        parser.error("at least one artifact path is required")

    errors: list[str] = []
    details: dict[str, Any] = {}
    identities: list[str] = []
    for name, raw_path, validator in specs:
        if not raw_path:
            continue
        path = Path(raw_path)
        try:
            data = load(path)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"[{name}/READ] {path}: {exc}")
            continue
        local_errors, meta = validator(data)
        errors.extend(f"[{name}] {e}" for e in local_errors)
        details[name] = {"path": str(path), "errors": local_errors, "meta": _jsonable(meta)}
        identity = meta.get("target_identity")
        if nonempty_str(identity):
            identities.append(identity)

    if len(set(identities)) > 1:
        errors.append(f"[CROSS_TARGET_IDENTITY] artifacts refer to different target identities: {sorted(set(identities))}")

    cap_ids = set(details.get("capability_map", {}).get("meta", {}).get("capability_ids", []))
    cap_refs = set(details.get("transformation_registry", {}).get("meta", {}).get("capability_refs", []))
    if cap_ids and cap_refs:
        missing = sorted(cap_refs - cap_ids)
        if missing:
            errors.append(f"[CAPABILITY_REF_UNKNOWN] transformation registry references unknown capabilities: {missing}")

    transform_ids = set(details.get("transformation_registry", {}).get("meta", {}).get("transformation_ids", []))
    transform_refs = set(details.get("experiment_registry", {}).get("meta", {}).get("transformation_refs", []))
    if transform_ids and transform_refs:
        missing = sorted(transform_refs - transform_ids)
        if missing:
            errors.append(f"[TRANSFORMATION_REF_UNKNOWN] experiment registry references unknown transformations: {missing}")

    report = {"status": "pass" if not errors else "fail", "errors": errors, "details": details}
    rendered = json.dumps(report, indent=2, sort_keys=True)
    print(rendered)
    if args.json:
        Path(args.json).write_text(rendered + "\n", encoding="utf-8")
    return 0 if not errors else 1


def _jsonable(value: Any) -> Any:
    if isinstance(value, set):
        return sorted(value)
    if isinstance(value, dict):
        return {k: _jsonable(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_jsonable(v) for v in value]
    return value


if __name__ == "__main__":
    sys.exit(main())
