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


def test_validator_rejects_long_skill_when_control_plane_is_after_line_100() -> None:
    with tempfile.TemporaryDirectory() as td:
        report = run(make_skill(Path(td), early_control=False))
        assert any(d.get("code") == "TOP100_CONTROL_PLANE" for d in report["diagnostics"])
        assert report["status"] == "fail"


def test_validator_accepts_top100_control_plane_and_warns_on_long_reference_without_preview() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = make_skill(Path(td), early_control=True)
        refs = root / "references"
        refs.mkdir()
        (refs / "detail.md").write_text("# Detail\n\n" + "\n".join(f"line {i}" for i in range(120)) + "\n", encoding="utf-8")
        skill = root / "SKILL.md"
        skill.write_text(skill.read_text(encoding="utf-8") + "\n[Detail](references/detail.md)\n", encoding="utf-8")
        report = run(root)
        assert report["status"] == "pass"
        assert any(d.get("code") == "TOP100_SUPPORT_PREVIEW" for d in report["diagnostics"])


if __name__ == "__main__":
    test_validator_rejects_long_skill_when_control_plane_is_after_line_100()
    test_validator_accepts_top100_control_plane_and_warns_on_long_reference_without_preview()
    print("ok")
