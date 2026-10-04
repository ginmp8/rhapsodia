#!/usr/bin/env python3
"""Assess bounded gate stability without turning retries into acceptance."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from discover_commands import GATES
from run_gate import load_argv, make_receipt, write_json_atomic

MIN_RUNS = 2
MAX_RUNS = 20


def classify_stability(attempts: list[dict[str, Any]]) -> tuple[str, str]:
    if not attempts:
        return "not-assessed", "not-run"
    if any(bool(item.get("target_mutated")) for item in attempts):
        return "inconclusive", "mutated"
    statuses = [str(item.get("status", "not-run")) for item in attempts]
    if any(status == "blocked" for status in statuses):
        return "inconclusive", "blocked"
    if any(status == "not-run" for status in statuses):
        return "not-assessed", "not-run"
    unique = set(statuses)
    if unique == {"pass"}:
        return "stable", "pass"
    if unique == {"fail"}:
        signatures = {(item.get("classification"), item.get("exit_code")) for item in attempts}
        return ("stable", "fail") if len(signatures) == 1 else ("unstable", "mixed-failure")
    return "unstable", "mixed"


def assess(target: Path, gate: str, runs: int, execute: bool, argv: list[str] | None, timeout: int) -> tuple[dict[str, Any], int]:
    if runs < MIN_RUNS or runs > MAX_RUNS:
        raise ValueError(f"--runs must be between {MIN_RUNS} and {MAX_RUNS}")
    if not execute:
        result = {
            "stability_version": 1,
            "target": str(target.resolve()),
            "gate": gate,
            "requested_runs": runs,
            "executed_runs": 0,
            "stability": "not-assessed",
            "outcome": "not-run",
            "attempts": [],
            "diagnostic": {"code": "stability/execution-not-requested"},
        }
        return result, 0
    attempts: list[dict[str, Any]] = []
    for _ in range(runs):
        receipt, _ = make_receipt(target, gate, argv, True, timeout)
        attempts.append(receipt)
    stability, outcome = classify_stability(attempts)
    result = {
        "stability_version": 1,
        "target": str(target.resolve()),
        "gate": gate,
        "requested_runs": runs,
        "executed_runs": len(attempts),
        "stability": stability,
        "outcome": outcome,
        "attempts": attempts,
    }
    process_code = 0 if stability == "stable" else (2 if stability in {"inconclusive", "not-assessed"} else 1)
    return result, process_code


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the same gate a bounded number of times and classify stability separately from gate status.")
    parser.add_argument("--target", required=True)
    parser.add_argument("--gate", required=True, choices=GATES)
    parser.add_argument("--runs", required=True, type=int, help=f"Explicit attempt count ({MIN_RUNS}-{MAX_RUNS}); no retry-to-green default")
    parser.add_argument("--argv-json", help="Optional explicit argv JSON array; otherwise the same discovered command is selected each attempt")
    parser.add_argument("--execute", action="store_true", help="Actually execute attempts; otherwise result is not-assessed")
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--receipt", help="Optional JSON receipt path")
    args = parser.parse_args()
    try:
        argv = load_argv(args.argv_json) if args.argv_json else None
        result, code = assess(Path(args.target), args.gate, args.runs, args.execute, argv, args.timeout)
    except (ValueError, json.JSONDecodeError) as exc:
        result = {
            "stability_version": 1,
            "target": str(Path(args.target).resolve()),
            "gate": args.gate,
            "requested_runs": args.runs,
            "executed_runs": 0,
            "stability": "inconclusive",
            "outcome": "configuration",
            "attempts": [],
            "diagnostic": {"code": "configuration/invalid-stability-request", "error": str(exc)},
        }
        code = 2
    if args.receipt:
        write_json_atomic(Path(args.receipt), result)
    print(json.dumps(result, indent=2, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
