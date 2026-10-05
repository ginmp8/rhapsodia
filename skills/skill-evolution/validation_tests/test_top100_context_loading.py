import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_validator(target: Path):
    proc = subprocess.run(
        [sys.executable, str(target / "scripts/validate_skill_evolution.py"), "--target", str(target)],
        text=True,
        capture_output=True,
        check=False,
    )
    return proc.returncode, json.loads(proc.stdout)


def copy_target(tmp_path: Path) -> Path:
    target = tmp_path / "skill-evolution"
    shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
    return target


def test_context_loading_contract_passes_for_package():
    code, report = run_validator(ROOT)
    assert code == 0
    assert report["status"] == "pass"


def test_validator_rejects_quick_start_displaced_below_top100(tmp_path):
    target = copy_target(tmp_path)
    skill = target / "SKILL.md"
    text = skill.read_text(encoding="utf-8")
    text = text.replace("## Quick-start workflow", "## Deferred workflow", 1)
    skill.write_text(text, encoding="utf-8")

    code, report = run_validator(target)
    assert code == 2
    assert "context:top100:quick-start" in report["errors"]


def test_validator_rejects_missing_long_reference_preview(tmp_path):
    target = copy_target(tmp_path)
    ref = target / "references/evidence-aware-profile.md"
    text = ref.read_text(encoding="utf-8")
    text = text.replace("**Decision impact:**", "**Effect:**", 1)
    ref.write_text(text, encoding="utf-8")

    code, report = run_validator(target)
    assert code == 2
    assert any(error.startswith("context:long-reference-preview:evidence-aware-profile.md:decision-impact") for error in report["errors"])
