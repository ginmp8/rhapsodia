from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "inspect_external_skill.py"


def run(target: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run([sys.executable, str(SCRIPT), "--target", str(target)], capture_output=True, text=True, env=env)


def test_clean_external_skill_is_inspected_without_execution() -> None:
    with tempfile.TemporaryDirectory() as td:
        skill = Path(td) / "demo-skill"
        skill.mkdir()
        (skill / "SKILL.md").write_text("---\nname: demo-skill\ndescription: Demo.\n---\n# Demo\n", encoding="utf-8")
        (skill / "run.py").write_text("print('not executed')\n", encoding="utf-8")
        result = run(skill)
        assert result.returncode == 0, result.stderr or result.stdout
        report = json.loads(result.stdout)
        assert report["target_code_executed"] is False
        assert report["executable_surface_count"] == 1
        assert report["decision"] == "pass"
        (skill / "notes.md").write_text("Use " + "functions" + ".exec directly.\n", encoding="utf-8")
        report = json.loads(run(skill).stdout)
        assert any(f["code"] == "HOST_COUPLING" for f in report["findings"])


def test_traversal_zip_fails_closed() -> None:
    with tempfile.TemporaryDirectory() as td:
        archive = Path(td) / "skill.zip"
        with zipfile.ZipFile(archive, "w") as zf:
            zf.writestr("demo-skill/SKILL.md", "---\nname: demo-skill\ndescription: Demo.\n---\n# Demo\n")
            zf.writestr("../escape.sh", "echo bad\n")
        result = run(archive)
        assert result.returncode == 1
        report = json.loads(result.stdout)
        assert report["decision"] == "block"
        assert any(f["code"] == "UNSAFE_ARCHIVE_PATH" for f in report["findings"])


def test_secret_value_is_not_echoed() -> None:
    with tempfile.TemporaryDirectory() as td:
        skill = Path(td) / "demo-skill"
        skill.mkdir()
        (skill / "SKILL.md").write_text("---\nname: demo-skill\ndescription: Demo.\n---\n# Demo\n", encoding="utf-8")
        secret = "super-secret-value-1234567890"
        (skill / "config.txt").write_text(f"api_key={secret}\n", encoding="utf-8")
        result = run(skill)
        assert result.returncode == 1
        assert secret not in result.stdout
        report = json.loads(result.stdout)
        assert any(f["code"] == "POSSIBLE_SECRET_VALUE" for f in report["findings"])


if __name__ == "__main__":
    test_clean_external_skill_is_inspected_without_execution()
    test_traversal_zip_fails_closed()
    test_secret_value_is_not_echoed()
    print("ok")
