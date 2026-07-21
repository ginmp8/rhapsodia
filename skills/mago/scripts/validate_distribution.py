#!/usr/bin/env python3
"""Execute Mago distribution gates and emit one external, hash-bound evidence report."""
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
import zipfile
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from package_skill import iter_package_files


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def tree_manifest(root: Path) -> dict[str, str]:
    files, _ = iter_package_files(root)
    return {
        path.relative_to(root).as_posix(): sha256_file(path)
        for path in files
    }


def ensure_external_output(target: Path, output_dir: Path) -> None:
    try:
        output_dir.relative_to(target)
    except ValueError:
        return
    raise ValueError("output directory must be outside the target skill")


def terminate(process: subprocess.Popen[str], grace_seconds: float = 2.0) -> None:
    if process.poll() is not None:
        return
    if os.name == "nt":
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


def run_command(name: str, command: list[str], cwd: Path, timeout: int) -> dict[str, Any]:
    started = time.monotonic()
    process = subprocess.Popen(
        command,
        cwd=str(cwd),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=os.name != "nt",
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    timed_out = False
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        terminate(process)
        stdout, stderr = process.communicate()
    return {
        "name": name,
        "command": command,
        "status": "pass" if not timed_out and process.returncode == 0 else "fail",
        "exit_code": process.returncode,
        "timed_out": timed_out,
        "duration_seconds": round(time.monotonic() - started, 3),
        "stdout_tail": stdout[-2400:],
        "stderr_tail": stderr[-2400:],
    }


def safe_extract(zip_path: Path, destination: Path) -> Path:
    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as archive:
        files = [name for name in archive.namelist() if not name.endswith("/")]
        roots = {name.split("/", 1)[0] for name in files}
        if len(roots) != 1:
            raise ValueError(f"archive must have one top-level directory, found {sorted(roots)}")
        for name in files:
            if name.startswith("/") or ".." in Path(name).parts:
                raise ValueError(f"unsafe archive member: {name}")
        archive.extractall(destination)
    return destination / next(iter(roots))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run complete Mago distribution validation outside the skill folder.")
    parser.add_argument("--target", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--jobs", type=int, default=1)
    parser.add_argument("--timeout", type=int, default=240, help="Per command deadline in seconds.")
    parser.add_argument("--total-timeout", type=int, default=1200, help="Deadline passed to bounded suite runners.")
    args = parser.parse_args(argv)

    target = Path(args.target).resolve()
    output_dir = Path(args.output_dir).resolve()
    report_path = Path(args.report).resolve()
    ensure_external_output(target, output_dir)
    ensure_external_output(target, report_path.parent)
    output_dir.mkdir(parents=True, exist_ok=True)
    reports = output_dir / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    archive_path = output_dir / "skill.zip"
    started = time.monotonic()
    payload: dict[str, Any] = {
        "kind": "mago-distribution-validation",
        "status": "running",
        "measurement_kind": "deterministic_distribution_evidence",
        "target": str(target),
        "output_dir": str(output_dir),
        "archive": str(archive_path),
        "commands": [],
        "limitations": [
            "Deterministic package evidence does not measure live LLM routing or prose quality.",
            "Runtime behavior remains Magia-owned evidence and is not claimed by this validator."
        ],
    }
    atomic_write_json(report_path, payload)

    def gate(name: str, command: list[str], cwd: Path = target, timeout: int | None = None) -> bool:
        result = run_command(name, command, cwd, timeout or args.timeout)
        payload["commands"].append(result)
        payload["status"] = "running" if result["status"] == "pass" else "fail"
        atomic_write_json(report_path, payload)
        return result["status"] == "pass"

    py = sys.executable
    test_report = reports / "tests.json"
    merged_tests = reports / "tests-merged.json"
    core_evidence = reports / "evidence-core.json"
    merged_core_evidence = reports / "evidence-core-merged.json"
    lifecycle_evidence = reports / "evidence-lifecycle.json"
    merged_lifecycle_evidence = reports / "evidence-lifecycle-merged.json"
    skill_validation = reports / "skill-package.json"
    package_report = reports / "package-build.json"
    archive_report = reports / "archive-validation.json"

    commands: list[tuple[str, list[str], int | None]] = [
        ("runtime-dependencies", [py, "-B", "scripts/validate_runtime_dependencies.py", str(target), "--json-output", str(reports / "runtime-dependencies.json")], None),
        ("release-metadata", [py, "-B", "scripts/validate_release_metadata.py", str(target)], None),
        ("activation-oracle", [py, "-B", "scripts/validate_activation_scenarios.py", str(target), "--json-output", str(reports / "activation.json")], None),
        ("full-test-suite", [py, "-B", "scripts/run_test_suite.py", "--target", str(target), "--jobs", str(max(1, args.jobs)), "--timeout", str(args.timeout), "--total-timeout", str(args.total_timeout), "--minimum-tests", "69", "--progress", "--output", str(test_report)], args.total_timeout + 30),
        ("merge-test-report", [py, "-B", "scripts/merge_test_reports.py", "--target", str(target), "--report", str(test_report), "--minimum-tests", "69", "--output", str(merged_tests)], None),
        ("core-evidence-harness", [py, "-B", "scripts/run_sdd_evidence_harness.py", "--target", str(target), "--suite", "evidence/sdd-evidence-scenarios.json", "--jobs", str(max(1, args.jobs)), "--timeout", str(args.timeout), "--total-timeout", str(args.total_timeout), "--progress", "--output", str(core_evidence)], args.total_timeout + 30),
        ("merge-core-evidence", [py, "-B", "scripts/merge_evidence_reports.py", "--target", str(target), "--suite", "evidence/sdd-evidence-scenarios.json", "--report", str(core_evidence), "--output", str(merged_core_evidence)], None),
        ("lifecycle-evidence-harness", [py, "-B", "scripts/run_sdd_evidence_harness.py", "--target", str(target), "--suite", "evidence/lifecycle-contract-scenarios.json", "--jobs", str(max(1, args.jobs)), "--timeout", str(args.timeout), "--total-timeout", str(args.total_timeout), "--progress", "--output", str(lifecycle_evidence)], args.total_timeout + 30),
        ("merge-lifecycle-evidence", [py, "-B", "scripts/merge_evidence_reports.py", "--target", str(target), "--suite", "evidence/lifecycle-contract-scenarios.json", "--report", str(lifecycle_evidence), "--output", str(merged_lifecycle_evidence)], None),
        ("skill-package-validation", [py, "-B", "scripts/validate_skill_package.py", str(target), "--test-report", str(merged_tests), "--json-output", str(skill_validation)], 600),
        ("package-build", [py, "-B", "scripts/package_skill.py", "--target", str(target), "--output", str(archive_path), "--json-output", str(package_report)], 300),
        ("archive-validation", [py, "-B", "scripts/package_skill.py", "--validate-only", str(archive_path), "--json-output", str(archive_report)], 300),
    ]

    for name, command, timeout in commands:
        if not gate(name, command, timeout=timeout):
            payload["duration_seconds"] = round(time.monotonic() - started, 3)
            payload["failed_gate"] = name
            atomic_write_json(report_path, payload)
            return 1

    target_manifest = tree_manifest(target)
    with tempfile.TemporaryDirectory(prefix="mago-extracted-", dir=str(output_dir)) as temporary:
        extracted = safe_extract(archive_path, Path(temporary))
        extracted_manifest = tree_manifest(extracted)
        payload["archive_content"] = {
            "target_file_count": len(target_manifest),
            "extracted_file_count": len(extracted_manifest),
            "target_tree_digest": hashlib.sha256(json.dumps(target_manifest, sort_keys=True).encode()).hexdigest(),
            "extracted_tree_digest": hashlib.sha256(json.dumps(extracted_manifest, sort_keys=True).encode()).hexdigest(),
            "byte_identical": target_manifest == extracted_manifest,
        }
        if target_manifest != extracted_manifest:
            payload["status"] = "fail"
            payload["failed_gate"] = "archive-byte-equivalence"
            atomic_write_json(report_path, payload)
            return 1
        extracted_validation = reports / "extracted-skill-package.json"
        extracted_gates = [
            ("extracted-runtime-dependencies", [py, "-B", "scripts/validate_runtime_dependencies.py", str(extracted), "--json-output", str(reports / "extracted-runtime.json")]),
            ("extracted-release-metadata", [py, "-B", "scripts/validate_release_metadata.py", str(extracted)]),
            ("extracted-skill-package-validation", [py, "-B", "scripts/validate_skill_package.py", str(extracted), "--test-report", str(merged_tests), "--json-output", str(extracted_validation)]),
        ]
        for name, command in extracted_gates:
            if not gate(name, command, cwd=extracted, timeout=600):
                payload["duration_seconds"] = round(time.monotonic() - started, 3)
                payload["failed_gate"] = name
                atomic_write_json(report_path, payload)
                return 1

    payload["status"] = "pass"
    payload["duration_seconds"] = round(time.monotonic() - started, 3)
    payload["archive_sha256"] = sha256_file(archive_path)
    payload["test_evidence"] = json.loads(merged_tests.read_text(encoding="utf-8"))
    payload["core_evidence"] = json.loads(merged_core_evidence.read_text(encoding="utf-8"))
    payload["lifecycle_evidence"] = json.loads(merged_lifecycle_evidence.read_text(encoding="utf-8"))
    atomic_write_json(report_path, payload)
    print(json.dumps({
        "status": payload["status"],
        "archive": payload["archive"],
        "archive_sha256": payload["archive_sha256"],
        "test_count": payload["test_evidence"].get("test_count"),
        "core_scenarios": payload["core_evidence"].get("scenario_count"),
        "lifecycle_scenarios": payload["lifecycle_evidence"].get("scenario_count"),
        "duration_seconds": payload["duration_seconds"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
