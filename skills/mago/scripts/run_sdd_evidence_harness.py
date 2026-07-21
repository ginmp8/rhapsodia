#!/usr/bin/env python3
"""Run declared deterministic Mago evidence scenarios and emit bounded JSON results."""
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


def terminate(process: subprocess.Popen[str], *, grace_seconds: float = 2.0) -> None:
    """Terminate one isolated scenario process group without an unbounded wait."""
    if os.name == "nt":
        if process.poll() is None:
            process.terminate()
    else:
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
    try:
        process.wait(timeout=grace_seconds)
        return
    except subprocess.TimeoutExpired:
        pass
    if os.name == "nt":
        process.kill()
    else:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    try:
        process.wait(timeout=grace_seconds)
    except subprocess.TimeoutExpired:
        pass


def launch_scenario(root: Path, scenario: dict[str, Any], index: int) -> dict[str, Any]:
    command = [item.replace("{python}", sys.executable).replace("{root}", str(root)) for item in scenario["command"]]
    stdout_file = tempfile.TemporaryFile(mode="w+", encoding="utf-8")
    stderr_file = tempfile.TemporaryFile(mode="w+", encoding="utf-8")
    process = subprocess.Popen(
        command,
        cwd=str(root),
        text=True,
        stdout=stdout_file,
        stderr=stderr_file,
        start_new_session=os.name != "nt",
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    return {
        "process": process,
        "scenario": scenario,
        "index": index,
        "command": command,
        "started": time.monotonic(),
        "stdout_file": stdout_file,
        "stderr_file": stderr_file,
    }


def finish_scenario(
    state: dict[str, Any],
    *,
    timed_out: bool,
    termination_reason: str | None = None,
) -> tuple[int, dict[str, Any]]:
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
        "id": scenario["id"],
        "area": scenario["area"],
        "command": state["command"],
        "expected_exit": scenario["expected_exit"],
        "actual_exit": return_code,
        "status": status,
        "duration_seconds": round(time.monotonic() - state["started"], 3),
        "stdout_tail": stdout[-1200:],
        "stderr_tail": stderr[-1200:],
        "timed_out": timed_out,
        "termination_reason": termination_reason,
    }


def not_run_scenario(scenario: dict[str, Any], index: int, reason: str) -> tuple[int, dict[str, Any]]:
    return index, {
        "id": scenario["id"],
        "area": scenario["area"],
        "command": scenario["command"],
        "expected_exit": scenario["expected_exit"],
        "actual_exit": None,
        "status": "fail",
        "duration_seconds": 0.0,
        "stdout_tail": "",
        "stderr_tail": "",
        "timed_out": False,
        "not_run": True,
        "termination_reason": reason,
    }


