#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "scripts" / "inventory_skill_package.py"
REPORT_VALIDATOR = ROOT / "scripts" / "validate_architecture_report.py"


def run_json(cmd: list[str]) -> tuple[int, dict]:
    proc = subprocess.run(cmd, text=True, capture_output=True)
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(f"command did not emit JSON: {cmd}\nstdout={proc.stdout}\nstderr={proc.stderr}") from exc
    return proc.returncode, payload


def write_fixture(root: Path) -> None:
    (root / "references").mkdir(parents=True)
    (root / "assets" / "templates").mkdir(parents=True)
    (root / "scripts").mkdir(parents=True)
    (root / "SKILL.md").write_text(
        "---\nname: fixture\ndescription: fixture package for architecture inventory tests.\n---\n\n"
        "# Fixture\n\nLoad [rule](references/rule.md) when reviewing decisions.\n"
        "Use `assets/templates/report.md.template` for durable output.\n",
        encoding="utf-8",
    )
    (root / "references" / "rule.md").write_text("# Rule\n\nEvidence first.\n", encoding="utf-8")
    (root / "assets" / "templates" / "report.md.template").write_text("{{report}}\n", encoding="utf-8")
    (root / "assets" / "unused.txt").write_text("retained but no visible consumer\n", encoding="utf-8")
    (root / "scripts" / "worker.py").write_text(
        'TEMPLATE = "assets/templates/report.md.template"\n', encoding="utf-8"
    )


def inventory(path: Path) -> dict:
    code, payload = run_json([sys.executable, str(INVENTORY), "--target", str(path)])
    assert code == 0, payload
    return payload


def test_package_identity_is_path_independent() -> None:
    with tempfile.TemporaryDirectory() as td:
        a = Path(td) / "a"
        b = Path(td) / "b"
        write_fixture(a)
        write_fixture(b)
        ia = inventory(a)
        ib = inventory(b)
        assert ia["schema_version"] == "2.1.0"
        assert ia["package_identity_sha256"] == ib["package_identity_sha256"], (
            ia.get("package_identity_sha256"), ib.get("package_identity_sha256")
        )
        assert ia["context_topology"] == ib["context_topology"]


def test_resource_and_consumer_maps_are_explicit() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "pkg"
        write_fixture(root)
        data = inventory(root)
        resources = {item["path"]: item for item in data["resource_map"]}
        rule = resources["references/rule.md"]
        assert rule["taxonomy"] == "reference"
        assert "SKILL.md" in rule["consumer_evidence"]
        template = resources["assets/templates/report.md.template"]
        assert template["taxonomy"] == "template-asset"
        assert set(template["consumer_evidence"]) == {"SKILL.md", "scripts/worker.py"}
        unused = resources["assets/unused.txt"]
        assert unused["consumer_status"] == "unresolved-no-evidence"
        assert unused["consumer_status"] != "orphaned"


def test_ownership_and_progressive_loading_maps_are_stable() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "pkg"
        write_fixture(root)
        data = inventory(root)
        ownership = {item["path"]: item["owner_role"] for item in data["ownership_map"]}
        assert ownership["SKILL.md"] == "control-plane"
        assert ownership["references/rule.md"] == "review-guidance"
        assert ownership["scripts/worker.py"] == "deterministic-mechanics"
        declared = {item["target"] for item in data["progressive_loading_map"]["skill_md_declared_resources"]}
        assert "references/rule.md" in declared
        assert "assets/templates/report.md.template" in declared


def test_context_topology_is_mechanical_not_a_decision() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "pkg"
        write_fixture(root)
        data = inventory(root)
        topology = data["context_topology"]
        assert topology["skill_md_line_count"] > 0
        assert topology["skill_md_word_count"] > 0
        assert topology["direct_declared_resource_count"] == 2
        assert topology["reference_chain_max_depth"] == 1
        assert topology["nested_reference_edge_count"] == 0
        assert topology["reachable_reference_count"] == 1
        assert topology["unreachable_reference_count"] == 0


