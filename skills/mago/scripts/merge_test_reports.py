#!/usr/bin/env python3
"""Merge hash-bound Mago test shards and prove complete current-suite coverage."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def current_manifest(root: Path) -> tuple[list[dict[str, str]], str]:
    files = sorted(path for path in (root / "tests").glob("test_*.py") if path.is_file())
    entries = [{"file": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()} for path in files]
    digest = hashlib.sha256("\n".join(f"{item['file']}:{item['sha256']}" for item in entries).encode()).hexdigest()
    return entries, digest


def merge(root: Path, report_paths: list[Path], minimum_tests: int) -> dict[str, Any]:
    errors: list[str] = []
    expected_manifest, expected_digest = current_manifest(root)
    expected_files = {item["file"] for item in expected_manifest}
    by_file: dict[str, dict[str, Any]] = {}
    source_reports: list[str] = []
    for path in report_paths:
        source_reports.append(str(path.resolve()))
        try:
            report = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{path}: cannot read shard report: {exc}")
            continue
        if report.get("suite_digest") != expected_digest:
            errors.append(f"{path}: suite digest does not match current tests")
        if report.get("status") != "pass":
            errors.append(f"{path}: shard status is not pass")
        for result in report.get("results", []):
            name = Path(str(result.get("file", ""))).name
            if not name:
                errors.append(f"{path}: result missing file")
                continue
            if name in by_file:
                errors.append(f"duplicate test file across shards: {name}")
                continue
            by_file[name] = result
    missing = sorted(expected_files - set(by_file))
    extra = sorted(set(by_file) - expected_files)
    if missing:
        errors.append(f"missing test files: {missing}")
    if extra:
        errors.append(f"unknown test files: {extra}")
    failed = sorted(name for name, result in by_file.items() if result.get("status") != "pass")
    if failed:
        errors.append(f"failed test files: {failed}")
    test_count = sum(int(result.get("test_count", 0)) for result in by_file.values())
    if test_count < minimum_tests:
        errors.append(f"expected at least {minimum_tests} tests, observed {test_count}")
    return {
        "kind": "mago-merged-test-report",
        "status": "pass" if not errors else "fail",
        "measurement_kind": "hash_bound_sharded_unittest_coverage",
        "target": str(root),
        "suite_digest": expected_digest,
        "suite_files": expected_manifest,
        "source_reports": source_reports,
        "file_count": len(by_file),
        "test_count": test_count,
        "errors": errors,
        "results": [by_file[name] for name in sorted(by_file)],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Merge Mago test shard reports and verify complete suite coverage.")
    parser.add_argument("--target", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--report", action="append", required=True)
    parser.add_argument("--minimum-tests", type=int, default=69)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    result = merge(Path(args.target).resolve(), [Path(item).resolve() for item in args.report], args.minimum_tests)
    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in ("status", "file_count", "test_count", "suite_digest", "errors")}, indent=2))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
