from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_markdown_structure.py"
SPEC = importlib.util.spec_from_file_location("check_markdown_structure", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class MarkdownStructureTests(unittest.TestCase):
    def test_valid_document_has_no_findings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            doc = Path(tmp) / "README.md"
            doc.write_text(
                "# Title\n\n## Run\n\n```bash\necho ok\n```\n\n[Guide](guide.md)\n",
                encoding="utf-8",
            )
            findings = MODULE.analyze_file(doc)
            self.assertEqual([], findings)

    def test_heading_skip_and_ambiguous_link_are_warnings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            doc = Path(tmp) / "README.md"
            doc.write_text("# Title\n\n### Deep\n\n[click here](guide.md)\n", encoding="utf-8")
            findings = MODULE.analyze_file(doc)
            codes = {item["code"] for item in findings}
            self.assertIn("docs/heading/level-skip", codes)
            self.assertIn("docs/link/ambiguous-text", codes)
            self.assertFalse(any(item["severity"] == "error" for item in findings))

    def test_unclosed_fence_is_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            doc = Path(tmp) / "README.md"
            doc.write_text("# Title\n\n```python\nprint('x')\n", encoding="utf-8")
            receipt = MODULE.build_receipt([doc], MODULE.analyze_file(doc))
            self.assertEqual("fail", receipt["status"])
            self.assertEqual(1, receipt["errors"])
            self.assertTrue(any(item["code"] == "docs/fence/unclosed" for item in receipt["checks"]))


    def test_longer_outer_fence_allows_nested_triple_fence_example(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            doc = Path(tmp) / "README.md"
            doc.write_text(
                "# Title\n\n````markdown\n```bash\necho ok\n```\n````\n",
                encoding="utf-8",
            )
            receipt = MODULE.build_receipt([doc], MODULE.analyze_file(doc))
            self.assertEqual("pass", receipt["status"])
            self.assertEqual(0, receipt["errors"])
            self.assertEqual(0, receipt["warnings"])

    def test_missing_fence_language_is_non_blocking_warning(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            doc = Path(tmp) / "README.md"
            doc.write_text("# Title\n\n```\ntext\n```\n", encoding="utf-8")
            receipt = MODULE.build_receipt([doc], MODULE.analyze_file(doc))
            self.assertEqual("pass", receipt["status"])
            self.assertEqual(0, receipt["errors"])
            self.assertEqual(1, receipt["warnings"])


if __name__ == "__main__":
    unittest.main()
