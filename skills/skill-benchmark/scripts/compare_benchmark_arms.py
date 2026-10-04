#!/usr/bin/env python3
"""Compare behavioral benchmark arms with identity, uncertainty, and efficiency gates."""
from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path
from typing import Any

from validate_scenario_results import load_json, validate_payload

HIGHER_BETTER = {"activation_precision", "activation_recall", "output_conformance", "robustness"}
LOWER_BETTER = {"rework_rate"}
EFFICIENCY_FIELDS = ("input_tokens", "output_tokens", "latency_ms", "tool_calls", "cost_usd")


def _ratio(num: int, den: int) -> float | None:
    return None if den == 0 else num / den


def metrics(rows: list[dict]) -> dict[str, float | None]:
    complete = [
        r for r in rows
        if isinstance(r, dict)
        and r.get("actual_activation") is not None
        and r.get("output_conforms") is not None
        and r.get("needs_rework") is not None
    ]
    expected_yes = [r for r in complete if r.get("expected_activation") is True]
    actual_yes = [r for r in complete if r.get("actual_activation") is True]
    tp = [r for r in actual_yes if r.get("expected_activation") is True]
    conforming = [r for r in complete if r.get("output_conforms") is True]
    edges = [r for r in complete if r.get("category") == "edge_case"]
    robust_edges = [r for r in edges if r.get("output_conforms") is True and r.get("needs_rework") is False]
    rework = [r for r in complete if r.get("needs_rework") is True]
    return {
        "activation_precision": _ratio(len(tp), len(actual_yes)),
        "activation_recall": _ratio(len(tp), len(expected_yes)),
        "output_conformance": _ratio(len(conforming), len(complete)),
        "robustness": _ratio(len(robust_edges), len(edges)),
        "rework_rate": _ratio(len(rework), len(complete)),
    }


def efficiency_metrics(rows: list[dict]) -> dict[str, float | None]:
    out: dict[str, float | None] = {}
    for field in EFFICIENCY_FIELDS:
        values = [float(r[field]) for r in rows if isinstance(r, dict) and isinstance(r.get(field), (int, float)) and not isinstance(r.get(field), bool)]
        out[field] = (sum(values) / len(values)) if values else None
    input_tokens = out.get("input_tokens")
    output_tokens = out.get("output_tokens")
    out["total_tokens"] = (input_tokens + output_tokens) if input_tokens is not None and output_tokens is not None else None
    return out


def _validate_arm(path: Path, expected_arm: str) -> tuple[dict, dict]:
    result = validate_payload(load_json(path))
    if result["status"] != "pass":
        raise ValueError(f"{expected_arm} evidence invalid: {'; '.join(result['errors'])}")
    meta = result.get("metadata", {})
    declared = meta.get("arm_type")
    if declared and declared != expected_arm:
        raise ValueError(f"{expected_arm} file declares arm_type={declared!r}")
    if result.get("provenance_status") != "pinned" and expected_arm != "without-skill":
        raise ValueError(f"{expected_arm} evidence must be identity-pinned for strict comparison")
    if meta.get("evidence_origin") != "executed":
        raise ValueError(f"{expected_arm} evidence must have evidence_origin=executed for measured delta")
    if meta.get("evaluator_visibility") == "hidden" and meta.get("candidate_saw_evaluator_only_assets") is not False:
        raise ValueError(f"{expected_arm} hidden-evaluator evidence lacks a passing leakage check")
    return result, meta


def _comparable(a_meta: dict, b_meta: dict) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    if a_meta.get("schema_version") != b_meta.get("schema_version"):
        reasons.append("schema_version")
    for field in ("evaluator_identity_sha256", "scenario_suite_sha256"):
        if not a_meta.get(field) or a_meta.get(field) != b_meta.get(field):
            reasons.append(field)
    if a_meta.get("schema_version") == 3 or b_meta.get("schema_version") == 3:
        if not a_meta.get("runtime_profile_sha256") or a_meta.get("runtime_profile_sha256") != b_meta.get("runtime_profile_sha256"):
            reasons.append("runtime_profile_sha256")
        for field in ("suite_role", "distribution_profile"):
            if a_meta.get(field) != b_meta.get(field):
                reasons.append(field)
    if a_meta.get("host_profile") and b_meta.get("host_profile") and a_meta.get("host_profile") != b_meta.get("host_profile"):
        reasons.append("host_profile")
    a_self = a_meta.get("self_improvement")
    b_self = b_meta.get("self_improvement")
    if bool(a_self) != bool(b_self):
        reasons.append("self_improvement_provenance")
    elif isinstance(a_self, dict) and isinstance(b_self, dict):
        for field in ("generation_id", "controller_identity_sha256"):
            if not a_self.get(field) or a_self.get(field) != b_self.get(field):
                reasons.append(f"self_improvement.{field}")
    return not reasons, reasons


