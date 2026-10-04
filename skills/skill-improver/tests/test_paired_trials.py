import json
from pathlib import Path

from scripts.summarize_paired_trials import summarize

ROOT = Path(__file__).resolve().parents[1]


def load_template():
    return json.loads((ROOT / "assets/templates/paired-trials.json.template").read_text())


def test_template_summary_has_three_arm_deltas():
    result = summarize(load_template(), 3)
    assert result["status"] == "pass", result
    assert result["paired_observations"] == 3
    assert result["candidate_skill_lift"] > result["parent_skill_lift"]
    assert result["candidate_vs_parent_delta"] > 0
    assert "candidate_pass@k" in result["reliability"]
    assert "candidate_pass^k" in result["reliability"]


def test_runtime_drift_fails_comparability():
    data = load_template()
    data["runtime_identity"]["candidate"] = "different-environment"
    result = summarize(data, 3)
    assert result["status"] == "fail"
    assert "runtime_identity:drift-across-arms" in result["errors"]
