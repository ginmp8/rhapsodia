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
from typing import Any, Callable

COUNT_RE = re.compile(r"Ran\s+(\d+)\s+tests?\s+in")
HEAVY_TEST_PRIORITY = (
    "test_mutation_transaction.py",
    "test_sdd_adapter_roundtrip.py",
    "test_concurrency_model.py",
    "test_kiro_adapter_v2.py",
)


def terminate(process: subprocess.Popen[str], *, grace_seconds: float = 2.0) -> None:
    """Terminate the complete isolated process group without blocking forever."""
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
        # The caller must still receive a bounded result. A surviving process is
        # reported by return_code=-1 and can be diagnosed from the process id.
        pass


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


def finish(
    root: Path,
    state: dict[str, Any],
    *,
    timed_out: bool,
    termination_reason: str | None = None,
) -> dict[str, Any]:
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
        "termination_reason": termination_reason,
        "stdout_tail": stdout[-1200:],
        "stderr_tail": stderr[-1200:],
    }


def not_run(root: Path, test_file: Path, reason: str) -> dict[str, Any]:
    return {
        "file": test_file.relative_to(root).as_posix(),
        "command": [sys.executable, "-B", str(test_file)],
        "status": "fail",
        "return_code": None,
        "test_count": 0,
        "duration_seconds": 0.0,
        "timed_out": False,
        "termination_reason": reason,
        "not_run": True,
        "stdout_tail": "",
        "stderr_tail": "",
    }


def suite_manifest(files: list[Path]) -> tuple[list[dict[str, str]], str]:
    entries = [{"file": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()} for path in files]
    digest = hashlib.sha256("\n".join(f"{item['file']}:{item['sha256']}" for item in entries).encode()).hexdigest()
    return entries, digest


def build_payload(
    *,
    root: Path,
    tests_dir: Path,
    manifest: list[dict[str, str]],
    suite_digest: str,
    selected_files: list[Path],
    worker_count: int,
    heavy_limit: int,
    timeout: int,
    total_timeout: int | None,
    started: float,
    results: list[dict[str, Any]],
    active: list[dict[str, Any]],
    pending: list[Path],
    state: str,
    stop_reason: str | None,
) -> dict[str, Any]:
    ordered = sorted(results, key=lambda item: item["file"])
    failed = [item for item in ordered if item["status"] != "pass"]
    complete = not active and not pending
    status = "running" if state == "running" else ("pass" if complete and not failed else "fail")
    errors: list[str] = []
    for item in failed:
        if item.get("not_run"):
            errors.append(f"{item['file']}: not run ({item.get('termination_reason')})")
        elif item["timed_out"]:
            errors.append(f"{item['file']}: timeout ({item.get('termination_reason') or 'per-file'})")
        else:
            errors.append(f"{item['file']}: exit {item['return_code']}")
    return {
        "status": status,
        "measurement_kind": "isolated_bounded_unittest_files",
        "root": str(root),
        "tests_dir": str(tests_dir),
        "suite_files": manifest,
        "suite_digest": suite_digest,
        "selected_files": [path.name for path in selected_files],
        "jobs": worker_count,
        "timeout_seconds_per_file": timeout,
        "total_timeout_seconds": total_timeout,
        "file_count": len(ordered),
        "selected_file_count": len(selected_files),
        "pending_file_count": len(pending) + len(active),
        "active_files": [state_item["test_file"].name for state_item in active],
        "heavy_process_limit": heavy_limit,
        "test_count": sum(item["test_count"] for item in ordered),
        "passed_files": len(ordered) - len(failed),
        "failed_files": len(failed),
        "duration_seconds": round(time.monotonic() - started, 3),
        "stop_reason": stop_reason,
        "total_timed_out": stop_reason == "total-timeout",
        "interrupted": bool(stop_reason and stop_reason.startswith("signal-")),
        "errors": errors,
        "results": ordered,
    }


