import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_optimization_state.py"
TEMPLATES = ROOT / "assets" / "templates"


def run(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)


def test_templates_validate_together():
    result = run(
        "--capability-map", str(TEMPLATES / "capability-map.json.template"),
        "--transformation-registry", str(TEMPLATES / "transformation-registry.json.template"),
        "--experiment-registry", str(TEMPLATES / "experiment-registry.json.template"),
        "--evaluation-plan", str(TEMPLATES / "evaluation-plan.json.template"),
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)["status"] == "pass"


def test_unknown_capability_reference_fails(tmp_path):
    cap = json.loads((TEMPLATES / "capability-map.json.template").read_text())
    trans = json.loads((TEMPLATES / "transformation-registry.json.template").read_text())
    trans["transformations"][0]["capability_refs"] = ["cap.unknown"]
    cap_path = tmp_path / "cap.json"
    trans_path = tmp_path / "trans.json"
    cap_path.write_text(json.dumps(cap))
    trans_path.write_text(json.dumps(trans))
    result = run("--capability-map", str(cap_path), "--transformation-registry", str(trans_path))
    assert result.returncode != 0
    assert "CAPABILITY_REF_UNKNOWN" in result.stdout


def test_canonical_templates_validate_without_experiment_registry():
    result = run(
        "--capability-map", str(TEMPLATES / "capability-map.json.template"),
        "--transformation-registry", str(TEMPLATES / "transformation-registry.json.template"),
        "--evaluation-plan", str(TEMPLATES / "evaluation-plan.json.template"),
    )
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads(result.stdout)
    assert report["status"] == "pass"
    assert "experiment_registry" not in report["details"]


def test_transformation_authority_cannot_self_promote(tmp_path):
    cap = json.loads((TEMPLATES / "capability-map.json.template").read_text())
    trans = json.loads((TEMPLATES / "transformation-registry.json.template").read_text())
    trans["transformations"][0]["authority"]["can_promote"] = True
    cap_path = tmp_path / "cap.json"
    trans_path = tmp_path / "trans.json"
    cap_path.write_text(json.dumps(cap))
    trans_path.write_text(json.dumps(trans))
    result = run("--capability-map", str(cap_path), "--transformation-registry", str(trans_path))
    assert result.returncode != 0
    assert "AUTHORITY_PROMOTE" in result.stdout


def test_contaminated_evaluation_requires_blind_l5_holdout(tmp_path):
    plan = json.loads((TEMPLATES / "evaluation-plan.json.template").read_text())
    plan["contamination"]["status"] = "contaminated"
    plan["contamination"]["promotion_holdout_required"] = True
    plan["contamination"]["reason"] = "Candidate received development evaluator feedback during repair."
    path = tmp_path / "plan.json"
    path.write_text(json.dumps(plan))
    result = run("--evaluation-plan", str(path))
    assert result.returncode != 0
    assert "CONTAMINATION_L5" in result.stdout or "CONTAMINATION_FINALIST" in result.stdout


def test_contaminated_evaluation_passes_with_blind_l5_holdout(tmp_path):
    plan = json.loads((TEMPLATES / "evaluation-plan.json.template").read_text())
    plan["contamination"]["status"] = "contaminated"
    plan["contamination"]["promotion_holdout_required"] = True
    plan["contamination"]["reason"] = "Candidate received development evaluator feedback during repair."
    for level in plan["levels"]:
        if level["id"] == "L5-holdout":
            level["required"] = True
    plan["finalist_policy"]["minimum_evaluation_level"] = "L5-holdout"
    plan["finalist_policy"]["holdout_policy"] = "blind-pass-required"
    path = tmp_path / "plan.json"
    path.write_text(json.dumps(plan))
    result = run("--evaluation-plan", str(path))
    assert result.returncode == 0, result.stdout + result.stderr
