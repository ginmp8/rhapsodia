import copy
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


build_mod = load("build_v4_finalist", ROOT / "scripts" / "build_evolution_contract.py")
handoff_mod = load("handoff_v4_finalist", ROOT / "scripts" / "validate_evolution_handoff.py")
pre_mod = load("pre_v4_finalist", ROOT / "scripts" / "validate_pre_evolution_state.py")


def handoff_template():
    return json.loads((ROOT / "assets" / "templates" / "evolution-handoff.json.template").read_text())


def evaluation_plan_template():
    return json.loads((ROOT / "assets" / "templates" / "evaluation-plan.json.template").read_text())


def write_inputs(tmp_path, evaluation_plan):
    target = "sha256:test"
    cap = {"schema_version": 1, "target": {"name": "x", "identity": target, "class": "orchestration-meta"}, "capabilities": []}
    tr = {"schema_version": 1, "target_identity": target, "transformations": []}
    hyp = {"schema_version": "2.0", "target": {"name": "x", "identity": target}, "items": []}
    for name, data in [("cap.json", cap), ("tr.json", tr), ("ev.json", evaluation_plan), ("hyp.json", hyp)]:
        (tmp_path / name).write_text(json.dumps(data))
    handoff = handoff_template()
    handoff["target_identity"] = target
    handoff["artifact_refs"] = {
        "capability_map": "cap.json",
        "hypothesis_pool": "hyp.json",
        "transformation_registry": "tr.json",
        "evaluation_plan": "ev.json",
    }
    return handoff


def test_evaluation_plan_v2_declares_finalist_policy():
    plan = evaluation_plan_template()
    assert plan["schema_version"] == 2
    assert plan["finalist_policy"] == {
        "minimum_evaluation_level": "L4-benchmark",
        "holdout_policy": "not-required",
    }
    errors, _ = pre_mod.validate_evaluation_plan(plan)
    assert errors == []


def test_handoff_v4_carries_finalist_policy():
    handoff = handoff_template()
    assert handoff["handoff_version"] == 4
    assert handoff["contract_version"] == 4
    assert handoff["finalist_policy"]["minimum_evaluation_level"] == "L4-benchmark"
    assert handoff_mod.validate(handoff) == []


def test_compiled_search_contract_v4_uses_frozen_evaluation_plan_policy(tmp_path):
    plan = evaluation_plan_template()
    plan["target_identity"] = "sha256:test"
    handoff = write_inputs(tmp_path, plan)
    handoff["finalist_policy"] = copy.deepcopy(plan["finalist_policy"])
    contract = build_mod.build(handoff, tmp_path)
    assert contract["contract_version"] == 4
    assert contract["finalist_policy"] == plan["finalist_policy"]


def test_build_rejects_handoff_policy_drift_from_evaluation_plan(tmp_path):
    plan = evaluation_plan_template()
    plan["target_identity"] = "sha256:test"
    handoff = write_inputs(tmp_path, plan)
    handoff["finalist_policy"] = {
        "minimum_evaluation_level": "L2-focused",
        "holdout_policy": "not-required",
    }
    try:
        build_mod.build(handoff, tmp_path)
    except ValueError as exc:
        assert "finalist policy mismatch" in str(exc)
    else:
        assert False, "expected finalist policy mismatch"
