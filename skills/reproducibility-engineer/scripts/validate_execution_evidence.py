#!/usr/bin/env python3
from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

DIGEST_PREFIX = "sha256:"
VALID_DIGEST_LEN = 64


def canonical_hash(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return DIGEST_PREFIX + hashlib.sha256(raw).hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def norm_digest(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    raw = value[len(DIGEST_PREFIX):] if value.lower().startswith(DIGEST_PREFIX) else value
    raw = raw.lower()
    if len(raw) != VALID_DIGEST_LEN or any(ch not in "0123456789abcdef" for ch in raw):
        return None
    return raw


def diag(code: str, subject: str, evidence: Any, supported_fixes: list[str] | None = None) -> dict[str, Any]:
    return {
        "code": code,
        "severity": "error",
        "subject": subject,
        "evidence": evidence,
        "supported_fixes": supported_fixes or [],
    }


def require_nonempty_string(data: dict[str, Any], key: str, diagnostics: list[dict[str, Any]], prefix: str = "", min_length: int = 1) -> None:
    value = data.get(key)
    if not isinstance(value, str) or len(value.strip()) < min_length:
        diagnostics.append(diag("REQUIRED_STRING", f"{prefix}{key}", f"expected a string with length >= {min_length}"))


def reject_unknown_properties(data: dict[str, Any], allowed: set[str], subject: str, diagnostics: list[dict[str, Any]]) -> None:
    for key in sorted(set(data) - allowed):
        diagnostics.append(diag("UNKNOWN_PROPERTY", f"{subject}.{key}" if subject else key, "property is not allowed by the evidence contract"))


def require_optional_string(data: dict[str, Any], key: str, diagnostics: list[dict[str, Any]], prefix: str = "", min_length: int = 0) -> None:
    if key not in data:
        return
    value = data.get(key)
    if not isinstance(value, str) or len(value.strip()) < min_length:
        diagnostics.append(diag("STRING_TYPE", f"{prefix}{key}", f"expected a string with length >= {min_length}"))


def validate_digested_subjects(value: Any, subject: str, diagnostics: list[dict[str, Any]]) -> None:
    if not isinstance(value, list) or not value:
        diagnostics.append(diag("DIGESTED_SUBJECTS_REQUIRED", subject, "expected a non-empty array"))
        return
    seen: set[str] = set()
    for i, row in enumerate(value):
        loc = f"{subject}[{i}]"
        if not isinstance(row, dict):
            diagnostics.append(diag("DIGESTED_SUBJECT_TYPE", loc, "expected object"))
            continue
        reject_unknown_properties(row, {"subject", "sha256"}, loc, diagnostics)
        name = row.get("subject")
        if not isinstance(name, str) or not name.strip():
            diagnostics.append(diag("DIGESTED_SUBJECT_NAME", loc, "subject must be non-empty"))
        elif name in seen:
            diagnostics.append(diag("DIGESTED_SUBJECT_DUPLICATE", loc, name))
        else:
            seen.add(name)
        if norm_digest(row.get("sha256")) is None:
            diagnostics.append(diag("INVALID_SHA256", f"{loc}.sha256", row.get("sha256")))


def validate_environment(data: Any) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    diagnostics: list[dict[str, Any]] = []
    metrics: dict[str, Any] = {}
    if not isinstance(data, dict):
        return [diag("ROOT_TYPE", "root", "expected object")], metrics
    reject_unknown_properties(data, {"profile_version", "run_id", "host", "runtime", "model", "tools", "dependencies", "locale", "timezone", "cache_policy", "concurrency_policy", "hermeticity", "controller_identity", "inputs", "outputs"}, "", diagnostics)
    if data.get("profile_version") != 1:
        diagnostics.append(diag("PROFILE_VERSION", "profile_version", data.get("profile_version"), ["use profile_version 1"]))
    for key in ("run_id", "host", "locale", "timezone", "cache_policy", "concurrency_policy"):
        require_nonempty_string(data, key, diagnostics)
    runtime = data.get("runtime")
    if not isinstance(runtime, dict):
        diagnostics.append(diag("RUNTIME_REQUIRED", "runtime", "expected object"))
    else:
        reject_unknown_properties(runtime, {"python", "os"}, "runtime", diagnostics)
        for key in ("python", "os"):
            require_nonempty_string(runtime, key, diagnostics, "runtime.")
    model = data.get("model")
    if not isinstance(model, dict):
        diagnostics.append(diag("MODEL_REQUIRED", "model", "expected object; use explicit not-applicable values for non-model runs"))
    else:
        reject_unknown_properties(model, {"provider", "name", "configuration_identity"}, "model", diagnostics)
        for key in ("provider", "name"):
            require_nonempty_string(model, key, diagnostics, "model.")
        require_nonempty_string(model, "configuration_identity", diagnostics, "model.", min_length=3)
    for key, needs_version in (("tools", False), ("dependencies", True)):
        rows = data.get(key)
        if not isinstance(rows, list):
            diagnostics.append(diag("COLLECTION_REQUIRED", key, "expected array"))
            continue
        seen: set[tuple[str, str]] = set()
        for i, row in enumerate(rows):
            loc = f"{key}[{i}]"
            if not isinstance(row, dict):
                diagnostics.append(diag("COLLECTION_ITEM_TYPE", loc, "expected object"))
                continue
            reject_unknown_properties(row, {"name", "identity", "version"}, loc, diagnostics)
            for field in (("name", "identity", "version") if needs_version else ("name", "identity")):
                require_nonempty_string(row, field, diagnostics, f"{loc}.")
            if not needs_version:
                require_optional_string(row, "version", diagnostics, f"{loc}.")
            pair = (str(row.get("name", "")), str(row.get("identity", "")))
            if pair in seen:
                diagnostics.append(diag("DUPLICATE_IDENTITY", loc, {"name": pair[0], "identity": pair[1]}))
            seen.add(pair)
    hermeticity = data.get("hermeticity")
    if hermeticity is not None and hermeticity not in {"recorded", "pinned", "hermetic"}:
        diagnostics.append(diag("HERMETICITY_VALUE", "hermeticity", hermeticity))
    if "controller_identity" in data:
        require_nonempty_string(data, "controller_identity", diagnostics)
    validate_digested_subjects(data.get("inputs"), "inputs", diagnostics)
    validate_digested_subjects(data.get("outputs"), "outputs", diagnostics)
    return diagnostics, metrics


def normalized_environment_identity(data: dict[str, Any]) -> dict[str, Any]:
    tools = sorted(data.get("tools", []), key=lambda x: (str(x.get("name", "")), str(x.get("identity", "")))) if isinstance(data.get("tools"), list) else []
    dependencies = sorted(data.get("dependencies", []), key=lambda x: (str(x.get("name", "")), str(x.get("version", "")), str(x.get("identity", "")))) if isinstance(data.get("dependencies"), list) else []
    return {
        "host": data.get("host"),
        "runtime": data.get("runtime"),
        "model": data.get("model"),
        "tools": tools,
        "dependencies": dependencies,
        "locale": data.get("locale"),
        "timezone": data.get("timezone"),
        "cache_policy": data.get("cache_policy"),
        "concurrency_policy": data.get("concurrency_policy"),
        "hermeticity": data.get("hermeticity", "recorded"),
    }


def wilson_interval(successes: int, total: int, z: float = 1.959963984540054) -> list[float]:
    if total <= 0:
        return [0.0, 0.0]
    p = successes / total
    denom = 1.0 + (z * z) / total
    center = (p + (z * z) / (2.0 * total)) / denom
    margin = z * math.sqrt((p * (1.0 - p) / total) + (z * z) / (4.0 * total * total)) / denom
    return [max(0.0, center - margin), min(1.0, center + margin)]


def validate_stochastic(data: Any) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    diagnostics: list[dict[str, Any]] = []
    metrics: dict[str, Any] = {}
    if not isinstance(data, dict):
        return [diag("ROOT_TYPE", "root", "expected object")], metrics
    reject_unknown_properties(data, {"profile_version", "scenario_id", "evaluator_identity", "reliability_k", "stop_rule", "claim", "evaluator", "trials"}, "", diagnostics)
    if data.get("profile_version") != 1:
        diagnostics.append(diag("PROFILE_VERSION", "profile_version", data.get("profile_version")))
    for key in ("scenario_id", "evaluator_identity"):
        require_nonempty_string(data, key, diagnostics)
    reliability_k = data.get("reliability_k")
    if not isinstance(reliability_k, list) or not reliability_k:
        diagnostics.append(diag("RELIABILITY_K_REQUIRED", "reliability_k", "expected non-empty array"))
        reliability_k = []
    elif len(reliability_k) != len(set(reliability_k)) or any(not isinstance(k, int) or isinstance(k, bool) or k < 1 or k > 100 for k in reliability_k):
        diagnostics.append(diag("RELIABILITY_K_INVALID", "reliability_k", reliability_k))
    stop_rule = data.get("stop_rule")
    stop_type = None
    max_trials = None
    if not isinstance(stop_rule, dict):
        diagnostics.append(diag("STOP_RULE_REQUIRED", "stop_rule", "expected object"))
    else:
        reject_unknown_properties(stop_rule, {"type", "max_trials"}, "stop_rule", diagnostics)
        stop_type = stop_rule.get("type")
        if stop_type not in {"fixed-trials", "budget"}:
            diagnostics.append(diag("STOP_RULE_TYPE", "stop_rule.type", stop_type))
        max_trials = stop_rule.get("max_trials")
        if not isinstance(max_trials, int) or isinstance(max_trials, bool) or max_trials < 1:
            diagnostics.append(diag("STOP_RULE_MAX_TRIALS", "stop_rule.max_trials", max_trials))
    claim = data.get("claim")
    claim_level = None
    if not isinstance(claim, dict):
        diagnostics.append(diag("CLAIM_REQUIRED", "claim", "expected object"))
    else:
        reject_unknown_properties(claim, {"level", "independent_replication"}, "claim", diagnostics)
        claim_level = claim.get("level")
        if claim_level not in {"exploratory", "standard", "strong"}:
            diagnostics.append(diag("CLAIM_LEVEL", "claim.level", claim_level))
        if not isinstance(claim.get("independent_replication"), bool):
            diagnostics.append(diag("CLAIM_REPLICATION_TYPE", "claim.independent_replication", claim.get("independent_replication")))
        if claim_level == "strong" and claim.get("independent_replication") is not True:
            diagnostics.append(diag("STRONG_CLAIM_REPLICATION_REQUIRED", "claim.independent_replication", False, ["run an independent replication against the frozen evaluator before a strong promotion claim"]))
    evaluator = data.get("evaluator")
    if not isinstance(evaluator, dict):
        diagnostics.append(diag("EVALUATOR_REQUIRED", "evaluator", "expected object"))
    else:
        reject_unknown_properties(evaluator, {"kind", "judge_identity", "calibration"}, "evaluator", diagnostics)
        kind = evaluator.get("kind")
        if kind not in {"deterministic", "human", "llm-judge"}:
            diagnostics.append(diag("EVALUATOR_KIND", "evaluator.kind", kind))
        require_optional_string(evaluator, "judge_identity", diagnostics, "evaluator.", min_length=1)
        calibration = evaluator.get("calibration")
        if calibration is not None:
            if not isinstance(calibration, dict):
                diagnostics.append(diag("LLM_JUDGE_CALIBRATION_REQUIRED", "evaluator.calibration", calibration))
            else:
                reject_unknown_properties(calibration, {"status", "evidence_identity"}, "evaluator.calibration", diagnostics)
                if calibration.get("status") not in {"calibrated", "supplied", "unknown"}:
                    diagnostics.append(diag("LLM_JUDGE_CALIBRATION_REQUIRED", "evaluator.calibration.status", calibration.get("status")))
                require_optional_string(calibration, "evidence_identity", diagnostics, "evaluator.calibration.")
        if kind == "llm-judge":
            if not isinstance(evaluator.get("judge_identity"), str) or not evaluator.get("judge_identity", "").strip():
                diagnostics.append(diag("LLM_JUDGE_IDENTITY_REQUIRED", "evaluator.judge_identity", evaluator.get("judge_identity")))
            if not isinstance(calibration, dict) or calibration.get("status") not in {"calibrated", "supplied", "unknown"}:
                diagnostics.append(diag("LLM_JUDGE_CALIBRATION_REQUIRED", "evaluator.calibration", calibration))
            elif claim_level == "strong" and calibration.get("status") == "unknown":
                diagnostics.append(diag("STRONG_CLAIM_CALIBRATION_REQUIRED", "evaluator.calibration.status", "unknown"))
    trials = data.get("trials")
    outcomes: list[str] = []
    if not isinstance(trials, list) or not trials:
        diagnostics.append(diag("TRIALS_REQUIRED", "trials", "expected non-empty array"))
        trials = []
    seen: set[str] = set()
    for i, row in enumerate(trials):
        loc = f"trials[{i}]"
        if not isinstance(row, dict):
            diagnostics.append(diag("TRIAL_TYPE", loc, "expected object"))
            continue
        reject_unknown_properties(row, {"id", "outcome", "result_identity"}, loc, diagnostics)
        require_optional_string(row, "result_identity", diagnostics, f"{loc}.")
        trial_id = row.get("id")
        if not isinstance(trial_id, str) or not trial_id.strip():
            diagnostics.append(diag("TRIAL_ID", f"{loc}.id", trial_id))
        elif trial_id in seen:
            diagnostics.append(diag("TRIAL_ID_DUPLICATE", f"{loc}.id", trial_id))
        else:
            seen.add(trial_id)
        outcome = row.get("outcome")
        if outcome not in {"success", "failure", "unknown"}:
            diagnostics.append(diag("TRIAL_OUTCOME", f"{loc}.outcome", outcome))
        else:
            outcomes.append(outcome)
    if isinstance(max_trials, int) and max_trials > 0:
        if len(trials) > max_trials:
            diagnostics.append(diag("TRIAL_BUDGET_EXCEEDED", "trials", {"observed": len(trials), "max_trials": max_trials}))
        if stop_type == "fixed-trials" and len(trials) != max_trials:
            diagnostics.append(diag("FIXED_TRIAL_COUNT_MISMATCH", "trials", {"observed": len(trials), "expected": max_trials}))
    if outcomes:
        total = len(outcomes)
        successes = sum(x == "success" for x in outcomes)
        failures = sum(x == "failure" for x in outcomes)
        unknown = sum(x == "unknown" for x in outcomes)
        p = successes / total
        metrics = {
            "trial_count": total,
            "success_count": successes,
            "failure_count": failures,
            "unknown_count": unknown,
            "success_rate": p,
            "pass_power": {str(k): p ** k for k in reliability_k if isinstance(k, int) and 1 <= k <= 100},
            "wilson_95": wilson_interval(successes, total),
            "unknowns_count_as_non_success": True,
        }
    return diagnostics, metrics


def validate_lineage(data: Any) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    diagnostics: list[dict[str, Any]] = []
    metrics: dict[str, Any] = {}
    if not isinstance(data, dict):
        return [diag("ROOT_TYPE", "root", "expected object")], metrics
    reject_unknown_properties(data, {"profile_version", "source_identity", "planner_identity", "workflow_plan_identity", "evaluator_identity", "nodes", "canonical_outputs"}, "", diagnostics)
    if data.get("profile_version") != 1:
        diagnostics.append(diag("PROFILE_VERSION", "profile_version", data.get("profile_version")))
    for key in ("planner_identity", "workflow_plan_identity", "evaluator_identity"):
        require_nonempty_string(data, key, diagnostics)
    if "source_identity" in data:
        require_nonempty_string(data, "source_identity", diagnostics)
    nodes = data.get("nodes")
    if not isinstance(nodes, list) or not nodes:
        diagnostics.append(diag("NODES_REQUIRED", "nodes", "expected non-empty array"))
        nodes = []
    by_id: dict[str, dict[str, Any]] = {}
    for i, row in enumerate(nodes):
        loc = f"nodes[{i}]"
        if not isinstance(row, dict):
            diagnostics.append(diag("NODE_TYPE", loc, "expected object"))
            continue
        reject_unknown_properties(row, {"id", "kind", "upstream", "execution_identity", "input_digests", "output_digest", "replayable", "invalidation_key"}, loc, diagnostics)
        node_id = row.get("id")
        if not isinstance(node_id, str) or not node_id.strip():
            diagnostics.append(diag("NODE_ID", f"{loc}.id", node_id))
            continue
        if node_id in by_id:
            diagnostics.append(diag("NODE_ID_DUPLICATE", f"{loc}.id", node_id))
        else:
            by_id[node_id] = row
        if row.get("kind") not in {"tool", "model", "human", "transform", "aggregate", "other"}:
            diagnostics.append(diag("NODE_KIND", f"{loc}.kind", row.get("kind")))
        if not isinstance(row.get("upstream"), list) or any(not isinstance(x, str) or not x for x in row.get("upstream", [])):
            diagnostics.append(diag("NODE_UPSTREAM", f"{loc}.upstream", row.get("upstream")))
        elif len(row.get("upstream", [])) != len(set(row.get("upstream", []))):
            diagnostics.append(diag("NODE_UPSTREAM_DUPLICATE", f"{loc}.upstream", row.get("upstream")))
        require_nonempty_string(row, "execution_identity", diagnostics, f"{loc}.")
        if not isinstance(row.get("input_digests"), list) or any(norm_digest(x) is None for x in row.get("input_digests", [])):
            diagnostics.append(diag("NODE_INPUT_DIGESTS", f"{loc}.input_digests", row.get("input_digests")))
        if norm_digest(row.get("output_digest")) is None:
            diagnostics.append(diag("NODE_OUTPUT_DIGEST", f"{loc}.output_digest", row.get("output_digest")))
        if not isinstance(row.get("replayable"), bool):
            diagnostics.append(diag("NODE_REPLAYABLE", f"{loc}.replayable", row.get("replayable")))
        require_nonempty_string(row, "invalidation_key", diagnostics, f"{loc}.")
    for node_id, row in by_id.items():
        for upstream in row.get("upstream", []) if isinstance(row.get("upstream"), list) else []:
            if upstream not in by_id:
                diagnostics.append(diag("UNKNOWN_UPSTREAM", f"node:{node_id}", upstream))
            elif upstream == node_id:
                diagnostics.append(diag("LINEAGE_CYCLE", f"node:{node_id}", "self-cycle"))
    graph = {node_id: [u for u in row.get("upstream", []) if u in by_id] for node_id, row in by_id.items()}
    state: dict[str, int] = {}
    def visit(node_id: str) -> bool:
        mark = state.get(node_id, 0)
        if mark == 1:
            return True
        if mark == 2:
            return False
        state[node_id] = 1
        if any(visit(upstream) for upstream in graph.get(node_id, [])):
            return True
        state[node_id] = 2
        return False
    if any(visit(node_id) for node_id in graph if state.get(node_id, 0) == 0):
        if not any(d.get("code") == "LINEAGE_CYCLE" for d in diagnostics):
            diagnostics.append(diag("LINEAGE_CYCLE", "nodes", "dependency graph contains a cycle"))
    canonical = data.get("canonical_outputs")
    if not isinstance(canonical, list) or not canonical:
        diagnostics.append(diag("CANONICAL_OUTPUTS_REQUIRED", "canonical_outputs", "expected non-empty array"))
        canonical = []
    output_names: set[str] = set()
    for i, row in enumerate(canonical):
        loc = f"canonical_outputs[{i}]"
        if not isinstance(row, dict):
            diagnostics.append(diag("CANONICAL_OUTPUT_TYPE", loc, "expected object"))
            continue
        reject_unknown_properties(row, {"name", "node_id", "sha256"}, loc, diagnostics)
        name = row.get("name")
        node_id = row.get("node_id")
        digest = norm_digest(row.get("sha256"))
        if not isinstance(name, str) or not name.strip():
            diagnostics.append(diag("CANONICAL_OUTPUT_NAME", f"{loc}.name", name))
        elif name in output_names:
            diagnostics.append(diag("CANONICAL_OUTPUT_DUPLICATE", f"{loc}.name", name))
        else:
            output_names.add(name)
        if node_id not in by_id:
            diagnostics.append(diag("CANONICAL_OUTPUT_NODE", f"{loc}.node_id", node_id))
        if digest is None:
            diagnostics.append(diag("INVALID_SHA256", f"{loc}.sha256", row.get("sha256")))
        elif node_id in by_id and digest != norm_digest(by_id[node_id].get("output_digest")):
            diagnostics.append(diag("CANONICAL_OUTPUT_DIGEST_MISMATCH", loc, {"declared": row.get("sha256"), "node_output": by_id[node_id].get("output_digest")}))
    metrics = {"node_count": len(by_id), "canonical_output_count": len(canonical)}
    return diagnostics, metrics


def emit(report: dict[str, Any], output: str | None) -> None:
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    print(rendered)
    if output:
        Path(output).write_text(rendered + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate environment/provenance, stochastic-evaluation, or execution-lineage evidence using only the Python standard library.")
    ap.add_argument("--kind", choices=("environment", "stochastic", "lineage"), required=True)
    ap.add_argument("--input", required=True)
    ap.add_argument("--compare", help="For environment evidence, compare material execution identity against another valid environment profile.")
    ap.add_argument("--json", dest="json_out")
    args = ap.parse_args()
    path = Path(args.input)
    try:
        data = read_json(path)
    except Exception as exc:
        report = {"status": "fail", "kind": args.kind, "diagnostics": [diag("INVALID_JSON", str(path), str(exc))]}
        emit(report, args.json_out)
        return 2
    if args.kind == "environment":
        diagnostics, metrics = validate_environment(data)
        identity = canonical_hash(normalized_environment_identity(data)) if isinstance(data, dict) else None
        if not diagnostics and args.compare:
            other_path = Path(args.compare)
            try:
                other = read_json(other_path)
            except Exception as exc:
                diagnostics.append(diag("COMPARE_INVALID_JSON", str(other_path), str(exc)))
            else:
                other_diag, _ = validate_environment(other)
                if other_diag:
                    diagnostics.append(diag("COMPARE_INVALID_PROFILE", str(other_path), other_diag))
                else:
                    other_identity = canonical_hash(normalized_environment_identity(other))
                    if other_identity != identity:
                        diagnostics.append(diag("ENVIRONMENT_DRIFT", "environment_identity", {"left": identity, "right": other_identity}, ["re-run paired arms under the same material environment or explicitly re-baseline"]))
        report = {"status": "fail" if diagnostics else "pass", "kind": args.kind, "identity_sha256": identity, "metrics": metrics, "diagnostics": diagnostics}
    elif args.kind == "stochastic":
        diagnostics, metrics = validate_stochastic(data)
        report = {"status": "fail" if diagnostics else "pass", "kind": args.kind, "identity_sha256": canonical_hash(data) if isinstance(data, dict) else None, "metrics": metrics, "diagnostics": diagnostics}
    else:
        diagnostics, metrics = validate_lineage(data)
        report = {"status": "fail" if diagnostics else "pass", "kind": args.kind, "identity_sha256": canonical_hash(data) if isinstance(data, dict) else None, "metrics": metrics, "diagnostics": diagnostics}
    emit(report, args.json_out)
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
