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


contract_mod = load("contract_extensions", SCRIPTS / "validate_evidence_aware_search_contract.py")
eval_mod = load("evaluation_extensions", SCRIPTS / "validate_evidence_aware_candidate_evaluation.py")
selection_mod = load("selection_extensions", SCRIPTS / "select_survivors_evidence_aware.py")


def template(name):
    return json.loads((ROOT / "assets/templates" / name).read_text())


def candidate(base, cid, role, transforms, effects, quality, token_cost):
    c = copy.deepcopy(base)
    c["candidate_id"] = cid
    c["role"] = role
    c["candidate_identity"] = f"bytes-{cid}"
    c["transformation_ids"] = transforms
    c["expected_capability_effects"] = effects
    c["generation_receipt"]["receipt_identity"] = f"receipt-{cid}"
    c["generation_receipt"]["candidate_identity"] = f"bytes-{cid}"
    c["generation_receipt"]["transformation_ids"] = transforms
    c["evaluation"]["metrics"] = {
        "quality": {"value": quality, "uncertainty": 0.0},
        "token_cost": {"value": token_cost, "uncertainty": 0.0},
    }
    return c


def state_with(candidates):
    state = template("search-state-evidence-aware.json.template")
    state["candidates"] = candidates
    state["pareto_archive"] = []
    state["finalists"] = []
    return state


def test_contract_accepts_evidence_aware_optional_policies():
    contract = template("search-contract-evidence-aware.json.template")
    contract["evidence_aware"]["required_evaluation_slices"] = ["activation-regression"]
    contract["evidence_aware"]["complexity_policy"] = {
        "id": "metric-upper-bounds-v1",
        "limits": {"token_cost": 1200},
    }
    contract["evidence_aware"]["uncertainty_metadata_required"] = True
    contract["evidence_aware"]["stability_policy"] = {
        "id": "minimum-win-rate-v1",
        "method_id": "bootstrap-v1",
        "minimum_win_rate": 0.7,
        "minimum_resamples": 20,
    }
    contract["evidence_aware"]["frontier_policy"] = {
        "id": "aggregate-plus-scenario-elites-v1",
        "scenario_direction": "maximize",
        "scenario_min_delta": 0.0,
    }
    contract["evidence_aware"]["novelty_policy"] = {
        "id": "behavior-label-jaccard-v1",
        "source": "derived",
        "descriptor_id": "skill-behavior-v1",
    }
    assert contract_mod.validate(contract) == []


def test_candidate_evaluation_requires_statistics_when_contract_requires_metadata():
    contract = template("search-contract-evidence-aware.json.template")
    contract["evidence_aware"]["uncertainty_metadata_required"] = True
    envelope = template("candidate-evaluation-evidence-aware.json.template")
    del envelope["evaluation"]["statistics"]
    errors = eval_mod.validate(contract, envelope)
    assert "statistics:required" in errors


def test_required_slice_failure_is_eliminated_before_pareto():
    contract = template("search-contract-evidence-aware.json.template")
    contract["evidence_aware"]["required_evaluation_slices"] = ["activation-regression"]
    base = template("search-state-evidence-aware.json.template")["candidates"][0]
    a = candidate(base, "C_CANONICAL", "canonical", ["T001"], ["canonical-baseline"], 0.90, 1000)
    b = candidate(base, "C002", "focused", ["T002"], ["activation"], 0.95, 900)
    a["evaluation"]["slices"] = {"activation-regression": "pass"}
    b["evaluation"]["slices"] = {"activation-regression": "fail"}
    result = selection_mod.select(contract, state_with([a, b]))
    assert result["eliminated_required_slice"] == ["C002"]
    assert result["pareto_frontier"] == ["C_CANONICAL"]


