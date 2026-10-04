from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_change_gate_result.py"
spec = importlib.util.spec_from_file_location("result_validator", SCRIPT)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
ZERO = "0" * 64


def valid() -> dict:
    return {
        "result_version": 1,
        "subject": {"candidate_tree_sha256": ZERO, "baseline_tree_sha256": None, "direct_parent_identity": None, "destination_identity": None},
        "gate": {"mode": "candidate-gate", "policy": "normal", "portability_profile": "portable", "policy_identity": None, "verifier_identity": None},
        "status": "pass",
        "decision_for_caller": "accept",
        "claim_scope": "local-acceptance",
        "freshness": "not-applicable",
        "evidence": [],
        "findings": [],
        "waivers": [],
        "portability": {"portable_core": "pass"},
    }


def test_valid_result_passes() -> None:
    assert module.validate(valid(), ZERO) == []


def test_candidate_mismatch_fails() -> None:
    assert "subject.candidate_tree_sha256:mismatch" in module.validate(valid(), "1" * 64)


def test_finding_requires_rule_origin_and_regression_delta() -> None:
    d = valid()
    d["findings"] = [{"severity": "material", "area": "activation", "origin": "candidate", "finding": "x", "decision_impact": "warning"}]
    errors = module.validate(d, ZERO)
    assert "findings[0].rule_origin:invalid" in errors
    assert "findings[0].regression_delta:invalid" in errors
