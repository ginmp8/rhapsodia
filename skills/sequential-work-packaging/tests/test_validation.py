from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from validate_sequential import validate_cycle  # noqa: E402
from validate_transition import validate_transition  # noqa: E402
from _fixtures import make_cycle, write_spec  # noqa: E402


def codes(report):
    return {d["code"] for d in report["diagnostics"]}


class ValidationTests(unittest.TestCase):
    def test_valid_define(self):
        with tempfile.TemporaryDirectory() as td:
            root = make_cycle(Path(td))
            report = validate_cycle(root, "define", "spec001")
            self.assertEqual("pass", report["status"])
            self.assertEqual(0, report["error_count"])

    def test_duplicate_spec_id_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            specs = [
                {"order":10,"spec_id":"spec001","feature_key":"alpha","title":"Alpha","type":"feature","classification":"feature","depends_on_features":[],"depends_on_specs":[],"status":"planned","feature_version":"v0.1.0"},
                {"order":20,"spec_id":"spec001","feature_key":"beta","title":"Beta","type":"feature","classification":"feature","depends_on_features":[],"depends_on_specs":[],"status":"planned","feature_version":"v0.1.0"}
            ]
            root = make_cycle(Path(td), specs, create_specs=False)
            report = validate_cycle(root, "order")
            self.assertIn("SPEC_ID_DUPLICATE", codes(report))

    def test_duplicate_functional_identity_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            specs = [
                {"order":10,"spec_id":"spec001","feature_key":"alpha","title":"Alpha","type":"feature","classification":"feature","depends_on_features":[],"depends_on_specs":[],"status":"planned","feature_version":"v0.1.0"},
                {"order":20,"spec_id":"spec002","feature_key":"alpha","title":"Alpha 2","type":"feature","classification":"feature","depends_on_features":[],"depends_on_specs":["spec001"],"status":"planned","feature_version":"v0.1.0"}
            ]
            root = make_cycle(Path(td), specs, create_specs=False)
            report = validate_cycle(root, "order")
            self.assertIn("FUNCTIONAL_IDENTITY_DUPLICATE", codes(report))

    def test_manifest_mismatch_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            root = make_cycle(Path(td))
            p = root / "specs/spec001/manifest.yaml"
            p.write_text(p.read_text().replace("feature_key: alpha", "feature_key: beta"), encoding="utf-8")
            report = validate_cycle(root, "define", "spec001")
            self.assertIn("MANIFEST_CATALOG_MISMATCH", codes(report))

    def test_dependency_cycle_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            specs = [
                {"order":10,"spec_id":"spec001","feature_key":"alpha","title":"Alpha","type":"feature","classification":"feature","depends_on_features":["beta"],"depends_on_specs":["spec002"],"status":"planned","feature_version":"v0.1.0"},
                {"order":20,"spec_id":"spec002","feature_key":"beta","title":"Beta","type":"feature","classification":"feature","depends_on_features":["alpha"],"depends_on_specs":["spec001"],"status":"planned","feature_version":"v0.1.0"}
            ]
            root = make_cycle(Path(td), specs, create_specs=False)
            report = validate_cycle(root, "order")
            self.assertIn("SPEC_DEPENDENCY_CYCLE", codes(report))

    def test_task_dependency_order_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            root = make_cycle(Path(td))
            tasks = root / "specs/spec001/tasks.md"
            text = tasks.read_text(encoding="utf-8")
            text = text.replace("- Dependencies: none", "- Dependencies: task002", 1)
            tasks.write_text(text, encoding="utf-8")
            report = validate_cycle(root, "define", "spec001")
            self.assertIn("TASK_DEPENDENCY_ORDER_INVALID", codes(report))

    def test_unknown_file_is_preserved_warning(self):
        with tempfile.TemporaryDirectory() as td:
            root = make_cycle(Path(td))
            extra = root / "specs/spec001/custom-context.md"
            extra.write_text("keep me", encoding="utf-8")
            report = validate_cycle(root, "refine", "spec001")
            self.assertEqual("pass", report["status"])
            self.assertIn("UNKNOWN_FILE_PRESERVED", codes(report))

    def test_define_requires_explicit_task_id(self):
        with tempfile.TemporaryDirectory() as td:
            root = make_cycle(Path(td))
            p = root / "specs/spec001/tasks.md"
            p.write_text(p.read_text().replace("  - Task ID: task001\n", "", 1), encoding="utf-8")
            report = validate_cycle(root, "define", "spec001")
            self.assertIn("LEGACY_TASK_ID", codes(report))
            self.assertEqual("fail", report["status"])


class TransitionTests(unittest.TestCase):
    def test_stable_task_removal_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            before = make_cycle(base / "before")
            after_parent = base / "after"
            after_parent.mkdir()
            after = after_parent / before.name
            shutil.copytree(before, after)
            p = after / "specs/spec001/tasks.md"
            text = p.read_text(encoding="utf-8")
            text = text[text.index("- [ ] Task 2:"):]
            p.write_text(text, encoding="utf-8")
            report = validate_transition(before, after, "refine")
            self.assertIn("TASK_ID_REMOVED", codes(report))

    def test_unknown_file_deletion_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            before = make_cycle(base / "before")
            extra = before / "specs/spec001/custom-context.md"
            extra.write_text("keep", encoding="utf-8")
            after_parent = base / "after"
            after_parent.mkdir()
            after = after_parent / before.name
            shutil.copytree(before, after)
            (after / "specs/spec001/custom-context.md").unlink()
            report = validate_transition(before, after, "refine")
            self.assertIn("UNKNOWN_FILE_DELETED", codes(report))

    def test_same_input_output_alias_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            root = make_cycle(Path(td))
            report = validate_transition(root, root, "normalize")
            self.assertIn("INPUT_OUTPUT_ALIAS", codes(report))

    def test_order_change_requires_authorization(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            before = make_cycle(base / "before")
            after_parent = base / "after"
            after_parent.mkdir()
            after = after_parent / before.name
            shutil.copytree(before, after)
            p = after / "spec-catalog.yaml"
            p.write_text(p.read_text().replace("  - order: 10", "  - order: 15"), encoding="utf-8")
            report = validate_transition(before, after, "order")
            self.assertIn("ORDER_CHANGED_WITHOUT_AUTHORIZATION", codes(report))

    def test_normalize_legacy_source_is_read_as_source_not_canonical_target(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            legacy = base / "legacy"
            legacy.mkdir()
            (legacy / "PRD.md").write_text("legacy", encoding="utf-8")
            after = make_cycle(base / "after")
            report = validate_transition(legacy, after, "normalize")
            self.assertEqual("pass", report["status"])
            self.assertIn("LEGACY_SOURCE_NO_CANONICAL_CATALOG", codes(report))
            self.assertEqual("legacy", (legacy / "PRD.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
