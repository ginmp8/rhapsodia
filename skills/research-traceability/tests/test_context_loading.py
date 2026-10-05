from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "SKILL.md"


class ContextLoadingContractTests(unittest.TestCase):
    def test_skill_exposes_control_plane_in_first_100_lines(self):
        lines = SKILL.read_text(encoding="utf-8").splitlines()
        self.assertGreater(len(lines), 100)
        top = "\n".join(lines[:100]).lower()

        required_markers = {
            "mission/scope": ["## mission and authority", "own only the convergence layer"],
            "activation/routing": ["## activation and routing", "do not activate for"],
            "modes": ["## modes", "`create`", "`improve`", "`audit`", "`refresh`"],
            "invariants": ["## core invariants", "corpus-bounded", "reverse justification"],
            "workflow": ["## workflow at a glance", "resolve and freeze", "repair, freeze, deliver"],
            "resources": ["## resource loading", "references/workflow.md", "references/semantic-review.md"],
        }
        for surface, markers in required_markers.items():
            with self.subTest(surface=surface):
                for marker in markers:
                    self.assertIn(marker.lower(), top)

    def test_all_reference_markdown_is_directly_discoverable_from_skill(self):
        skill_text = SKILL.read_text(encoding="utf-8")
        linked = set(re.findall(r"\]\((references/[^)#]+\.md)(?:#[^)]+)?\)", skill_text))
        actual = {
            p.relative_to(ROOT).as_posix()
            for p in (ROOT / "references").glob("*.md")
        }
        self.assertEqual(actual, linked)

    def test_long_supporting_markdown_has_preview_structure(self):
        for path in sorted((ROOT / "references").glob("*.md")):
            lines = path.read_text(encoding="utf-8").splitlines()
            if len(lines) <= 100:
                continue
            top = "\n".join(lines[:40]).lower()
            with self.subTest(path=path.name):
                self.assertIn("## at a glance", top)
                self.assertIn("## contents", top)


if __name__ == "__main__":
    unittest.main()
