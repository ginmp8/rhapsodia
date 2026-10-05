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


def test_long_supporting_markdown_without_preview_summary_warns() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = make_long_skill(Path(td), early_control=True)
        refs = root / "references"
        refs.mkdir()
        ref = refs / "detail.md"
        ref.write_text("# Detail\n\n" + "\n".join(f"line {i}" for i in range(120)) + "\n", encoding="utf-8")
        skill = root / "SKILL.md"
        skill.write_text(skill.read_text(encoding="utf-8") + "\n[Detail](references/detail.md)\n", encoding="utf-8")
        _errors, warnings = check_top100_contract(root, skill)
        assert any("early summary/index" in warning for warning in warnings)


if __name__ == "__main__":
    test_long_skill_requires_decision_and_execution_surface_in_first_100_lines()
    test_long_skill_passes_when_boundary_workflow_and_rules_are_early()
    test_long_supporting_markdown_without_preview_summary_warns()
    print("ok")
