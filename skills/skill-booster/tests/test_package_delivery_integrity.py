from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "package_skill.py"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, env=env)


def make_skill(base: Path, *, valid: bool = True) -> Path:
    skill = base / "demo-skill"
    skill.mkdir()
    description = (
        "Use when a deterministic demo skill is needed to verify packaging behavior and delivery integrity."
        if valid
        else ""
    )
    (skill / "SKILL.md").write_text(
        f"---\nname: demo-skill\ndescription: {description}\n---\n\n# Demo\n\n## Workflow\nRun.\n\n## Output contract\nReturn.\n\n## Stop conditions\nStop on error.\n",
        encoding="utf-8",
    )
    return skill


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_validation_failure_preserves_last_good_package_and_receipt() -> None:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        skill = make_skill(base, valid=False)
        output = base / "skill.zip"
        report = base / "package-receipt.json"
        output.write_bytes(b"last-good-package")
        report.write_text('{"status":"pass","last_good":true}\n', encoding="utf-8")
        old_output = output.read_bytes()
        old_report = report.read_bytes()

        result = run("--target", str(skill), "--output", str(output), "--report", str(report))

        assert result.returncode == 1
        failure = json.loads(result.stdout)
        assert failure["status"] == "fail"
        assert failure["stage"] == "validate"
        assert output.read_bytes() == old_output
        assert report.read_bytes() == old_report


def test_package_and_receipt_exact_alias_fails_closed() -> None:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        skill = make_skill(base)
        output = base / "skill.zip"
        output.write_bytes(b"last-good-package")
        old_output = output.read_bytes()

        result = run("--target", str(skill), "--output", str(output), "--report", str(output))

        assert result.returncode == 1
        failure = json.loads(result.stdout)
        assert failure["stage"] == "preflight"
        assert failure["code"] == "OUTPUT_REPORT_ALIAS"
        assert output.read_bytes() == old_output


def test_package_and_receipt_hardlink_alias_fails_closed() -> None:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        skill = make_skill(base)
        output = base / "skill.zip"
        report = base / "package-receipt.json"
        output.write_bytes(b"last-good-package")
        try:
            os.link(output, report)
        except OSError:
            return
        old_output = output.read_bytes()

        result = run("--target", str(skill), "--output", str(output), "--report", str(report))

        assert result.returncode == 1
        failure = json.loads(result.stdout)
        assert failure["stage"] == "preflight"
        assert failure["code"] == "OUTPUT_REPORT_ALIAS"
        assert output.read_bytes() == old_output
        assert report.read_bytes() == old_output


def test_success_receipt_matches_committed_archive() -> None:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        skill = make_skill(base)
        output = base / "skill.zip"
        report = base / "package-receipt.json"

        result = run("--target", str(skill), "--output", str(output), "--report", str(report))

        assert result.returncode == 0, result.stderr or result.stdout
        receipt = json.loads(report.read_text(encoding="utf-8"))
        assert receipt["status"] == "pass"
        assert receipt["stage"] == "committed"
        assert receipt["receipt_version"] == 2
        assert receipt["archive_sha256"] == sha256(output)
        assert receipt["last_good_preserved_on_failure"] is True
        with zipfile.ZipFile(output, "r") as zf:
            assert zf.testzip() is None
            assert "demo-skill/SKILL.md" in zf.namelist()


def test_commit_failure_restores_last_good_and_preserves_recovery() -> None:
    import importlib.util

    spec = importlib.util.spec_from_file_location("skill_booster_packager", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        skill = make_skill(base)
        output = base / "skill.zip"
        report = base / "package-receipt.json"
        output.write_bytes(b"last-good-package")
        report.write_text('{"status":"pass","last_good":true}\n', encoding="utf-8")
        old_output = output.read_bytes()
        old_report = report.read_bytes()
        real_replace = module.os.replace

        def fail_report_commit(src, dst):
            src_path = Path(src)
            dst_path = Path(dst)
            if dst_path == report and src_path.name.startswith(f".{report.name}.") and src_path.suffix == ".tmp":
                raise OSError("simulated report commit failure")
            return real_replace(src, dst)

        module.os.replace = fail_report_commit
        try:
            result = module.package(skill, output, report)
        finally:
            module.os.replace = real_replace

        assert result["status"] == "fail"
        assert result["stage"] == "commit"
        assert output.read_bytes() == old_output
        assert report.read_bytes() == old_report
        assert result["recovery"]
        for item in result["recovery"]:
            assert Path(item["preserved_at"]).exists(), item


if __name__ == "__main__":
    test_validation_failure_preserves_last_good_package_and_receipt()
    test_package_and_receipt_exact_alias_fails_closed()
    test_package_and_receipt_hardlink_alias_fails_closed()
    test_success_receipt_matches_committed_archive()
    test_commit_failure_restores_last_good_and_preserves_recovery()
    print("ok")
