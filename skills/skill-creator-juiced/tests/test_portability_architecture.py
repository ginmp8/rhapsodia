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


if __name__ == "__main__":
    test_portability_mode_validates_all_default_hosts()
    test_creator_owns_portability_transformation_not_a_third_specialist()
    print("ok")
