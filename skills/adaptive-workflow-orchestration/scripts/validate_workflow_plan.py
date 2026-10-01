#!/usr/bin/env python3
"""Validate workflow-plan/v1 structural and semantic invariants."""
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
from pathlib import Path
from typing import Any

STRATEGIES = {
    "single", "sequential", "classify-route", "fan-out-synthesize", "pipeline",
    "adversarial-verify", "generate-filter", "tournament", "bounded-loop",
}
MODES = {"single", "parallel", "pipeline", "verify", "synthesize", "loop"}
ISOLATION = {"shared-readonly", "fresh-context", "workspace", "process", "host-native", "serial"}
STAGE_EFFECTS = {"read-only", "mutating"}
AUTH_EFFECTS = {"read-only", "mutating", "external-side-effect"}
FAILURE = {"stop", "continue-independent", "retry", "repair", "escalate"}
TERMINAL = {"completed", "blocked", "escalated", "failed", "budget_exhausted"}
DEGRADATION = {"serial", "blocked", "not-run"}
INDEPENDENT_ISOLATION = {"fresh-context", "workspace", "process", "host-native"}


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _positive_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _nonnegative_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _list_of_nonempty_strings(value: Any) -> bool:
    return isinstance(value, list) and all(_nonempty(x) for x in value)


def _diag(code: str, path: str, message: str) -> dict[str, str]:
    return {"code": code, "path": path, "message": message}


def _dedupe_check(values: list[str], path: str, errors: list[dict[str, str]]) -> None:
    if len(values) != len(set(values)):
        errors.append(_diag("E_DUPLICATE", path, "items must be unique"))


def _resource_overlap(a: str, b: str) -> bool:
    """Conservative resource overlap check for exact ids and simple globs."""
    if a == b:
        return True
    return fnmatch.fnmatchcase(a, b) or fnmatch.fnmatchcase(b, a)


def _set_conflicts(left: dict[str, Any], right: dict[str, Any]) -> list[tuple[str, str, str]]:
    conflicts: list[tuple[str, str, str]] = []
    lreads = [x for x in left.get("read_set", []) if isinstance(x, str)]
    lwrites = [x for x in left.get("write_set", []) if isinstance(x, str)]
    rreads = [x for x in right.get("read_set", []) if isinstance(x, str)]
    rwrites = [x for x in right.get("write_set", []) if isinstance(x, str)]
    for a in lwrites:
        for b in rwrites:
            if _resource_overlap(a, b):
                conflicts.append(("write/write", a, b))
        for b in rreads:
            if _resource_overlap(a, b):
                conflicts.append(("write/read", a, b))
    for a in lreads:
        for b in rwrites:
            if _resource_overlap(a, b):
                conflicts.append(("read/write", a, b))
    return conflicts


