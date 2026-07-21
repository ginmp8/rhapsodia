from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "select_validation_checks.py"


def run_case(tmp_path: Path, data: dict, *, expect=0) -> dict:
    source = tmp_path / "request.json"
    source.write_text(json.dumps(data), encoding="utf-8")
    result = subprocess.run([sys.executable, str(SCRIPT), "--input", str(source)], capture_output=True, text=True)
    assert result.returncode == expect, result.stderr
    return json.loads(result.stdout)


def test_code_only_selects_targeted_proof(tmp_path: Path):
    result = run_case(tmp_path, {"surfaces": ["code"], "available_checks": ["targeted-test"]})
    assert result["risk_profile"] == "standard"
    assert result["narrowest_proving_category"] == "targeted-test"
    assert result["blocked_required_checks"] == []


def test_api_escalates_and_requires_contract_checks(tmp_path: Path):
    result = run_case(tmp_path, {"surfaces": ["code", "api"], "available_checks": ["targeted-test"]})
    assert result["risk_profile"] == "governed"
    assert result["status"] == "blocked-required-checks"
    assert {"contract-validation", "compatibility", "integration"} <= set(result["blocked_required_checks"])


def test_migration_requires_forward_data_and_recovery(tmp_path: Path):
    checks = ["migration-forward", "data-integrity", "rollback-recovery"]
    result = run_case(tmp_path, {"surfaces": ["migration"], "available_checks": checks})
    assert result["status"] == "ready-to-execute-checks"
    assert result["required_checks"] == checks


def test_sensitive_surfaces_keep_distinct_checks(tmp_path: Path):
    result = run_case(tmp_path, {"surfaces": ["auth", "secrets", "pii"], "available_checks": []})
    assert "authorization" in result["required_checks"]
    assert "secret-handling" in result["required_checks"]
    assert "sensitive-data" in result["required_checks"]


def test_unknown_surface_is_blocked(tmp_path: Path):
    result = run_case(tmp_path, {"surfaces": ["magic"], "available_checks": []}, expect=1)
    assert result["status"] == "blocked"
    assert "unknown surfaces" in result["errors"][0]
