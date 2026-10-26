#!/usr/bin/env python3
"""Conservative, read-only numeric comparator for software-improvement-loop.

This helper evaluates supplied benchmark samples. It does not execute benchmarks,
verify source identities, inspect Git, or attest functional correctness.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import statistics
import sys
import tempfile
from typing import Any


INPUT_SCHEMA = "software-improvement-loop.metric-input/v1"
OUTPUT_SCHEMA = "software-improvement-loop.metric-report/v1"
MAX_INPUT_BYTES = 2_000_000
MAX_METRICS = 64
MAX_SAMPLES = 5000
MIN_SAMPLES = 5


class InvalidEvidence(ValueError):
    """The supplied input violates the comparison protocol."""


def unique_object_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise InvalidEvidence(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def reject_constant(value: str) -> None:
    raise InvalidEvidence(f"non-finite JSON constant: {value}")


def require_object(value: Any, where: str, required: set[str], allowed: set[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise InvalidEvidence(f"{where} must be an object")
    missing = required - value.keys()
    extra = value.keys() - allowed
    if missing:
        raise InvalidEvidence(f"{where} missing: {', '.join(sorted(missing))}")
    if extra:
        raise InvalidEvidence(f"{where} unknown keys: {', '.join(sorted(extra))}")
    return value


def require_text(value: Any, where: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 256:
        raise InvalidEvidence(f"{where} must be a nonempty string (at most 256 chars)")
    return value


def number(value: Any, where: str, low: float = 0.0, high: float = 100.0) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise InvalidEvidence(f"{where} must be numeric")
    try:
        result = float(value)
    except (ValueError, OverflowError) as exc:
        raise InvalidEvidence(f"{where} is outside supported numeric range") from exc
    if not math.isfinite(result) or not low <= result <= high:
        raise InvalidEvidence(f"{where} must be finite in [{low}, {high}]")
    return result


def samples(value: Any, where: str) -> list[float]:
    if not isinstance(value, list) or not MIN_SAMPLES <= len(value) <= MAX_SAMPLES:
        raise InvalidEvidence(f"{where} must contain {MIN_SAMPLES}..{MAX_SAMPLES} samples")
    return [number(v, f"{where}[{i}]", low=1e-12, high=1e18) for i, v in enumerate(value)]


def identity(value: Any, where: str) -> dict[str, str]:
    keys = {"id", "environment_id", "workload_id", "harness_id"}
    obj = require_object(value, where, keys, keys)
    return {key: require_text(obj[key], f"{where}.{key}") for key in sorted(keys)}


def validate_evidence(data: Any) -> dict[str, Any]:
    keys = {"schema", "experiment_id", "baseline", "candidate", "metrics"}
    payload = require_object(data, "input", keys, keys)
    if payload["schema"] != INPUT_SCHEMA:
        raise InvalidEvidence(f"schema must be {INPUT_SCHEMA}")
    experiment_id = require_text(payload["experiment_id"], "experiment_id")
    baseline = identity(payload["baseline"], "baseline")
    candidate = identity(payload["candidate"], "candidate")
    if baseline["id"] == candidate["id"]:
        raise InvalidEvidence("baseline.id and candidate.id must differ")
    for key in ("environment_id", "workload_id", "harness_id"):
        if baseline[key] != candidate[key]:
            raise InvalidEvidence(f"baseline/candidate mismatch: {key}")

    raw_metrics = payload["metrics"]
    if not isinstance(raw_metrics, list) or not 1 <= len(raw_metrics) <= MAX_METRICS:
        raise InvalidEvidence(f"metrics must contain 1..{MAX_METRICS} entries")
    metric_keys = {
        "id", "role", "direction", "unit", "min_improvement_pct",
        "max_regression_pct", "noise_floor_pct", "baseline_samples", "candidate_samples",
    }
    common = metric_keys - {"min_improvement_pct"}
    clean_metrics: list[dict[str, Any]] = []
    ids: set[str] = set()
    target_count = 0
    for i, raw in enumerate(raw_metrics):
        where = f"metrics[{i}]"
        obj = require_object(raw, where, common, metric_keys)
        mid = require_text(obj["id"], f"{where}.id")
        if mid in ids:
            raise InvalidEvidence(f"duplicate metric id: {mid}")
        ids.add(mid)
        role = obj["role"]
        direction = obj["direction"]
        if role not in ("target", "guardrail"):
            raise InvalidEvidence(f"{where}.role must be target or guardrail")
        if direction not in ("lower", "higher"):
            raise InvalidEvidence(f"{where}.direction must be lower or higher")
        if role == "target":
            target_count += 1
            if "min_improvement_pct" not in obj:
                raise InvalidEvidence(f"{where}.min_improvement_pct is required for a target")
            improvement = number(obj["min_improvement_pct"], f"{where}.min_improvement_pct")
        else:
            if "min_improvement_pct" in obj:
                raise InvalidEvidence(f"{where}.min_improvement_pct is not allowed for a guardrail")
            improvement = None
        clean_metrics.append({
            "id": mid,
            "role": role,
            "direction": direction,
            "unit": require_text(obj["unit"], f"{where}.unit"),
            "min_improvement_pct": improvement,
            "max_regression_pct": number(obj["max_regression_pct"], f"{where}.max_regression_pct"),
            "noise_floor_pct": number(obj["noise_floor_pct"], f"{where}.noise_floor_pct"),
            "baseline_samples": samples(obj["baseline_samples"], f"{where}.baseline_samples"),
            "candidate_samples": samples(obj["candidate_samples"], f"{where}.candidate_samples"),
        })
    if target_count == 0:
        raise InvalidEvidence("at least one target metric is required")
    return {
        "experiment_id": experiment_id,
        "baseline": baseline,
        "candidate": candidate,
        "metrics": clean_metrics,
    }


def relative_mad_pct(values: list[float], med: float) -> float:
    mad = statistics.median(abs(value - med) for value in values)
    return 100.0 * mad / med


def analyze_metric(metric: dict[str, Any]) -> dict[str, Any]:
    baseline_values, candidate_values = metric["baseline_samples"], metric["candidate_samples"]
    bmed = statistics.median(baseline_values)
    cmed = statistics.median(candidate_values)
    # Positive inputs and bounded floats prevent division by zero.
    improvement_pct = 100.0 * ((bmed - cmed) / bmed if metric["direction"] == "lower" else (cmed - bmed) / bmed)
    noise_margin = max(
        metric["noise_floor_pct"],
        3.0 * relative_mad_pct(baseline_values, bmed),
        3.0 * relative_mad_pct(candidate_values, cmed),
    )
    reg_limit = metric["max_regression_pct"]
    if improvement_pct < -(reg_limit + noise_margin):
        status = "regression"
    elif metric["role"] == "guardrail":
        status = "met" if improvement_pct >= -reg_limit + noise_margin else "inconclusive"
    else:
        min_gain = metric["min_improvement_pct"]
        if improvement_pct >= min_gain + noise_margin:
            status = "met"
        elif improvement_pct < min_gain - noise_margin:
            status = "unmet"
        else:
            status = "inconclusive"

    return {
        "id": metric["id"],
        "role": metric["role"],
        "direction": metric["direction"],
        "unit": metric["unit"],
        "baseline_median": bmed,
        "candidate_median": cmed,
        "baseline_sample_count": len(baseline_values),
        "candidate_sample_count": len(candidate_values),
        "improvement_pct": round(improvement_pct, 6),
        "noise_margin_pct": round(noise_margin, 6),
        "metric_status": status,
    }


def evaluate(data: Any, raw_sha256: str) -> dict[str, Any]:
    validated = validate_evidence(data)
    metric_results = [analyze_metric(m) for m in validated["metrics"]]
    statuses = {m["metric_status"] for m in metric_results}
    gate = (
        "fail" if statuses.intersection({"regression", "unmet"})
        else "inconclusive" if "inconclusive" in statuses
        else "pass"
    )
    return {
        "schema": OUTPUT_SCHEMA,
        "experiment_id": validated["experiment_id"],
        "source_sha256": raw_sha256,
        "baseline": validated["baseline"],
        "candidate": validated["candidate"],
        "gate": gate,
        "metric_results": metric_results,
        "scope_of_proof": "Numeric heuristic only; does not prove tests, code correctness, source identity, statistical significance or safety.",
    }


def read_input(path: Path) -> tuple[Any, str]:
    try:
        if path.stat().st_size > MAX_INPUT_BYTES:
            raise InvalidEvidence(f"input exceeds {MAX_INPUT_BYTES} bytes")
        raw = path.read_bytes()
    except OSError as exc:
        raise InvalidEvidence(f"cannot read input: {exc}") from exc
    if len(raw) > MAX_INPUT_BYTES:
        raise InvalidEvidence(f"input exceeds {MAX_INPUT_BYTES} bytes")
    try:
        data = json.loads(raw, object_pairs_hook=unique_object_pairs, parse_constant=reject_constant)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise InvalidEvidence(f"invalid JSON: {exc}") from exc
    return data, hashlib.sha256(raw).hexdigest()


def write_atomic(output: Path, source: Path, result: dict[str, Any]) -> None:
    # A bad candidate must not overwrite good evidence; preflight before writes.
    if output.resolve() == source.resolve():
        raise InvalidEvidence("output may not overwrite input")
    if output.is_symlink():
        raise InvalidEvidence("output may not be a symlink")
    if output.exists():
        raise InvalidEvidence("output already exists; choose a unique report path")
    if not output.parent.is_dir():
        raise InvalidEvidence("output parent must exist")
    target_dir = output.parent.resolve()
    staged: str | None = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".tmp", prefix=".metrics-", dir=target_dir, delete=False) as handle:
            staged = handle.name
            json.dump(result, handle, indent=2, sort_keys=True, allow_nan=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(staged, output)
    except OSError as exc:
        raise InvalidEvidence(f"cannot write report: {exc}") from exc
    finally:
        if staged and os.path.exists(staged):
            os.unlink(staged)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="JSON evidence with baseline/candidate samples")
    parser.add_argument("--out", type=Path, help="Write metric-only report atomically to this path")
    args = parser.parse_args(argv)
    try:
        data, digest = read_input(args.input)
        report = evaluate(data, digest)
        if args.out:
            write_atomic(args.out, args.input, report)
            print(f"metric gate: {report['gate']}; report: {args.out}")
        else:
            print(json.dumps(report, indent=2, sort_keys=True, allow_nan=False))
        return 0 if report["gate"] == "pass" else 2
    except InvalidEvidence as exc:
        print(f"invalid evidence: {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
