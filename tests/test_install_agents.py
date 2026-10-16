#!/usr/bin/env python3
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "scripts" / "install_agents.py"
AGENT_NAMES = {
    "rhapsodia-adhoc.agent.md",
    "rhapsodia-supervisor.agent.md",
    "rhapsodia-analyst.agent.md",
    "rhapsodia-verifier.agent.md",
    "nomia.agent.md",
    "mago.agent.md",
    "magia.agent.md",
    "rhapsodia-workspace.agent.md",
}


def run_installer(*args):
    return subprocess.run(
        [sys.executable, str(INSTALLER), *map(str, args)],
        text=True,
        capture_output=True,
        check=False,
    )


class InstallerTests(unittest.TestCase):
    def make_target_with_skills(self):
        td = tempfile.TemporaryDirectory()
        target = Path(td.name) / "repo"
        target.mkdir()
        for name in ("nomia", "mago", "magia", "test-oracle-engineering", "runtime-harness", "local-graph-engine"):
            p = target / ".github" / "skills" / name
            p.mkdir(parents=True, exist_ok=True)
            (p / "SKILL.md").write_text(f"---\\nname: {name}\\ndescription: test\\n---\\n", encoding="utf-8")
        for name, script in (("runtime-harness", "agent_session.py"), ("local-graph-engine", "workspace_memory.py")):
            helper = target / ".github/skills" / name / "scripts" / script
            helper.parent.mkdir(exist_ok=True)
            helper.write_text("# Fixture only; never executed.\n", encoding="utf-8")
        return td, target

    def test_missing_required_session_helper_blocks_install(self):
        td, target = self.make_target_with_skills()
        try:
            (target / ".github/skills/runtime-harness/scripts/agent_session.py").unlink()
            proc = run_installer("--target", target)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("agent_session.py", proc.stderr)
            self.assertFalse((target / ".github/agents").exists())
        finally:
            td.cleanup()

    def test_missing_graph_memory_helper_blocks_install(self):
        td, target = self.make_target_with_skills()
        try:
            (target / ".github/skills/local-graph-engine/scripts/workspace_memory.py").unlink()
            proc = run_installer("--target", target, "--dry-run")
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("workspace_memory.py", proc.stderr)
        finally:
            td.cleanup()

    def test_install_copies_only_agent_profiles(self):
        td, target = self.make_target_with_skills()
        try:
            proc = run_installer("--target", target)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            installed = target / ".github" / "agents"
            self.assertEqual({p.name for p in installed.glob("*.agent.md")}, AGENT_NAMES)
            self.assertFalse((target / "docs" / "agents").exists())
        finally:
            td.cleanup()

    def test_check_fails_when_required_skill_is_missing(self):
        td, target = self.make_target_with_skills()
        try:
            shutil.rmtree(target / ".github" / "skills" / "mago")
            proc = run_installer("--target", target, "--check")
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("mago", (proc.stdout + proc.stderr).lower())
        finally:
            td.cleanup()

    def test_check_passes_after_install(self):
        td, target = self.make_target_with_skills()
        try:
            install = run_installer("--target", target)
            self.assertEqual(install.returncode, 0, install.stdout + install.stderr)
            check = run_installer("--target", target, "--check")
            self.assertEqual(check.returncode, 0, check.stdout + check.stderr)
        finally:
            td.cleanup()

    def test_existing_different_agent_requires_force(self):
        td, target = self.make_target_with_skills()
        try:
            installed = target / ".github" / "agents"
            installed.mkdir(parents=True, exist_ok=True)
            (installed / "mago.agent.md").write_text("different", encoding="utf-8")
            proc = run_installer("--target", target)
            self.assertNotEqual(proc.returncode, 0)
            force = run_installer("--target", target, "--force")
            self.assertEqual(force.returncode, 0, force.stdout + force.stderr)
        finally:
            td.cleanup()

    def test_dry_run_does_not_mutate_target(self):
        td, target = self.make_target_with_skills()
        try:
            proc = run_installer("--target", target, "--dry-run")
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertFalse((target / ".github" / "agents").exists())
        finally:
            td.cleanup()


if __name__ == "__main__":
    unittest.main()
