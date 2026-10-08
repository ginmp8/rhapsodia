"""Public CLI regressions: portable fixtures, no installed service or dependencies."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SKILL = Path(__file__).resolve().parents[1]
CLI = SKILL / "scripts" / "runtime.py"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="rhapsodia runtime ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "workspace"
        self.root.mkdir()
        self.skills = Path(self.temp.name) / "installed skills"
        for name in ("alpha", "beta"):
            p = self.skills / name
            (p / "scripts").mkdir(parents=True)
            (p / "SKILL.md").write_text(f"---\nname: {name}\ndescription: Example.\n---\n# {name}\n", encoding="utf-8")
            (p / "scripts" / "check.py").write_text("raise RuntimeError('indexing must never execute this')\n", encoding="utf-8")
        (self.root / "task.txt").write_text("review this exact content\n", encoding="utf-8")

    def command(self, *args, data=None, env=None, expected=0, root=None):
        proc = subprocess.run([sys.executable, "-S", "-B", str(CLI), "--workspace", str(root or self.root), *map(str, args)],
                              input=None if data is None else json.dumps(data), capture_output=True, text=True,
                              encoding="utf-8", timeout=15, env=env)
        if expected is not None:
            self.assertEqual(proc.returncode, expected, proc.stdout + proc.stderr)
        self.assertNotIn("Traceback", proc.stderr)
        try:
            return json.loads(proc.stdout)
        except json.JSONDecodeError:
            self.fail("CLI must return one JSON value: " + proc.stdout + proc.stderr)

    def init(self, *args, **kwargs):
        return self.command("init", "--skills-root", self.skills, *args, **kwargs)

    def query(self, request, **kwargs):
        return self.command("query", data=request, **kwargs)

    def receipt(self, **extra):
        req = {"task_id": "task-1", "next_action": "review-candidate", "refs": ["repo://task.txt", "skill://alpha", "tool://python"]}
        req.update(extra)
        return self.command("handoff-create", data=req)

    def test_init_returns_bounded_bootstrap(self):
        result = self.init()
        self.assertEqual(result["status"], "ready")
        self.assertFalse(result["cache_hit"])
        self.assertLess(len(json.dumps(result).encode()), 2048)
        current = json.loads((self.root / ".rhapsodia/runtime/current.json").read_text())
        self.assertEqual(current["python_argv"], [sys.executable])
        self.assertEqual(current["snapshot_id"], result["snapshot_id"])

    def test_warm_init_has_stable_identity_and_no_discovery(self):
        a, b = self.init(), self.init()
        self.assertEqual(a["snapshot_id"], b["snapshot_id"])
        self.assertTrue(b["cache_hit"])
        self.assertFalse(b["discovery_performed"])

    def test_refresh_is_explicit(self):
        self.init()
        result = self.init("--refresh")
        self.assertFalse(result["cache_hit"])
        self.assertTrue(result["discovery_performed"])

    def test_resolve_python_uses_active_interpreter(self):
        self.init()
        r = self.query({"operation": "resolve", "refs": ["tool://python"]})
        self.assertEqual(r["records"][0]["argv"], [sys.executable])
        self.assertEqual(r["records"][0]["status"], "available")

    def test_resolve_skill_and_script_without_execution(self):
        self.init()
        r = self.query({"operation": "resolve", "refs": ["skill://alpha", "skill://alpha/scripts/check.py"]})
        self.assertEqual(len(r["records"]), 2)
        self.assertEqual(r["records"][1]["sha256"], digest(self.skills / "alpha/scripts/check.py"))
        self.assertEqual(r["records"][1]["path"], str(self.skills / "alpha/scripts/check.py"))

    def test_unknown_skill_does_not_trigger_discovery(self):
        self.init()
        r = self.query({"operation": "resolve", "refs": ["skill://not-installed"]})
        self.assertEqual(r["status"], "partial")
        self.assertEqual(r["records"][0]["status"], "missing")

    def test_context_does_not_dump_catalog(self):
        self.init()
        r = self.query({"operation": "context", "refs": ["skill://alpha"], "budget_bytes": 2048})
        self.assertEqual([v["uri"] for v in r["records"]], ["skill://alpha"])
        self.assertNotIn("beta", json.dumps(r))
        self.assertLessEqual(len((json.dumps(r, separators=(",", ":"), ensure_ascii=False, sort_keys=True) + "\n").encode()), 2048)

    def test_context_budget_fails_without_silent_truncation(self):
        self.init()
        r = self.query({"operation": "context", "refs": ["skill://alpha/scripts/check.py", "skill://beta/scripts/check.py"], "budget_bytes": 256}, expected=2)
        self.assertEqual(r["error"]["code"], "BUDGET_EXCEEDED")

    def test_etag_reuse_requires_caller_retained_context(self):
        self.init()
        req = {"operation": "context", "refs": ["repo://task.txt"]}
        a = self.query(req)
        b = self.query({**req, "if_none_match": a["etag"]})
        self.assertEqual(b["status"], "not_modified")
        self.assertNotIn("records", b)

    def test_changed_file_invalidates_context_etag(self):
        self.init()
        req = {"operation": "context", "refs": ["repo://task.txt"]}
        a = self.query(req)
        (self.root / "task.txt").write_text("changed", encoding="utf-8")
        b = self.query({**req, "if_none_match": a["etag"]})
        self.assertNotEqual(a["etag"], b["etag"])
        self.assertEqual(b["status"], "ok")

    def test_query_rejects_unknown_fields(self):
        self.init()
        r = self.query({"operation": "status", "shell": "whoami"}, expected=2)
        self.assertEqual(r["error"]["code"], "INVALID_INPUT")

    def test_query_rejects_unknown_operation(self):
        self.init()
        r = self.query({"operation": "execute"}, expected=2)
        self.assertEqual(r["error"]["code"], "INVALID_INPUT")

    def test_query_missing_state_has_actionable_error(self):
        r = self.query({"operation": "status"}, expected=3)
        self.assertEqual(r["error"]["code"], "NOT_INITIALIZED")

    def test_path_changes_do_not_invalidate_stable_runtime_scope(self):
        self.init()
        env = dict(os.environ, PATH=os.environ.get("PATH", "") + os.pathsep + "/different-path")
        r = self.query({"operation": "status"}, env=env)
        self.assertEqual(r["status"], "ok")

    def test_duplicate_skill_ids_leave_last_good_snapshot(self):
        self.init()
        pointer = self.root / ".rhapsodia/runtime/current.json"
        before = pointer.read_bytes()
        another = Path(self.temp.name) / "duplicate"
        (another / "alpha").mkdir(parents=True)
        shutil.copy2(self.skills / "alpha/SKILL.md", another / "alpha/SKILL.md")
        r = self.init("--skills-root", another, expected=4)
        self.assertEqual(r["error"]["code"], "DUPLICATE_ID")
        self.assertEqual(before, pointer.read_bytes())

    def test_corrupt_snapshot_is_never_trusted(self):
        self.init()
        current = json.loads((self.root / ".rhapsodia/runtime/current.json").read_text())
        p = self.root / ".rhapsodia/runtime" / current["snapshot_file"]
        data = json.loads(p.read_text())
        data["workspace"] = "/somewhere/else"
        p.write_text(json.dumps(data), encoding="utf-8")
        r = self.query({"operation": "status"}, expected=3)
        self.assertEqual(r["error"]["code"], "CORRUPT_STATE")

    def test_writer_lock_is_not_stolen(self):
        self.init()
        lock = self.root / ".rhapsodia/runtime/.writer.lock"
        lock.write_text('{"pid":0,"nonce":"owned elsewhere"}', encoding="utf-8")
        r = self.init("--refresh", expected=5)
        self.assertEqual(r["error"]["code"], "BUSY")
        self.assertTrue(lock.exists())

    def test_traversal_and_nonlocal_uri_are_rejected(self):
        self.init()
        for uri in ("repo://../outside", "repo:///etc/passwd", "repo://a/../b", "repo://.git/config", "repo://.env", "skill://alpha/../../beta/SKILL.md", "https://example.com/a", "repo://C:/secret", "repo://a\\b", "repo://%2e%2e/file"):
            with self.subTest(uri=uri):
                r = self.query({"operation": "resolve", "refs": [uri]}, expected=2)
                self.assertEqual(r["error"]["code"], "UNSAFE_PATH")

    def test_unicode_and_spaces_are_supported(self):
        self.init()
        p = self.root / "informa\u00e7\u00e3o com espa\u00e7o.txt"
        p.write_text("Ol\u00e1", encoding="utf-8")
        r = self.query({"operation": "resolve", "refs": ["repo://" + p.name]})
        self.assertEqual(r["records"][0]["sha256"], digest(p))

    def test_symlink_escape_is_rejected(self):
        outside = Path(self.temp.name) / "outside.txt"
        outside.write_text("private", encoding="utf-8")
        try:
            (self.root / "link.txt").symlink_to(outside)
        except (OSError, NotImplementedError):
            self.skipTest("host does not permit symlink creation")
        self.init()
        self.query({"operation": "resolve", "refs": ["repo://link.txt"]}, expected=2)

    def test_state_symlink_is_rejected(self):
        outside = Path(self.temp.name) / "foreign-state"
        outside.mkdir()
        (self.root / ".rhapsodia").mkdir()
        try:
            (self.root / ".rhapsodia/runtime").symlink_to(outside, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("host does not permit symlink creation")
        self.init(expected=2)
        self.assertEqual(list(outside.iterdir()), [])

    def test_raw_secrets_are_not_collected(self):
        env = dict(os.environ, SECRET_TEST_TOKEN="unshareable-fixture-value")
        self.init(env=env)
        for f in (self.root / ".rhapsodia/runtime").rglob("*.json"):
            self.assertNotIn("unshareable-fixture-value", f.read_text())
            self.assertNotIn("SECRET_TEST_TOKEN", f.read_text())

    def test_handoff_is_content_addressed_and_idempotent(self):
        self.init()
        a, b = self.receipt(), self.receipt()
        self.assertEqual(a["handoff_id"], b["handoff_id"])
        self.assertEqual(len(list((self.root / ".rhapsodia/runtime/handoffs").glob("*.json"))), 1)

    def test_handoff_resumes_only_pinned_resources(self):
        self.init()
        h = self.receipt()
        result = self.command("handoff-resume", "--id", h["handoff_id"])
        self.assertEqual(result["status"], "ready")
        self.assertEqual(result["next_action"], "review-candidate")
        self.assertEqual(len(result["records"]), 3)

    def test_handoff_detects_modified_content(self):
        self.init()
        h = self.receipt()
        (self.root / "task.txt").write_text("different", encoding="utf-8")
        r = self.command("handoff-resume", "--id", h["handoff_id"], expected=3)
        self.assertEqual(r["error"]["code"], "STALE_HANDOFF")

    def test_handoff_missing_required_resource_is_blocked(self):
        self.init()
        self.command("handoff-create", data={"task_id": "a", "next_action": "review", "refs": ["skill://absent"]}, expected=3)
        self.assertFalse(list((self.root / ".rhapsodia/runtime/handoffs").glob("*.json")))

    def test_handoff_cannot_claim_permission_or_test_success(self):
        self.init()
        for field in ("permissions", "validation_passed", "shell", "authority"):
            self.command("handoff-create", data={"task_id": "a", "next_action": "review", "refs": ["repo://task.txt"], field: True}, expected=2)

    def test_foreign_handoff_requires_explicit_rebind(self):
        self.init()
        h = self.receipt()
        hp = self.root / ".rhapsodia/runtime/handoffs" / (h["handoff_id"] + ".json")
        other = Path(self.temp.name) / "other-worktree"
        other.mkdir()
        shutil.copy2(self.root / "task.txt", other / "task.txt")
        self.init(root=other)
        r = self.command("handoff-resume", "--input", hp, root=other, expected=3)
        self.assertEqual(r["error"]["code"], "REBIND_REQUIRED")
        r = self.command("handoff-resume", "--input", hp, "--rebind", root=other)
        self.assertEqual(r["status"], "ready")
        self.assertTrue(r["rebound"])
        self.assertTrue(any(v.get("path") == str(other / "task.txt") for v in r["records"]))

    def test_graph_export_is_data_only_and_has_evidence(self):
        self.init()
        r = self.command("export-graph")
        self.assertEqual(r["schema_version"], "graph-patch-v1")
        self.assertGreaterEqual(len(r["nodes"]), 3)
        self.assertTrue(all(n["evidence"] for n in r["nodes"]))
        self.assertTrue(all(e["evidence"] for e in r["edges"]))
        self.assertNotIn(str(self.temp.name), json.dumps(r))
        self.assertNotIn("requires", {e["relation"] for e in r["edges"]})

    def test_configure_preserves_existing_host_instructions(self):
        self.init()
        p = self.root / "AGENTS.md"
        p.write_text("# Existing policy\nNever expand authority.\n", encoding="utf-8")
        self.command("configure", "--host", "generic")
        first = p.read_bytes()
        self.assertTrue(first.startswith(b"# Existing policy\nNever expand authority.\n"))
        self.assertIn(b".rhapsodia/runtime/current.json", first)
        self.command("configure", "--host", "generic")
        self.assertEqual(first, p.read_bytes())

    def test_configure_all_hosts_is_opt_in_and_idempotent(self):
        self.init()
        self.assertFalse((self.root / "AGENTS.md").exists())
        paths = {"copilot": ".github/copilot-instructions.md", "cursor": ".cursor/rules/rhapsodia-runtime.mdc", "claude": "CLAUDE.md", "codex": "AGENTS.md"}
        for host, rel in paths.items():
            self.command("configure", "--host", host)
            p = self.root / rel
            self.assertTrue(p.exists())
            first = p.read_bytes()
            self.command("configure", "--host", host)
            self.assertEqual(first, p.read_bytes())

    def test_configure_rejects_modified_managed_block(self):
        self.init()
        self.command("configure", "--host", "generic")
        p = self.root / "AGENTS.md"
        p.write_text(p.read_text().replace("Do not", "Never ever"), encoding="utf-8")
        r = self.command("configure", "--host", "generic", expected=4)
        self.assertEqual(r["error"]["code"], "CONFLICT")

    def test_benchmark_reports_bytes_not_billed_tokens(self):
        self.init()
        r = self.command("benchmark", "--iterations", "3")
        self.assertEqual(r["iterations"], 3)
        self.assertIn("warm_init_ms", r)
        self.assertIn("context_bytes", r)
        self.assertIsNone(r["billed_tokens"])
        self.assertEqual(r["scope"], "local-mechanics-not-agent-benchmark")


if __name__ == "__main__":
    unittest.main()