def valid_legacy_report() -> dict:
    return {
        "schema_version": "1.0.0",
        "rubric_version": "2.0.0",
        "target": {"name": "fixture", "package_identity_sha256": "a" * 64},
        "mode": "architecture-recommendation",
        "evidence_snapshot": {"identity": "b" * 64, "source": "inventory"},
        "observations": [
            {"id": "obs-1", "kind": "mechanical", "claim": "One root SKILL.md exists.", "evidence": ["inventory:skill_md_files"]}
        ],
        "judgments": [
            {"id": "jud-1", "claim": "The package is cohesive.", "evidence_ids": ["obs-1"], "confidence": "medium"}
        ],
        "decision": {
            "choice": "no_change",
            "evidence_ids": ["obs-1", "jud-1"],
            "alternatives_considered": ["keep_unified"],
            "tie_breaker_used": "minimum-change",
        },
        "recommendations": [],
        "measured": {"commands": [], "behavioral_scenarios_executed": False},
        "residual_risks": ["Behavioral scenario execution not performed."],
    }


def valid_current_report() -> dict:
    report = valid_legacy_report()
    report.update({
        "schema_version": "2.0.0",
        "rubric_version": "3.0.0",
        "architecture_scope": "single_skill",
        "activation_evidence": {"status": "unknown", "signals": [], "catalog_scope": "not-inspected"},
        "context_topology": {
            "skill_md_line_count": 20,
            "direct_declared_resource_count": 3,
            "reference_chain_max_depth": 1,
            "nested_reference_edge_count": 0,
        },
        "quality_scenarios": [
            {"id": "qs-1", "stimulus": "add a mode", "affected_surfaces": ["routing"], "evidence_ids": ["obs-1"]}
        ],
        "sensitivity_points": [
            {"id": "sp-1", "claim": "Routing is sensitive to trigger overlap.", "evidence_ids": ["obs-1"]}
        ],
        "tradeoff_points": [
            {"id": "tp-1", "claim": "Isolation can increase composition overhead.", "evidence_ids": ["obs-1"]}
        ],
        "evolution_evidence": {"history_status": "not-inspected", "change_coupling": [], "change_radius_notes": []},
        "trust_boundary_map": {
            "status": "observed",
            "executable_resources": [],
            "network_requirements": [],
            "filesystem_write_requirements": [],
            "external_tool_requirements": [],
            "security_handoff_required": False,
        },
        "evidence_gaps": ["Adjacent catalog not inspected."],
    })
    return report


def test_report_validator_accepts_legacy_and_current_contracts() -> None:
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "report.json"
        p.write_text(json.dumps(valid_legacy_report()), encoding="utf-8")
        code, payload = run_json([sys.executable, str(REPORT_VALIDATOR), str(p)])
        assert code == 0 and payload["status"] == "pass" and payload["contract"] == "legacy", payload

        p.write_text(json.dumps(valid_current_report()), encoding="utf-8")
        code, payload = run_json([sys.executable, str(REPORT_VALIDATOR), str(p)])
        assert code == 0 and payload["status"] == "pass" and payload["contract"] == "current", payload

        broken = valid_current_report()
        del broken["target"]["package_identity_sha256"]
        p.write_text(json.dumps(broken), encoding="utf-8")
        code, payload = run_json([sys.executable, str(REPORT_VALIDATOR), str(p)])
        assert code != 0
        assert any("package_identity_sha256" in err for err in payload["errors"]), payload


def test_portability_validator_passes_current_package() -> None:
    validator_path = ROOT / "scripts" / "validate_portability.py"
    namespace: dict[str, object] = {"__name__": "portability_self_test"}
    exec(compile(validator_path.read_text(encoding="utf-8"), str(validator_path), "exec"), namespace)
    result = namespace["validate"](ROOT)
    assert result["status"] == "pass", result
    assert result["checks"]["package_identity_path_independent"] is True


def main() -> int:
    tests = [
        test_package_identity_is_path_independent,
        test_resource_and_consumer_maps_are_explicit,
        test_ownership_and_progressive_loading_maps_are_stable,
        test_context_topology_is_mechanical_not_a_decision,
        test_report_validator_accepts_legacy_and_current_contracts,
        test_portability_validator_passes_current_package,
    ]
    failures: list[str] = []
    for test in tests:
        try:
            test()
            print(f"PASS {test.__name__}")
        except Exception as exc:
            failures.append(f"FAIL {test.__name__}: {exc}")
            print(failures[-1])
    if failures:
        print(json.dumps({"status": "fail", "failures": failures}, indent=2))
        return 1
    print(json.dumps({"status": "pass", "tests": len(tests)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
