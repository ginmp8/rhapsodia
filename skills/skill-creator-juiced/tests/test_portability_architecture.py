from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_portability.py"


def run_validator(target: Path, hosts: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [sys.executable, str(VALIDATOR), str(target), "--hosts", hosts],
        capture_output=True,
        text=True,
        env=env,
    )


def make_skill(base: Path) -> Path:
    skill = base / "demo-skill"
    skill.mkdir()
    (skill / "SKILL.md").write_text(
        "---\nname: demo-skill\ndescription: Portable demo used to validate multi-host profiles.\n---\n\n# Demo\n",
        encoding="utf-8",
    )
    return skill


def test_portability_mode_validates_all_default_hosts() -> None:
    with tempfile.TemporaryDirectory() as td:
        result = run_validator(make_skill(Path(td)), "all")
        assert result.returncode == 0, result.stderr or result.stdout
        report = json.loads(result.stdout)
        assert report["requested_hosts"] == [
            "portable-core",
            "openai",
            "codex",
            "claude",
            "copilot",
            "cursor",
        ]
        assert all(report["host_results"][host]["status"] == "pass" for host in report["requested_hosts"])


def test_creator_owns_portability_transformation_not_a_third_specialist() -> None:
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    assert "PORTABILITY_OWNER" in text
    assert "skill-creator-juiced" in text.lower()
    assert "portable-core,openai,codex,claude,copilot,cursor" in text



def test_portability_validator_rejects_private_core_token_without_self_false_positive() -> None:
    with tempfile.TemporaryDirectory() as td:
        skill = make_skill(Path(td))
        refs = skill / "references"
        refs.mkdir()
        private_token = "functions" + ".exec"
        (refs / "runtime.md").write_text(f"Use {private_token} directly.\n", encoding="utf-8")
        result = run_validator(skill, "all")
        assert result.returncode == 1, result.stdout
        report = json.loads(result.stdout)
        assert any(item.get("code") == "HOST_PRIVATE_CORE" for item in report.get("errors", []))


def test_delegated_authority_boundary_is_explicit() -> None:
    skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    orchestration = (ROOT / "references" / "specialist-orchestration.md").read_text(encoding="utf-8")
    assert "upstream orchestrator" in skill_text.lower()
    assert "final promotion" in skill_text.lower()
    assert "caller remains the global orchestrator" in orchestration.lower()


if __name__ == "__main__":
    test_portability_mode_validates_all_default_hosts()
    test_creator_owns_portability_transformation_not_a_third_specialist()
    test_portability_validator_rejects_private_core_token_without_self_false_positive()
    test_delegated_authority_boundary_is_explicit()
    print("ok")