def build_payload(
    *,
    root: Path,
    suite_path: Path,
    suite_digest: str,
    data: dict[str, Any],
    selected: list[dict[str, Any]],
    jobs: int,
    timeout: int,
    total_timeout: int | None,
    started: float,
    indexed_results: list[tuple[int, dict[str, Any]]],
    active: list[dict[str, Any]],
    pending: list[tuple[int, dict[str, Any]]],
    state: str,
    stop_reason: str | None,
) -> dict[str, Any]:
    results = [item for _, item in sorted(indexed_results, key=lambda pair: pair[0])]
    passed = sum(item["status"] == "pass" for item in results)
    complete = not active and not pending
    status = "running" if state == "running" else ("pass" if complete and passed == len(results) else "fail")
    return {
        "status": status,
        "measurement_kind": data["measurement_kind"],
        "execution_model": "isolated_bounded_subprocesses",
        "jobs": jobs,
        "timeout_seconds_per_scenario": timeout,
        "total_timeout_seconds": total_timeout,
        "duration_seconds": round(time.monotonic() - started, 3),
        "target": str(root),
        "suite": str(suite_path.resolve()),
        "suite_digest": suite_digest,
        "selected_ids": [scenario["id"] for scenario in selected],
        "scenario_count": len(results),
        "selected_scenario_count": len(selected),
        "pending_scenario_count": len(active) + len(pending),
        "active_ids": [state_item["scenario"]["id"] for state_item in active],
        "passed": passed,
        "failed": len(results) - passed,
        "stop_reason": stop_reason,
        "total_timed_out": stop_reason == "total-timeout",
        "interrupted": bool(stop_reason and stop_reason.startswith("signal-")),
        "areas": sorted({scenario["area"] for scenario in selected}),
        "results": results,
        "limitation": "This harness measures deterministic package mechanisms, not live LLM routing or plan-writing quality.",
    }


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Mago deterministic evidence scenarios.")
    parser.add_argument("--target", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--suite", default="evidence/sdd-evidence-scenarios.json")
    parser.add_argument("--output", required=True)
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--total-timeout", type=int, default=600, help="Whole-harness deadline in seconds; 0 disables it.")
    parser.add_argument("--jobs", type=int, default=1, help="Worker count; sequential is the reliable default.")
    parser.add_argument("--progress", action="store_true")
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
    selected = [
        scenario for scenario in data["scenarios"]
        if (not include_ids or scenario["id"] in include_ids) and scenario["id"] not in exclude_ids
    ]
    if not selected:
        print("ERROR: scenario selection is empty", file=sys.stderr)
        return 1

    pending = list(enumerate(selected))
    active: list[dict[str, Any]] = []
    indexed_results: list[tuple[int, dict[str, Any]]] = []
    jobs = max(1, min(args.jobs, len(pending)))
    started = time.monotonic()
    output = Path(args.output).resolve()
    signal_state: dict[str, int | None] = {"value": None}
    stop_reason: str | None = None

    def handle_signal(signum: int, _frame: object) -> None:
        signal_state["value"] = signum

    def emit(state: str) -> None:
        atomic_write_json(output, build_payload(
            root=root,
            suite_path=suite_path,
            suite_digest=suite_digest,
            data=data,
            selected=selected,
            jobs=jobs,
            timeout=args.timeout,
            total_timeout=args.total_timeout or None,
            started=started,
            indexed_results=indexed_results,
            active=active,
            pending=pending,
            state=state,
            stop_reason=stop_reason,
        ))

    previous_handlers: dict[int, Any] = {}
    for signum in (signal.SIGINT, signal.SIGTERM):
        previous_handlers[signum] = signal.getsignal(signum)
        signal.signal(signum, handle_signal)

    emit("running")
    try:
        while pending or active:
            if signal_state["value"]:
                stop_reason = f"signal-{signal_state['value']}"
            if args.total_timeout and time.monotonic() - started >= args.total_timeout:
                stop_reason = stop_reason or "total-timeout"
            if stop_reason:
                for state_item in list(active):
                    indexed_results.append(finish_scenario(
                        state_item,
                        timed_out=True,
                        termination_reason=stop_reason,
                    ))
                    active.remove(state_item)
                for index, scenario in pending:
                    indexed_results.append(not_run_scenario(scenario, index, stop_reason))
                pending.clear()
                emit("final")
                break

            while pending and len(active) < jobs:
                index, scenario = pending.pop(0)
                active.append(launch_scenario(root, scenario, index))
            completed: list[dict[str, Any]] = []
            now = time.monotonic()
            for state_item in active:
                process: subprocess.Popen[str] = state_item["process"]
                return_code = process.poll()
                expired = now - state_item["started"] >= args.timeout
                if return_code is not None or expired:
                    result_pair = finish_scenario(
                        state_item,
                        timed_out=return_code is None and expired,
                        termination_reason="per-scenario-timeout" if return_code is None and expired else None,
                    )
                    indexed_results.append(result_pair)
                    if args.progress:
                        item = result_pair[1]
                        print(f"completed {item['id']}: {item['status']} ({item['duration_seconds']}s)", flush=True)
                    completed.append(state_item)
            for state_item in completed:
                active.remove(state_item)
            if completed:
                emit("running")
            if active and not completed:
                time.sleep(0.05)
    finally:
        for signum, previous in previous_handlers.items():
            signal.signal(signum, previous)
        for state_item in list(active):
            terminate(state_item["process"])
            state_item["stdout_file"].close()
            state_item["stderr_file"].close()
        active.clear()

    payload = build_payload(
        root=root,
        suite_path=suite_path,
        suite_digest=suite_digest,
        data=data,
        selected=selected,
        jobs=jobs,
        timeout=args.timeout,
        total_timeout=args.total_timeout or None,
        started=started,
        indexed_results=indexed_results,
        active=[],
        pending=[],
        state="final",
        stop_reason=stop_reason,
    )
    atomic_write_json(output, payload)
    print(json.dumps({key: payload[key] for key in (
        "status", "scenario_count", "passed", "failed", "duration_seconds", "jobs", "stop_reason", "areas"
    )}, indent=2))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
