import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("vee", ROOT / "scripts" / "validate_execution_evidence.py")
MOD = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MOD)

SHA = "a" * 64


def evidence(**overrides):
    data = {
        "schema_version": 1,
        "run_id": "run-1",
        "arm": "candidate",
        "evidence_status": "executed",
        "target_identity_sha256": SHA,
        "evaluator_identity_sha256": SHA,
        "scenario_suite_sha256": SHA,
        "host_profile": "portable-test",
        "isolation_level": "workspace",
        "candidate_visible_manifest_sha256": SHA,
        "evaluator_only_manifest_sha256": SHA,
        "trace": {"status": "available", "reference": "trace-1", "sha256": SHA},
        "leakage_check": {"status": "pass", "candidate_saw_evaluator_only_assets": False, "notes": ""},
        "scenarios": [{"id": "s1"}],
    }
    data.update(overrides)
    return data


def test_valid_execution_is_measured_eligible():
    result = MOD.validate(evidence())
    assert result["status"] == "pass"
    assert result["checks"]["measured_claim_eligible"] is True


def test_hidden_evaluator_leak_fails():
    data = evidence()
    data["leakage_check"] = {"status": "pass", "candidate_saw_evaluator_only_assets": True}
    result = MOD.validate(data)
    assert result["status"] == "fail"
    assert result["checks"]["measured_claim_eligible"] is False


def test_without_skill_rejects_target_hash():
    result = MOD.validate(evidence(arm="without-skill"))
    assert result["status"] == "fail"
