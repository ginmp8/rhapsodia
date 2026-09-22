from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from inspect_skill_package import scenario_coverage_type  # noqa: E402


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
