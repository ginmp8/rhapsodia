#!/usr/bin/env python3
"""Run the complete MAGIA pytest suite and emit hash-bound evidence."""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import importlib.util
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

REPORT_KIND = "magia-test-report-v1"
PASS_RE = re.compile(r"(\d+)\s+passed")


def suite_manifest(root: Path) -> tuple[list[dict[str, str]], str]:
    root = root.resolve()
    files = sorted(path for path in (root / "tests").glob("test_*.py") if path.is_file())
    entries = [
        {
            "file": path.relative_to(root).as_posix(),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
        for path in files
    ]
    digest_input = "\n".join(f"{entry['file']}:{entry['sha256']}" for entry in entries)
    digest = hashlib.sha256(digest_input.encode("utf-8")).hexdigest()
    return entries, digest


def run_suite(root: Path, *, timeout: int = 180) -> dict[str, Any]:
    root = root.resolve()
    manifest, digest = suite_manifest(root)
    started = time.monotonic()
    command = [sys.executable, "-B", "-m", "pytest", "-q", str(root / "tests")]
    if not manifest:
        return {
            "kind": REPORT_KIND,
            "status": "fail",
            "root": str(root),
            "suite_files": manifest,
            "suite_digest": digest,
            "test_count": 0,
            "command": command,
            "return_code": None,
            "failure_classification": "configuration",
            "errors": ["no tests/test_*.py files found"],
        }
    if importlib.util.find_spec("pytest") is None:
        return {
            "kind": REPORT_KIND,
            "status": "fail",
            "root": str(root),
            "suite_files": manifest,
            "suite_digest": digest,
            "test_count": 0,
            "command": command,
            "return_code": None,
            "failure_classification": "environment",
            "errors": ["pytest is unavailable; install dependencies from requirements-test.txt"],
        }
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    try:
        completed = subprocess.run(
            command,
            cwd=str(root),
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout,
            env=env,
        )
        combined = completed.stdout + "\n" + completed.stderr
        match = PASS_RE.search(combined)
        count = int(match.group(1)) if match else 0
        status = "pass" if completed.returncode == 0 and count > 0 else "fail"
        errors = [] if status == "pass" else [f"pytest exited with {completed.returncode}"]
        return {
            "kind": REPORT_KIND,
            "status": status,
            "root": str(root),
            "suite_files": manifest,
            "suite_digest": digest,
            "test_count": count,
            "command": command,
            "return_code": completed.returncode,
            "duration_seconds": round(time.monotonic() - started, 3),
            "python_version": sys.version.split()[0],
            "pytest_version": importlib.metadata.version("pytest"),
            "failure_classification": None if status == "pass" else "test",
            "errors": errors,
            "stdout_tail": completed.stdout[-4000:],
            "stderr_tail": completed.stderr[-4000:],
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "kind": REPORT_KIND,
            "status": "fail",
            "root": str(root),
            "suite_files": manifest,
            "suite_digest": digest,
            "test_count": 0,
            "command": command,
            "return_code": None,
            "duration_seconds": round(time.monotonic() - started, 3),
            "failure_classification": "test",
            "errors": [f"pytest timed out after {timeout} seconds"],
            "stdout_tail": (exc.stdout or "")[-4000:] if isinstance(exc.stdout, str) else "",
            "stderr_tail": (exc.stderr or "")[-4000:] if isinstance(exc.stderr, str) else "",
        }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--json-output")
    args = parser.parse_args(argv)
    result = run_suite(Path(args.target), timeout=args.timeout)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.json_output:
        output = Path(args.json_output).resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
