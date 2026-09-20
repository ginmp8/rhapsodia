#!/usr/bin/env python3
"""Run Skill Harness self-tests with only the Python standard library."""
from __future__ import annotations

import argparse
import importlib.util
import inspect
import json
import sys
import traceback
from pathlib import Path

sys.dont_write_bytecode = True


def _load_module(path: Path, index: int):
    name = f"_skill_harness_test_{index}_{path.stem}"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load test module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _zero_arg_test(function) -> bool:
    signature = inspect.signature(function)
    for parameter in signature.parameters.values():
        if parameter.kind in (parameter.VAR_POSITIONAL, parameter.VAR_KEYWORD):
            continue
        if parameter.default is inspect.Parameter.empty:
            return False
    return True


def run_tests(tests_dir: Path) -> dict:
    tests_dir = tests_dir.expanduser().resolve()
    files = sorted(tests_dir.glob("test_*.py")) if tests_dir.is_dir() else []
    results: list[dict] = []
    module_errors: list[dict] = []

    for index, path in enumerate(files):
        try:
            module = _load_module(path, index)
        except BaseException as exc:  # test import failures are evidence, not runner crashes
            module_errors.append(
                {
                    "file": path.name,
                    "error": f"{type(exc).__name__}: {exc}",
                    "traceback": traceback.format_exc(),
                }
            )
            continue

        functions = [
            (name, value)
            for name, value in vars(module).items()
            if name.startswith("test_") and inspect.isfunction(value) and value.__module__ == module.__name__
        ]
        for name, function in sorted(functions, key=lambda item: item[0]):
            test_id = f"{path.name}::{name}"
            if not _zero_arg_test(function):
                results.append({"id": test_id, "status": "fail", "error": "test requires arguments/fixtures"})
                continue
            try:
                function()
                results.append({"id": test_id, "status": "pass"})
            except BaseException as exc:  # capture assertion/SystemExit evidence per test
                results.append(
                    {
                        "id": test_id,
                        "status": "fail",
                        "error": f"{type(exc).__name__}: {exc}",
                        "traceback": traceback.format_exc(),
                    }
                )

    passed = sum(item["status"] == "pass" for item in results)
    failed = sum(item["status"] == "fail" for item in results) + len(module_errors)
    discovered = len(results)
    status = "pass" if files and discovered > 0 and failed == 0 else "fail"
    errors: list[str] = []
    if not tests_dir.is_dir():
        errors.append("tests directory does not exist")
    elif not files:
        errors.append("no test_*.py files found")
    elif discovered == 0 and not module_errors:
        errors.append("no test_* functions discovered")

    return {
        "status": status,
        "tests_dir": str(tests_dir),
        "test_files": [path.name for path in files],
        "discovered_tests": discovered,
        "passed": passed,
        "failed": failed,
        "module_errors": module_errors,
        "results": results,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run zero-argument test_* functions without pytest or third-party packages.")
    default_tests = Path(__file__).resolve().parents[1] / "tests"
    parser.add_argument("--tests-dir", default=str(default_tests))
    parser.add_argument("--output")
    args = parser.parse_args()

    report = run_tests(Path(args.tests_dir))
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        output = Path(args.output).expanduser()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload, encoding="utf-8")
    sys.stdout.write(payload)
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
