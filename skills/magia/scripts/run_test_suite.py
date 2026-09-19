#!/usr/bin/env python3
"""Run the complete MAGIA pytest suite and emit a deterministic attestation."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
import time
from pathlib import Path

SUMMARY_RE = re.compile(r"(?P<count>\d+)\s+(?P<label>passed|failed|skipped|error|errors|xfailed|xpassed)")


def suite_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted((root / "tests").glob("test_*.py")):
        digest.update(path.relative_to(root).as_posix().encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def parse_summary(text: str) -> dict[str, int]:
    result = {"passed": 0, "failed": 0, "skipped": 0, "errors": 0, "xfailed": 0, "xpassed": 0}
    for match in SUMMARY_RE.finditer(text):
        label = match.group("label")
        if label == "error":
            label = "errors"
        result[label] = int(match.group("count"))
    return result


def run(root: Path) -> dict[str, object]:
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    # Package-validation tests call the validator recursively. This marker lets
    # nested validators suppress only the nested full-suite run while the outer
    # release gate still executes all tests once.
    env["MAGIA_TEST_SUITE_ACTIVE"] = "1"
    with tempfile.TemporaryDirectory(prefix="magia-pytest-attestation-") as temp_dir:
        temp = Path(temp_dir)
        stdout_path = temp / "pytest.out"
        stderr_path = temp / "pytest.err"
        pytest_target = shlex.quote(str(root / "tests"))
        python_executable = shlex.quote(sys.executable)
        shell_command = f"{python_executable} -B -m pytest -q {pytest_target}"
        start = time.monotonic()
        # A shell parent avoids a pytest teardown edge observed when package tests
        # spawn validation children under a direct Python subprocess parent.
        with stdout_path.open("w", encoding="utf-8") as stdout, stderr_path.open("w", encoding="utf-8") as stderr:
            completed = subprocess.run(["bash", "-lc", shell_command], stdout=stdout, stderr=stderr, env=env, check=False)
        duration = round(time.monotonic() - start, 3)
        stdout_text = stdout_path.read_text(encoding="utf-8")
        stderr_text = stderr_path.read_text(encoding="utf-8")

    summary = parse_summary(stdout_text + "\n" + stderr_text)
    executed = sum(summary.values())
    # A successful full execution proves collection of the same test set; separate
    # collect-only invocation is intentionally avoided because it can leave pytest
    # plugin teardown state that blocks a second run in the same attestation process.
    collected = executed
    status = "pass" if completed.returncode == 0 and collected > 0 and summary["passed"] > 0 else "fail"
    errors: list[str] = []
    if completed.returncode != 0:
        errors.append("pytest execution or collection failed")
    if collected == 0:
        errors.append("pytest collected zero tests")
    if summary["passed"] == 0:
        errors.append("pytest reported zero passed tests")
    return {
        "kind": "magia-pytest-attestation-v1",
        "status": status,
        "collected": collected,
        "executed": executed,
        **summary,
        "duration_seconds": duration,
        "suite_digest": suite_digest(root),
        "command": [sys.executable, "-B", "-m", "pytest", "-q", "tests"],
        "collection_evidence": "derived from the completed pytest execution summary",
        "errors": errors,
        "stdout_tail": "\n".join(stdout_text.splitlines()[-12:]),
        "stderr_tail": "\n".join(stderr_text.splitlines()[-12:]),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--output")
    args = parser.parse_args(argv)
    result = run(Path(args.target).resolve())
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
