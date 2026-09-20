from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_self_tests.py"
MATRIX = ROOT / "scripts" / "skill_harness_host_matrix.py"


def run(script: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(script), *args], capture_output=True, text=True)


def test_stdlib_runner_executes_external_zero_arg_tests() -> None:
    with tempfile.TemporaryDirectory() as td:
        tests = Path(td) / "tests"
        tests.mkdir()
        (tests / "test_sample.py").write_text("def test_ok():\n    assert 2 + 2 == 4\n", encoding="utf-8")
        proc = run(RUNNER, "--tests-dir", str(tests))
        assert proc.returncode == 0, proc.stderr or proc.stdout
        report = json.loads(proc.stdout)
        assert report["status"] == "pass"
        assert report["discovered_tests"] == 1
        assert report["passed"] == 1


def test_stdlib_runner_fails_when_no_tests_are_discovered() -> None:
    with tempfile.TemporaryDirectory() as td:
        tests = Path(td) / "tests"
        tests.mkdir()
        proc = run(RUNNER, "--tests-dir", str(tests))
        assert proc.returncode == 1
        report = json.loads(proc.stdout)
        assert report["status"] == "fail"
        assert report["discovered_tests"] == 0


def test_host_matrix_validates_all_supported_profiles() -> None:
    proc = run(MATRIX, "--target", str(ROOT), "--profiles", "all", "--strict")
    assert proc.returncode == 0, proc.stderr or proc.stdout
    report = json.loads(proc.stdout)
    assert report["status"] == "pass"
    assert report["requested_profiles"] == ["portable", "openai", "claude", "copilot", "cursor"]
    assert report["summary"]["pass_count"] == 5
    assert report["summary"]["fail_count"] == 0
