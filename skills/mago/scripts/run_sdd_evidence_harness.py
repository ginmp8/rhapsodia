#!/usr/bin/env python3
"""Run declared deterministic Mago evidence scenarios and emit JSON results."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

ALLOWED_AREAS = {
    "requirements-design-validation",
    "security-risk",
    "execution-resume",
    "interoperability",
    "product-ecosystem",
    "activation-boundary",
}


def validate_suite(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        return ["suite must be an object with schema_version 1"]
    if data.get("measurement_kind") != "deterministic_executable_evidence":
        errors.append("measurement_kind must be deterministic_executable_evidence")
    scenarios = data.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        return errors + ["scenarios must be a non-empty list"]
    seen: set[str] = set()
    for index, scenario in enumerate(scenarios):
        if not isinstance(scenario, dict):
            errors.append(f"scenario {index} must be an object")
            continue
        scenario_id = scenario.get("id")
        if not isinstance(scenario_id, str) or not scenario_id:
            errors.append(f"scenario {index} has invalid id")
        elif scenario_id in seen:
            errors.append(f"duplicate scenario id: {scenario_id}")
        else:
            seen.add(scenario_id)
        if scenario.get("area") not in ALLOWED_AREAS:
            errors.append(f"scenario {scenario_id} has invalid area")
        command = scenario.get("command")
        if not isinstance(command, list) or not command or not all(isinstance(item, str) and item for item in command):
            errors.append(f"scenario {scenario_id} command must be a non-empty argv list")
        if scenario.get("expected_exit") not in {0, 1, 2, 75}:
            errors.append(f"scenario {scenario_id} expected_exit is unsupported")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Mago deterministic evidence scenarios.")
    parser.add_argument("--target", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--suite", default="evals/sdd-evidence-scenarios.json")
    parser.add_argument("--output", required=True)
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args(argv)

    root = Path(args.target).resolve()
    suite_path = Path(args.suite)
    if not suite_path.is_absolute():
        suite_path = root / suite_path
    data = json.loads(suite_path.read_text(encoding="utf-8"))
    errors = validate_suite(data)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    results: list[dict[str, Any]] = []
    passed = 0
    for scenario in data["scenarios"]:
        command = [item.replace("{python}", sys.executable).replace("{root}", str(root)) for item in scenario["command"]]
        started = time.monotonic()
        timed_out = False
        try:
            completed = subprocess.run(
                command,
                cwd=str(root),
                text=True,
                capture_output=True,
                check=False,
                timeout=args.timeout,
            )
            return_code = completed.returncode
            stdout = completed.stdout
            stderr = completed.stderr
        except subprocess.TimeoutExpired as exc:
            timed_out = True
            return_code = -1
            stdout = exc.stdout or ""
            stderr = exc.stderr or ""
        duration = round(time.monotonic() - started, 3)
        status = "pass" if not timed_out and return_code == scenario["expected_exit"] else "fail"
        if status == "pass":
            passed += 1
        results.append(
            {
                "id": scenario["id"],
                "area": scenario["area"],
                "command": command,
                "expected_exit": scenario["expected_exit"],
                "actual_exit": return_code,
                "status": status,
                "duration_seconds": duration,
                "stdout_tail": stdout[-1200:],
                "stderr_tail": stderr[-1200:],
                "timed_out": timed_out,
            }
        )

    payload = {
        "status": "pass" if passed == len(results) else "fail",
        "measurement_kind": data["measurement_kind"],
        "target": str(root),
        "suite": str(suite_path.resolve()),
        "scenario_count": len(results),
        "passed": passed,
        "failed": len(results) - passed,
        "areas": sorted({item["area"] for item in results}),
        "results": results,
        "limitation": "This harness measures deterministic package mechanisms, not live LLM routing or plan-writing quality.",
    }
    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: payload[key] for key in ("status", "scenario_count", "passed", "failed", "areas")}, indent=2))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
