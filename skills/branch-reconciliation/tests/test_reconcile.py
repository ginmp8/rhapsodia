"""Real Git DAG, tree and conflict regression tests; no remote access."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "reconcile.py"


class ReconcileTests(unittest.TestCase):
    def setUp(self) -> None:
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.root = Path(self.folder.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.git("init", "-q", "-b", "target")
        self.git("config", "user.name", "Integration Test")
        self.git("config", "user.email", "integration@example.invalid")
        self.write("shared.txt", "".join(f"line {i}\n" for i in range(30)))
        self.git("add", "-A")
        self.git("commit", "-qm", "initial")
        self.git("branch", "source")
        self.base = self.git("rev-parse", "HEAD")

    def git(self, *args: str) -> str:
        result = subprocess.run(["git", "-C", str(self.repo), *args], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result.stdout.strip()

    def write(self, name: str, content: str) -> None:
        file = self.repo / name
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(content, encoding="utf-8")

    def edit_line(self, line: int, value: str) -> None:
        file = self.repo / "shared.txt"
        rows = file.read_text(encoding="utf-8").splitlines(keepends=True)
        rows[line] = value + "\n"
        file.write_text("".join(rows), encoding="utf-8")

    def target_change(self, conflicting: bool = False) -> str:
        self.edit_line(5, "target update")
        self.write("only-target.txt", "target kept\n")
        self.git("add", "-A")
        self.git("commit", "-qm", "target update")
        return self.git("rev-parse", "HEAD")

    def source_change(self, conflicting: bool = False) -> str:
        self.git("switch", "-q", "source")
        self.edit_line(5 if conflicting else 24, "source update")
        self.write("only-source.txt", "source kept\n")
        self.git("add", "-A")
        self.git("commit", "-qm", "source update")
        return self.git("rev-parse", "HEAD")

    def cli(self, *args: str) -> tuple[int, dict]:
        result = subprocess.run([sys.executable, "-I", "-S", "-B", str(SCRIPT), "--repo", str(self.repo), *args],
                                capture_output=True, text=True)
        text = result.stdout if result.stdout.strip() else result.stderr
        return result.returncode, json.loads(text)

    def make_plan(self, *extra: str) -> tuple[int, dict, Path]:
        file = self.root / "plan.json"
        code, result = self.cli("plan", "--source", "source", "--target", "target", "--output", str(file), *extra)
        return code, result, file

    def test_clean_reconciliation_preserves_both_sides_and_single_parent(self):
        target = self.target_change()
        source = self.source_change()
        code, plan, file = self.make_plan()
        self.assertEqual(code, 0)
        self.assertEqual(plan["status"], "ready")
        self.assertIn("only-source.txt", plan["groups"]["source_only"])
        self.assertIn("only-target.txt", plan["groups"]["target_only"])
        self.assertIn("shared.txt", plan["groups"]["both_changed"])
        self.assertEqual(self.git("rev-parse", "target"), target)
        self.assertEqual(self.git("rev-parse", "source"), source)
        code, rejected = self.cli("apply", "--plan", str(file), "--message", "single parent integration", "--confirm")
        self.assertEqual(code, 2)
        self.assertIn("semantic review", rejected["reason"])
        code, applied = self.cli("apply", "--plan", str(file), "--message", "single parent integration", "--reviewed", "--confirm")
        self.assertEqual(code, 0, applied)
        commit = applied["new_commit"]
        self.assertEqual(self.git("rev-list", "--parents", "-n", "1", commit), f"{commit} {target}")
        self.assertEqual(self.git("rev-parse", "source"), source)
        self.assertEqual(self.git("rev-parse", "target"), commit)
        self.assertEqual(self.git("show", "target:only-target.txt"), "target kept")
        self.assertEqual(self.git("show", "target:only-source.txt"), "source kept")
        shared = self.git("show", "target:shared.txt")
        self.assertIn("target update", shared)
        self.assertIn("source update", shared)
        self.assertEqual(self.git("merge-base", "source", "target"), self.base)

    def test_conflict_blocks_ref_and_explicit_resolution_works(self):
        original_target = self.target_change()
        self.source_change(conflicting=True)
        code, conflict, path = self.make_plan()
        self.assertEqual(code, 3)
        self.assertEqual(conflict["status"], "conflicts")
        self.assertEqual(conflict["conflict_paths"], ["shared.txt"])
        self.assertIsNone(conflict["candidate_tree"])
        self.assertEqual(self.git("rev-parse", "target"), original_target)
        root = self.root / "resolutions"
        root.mkdir()
        (root / "shared.txt").write_text("combined target and source\n", encoding="utf-8")
        manifest = self.root / "resolutions.json"
        manifest.write_text(json.dumps({"schema": "branch-reconciliation-resolutions/v1",
                                        "paths": {"shared.txt": {"file": "shared.txt", "mode": "100644", "reason": "reviewed both changes"}}}), encoding="utf-8")
        code, plan, approved = self.make_resolved_plan(manifest, root)
        self.assertEqual(code, 0, plan)
        self.assertEqual(plan["status"], "ready")
        code, result = self.cli("apply", "--plan", str(approved), "--message", "integrate both",
                                "--reviewed", "--confirm", "--resolutions", str(manifest),
                                "--resolution-root", str(root))
        self.assertEqual(code, 0, result)
        self.assertEqual(self.git("show", "target:shared.txt"), "combined target and source")
        self.assertEqual(self.git("show", "target:only-source.txt"), "source kept")

    def make_resolved_plan(self, manifest: Path, root: Path) -> tuple[int, dict, Path]:
        file = self.root / "resolved-plan.json"
        code, output = self.cli("plan", "--source", "source", "--target", "target", "--output", str(file),
                                "--resolutions", str(manifest), "--resolution-root", str(root))
        return code, output, file

    def test_stale_plan_rejected_without_branch_mutation(self):
        target = self.target_change()
        self.source_change()
        code, _, plan = self.make_plan()
        self.assertEqual(code, 0)
        self.write("new.txt", "new commit")
        self.git("add", "-A")
        self.git("commit", "-qm", "source advanced")
        code, result = self.cli("apply", "--plan", str(plan), "--message", "stale", "--confirm", "--reviewed")
        self.assertEqual(code, 2)
        self.assertIn("changed", result["reason"])
        self.assertEqual(self.git("rev-parse", "target"), target)

    def test_dirty_worktree_and_checked_out_target_are_rejected(self):
        target = self.target_change()
        self.source_change()
        _, _, plan = self.make_plan()
        self.write("untracked.tmp", "not mine")
        code, result = self.cli("apply", "--plan", str(plan), "--message", "blocked", "--confirm", "--reviewed")
        self.assertEqual(code, 2)
        self.assertIn("local changes", result["reason"])
        (self.repo / "untracked.tmp").unlink()
        self.git("switch", "-q", "target")
        code, result = self.cli("apply", "--plan", str(plan), "--message", "blocked", "--confirm", "--reviewed")
        self.assertEqual(code, 2)
        self.assertIn("checked out", result["reason"])
        self.assertEqual(self.git("rev-parse", "target"), target)

    def test_resolution_path_escape_is_rejected(self):
        self.target_change()
        self.source_change(conflicting=True)
        root = self.root / "resolutions"
        root.mkdir()
        manifest = self.root / "invalid.json"
        manifest.write_text(json.dumps({"schema": "branch-reconciliation-resolutions/v1",
                                        "paths": {"shared.txt": {"file": "../outside", "mode": "100644", "reason": "invalid"}}}), encoding="utf-8")
        code, result = self.cli("plan", "--source", "source", "--target", "target", "--resolutions", str(manifest), "--resolution-root", str(root))
        self.assertEqual(code, 2)
        self.assertIn("relative path", result["reason"])

    def test_configured_custom_merge_driver_is_blocked_before_running(self):
        self.target_change()
        self.source_change()
        self.git("config", "merge.external.driver", "echo do-not-execute")
        code, result = self.cli("plan", "--source", "source", "--target", "target")
        self.assertEqual(code, 2)
        self.assertIn("Custom external", result["reason"])

    def test_no_change_fails_closed_for_apply(self):
        code, plan, file = self.make_plan()
        self.assertEqual(code, 0)
        self.assertEqual(plan["status"], "no_change")
        code, result = self.cli("apply", "--plan", str(file), "--message", "no change", "--confirm")
        self.assertEqual(code, 2)
        self.assertIn("Only a conflict-free", result["reason"])


if __name__ == "__main__":
    unittest.main()
