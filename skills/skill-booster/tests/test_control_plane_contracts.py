from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "assets" / "templates"
SCRIPTS = ROOT / "scripts"


def run(script: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script), *args],
        capture_output=True,
        text=True,
    )


def write_json(path: Path, data: dict) -> Path:
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def test_run_state_template_validates() -> None:
    result = run("validate_run_state.py", "--state", str(TEMPLATES / "optimization-run-state.json.template"))
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads(result.stdout)
    assert report["status"] == "pass"
    assert report["resume_allowed"] is True


def test_run_state_rejects_stale_candidate_evidence(tmp_path: Path) -> None:
    state = json.loads((TEMPLATES / "optimization-run-state.json.template").read_text(encoding="utf-8"))
    state["evidence"]["candidate_bound"] = [
        {
            "id": "EV-CANDIDATE-1",
            "candidate_identity": "sha256:" + "1" * 64,
            "status": "pass",
        }
    ]
    path = write_json(tmp_path / "state.json", state)
    result = run("validate_run_state.py", "--state", str(path))
    assert result.returncode != 0
    assert "STALE_EVIDENCE" in result.stdout


def test_strategy_template_validates() -> None:
    result = run("validate_strategy_decision.py", "--input", str(TEMPLATES / "strategy-decision.json.template"))
    assert result.returncode == 0, result.stdout + result.stderr


def test_evolution_requires_explicit_authorization(tmp_path: Path) -> None:
    decision = json.loads((TEMPLATES / "strategy-decision.json.template").read_text(encoding="utf-8"))
    decision["selected_strategy"] = "evolutionary-search"
    decision["simpler_strategy_considered"] = "single-candidate"
    decision["budget"]["max_candidates"] = 4
    decision["evolution_explicit_authorization"] = False
    path = write_json(tmp_path / "strategy.json", decision)
    result = run("validate_strategy_decision.py", "--input", str(path))
    assert result.returncode != 0
    assert "EVOLUTION_AUTH" in result.stdout


def test_consumer_contract_template_validates() -> None:
    result = run(
        "validate_consumer_contract_evidence.py",
        "--input", str(TEMPLATES / "consumer-contract-evidence.json.template"),
        "--require-all-pass",
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_consumer_contract_required_failure_blocks(tmp_path: Path) -> None:
    evidence = json.loads((TEMPLATES / "consumer-contract-evidence.json.template").read_text(encoding="utf-8"))
    evidence["verifications"][0]["status"] = "fail"
    path = write_json(tmp_path / "consumer.json", evidence)
    result = run("validate_consumer_contract_evidence.py", "--input", str(path), "--require-all-pass")
    assert result.returncode != 0
    assert "CONTRACT_GATE" in result.stdout


def test_promotion_attestation_template_validates() -> None:
    result = run("validate_promotion_attestation.py", "--input", str(TEMPLATES / "promotion-attestation.json.template"))
    assert result.returncode == 0, result.stdout + result.stderr


def test_promotion_attestation_rejects_approved_candidate_mismatch(tmp_path: Path) -> None:
    attestation = json.loads((TEMPLATES / "promotion-attestation.json.template").read_text(encoding="utf-8"))
    attestation["decision"]["approved_candidate_identity"] = "sha256:" + "1" * 64
    path = write_json(tmp_path / "attestation.json", attestation)
    result = run("validate_promotion_attestation.py", "--input", str(path))
    assert result.returncode != 0
    assert "approved_candidate_identity" in result.stdout
