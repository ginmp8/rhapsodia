import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


contract_mod = load("evidence_profile_contract", SCRIPTS / "validate_evidence_aware_search_contract.py")
state_mod = load("evidence_profile_state", SCRIPTS / "validate_evidence_aware_search_state.py")
evaluation_mod = load("evidence_profile_eval", SCRIPTS / "validate_evidence_aware_candidate_evaluation.py")


def template(name):
    return json.loads((ROOT / "assets/templates" / name).read_text(encoding="utf-8"))


def test_evidence_aware_profile_templates_are_valid_and_coherent():
    contract = template("search-contract-evidence-aware.json.template")
    state = template("search-state-evidence-aware.json.template")
    evaluation = template("candidate-evaluation-evidence-aware.json.template")

    assert contract["contract_version"] == 4
    assert contract["evidence_aware"]["uncertainty_metadata_required"] is True
    assert contract["evidence_aware"]["frontier_policy"]["id"] == "aggregate-plus-scenario-elites-v1"
    assert contract["evidence_aware"]["novelty_policy"]["id"] == "behavior-label-jaccard-v1"
    assert contract["evidence_aware"]["stagnation_policy"]["id"] == "pareto-plus-semantic-signatures-v1"
    assert contract_mod.validate(contract) == []
    assert state_mod.validate(contract, state) == []
    assert evaluation_mod.validate(contract, evaluation) == []


def test_package_validator_requires_evidence_aware_profile_templates(tmp_path):
    import shutil
    import subprocess
    target = tmp_path / "skill-evolution"
    shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
    (target / "assets/templates/search-contract-evidence-aware.json.template").unlink()
    validator = target / "scripts/validate_skill_evolution.py"
    proc = subprocess.run([sys.executable, str(validator), "--target", str(target)], text=True, capture_output=True, check=False)
    report = json.loads(proc.stdout)
    assert proc.returncode == 2
    assert "missing:assets/templates/search-contract-evidence-aware.json.template" in report["errors"]