def _canonical_hash(data: dict[str, Any]) -> str:
    payload = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def validate(data: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    if not isinstance(data, dict):
        return {
            "validator": "workflow-plan-validator/v1",
            "status": "fail",
            "plan_sha256": None,
            "errors": [_diag("E_ROOT_TYPE", "$", "plan must be a JSON object")],
            "warnings": [],
        }

    if data.get("contract") != "workflow-plan/v1":
        errors.append(_diag("E_CONTRACT", "$.contract", "must be workflow-plan/v1"))
    if not _nonempty(data.get("workflow_id")):
        errors.append(_diag("E_WORKFLOW_ID", "$.workflow_id", "must be a non-empty string"))
    if not _nonempty(data.get("objective")):
        errors.append(_diag("E_OBJECTIVE", "$.objective", "must be a non-empty string"))
    criteria = data.get("success_criteria")
    if not _list_of_nonempty_strings(criteria) or not criteria:
        errors.append(_diag("E_SUCCESS_CRITERIA", "$.success_criteria", "must be a non-empty array of non-empty strings"))
    elif isinstance(criteria, list):
        _dedupe_check(criteria, "$.success_criteria", errors)
    if data.get("strategy") not in STRATEGIES:
        errors.append(_diag("E_STRATEGY", "$.strategy", f"must be one of {sorted(STRATEGIES)}"))

    authority = data.get("authority")
    allowed_effects: list[str] = []
    forbidden_effects: list[str] = []
    write_scope: list[str] = []
    if not isinstance(authority, dict):
        errors.append(_diag("E_AUTHORITY", "$.authority", "must be an object"))
    else:
        if not _nonempty(authority.get("owner")):
            errors.append(_diag("E_AUTHORITY_OWNER", "$.authority.owner", "must be a non-empty string"))
        for field in ("allowed_effects", "forbidden_effects", "write_scope"):
            value = authority.get(field)
            if not _list_of_nonempty_strings(value):
                errors.append(_diag("E_AUTHORITY_FIELD", f"$.authority.{field}", "must be an array of non-empty strings"))
            elif isinstance(value, list):
                _dedupe_check(value, f"$.authority.{field}", errors)
        allowed_effects = [x for x in authority.get("allowed_effects", []) if isinstance(x, str)]
        forbidden_effects = [x for x in authority.get("forbidden_effects", []) if isinstance(x, str)]
        write_scope = [x for x in authority.get("write_scope", []) if isinstance(x, str)]
        unknown_allowed = sorted(set(allowed_effects) - AUTH_EFFECTS)
        unknown_forbidden = sorted(set(forbidden_effects) - AUTH_EFFECTS)
        if unknown_allowed:
            errors.append(_diag("E_AUTHORITY_EFFECT", "$.authority.allowed_effects", f"unsupported values: {unknown_allowed}"))
        if unknown_forbidden:
            errors.append(_diag("E_AUTHORITY_EFFECT", "$.authority.forbidden_effects", f"unsupported values: {unknown_forbidden}"))
        overlap = sorted(set(allowed_effects) & set(forbidden_effects))
        if overlap:
            errors.append(_diag("E_AUTHORITY_CONTRADICTION", "$.authority", f"effects cannot be both allowed and forbidden: {overlap}"))

    budgets = data.get("budgets")
    max_workers = None
    max_parallel = None
    max_retries = None
    if not isinstance(budgets, dict):
        errors.append(_diag("E_BUDGETS", "$.budgets", "must be an object"))
    else:
        if not _positive_int(budgets.get("max_workers")):
            errors.append(_diag("E_BUDGET", "$.budgets.max_workers", "must be a positive integer"))
        else:
            max_workers = budgets["max_workers"]
        if not _positive_int(budgets.get("max_parallel")):
            errors.append(_diag("E_BUDGET", "$.budgets.max_parallel", "must be a positive integer"))
        else:
            max_parallel = budgets["max_parallel"]
        for field in ("max_retries_per_unit", "max_reentries"):
            if not _nonnegative_int(budgets.get(field)):
                errors.append(_diag("E_BUDGET", f"$.budgets.{field}", "must be a non-negative integer"))
        if _nonnegative_int(budgets.get("max_retries_per_unit")):
            max_retries = budgets["max_retries_per_unit"]
        if max_workers is not None and max_parallel is not None and max_parallel > max_workers:
            errors.append(_diag("E_BUDGET_RELATION", "$.budgets.max_parallel", "must not exceed max_workers"))

    stages = data.get("stages")
    stage_ids: list[str] = []
    valid_stages: list[dict[str, Any]] = []
    if not isinstance(stages, list) or not stages:
        errors.append(_diag("E_STAGES", "$.stages", "must be a non-empty array"))
        stages = []
    else:
        for idx, stage in enumerate(stages):
            base = f"$.stages[{idx}]"
            if not isinstance(stage, dict):
                errors.append(_diag("E_STAGE_TYPE", base, "must be an object"))
                continue
            valid_stages.append(stage)
            sid = stage.get("id")
            if not _nonempty(sid):
                errors.append(_diag("E_STAGE_ID", f"{base}.id", "must be a non-empty string"))
            else:
                stage_ids.append(sid)
            if stage.get("mode") not in MODES:
                errors.append(_diag("E_STAGE_MODE", f"{base}.mode", f"must be one of {sorted(MODES)}"))
            if not _nonempty(stage.get("work_source")):
                errors.append(_diag("E_WORK_SOURCE", f"{base}.work_source", "must be a non-empty string"))
            deps = stage.get("depends_on")
            if not _list_of_nonempty_strings(deps):
                errors.append(_diag("E_DEPENDENCIES", f"{base}.depends_on", "must be an array of non-empty stage ids"))
            elif isinstance(deps, list):
                _dedupe_check(deps, f"{base}.depends_on", errors)
            sp = stage.get("max_parallel")
            if not _positive_int(sp):
                errors.append(_diag("E_STAGE_PARALLEL", f"{base}.max_parallel", "must be a positive integer"))
            else:
                if max_parallel is not None and sp > max_parallel:
                    errors.append(_diag("E_STAGE_PARALLEL", f"{base}.max_parallel", "must not exceed budgets.max_parallel"))
                if max_workers is not None and sp > max_workers:
                    errors.append(_diag("E_STAGE_PARALLEL", f"{base}.max_parallel", "must not exceed budgets.max_workers"))
            if stage.get("isolation") not in ISOLATION:
                errors.append(_diag("E_STAGE_ISOLATION", f"{base}.isolation", f"must be one of {sorted(ISOLATION)}"))
            effects = stage.get("effects")
            if effects not in STAGE_EFFECTS:
                errors.append(_diag("E_STAGE_EFFECT", f"{base}.effects", f"must be one of {sorted(STAGE_EFFECTS)}"))
            for field in ("read_set", "write_set"):
                value = stage.get(field)
                if not _list_of_nonempty_strings(value):
                    errors.append(_diag("E_RESOURCE_SET", f"{base}.{field}", "must be an array of non-empty strings"))
                elif isinstance(value, list):
                    _dedupe_check(value, f"{base}.{field}", errors)
            write_set = [x for x in stage.get("write_set", []) if isinstance(x, str)]
            if effects == "read-only" and write_set:
                errors.append(_diag("E_READONLY_WRITE", f"{base}.write_set", "read-only stage must have an empty write_set"))
            if effects == "mutating" and not write_set:
                errors.append(_diag("E_MUTATION_SCOPE", f"{base}.write_set", "mutating stage requires a non-empty write_set"))
            if effects in STAGE_EFFECTS:
                if effects not in allowed_effects or effects in forbidden_effects:
                    errors.append(_diag("E_AUTHORITY_EXPANSION", f"{base}.effects", f"stage effect {effects!r} is not authorized"))
            if effects == "mutating":
                if not write_scope:
                    errors.append(_diag("E_WRITE_SCOPE", "$.authority.write_scope", "mutating workflow requires non-empty authority.write_scope"))
                else:
                    for resource in write_set:
                        if not any(fnmatch.fnmatchcase(resource, scope) for scope in write_scope):
                            errors.append(_diag("E_WRITE_SCOPE", f"{base}.write_set", f"resource {resource!r} is outside authority.write_scope"))
            if not _nonempty(stage.get("success")):
                errors.append(_diag("E_STAGE_SUCCESS", f"{base}.success", "must be a non-empty string"))
            if stage.get("on_failure") not in FAILURE:
                errors.append(_diag("E_FAILURE_POLICY", f"{base}.on_failure", f"must be one of {sorted(FAILURE)}"))
            if stage.get("on_failure") == "retry" and max_retries == 0:
                errors.append(_diag("E_RETRY_BUDGET", f"{base}.on_failure", "retry policy requires budgets.max_retries_per_unit > 0"))
            if stage.get("mode") == "loop" and not _positive_int(stage.get("max_iterations")):
                errors.append(_diag("E_LOOP_BOUND", f"{base}.max_iterations", "loop stage requires a positive max_iterations"))
            if stage.get("mode") == "verify" and stage.get("isolation") not in INDEPENDENT_ISOLATION:
                errors.append(_diag("E_VERIFY_ISOLATION", f"{base}.isolation", "verify stage requires independent isolation"))

    if len(stage_ids) != len(set(stage_ids)):
        errors.append(_diag("E_STAGE_DUPLICATE_ID", "$.stages", "stage ids must be unique"))

    known = set(stage_ids)
    graph: dict[str, list[str]] = {}
    by_id: dict[str, dict[str, Any]] = {}
    for stage in valid_stages:
        sid = stage.get("id")
        if not _nonempty(sid):
            continue
        by_id[sid] = stage
        deps = stage.get("depends_on") if isinstance(stage.get("depends_on"), list) else []
        graph[sid] = [d for d in deps if isinstance(d, str)]
        for dep in graph[sid]:
            if dep not in known:
                errors.append(_diag("E_DEP_UNKNOWN", f"$.stages[{sid}].depends_on", f"unknown stage {dep!r}"))
            if dep == sid:
                errors.append(_diag("E_DEP_SELF", f"$.stages[{sid}].depends_on", "stage cannot depend on itself"))

    visiting: set[str] = set()
    visited: set[str] = set()
    cycle_reported = False

    def visit(node: str) -> None:
        nonlocal cycle_reported
        if node in visited:
            return
        if node in visiting:
            if not cycle_reported:
                errors.append(_diag("E_DEP_CYCLE", "$.stages", "stage dependencies must be acyclic"))
                cycle_reported = True
            return
        visiting.add(node)
        for dep in graph.get(node, []):
            if dep in graph:
                visit(dep)
        visiting.remove(node)
        visited.add(node)

    for node in graph:
        visit(node)

    ancestors_cache: dict[str, set[str]] = {}

    def ancestors(node: str) -> set[str]:
        if node in ancestors_cache:
            return ancestors_cache[node]
        result: set[str] = set()
        for dep in graph.get(node, []):
            if dep in graph:
                result.add(dep)
                result.update(ancestors(dep))
        ancestors_cache[node] = result
        return result

    if max_parallel is not None and max_parallel > 1 and not cycle_reported:
        ids = [sid for sid in stage_ids if sid in by_id]
        for i, left_id in enumerate(ids):
            for right_id in ids[i + 1:]:
                if left_id in ancestors(right_id) or right_id in ancestors(left_id):
                    continue
                conflicts = _set_conflicts(by_id[left_id], by_id[right_id])
                if conflicts:
                    kind, a, b = conflicts[0]
                    errors.append(_diag(
                        "E_PARALLEL_CONFLICT",
                        "$.stages",
                        f"unordered stages {left_id!r} and {right_id!r} conflict ({kind}) on {a!r} vs {b!r}; add an ordering edge or remove overlap",
                    ))

    termination = data.get("termination")
    if not isinstance(termination, dict):
        errors.append(_diag("E_TERMINATION", "$.termination", "must be an object"))
    else:
        if not _nonempty(termination.get("success_predicate")):
            errors.append(_diag("E_TERMINATION", "$.termination.success_predicate", "must be a non-empty string"))
        states = termination.get("terminal_states")
        if not _list_of_nonempty_strings(states) or not states:
            errors.append(_diag("E_TERMINATION", "$.termination.terminal_states", "must be a non-empty array"))
        elif isinstance(states, list):
            _dedupe_check(states, "$.termination.terminal_states", errors)
            unknown = sorted(set(states) - TERMINAL)
            if unknown:
                errors.append(_diag("E_TERMINATION_STATE", "$.termination.terminal_states", f"unsupported values: {unknown}"))
            if "completed" not in states:
                errors.append(_diag("E_TERMINATION_STATE", "$.termination.terminal_states", "must include completed"))

    capabilities = data.get("capabilities")
    if not isinstance(capabilities, dict):
        errors.append(_diag("E_CAPABILITIES", "$.capabilities", "must be an object"))
    else:
        required = capabilities.get("required")
        optional = capabilities.get("optional")
        degradation = capabilities.get("degradation")
        for field, value in (("required", required), ("optional", optional)):
            if not _list_of_nonempty_strings(value):
                errors.append(_diag("E_CAPABILITY_LIST", f"$.capabilities.{field}", "must be an array of non-empty strings"))
            elif isinstance(value, list):
                _dedupe_check(value, f"$.capabilities.{field}", errors)
        required_set = set(required) if isinstance(required, list) else set()
        optional_set = set(optional) if isinstance(optional, list) else set()
        overlap = sorted(required_set & optional_set)
        if overlap:
            errors.append(_diag("E_CAPABILITY_OVERLAP", "$.capabilities", f"capabilities cannot be both required and optional: {overlap}"))
        if not isinstance(degradation, dict):
            errors.append(_diag("E_DEGRADATION", "$.capabilities.degradation", "must be an object"))
            degradation = {}
        else:
            for key, value in degradation.items():
                if value not in DEGRADATION:
                    errors.append(_diag("E_DEGRADATION", f"$.capabilities.degradation.{key}", f"must be one of {sorted(DEGRADATION)}"))
        if max_parallel is not None and max_parallel > 1:
            cap = "parallelize-independent-work"
            if cap in optional_set and degradation.get(cap) not in {"serial", "blocked"}:
                errors.append(_diag("E_PARALLEL_DEGRADATION", "$.capabilities.degradation", "optional parallel capability requires serial or blocked degradation"))
            if cap not in required_set and cap not in optional_set:
                errors.append(_diag("E_PARALLEL_CAPABILITY", "$.capabilities", "max_parallel > 1 requires parallelize-independent-work as required or optional"))

    evidence = data.get("evidence")
    if not isinstance(evidence, dict):
        errors.append(_diag("E_EVIDENCE", "$.evidence", "must be an object"))
    else:
        for field in ("input_identity", "planner_identity", "evaluator_identity"):
            if not _nonempty(evidence.get(field)):
                errors.append(_diag("E_EVIDENCE_ID", f"$.evidence.{field}", "must be a non-empty string"))

    strategy = data.get("strategy")
    if strategy == "single":
        if len(valid_stages) != 1:
            errors.append(_diag("E_STRATEGY_SHAPE", "$.strategy", "single strategy requires exactly one stage"))
        if max_workers not in {None, 1} or max_parallel not in {None, 1}:
            errors.append(_diag("E_STRATEGY_SHAPE", "$.budgets", "single strategy requires max_workers=max_parallel=1"))
    if strategy == "bounded-loop" and not any(s.get("mode") == "loop" for s in valid_stages):
        errors.append(_diag("E_STRATEGY_SHAPE", "$.strategy", "bounded-loop strategy requires at least one loop stage"))
    if strategy == "adversarial-verify" and not any(s.get("mode") == "verify" for s in valid_stages):
        errors.append(_diag("E_STRATEGY_SHAPE", "$.strategy", "adversarial-verify strategy requires at least one verify stage"))
    if strategy == "fan-out-synthesize" and not any(s.get("mode") == "synthesize" for s in valid_stages):
        warnings.append(_diag("W_STRATEGY_SHAPE", "$.strategy", "fan-out-synthesize normally includes an explicit synthesize stage"))
    if strategy == "pipeline" and not any(s.get("mode") == "pipeline" for s in valid_stages):
        warnings.append(_diag("W_STRATEGY_SHAPE", "$.strategy", "pipeline strategy normally includes a pipeline stage"))

    plan_hash = _canonical_hash(data)
    return {
        "validator": "workflow-plan-validator/v1",
        "status": "pass" if not errors else "fail",
        "plan_sha256": plan_hash,
        "errors": errors,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", help="workflow-plan/v1 JSON file")
    parser.add_argument("--json", dest="json_out", help="optional report output path")
    args = parser.parse_args()
    try:
        data = json.loads(Path(args.plan).read_text(encoding="utf-8"))
        report = validate(data)
    except Exception as exc:
        report = {
            "validator": "workflow-plan-validator/v1",
            "status": "fail",
            "plan_sha256": None,
            "errors": [_diag("E_PARSE", "$", str(exc))],
            "warnings": [],
        }
    payload = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.json_out:
        Path(args.json_out).write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
