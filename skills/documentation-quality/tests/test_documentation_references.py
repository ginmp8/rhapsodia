from __future__ import annotations

import importlib.util
import tempfile
import unittest
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_documentation_references.py"
SPEC = importlib.util.spec_from_file_location("check_documentation_references", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class DocumentationReferenceTests(unittest.TestCase):
    def test_missing_link_emits_stable_failure_diagnostic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            doc = root / "README.md"
            doc.write_text("# T\n\n[Missing](docs/missing.md)\n", encoding="utf-8")
            missing, skipped = MODULE.check_links(doc, root)
            receipt = MODULE.build_receipt([doc], missing, skipped)
            self.assertEqual("fail", receipt["status"])
            self.assertEqual(1, receipt["errors"])
            self.assertEqual("docs/ref/missing-markdown-link", receipt["checks"][0]["code"])
            self.assertEqual(1, receipt["missing_count"])

    def test_illustrative_code_span_is_skipped_not_failed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            doc = root / "README.md"
            doc.write_text("# T\n\nUse `path/to/script.py`.\n", encoding="utf-8")
            missing, skipped = MODULE.check_code_spans(doc, root)
            receipt = MODULE.build_receipt([doc], missing, skipped)
            self.assertEqual("pass", receipt["status"])
            self.assertEqual(0, receipt["errors"])
            self.assertEqual("illustrative_or_pattern", receipt["skipped"][0]["reason"])


    def test_code_span_can_resolve_from_declared_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "scripts").mkdir()
            (root / "scripts" / "check.py").write_text("print('ok')\n", encoding="utf-8")
            refs = root / "references"
            refs.mkdir()
            doc = refs / "guide.md"
            doc.write_text("# Guide\n\nUse `scripts/check.py`.\n", encoding="utf-8")
            missing, skipped = MODULE.check_code_spans(doc, root)
            receipt = MODULE.build_receipt([doc], missing, skipped)
            self.assertEqual("pass", receipt["status"])
            self.assertEqual([], receipt["missing"])

    def test_existing_relative_link_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            docs = root / "docs"
            docs.mkdir()
            target = docs / "guide.md"
            target.write_text("# Guide\n", encoding="utf-8")
            readme = root / "README.md"
            readme.write_text("# T\n\n[Guide](docs/guide.md)\n", encoding="utf-8")
            missing, skipped = MODULE.check_links(readme, root)
            receipt = MODULE.build_receipt([readme], missing, skipped)
            self.assertEqual("pass", receipt["status"])
            self.assertEqual([], receipt["missing"])

    def test_dot_slash_link_resolves_relative_to_source_document(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            refs = root / "references"
            refs.mkdir()
            (refs / "peer.md").write_text("# Peer\n", encoding="utf-8")
            guide = refs / "guide.md"
            guide.write_text("# Guide\n\n[Peer](./peer.md)\n", encoding="utf-8")
            missing, skipped = MODULE.check_links(guide, root)
            receipt = MODULE.build_receipt([guide], missing, skipped)
            self.assertEqual("pass", receipt["status"])
            self.assertEqual([], receipt["missing"])

    def test_links_inside_fenced_examples_are_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            doc = root / "README.md"
            doc.write_text(
                "# T\n\n```markdown\n[Illustrative](missing.md)\n```\n",
                encoding="utf-8",
            )
            missing, skipped = MODULE.check_links(doc, root)
            receipt = MODULE.build_receipt([doc], missing, skipped)
            self.assertEqual("pass", receipt["status"])
            self.assertEqual([], receipt["missing"])


if __name__ == "__main__":
    unittest.main()
