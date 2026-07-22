from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from test_board_contract import build_board  # noqa: E402


def load_script(name: str):
    path = SCRIPTS / name
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_scaffold_rejects_destination_outside_authorized_root(tmp_path: Path):
    writer = load_script("write_artifact_scaffold.py")
    outside = tmp_path / "outside" / "implementation-notes.md"
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    assert writer.main([str(outside), "--allowed-root", str(allowed)]) == 1
    assert not outside.exists()


def test_scaffold_allows_canonical_board_destination(tmp_path: Path):
    root, spec_id = build_board(tmp_path)
    writer = load_script("write_artifact_scaffold.py")
    destination = root / "specs" / spec_id / "implementation-notes.md"
    assert writer.main([str(destination), "--board-root", str(root)]) == 0
    assert destination.is_file()


def test_scaffold_requires_explicit_root_for_adhoc_docs(tmp_path: Path):
    writer = load_script("write_artifact_scaffold.py")
    destination = tmp_path / "docs" / "implementation-notes.md"
    assert writer.main([str(destination)]) == 1
    assert writer.main([str(destination), "--allowed-root", str(tmp_path)]) == 0


def test_scaffold_rejects_symlink_escape(tmp_path: Path):
    writer = load_script("write_artifact_scaffold.py")
    allowed = tmp_path / "allowed"
    outside = tmp_path / "outside"
    allowed.mkdir()
    outside.mkdir()
    link = allowed / "linked"
    link.symlink_to(outside, target_is_directory=True)
    destination = link / "implementation-notes.md"
    assert writer.main([str(destination), "--allowed-root", str(allowed)]) == 1
    assert not (outside / "implementation-notes.md").exists()


