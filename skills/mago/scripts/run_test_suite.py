#!/usr/bin/env python3
"""Run Mago unittest files as isolated, bounded subprocesses."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

COUNT_RE = re.compile(r"Ran\s+(\d+)\s+tests?\s+in")
HEAVY_TEST_PRIORITY = (
    "test_mutation_transaction.py",
    "test_sdd_adapter_roundtrip.py",
    "test_concurrency_model.py",
    "test_kiro_adapter_v2.py",
)


def terminate(process: subprocess.Popen[str]) -> None:
    if os.name == "nt":
        process.kill()
    else:
        os.killpg(process.pid, signal.SIGKILL)
    process.wait()


def launch(root: Path, test_file: Path) -> dict[str, Any]:
    stdout_file = tempfile.TemporaryFile(mode="w+", encoding="utf-8")
    stderr_file = tempfile.TemporaryFile(mode="w+", encoding="utf-8")
    command = [sys.executable, "-B", str(test_file)]
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
        "test_file": test_file,
        "command": command,
        "started": time.monotonic(),
        "stdout_file": stdout_file,
        "stderr_file": stderr_file,
    }


def finish(root: Path, state: dict[str, Any], *, timed_out: bool) -> dict[str, Any]:
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
    match = COUNT_RE.search(stdout + "\n" + stderr)
    count = int(match.group(1)) if match else 0
    status = "pass" if return_code == 0 and not timed_out and count > 0 else "fail"
    return {
        "file": state["test_file"].relative_to(root).as_posix(),
        "command": state["command"],
        "status": status,
        "return_code": return_code,
        "test_count": count,
        "duration_seconds": round(time.monotonic() - state["started"], 3),
        "timed_out": timed_out,
        "stdout_tail": stdout[-1200:],
        "stderr_tail": stderr[-1200:],
    }


def suite_manifest(files: list[Path]) -> tuple[list[dict[str, str]], str]:
    entries = [{"file": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()} for path in files]
    digest = hashlib.sha256("\n".join(f"{item['file']}:{item['sha256']}" for item in entries).encode()).hexdigest()
    return entries, digest


def run_suite(root: Path, tests_dir: Path, *, jobs: int, timeout: int, pattern: str = "test_*.py", progress: bool = False, include: set[str] | None = None, exclude: set[str] | None = None) -> dict[str, Any]:
    suite_files = sorted(path for path in tests_dir.glob(pattern) if path.is_file() and path.name != "__init__.py")
    manifest, suite_digest = suite_manifest(suite_files)
    include = include or set()
    exclude = exclude or set()
    all_files = [path for path in suite_files if (not include or path.name in include) and path.name not in exclude]
    if not all_files:
        return {"status": "fail", "errors": [f"no tests matched {tests_dir / pattern}"], "results": [], "test_count": 0}
    priority = {name: index for index, name in enumerate(HEAVY_TEST_PRIORITY)}
    pending_heavy = sorted((path for path in all_files if path.name in priority), key=lambda path: priority[path.name])
    pending_light = [path for path in all_files if path.name not in priority]
    started = time.monotonic()
    active: list[dict[str, Any]] = []
    results: list[dict[str, Any]] = []
    worker_count = max(1, min(jobs, len(all_files)))
    heavy_limit = min(2, worker_count)
    warmup_done = not pending_heavy

    while pending_heavy or pending_light or active:
        active_heavy = sum(state["test_file"].name in priority for state in active)
        while pending_heavy and active_heavy < heavy_limit and len(active) < worker_count:
            active.append(launch(root, pending_heavy.pop(0)))
            active_heavy += 1
        if warmup_done:
            light_capacity = 1 if active_heavy >= heavy_limit and pending_heavy else worker_count - len(active)
            while pending_light and len(active) < worker_count and light_capacity > 0:
                active.append(launch(root, pending_light.pop(0)))
                light_capacity -= 1
        if not active and pending_heavy:
            active.append(launch(root, pending_heavy.pop(0)))
        completed: list[dict[str, Any]] = []
        now = time.monotonic()
        for state in active:
            process: subprocess.Popen[str] = state["process"]
            return_code = process.poll()
            expired = now - state["started"] >= timeout
            if return_code is not None or expired:
                result_item = finish(root, state, timed_out=return_code is None and expired)
                results.append(result_item)
                if progress:
                    print(f"completed {result_item['file']}: {result_item['status']} ({result_item['duration_seconds']}s)", flush=True)
                completed.append(state)
        if completed and not warmup_done:
            warmup_done = True
        for state in completed:
            active.remove(state)
        if active and not completed:
            time.sleep(0.05)

    results.sort(key=lambda item: item["file"])
    failed = [item for item in results if item["status"] != "pass"]
    return {
        "status": "pass" if not failed else "fail",
        "measurement_kind": "isolated_parallel_unittest_files",
        "root": str(root),
        "tests_dir": str(tests_dir),
        "suite_files": manifest,
        "suite_digest": suite_digest,
        "selected_files": [path.name for path in all_files],
        "jobs": worker_count,
        "timeout_seconds_per_file": timeout,
        "file_count": len(results),
        "heavy_process_limit": heavy_limit,
        "test_count": sum(item["test_count"] for item in results),
        "passed_files": len(results) - len(failed),
        "failed_files": len(failed),
        "duration_seconds": round(time.monotonic() - started, 3),
        "errors": [f"{item['file']}: timeout" if item["timed_out"] else f"{item['file']}: exit {item['return_code']}" for item in failed],
        "results": results,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Mago unittest files in isolated bounded subprocesses.")
    parser.add_argument("--target", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--tests-dir", default="tests")
    parser.add_argument("--pattern", default="test_*.py")
    parser.add_argument("--jobs", type=int, default=min(4, os.cpu_count() or 1))
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--minimum-tests", type=int, default=1)
    parser.add_argument("--output", required=True)
    parser.add_argument("--progress", action="store_true")
    parser.add_argument("--include", help="Comma-separated test filenames to run; suite digest still covers every test file.")
    parser.add_argument("--exclude", help="Comma-separated test filenames to omit from this shard.")
    args = parser.parse_args(argv)
    root = Path(args.target).resolve()
    tests_dir = Path(args.tests_dir)
    if not tests_dir.is_absolute():
        tests_dir = root / tests_dir
    include = {item.strip() for item in (args.include or "").split(",") if item.strip()}
    exclude = {item.strip() for item in (args.exclude or "").split(",") if item.strip()}
    result = run_suite(root, tests_dir.resolve(), jobs=args.jobs, timeout=args.timeout, pattern=args.pattern, progress=args.progress, include=include, exclude=exclude)
    if result.get("test_count", 0) < args.minimum_tests:
        result["status"] = "fail"
        result.setdefault("errors", []).append(
            f"expected at least {args.minimum_tests} tests, observed {result.get('test_count', 0)}"
        )
    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: result.get(key) for key in ("status", "file_count", "test_count", "duration_seconds", "failed_files")}, indent=2))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
