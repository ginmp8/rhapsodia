#!/usr/bin/env python3
"""Compare benchmark behavioral arms with strict identity and capability-delta gates."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from validate_scenario_results import load_json, validate_payload

HIGHER_BETTER = {"activation_precision", "activation_recall", "output_conformance", "robustness"}
LOWER_BETTER = {"rework_rate"}


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
    for field in ("evaluator_identity_sha256", "scenario_suite_sha256"):
        if not a_meta.get(field) or a_meta.get(field) != b_meta.get(field):
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


def _delta(candidate: dict[str, float | None], reference: dict[str, float | None], comparable: bool) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for name in sorted(HIGHER_BETTER | LOWER_BETTER):
        c = candidate.get(name)
        r = reference.get(name)
        if not comparable:
            out[name] = {"candidate": c, "reference": r, "delta": None, "classification": "not-comparable"}
            continue
        if c is None or r is None:
            out[name] = {"candidate": c, "reference": r, "delta": None, "classification": "unmeasured"}
            continue
        d = c - r
        if d == 0:
            cls = "unchanged"
        elif name in HIGHER_BETTER:
            cls = "improved" if d > 0 else "regressed"
        else:
            cls = "improved" if d < 0 else "regressed"
        out[name] = {"candidate": c, "reference": r, "delta": d, "classification": cls}
    return out


def compare(candidate_path: Path, baseline_path: Path | None, parent_path: Path | None, control_path: Path | None) -> dict[str, Any]:
    cand, cand_meta = _validate_arm(candidate_path, "candidate")
    cand_metrics = metrics(cand["rows"])
    report: dict[str, Any] = {
        "status": "pass",
        "candidate": {"path": str(candidate_path), "metadata": cand_meta, "metrics": cand_metrics},
        "baseline_comparison": None,
        "parent_comparison": None,
        "without_skill_comparison": None,
        "claim_rules": {
            "regression_claim_source": "baseline" if baseline_path else None,
            "local_attribution_source": "parent" if parent_path else None,
            "incremental_value_claim_source": "without-skill" if control_path else None,
        },
    }
    if baseline_path:
        base, base_meta = _validate_arm(baseline_path, "baseline")
        ok, reasons = _comparable(cand_meta, base_meta)
        bmetrics = metrics(base["rows"])
        report["baseline_comparison"] = {
            "comparable": ok,
            "non_comparable_reasons": reasons,
            "reference_metadata": base_meta,
            "reference_metrics": bmetrics,
            "capability_delta": _delta(cand_metrics, bmetrics, ok),
        }
    if parent_path:
        parent, parent_meta = _validate_arm(parent_path, "parent")
        ok, reasons = _comparable(cand_meta, parent_meta)
        pmetrics = metrics(parent["rows"])
        report["parent_comparison"] = {
            "comparable": ok,
            "non_comparable_reasons": reasons,
            "reference_metadata": parent_meta,
            "reference_metrics": pmetrics,
            "capability_delta": _delta(cand_metrics, pmetrics, ok),
        }
    if control_path:
        ctrl, ctrl_meta = _validate_arm(control_path, "without-skill")
        ok, reasons = _comparable(cand_meta, ctrl_meta)
        cmetrics = metrics(ctrl["rows"])
        report["without_skill_comparison"] = {
            "comparable": ok,
            "non_comparable_reasons": reasons,
            "reference_metadata": ctrl_meta,
            "reference_metrics": cmetrics,
            "capability_delta": _delta(cand_metrics, cmetrics, ok),
        }
    if not baseline_path and not parent_path and not control_path:
        report["status"] = "fail"
        report["error"] = "at least one reference arm (--baseline, --parent, or --without-skill) is required"
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--baseline")
    parser.add_argument("--parent")
    parser.add_argument("--without-skill")
    parser.add_argument("--json-output")
    args = parser.parse_args()
    try:
        report = compare(
            Path(args.candidate),
            Path(args.baseline) if args.baseline else None,
            Path(args.parent) if args.parent else None,
            Path(args.without_skill) if args.without_skill else None,
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