def test_package_validator_rejects_sensitive_content_in_neutral_name(tmp_path: Path):
    validator = load_script("validate_skill_package.py")
    target = tmp_path / "magia-copy"
    source = Path(__file__).resolve().parents[1]
    import shutil
    shutil.copytree(source, target, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
    sensitive = "OPENAI_" + "API_KEY=" + "sk-" + ("A" * 32)
    (target / "assets" / "sample-data.txt").write_text(sensitive + "\n", encoding="utf-8")
    result = validator.validate_target(target)
    assert result["status"] == "fail"
    assert any("sensitive content" in error for error in result["errors"])


def test_package_validator_allows_explicitly_redacted_example(tmp_path: Path):
    scanner = load_script("security_scan.py")
    content = ("OPENAI_" + "API_KEY=REDACTED_EXAMPLE_VALUE").encode()
    assert scanner.scan_bytes(content, label="example.txt") == []


def test_security_scan_does_not_hide_real_secret_when_comment_mentions_example():
    scanner = load_script("security_scan.py")
    content = ("OPENAI_" + "API_KEY=" + "sk-" + ("C" * 32) + " # example production value").encode()
    findings = scanner.scan_bytes(content, label="commented.txt")
    assert any("sensitive content" in finding for finding in findings)


def test_security_scan_fails_closed_for_oversized_or_binary_content():
    scanner = load_script("security_scan.py")
    oversized = b"A" * (scanner.MAX_SCAN_BYTES + 1)
    assert any("exceeds scan limit" in finding for finding in scanner.scan_bytes(oversized, label="large.bin"))
    assert any("binary" in finding for finding in scanner.scan_bytes(b"safe\x00payload", label="binary.bin"))


def test_package_validator_fails_closed_for_unscannable_content(tmp_path: Path):
    import shutil

    validator = load_script("validate_skill_package.py")
    scanner = load_script("security_scan.py")
    source = Path(__file__).resolve().parents[1]

    oversized_target = tmp_path / "magia-oversized"
    shutil.copytree(source, oversized_target, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
    (oversized_target / "assets" / "large.dat").write_bytes(b"A" * (scanner.MAX_SCAN_BYTES + 1))
    oversized_result = validator.validate_target(oversized_target)
    assert oversized_result["status"] == "fail"
    assert any("exceeds scan limit" in error for error in oversized_result["errors"])

    binary_target = tmp_path / "magia-binary"
    shutil.copytree(source, binary_target, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
    (binary_target / "assets" / "binary.dat").write_bytes(b"safe\x00payload")
    binary_result = validator.validate_target(binary_target)
    assert binary_result["status"] == "fail"
    assert any("binary content" in error for error in binary_result["errors"])


def test_zip_validator_rejects_sensitive_content_in_neutral_member(tmp_path: Path):
    import zipfile
    validator = load_script("validate_skill_package.py")
    archive_path = tmp_path / "skill.zip"
    sensitive = "OPENAI_" + "API_KEY=" + "sk-" + ("B" * 32)
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("magia/assets/sample-data.txt", sensitive)
    result = validator.validate_zip(archive_path)
    assert result["status"] == "fail"
    assert any("sensitive content" in error for error in result["errors"])


def test_package_validator_rejects_symlink(tmp_path: Path):
    scanner = load_script("security_scan.py")
    target = tmp_path / "target"
    target.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("safe\n", encoding="utf-8")
    (target / "linked.txt").symlink_to(outside)
    assert any("symlink" in finding for finding in scanner.scan_tree(target))


def test_package_validation_ignores_only_known_generated_artifacts(tmp_path: Path):
    import shutil

    validator = load_script("validate_skill_package.py")
    source = Path(__file__).resolve().parents[1]
    target = tmp_path / "magia-generated-artifacts"
    shutil.copytree(source, target, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache", ".coverage"))
    (target / ".coverage").write_bytes(b"coverage\x00database")
    cache = target / "scripts" / "__pycache__"
    cache.mkdir()
    (cache / "generated.pyc").write_bytes(b"python\x00bytecode")

    result = validator.validate_target(target)
    assert result["status"] == "pass"


def test_package_validation_rejects_sensitive_eligible_filename(tmp_path: Path):
    import shutil

    validator = load_script("validate_skill_package.py")
    source = Path(__file__).resolve().parents[1]
    target = tmp_path / "magia-sensitive-name"
    shutil.copytree(source, target, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache", ".coverage"))
    (target / "assets" / "credentials.txt").write_text("redacted\n", encoding="utf-8")

    result = validator.validate_target(target)
    assert result["status"] == "fail"
    assert any("secret-like file name" in error for error in result["errors"])


def test_packager_succeeds_after_tests_create_cache_artifacts(tmp_path: Path):
    import shutil
    import zipfile

    packager = load_script("package_skill.py")
    source = Path(__file__).resolve().parents[1]
    target = tmp_path / "magia-after-tests"
    shutil.copytree(source, target, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache", ".coverage"))
    (target / ".coverage").write_bytes(b"coverage\x00database")
    cache = target / "tests" / "__pycache__"
    cache.mkdir()
    (cache / "test.pyc").write_bytes(b"python\x00bytecode")
    output = tmp_path / "skill.zip"
    runner = load_script("run_test_suite.py")
    manifest, digest = runner.suite_manifest(target)
    report_path = tmp_path / "magia-test-report.json"
    report_path.write_text(
        __import__("json").dumps({
            "kind": runner.REPORT_KIND,
            "status": "pass",
            "root": str(target),
            "suite_files": manifest,
            "suite_digest": digest,
            "test_count": 1,
            "command": ["supplied-test-evidence"],
            "return_code": 0,
            "errors": [],
        }) + "\n",
        encoding="utf-8",
    )

    assert packager.main([
        "--target", str(target), "--output", str(output), "--validate",
        "--test-report", str(report_path),
    ]) == 0
    with zipfile.ZipFile(output) as archive:
        names = archive.namelist()
    assert not any("__pycache__" in name for name in names)
    assert not any(name.endswith("/.coverage") or name.endswith(".coverage") for name in names)
