from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from validate_documentation import validate_documentation


class DocumentationValidationTests(unittest.TestCase):
    def make_root(self, raw: str) -> Path:
        root = Path(raw) / "nomia"
        (root / "references" / "artifacts").mkdir(parents=True)
        (root / "examples").mkdir()
        (root / "SKILL.md").write_text("# Skill\n", encoding="utf-8")
        return root

    def test_parent_relative_link_is_normalized(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = self.make_root(raw)
            (root / "references" / "target.md").write_text("# Target\n", encoding="utf-8")
            (root / "references" / "artifacts" / "source.md").write_text(
                "[Target](../target.md)\n", encoding="utf-8"
            )
            self.assertEqual(validate_documentation(root)["errors"], [])

    def test_missing_link_fails(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = self.make_root(raw)
            (root / "references" / "source.md").write_text("[Missing](missing.md)\n", encoding="utf-8")
            errors = validate_documentation(root)["errors"]
            self.assertTrue(any("is missing" in error for error in errors))

    def test_root_escape_fails(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = self.make_root(raw)
            (root / "references" / "source.md").write_text("[Escape](../../outside.md)\n", encoding="utf-8")
            errors = validate_documentation(root)["errors"]
            self.assertTrue(any("escapes skill root" in error for error in errors))

    def test_external_and_anchor_links_are_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = self.make_root(raw)
            (root / "references" / "source.md").write_text(
                "[Web](https://example.com)\n[Anchor](#section)\n", encoding="utf-8"
            )
            self.assertEqual(validate_documentation(root)["errors"], [])


if __name__ == "__main__":
    unittest.main()
