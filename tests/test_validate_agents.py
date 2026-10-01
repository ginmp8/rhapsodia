#!/usr/bin/env python3
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_agents.py"


def run_validator(target):
    proc = subprocess.run(
        [sys.executable, str(VALIDATOR), "--target", str(target)],
        text=True,
        capture_output=True,
        check=False,
    )
    try:
        doc = json.loads(proc.stdout)
    except Exception as exc:
        raise AssertionError(f"validator did not emit JSON: {exc}\nstdout={proc.stdout}\nstderr={proc.stderr}")
    return proc.returncode, doc


class ValidatorTests(unittest.TestCase):
    def copy_package(self):
        td = tempfile.TemporaryDirectory()
        dst = Path(td.name) / "pkg"
        shutil.copytree(ROOT, dst)
        return td, dst

    def assert_code(self, doc, code):
        self.assertIn(code, {f["code"] for f in doc["findings"]})

    def test_clean_package_passes(self):
        rc, doc = run_validator(ROOT)
        self.assertEqual(rc, 0, doc)
        self.assertEqual(doc["status"], "pass")

    def test_supervisor_write_tool_is_rejected(self):
        td, dst = self.copy_package()
        try:
            p = dst / "agents" / "rhapsodia-supervisor.agent.md"
            text = p.read_text(encoding="utf-8").replace(
                'tools: ["read", "search", "agent"]',
                'tools: ["read", "search", "edit", "agent"]',
            )
            p.write_text(text, encoding="utf-8")
            rc, doc = run_validator(dst)
            self.assertNotEqual(rc, 0)
            self.assert_code(doc, "SUPERVISOR_WRITE_TOOL")
        finally:
            td.cleanup()


    def test_analyst_write_tool_is_rejected(self):
        td, dst = self.copy_package()
        try:
            p = dst / "agents" / "rhapsodia-analyst.agent.md"
            text = p.read_text(encoding="utf-8").replace(
                'tools: ["read", "search"]',
                'tools: ["read", "search", "edit"]',
            )
            p.write_text(text, encoding="utf-8")
            rc, doc = run_validator(dst)
            self.assertNotEqual(rc, 0)
            self.assert_code(doc, "ANALYST_TOOL_SCOPE")
        finally:
            td.cleanup()

    def test_verifier_agent_tool_is_rejected(self):
        td, dst = self.copy_package()
        try:
            p = dst / "agents" / "rhapsodia-verifier.agent.md"
            text = p.read_text(encoding="utf-8").replace(
                'tools: ["read", "search", "edit", "execute"]',
                'tools: ["read", "search", "edit", "execute", "agent"]',
            )
            p.write_text(text, encoding="utf-8")
            rc, doc = run_validator(dst)
            self.assertNotEqual(rc, 0)
            self.assert_code(doc, "TOOLS")
        finally:
            td.cleanup()

    def test_supervisor_allowlist_must_include_analyst(self):
        td, dst = self.copy_package()
        try:
            p = dst / "agents" / "rhapsodia-supervisor.agent.md"
            text = p.read_text(encoding="utf-8").replace(
                'agents: ["Rhapsodia Analyst", "Rhapsodia Verifier", "Nomia", "Mago", "Magia"]',
                'agents: ["Rhapsodia Analyst", "Nomia", "Mago", "Magia"]',
            )
            p.write_text(text, encoding="utf-8")
            rc, doc = run_validator(dst)
            self.assertNotEqual(rc, 0)
            self.assert_code(doc, "SUPERVISOR_ALLOWLIST")
        finally:
            td.cleanup()

    def test_write_capable_fanout_contract_is_rejected(self):
        td, dst = self.copy_package()
        try:
            p = dst / "docs" / "agents" / "contracts" / "rhapsodia-agent-system.json"
            doc = json.loads(p.read_text(encoding="utf-8"))
            doc["routing"]["adaptive_execution"]["write_capable_worker_fanout"] = True
            p.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
            rc, result = run_validator(dst)
            self.assertNotEqual(rc, 0)
            self.assert_code(result, "WRITE_FANOUT")
        finally:
            td.cleanup()

    def test_required_gate_override_contract_is_rejected(self):
        td, dst = self.copy_package()
        try:
            p = dst / "docs" / "agents" / "contracts" / "rhapsodia-agent-system.json"
            doc = json.loads(p.read_text(encoding="utf-8"))
            doc["routing"]["adaptive_execution"]["gated_convergence"]["required_gate_failure_overridable"] = True
            p.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
            rc, result = run_validator(dst)
            self.assertNotEqual(rc, 0)
            self.assert_code(result, "GATED_CONVERGENCE")
        finally:
            td.cleanup()

    def test_supporting_capability_resolution_rejects_fixed_catalog(self):
        td, dst = self.copy_package()
        try:
            p = dst / "docs" / "agents" / "contracts" / "rhapsodia-agent-system.json"
            doc = json.loads(p.read_text(encoding="utf-8"))
            doc["routing"]["supporting_capability_resolution"] = {
                "selection": "semantic-capability",
                "binding": "host-native-agent-skill-discovery",
                "fixed_skill_catalog": True,
                "authority_precedence": "active-agent-contract",
                "ownership_precedence": "canonical-lifecycle-owner",
                "required_unavailable": "blocked",
                "optional_unavailable": "continue-with-not-run",
                "supporting_skill_may_expand_authority": False,
                "supporting_skill_may_change_owner": False,
            }
            p.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
            rc, result = run_validator(dst)
            self.assertNotEqual(rc, 0)
            self.assert_code(result, "SUPPORTING_CAPABILITY_RESOLUTION")
        finally:
            td.cleanup()

    def test_required_supporting_capability_must_fail_closed(self):
        td, dst = self.copy_package()
        try:
            p = dst / "docs" / "agents" / "contracts" / "rhapsodia-agent-system.json"
            doc = json.loads(p.read_text(encoding="utf-8"))
            doc["routing"]["supporting_capability_resolution"] = {
                "selection": "semantic-capability",
                "binding": "host-native-agent-skill-discovery",
                "fixed_skill_catalog": False,
                "authority_precedence": "active-agent-contract",
                "ownership_precedence": "canonical-lifecycle-owner",
                "required_unavailable": "continue-with-not-run",
                "optional_unavailable": "continue-with-not-run",
                "supporting_skill_may_expand_authority": False,
                "supporting_skill_may_change_owner": False,
            }
            p.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
            rc, result = run_validator(dst)
            self.assertNotEqual(rc, 0)
            self.assert_code(result, "SUPPORTING_CAPABILITY_RESOLUTION")
        finally:
            td.cleanup()

    def test_worker_delegation_tool_is_rejected(self):
        td, dst = self.copy_package()
        try:
            p = dst / "agents" / "magia.agent.md"
            text = p.read_text(encoding="utf-8").replace(
                'tools: ["read", "search", "edit", "execute"]',
                'tools: ["read", "search", "edit", "execute", "agent"]',
            )
            p.write_text(text, encoding="utf-8")
            rc, doc = run_validator(dst)
            self.assertNotEqual(rc, 0)
            self.assert_code(doc, "WORKER_DELEGATION_TOOL")
        finally:
            td.cleanup()

    def test_mcp_dependency_is_rejected(self):
        td, dst = self.copy_package()
        try:
            p = dst / "agents" / "nomia.agent.md"
            text = p.read_text(encoding="utf-8").replace(
                'tools: ["read", "search", "edit", "execute"]',
                'tools: ["read", "search", "edit", "execute"]\nmcp-servers: custom-runtime',
            )
            p.write_text(text, encoding="utf-8")
            rc, doc = run_validator(dst)
            self.assertNotEqual(rc, 0)
            self.assert_code(doc, "MCP_DEPENDENCY")
        finally:
            td.cleanup()

    def test_runtime_name_in_prompt_is_allowed(self):
        td, dst = self.copy_package()
        try:
            p = dst / "agents" / "magia.agent.md"
            p.write_text(
                p.read_text(encoding="utf-8")
                + "\nAn optional host integration may use LangGraph.\n",
                encoding="utf-8",
            )
            manifest = dst / "MANIFEST.json"
            mdoc = json.loads(manifest.read_text(encoding="utf-8"))
            rel = "agents/magia.agent.md"
            record = next(item for item in mdoc["files"] if item["path"] == rel)
            data = p.read_bytes()
            record["size"] = len(data)
            record["sha256"] = hashlib.sha256(data).hexdigest()
            manifest.write_text(json.dumps(mdoc, indent=2) + "\n", encoding="utf-8")
            rc, doc = run_validator(dst)
            self.assertEqual(rc, 0, doc)
            self.assertEqual(doc["status"], "pass")
        finally:
            td.cleanup()

    def test_budget_drift_is_rejected(self):
        td, dst = self.copy_package()
        try:
            p = dst / "agents" / "rhapsodia-supervisor.agent.md"
            text = p.read_text(encoding="utf-8").replace(
                "maximum 24 total subagent delegations",
                "maximum total subagent delegations are host-defined",
            )
            p.write_text(text, encoding="utf-8")
            rc, doc = run_validator(dst)
            self.assertNotEqual(rc, 0)
            self.assert_code(doc, "SUPERVISOR_INVARIANT")
        finally:
            td.cleanup()

    def test_duplicate_scenario_id_is_rejected(self):
        td, dst = self.copy_package()
        try:
            p = dst / "tests" / "agent-scenarios.json"
            doc = json.loads(p.read_text(encoding="utf-8"))
            doc["scenarios"][1]["id"] = doc["scenarios"][0]["id"]
            p.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
            rc, result = run_validator(dst)
            self.assertNotEqual(rc, 0)
            self.assert_code(result, "SCENARIO_DUPLICATE_ID")
        finally:
            td.cleanup()

    def test_generated_bytecode_is_rejected(self):
        td, dst = self.copy_package()
        try:
            cache = dst / "tests" / "__pycache__"
            cache.mkdir(parents=True, exist_ok=True)
            (cache / "bad.pyc").write_bytes(b"generated")
            rc, result = run_validator(dst)
            self.assertNotEqual(rc, 0)
            self.assert_code(result, "PACKAGE_HYGIENE")
        finally:
            td.cleanup()

    def test_vscode_support_regression_is_rejected(self):
        td, dst = self.copy_package()
        try:
            p = dst / "docs" / "agents" / "contracts" / "rhapsodia-agent-system.json"
            doc = json.loads(p.read_text(encoding="utf-8"))
            next(h for h in doc["hosts"] if h["host"] == "vscode")["status"] = "unverified"
            p.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
            rc, result = run_validator(dst)
            self.assertNotEqual(rc, 0)
            self.assert_code(result, "VSCODE_HOST")
        finally:
            td.cleanup()

    def test_stale_manifest_is_rejected(self):
        td, dst = self.copy_package()
        try:
            manifest = dst / "MANIFEST.json"
            doc = json.loads(manifest.read_text(encoding="utf-8"))
            target = next(item for item in doc["files"] if item["path"] == "agents/magia.agent.md")
            target["sha256"] = "0" * 64
            manifest.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
            rc, result = run_validator(dst)
            self.assertNotEqual(rc, 0)
            self.assert_code(result, "MANIFEST_INTEGRITY")
        finally:
            td.cleanup()


if __name__ == "__main__":
    unittest.main()
