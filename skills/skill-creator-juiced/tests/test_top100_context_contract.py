from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
try:
    from juiced_quality_gate import check_top100_contract
finally:
    sys.path.remove(str(SCRIPTS))


def make_long_skill(base: Path, *, early_control: bool) -> Path:
    root = base / "demo-skill"
    root.mkdir()
    early = "## Activation and Routing\nUse when demo work applies.\n\n## Workflow\n1. Do the work.\n\n## Core Rules\n- Preserve evidence.\n" if early_control else "## Notes\nGeneral notes only.\n"
    filler = "\n".join(f"filler {i}" for i in range(120))
    late = "\n## Activation and Routing\nUse when demo work applies.\n\n## Workflow\nDo the work.\n\n## Core Rules\nPreserve evidence.\n"
    (root / "SKILL.md").write_text(
        "---\nname: demo-skill\ndescription: Use when demo work applies; do not use for unrelated work.\n---\n\n# Demo\n\n"
        + early + filler + ("" if early_control else late),
        encoding="utf-8",
    )
    return root


def add_reference(root: Path, content: str) -> Path:
    refs = root / "references"
    refs.mkdir(exist_ok=True)
    ref = refs / "detail.md"
    ref.write_text(content, encoding="utf-8")
    skill = root / "SKILL.md"
    skill.write_text(skill.read_text(encoding="utf-8") + "\n[Detail](references/detail.md)\n", encoding="utf-8")
    return skill


def valid_long_reference() -> str:
    filler = "\n".join(f"detail line {i}" for i in range(110))
    return (
        "# Detail\n\n"
        "## Summary\n\n"
        "Detailed rules for the active branch.\n\n"
        "## Table of Contents\n\n"
        "- [Alpha](#alpha)\n"
        "- [Beta](#beta)\n\n"
        "## Alpha\n\n"
        "```markdown\n## Embedded Example Heading\n```\n\n"
        + filler
        + "\n\n## Beta\n\nFinal details.\n"
    )


def test_long_skill_requires_decision_and_execution_surface_in_first_100_lines() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = make_long_skill(Path(td), early_control=False)
        errors, _warnings = check_top100_contract(root, root / "SKILL.md")
        assert any("Top-100 control plane" in error for error in errors)


def test_long_skill_passes_when_boundary_workflow_and_rules_are_early() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = make_long_skill(Path(td), early_control=True)
        errors, _warnings = check_top100_contract(root, root / "SKILL.md")
        assert not errors


def test_long_supporting_markdown_without_preview_fails() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = make_long_skill(Path(td), early_control=True)
        skill = add_reference(root, "# Detail\n\n" + "\n".join(f"line {i}" for i in range(120)) + "\n")
        errors, _warnings = check_top100_contract(root, skill)
        assert any("requires an early summary" in error for error in errors)


def test_long_supporting_markdown_passes_with_heading_derived_contents() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = make_long_skill(Path(td), early_control=True)
        skill = add_reference(root, valid_long_reference())
        errors, _warnings = check_top100_contract(root, skill)
        assert not errors


def test_long_supporting_markdown_rejects_stale_contents() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = make_long_skill(Path(td), early_control=True)
        content = valid_long_reference().replace("[Beta](#beta)", "[Old Section](#old-section)", 1)
        skill = add_reference(root, content)
        errors, _warnings = check_top100_contract(root, skill)
        assert any("contents do not match material H2 headings" in error for error in errors)


def test_long_supporting_markdown_allows_explicit_exception_with_warning() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = make_long_skill(Path(td), early_control=True)
        content = "# Vendor Detail\n\n<!-- context-preview-exception: vendor -->\n\n" + "\n".join(f"line {i}" for i in range(120)) + "\n"
        skill = add_reference(root, content)
        errors, warnings = check_top100_contract(root, skill)
        assert not errors
        assert any("preview exception declared" in warning for warning in warnings)


if __name__ == "__main__":
    test_long_skill_requires_decision_and_execution_surface_in_first_100_lines()
    test_long_skill_passes_when_boundary_workflow_and_rules_are_early()
    test_long_supporting_markdown_without_preview_fails()
    test_long_supporting_markdown_passes_with_heading_derived_contents()
    test_long_supporting_markdown_rejects_stale_contents()
    test_long_supporting_markdown_allows_explicit_exception_with_warning()
    print("ok")
