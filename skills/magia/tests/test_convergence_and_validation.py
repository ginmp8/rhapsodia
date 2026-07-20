from __future__ import annotations

import json
from pathlib import Path

from scripts.select_validation_profile import select_profile
from scripts.validate_convergence import validate_convergence
from scripts.validate_execution_scenarios import validate_suite

ROOT = Path(__file__).resolve().parents[1]


def test_quick_profile_for_localized_low_risk_docs():
    result = select_profile({"file_types": [".md"], "components": ["docs"], "signals": {}})
    assert result["profile"] == "quick"
    assert result["required_checks"] == ["targeted_tests"]


def test_governed_profile_selects_security_migration_and_contract_checks():
    result = select_profile({
        "file_types": [".cs", ".sql"], "components": ["api", "database"],
        "signals": {"authorization": True, "migration": True, "public_contract": True, "interruptible": True},
    })
    assert result["profile"] == "governed"
    assert {"security_checks", "migration_validation", "contract_tests", "full_relevant_test_suite"} <= set(result["required_checks"])
    assert result["run_state_required"] is True


def test_convergence_links_every_modified_file_and_blocks_unverified():
    payload = {
        "schema_version": 1, "scope_type": "planned", "modified_files": ["src/a.py"],
        "items": [{
            "id": "REQ-1", "requirement": "Parse valid input", "acceptance_criteria": ["valid input returns value"],
            "tasks": ["task001"], "changed_files": ["src/a.py"], "checks": ["pytest tests/test_a.py"],
            "evidence": ["pytest passed"], "status": "satisfied", "reason": None, "handoff": "none"
        }],
    }
    errors, summary = validate_convergence(payload)
    assert errors == []
    assert summary["completion_allowed"] is True
    payload["items"][0]["status"] = "unverified"
    payload["items"][0]["reason"] = "integration environment unavailable"
    errors, summary = validate_convergence(payload)
    assert errors == []
    assert summary["completion_allowed"] is False


def test_planning_change_requires_mago_handoff():
    payload = {
        "schema_version": 1, "scope_type": "adhoc", "modified_files": [],
        "items": [{
            "id": "GAP-1", "requirement": "Existing intent", "acceptance_criteria": [], "tasks": [],
            "changed_files": [], "checks": [], "evidence": [], "status": "planning_change_required",
            "reason": "public contract must change", "handoff": "none"
        }],
    }
    errors, _ = validate_convergence(payload)
    assert "item GAP-1 planning change requires Mago handoff" in errors


def test_frozen_execution_scenarios_cover_required_architecture():
    payload = json.loads((ROOT / "evals/execution-scenarios.json").read_text(encoding="utf-8"))
    assert validate_suite(payload) == []
