#!/usr/bin/env python3
"""Validate a grader-calibration profile and compute agreement/bias metrics."""
from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
import json
from pathlib import Path
from typing import Any

from _harness_common import canonical_json_sha256, dump_json


def ratio(num: int, den: int) -> float | None:
    return None if den <= 0 else num / den


def validate(data: Any) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(data, dict):
        return {"status": "fail", "errors": ["profile must be a JSON object"], "warnings": [], "metrics": {}}
    allowed = {"profile_version", "grader_identity", "reference_set_identity", "sample", "bias_probes", "thresholds", "notes"}
    extra = sorted(set(data) - allowed)
    if extra:
        errors.append(f"unknown top-level properties: {extra}")
    if data.get("profile_version") != 1:
        errors.append("profile_version must be 1")
    for key in ("grader_identity", "reference_set_identity"):
        if not isinstance(data.get(key), str) or not data.get(key, "").strip():
            errors.append(f"{key} must be a non-empty string")

    sample = data.get("sample")
    total = agreements = abstentions = 0
    if not isinstance(sample, dict):
        errors.append("sample must be an object")
    else:
        if set(sample) - {"total", "agreements", "abstentions"}:
            errors.append("sample contains unknown properties")
        total, agreements, abstentions = (sample.get("total"), sample.get("agreements"), sample.get("abstentions"))
        if not isinstance(total, int) or isinstance(total, bool) or total < 1:
            errors.append("sample.total must be an integer >= 1")
            total = 0
        for name, value in (("agreements", agreements), ("abstentions", abstentions)):
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                errors.append(f"sample.{name} must be an integer >= 0")
        if isinstance(total, int) and isinstance(agreements, int) and isinstance(abstentions, int) and total >= 0:
            if agreements + abstentions > total:
                errors.append("sample.agreements + sample.abstentions must not exceed sample.total")

    probes = data.get("bias_probes")
    probe_values: dict[str, int] = {}
    probe_fields = ("order_swap_total", "order_swap_consistent", "verbosity_total", "verbosity_consistent")
    if not isinstance(probes, dict):
        errors.append("bias_probes must be an object")
    else:
        if set(probes) - set(probe_fields):
            errors.append("bias_probes contains unknown properties")
        for key in probe_fields:
            value = probes.get(key)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                errors.append(f"bias_probes.{key} must be an integer >= 0")
                value = 0
            probe_values[key] = value
        if probe_values.get("order_swap_consistent", 0) > probe_values.get("order_swap_total", 0):
            errors.append("order_swap_consistent must not exceed order_swap_total")
        if probe_values.get("verbosity_consistent", 0) > probe_values.get("verbosity_total", 0):
            errors.append("verbosity_consistent must not exceed verbosity_total")

    thresholds = data.get("thresholds")
    threshold_fields = ("min_agreement", "min_coverage", "min_order_swap_consistency", "min_verbosity_consistency")
    threshold_values: dict[str, float] = {}
    if not isinstance(thresholds, dict):
        errors.append("thresholds must be an object")
    else:
        if set(thresholds) - set(threshold_fields):
            errors.append("thresholds contains unknown properties")
        for key in threshold_fields:
            value = thresholds.get(key)
            if not isinstance(value, (int, float)) or isinstance(value, bool) or not 0 <= float(value) <= 1:
                errors.append(f"thresholds.{key} must be between 0 and 1")
                value = 0.0
            threshold_values[key] = float(value)

    non_abstained = total - abstentions if isinstance(total, int) and isinstance(abstentions, int) else 0
    metrics = {
        "agreement": ratio(agreements, non_abstained),
        "coverage": ratio(non_abstained, total),
        "order_swap_consistency": ratio(probe_values.get("order_swap_consistent", 0), probe_values.get("order_swap_total", 0)),
        "verbosity_consistency": ratio(probe_values.get("verbosity_consistent", 0), probe_values.get("verbosity_total", 0)),
    }
    checks = {
        "agreement": metrics["agreement"] is not None and metrics["agreement"] >= threshold_values.get("min_agreement", 0),
        "coverage": metrics["coverage"] is not None and metrics["coverage"] >= threshold_values.get("min_coverage", 0),
        "order_swap": metrics["order_swap_consistency"] is not None and metrics["order_swap_consistency"] >= threshold_values.get("min_order_swap_consistency", 0),
        "verbosity": metrics["verbosity_consistency"] is not None and metrics["verbosity_consistency"] >= threshold_values.get("min_verbosity_consistency", 0),
    }
    if not errors:
        if probe_values.get("order_swap_total", 0) == 0:
            warnings.append("no order-swap bias probes were supplied")
        if probe_values.get("verbosity_total", 0) == 0:
            warnings.append("no verbosity-bias probes were supplied")
        for name, passed in checks.items():
            if not passed:
                errors.append(f"calibration threshold failed: {name}")
    identity = canonical_json_sha256({k: data.get(k) for k in sorted(allowed - {"notes"})}) if isinstance(data, dict) else None
    return {"status": "pass" if not errors else "fail", "identity_sha256": identity, "errors": errors, "warnings": warnings, "metrics": metrics, "checks": checks}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("profile")
    ap.add_argument("--json", dest="json_out")
    args = ap.parse_args()
    try:
        data = json.loads(Path(args.profile).read_text(encoding="utf-8"))
        report = validate(data)
    except Exception as exc:
        report = {"status": "fail", "errors": [str(exc)], "warnings": [], "metrics": {}, "checks": {}}
    dump_json(report, args.json_out)
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
