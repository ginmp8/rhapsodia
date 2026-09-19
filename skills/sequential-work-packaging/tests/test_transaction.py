from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from apply_transaction import apply  # noqa: E402
from _swp_common import sha256_file  # noqa: E402
from _fixtures import make_cycle  # noqa: E402


class TransactionTests(unittest.TestCase):
    def _plan(self, root: Path, writes: list[dict], mode="refine", spec_id="spec001") -> dict:
        return {
            "plan_version": 1,
            "mode": mode,
            "cycle_root": str(root),
            "writes": writes,
            "post_validate": {"mode": mode, "spec_id": spec_id} if spec_id else {"mode": mode}
        }

    def test_success_then_rerun_is_no_change(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = make_cycle(base)
            target = root / "specs/spec001/notes.md"
            before = sha256_file(target)
            staged = base / "notes.candidate.md"
            staged.write_text("# assumptions\n\nupdated\n", encoding="utf-8")
            plan = self._plan(root, [{"path":"specs/spec001/notes.md","source":str(staged),"expected_before_sha256":before}])
            plan_path, receipt = base / "plan.json", base / "receipt.json"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            first = apply(plan_path, receipt)
            self.assertEqual("applied", first["status"])
            self.assertEqual(staged.read_bytes(), target.read_bytes())
            second = apply(plan_path, receipt)
            self.assertEqual("no_change", second["status"])
            self.assertEqual(staged.read_bytes(), target.read_bytes())

    def test_partial_failure_restores_last_good(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = make_cycle(base)
            n = root / "specs/spec001/notes.md"
            v = root / "specs/spec001/validation.md"
            n_before, v_before = n.read_bytes(), v.read_bytes()
            sn, sv = base / "n.md", base / "v.md"
            sn.write_text("# assumptions\n\nchanged\n", encoding="utf-8")
            sv.write_text("# validation strategy\n\nchanged\n", encoding="utf-8")
            plan = self._plan(root, [
                {"path":"specs/spec001/notes.md","source":str(sn),"expected_before_sha256":sha256_file(n)},
                {"path":"specs/spec001/validation.md","source":str(sv),"expected_before_sha256":sha256_file(v)}
            ])
            plan_path, receipt = base / "plan.json", base / "receipt.json"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            result = apply(plan_path, receipt, fail_after=1)
            self.assertEqual("failed_recovered", result["status"])
            self.assertEqual(n_before, n.read_bytes())
            self.assertEqual(v_before, v.read_bytes())
            retry = apply(plan_path, receipt)
            self.assertEqual("applied", retry["status"])

    def test_protected_path_blocks_before_mutation(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = make_cycle(base)
            source = base / "candidate"
            source.write_text("secret", encoding="utf-8")
            plan = self._plan(root, [{"path":".env","source":str(source),"expected_before_sha256":"ABSENT"}])
            plan_path, receipt = base / "plan.json", base / "receipt.json"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            result = apply(plan_path, receipt)
            self.assertEqual("blocked", result["status"])
            self.assertEqual("PROTECTED_PATH", result["code"])
            self.assertFalse((root / ".env").exists())

    def test_source_target_alias_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = make_cycle(base)
            target = root / "specs/spec001/notes.md"
            plan = self._plan(root, [{"path":"specs/spec001/notes.md","source":str(target),"expected_before_sha256":sha256_file(target)}])
            plan_path, receipt = base / "plan.json", base / "receipt.json"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            result = apply(plan_path, receipt)
            self.assertEqual("SOURCE_TARGET_ALIAS", result["code"])

    def test_expected_hash_mismatch_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = make_cycle(base)
            staged = base / "notes.md"
            staged.write_text("different", encoding="utf-8")
            plan = self._plan(root, [{"path":"specs/spec001/notes.md","source":str(staged),"expected_before_sha256":"0"*64}])
            plan_path, receipt = base / "plan.json", base / "receipt.json"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            result = apply(plan_path, receipt)
            self.assertEqual("EXPECTED_HASH_MISMATCH", result["code"])

    def test_new_spec_transaction_creates_canonical_package(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            specs = [
                {"order":10,"spec_id":"spec001","feature_key":"alpha","title":"Alpha","type":"feature","classification":"feature","depends_on_features":[],"depends_on_specs":[],"status":"planned","feature_version":"v0.1.0"},
                {"order":20,"spec_id":"spec002","feature_key":"beta","title":"Beta","type":"feature","classification":"feature","depends_on_features":[],"depends_on_specs":[],"status":"planned","feature_version":"v0.1.0"}
            ]
            root = make_cycle(base, specs, create_specs=False)
            from _fixtures import write_spec
            write_spec(root, "spec001", "alpha", "v0.1.0", 10)
            staging_root = base / "staging" / "01.00.00"
            staging_root.mkdir(parents=True)
            write_spec(staging_root, "spec002", "beta", "v0.1.0", 20)
            manifest = staging_root / "specs/spec002/manifest.yaml"
            manifest.write_text(manifest.read_text(encoding="utf-8").replace("title: Alpha", "title: Beta"), encoding="utf-8")
            writes = []
            for name in ("manifest.yaml", "prd.md", "tasks.md", "notes.md", "validation.md"):
                writes.append({
                    "path": f"specs/spec002/{name}",
                    "source": str(staging_root / "specs/spec002" / name),
                    "expected_before_sha256": "ABSENT"
                })
            plan = self._plan(root, writes, mode="define", spec_id="spec002")
            plan_path, receipt = base / "plan-new.json", base / "receipt-new.json"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            result = apply(plan_path, receipt)
            self.assertEqual("applied", result["status"])
            self.assertTrue((root / "specs/spec002/manifest.yaml").is_file())

    def test_decompose_repeated_candidate_is_no_change(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = make_cycle(base)
            target = root / "specs/spec001/tasks.md"
            staged = base / "tasks.candidate.md"
            staged.write_bytes(target.read_bytes())
            plan = self._plan(root, [{"path":"specs/spec001/tasks.md","source":str(staged),"expected_before_sha256":sha256_file(target)}], mode="decompose", spec_id="spec001")
            plan_path, receipt = base / "plan-decompose.json", base / "receipt-decompose.json"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            result = apply(plan_path, receipt)
            self.assertEqual("no_change", result["status"])


if __name__ == "__main__":
    unittest.main()
