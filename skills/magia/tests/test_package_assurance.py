from __future__ import annotations

import importlib.util
import json
import shutil
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))


def load_script(name: str):
    path = SCRIPTS / name
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def valid_report(root: Path) -> dict:
    runner = load_script("run_test_suite.py")
    manifest, digest = runner.suite_manifest(root)
    return {
        "kind": runner.REPORT_KIND,
        "status": "pass",
        "root": str(root),
        "suite_files": manifest,
        "suite_digest": digest,
        "test_count": 1,
        "command": ["supplied-test-evidence"],
        "return_code": 0,
        "errors": [],
    }


def test_test_dependency_is_declared():
    validator = load_script("validate_skill_package.py")
    assert validator.validate_test_dependency(ROOT) == []


def test_hash_bound_test_report_accepts_current_suite_and_rejects_drift(tmp_path: Path):
    validator = load_script("validate_skill_package.py")
    report = valid_report(ROOT)
    assert validator.validate_test_report(ROOT, report) == []

    copied = tmp_path / "magia"
    shutil.copytree(ROOT, copied, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
    test_file = copied / "tests" / "test_validation_selection.py"
    test_file.write_text(test_file.read_text(encoding="utf-8") + "\n# drift\n", encoding="utf-8")
    errors = validator.validate_test_report(copied, report)
    assert any("digest" in error or "manifest" in error for error in errors)


def test_package_readiness_requires_test_evidence():
    validator = load_script("validate_skill_package.py")
    result = validator.validate_target(ROOT, require_tests=True)
    assert result["status"] == "fail"
    assert any("test report" in error for error in result["errors"])


def test_contract_semantics_rejects_generic_alias_preservation(tmp_path: Path):
    semantic = load_script("validate_contract_semantics.py")
    assert semantic.collect_errors(ROOT) == []

    copied = tmp_path / "magia"
    (copied / "references").mkdir(parents=True)
    source = (ROOT / "references" / "shared-artifact-ownership.md").read_text(encoding="utf-8")
    source = source.replace(
        "Preserve identity, versions, dependencies, supersession, handoff, `business_priority`, `technical_criticality`, `execution_sequence`, and provenance.",
        "Preserve identity, versions, dependencies, supersession, handoff, priority, order hint, and provenance.",
    )
    (copied / "references" / "shared-artifact-ownership.md").write_text(source, encoding="utf-8")
    errors = semantic.collect_errors(copied)
    assert any("unsupported generic priority alias" in error for error in errors)


def test_runner_reports_missing_pytest_as_environment_failure():
    runner = load_script("run_test_suite.py")
    with patch.object(runner.importlib.util, "find_spec", return_value=None):
        result = runner.run_suite(ROOT)
    assert result["status"] == "fail"
    assert result["failure_classification"] == "environment"


def test_runner_builds_passing_report_from_pytest_output():
    runner = load_script("run_test_suite.py")
    completed = SimpleNamespace(returncode=0, stdout="104 passed in 1.00s\n", stderr="")
    with patch.object(runner.subprocess, "run", return_value=completed):
        result = runner.run_suite(ROOT)
    assert result["status"] == "pass"
    assert result["test_count"] == 104
    assert result["suite_digest"]
