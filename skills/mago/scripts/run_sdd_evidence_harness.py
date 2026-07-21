#!/usr/bin/env python3
"""Run declared deterministic Mago evidence scenarios and emit JSON results."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import signal
import subprocess
import sys
import tempfile
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


def terminate(process: subprocess.Popen[str]) -> None:
    if os.name == "nt":
        process.kill()
    else:
        os.killpg(process.pid, signal.SIGKILL)
    process.wait()


def launch_scenario(root: Path, scenario: dict[str, Any], index: int) -> dict[str, Any]:
    command = [item.replace("{python}", sys.executable).replace("{root}", str(root)) for item in scenario["command"]]
    stdout_file = tempfile.TemporaryFile(mode="w+", encoding="utf-8")
    stderr_file = tempfile.TemporaryFile(mode="w+", encoding="utf-8")
    process = subprocess.Popen(
        command, cwd=str(root), text=True, stdout=stdout_file, stderr=stderr_file,
        start_new_session=os.name != "nt", env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    return {"process": process, "scenario": scenario, "index": index, "command": command,
            "started": time.monotonic(), "stdout_file": stdout_file, "stderr_file": stderr_file}


def finish_scenario(state: dict[str, Any], *, timed_out: bool) -> tuple[int, dict[str, Any]]:
    process: subprocess.Popen[str] = state["process"]
    if timed_out:
        terminate(process)
        return_code = -1
    else:
        return_code = int(process.returncode or 0)
    stdout_file = state["stdout_file"]
    stderr_file = state["stderr_file"]
    stdout_file.seek(0)
    stderr_file.seek(0)
    stdout = stdout_file.read()
    stderr = stderr_file.read()
    stdout_file.close()
    stderr_file.close()
    scenario = state["scenario"]
    status = "pass" if not timed_out and return_code == scenario["expected_exit"] else "fail"
    return state["index"], {
        "id": scenario["id"], "area": scenario["area"], "command": state["command"],
        "expected_exit": scenario["expected_exit"], "actual_exit": return_code,
        "status": status, "duration_seconds": round(time.monotonic() - state["started"], 3),
        "stdout_tail": stdout[-1200:], "stderr_tail": stderr[-1200:], "timed_out": timed_out,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Mago deterministic evidence scenarios.")
    parser.add_argument("--target", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--suite", default="evals/sdd-evidence-scenarios.json")
    parser.add_argument("--output", required=True)
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--jobs", type=int, default=min(4, os.cpu_count() or 1))
    parser.add_argument("--include", action="append", default=[], help="Comma-separated scenario ids; repeatable.")
    parser.add_argument("--exclude", action="append", default=[], help="Comma-separated scenario ids; repeatable.")
    args = parser.parse_args(argv)

    root = Path(args.target).resolve()
    suite_path = Path(args.suite)
    if not suite_path.is_absolute():
        suite_path = root / suite_path
    suite_bytes = suite_path.read_bytes()
    suite_digest = hashlib.sha256(suite_bytes).hexdigest()
    data = json.loads(suite_bytes.decode("utf-8"))
    errors = validate_suite(data)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    include_ids = {item.strip() for value in args.include for item in value.split(",") if item.strip()}
    exclude_ids = {item.strip() for value in args.exclude for item in value.split(",") if item.strip()}
    all_ids = {scenario["id"] for scenario in data["scenarios"]}
    unknown = sorted((include_ids | exclude_ids) - all_ids)
    if unknown:
        print(f"ERROR: unknown scenario ids: {unknown}", file=sys.stderr)
        return 1
    selected = [scenario for scenario in data["scenarios"] if (not include_ids or scenario["id"] in include_ids) and scenario["id"] not in exclude_ids]
    if not selected:
        print("ERROR: scenario selection is empty", file=sys.stderr)
        return 1
    pending = list(enumerate(selected))
    active: list[dict[str, Any]] = []
    indexed_results: list[tuple[int, dict[str, Any]]] = []
    jobs = max(1, min(args.jobs, len(pending)))
    started = time.monotonic()
    while pending or active:
        while pending and len(active) < jobs:
            index, scenario = pending.pop(0)
            active.append(launch_scenario(root, scenario, index))
        completed: list[dict[str, Any]] = []
        now = time.monotonic()
        for state in active:
            process: subprocess.Popen[str] = state["process"]
            return_code = process.poll()
            expired = now - state["started"] >= args.timeout
            if return_code is not None or expired:
                indexed_results.append(finish_scenario(state, timed_out=return_code is None and expired))
                completed.append(state)
        for state in completed:
            active.remove(state)
        if active and not completed:
            time.sleep(0.05)

    results = [item for _, item in sorted(indexed_results, key=lambda pair: pair[0])]
    passed = sum(item["status"] == "pass" for item in results)
    payload = {
        "status": "pass" if passed == len(results) else "fail",
        "measurement_kind": data["measurement_kind"],
        "execution_model": "isolated_parallel_subprocesses",
        "jobs": jobs,
        "duration_seconds": round(time.monotonic() - started, 3),
        "target": str(root), "suite": str(suite_path.resolve()), "suite_digest": suite_digest,
        "selected_ids": [scenario["id"] for scenario in selected],
        "scenario_count": len(results), "passed": passed, "failed": len(results) - passed,
        "areas": sorted({item["area"] for item in results}), "results": results,
        "limitation": "This harness measures deterministic package mechanisms, not live LLM routing or plan-writing quality.",
    }
    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: payload[key] for key in ("status", "scenario_count", "passed", "failed", "duration_seconds", "jobs", "areas")}, indent=2))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
