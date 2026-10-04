from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def load_script(name: str):
    path = ROOT / "scripts" / name
    spec = importlib.util.spec_from_file_location(f"testmod_{path.stem}", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


REPRO = load_script("validate_reproducibility_profiles.py")
CAL = load_script("validate_grader_calibration.py")
META = load_script("validate_metamorphic_suite.py")
PROV = load_script("validate_evaluation_provenance.py")
HOLDOUT = load_script("validate_holdout_exposure.py")
TRUST = load_script("assess_target_trust.py")
SHA = "a" * 64


def template(name: str):
    return json.loads((ROOT / "assets" / "templates" / name).read_text(encoding="utf-8"))


def test_environment_profile_template_is_valid():
    data = template("execution-environment.json.template")
    diagnostics, _ = REPRO.validate_environment(data)
    assert diagnostics == []


def test_environment_identity_detects_material_drift():
    left = template("execution-environment.json.template")
    right = json.loads(json.dumps(left))
    right["model"]["name"] = "different-model"
    assert REPRO.canonical_hash(REPRO.normalized_environment_identity(left)) != REPRO.canonical_hash(REPRO.normalized_environment_identity(right))


def test_stochastic_profile_derives_uncertainty_and_pass_power():
    data = template("stochastic-evaluation.json.template")
    data["trials"] = [
        {"id": "trial-1", "outcome": "success"},
        {"id": "trial-2", "outcome": "success"},
        {"id": "trial-3", "outcome": "failure"},
    ]
    diagnostics, metrics = REPRO.validate_stochastic(data)
    assert diagnostics == []
    assert metrics["success_count"] == 2
    assert metrics["failure_count"] == 1
    assert 0.0 < metrics["wilson_95"][0] < metrics["wilson_95"][1] < 1.0
    assert abs(metrics["pass_power"]["3"] - (2 / 3) ** 3) < 1e-12


def test_strong_stochastic_claim_requires_independent_replication():
    data = template("stochastic-evaluation.json.template")
    data["claim"] = {"level": "strong", "independent_replication": False}
    diagnostics, _ = REPRO.validate_stochastic(data)
    assert any(item["code"] == "STRONG_CLAIM_REPLICATION_REQUIRED" for item in diagnostics)


def test_execution_lineage_template_is_valid():
    diagnostics, metrics = REPRO.validate_lineage(template("execution-lineage.json.template"))
    assert diagnostics == []
    assert metrics["node_count"] == 1


def test_execution_lineage_rejects_cycle():
    data = template("execution-lineage.json.template")
    data["nodes"][0]["upstream"] = ["node-1"]
    diagnostics, _ = REPRO.validate_lineage(data)
    assert any(item["code"] == "LINEAGE_CYCLE" for item in diagnostics)


def test_grader_calibration_template_passes():
    result = CAL.validate(template("grader-calibration.json.template"))
    assert result["status"] == "pass", result
    assert result["metrics"]["agreement"] >= 0.8


def test_grader_calibration_rejects_position_bias_probe_below_threshold():
    data = template("grader-calibration.json.template")
    data["bias_probes"]["order_swap_consistent"] = 2
    result = CAL.validate(data)
    assert result["status"] == "fail"
    assert any("order_swap" in error for error in result["errors"])


def test_metamorphic_suite_template_passes_as_planned():
    result = META.validate(template("metamorphic-suite.json.template"))
    assert result["status"] == "pass", result
    assert result["metrics"]["group_count"] == 1


def test_measured_metamorphic_suite_requires_variant_results():
    data = template("metamorphic-suite.json.template")
    data["status"] = "measured"
    result = META.validate(data)
    assert result["status"] == "fail"


def test_evaluation_provenance_template_passes():
    result = PROV.validate(template("evaluation-provenance.json.template"))
    assert result["status"] == "pass", result
    assert result["subject_count"] == 1


def test_evaluation_provenance_rejects_invalid_subject_digest():
    data = template("evaluation-provenance.json.template")
    data["subjects"][0]["sha256"] = "not-a-digest"
    result = PROV.validate(data)
    assert result["status"] == "fail"


def test_holdout_exposure_template_passes():
    result = HOLDOUT.validate(template("holdout-exposure.json.template"))
    assert result["status"] == "pass", result
    assert result["blind_eligible_count"] == 1


def test_holdout_feedback_invalidates_blind_claim():
    data = template("holdout-exposure.json.template")
    data["lineages"][0]["used_for_mutation"] = True
    result = HOLDOUT.validate(data)
    assert result["status"] == "fail"


def test_trusted_local_target_may_execute_after_static_preflight():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "SKILL.md").write_text("---\nname: x\ndescription: x\n---\n", encoding="utf-8")
        (root / "scripts").mkdir()
        (root / "scripts" / "check.py").write_text("print('ok')\n", encoding="utf-8")
        result = TRUST.assess(root, "trusted-local")
        assert result["status"] == "pass"
        assert result["execution_policy"] == "trusted"


def test_external_executable_target_requires_sandbox():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "SKILL.md").write_text("---\nname: x\ndescription: x\n---\n", encoding="utf-8")
        (root / "runner.py").write_text("print('external')\n", encoding="utf-8")
        result = TRUST.assess(root, "external-untrusted")
        assert result["status"] == "pass"
        assert result["execution_policy"] == "sandbox-required"
        assert result["requirements"]


def test_secret_like_file_blocks_execution_preflight():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "SKILL.md").write_text("---\nname: x\ndescription: x\n---\n", encoding="utf-8")
        (root / ".env").write_text("TOKEN=x\n", encoding="utf-8")
        result = TRUST.assess(root, "external-untrusted")
        assert result["status"] == "fail"
        assert result["execution_policy"] == "inspect-only"
