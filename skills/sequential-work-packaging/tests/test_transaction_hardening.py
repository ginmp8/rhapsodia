from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from apply_transaction import apply  # noqa: E402
from _swp_common import sha256_bytes, sha256_file, tree_hash  # noqa: E402
from _fixtures import make_cycle  # noqa: E402


class TransactionHardeningTests(unittest.TestCase):
    def _plan(self, root: Path, writes: list[dict], mode: str = "refine", spec_id: str | None = "spec001", **extra) -> dict:
        plan = {
            "plan_version": 1,
            "mode": mode,
            "cycle_root": str(root),
            "writes": writes,
            "post_validate": {"mode": mode, "spec_id": spec_id} if spec_id else {"mode": mode},
        }
        plan.update(extra)
        return plan

    def _apply(self, base: Path, plan: dict, name: str = "op") -> dict:
        plan_path = base / f"{name}.plan.json"
        receipt_path = base / f"{name}.receipt.json"
        plan_path.write_text(json.dumps(plan), encoding="utf-8")
        return apply(plan_path, receipt_path)

    def test_success_receipt_hash_matches_final_committed_tree(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = make_cycle(base)
            target = root / "specs/spec001/notes.md"
            source = base / "notes.md"
            source.write_text("# assumptions\n\nupdated\n", encoding="utf-8")
            result = self._apply(base, self._plan(root, [{
                "path": "specs/spec001/notes.md",
                "source": str(source),
                "expected_before_sha256": sha256_file(target),
            }]))
            self.assertEqual("applied", result["status"])
            self.assertEqual(result["candidate_tree_sha256"], tree_hash(root))
            self.assertEqual(result["after_tree_sha256"], tree_hash(root))
            self.assertEqual(result["validation"]["tree_sha256"], tree_hash(root))

    def test_done_history_reversal_is_blocked_before_live_mutation(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = make_cycle(base)
            target = root / "specs/spec001/tasks.md"
            done_text = target.read_text(encoding="utf-8").replace("- [ ] Task 1: First", "- [x] Task 1: First")
            target.write_text(done_text, encoding="utf-8")
            before = target.read_bytes()
            source = base / "tasks.md"
            source.write_text(done_text.replace("- [x] Task 1: First", "- [ ] Task 1: First"), encoding="utf-8")
            result = self._apply(base, self._plan(root, [{
                "path": "specs/spec001/tasks.md",
                "source": str(source),
                "expected_before_sha256": sha256_file(target),
            }]))
            self.assertEqual("blocked", result["status"])
            self.assertEqual("TRANSITION_VALIDATION_FAILED", result["code"])
            self.assertEqual(before, target.read_bytes())

    def test_feature_key_identity_change_is_blocked_before_live_mutation(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = make_cycle(base)
            catalog = root / "spec-catalog.yaml"
            manifest = root / "specs/spec001/manifest.yaml"
            catalog_before, manifest_before = catalog.read_bytes(), manifest.read_bytes()
            catalog_candidate = base / "catalog.yaml"
            manifest_candidate = base / "manifest.yaml"
            catalog_candidate.write_text(catalog.read_text().replace("feature_key: alpha", "feature_key: beta"), encoding="utf-8")
            manifest_candidate.write_text(manifest.read_text().replace("feature_key: alpha", "feature_key: beta"), encoding="utf-8")
            result = self._apply(base, self._plan(root, [
                {"path": "spec-catalog.yaml", "source": str(catalog_candidate), "expected_before_sha256": sha256_file(catalog)},
                {"path": "specs/spec001/manifest.yaml", "source": str(manifest_candidate), "expected_before_sha256": sha256_file(manifest)},
            ]))
            self.assertEqual("blocked", result["status"])
            self.assertEqual("TRANSITION_VALIDATION_FAILED", result["code"])
            self.assertEqual(catalog_before, catalog.read_bytes())
            self.assertEqual(manifest_before, manifest.read_bytes())

    def test_invalid_candidate_is_rejected_without_touching_live_bytes(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = make_cycle(base)
            manifest = root / "specs/spec001/manifest.yaml"
            before = manifest.read_bytes()
            candidate = base / "manifest.yaml"
            candidate.write_text(manifest.read_text().replace("feature_key: alpha", "feature_key: beta"), encoding="utf-8")
            result = self._apply(base, self._plan(root, [{
                "path": "specs/spec001/manifest.yaml",
                "source": str(candidate),
                "expected_before_sha256": sha256_file(manifest),
            }]))
            self.assertEqual("blocked", result["status"])
            self.assertEqual("CANDIDATE_VALIDATION_FAILED", result["code"])
            self.assertEqual(before, manifest.read_bytes())

    def test_equivalent_candidate_bytes_ignore_staging_source_path_in_transaction_identity(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = make_cycle(base)
            target = root / "specs/spec001/notes.md"
            original = target.read_bytes()
            original_hash = sha256_file(target)
            txids = []
            for idx in (1, 2):
                target.write_bytes(original)
                source = base / f"source-{idx}.md"
                source.write_text("# assumptions\n\nsame candidate\n", encoding="utf-8")
                result = self._apply(base, self._plan(root, [{
                    "path": "specs/spec001/notes.md",
                    "source": str(source),
                    "expected_before_sha256": original_hash,
                }]), name=f"op-{idx}")
                self.assertEqual("applied", result["status"])
                txids.append(result["transaction_id"])
            self.assertEqual(txids[0], txids[1])

    def test_receipt_inside_cycle_is_blocked_without_creating_receipt(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = make_cycle(base)
            target = root / "specs/spec001/notes.md"
            source = base / "notes.md"
            source.write_text("# assumptions\n\nupdated\n", encoding="utf-8")
            plan = self._plan(root, [{
                "path": "specs/spec001/notes.md",
                "source": str(source),
                "expected_before_sha256": sha256_file(target),
            }])
            plan_path = base / "plan.json"
            receipt_path = root / "receipt.json"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            result = apply(plan_path, receipt_path)
            self.assertEqual("RECEIPT_INSIDE_CYCLE", result["code"])
            self.assertFalse(receipt_path.exists())

    def test_existing_recovery_state_blocks_new_mutation(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = make_cycle(base)
            (root / ".swp-old-recovery").mkdir()
            target = root / "specs/spec001/notes.md"
            before = target.read_bytes()
            source = base / "notes.md"
            source.write_text("# assumptions\n\nupdated\n", encoding="utf-8")
            result = self._apply(base, self._plan(root, [{
                "path": "specs/spec001/notes.md",
                "source": str(source),
                "expected_before_sha256": sha256_file(target),
            }]))
            self.assertEqual("RECOVERY_STATE_PRESENT", result["code"])
            self.assertEqual(before, target.read_bytes())

    def test_active_transaction_lock_blocks_new_mutation(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = make_cycle(base)
            token = sha256_bytes(str(root.resolve()).encode("utf-8"))[:12]
            lock = root.parent / f".swp-lock-{token}"
            lock.mkdir()
            target = root / "specs/spec001/notes.md"
            before = target.read_bytes()
            source = base / "notes.md"
            source.write_text("# assumptions\n\nupdated\n", encoding="utf-8")
            result = self._apply(base, self._plan(root, [{
                "path": "specs/spec001/notes.md",
                "source": str(source),
                "expected_before_sha256": sha256_file(target),
            }]), name="locked")
            self.assertEqual("TRANSACTION_LOCKED", result["code"])
            self.assertEqual(before, target.read_bytes())

    def test_order_change_requires_explicit_authorization(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = make_cycle(base)
            catalog = root / "spec-catalog.yaml"
            candidate = base / "catalog.yaml"
            candidate.write_text(catalog.read_text().replace("  - order: 10", "  - order: 15"), encoding="utf-8")
            plan = self._plan(root, [{
                "path": "spec-catalog.yaml",
                "source": str(candidate),
                "expected_before_sha256": sha256_file(catalog),
            }], mode="order", spec_id=None)
            blocked = self._apply(base, plan, name="blocked")
            self.assertEqual("TRANSITION_VALIDATION_FAILED", blocked["code"])
            plan["allow_order_change"] = True
            applied = self._apply(base, plan, name="authorized")
            self.assertEqual("applied", applied["status"])

    def test_unknown_operation_plan_field_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = make_cycle(base)
            target = root / "specs/spec001/notes.md"
            source = base / "notes.md"
            source.write_bytes(target.read_bytes())
            plan = self._plan(root, [{
                "path": "specs/spec001/notes.md",
                "source": str(source),
                "expected_before_sha256": sha256_file(target),
            }])
            plan["unexpected"] = True
            result = self._apply(base, plan, name="unknown-field")
            self.assertEqual("PLAN_FIELDS_UNKNOWN", result["code"])

    def test_post_validate_mode_cannot_weaken_operation_mode(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = make_cycle(base)
            target = root / "specs/spec001/notes.md"
            source = base / "notes.md"
            source.write_text("# assumptions\n\nupdated\n", encoding="utf-8")
            plan = self._plan(root, [{
                "path": "specs/spec001/notes.md",
                "source": str(source),
                "expected_before_sha256": sha256_file(target),
            }])
            plan["post_validate"]["mode"] = "audit"
            result = self._apply(base, plan, name="mode-mismatch")
            self.assertEqual("POST_VALIDATE_MODE_MISMATCH", result["code"])

    def test_invalid_expected_hash_is_rejected_even_when_write_is_noop(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = make_cycle(base)
            target = root / "specs/spec001/notes.md"
            source = base / "notes.md"
            source.write_bytes(target.read_bytes())
            result = self._apply(base, self._plan(root, [{
                "path": "specs/spec001/notes.md",
                "source": str(source),
                "expected_before_sha256": "not-a-hash",
            }]), name="bad-hash")
            self.assertEqual("EXPECTED_HASH_INVALID", result["code"])

    def test_empty_cycle_root_is_never_interpreted_as_current_directory(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            source = base / "candidate"
            source.write_text("x", encoding="utf-8")
            plan = {
                "plan_version": 1,
                "mode": "order",
                "cycle_root": "",
                "writes": [{"path": "spec-catalog.yaml", "source": str(source), "expected_before_sha256": "ABSENT"}],
            }
            result = self._apply(base, plan)
            self.assertEqual("CYCLE_ROOT_INVALID", result["code"])


if __name__ == "__main__":
    unittest.main()
