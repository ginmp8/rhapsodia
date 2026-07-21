#!/usr/bin/env python3
"""Merge hash-bound Mago evidence harness shards and prove complete coverage."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: report must be an object")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Merge deterministic evidence harness shard reports.")
    parser.add_argument("--target", required=True)
    parser.add_argument("--suite", default="evals/sdd-evidence-scenarios.json")
    parser.add_argument("--report", action="append", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)

    root = Path(args.target).resolve()
    suite_path = Path(args.suite)
    if not suite_path.is_absolute():
        suite_path = root / suite_path
    suite_bytes = suite_path.read_bytes()
    suite_digest = hashlib.sha256(suite_bytes).hexdigest()
    suite = json.loads(suite_bytes.decode("utf-8"))
    required_ids = [item["id"] for item in suite.get("scenarios", [])]
    errors: list[str] = []
    results: dict[str, dict[str, Any]] = {}
    reports: list[str] = []

    for raw in args.report:
        path = Path(raw).resolve()
        reports.append(str(path))
        try:
            report = load(path)
        except Exception as exc:
            errors.append(f"{path}: unreadable report: {exc}")
            continue
        if report.get("suite_digest") != suite_digest:
            errors.append(f"{path}: suite digest does not match current suite")
        if report.get("status") != "pass":
            errors.append(f"{path}: shard status is not pass")
        for item in report.get("results", []):
            scenario_id = item.get("id")
            if scenario_id in results:
                errors.append(f"duplicate scenario result `{scenario_id}`")
            elif isinstance(scenario_id, str):
                results[scenario_id] = item

    missing = [scenario_id for scenario_id in required_ids if scenario_id not in results]
    unexpected = sorted(set(results) - set(required_ids))
    if missing:
        errors.append(f"missing scenario results: {missing}")
    if unexpected:
        errors.append(f"unexpected scenario results: {unexpected}")
    failed = [scenario_id for scenario_id, item in results.items() if item.get("status") != "pass"]
    if failed:
        errors.append(f"failed scenario results: {failed}")

    ordered = [results[scenario_id] for scenario_id in required_ids if scenario_id in results]
    payload = {
        "kind": "mago-merged-evidence-report",
        "status": "pass" if not errors else "fail",
        "measurement_kind": suite.get("measurement_kind"),
        "target": str(root),
        "suite": str(suite_path),
        "suite_digest": suite_digest,
        "reports": reports,
        "scenario_count": len(ordered),
        "passed": sum(item.get("status") == "pass" for item in ordered),
        "failed": sum(item.get("status") != "pass" for item in ordered),
        "areas": sorted({item.get("area") for item in ordered if item.get("area")}),
        "results": ordered,
        "errors": errors,
        "limitation": "Deterministic mechanism evidence only; live LLM behavior remains unmeasured.",
    }
    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: payload[key] for key in ("status", "scenario_count", "passed", "failed", "areas")}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
