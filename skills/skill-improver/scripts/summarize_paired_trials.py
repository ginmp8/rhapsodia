#!/usr/bin/env python3
"""Summarize paired no-skill/parent/candidate trial evidence without third-party deps."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

ARMS = ("no_skill", "parent", "candidate")


def mean(values: list[float]) -> float:
    return sum(values) / len(values)


def exact_two_sided_sign_p(wins: int, losses: int) -> float | None:
    n = wins + losses
    if n == 0:
        return None
    tail = min(wins, losses)
    prob = sum(math.comb(n, i) for i in range(tail + 1)) / (2 ** n)
    return min(1.0, 2.0 * prob)


def summarize(data: Any, k: int) -> dict[str, Any]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return {"status": "fail", "errors": ["root:expected-object"]}
    if data.get("evidence_version") != 1:
        errors.append("evidence_version:expected-1")
    metric = data.get("metric")
    if not isinstance(metric, dict):
        errors.append("metric:expected-object")
        metric = {}
    direction = metric.get("direction")
    if direction not in {"higher-is-better", "lower-is-better"}:
        errors.append("metric.direction:invalid")
    binary = metric.get("binary") is True

    runtime = data.get("runtime_identity")
    if not isinstance(runtime, dict):
        errors.append("runtime_identity:expected-object")
        runtime = {}
    runtime_values = [runtime.get(arm) for arm in ARMS]
    if any(not isinstance(x, str) or not x for x in runtime_values):
        errors.append("runtime_identity:all-arm-identities-required")
    elif len(set(runtime_values)) != 1:
        errors.append("runtime_identity:drift-across-arms")

    cases = data.get("cases")
    if not isinstance(cases, list) or not cases:
        errors.append("cases:expected-non-empty-list")
        cases = []

    values = {arm: [] for arm in ARMS}
    seen_pairs: set[tuple[str, str]] = set()
    for ci, case in enumerate(cases):
        if not isinstance(case, dict):
            errors.append(f"cases[{ci}]:expected-object")
            continue
        case_id = case.get("case_id")
        if not isinstance(case_id, str) or not case_id:
            errors.append(f"cases[{ci}].case_id:required")
            case_id = f"index-{ci}"
        trials = case.get("trials")
        if not isinstance(trials, list) or not trials:
            errors.append(f"cases[{ci}].trials:expected-non-empty-list")
            continue
        for ti, trial in enumerate(trials):
            if not isinstance(trial, dict):
                errors.append(f"cases[{ci}].trials[{ti}]:expected-object")
                continue
            trial_id = trial.get("trial_id")
            if not isinstance(trial_id, str) or not trial_id:
                errors.append(f"cases[{ci}].trials[{ti}].trial_id:required")
                trial_id = f"index-{ti}"
            pair_id = (case_id, trial_id)
            if pair_id in seen_pairs:
                errors.append(f"duplicate-pair:{case_id}:{trial_id}")
            seen_pairs.add(pair_id)
            for arm in ARMS:
                raw = trial.get(arm)
                if isinstance(raw, bool) or not isinstance(raw, (int, float)):
                    errors.append(f"cases[{ci}].trials[{ti}].{arm}:numeric-required")
                    continue
                value = float(raw)
                if binary and value not in {0.0, 1.0}:
                    errors.append(f"cases[{ci}].trials[{ti}].{arm}:binary-must-be-0-or-1")
                values[arm].append(value)

    lengths = {len(values[arm]) for arm in ARMS}
    if len(lengths) != 1 or not lengths or next(iter(lengths), 0) == 0:
        errors.append("paired-trials:incomplete-arm-data")

    if errors:
        return {"status": "fail", "errors": errors}

    means = {arm: mean(values[arm]) for arm in ARMS}
    if direction == "higher-is-better":
        parent_delta = means["parent"] - means["no_skill"]
        candidate_skill_lift = means["candidate"] - means["no_skill"]
        candidate_delta = means["candidate"] - means["parent"]
        cmp = lambda c, p: (c > p) - (c < p)
    else:
        parent_delta = means["no_skill"] - means["parent"]
        candidate_skill_lift = means["no_skill"] - means["candidate"]
        candidate_delta = means["parent"] - means["candidate"]
        cmp = lambda c, p: (c < p) - (c > p)

    outcomes = [cmp(c, p) for c, p in zip(values["candidate"], values["parent"])]
    wins = sum(x > 0 for x in outcomes)
    losses = sum(x < 0 for x in outcomes)
    ties = sum(x == 0 for x in outcomes)
    reliability: dict[str, Any] = {"k": k, "note": "Derived Bernoulli summary; interpret only when trial independence is a reasonable approximation."}
    if binary:
        reliability["candidate_pass@k"] = 1.0 - (1.0 - means["candidate"]) ** k
        reliability["candidate_pass^k"] = means["candidate"] ** k
        reliability["parent_pass@k"] = 1.0 - (1.0 - means["parent"]) ** k
        reliability["parent_pass^k"] = means["parent"] ** k

    return {
        "status": "pass",
        "metric": metric,
        "paired_observations": len(values["candidate"]),
        "runtime_comparable": True,
        "means": means,
        "parent_skill_lift": parent_delta,
        "candidate_skill_lift": candidate_skill_lift,
        "candidate_vs_parent_delta": candidate_delta,
        "paired_candidate_vs_parent": {
            "wins": wins,
            "losses": losses,
            "ties": ties,
            "two_sided_exact_sign_p": exact_two_sided_sign_p(wins, losses),
        },
        "reliability": reliability,
        "claim_limit": "Descriptive paired evidence only; promotion still requires declared hard gates, holdout integrity, and capability-delta review.",
        "errors": [],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize paired no-skill/parent/candidate trial evidence.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--k", type=int, default=3)
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args()
    if args.k < 1:
        raise SystemExit("--k must be >= 1")
    try:
        data = json.loads(args.input.read_text(encoding="utf-8"))
        result = summarize(data, args.k)
    except Exception as exc:
        result = {"status": "fail", "errors": [f"input:{exc}"]}
    payload = json.dumps(result, indent=2, sort_keys=True)
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 0 if result.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
