#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
from typing import Any

_EVIDENCE_MODULE_PATH = Path(__file__).with_name("validate_activation_evidence.py")
_SPEC = importlib.util.spec_from_file_location("_activation_evidence_validator", _EVIDENCE_MODULE_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError(f"unable to load sibling evidence validator: {_EVIDENCE_MODULE_PATH}")
_EVIDENCE_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_EVIDENCE_MODULE)
validate_evidence = _EVIDENCE_MODULE.validate_evidence

BINARY_EXPECTED = {
    "activate": True,
    "activate-constrained": True,
    "do-not-activate": False,
}
AUTO_INVOCATION = {"implicit", "contextual"}


def canonical_suite_hash(suite: dict[str, Any]) -> str:
    payload = json.dumps(suite, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _case_map(evidence: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {case.get("id"): case for case in evidence.get("cases", []) if isinstance(case, dict) and isinstance(case.get("id"), str)}


def _wilson(successes: int, total: int) -> list[float] | None:
    if total <= 0:
        return None
    z = 1.959963984540054
    p = successes / total
    denom = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denom
    margin = z * math.sqrt((p * (1 - p) / total) + (z * z / (4 * total * total))) / denom
    return [max(0.0, center - margin), min(1.0, center + margin)]


def _rate(successes: int, total: int) -> dict[str, Any]:
    return {
        "successes": successes,
        "total": total,
        "rate": (successes / total) if total else None,
        "wilson_95": _wilson(successes, total),
    }


def _trial_metrics(suite: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any] | None:
    cases = _case_map(evidence)
    tp = fp = tn = fn = 0
    route_successes = route_total = 0
    explicit_successes = explicit_total = 0
    abstain_successes = abstain_total = 0
    near_miss_activations = near_miss_total = 0
    case_rates: dict[str, Any] = {}

    for scenario in suite.get("scenarios", []):
        sid = scenario.get("id")
        case = cases.get(sid)
        if not case:
            return None
        trials = case.get("trials")
        if not isinstance(trials, list) or not trials:
            return None
        expected_route = scenario.get("expected_route")
        expected_binary = BINARY_EXPECTED.get(expected_route)
        route_matches = activation_count = 0
        for trial in trials:
            if not isinstance(trial, dict) or not isinstance(trial.get("activated"), bool):
                return None
            observed_route = trial.get("observed_route")
            if not isinstance(observed_route, str):
                return None
            activated = trial["activated"]
            activation_count += int(activated)
            if observed_route == expected_route:
                route_matches += 1
            route_successes += int(observed_route == expected_route)
            route_total += 1

            if scenario.get("invocation_mode") == "explicit":
                explicit_successes += int(observed_route == expected_route)
                explicit_total += 1

            if scenario.get("invocation_mode") in AUTO_INVOCATION and expected_binary is not None:
                if expected_binary and activated:
                    tp += 1
                elif expected_binary and not activated:
                    fn += 1
                elif not expected_binary and activated:
                    fp += 1
                else:
                    tn += 1

            negative_kind = scenario.get("negative_kind")
            if negative_kind == "abstain":
                abstain_total += 1
                abstain_successes += int(not activated)
            elif negative_kind == "alternative-owner":
                near_miss_total += 1
                near_miss_activations += int(activated)

        case_rates[sid] = {
            "trial_count": len(trials),
            "trigger_rate": activation_count / len(trials),
            "expected_route_match_rate": route_matches / len(trials),
            "invocation_mode": scenario.get("invocation_mode"),
            "negative_kind": scenario.get("negative_kind"),
        }

    precision_total = tp + fp
    recall_total = tp + fn
    precision = _rate(tp, precision_total)
    recall = _rate(tp, recall_total)
    abstention = _rate(abstain_successes, abstain_total)
    near_miss_false_activation = _rate(near_miss_activations, near_miss_total)
    explicit_accuracy = _rate(explicit_successes, explicit_total)
    route_accuracy = _rate(route_successes, route_total)
    return {
        "auto_routing_confusion": {"tp": tp, "fp": fp, "tn": tn, "fn": fn},
        "auto_activation_precision": precision,
        "auto_activation_recall": recall,
        "overall_expected_route_accuracy": route_accuracy,
        "explicit_route_accuracy": explicit_accuracy,
        "abstention_accuracy": abstention,
        "near_miss_false_activation_rate": near_miss_false_activation,
        "case_rates": case_rates,
    }


def _delta(left: dict[str, Any], right: dict[str, Any], key: str) -> float | None:
    lv = left.get(key, {}).get("rate")
    rv = right.get(key, {}).get("rate")
    if lv is None or rv is None:
        return None
    return rv - lv


def compare(suite: dict[str, Any], baseline: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []
    expected_hash = canonical_suite_hash(suite)

    baseline_validation = validate_evidence(baseline, suite)
    candidate_validation = validate_evidence(candidate, suite)
    for label, validation in (("baseline", baseline_validation), ("candidate", candidate_validation)):
        for item in validation.get("errors", []):
            errors.append({"code": f"comparison/{item['code']}", "subject": label, "evidence": item})

    for label, evidence in (("baseline", baseline), ("candidate", candidate)):
        if evidence.get("suite_sha256") != expected_hash:
            errors.append({"code": "comparison/suite-identity", "subject": label, "evidence": {"expected": expected_hash, "actual": evidence.get("suite_sha256")}})

    if baseline.get("evaluator_sha256") != candidate.get("evaluator_sha256") or not baseline.get("evaluator_sha256"):
        errors.append({"code": "comparison/evaluator-identity", "subject": "baseline,candidate", "evidence": {"baseline": baseline.get("evaluator_sha256"), "candidate": candidate.get("evaluator_sha256")}})

    base_fp = baseline_validation.get("routing_fingerprint_sha256")
    cand_fp = candidate_validation.get("routing_fingerprint_sha256")
    if not base_fp or base_fp != cand_fp:
        errors.append({"code": "comparison/routing-fingerprint", "subject": "baseline,candidate", "evidence": {"baseline": base_fp, "candidate": cand_fp}})

    base_trials = baseline.get("trial_policy")
    cand_trials = candidate.get("trial_policy")
    if base_trials != cand_trials:
        errors.append({"code": "comparison/trial-policy", "subject": "baseline,candidate", "evidence": {"baseline": base_trials, "candidate": cand_trials}})

    eligible = (
        not errors
        and baseline.get("execution_kind") == "host-routing"
        and candidate.get("execution_kind") == "host-routing"
        and baseline.get("evidence_status") == "executed"
        and candidate.get("evidence_status") == "executed"
    )

    behavioral: dict[str, Any] = {
        "status": "not-claimable",
        "reason": "requires v2 executed host-routing evidence with identical frozen suite, evaluator, trial policy, and routing fingerprint",
        "repeated_trials": False,
        "baseline": None,
        "candidate": None,
        "deltas": None,
        "regressions": None,
    }

    if eligible:
        baseline_metrics = _trial_metrics(suite, baseline)
        candidate_metrics = _trial_metrics(suite, candidate)
        if baseline_metrics is None or candidate_metrics is None:
            behavioral["reason"] = "host-routing trial evidence is incomplete"
        else:
            repeated = int(baseline.get("trial_policy", {}).get("trials_per_case", 0)) >= 2
            regressions = []
            for sid, base_case in baseline_metrics["case_rates"].items():
                cand_case = candidate_metrics["case_rates"][sid]
                if cand_case["expected_route_match_rate"] < base_case["expected_route_match_rate"]:
                    regressions.append({
                        "id": sid,
                        "baseline_expected_route_match_rate": base_case["expected_route_match_rate"],
                        "candidate_expected_route_match_rate": cand_case["expected_route_match_rate"],
                    })
            behavioral = {
                "status": "measured-repeated" if repeated else "measured-single-run",
                "reason": None if repeated else "single-run routing evidence is measured observation, not stochastic reliability evidence",
                "repeated_trials": repeated,
                "baseline": baseline_metrics,
                "candidate": candidate_metrics,
                "deltas": {
                    "auto_activation_precision": _delta(baseline_metrics, candidate_metrics, "auto_activation_precision"),
                    "auto_activation_recall": _delta(baseline_metrics, candidate_metrics, "auto_activation_recall"),
                    "abstention_accuracy": _delta(baseline_metrics, candidate_metrics, "abstention_accuracy"),
                    "near_miss_false_activation_rate": _delta(baseline_metrics, candidate_metrics, "near_miss_false_activation_rate"),
                    "overall_expected_route_accuracy": _delta(baseline_metrics, candidate_metrics, "overall_expected_route_accuracy"),
                },
                "regressions": regressions,
            }

    return {
        "status": "fail" if errors else "pass",
        "suite_sha256": expected_hash,
        "evaluator_sha256": baseline.get("evaluator_sha256") if not errors else None,
        "routing_fingerprint_sha256": base_fp if not errors else None,
        "errors": errors,
        "behavioral_comparison": behavioral,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare v2 baseline/candidate activation evidence without mixing explicit invocation, routing drift, or single-run reliability claims.")
    parser.add_argument("--suite", required=True)
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--json")
    args = parser.parse_args()

    suite = json.loads(Path(args.suite).read_text(encoding="utf-8"))
    baseline = json.loads(Path(args.baseline).read_text(encoding="utf-8"))
    candidate = json.loads(Path(args.candidate).read_text(encoding="utf-8"))
    report = compare(suite, baseline, candidate)
    payload = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.json:
        Path(args.json).write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
