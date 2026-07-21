from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "mutation_transaction.py"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class MutationTransactionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="mago-mutation-test-")
        self.root = Path(self.temp.name)
        self.package = self.root / "package"
        self.package.mkdir()
        manifest = {
            "kind": "mago-spec-manifest",
            "spec_id": "spec-2026-07-20-filtered-export",
            "cycle_id": "cycle-2026-07-20-q3-delivery",
            "feature_key": "filtered-export",
            "title": "Filtered export",
            "type": "feature",
            "classification": "internal",
            "profile": "standard",
            "status": "planned",
            "phase": "define",
            "feature_version": "1.0.0",
            "created_at": "2026-07-20T12:00:00Z",
            "source_of_truth": {
                "registry": "../../registry/spec-2026-07-20-filtered-export.yaml",
                "prd": "prd.md",
                "tasks": "tasks.md",
                "validation": "validation.md",
                "notes": "notes.md",
            },
            "artifact_decisions": {},
            "traceability": {
                "primary_discovery_file": "",
                "supporting_discovery_files": [],
                "discovery_frontier": "",
            },
            "mutation_state": {
                "status": "clean",
                "transaction_id": None,
                "inspected_digest": None,
                "planned_writes": [],
                "completed_writes": [],
                "checkpoint": None,
                "cancellation_requested": False,
                "rollback_required": False,
            },
        }
        (self.package / "manifest.yaml").write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
        (self.package / "prd.md").write_text("old prd\n", encoding="utf-8")
        (self.package / "tasks.md").write_text("old tasks\n", encoding="utf-8")
        self.source = self.root / "source"
        self.source.mkdir()
        (self.source / "prd.md").write_text("new prd\n", encoding="utf-8")
        (self.source / "tasks.md").write_text("new tasks\n", encoding="utf-8")
        self.workspace = self.root / "transaction"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_cli(self, *args: str, expected: int = 0) -> subprocess.CompletedProcess[str]:
        completed = subprocess.run(
            [sys.executable, "-B", str(SCRIPT), *args],
            cwd=str(ROOT),
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, expected, completed.stdout + completed.stderr)
        return completed

    def begin_and_stage(self) -> None:
        self.run_cli(
            "begin",
            "--package",
            str(self.package),
            "--workspace",
            str(self.workspace),
            "--transaction-id",
            "tx-test",
            "--write",
            "prd.md",
            "--write",
            "tasks.md",
        )
        self.run_cli("stage", "--workspace", str(self.workspace), "--source-dir", str(self.source))

    def manifest_state(self) -> dict:
        manifest = yaml.safe_load((self.package / "manifest.yaml").read_text(encoding="utf-8"))
        return manifest["mutation_state"]

    def transaction_state(self) -> dict:
        return json.loads((self.workspace / "transaction.json").read_text(encoding="utf-8"))

    def test_successful_atomic_promotion_cleans_manifest(self) -> None:
        self.begin_and_stage()
        self.run_cli("promote", "--workspace", str(self.workspace))
        self.assertEqual((self.package / "prd.md").read_text(encoding="utf-8"), "new prd\n")
        self.assertEqual((self.package / "tasks.md").read_text(encoding="utf-8"), "new tasks\n")
        self.assertEqual(self.manifest_state()["status"], "clean")
        self.assertEqual(self.transaction_state()["status"], "completed")

    def test_interruption_after_first_write_resumes_safely(self) -> None:
        self.begin_and_stage()
        self.run_cli("promote", "--workspace", str(self.workspace), "--interrupt-after", "1", expected=75)
        state = self.transaction_state()
        self.assertEqual(state["status"], "in_progress")
        self.assertEqual(len(state["completed_writes"]), 1)
        self.assertEqual(self.manifest_state()["status"], "in_progress")
        self.run_cli("resume", "--workspace", str(self.workspace))
        self.assertEqual(self.manifest_state()["status"], "clean")
        self.assertEqual((self.package / "tasks.md").read_text(encoding="utf-8"), "new tasks\n")

    def test_injected_partial_failure_requires_and_supports_verified_rollback(self) -> None:
        before = {name: digest(self.package / name) for name in ("prd.md", "tasks.md")}
        self.begin_and_stage()
        self.run_cli("promote", "--workspace", str(self.workspace), "--fail-after", "1", expected=1)
        self.assertEqual(self.manifest_state()["status"], "rollback_required")
        self.assertTrue(self.manifest_state()["rollback_required"])
        self.run_cli("rollback", "--workspace", str(self.workspace))
        after = {name: digest(self.package / name) for name in ("prd.md", "tasks.md")}
        self.assertEqual(after, before)
        self.assertEqual(self.manifest_state()["status"], "clean")
        self.assertEqual(self.transaction_state()["status"], "rolled_back")

    def test_drift_before_promotion_is_detected_without_overwrite(self) -> None:
        self.begin_and_stage()
        (self.package / "prd.md").write_text("concurrent edit\n", encoding="utf-8")
        self.run_cli("promote", "--workspace", str(self.workspace), expected=1)
        self.assertEqual((self.package / "prd.md").read_text(encoding="utf-8"), "concurrent edit\n")
        self.assertEqual((self.package / "tasks.md").read_text(encoding="utf-8"), "old tasks\n")
        self.assertEqual(self.manifest_state()["status"], "in_progress")

    def test_second_transaction_is_rejected_while_first_is_active(self) -> None:
        self.begin_and_stage()
        other = self.root / "other-transaction"
        self.run_cli(
            "begin",
            "--package",
            str(self.package),
            "--workspace",
            str(other),
            "--write",
            "prd.md",
            expected=1,
        )
        self.assertFalse(other.exists())

    def test_cancel_then_rollback_returns_to_clean(self) -> None:
        self.run_cli(
            "begin",
            "--package",
            str(self.package),
            "--workspace",
            str(self.workspace),
            "--write",
            "prd.md",
        )
        self.run_cli("cancel", "--workspace", str(self.workspace))
        self.assertEqual(self.manifest_state()["status"], "cancelled")
        self.run_cli("rollback", "--workspace", str(self.workspace))
        self.assertEqual(self.manifest_state()["status"], "clean")

    def test_path_traversal_is_rejected_before_workspace_creation(self) -> None:
        self.run_cli(
            "begin",
            "--package",
            str(self.package),
            "--workspace",
            str(self.workspace),
            "--write",
            "../outside.md",
            expected=1,
        )
        self.assertFalse(self.workspace.exists())


if __name__ == "__main__":
    unittest.main()
