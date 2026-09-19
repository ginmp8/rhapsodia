from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_self_improvement_receipt.py"
A, B, C, D, E = (x * 64 for x in "abcde")


def receipt() -> dict:
    return {
        "schema_version": 1,
        "run_id": "run-1",
        "generation_id": "gen-1",
        "controller_identity_sha256": A,
        "baseline_identity_sha256": A,
        "candidate_identity_sha256": B,
        "evaluator_identity_sha256": C,
        "last_known_good_identity_sha256": D,
        "max_self_recursion_depth": 1,
        "controller_unchanged": True,
        "evaluator_unchanged": True,
        "candidate_frozen": True,
        "external_validation_surface": True,
        "gate_status": "pass",
        "decision": "promote",
        "promoted_identity_sha256": B,
    }


def run(payload: dict):
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "receipt.json"
        p.write_text(json.dumps(payload), encoding="utf-8")
        return subprocess.run([sys.executable, str(SCRIPT), str(p)], capture_output=True, text=True)


def test_valid_promotion_receipt_passes():
    result = run(receipt())
    assert result.returncode == 0, result.stdout + result.stderr


def test_same_controller_candidate_fails():
    payload = receipt()
    payload["candidate_identity_sha256"] = A
    payload["promoted_identity_sha256"] = A
    result = run(payload)
    assert result.returncode != 0
    assert "must differ" in result.stdout


def test_promotion_must_match_frozen_candidate():
    payload = receipt()
    payload["promoted_identity_sha256"] = E
    result = run(payload)
    assert result.returncode != 0
    assert "must equal candidate" in result.stdout


def test_failed_gate_cannot_promote():
    payload = receipt()
    payload["gate_status"] = "fail"
    result = run(payload)
    assert result.returncode != 0
    assert "passing gate_status" in result.stdout
