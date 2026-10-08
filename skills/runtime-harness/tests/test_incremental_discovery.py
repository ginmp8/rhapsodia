"""Incremental/lazy discovery and cross-agent knowledge sharing contracts."""
from __future__ import annotations
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest

SKILL = Path(__file__).resolve().parents[1]
CLI = SKILL / "scripts" / "runtime.py"


class IncrementalDiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="rhapsodia incremental ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "workspace"
        self.root.mkdir()
        self.skills = Path(self.temp.name) / "skills"
        (self.skills / "alpha").mkdir(parents=True)
        (self.skills / "alpha/SKILL.md").write_text("# alpha\n", encoding="utf-8")
        self.bin = Path(self.temp.name) / "bin"
        self.bin.mkdir()
        self.base_env = dict(os.environ)

    def call(self, *args, env=None, data=None, expected=0):
        proc = subprocess.run(
            [sys.executable, "-I", "-S", "-B", str(CLI), "--workspace", str(self.root), *map(str, args)],
            input=None if data is None else json.dumps(data),
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=20,
            env=env or self.base_env,
        )
        self.assertEqual(proc.returncode, expected, proc.stdout + proc.stderr)
        self.assertNotIn("Traceback", proc.stderr)
        return json.loads(proc.stdout)

    def init(self, env=None):
        return self.call("init", "--skills-root", self.skills, env=env)

    def fake_tool(self, name: str) -> Path:
        if os.name == "nt":
            path = self.bin / (name + ".cmd")
            path.write_text("@echo off\r\n", encoding="utf-8")
        else:
            path = self.bin / name
            path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            path.chmod(path.stat().st_mode | stat.S_IXUSR)
        return path

    def env_with_bin(self):
        env = dict(self.base_env)
        env["PATH"] = str(self.bin) + os.pathsep + env.get("PATH", "")
        return env

    def snapshot(self):
        pointer = json.loads((self.root / ".rhapsodia/runtime/current.json").read_text(encoding="utf-8"))
        return pointer, json.loads((self.root / ".rhapsodia/runtime" / pointer["snapshot_file"]).read_text(encoding="utf-8"))

    def test_bootstrap_discovers_only_running_python(self):
        self.init(env=self.env_with_bin())
        _, snapshot = self.snapshot()
        self.assertEqual(set(snapshot["tools"]), {"python"})

    def test_path_change_does_not_invalidate_existing_snapshot(self):
        self.init()
        env = dict(self.base_env)
        env["PATH"] = str(self.bin) + os.pathsep + env.get("PATH", "")
        result = self.call("status", env=env)
        self.assertEqual(result["status"], "ok")

    def test_ensure_discovers_arbitrary_tool_and_publishes_for_next_agent(self):
        tool = self.fake_tool("docker")
        env = self.env_with_bin()
        first = self.init(env=env)
        ensured = self.call("ensure", "tool://docker", env=env)
        self.assertNotEqual(first["snapshot_id"], ensured["snapshot_id"])
        self.assertEqual(ensured["records"][0]["status"], "available")
        self.assertEqual(Path(ensured["records"][0]["argv"][0]), tool)
        # A separate process/agent reads the published observation without rediscovery.
        reused = self.call("resolve", "tool://docker", env=self.base_env)
        self.assertEqual(reused["records"][0]["status"], "available")
        self.assertEqual(Path(reused["records"][0]["argv"][0]), tool)
        self.assertEqual(reused["snapshot_id"], ensured["snapshot_id"])

    def test_agent_can_publish_explicit_tool_location_outside_path(self):
        tool = self.fake_tool("custom-tool")
        self.init(env=self.base_env)
        observed = self.call("observe-tool", "tool://custom-tool", "--path", tool, env=self.base_env)
        self.assertEqual(observed["records"][0]["status"], "available")
        reused = self.call("resolve", "tool://custom-tool", env=self.base_env)
        self.assertEqual(Path(reused["records"][0]["argv"][0]), tool)

    def test_missing_tool_is_negative_cached_until_search_space_changes(self):
        self.init(env=self.base_env)
        first = self.call("ensure", "tool://never-there", env=self.base_env)
        self.assertEqual(first["records"][0]["status"], "missing")
        first_id = first["snapshot_id"]
        second = self.call("ensure", "tool://never-there", env=self.base_env)
        self.assertEqual(second["snapshot_id"], first_id)
        self.fake_tool("never-there")
        changed = self.call("ensure", "tool://never-there", env=self.env_with_bin())
        self.assertEqual(changed["records"][0]["status"], "available")
        self.assertNotEqual(changed["snapshot_id"], first_id)

    def test_agent_can_publish_verified_resource_for_other_agents(self):
        self.init()
        validator = self.root / "tools" / "validate.py"
        validator.parent.mkdir()
        validator.write_text("print('ok')\n", encoding="utf-8")
        observed = self.call(
            "observe-resource", "resource://build/validator", "--path", validator
        )
        self.assertEqual(observed["status"], "stored")
        resolved = self.call("resolve", "resource://build/validator")
        record = resolved["records"][0]
        self.assertEqual(record["status"], "available")
        self.assertTrue(Path(record["path"]).samefile(validator))
        self.assertEqual(record["kind"], "resource")

    def test_resource_observations_merge_instead_of_overwriting_each_other(self):
        self.init()
        one = self.root / "one.txt"
        two = self.root / "two.txt"
        one.write_text("one", encoding="utf-8")
        two.write_text("two", encoding="utf-8")
        self.call("observe-resource", "resource://shared/one", "--path", one)
        first_pointer, _ = self.snapshot()
        self.call("observe-resource", "resource://shared/two", "--path", two)
        second_pointer, snapshot = self.snapshot()
        self.assertNotEqual(first_pointer["snapshot_id"], second_pointer["snapshot_id"])
        self.assertEqual(set(snapshot["resources"]), {"shared/one", "shared/two"})
        resolved = self.call("resolve", "resource://shared/one", "resource://shared/two")
        self.assertTrue(all(r["status"] == "available" for r in resolved["records"]))

    def test_resource_observation_accepts_alias_to_the_approved_workspace_root(self):
        # Reproduces a lexical root mismatch (like Windows RUNNER~1 vs runneradmin).
        # The alias refers to the approved root; descendant symlinks remain forbidden.
        self.init()
        file = self.root / "verified.txt"
        file.write_text("verified", encoding="utf-8")
        alias = Path(self.temp.name) / "workspace-alias"
        try:
            alias.symlink_to(self.root, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("workspace aliases unavailable on this host")
        observed = self.call("observe-resource", "resource://shared/alias", "--path", alias / file.name)
        self.assertEqual(observed["status"], "stored")
        record = self.call("resolve", "resource://shared/alias")["records"][0]
        self.assertEqual(record["status"], "available")
        self.assertTrue(Path(record["path"]).samefile(file))

    def test_resource_observation_rejects_descendant_symlink_inside_workspace(self):
        self.init()
        actual = self.root / "real"
        actual.mkdir()
        (actual / "verified.txt").write_text("verified", encoding="utf-8")
        link = self.root / "linked"
        try:
            link.symlink_to(actual, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable on this host")
        rejected = self.call("observe-resource", "resource://shared/alias", "--path", link / "verified.txt", expected=2)
        self.assertEqual(rejected["error"]["code"], "UNSAFE_PATH")

    def test_resource_observation_is_confined_to_approved_roots(self):
        self.init()
        outside = Path(self.temp.name) / "outside.txt"
        outside.write_text("outside", encoding="utf-8")
        body = self.call("observe-resource", "resource://unsafe/outside", "--path", outside, expected=2)
        self.assertEqual(body["error"]["code"], "UNSAFE_PATH")

    def test_handoff_can_pin_shared_resource_and_detect_later_change(self):
        self.init()
        path = self.root / "validator.py"
        path.write_text("print('v1')\n", encoding="utf-8")
        self.call("observe-resource", "resource://validation/main", "--path", path)
        created = self.call("handoff-create", data={
            "task_id": "task-1",
            "next_action": "validate",
            "refs": ["resource://validation/main", "tool://python"],
        })
        ready = self.call("handoff-resume", "--id", created["handoff_id"])
        self.assertEqual(ready["status"], "ready")
        path.write_text("print('v2')\n", encoding="utf-8")
        stale = self.call("handoff-resume", "--id", created["handoff_id"], expected=3)
        self.assertEqual(stale["error"]["code"], "STALE_HANDOFF")


if __name__ == "__main__":
    unittest.main()
