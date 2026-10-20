"""Repository integration contracts for installed expertise discovery, not host model benchmarks."""
from __future__ import annotations
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENT_DIR = ROOT / "agents"
CONTRACT = ROOT / "docs/agents/contracts/rhapsodia-agent-system.json"


def get_validator():
    spec = importlib.util.spec_from_file_location("rhapsodia_agents_validator", ROOT / "scripts/validate_agents.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CapabilityRoutingIntegration(unittest.TestCase):
    def test_all_eight_agents_keep_first_100_line_rule_and_allowlist(self):
        for agent in AGENT_DIR.glob("*.agent.md"):
            with self.subTest(agent=agent.name):
                content = "\n".join(agent.read_text(encoding="utf-8").splitlines()[:100]).lower()
                for marker in ("mandatory session and memory", "graph-first", "capability-discovery",
                               "partial/no local match", "host-native discovery"):
                    self.assertIn(marker, content)
                self.assertNotIn("docs/agents/capability-discovery.md", content)
        supervisor = (AGENT_DIR / "rhapsodia-supervisor.agent.md").read_text(encoding="utf-8")
        self.assertIn('agents: ["Rhapsodia Analyst", "Rhapsodia Verifier", "Nomia", "Mago", "Magia", "Rhapsodia Workspace"]', supervisor)
        adhoc = (AGENT_DIR / "rhapsodia-adhoc.agent.md").read_text(encoding="utf-8")
        self.assertIn('tools: ["read", "search", "edit", "execute"]', adhoc)

    def test_contract_is_authority_neutral_and_installable(self):
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        self.assertEqual(len(contract["agents"]), 8)
        routing = contract["routing"]["supporting_capability_resolution"]
        self.assertIs(routing["fixed_skill_catalog"], False)
        discovery = routing["discovery_skill"]
        self.assertEqual(discovery["name"], "capability-discovery")
        self.assertIs(discovery["required"], False)
        self.assertIs(discovery["host_native_discovery_first"], True)
        self.assertIs(discovery["docs_runtime_required"], False)
        self.assertIs(discovery["new_agent_delegation"], False)
        self.assertIs(discovery["canonical_owner_may_change"], False)
        self.assertIs(discovery["authority_may_expand"], False)

    def test_contract_rejects_weakened_discovery_rules(self):
        validator = get_validator()
        original = json.loads(CONTRACT.read_text(encoding="utf-8"))
        import tempfile
        for key, invalid in (("docs_runtime_required", True), ("new_agent_delegation", True),
                             ("canonical_owner_may_change", True), ("host_native_discovery_first", False),
                             ("partial_or_unmatched_means", "unavailable")):
            with self.subTest(field=key), tempfile.TemporaryDirectory() as tmp:
                tampered = json.loads(json.dumps(original))
                tampered["routing"]["supporting_capability_resolution"]["discovery_skill"][key] = invalid
                p = Path(tmp) / "contract.json"
                p.write_text(json.dumps(tampered), encoding="utf-8")
                findings = []
                validator.validate_contract(p, findings)
                self.assertIn("CAPABILITY_DISCOVERY", {finding["code"] for finding in findings})

    def test_all_existing_skill_release_identity_preserved(self):
        self.assertEqual((ROOT / "skills/capability-discovery/VERSION").read_text().strip(), "0.1.0")
        self.assertIn("## [0.1.0]", (ROOT / "skills/capability-discovery/CHANGELOG.md").read_text())
        self.assertEqual((ROOT / "skills/skill-benchmark/VERSION").read_text().strip(), "0.3.0")
        self.assertTrue((ROOT / "skills/skill-benchmark/scripts/validate_metamorphic_evidence.py").exists())
        self.assertTrue((ROOT / "skills/reproducibility-engineer/references/metamorphic-variance.md").exists())
        self.assertTrue((ROOT / "skills/skill-prompt-and-activation-review/references/metamorphic-activation-review.md").exists())

    def test_installer_wires_local_discovery_tool_inside_skill(self):
        text = (ROOT / "scripts/install_agents.py").read_text(encoding="utf-8")
        self.assertIn('DISCOVERY_SKILL = "capability-discovery"', text)
        self.assertIn('"--agents-only"', text)
        self.assertIn('"scripts/capability_directory.py"', text)
        self.assertFalse((ROOT / "docs/agents/CAPABILITY-DISCOVERY.md").exists())
        self.assertFalse((ROOT / "scripts/capability_directory.py").exists())

    def test_directly_executes_self_contained_skill_cli(self):
        script = ROOT / "skills/capability-discovery/scripts/capability_directory.py"
        result = subprocess.run([sys.executable, "-I", "-S", "-B", str(script),
                                 "find", "technical plan", "--root", str(ROOT), "--limit", "6"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["scope"], "bounded-local-roots-not-host-inventory")
        self.assertGreaterEqual(payload["returned"], 1)
        self.assertTrue(all("sha256" in entry for entry in payload["matches"]))


if __name__ == "__main__":
    unittest.main()
