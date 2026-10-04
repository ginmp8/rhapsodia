import json
from pathlib import Path

from scripts.validate_evaluation_plan import validate_plan

ROOT = Path(__file__).resolve().parents[1]


def load_template():
    return json.loads((ROOT / "assets/templates/evaluation-plan.json.template").read_text())


def test_template_is_valid():
    result = validate_plan(load_template())
    assert result["status"] == "pass", result


def test_behavioral_claim_requires_no_skill_arm():
    data = load_template()
    data["arms"]["no_skill"]["enabled"] = False
    result = validate_plan(data)
    assert result["status"] == "fail"
    assert any("no_skill" in e for e in result["errors"])


def test_promotion_holdout_must_be_controller_only():
    data = load_template()
    data["partitions"]["promotion_holdout"]["visibility"] = "mutator-visible"
    result = validate_plan(data)
    assert result["status"] == "fail"
    assert any("promotion_holdout" in e for e in result["errors"])
