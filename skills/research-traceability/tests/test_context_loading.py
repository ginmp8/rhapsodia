from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "SKILL.md"
PREVIEW_HEADINGS = {
    "at a glance",
    "summary",
    "quick reference",
    "overview",
    "contents",
    "table of contents",
    "section map",
}


def h2_headings(lines: list[str]) -> list[str]:
    headings: list[str] = []
    in_fence = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        match = re.match(r"^##\s+(.+?)\s*$", line)
        if match:
            headings.append(match.group(1).strip())
    return headings


def contents_entries(lines: list[str]) -> list[str]:
    start = None
    for i, line in enumerate(lines[:40]):
        if re.match(r"^##\s+(Contents|Table of Contents|Section Map)\s*$", line, re.I):
            start = i + 1
            break
    if start is None:
        return []

    entries: list[str] = []
    for line in lines[start:]:
        if line.startswith("## "):
            break
        bullet = re.match(r"^\s*[-*]\s+(.+?)\s*$", line)
        numbered = re.match(r"^\s*(\d+\.\s+.+?)\s*$", line)
        if bullet:
            entries.append(bullet.group(1).strip())
        elif numbered:
            entries.append(numbered.group(1).strip())
    return entries


class ContextLoadingContractTests(unittest.TestCase):
    def test_skill_top_100_is_self_sufficient_control_plane(self):
        lines = SKILL.read_text(encoding="utf-8").splitlines()
        self.assertGreater(len(lines), 100)
        top = "\n".join(lines[:100]).lower()

        required_markers = {
            "mission/scope": [
                "## mission and authority",
                "own only the convergence layer",
                "research evidence -> atomic findings",
            ],
            "activation/routing": [
                "## activation and routing",
                "use this skill only when",
                "do not activate for",
                "deep-research phase",
            ],
            "modes": ["## modes", "`create`", "`improve`", "`audit`", "`refresh`"],
            "critical invariants": [
                "## core invariants",
                "corpus-bounded",
                "exactly one disposition",
                "reverse-trace",
                "freeze evaluator assets",
                "mechanical proof from model judgment",
                "paired baseline-vs-candidate",
                "first 100 physical lines",
                "multi-hop markdown chains",
                "passing candidate is immutable",
            ],
            "usable workflow": [
                "## quick-start workflow",
                "resolve and freeze",
                "normalize and extract",
                "derive and map",
                "freeze evaluation and plan",
                "mutate minimally and evaluate",
                "repair, freeze, deliver",
            ],
            "finalization": [
                "## minimum finalization gates",
                "finding_accounting = 100%",
                "bidirectional `f -> r -> c/e`",
                "no unresolved required conflict",
                "no candidate edit after the last passing validation",
                "do not claim unavailable proof",
            ],
            "direct resources": [
                "## direct resource map",
                "references/workflow.md",
                "references/traceability-model.md",
                "references/workspace-contract.md",
                "references/semantic-review.md",
                "references/reproducibility.md",
                "references/refresh-impact.md",
            ],
            "claim boundary": [
                "## reproducibility ceiling",
                "never present structural trace coverage",
            ],
        }
        for surface, markers in required_markers.items():
            with self.subTest(surface=surface):
                for marker in markers:
                    self.assertIn(marker.lower(), top)

    def test_all_reference_markdown_is_directly_discoverable_from_skill_top_100(self):
        lines = SKILL.read_text(encoding="utf-8").splitlines()
        top = "\n".join(lines[:100])
        linked = set(re.findall(r"\]\((references/[^)#]+\.md)(?:#[^)]+)?\)", top))
        actual = {p.relative_to(ROOT).as_posix() for p in (ROOT / "references").glob("*.md")}
        self.assertEqual(actual, linked)

    def test_no_reference_requires_hidden_markdown_hop(self):
        skill_text = SKILL.read_text(encoding="utf-8")
        direct = set(re.findall(r"\]\((references/[^)#]+\.md)(?:#[^)]+)?\)", skill_text))
        for path in sorted((ROOT / "references").glob("*.md")):
            text = path.read_text(encoding="utf-8")
            for target in re.findall(r"\]\(([^)#]+\.md)(?:#[^)]+)?\)", text):
                resolved = (path.parent / target).resolve()
                try:
                    rel = resolved.relative_to(ROOT).as_posix()
                except ValueError:
                    continue
                if rel.startswith("references/"):
                    with self.subTest(source=path.name, target=rel):
                        self.assertIn(rel, direct)

    def test_long_supporting_markdown_preview_matches_material_h2_sections(self):
        for path in sorted((ROOT / "references").glob("*.md")):
            lines = path.read_text(encoding="utf-8").splitlines()
            if len(lines) <= 100:
                continue
            top = "\n".join(lines[:40]).lower()
            with self.subTest(path=path.name):
                self.assertIn("## at a glance", top)
                self.assertIn("## contents", top)

                actual = [h for h in h2_headings(lines) if h.lower() not in PREVIEW_HEADINGS]
                indexed = contents_entries(lines)
                self.assertEqual(actual, indexed)


if __name__ == "__main__":
    unittest.main()