def test_stability_policy_eliminates_candidate_below_threshold():
    contract = template("search-contract-evidence-aware.json.template")
    contract["evidence_aware"]["stability_policy"] = {
        "id": "minimum-win-rate-v1",
        "method_id": "bootstrap-v1",
        "minimum_win_rate": 0.70,
        "minimum_resamples": 20,
    }
    base = template("search-state-evidence-aware.json.template")["candidates"][0]
    a = candidate(base, "C_CANONICAL", "canonical", ["T001"], ["canonical-baseline"], 0.90, 1000)
    b = candidate(base, "C002", "focused", ["T002"], ["activation"], 0.95, 900)
    a["evaluation"]["stability"] = {"method_id": "bootstrap-v1", "win_rate": 0.80, "resamples": 20}
    b["evaluation"]["stability"] = {"method_id": "bootstrap-v1", "win_rate": 0.65, "resamples": 20}
    result = selection_mod.select(contract, state_with([a, b]))
    assert result["eliminated_stability"] == ["C002"]
    assert result["pareto_frontier"] == ["C_CANONICAL"]


def test_hybrid_frontier_preserves_scenario_specialist():
    contract = template("search-contract-evidence-aware.json.template")
    contract["evidence_aware"]["frontier_policy"] = {
        "id": "aggregate-plus-scenario-elites-v1",
        "scenario_direction": "maximize",
        "scenario_min_delta": 0.0,
    }
    base = template("search-state-evidence-aware.json.template")["candidates"][0]
    a = candidate(base, "C_CANONICAL", "canonical", ["T001"], ["canonical-baseline"], 0.95, 800)
    b = candidate(base, "C002", "focused", ["T002"], ["activation"], 0.90, 900)
    a["evaluation"]["scenario_scores"] = {"edge-case": 0.60}
    b["evaluation"]["scenario_scores"] = {"edge-case": 0.95}
    result = selection_mod.select(contract, state_with([a, b]))
    assert result["pareto_frontier"] == ["C_CANONICAL"]
    assert result["scenario_elites"] == ["C002"]
    assert "C002" in result["selected_survivors"]


def test_behavioral_novelty_prefers_behaviorally_distinct_frontier_candidate():
    contract = template("search-contract-evidence-aware.json.template")
    contract["budget"]["max_active_candidates"] = 2
    contract["evidence_aware"]["novelty_policy"] = {
        "id": "behavior-label-jaccard-v1",
        "source": "derived",
        "descriptor_id": "skill-behavior-v1",
    }
    base = template("search-state-evidence-aware.json.template")["candidates"][0]
    a = candidate(base, "C_CANONICAL", "canonical", ["T001"], ["canonical-baseline"], 0.90, 1000)
    b = candidate(base, "C002", "focused", ["T002"], ["activation"], 0.91, 1000)
    c = candidate(base, "C003", "novel-bounded", ["T003"], ["lineage-integrity"], 0.91, 1000)
    a["evaluation"]["behavior_descriptor"] = {"descriptor_id": "skill-behavior-v1", "labels": ["activation", "boundary"]}
    b["evaluation"]["behavior_descriptor"] = {"descriptor_id": "skill-behavior-v1", "labels": ["activation", "boundary"]}
    c["evaluation"]["behavior_descriptor"] = {"descriptor_id": "skill-behavior-v1", "labels": ["portability"]}
    b["status"] = "evaluating"
    c["status"] = "evaluating"
    result = selection_mod.select(contract, state_with([a, b, c]))
    assert result["selected_survivors"] == ["C_CANONICAL", "C003"]


def test_complexity_limit_eliminates_candidate_before_pareto():
    contract = template("search-contract-evidence-aware.json.template")
    contract["evidence_aware"]["complexity_policy"] = {
        "id": "metric-upper-bounds-v1",
        "limits": {"token_cost": 1100},
    }
    base = template("search-state-evidence-aware.json.template")["candidates"][0]
    a = candidate(base, "C_CANONICAL", "canonical", ["T001"], ["canonical-baseline"], 0.90, 1000)
    b = candidate(base, "C002", "focused", ["T002"], ["activation"], 0.95, 1200)
    result = selection_mod.select(contract, state_with([a, b]))
    assert result["eliminated_complexity"] == ["C002"]
    assert result["pareto_frontier"] == ["C_CANONICAL"]
