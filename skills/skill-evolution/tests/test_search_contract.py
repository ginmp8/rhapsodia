import copy
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


contract_mod = load("contract_v2", SCRIPTS / "validate_search_contract.py")
state_mod = load("state_v2", SCRIPTS / "validate_search_state.py")


def template(name):
    return json.loads((ROOT / "assets/templates" / name).read_text())


def test_contract_template_valid():
    assert contract_mod.validate(template("search-contract.json.template")) == []


def test_contract_rejects_v1_instead_of_silently_reinterpreting():
    c = template("search-contract.json.template")
    c["contract_version"] = 1
    assert "contract_version:upgrade_required_v2" in contract_mod.validate(c)


def test_contract_rejects_budget_above_20():
    c = template("search-contract.json.template")
    c["budget"]["max_total_candidates"] = 21
    assert "budget:max_total_candidates_exceeds_20" in contract_mod.validate(c)


def test_contract_rejects_transformation_dependency_cycle():
    c = template("search-contract.json.template")
    c["transformation_registry"].extend([
        {"id":"T004","status":"proposed","depends_on":["T005"],"conflicts_with":[],"capability_effects":[],"violates_invariants":[],"addresses":[]},
        {"id":"T005","status":"proposed","depends_on":["T004"],"conflicts_with":[],"capability_effects":[],"violates_invariants":[],"addresses":[]},
    ])
    assert any(e.startswith("transformation_dependency_cycle") for e in contract_mod.validate(c))


def test_state_template_valid():
    c = template("search-contract.json.template")
    s = template("search-state.json.template")
    assert state_mod.validate(c, s) == []


def test_state_rejects_generation_receipt_mismatch():
    c = template("search-contract.json.template")
    s = template("search-state.json.template")
    s["candidates"][0]["generation_receipt"]["candidate_identity"] = "different-bytes"
    assert "candidate:C_CANONICAL:generation_receipt_candidate_mismatch" in state_mod.validate(c, s)


def test_state_rejects_evaluator_identity_drift():
    c = template("search-contract.json.template")
    s = template("search-state.json.template")
    s["candidates"][0]["evaluation"]["identity"]["evaluator_id"] = "changed-grader"
    assert "candidate:C_CANONICAL:evaluation_identity_mismatch" in state_mod.validate(c, s)


def test_state_rejects_missing_transformation_dependency():
    c = template("search-contract.json.template")
    c["transformation_registry"].append(
        {"id":"T004","status":"proposed","depends_on":["T002"],"conflicts_with":[],"capability_effects":["docs"],"violates_invariants":[],"addresses":[]}
    )
    s = template("search-state.json.template")
    cand = s["candidates"][0]
    cand["transformation_ids"] = ["T004"]
    cand["expected_capability_effects"] = ["docs"]
    cand["generation_receipt"]["transformation_ids"] = ["T004"]
    errors = state_mod.validate(c, s)
    assert "candidate:C_CANONICAL:transformation:T004:missing_dependency:T002" in errors


def test_state_requires_parent_to_precede_child():
    c = template("search-contract.json.template")
    s = template("search-state.json.template")
    child = copy.deepcopy(s["candidates"][0])
    child["candidate_id"] = "C_CHILD"
    child["candidate_identity"] = "child-bytes"
    child["parent_ids"] = ["C_LATER"]
    child["base_parent_id"] = "C_LATER"
    child["generation_receipt"]["candidate_identity"] = "child-bytes"
    child["generation_receipt"]["base_parent_id"] = "C_LATER"
    child["generation_receipt"]["receipt_identity"] = "child-receipt"
    child["transformation_ids"] = ["T002"]
    child["expected_capability_effects"] = ["activation"]
    child["generation_receipt"]["transformation_ids"] = ["T002"]
    s["candidates"] = [child, s["candidates"][0]]
    assert "candidate:C_CHILD:parent_not_prior:C_LATER" in state_mod.validate(c, s)
