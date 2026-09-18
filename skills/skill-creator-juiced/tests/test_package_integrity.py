from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
sys.dont_write_bytecode = True
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "package_skill.py"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)


def make_skill(base: Path, *, valid: bool = True) -> Path:
    skill = base / "demo-skill"
    skill.mkdir()
    description = "Deterministic demo package used to test delivery integrity."
    name = "demo-skill" if valid else "wrong-name"
    (skill / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: {description}\n---\n\n# Demo\n\n## Workflow\n\nDo the deterministic thing.\n\n## Output Contract\n\nReturn the result.\n\n## Stop Conditions\n\nStop on invalid input.\n",
        encoding="utf-8",
    )
    return skill


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_stdout(result: subprocess.CompletedProcess[str]) -> dict:
    start = result.stdout.find("{")
    assert start >= 0, result.stdout
    return json.loads(result.stdout[start:])


def test_package_and_receipt_alias_is_rejected_without_mutation() -> None:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        skill = make_skill(base)
        output = base / "skill.zip"
        receipt = base / "receipt.json"
        output.write_bytes(b"last-good")
        try:
            os.link(output, receipt)
        except OSError:
            return
        before = output.read_bytes()
        result = run("--target", str(skill), "--output", str(output), "--json-output", str(receipt), "--validate")
        assert result.returncode == 1
        report = parse_stdout(result)
        assert report["stage"] == "preflight"
        assert report["code"] == "output/target-alias"
        assert output.read_bytes() == before
        assert receipt.read_bytes() == before


def test_symlink_output_resolving_to_non_zip_is_rejected() -> None:
    if not hasattr(os, "symlink"):
        return
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        skill = make_skill(base)
        marker = base / "marker.env"
        marker.write_bytes(b"keep-me")
        output = base / "skill.zip"
        try:
            output.symlink_to(marker)
        except OSError:
            return
        result = run("--target", str(skill), "--output", str(output), "--validate")
        assert result.returncode == 1
        report = parse_stdout(result)
        assert report["code"] == "output/resolved-extension"
        assert marker.read_bytes() == b"keep-me"
        assert output.is_symlink()


def test_validation_failure_preserves_existing_package_and_receipt() -> None:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        skill = make_skill(base, valid=False)
        output = base / "skill.zip"
        receipt = base / "receipt.json"
        output.write_bytes(b"old-package")
        receipt.write_text('{"status":"pass","old":true}\n', encoding="utf-8")
        old_output = output.read_bytes()
        old_receipt = receipt.read_bytes()
        result = run("--target", str(skill), "--output", str(output), "--json-output", str(receipt), "--validate")
        assert result.returncode == 1
        report = parse_stdout(result)
        assert report["stage"] == "validation"
        assert output.read_bytes() == old_output
        assert receipt.read_bytes() == old_receipt



def test_scaffold_marker_is_rejected() -> None:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        skill = make_skill(base)
        marker = "TO" + "DO: replace this"
        (skill / "SKILL.md").write_text(
            f'---\nname: demo-skill\ndescription: "{marker}"\n---\n\n# Demo\n\n## Workflow\n\nDo x.\n\n## Output Contract\n\nReturn x.\n\n## Stop Conditions\n\nStop.\n',
            encoding="utf-8",
        )
        result = run("--target", str(skill), "--output", str(base / "skill.zip"), "--validate")
        assert result.returncode == 1
        report = parse_stdout(result)
        assert report["stage"] == "validation"
        assert any("residual scaffold marker" in error for error in report["folder"]["errors"])

def test_output_inside_frozen_target_is_rejected() -> None:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        skill = make_skill(base)
        output = skill / "skill.zip"
        result = run("--target", str(skill), "--output", str(output), "--validate")
        assert result.returncode == 1
        report = parse_stdout(result)
        assert report["code"] == "output/inside-target"
        assert not output.exists()


def test_success_receipt_matches_committed_package() -> None:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        skill = make_skill(base)
        output = base / "skill.zip"
        receipt = base / "receipt.json"
        result = run("--target", str(skill), "--output", str(output), "--json-output", str(receipt), "--validate")
        assert result.returncode == 0, result.stderr or result.stdout
        persisted = json.loads(receipt.read_text(encoding="utf-8"))
        assert persisted["receipt_version"] == 2
        assert persisted["status"] == "pass"
        assert persisted["stage"] == "committed"
        assert persisted["package"]["sha256"] == sha256(output)
        assert persisted["archive"]["sha256"] == sha256(output)
        assert persisted["package"]["source_tree_sha256"]
        assert persisted["delivery"]["last_good_preserved_on_failure"] is True
        assert not list(base.glob(".*.juiced-backup-*"))


def test_commit_failure_restores_last_good_and_reports_recovery() -> None:
    scripts = str(ROOT / "scripts")
    sys.path.insert(0, scripts)
    try:
        spec = importlib.util.spec_from_file_location("juiced_packager", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(scripts)

    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        output = base / "skill.zip"
        receipt = base / "receipt.json"
        output.write_bytes(b"old-package")
        receipt.write_bytes(b"old-receipt")
        staged_output = base / ".staged-package"
        staged_receipt = base / ".staged-receipt"
        staged_output.write_bytes(b"new-package")
        staged_receipt.write_bytes(b"new-receipt")

        original_replace = module.os.replace
        calls = {"count": 0}

        def fail_fourth(src, dst):
            calls["count"] += 1
            if calls["count"] == 4:
                raise OSError("simulated receipt commit failure")
            return original_replace(src, dst)

        module.os.replace = fail_fourth
        try:
            try:
                module.transactional_commit([(staged_output, output), (staged_receipt, receipt)])
                raise AssertionError("transaction unexpectedly succeeded")
            except RuntimeError as exc:
                payload = json.loads(str(exc))
                assert payload["recovery"]
        finally:
            module.os.replace = original_replace

        assert output.read_bytes() == b"old-package"
        assert receipt.read_bytes() == b"old-receipt"


if __name__ == "__main__":
    test_package_and_receipt_alias_is_rejected_without_mutation()
    test_symlink_output_resolving_to_non_zip_is_rejected()
    test_validation_failure_preserves_existing_package_and_receipt()
    test_scaffold_marker_is_rejected()
    test_output_inside_frozen_target_is_rejected()
    test_success_receipt_matches_committed_package()
    test_commit_failure_restores_last_good_and_reports_recovery()
    print("ok")
