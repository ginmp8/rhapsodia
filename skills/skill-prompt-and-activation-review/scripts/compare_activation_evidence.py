#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

BINARY_EXPECTED = {
    "activate": True,
    "activate-constrained": True,
    "do-not-activate": False,
}


def canonical_suite_hash(suite: dict) -> str:
    payload = json.dumps(suite, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _case_map(evidence: dict) -> dict:
    return {case.get("id"): case for case in evidence.get("cases", []) if isinstance(case, dict)}


def _confusion(suite: dict, evidence: dict) -> dict | None:
    cases = _case_map(evidence)
    tp = fp = tn = fn = 0
    for scenario in suite.get("scenarios", []):
        expected = BINARY_EXPECTED.get(scenario.get("expected_route"))
        if expected is None:
            continue
        case = cases.get(scenario.get("id"))
        if not case or not isinstance(case.get("activated"), bool):
            return None
        observed = case["activated"]
        if expected and observed:
            tp += 1
        elif expected and not observed:
            fn += 1
        elif not expected and observed:
            fp += 1
        else:
            tn += 1
    precision = tp / (tp + fp) if (tp + fp) else None
    recall = tp / (tp + fn) if (tp + fn) else None
    return {"tp": tp, "fp": fp, "tn": tn, "fn": fn, "precision": precision, "recall": recall}


def compare(suite: dict, baseline: dict, candidate: dict) -> dict:
    errors = []
    expected_hash = canonical_suite_hash(suite)
    for label, evidence in (("baseline", baseline), ("candidate", candidate)):
        if evidence.get("suite_sha256") != expected_hash:
            errors.append({"code": "comparison/suite-identity", "subject": label, "evidence": {"expected": expected_hash, "actual": evidence.get("suite_sha256")}})
        visibility = evidence.get("evaluator_visibility")
        if visibility == "hidden" and evidence.get("candidate_saw_evaluator_only_assets") is not False:
            errors.append({"code": "comparison/evaluator-leakage", "subject": label, "evidence": {"evaluator_visibility": visibility, "candidate_saw_evaluator_only_assets": evidence.get("candidate_saw_evaluator_only_assets")}})
    if not baseline.get("evaluator_sha256") or baseline.get("evaluator_sha256") != candidate.get("evaluator_sha256"):
        errors.append({"code": "comparison/evaluator-identity", "subject": "baseline,candidate", "evidence": {"baseline": baseline.get("evaluator_sha256"), "candidate": candidate.get("evaluator_sha256")}})
    if baseline.get("host_profile") and candidate.get("host_profile") and baseline.get("host_profile") != candidate.get("host_profile"):
        errors.append({"code": "comparison/host-profile", "subject": "baseline,candidate", "evidence": {"baseline": baseline.get("host_profile"), "candidate": candidate.get("host_profile")}})

    suite_ids = {scenario.get("id") for scenario in suite.get("scenarios", [])}
    for label, evidence in (("baseline", baseline), ("candidate", candidate)):
        case_ids = set(_case_map(evidence))
        if case_ids != suite_ids:
            errors.append({"code": "comparison/case-set", "subject": label, "evidence": {"missing": sorted(suite_ids - case_ids), "extra": sorted(case_ids - suite_ids)}})

    eligible = (
        not errors
        and baseline.get("execution_kind") == "host-routing"
        and candidate.get("execution_kind") == "host-routing"
        and baseline.get("evidence_status") == "executed"
        and candidate.get("evidence_status") == "executed"
    )

    behavioral = {
        "status": "not-claimable",
        "reason": "requires identical frozen suite/evaluator plus executed host-routing evidence for both arms",
        "baseline": None,
        "candidate": None,
        "activation_precision_delta": None,
        "activation_recall_delta": None,
        "regressions": None,
    }
    if eligible:
        baseline_metrics = _confusion(suite, baseline)
        candidate_metrics = _confusion(suite, candidate)
        if baseline_metrics is not None and candidate_metrics is not None:
            base_cases = _case_map(baseline)
            cand_cases = _case_map(candidate)
            regressions = []
            for scenario in suite.get("scenarios", []):
                expected_route = scenario.get("expected_route")
                base_route = base_cases[scenario["id"]].get("observed_route")
                cand_route = cand_cases[scenario["id"]].get("observed_route")
                if base_route == expected_route and cand_route != expected_route:
                    regressions.append(scenario["id"])
            precision_delta = None
            if baseline_metrics["precision"] is not None and candidate_metrics["precision"] is not None:
                precision_delta = candidate_metrics["precision"] - baseline_metrics["precision"]
            recall_delta = None
            if baseline_metrics["recall"] is not None and candidate_metrics["recall"] is not None:
                recall_delta = candidate_metrics["recall"] - baseline_metrics["recall"]
            behavioral = {
                "status": "measured",
                "reason": None,
                "baseline": baseline_metrics,
                "candidate": candidate_metrics,
                "activation_precision_delta": precision_delta,
                "activation_recall_delta": recall_delta,
                "regressions": regressions,
            }
        else:
            behavioral["reason"] = "host-routing evidence is incomplete for one or more binary activation scenarios"

    return {
        "status": "fail" if errors else "pass",
        "suite_sha256": expected_hash,
        "evaluator_sha256": baseline.get("evaluator_sha256") if not errors else None,
        "errors": errors,
        "behavioral_comparison": behavioral,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare baseline/candidate activation evidence without fabricating behavioral metrics.")
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
        Path(getattr(args, "json")).write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
