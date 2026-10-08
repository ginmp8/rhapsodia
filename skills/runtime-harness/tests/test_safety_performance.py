"""Bounded invalidation, no-discovery hot path, and native bootstrap regressions."""
from __future__ import annotations
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL / "scripts"))
from runtime_core.common import RuntimeFault, canonical, sha
from runtime_core.environment import scope_id
from runtime_core.query import execute_query
from runtime_core.store import Store
from runtime_core.integration import configure


class SafetyPerformanceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="runtime bounded ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.skills = self.root / "skills"
        (self.skills / "one").mkdir(parents=True)
        (self.skills / "one/SKILL.md").write_text("# one\n", encoding="utf-8")
        self.store = Store(self.root)
        self.store.initialize([self.skills])

    def test_warm_path_does_not_discover_or_launch_processes(self):
        with patch("runtime_core.store.discover", side_effect=AssertionError("unexpected discovery")), \
             patch("subprocess.run", side_effect=AssertionError("unexpected process")), \
             patch.object(Path, "rglob", side_effect=AssertionError("unexpected recursive search")):
            self.assertTrue(self.store.initialize([self.skills])["cache_hit"])
            r = execute_query(self.store, {"operation": "resolve", "refs": ["skill://one", "tool://python"]})
            self.assertEqual(r["status"], "ok")

    def test_site_prefix_normalization_does_not_change_runtime_identity(self):
        a = scope_id(self.root)
        with patch.object(sys, "prefix", "/a-site-derived-prefix"):
            self.assertEqual(a, scope_id(self.root))

    def test_added_skill_invalidates_catalog(self):
        (self.skills / "two").mkdir()
        (self.skills / "two/SKILL.md").write_text("# two\n", encoding="utf-8")
        with self.assertRaises(RuntimeFault) as ctx:
            self.store.current()
        self.assertEqual(ctx.exception.code, "STALE_CATALOG")
        self.assertFalse(self.store.initialize([self.skills])["cache_hit"])
        self.assertEqual(execute_query(self.store, {"operation": "status"})["skill_count"], 2)

    def test_expiry_requires_refresh(self):
        _, snapshot = self.store.current()
        with patch("runtime_core.store.time.time", return_value=snapshot["created_at"] + 86401):
            with self.assertRaises(RuntimeFault) as ctx:
                self.store.current()
        self.assertEqual(ctx.exception.code, "EXPIRED")

    def test_cold_discovery_never_uses_implicit_cwd_search(self):
        from runtime_core.environment import discover_tools
        with patch('shutil.which', side_effect=AssertionError('implicit search forbidden')):
            result = discover_tools()
        self.assertEqual(result['python']['status'], 'available')

    def test_native_suffix_lookup_only_uses_explicit_roots(self):
        import runtime_core.environment as environment
        self.assertTrue(callable(getattr(environment, 'locate_tool', None)))
        approved = self.root / 'approved-bin'
        approved.mkdir()
        binary = approved / 'git.exe'
        binary.write_bytes(b'not executed')
        self.assertEqual(environment.locate_tool('git', [approved], windows=True), str(binary))
        self.assertIsNone(environment.locate_tool('git', [], windows=True))
        with self.assertRaises(RuntimeFault):
            environment.locate_tool('git', [approved / str(i) for i in range(257)], windows=True)

    def test_negative_lookup_does_not_probe_path(self):
        with patch("shutil.which", side_effect=AssertionError("unexpected probe")):
            result = execute_query(self.store, {"operation": "resolve", "refs": ["tool://uninstalled-tool"]})
        self.assertEqual(result["status"], "partial")

    def test_output_accounting_is_exact(self):
        result = execute_query(self.store, {"operation": "context", "refs": ["skill://one"]})
        self.assertEqual(result["output_bytes"], len(canonical(result)))

    def test_invalid_query_types_fail_as_contract_errors(self):
        for request in ({"operation": []}, {"operation": {}}, {"operation": True}, {"operation": "resolve", "refs": "tool://python"}, {"operation": "status", "budget_bytes": True}):
            with self.subTest(request=request):
                with self.assertRaises(RuntimeFault):
                    execute_query(self.store, request)

    def test_host_configuration_preflights_all_paths(self):
        (self.root / "AGENTS.md").write_text("# untouched\n", encoding="utf-8")
        target = self.root / "outside"
        target.write_text("private", encoding="utf-8")
        try:
            (self.root / ".gitignore").symlink_to(target)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable")
        with self.assertRaises(RuntimeFault):
            configure(self.store, "generic")
        self.assertEqual((self.root / "AGENTS.md").read_text(), "# untouched\n")

    def test_json_duplicates_and_nonfinite_numbers_are_rejected(self):
        from runtime_core.common import strict_json
        for body in (b'{"operation":"status","operation":"execute"}', b'{"x":NaN}', b'{"x":Infinity}'):
            with self.assertRaises(RuntimeFault):
                strict_json(body)

    def test_json_rejects_escaped_surrogates_and_numeric_overflow(self):
        from runtime_core.common import strict_json
        for body in (b'{"id":"\\ud800"}', b'{"value":1e999}'):
            with self.subTest(body=body):
                with self.assertRaises(RuntimeFault):
                    strict_json(body)

    def test_new_resource_can_be_resolved_without_reindex(self):
        p = self.skills / "one/new.md"
        p.write_text("# new\n", encoding="utf-8")
        with patch("runtime_core.store.discover", side_effect=AssertionError("unexpected index")):
            result = execute_query(self.store, {"operation": "resolve", "refs": ["skill://one/new.md"]})
        self.assertEqual(result["status"], "ok")

    def test_hardlinked_state_is_not_replaced(self):
        current = self.store.root / "current.json"
        target = self.root / "linked-copy"
        try:
            os.link(current, target)
        except OSError:
            self.skipTest("hardlinks unavailable")
        before = target.read_bytes()
        with self.assertRaises(RuntimeFault):
            self.store.initialize([self.skills], refresh=True)
        self.assertEqual(target.read_bytes(), before)

    def test_oversized_resource_is_not_hashed(self):
        target = self.root / "big.txt"
        with target.open("wb") as stream:
            stream.truncate(8 * 1024 * 1024 + 1)
        with self.assertRaises(RuntimeFault) as ctx:
            execute_query(self.store, {"operation": "resolve", "refs": ["repo://big.txt"]})
        self.assertEqual(ctx.exception.code, "INPUT_TOO_LARGE")

    def test_bootstrap_card_uses_stdlib_only_startup(self):
        current = json.loads((self.store.root / "current.json").read_text())
        self.assertIn("-S", current["runtime_argv"])
        self.assertNotIn("-S", current["python_argv"])

    @unittest.skipIf(os.name == "nt", "Native Windows Python uses the PowerShell launcher; Git Bash sh is not a POSIX Python environment")
    @unittest.skipUnless(shutil.which("sh"), "POSIX shell not available; PowerShell adapter is tested separately")
    def test_posix_launcher_avoids_sitecustomize(self):
        marker = self.root / "site-was-loaded"
        custom = self.root / "injected-site"
        custom.mkdir()
        (custom / "sitecustomize.py").write_text("from pathlib import Path\nPath(" + repr(str(marker)) + ").write_text('unexpected')\n", encoding="utf-8")
        proc = subprocess.run([shutil.which("sh"), str(SKILL / "scripts/bootstrap.sh"), "--workspace", str(self.root), "init", "--skills-root", str(self.skills)],
                              env=dict(os.environ, RHAPSODIA_PYTHON=sys.executable, PYTHONPATH=str(custom)), capture_output=True, timeout=15)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertFalse(marker.exists())


if __name__ == "__main__":
    unittest.main()
