from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from validate_resource_integration import validate as validate_resource_integration
from validate_booster_activation_scenarios import validate as validate_booster_activation


def test_new_execution_resources_are_reachable() -> None:
    result = validate_resource_integration(ROOT)
    assert result["status"] == "pass", result["errors"]
    assert result["route_count"] >= 13


def test_resource_gate_fails_when_execution_profile_route_is_lost() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        target = Path(temp_dir) / "magia"
        shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
        skill = target / "SKILL.md"
        text = skill.read_text(encoding="utf-8")
        text = text.replace("[execution profiles](references/execution-profiles.md)", "execution profiles")
        skill.write_text(text, encoding="utf-8")
        result = validate_resource_integration(target)
        assert result["status"] == "fail"
        assert any("references/execution-profiles.md" in error for error in result["errors"]), result["errors"]


def test_booster_activation_suite_has_structural_receipt() -> None:
    result = validate_booster_activation(ROOT / "evals" / "booster-activation-scenarios.json")
    assert result["status"] == "pass", result["errors"]
    assert result["evidence_kind"] == "structural_scenario_validation"
    assert result["behavior_measured"] is False
    assert result["scenario_count"] == 28


def test_booster_activation_gate_rejects_missing_category() -> None:
    source = ROOT / "evals" / "booster-activation-scenarios.json"
    payload = json.loads(source.read_text(encoding="utf-8"))
    payload["scenarios"] = [row for row in payload["scenarios"] if row["category"] != "edge_case"]
    with tempfile.TemporaryDirectory() as temp_dir:
        candidate = Path(temp_dir) / "suite.json"
        candidate.write_text(json.dumps(payload), encoding="utf-8")
        result = validate_booster_activation(candidate)
    assert result["status"] == "fail"
    assert any("missing required categories" in error for error in result["errors"]), result["errors"]
