from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_skill_booster.py"


def run(target: Path) -> dict:
    result = subprocess.run([sys.executable, str(SCRIPT), "--target", str(target)], capture_output=True, text=True)
    assert result.stdout
    return json.loads(result.stdout)


def make_skill(base: Path, *, early_control: bool) -> Path:
    root = base / "demo-skill"
    root.mkdir()
    early = "## Activation and Routing\nUse when demo work applies.\n\n## Workflow\nDo the work.\n\n## Core Rules\nPreserve evidence.\n" if early_control else "## Notes\nGeneral notes only.\n"
    filler = "\n".join(f"filler {i}" for i in range(120))
    late = "\n## Activation and Routing\nUse when demo work applies.\n\n## Workflow\nDo the work.\n\n## Core Rules\nPreserve evidence.\n"
    (root / "SKILL.md").write_text(
        "---\nname: demo-skill\ndescription: Demo skill used when optimization work applies and not for unrelated work.\n---\n\n# Demo\n\n"
        + early + filler + ("" if early_control else late),
        encoding="utf-8",
    )
    return root


def add_reference(root: Path, content: str) -> None:
    refs = root / "references"
    refs.mkdir(exist_ok=True)
    (refs / "detail.md").write_text(content, encoding="utf-8")
    skill = root / "SKILL.md"
    skill.write_text(skill.read_text(encoding="utf-8") + "\n[Detail](references/detail.md)\n", encoding="utf-8")


def valid_long_reference() -> str:
    filler = "\n".join(f"detail line {i}" for i in range(110))
    return (
        "# Detail\n\n"
        "## At a Glance\n\n"
        "Use this document for detailed behavior.\n\n"
        "## Contents\n\n"
        "- Alpha\n"
        "- Beta\n\n"
        "## Alpha\n\n"
        "```markdown\n## Embedded Example Heading\n```\n\n"
        + filler
        + "\n\n## Beta\n\nFinal details.\n"
    )


def test_validator_rejects_long_skill_when_control_plane_is_after_line_100() -> None:
    with tempfile.TemporaryDirectory() as td:
        report = run(make_skill(Path(td), early_control=False))
        assert any(d.get("code") == "TOP100_CONTROL_PLANE" for d in report["diagnostics"])
        assert report["status"] == "fail"


def test_validator_rejects_long_reference_without_preview() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = make_skill(Path(td), early_control=True)
        add_reference(root, "# Detail\n\n" + "\n".join(f"line {i}" for i in range(120)) + "\n")
        report = run(root)
        assert report["status"] == "fail"
        assert any(d.get("code") == "TOP100_SUPPORT_PREVIEW" for d in report["diagnostics"])


def test_validator_accepts_heading_derived_contents_and_ignores_fenced_headings() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = make_skill(Path(td), early_control=True)
        add_reference(root, valid_long_reference())
        report = run(root)
        assert report["status"] == "pass"
        assert not any(d.get("code") in {"TOP100_SUPPORT_PREVIEW", "TOP100_SUPPORT_CONTENTS_DRIFT"} for d in report["diagnostics"])


def test_validator_rejects_stale_contents_when_h2_headings_change() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = make_skill(Path(td), early_control=True)
        content = valid_long_reference().replace("- Beta\n", "- Old Section\n", 1)
        add_reference(root, content)
        report = run(root)
        assert report["status"] == "fail"
        assert any(d.get("code") == "TOP100_SUPPORT_CONTENTS_DRIFT" for d in report["diagnostics"])


def test_validator_allows_explicit_preview_exception_with_warning() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = make_skill(Path(td), early_control=True)
        content = "# Generated Detail\n\n<!-- context-preview-exception: generated -->\n\n" + "\n".join(f"line {i}" for i in range(120)) + "\n"
        add_reference(root, content)
        report = run(root)
        assert report["status"] == "pass"
        assert any(d.get("code") == "TOP100_SUPPORT_PREVIEW_EXCEPTION" for d in report["diagnostics"])


if __name__ == "__main__":
    test_validator_rejects_long_skill_when_control_plane_is_after_line_100()
    test_validator_rejects_long_reference_without_preview()
    test_validator_accepts_heading_derived_contents_and_ignores_fenced_headings()
    test_validator_rejects_stale_contents_when_h2_headings_change()
    test_validator_allows_explicit_preview_exception_with_warning()
    print("ok")