def run_suite(
    root: Path,
    tests_dir: Path,
    *,
    jobs: int,
    timeout: int,
    total_timeout: int | None = None,
    pattern: str = "test_*.py",
    progress: bool = False,
    include: set[str] | None = None,
    exclude: set[str] | None = None,
    checkpoint: Callable[[dict[str, Any]], None] | None = None,
    stop_requested: Callable[[], str | None] | None = None,
) -> dict[str, Any]:
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
    # Heavy tests create nested subprocesses. One heavy process at a time avoids
    # resource amplification while still allowing explicit light-test parallelism.
    heavy_limit = 1
    warmup_done = not pending_heavy
    stop_reason: str | None = None

    def pending_paths() -> list[Path]:
        return [*pending_heavy, *pending_light]

    def emit(state: str) -> None:
        if checkpoint is None:
            return
        checkpoint(build_payload(
            root=root,
            tests_dir=tests_dir,
            manifest=manifest,
            suite_digest=suite_digest,
            selected_files=all_files,
            worker_count=worker_count,
            heavy_limit=heavy_limit,
            timeout=timeout,
            total_timeout=total_timeout,
            started=started,
            results=results,
            active=active,
            pending=pending_paths(),
            state=state,
            stop_reason=stop_reason,
        ))

    emit("running")
    try:
        while pending_heavy or pending_light or active:
            requested = stop_requested() if stop_requested else None
            if requested:
                stop_reason = requested
            if total_timeout is not None and time.monotonic() - started >= total_timeout:
                stop_reason = stop_reason or "total-timeout"
            if stop_reason:
                for state_item in list(active):
                    results.append(finish(root, state_item, timed_out=True, termination_reason=stop_reason))
                    active.remove(state_item)
                for path in pending_paths():
                    results.append(not_run(root, path, stop_reason))
                pending_heavy.clear()
                pending_light.clear()
                emit("final")
                break

            active_heavy = sum(state_item["test_file"].name in priority for state_item in active)
            while pending_heavy and active_heavy < heavy_limit and len(active) < worker_count:
                active.append(launch(root, pending_heavy.pop(0)))
                active_heavy += 1
            if warmup_done:
                while pending_light and len(active) < worker_count:
                    active.append(launch(root, pending_light.pop(0)))
            if not active and pending_heavy:
                active.append(launch(root, pending_heavy.pop(0)))

            completed: list[dict[str, Any]] = []
            now = time.monotonic()
            for state_item in active:
                process: subprocess.Popen[str] = state_item["process"]
                return_code = process.poll()
                expired = now - state_item["started"] >= timeout
                if return_code is not None or expired:
                    result_item = finish(
                        root,
                        state_item,
                        timed_out=return_code is None and expired,
                        termination_reason="per-file-timeout" if return_code is None and expired else None,
                    )
                    results.append(result_item)
                    if progress:
                        print(
                            f"completed {result_item['file']}: {result_item['status']} "
                            f"({result_item['duration_seconds']}s)",
                            flush=True,
                        )
                    completed.append(state_item)
            if completed and not warmup_done:
                warmup_done = True
            for state_item in completed:
                active.remove(state_item)
            if completed:
                emit("running")
            if active and not completed:
                time.sleep(0.05)
    finally:
        # Covers unexpected exceptions in library callers. The CLI signal path
        # uses stop_requested and therefore still emits a final partial report.
        for state_item in list(active):
            terminate(state_item["process"])
            state_item["stdout_file"].close()
            state_item["stderr_file"].close()
        active.clear()

    return build_payload(
        root=root,
        tests_dir=tests_dir,
        manifest=manifest,
        suite_digest=suite_digest,
        selected_files=all_files,
        worker_count=worker_count,
        heavy_limit=heavy_limit,
        timeout=timeout,
        total_timeout=total_timeout,
        started=started,
        results=results,
        active=[],
        pending=[],
        state="final",
        stop_reason=stop_reason,
    )


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Mago unittest files in isolated bounded subprocesses.")
    parser.add_argument("--target", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--tests-dir", default="tests")
    parser.add_argument("--pattern", default="test_*.py")
    parser.add_argument("--jobs", type=int, default=1, help="Worker count; sequential is the reliable default.")
    parser.add_argument("--timeout", type=int, default=180, help="Per-file timeout in seconds.")
    parser.add_argument("--total-timeout", type=int, default=600, help="Whole-suite deadline in seconds; 0 disables it.")
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
    output = Path(args.output).resolve()
    signal_state: dict[str, int | None] = {"value": None}

    def handle_signal(signum: int, _frame: object) -> None:
        signal_state["value"] = signum

    previous_handlers: dict[int, Any] = {}
    for signum in (signal.SIGINT, signal.SIGTERM):
        previous_handlers[signum] = signal.getsignal(signum)
        signal.signal(signum, handle_signal)
    try:
        result = run_suite(
            root,
            tests_dir.resolve(),
            jobs=args.jobs,
            timeout=args.timeout,
            total_timeout=args.total_timeout or None,
            pattern=args.pattern,
            progress=args.progress,
            include=include,
            exclude=exclude,
            checkpoint=lambda payload: atomic_write_json(output, payload),
            stop_requested=lambda: f"signal-{signal_state['value']}" if signal_state["value"] else None,
        )
    finally:
        for signum, previous in previous_handlers.items():
            signal.signal(signum, previous)

    if result.get("test_count", 0) < args.minimum_tests:
        result["status"] = "fail"
        result.setdefault("errors", []).append(
            f"expected at least {args.minimum_tests} tests, observed {result.get('test_count', 0)}"
        )
    atomic_write_json(output, result)
    print(json.dumps({key: result.get(key) for key in (
        "status", "file_count", "test_count", "duration_seconds", "failed_files", "stop_reason"
    )}, indent=2))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
