from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_skill_version.py"


def cli(skill: Path, baseline: Path | None = None):
    args = [sys.executable, "-B", str(SCRIPT), "--target", str(skill)]
    if baseline:
        args.extend(["--baseline", str(baseline)])
    proc = subprocess.run(args, capture_output=True, text=True, check=False)
    return proc.returncode, json.loads(proc.stdout)


def sample(tmp_path: Path, name: str, version: str = "1.2.3") -> Path:
    skill = tmp_path / name
    skill.mkdir()
    (skill / "SKILL.md").write_text("# Example\n", encoding="utf-8")
    (skill / "VERSION").write_text(version + "\n", encoding="ascii")
    (skill / "CHANGELOG.md").write_text(f"# Changelog\n\n## [{version}]\n\n- Tracked release.\n", encoding="utf-8")
    return skill


def test_version_and_changelog_valid(tmp_path: Path):
    skill = sample(tmp_path, "valid")
    code, report = cli(skill)
    assert code == 0 and report["version"] == "1.2.3"


def test_missing_version_fails(tmp_path: Path):
    skill = sample(tmp_path, "missing")
    (skill / "VERSION").unlink()
    code, report = cli(skill)
    assert code != 0 and "VERSION" in str(report["errors"])


def test_malformed_semver_fails(tmp_path: Path):
    for bad in ("v1.2.3", "01.2.3", "1.2.3-rc.01", "1.2.3\n2.0.0"):
        skill = sample(tmp_path, "bad" + str(len(list(tmp_path.iterdir()))))
        (skill / "VERSION").write_text(bad + "\n", encoding="ascii")
        code, report = cli(skill)
        assert code != 0 and report["errors"]


def test_changelog_missing_mismatched_or_duplicate_fails(tmp_path: Path):
    skill = sample(tmp_path, "changelog")
    (skill / "CHANGELOG.md").unlink()
    assert cli(skill)[0] != 0
    (skill / "CHANGELOG.md").write_text("## [1.2.2]\n", encoding="utf-8")
    assert cli(skill)[0] != 0
    (skill / "CHANGELOG.md").write_text("## [1.2.3]\n\n## [1.2.3]\n", encoding="utf-8")
    assert cli(skill)[0] != 0


def test_optional_release_metadata_is_kept_in_sync(tmp_path: Path):
    skill = sample(tmp_path, "manifest")
    (skill / "release.json").write_text('{"version":"1.2.2"}', encoding="utf-8")
    assert cli(skill)[0] != 0
    (skill / "release.json").write_text('{"version":"1.2.3"}', encoding="utf-8")
    (skill / "RELEASE_NOTES.md").write_text("# Example 1.2.2\n", encoding="utf-8")
    assert cli(skill)[0] != 0
    (skill / "RELEASE_NOTES.md").write_text("# Example 1.2.3\n", encoding="utf-8")
    assert cli(skill)[0] == 0


def test_unchanged_release_with_modified_package_is_rejected(tmp_path: Path):
    old = sample(tmp_path, "baseline")
    candidate = sample(tmp_path, "candidate")
    assert cli(candidate, old)[0] == 0
    (candidate / "SKILL.md").write_text("# Modified\n", encoding="utf-8")
    code, report = cli(candidate, old)
    assert code != 0 and "did not advance" in str(report["errors"])


def test_monotonic_release_and_prerelease_order(tmp_path: Path):
    old = sample(tmp_path, "previous", "1.2.3-rc.2")
    candidate = sample(tmp_path, "new", "1.2.3-rc.10")
    assert cli(candidate, old)[0] == 0
    (candidate / "VERSION").write_text("1.2.3-rc.1\n", encoding="ascii")
    (candidate / "CHANGELOG.md").write_text("## [1.2.3-rc.1]\n", encoding="utf-8")
    assert cli(candidate, old)[0] != 0


def test_versionless_baseline_is_explicit_tracking_adoption(tmp_path: Path):
    old = sample(tmp_path, "unversioned")
    (old / "VERSION").unlink()
    candidate = sample(tmp_path, "adopted", "0.1.0")
    code, report = cli(candidate, old)
    assert code == 0 and report["baseline_version"] is None
    assert any("first tracked" in message for message in report["warnings"])


def test_baseline_cannot_point_to_candidate(tmp_path: Path):
    candidate = sample(tmp_path, "same")
    code, report = cli(candidate, candidate)
    assert code != 0 and "separate" in str(report["errors"])
