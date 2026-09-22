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
        [sys.executable, str(VALIDATOR), "--target", str(target), "--hosts", hosts],
        capture_output=True,
        text=True,
        env=env,
    )


def make_skill(base: Path) -> Path:
    skill = base / "demo-skill"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: demo-skill\ndescription: Portable demo used to validate multi-host profiles.\n---\n\n# Demo\n",
        encoding="utf-8",
    )
    return skill


def test_all_profiles_include_codex() -> None:
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
        assert report["host_results"]["codex"]["status"] == "pass"
        skill = make_skill(Path(td) / "private")
        (skill / "notes.md").write_text("Use " + "functions" + ".exec directly.\n", encoding="utf-8")
        private_report = json.loads(run_validator(skill, "portable-core").stdout)
        assert any(item.get("code") == "HOST_PRIVATE_CORE" for item in private_report["errors"])


def test_complete_optimization_contract_requires_default_multi_host_gate() -> None:
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    assert "DEFAULT_MULTI_HOSTS" in text
    assert "portable-core,openai,codex,claude,copilot,cursor" in text
    assert "external-untrusted-skill" in text
    assert "references/external-skill-intake.md" in text


if __name__ == "__main__":
    test_all_profiles_include_codex()
    test_complete_optimization_contract_requires_default_multi_host_gate()
    print("ok")
