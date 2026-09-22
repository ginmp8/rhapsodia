from __future__ import annotations

import json
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from inspect_skill_package import inspect as inspect_package, scenario_coverage_type  # noqa: E402


def test_prefers_canonical_type_over_noncanonical_category():
    item = {"type": "should_activate", "category": "activation", "group": "activation"}
    assert scenario_coverage_type(item) == "should_activate"


def test_group_only_schema_is_normalized():
    assert scenario_coverage_type({"group": "activation", "expected_route": "activate"}) == "should_activate"
    assert scenario_coverage_type({"group": "non-activation", "expected_route": "do-not-activate"}) == "should_not_activate"
    assert scenario_coverage_type({"group": "ambiguous", "expected_route": "conditional"}) == "ambiguous"
    assert scenario_coverage_type({"group": "boundary", "expected_route": "split-handoff"}) == "edge_case"


def test_adversarial_or_reject_route_counts_as_edge_coverage():
    assert scenario_coverage_type({"group": "adversarial", "expected_route": "reject-fabricated-evidence"}) == "edge_case"
    assert scenario_coverage_type({"expected_route": "reject-unsafe-input"}) == "edge_case"


def test_unknown_routing_values_are_not_silent():
    from inspect_skill_package import scenario_schema_issues

    issues = scenario_schema_issues({
        "type": "route_v3",
        "group": "activation",
        "expected_route": "activate",
    })
    assert any(issue["field"] == "type" and issue["kind"] == "unknown-value" for issue in issues)


def test_uninterpretable_future_schema_is_explicit():
    from inspect_skill_package import scenario_schema_issues

    item = {"id": "future", "prompt": "x", "routing_class": "activate-v3"}
    assert scenario_coverage_type(item) == ""
    issues = scenario_schema_issues(item)
    assert any(issue["kind"] == "uninterpretable-schema" for issue in issues)


def _make_minimal_skill(root: Path, scenarios: list[dict]) -> None:
    root.mkdir()
    (root / "SKILL.md").write_text("---\nname: demo\ndescription: demo reviewer fixture\n---\n\n## Mission\nX\n## Workflow\nX\n## Resource loading\nX\n## Output contract\nX\n## Stop conditions\nX\n", encoding="utf-8")
    (root / "evals").mkdir()
    (root / "evals" / "activation-scenarios.json").write_text(json.dumps({"scenarios": scenarios}), encoding="utf-8")


def test_inspector_reports_unknown_routing_value(tmp_path):
    root = tmp_path / "demo"
    scenarios = [
        {"id": "a", "type": "should_activate", "prompt": "a"},
        {"id": "n", "type": "should_not_activate", "prompt": "n"},
        {"id": "m", "type": "ambiguous", "prompt": "m"},
        {"id": "e", "type": "edge_case", "prompt": "e"},
        {"id": "future", "type": "route_v3", "group": "activation", "prompt": "x"},
    ]
    _make_minimal_skill(root, scenarios)
    report = inspect_package(root, "directory", "portable")
    assert any(f["code"] == "EVAL005" for f in report["findings"])


def test_inspector_reports_uninterpretable_future_schema(tmp_path):
    root = tmp_path / "demo"
    scenarios = [
        {"id": "a", "type": "should_activate", "prompt": "a"},
        {"id": "n", "type": "should_not_activate", "prompt": "n"},
        {"id": "m", "type": "ambiguous", "prompt": "m"},
        {"id": "e", "type": "edge_case", "prompt": "e"},
        {"id": "future", "routing_class": "activate-v3", "prompt": "x"},
    ]
    _make_minimal_skill(root, scenarios)
    report = inspect_package(root, "directory", "portable")
    assert any(f["code"] == "EVAL004" for f in report["findings"])
