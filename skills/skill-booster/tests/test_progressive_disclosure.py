from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_skill_booster.py"


def run(target: Path) -> dict:
    result = subprocess.run([sys.executable, str(SCRIPT), "--target", str(target)], capture_output=True, text=True)
    assert result.stdout
    return json.loads(result.stdout)


def make_skill(base: Path, body: str) -> Path:
    root = base / "demo-skill"
    root.mkdir(parents=True)
    (root / "SKILL.md").write_text(
        "---\nname: demo-skill\ndescription: Demo skill with enough activation context for validation coverage.\n---\n\n" + body,
        encoding="utf-8",
    )
    return root


def test_large_control_plane_emits_progressive_disclosure_warning(tmp_path: Path) -> None:
    root = make_skill(tmp_path, "\n".join(f"line {i}" for i in range(510)))
    report = run(root)
    assert any(d.get("code") == "PROGRESSIVE_DISCLOSURE_SIZE" for d in report["diagnostics"])


def test_deep_reference_chain_emits_warning(tmp_path: Path) -> None:
    root = make_skill(tmp_path, "# Demo\n\n[First](references/first.md)\n")
    refs = root / "references"
    refs.mkdir()
    (refs / "first.md").write_text("[Second](second.md)\n", encoding="utf-8")
    (refs / "second.md").write_text("# Second\n", encoding="utf-8")
    report = run(root)
    assert any(d.get("code") == "PROGRESSIVE_DISCLOSURE_DEPTH" for d in report["diagnostics"])
