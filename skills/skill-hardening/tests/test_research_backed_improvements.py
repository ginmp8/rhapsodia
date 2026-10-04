from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import hardening_audit  # noqa: E402
import package_skill  # noqa: E402
import reproducibility_controls  # noqa: E402
import validate_hardened_skill  # noqa: E402


def load_required_module(name: str, path: Path):
    if not path.exists():
        raise AssertionError(f"required module is missing: {path.name}")
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_skill(root: Path, *, name: str | None = None, frontmatter_extra: str = "", body: str = "") -> None:
    skill_name = name or root.name
    text = (
        "---\n"
        f"name: {skill_name}\n"
        "description: Review API contracts and package evidence when a skill needs hardening.\n"
        f"{frontmatter_extra}"
        "---\n\n"
        "# Demo\n\n"
        "## Output contract\nReturn validation evidence.\n\n"
        "## Validation\nValidate the package before completion.\n\n"
        "## Stop conditions\nStop on missing required evidence.\n\n"
        + body
    )
    (root / "SKILL.md").write_text(text, encoding="utf-8")


class ResearchBackedHardeningTests(unittest.TestCase):
    def test_frontmatter_accepts_optional_core_fields_and_mixed_case_description(self) -> None:
        text = """---
name: demo-skill
description: Review ASP.NET Core APIs and PostgreSQL migrations when requested.
license: Apache-2.0
compatibility: Requires Python 3.10+ for optional deterministic helpers.
metadata:
  owner: platform
  version: \"1\"
allowed-tools: Bash(python3:*)
---
# Demo
"""
        errors = package_skill.validate_frontmatter(text, root_name="demo-skill", profile="portable")
        self.assertEqual([], errors)

    def test_frontmatter_rejects_invalid_name_description_metadata_and_root_mismatch(self) -> None:
        invalid_name = "---\nname: Demo_Skill\ndescription: Valid description.\n---\n"
        self.assertTrue(package_skill.validate_frontmatter(invalid_name, root_name="Demo_Skill", profile="portable"))

        overlong = "---\nname: demo-skill\ndescription: " + ("x" * 1025) + "\n---\n"
        self.assertTrue(package_skill.validate_frontmatter(overlong, root_name="demo-skill", profile="portable"))

        bad_metadata = "---\nname: demo-skill\ndescription: Valid description.\nmetadata: not-a-map\n---\n"
        self.assertTrue(package_skill.validate_frontmatter(bad_metadata, root_name="demo-skill", profile="portable"))

        mismatch = "---\nname: demo-skill\ndescription: Valid description.\n---\n"
        self.assertTrue(package_skill.validate_frontmatter(mismatch, root_name="other-root", profile="portable"))

    def test_optional_resource_layers_are_not_universal_readiness_gates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "demo-skill"
            root.mkdir()
            write_skill(root)
            result = validate_hardened_skill.run_validation(root, min_score=0)
            gate_names = {gate["name"] for gate in result["gates"]}
            self.assertNotIn("resource_layer_present", gate_names)
            self.assertNotIn("script_or_validation_present", gate_names)
            self.assertNotIn("package_builder_present", gate_names)
            self.assertEqual("pass", result["status"])
            audit = hardening_audit.audit_target(root)
            self.assertGreaterEqual(audit["scores"]["resource_integration"], 20)

    def test_scenarios_support_coexistence_and_semantic_collision_without_universal_count_20(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "demo-skill"
            (root / "evals").mkdir(parents=True)
            write_skill(root)
            scenarios = []
            for sid, stype in [
                ("A1", "should_activate"),
                ("N1", "should_not_activate"),
                ("M1", "ambiguous"),
                ("E1", "edge_case"),
                ("C1", "coexistence"),
                ("S1", "semantic_collision"),
            ]:
                scenarios.append({
                    "id": sid,
                    "type": stype,
                    "prompt": f"prompt-{sid}",
                    "expected_behavior": "bounded behavior",
                    "acceptance_criteria": ["criterion"],
                })
            (root / "evals" / "activation-scenarios.json").write_text(
                json.dumps({"scenarios": scenarios}), encoding="utf-8"
            )
            summary = validate_hardened_skill.scenario_summary(root)
            self.assertFalse(summary["errors"])
            self.assertEqual([], summary["missing_required_types"])
            result = validate_hardened_skill.run_validation(
                root,
                min_score=0,
                require_scenarios=True,
                scenario_min_per_core_type=1,
                require_coexistence=True,
            )
            scenario_gate = next(g for g in result["gates"] if g["name"] == "scenario_coverage")
            coexistence_gate = next(g for g in result["gates"] if g["name"] == "scenario_coexistence")
            self.assertTrue(scenario_gate["passed"])
            self.assertTrue(coexistence_gate["passed"])

    def test_external_skill_intake_is_static_and_flags_execution_surfaces(self) -> None:
        trust_intake = load_required_module("trust_intake", SCRIPTS / "trust_intake.py")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "untrusted-skill"
            (root / "scripts").mkdir(parents=True)
            write_skill(root)
            marker = root / "EXECUTED"
            script = root / "scripts" / "probe.py"
            script.write_text(
                "from pathlib import Path\n"
                f"Path({str(marker)!r}).write_text('ran')\n"
                "import urllib.request\n"
                "urllib.request.urlopen('https://example.com')\n",
                encoding="utf-8",
            )
            report = trust_intake.inspect_target(root, source_class="external-untrusted-skill")
            self.assertIn(report["status"], {"review", "block"})
            self.assertFalse(marker.exists(), "static intake must never execute target-owned code")
            categories = {finding["category"] for finding in report["findings"]}
            self.assertIn("executable-surface", categories)
            self.assertIn("network-access", categories)

    def test_hardening_contract_v2_requires_host_and_conditional_evidence_profiles(self) -> None:
        contract = {
            "schema_version": 2,
            "target": {"name": "demo-skill", "path": "/tmp/demo-skill", "baseline_tree_sha256": "a" * 64},
            "ceiling": "research-analytic",
            "protected_paths": ["evals"],
            "host_profiles": ["portable-core", "openai", "codex", "claude", "copilot", "cursor"],
            "evidence_profiles": {
                "environment_provenance": {"applicable": False, "reason": "No runtime-sensitive paired comparison."},
                "stochastic_evaluation": {"applicable": False, "reason": "No stochastic reliability claim."},
                "execution_lineage": {"applicable": False, "reason": "No adaptive multi-stage replay claim."},
            },
            "variability": [{
                "id": "V1", "surface": "validation", "class": "mechanical",
                "evidence": "spec", "control": "validator", "validation": "tests"
            }],
            "evaluators": [{"id": "E1", "type": "validator", "metric": "contract", "command_or_review": "unit test"}],
            "hard_gates": ["portable-core-valid"],
            "acceptance": {"freeze_after_pass": True, "stagnation_limit": 2, "weaken_hard_gates_to_pass": False},
            "delivery": {"atomic_package_replace": True, "candidate_tree_sha256": True, "archive_sha256": True},
        }
        self.assertEqual([], reproducibility_controls.validate_contract(contract))

    def test_portability_validator_passes_all_supported_profiles(self) -> None:
        portability = load_required_module("validate_portability", SCRIPTS / "validate_portability.py")
        report = portability.validate_portability(
            ROOT,
            ["portable-core", "openai", "codex", "claude", "copilot", "cursor"],
        )
        self.assertEqual("pass", report["status"], report)
        self.assertEqual(
            {"portable-core", "openai", "codex", "claude", "copilot", "cursor"},
            {entry["profile"] for entry in report["profiles"]},
        )

    def test_package_receipt_adds_provenance_without_breaking_determinism(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            target = base / "demo-skill"
            target.mkdir()
            write_skill(target)
            out1 = base / "one.zip"
            out2 = base / "two.zip"
            baseline = "b" * 64
            first = package_skill.build_package(
                target, out1, validate=True, profile="portable", baseline_tree_sha256=baseline
            )
            second = package_skill.build_package(
                target, out2, validate=True, profile="portable", baseline_tree_sha256=baseline
            )
            self.assertEqual(first["package_sha256"], second["package_sha256"])
            self.assertEqual(baseline, first["baseline_tree_sha256"])
            self.assertEqual("portable", first["validation_profile"])
            self.assertRegex(first["builder_sha256"], r"^[0-9a-f]{64}$")
            self.assertRegex(first["candidate_tree_sha256"], r"^[0-9a-f]{64}$")


if __name__ == "__main__":
    unittest.main()
