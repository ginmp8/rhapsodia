#!/usr/bin/env python3
"""Evaluate context selection against frozen path-level fixtures."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def ratio(num: int, den: int, empty: float) -> float:
    return empty if den == 0 else num / den


def f1(precision: float, recall: float) -> float:
    return 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)


def evaluate_case(case: dict[str, Any]) -> dict[str, Any]:
    available = set(case.get("available_paths", []))
    relevant = set(case.get("expected_relevant", []))
    selected_rows = case.get("selected", [])
    selected = [row["path"] for row in selected_rows]
    selected_set = set(selected)
    selected_cost = sum(int(row.get("cost", 0)) for row in selected_rows)
    budget = int(case.get("budget", 0))
    abstain = bool(case.get("abstain", False))

    unsupported = selected_set - available if available else set()
    tp = len(selected_set & relevant)
    fp = len(selected_set - relevant)
    fn = len(relevant - selected_set)

    no_gold = len(relevant) == 0
    if no_gold:
        p = r = score_f1 = None
        no_gold_correct = abstain and len(selected_set) == 0
        budgeted_yield = None
    else:
        p = ratio(tp, len(selected_set), 0.0)
        r = ratio(tp, len(relevant), 0.0)
        score_f1 = f1(p, r)
        penalty = 1.0 if selected_cost <= budget or selected_cost == 0 else budget / selected_cost
        budgeted_yield = r * penalty
        no_gold_correct = None

    unsupported_rate = ratio(len(unsupported), len(selected_set), 0.0)
    result = {
        "id": case["id"],
        "no_gold": no_gold,
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": p,
        "recall": r,
        "f1": score_f1,
        "selected_cost": selected_cost,
        "budget": budget,
        "budget_compliant": selected_cost <= budget,
        "budgeted_yield": budgeted_yield,
        "unsupported_selection_rate": unsupported_rate,
        "unsupported_paths": sorted(unsupported),
        "abstain": abstain,
        "no_gold_correct": no_gold_correct,
    }

    gates = case.get("gates", {})
    failures: list[str] = []
    if no_gold:
        if gates.get("require_no_gold_correct", True) and not no_gold_correct:
            failures.append("no_gold_incorrect")
    else:
        for name, actual in (("min_precision", p), ("min_recall", r), ("min_f1", score_f1), ("min_budgeted_yield", budgeted_yield)):
            if name in gates and actual is not None and actual < float(gates[name]):
                failures.append(name)
    if "max_unsupported_rate" in gates and unsupported_rate > float(gates["max_unsupported_rate"]):
        failures.append("max_unsupported_rate")
    if gates.get("require_budget_compliant", False) and not result["budget_compliant"]:
        failures.append("budget_compliance")
    result["status"] = "pass" if not failures else "fail"
    result["failures"] = failures
    return result


def aggregate(results: list[dict[str, Any]]) -> dict[str, Any]:
    positives = [r for r in results if not r["no_gold"]]
    no_gold = [r for r in results if r["no_gold"]]
    tp = sum(r["tp"] for r in positives)
    fp = sum(r["fp"] for r in positives)
    fn = sum(r["fn"] for r in positives)
    p = ratio(tp, tp + fp, 0.0)
    r = ratio(tp, tp + fn, 0.0)
    return {
        "positive_case_count": len(positives),
        "no_gold_case_count": len(no_gold),
        "micro_precision": p,
        "micro_recall": r,
        "micro_f1": f1(p, r),
        "mean_budgeted_yield": ratio(sum(x["budgeted_yield"] or 0.0 for x in positives), len(positives), 0.0),
        "mean_unsupported_selection_rate": ratio(sum(x["unsupported_selection_rate"] for x in results), len(results), 0.0),
        "no_gold_accuracy": ratio(sum(1 for x in no_gold if x["no_gold_correct"]), len(no_gold), 1.0),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("fixture", help="JSON fixture file")
    ap.add_argument("--json", dest="json_output", help="optional JSON report path")
    args = ap.parse_args()
    payload = json.loads(Path(args.fixture).read_text(encoding="utf-8"))
    if payload.get("schema_version") != "1.0" or not isinstance(payload.get("cases"), list):
        raise SystemExit("invalid fixture: expected schema_version 1.0 and cases array")
    results = [evaluate_case(case) for case in payload["cases"]]
    status = "pass" if all(r["status"] == "pass" for r in results) else "fail"
    report = {"status": status, "schema_version": "1.0", "cases": results, "aggregate": aggregate(results)}
    if args.json_output:
        Path(args.json_output).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