def _legacy_direction(name: str, delta: float) -> str:
    if delta == 0:
        return "unchanged"
    if name in HIGHER_BETTER:
        return "improved" if delta > 0 else "regressed"
    return "improved" if delta < 0 else "regressed"


def _paired_rows(candidate_rows: list[dict], reference_rows: list[dict]) -> tuple[list[dict], list[dict]]:
    def key(row: dict) -> tuple[Any, Any]:
        return (row.get("scenario_id") or row.get("id"), row.get("trial_id"))
    c = {key(r): r for r in candidate_rows}
    r = {key(row): row for row in reference_rows}
    keys = sorted(set(c) & set(r), key=lambda item: (str(item[0]), str(item[1])))
    return [c[k] for k in keys], [r[k] for k in keys]


def _bootstrap_interval(
    metric_name: str,
    candidate_rows: list[dict],
    reference_rows: list[dict],
    seed_material: str,
    iterations: int = 2000,
) -> tuple[float, float] | None:
    crows, rrows = _paired_rows(candidate_rows, reference_rows)
    n = len(crows)
    if n < 2:
        return None
    seed = int(hashlib.sha256(f"{seed_material}:{metric_name}:{n}".encode()).hexdigest()[:16], 16)
    rng = random.Random(seed)
    deltas: list[float] = []
    for _ in range(iterations):
        indices = [rng.randrange(n) for _ in range(n)]
        cm = metrics([crows[i] for i in indices]).get(metric_name)
        rm = metrics([rrows[i] for i in indices]).get(metric_name)
        if cm is not None and rm is not None:
            deltas.append(cm - rm)
    if len(deltas) < max(30, iterations // 4):
        return None
    deltas.sort()
    lo = deltas[int(0.025 * (len(deltas) - 1))]
    hi = deltas[int(0.975 * (len(deltas) - 1))]
    return lo, hi


def _claim_classification(name: str, interval: tuple[float, float] | None, threshold: float) -> str:
    if interval is None:
        return "inconclusive"
    lo, hi = interval
    if lo >= -threshold and hi <= threshold:
        return "practically-unchanged"
    if name in HIGHER_BETTER:
        if lo > threshold:
            return "improved"
        if hi < -threshold:
            return "regressed"
    else:
        if hi < -threshold:
            return "improved"
        if lo > threshold:
            return "regressed"
    return "inconclusive"


def _delta(
    candidate: dict[str, float | None],
    reference: dict[str, float | None],
    comparable: bool,
    candidate_rows: list[dict],
    reference_rows: list[dict],
    candidate_meta: dict,
    practical_threshold: float,
) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    version = candidate_meta.get("schema_version")
    seed_material = ":".join(str(candidate_meta.get(k, "")) for k in ("evaluator_identity_sha256", "scenario_suite_sha256", "runtime_profile_sha256"))
    for name in sorted(HIGHER_BETTER | LOWER_BETTER):
        c = candidate.get(name)
        r = reference.get(name)
        if not comparable:
            out[name] = {"candidate": c, "reference": r, "delta": None, "classification": "not-comparable", "claim_classification": "not-comparable"}
            continue
        if c is None or r is None:
            out[name] = {"candidate": c, "reference": r, "delta": None, "classification": "unmeasured", "claim_classification": "unmeasured"}
            continue
        d = c - r
        legacy = _legacy_direction(name, d)
        interval = _bootstrap_interval(name, candidate_rows, reference_rows, seed_material) if version == 3 else None
        claim = _claim_classification(name, interval, practical_threshold) if version == 3 else "inconclusive"
        out[name] = {
            "candidate": c,
            "reference": r,
            "delta": d,
            "classification": legacy,
            "claim_classification": claim,
            "confidence_interval_95": list(interval) if interval is not None else None,
            "practical_threshold": practical_threshold,
            "paired_trial_count": len(_paired_rows(candidate_rows, reference_rows)[0]),
        }
    return out


def _efficiency_delta(candidate_rows: list[dict], reference_rows: list[dict], comparable: bool) -> dict[str, Any]:
    c = efficiency_metrics(candidate_rows)
    r = efficiency_metrics(reference_rows)
    out: dict[str, Any] = {}
    for name in sorted(c):
        cv, rv = c[name], r[name]
        if not comparable:
            out[name] = {"candidate": cv, "reference": rv, "delta": None, "classification": "not-comparable"}
        elif cv is None or rv is None:
            out[name] = {"candidate": cv, "reference": rv, "delta": None, "classification": "unmeasured"}
        else:
            d = cv - rv
            out[name] = {"candidate": cv, "reference": rv, "delta": d, "classification": "unchanged" if d == 0 else ("improved" if d < 0 else "regressed")}
    return out


def _comparison(cand: dict, cand_meta: dict, ref: dict, ref_meta: dict, practical_threshold: float) -> dict[str, Any]:
    ok, reasons = _comparable(cand_meta, ref_meta)
    cmetrics = metrics(cand["rows"])
    rmetrics = metrics(ref["rows"])
    return {
        "comparable": ok,
        "non_comparable_reasons": reasons,
        "reference_metadata": ref_meta,
        "reference_metrics": rmetrics,
        "capability_delta": _delta(cmetrics, rmetrics, ok, cand["rows"], ref["rows"], cand_meta, practical_threshold),
        "efficiency_delta": _efficiency_delta(cand["rows"], ref["rows"], ok),
        "strong_claim_policy": "v3 repeated paired trials with deterministic bootstrap uncertainty and practical threshold; v2 remains directional-only",
    }


def compare(
    candidate_path: Path,
    baseline_path: Path | None,
    parent_path: Path | None,
    control_path: Path | None,
    length_control_path: Path | None,
    practical_threshold: float = 0.01,
) -> dict[str, Any]:
    cand, cand_meta = _validate_arm(candidate_path, "candidate")
    cand_metrics = metrics(cand["rows"])
    report: dict[str, Any] = {
        "status": "pass",
        "candidate": {"path": str(candidate_path), "metadata": cand_meta, "metrics": cand_metrics, "efficiency_metrics": efficiency_metrics(cand["rows"])},
        "baseline_comparison": None,
        "parent_comparison": None,
        "without_skill_comparison": None,
        "length_control_comparison": None,
        "claim_rules": {
            "regression_claim_source": "baseline" if baseline_path else None,
            "local_attribution_source": "parent" if parent_path else None,
            "incremental_value_claim_source": "without-skill" if control_path else None,
            "context_length_control_source": "length-control" if length_control_path else None,
            "efficiency_metrics_are_separate": True,
            "composite_score": None,
        },
    }
    for path, arm, field in (
        (baseline_path, "baseline", "baseline_comparison"),
        (parent_path, "parent", "parent_comparison"),
        (control_path, "without-skill", "without_skill_comparison"),
        (length_control_path, "length-control", "length_control_comparison"),
    ):
        if path:
            ref, ref_meta = _validate_arm(path, arm)
            report[field] = _comparison(cand, cand_meta, ref, ref_meta, practical_threshold)
    if not any((baseline_path, parent_path, control_path, length_control_path)):
        report["status"] = "fail"
        report["error"] = "at least one reference arm (--baseline, --parent, --without-skill, or --length-control) is required"
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--baseline")
    parser.add_argument("--parent")
    parser.add_argument("--without-skill")
    parser.add_argument("--length-control")
    parser.add_argument("--practical-threshold", type=float, default=0.01)
    parser.add_argument("--json-output")
    args = parser.parse_args()
    try:
        if args.practical_threshold < 0:
            raise ValueError("--practical-threshold must be non-negative")
        report = compare(
            Path(args.candidate),
            Path(args.baseline) if args.baseline else None,
            Path(args.parent) if args.parent else None,
            Path(args.without_skill) if args.without_skill else None,
            Path(args.length_control) if args.length_control else None,
            args.practical_threshold,
        )
    except Exception as exc:
        report = {"status": "fail", "error": str(exc)}
    payload = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.json_output:
        Path(args.json_output).write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0 if report.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
