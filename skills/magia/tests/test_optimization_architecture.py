from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def run_script(script: str, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script), *args],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


def digest_tree(root: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        values[path.relative_to(root).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return values


def test_validation_selector_escalates_quick_migration_to_governed(tmp_path: Path):
    source = tmp_path / "change.json"
    source.write_text(
        json.dumps({"requested_profile": "quick", "changed_files": ["db/migrations/001_add.sql"]}),
        encoding="utf-8",
    )
    result = run_script("select_validation.py", "--input", str(source))
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["profile"] == "governed"
    assert "migration_validation" in payload["required_checks"]
    assert "rollback_check" in payload["required_checks"]
    assert payload["run_state_required"] is True


def test_validation_selector_keeps_localized_change_quick(tmp_path: Path):
    source = tmp_path / "change.json"
    source.write_text(
        json.dumps({"requested_profile": "quick", "changed_files": ["docs/guide.md"]}),
        encoding="utf-8",
    )
    result = run_script("select_validation.py", "--input", str(source))
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["profile"] == "quick"
    assert payload["required_checks"] == ["targeted_test_or_static_check"]


def test_run_state_resumes_when_tracked_file_is_unchanged(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    tracked = repo / "source.txt"
    tracked.write_text("stable\n", encoding="utf-8")
    state = tmp_path / "state.json"
    init = run_script(
        "run_state.py", "init", "--state", str(state), "--run-id", "run-1",
        "--mode", "adhoc", "--profile", "standard", "--repo-root", str(repo),
        "--scope", "source.txt", "--track", "source.txt",
    )
    assert init.returncode == 0, init.stderr
    resume = run_script("run_state.py", "resume", "--state", str(state))
    assert resume.returncode == 0
    assert json.loads(resume.stdout)["status"] == "resume_allowed"


def test_run_state_fails_closed_on_repository_drift(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    tracked = repo / "source.txt"
    tracked.write_text("before\n", encoding="utf-8")
    state = tmp_path / "state.json"
    init = run_script(
        "run_state.py", "init", "--state", str(state), "--run-id", "run-2",
        "--mode", "ralph", "--profile", "governed", "--repo-root", str(repo),
        "--scope", "task001", "--track", "source.txt",
    )
    assert init.returncode == 0
    tracked.write_text("after\n", encoding="utf-8")
    resume = run_script("run_state.py", "resume", "--state", str(state))
    assert resume.returncode == 2
    payload = json.loads(resume.stdout)
    assert payload["status"] == "repository_drift"
    persisted = json.loads(state.read_text(encoding="utf-8"))
    assert persisted["status"] == "blocked"
    assert persisted["pending_step"] == "reinspect_after_drift"


def test_run_state_cancellation_is_terminal(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    state = tmp_path / "state.json"
    assert run_script(
        "run_state.py", "init", "--state", str(state), "--run-id", "run-3",
        "--mode", "adhoc", "--profile", "quick", "--repo-root", str(repo),
        "--scope", "localized",
    ).returncode == 0
    cancelled = run_script("run_state.py", "cancel", "--state", str(state), "--reason", "user stop")
    assert cancelled.returncode == 0
    resume = run_script("run_state.py", "resume", "--state", str(state))
    assert resume.returncode == 2
    assert json.loads(resume.stdout)["status"] == "blocked"


def test_convergence_requires_complete_governed_traceability(tmp_path: Path):
    source = tmp_path / "convergence.json"
    source.write_text(
        json.dumps({
            "profile": "governed",
            "items": [{
                "id": "r1",
                "requirement": "preserve behavior",
                "acceptance_criteria": ["same output"],
                "tasks": ["task001"],
                "changed_files": ["src/core.py"],
                "checks": ["pytest tests/test_core.py"],
                "evidence": ["validation-evidence.md#run-1"],
                "status": "satisfied",
                "notes": "current evidence"
            }]
        }),
        encoding="utf-8",
    )
    result = run_script("validate_convergence.py", "--input", str(source), "--require-complete")
    assert result.returncode == 0, result.stdout
    assert json.loads(result.stdout)["blocking_count"] == 0


def test_convergence_blocks_unverified_item(tmp_path: Path):
    source = tmp_path / "convergence.json"
    source.write_text(
        json.dumps({
            "profile": "standard",
            "items": [{
                "id": "r1", "requirement": "behavior", "acceptance_criteria": [],
                "tasks": [], "changed_files": [], "checks": [], "evidence": [],
                "status": "unverified", "notes": "test unavailable"
            }]
        }),
        encoding="utf-8",
    )
    result = run_script("validate_convergence.py", "--input", str(source), "--require-complete")
    assert result.returncode == 1
    assert json.loads(result.stdout)["blocking_count"] == 1


def test_public_adapter_is_read_only_and_reports_missing_fields(tmp_path: Path):
    source = tmp_path / "spec-kit"
    source.mkdir()
    (source / "spec.md").write_text("# Requirement\n", encoding="utf-8")
    (source / "tasks.md").write_text("- [ ] task001: implement\n", encoding="utf-8")
    before = digest_tree(source)
    output = tmp_path / "normalized.json"
    result = run_script(
        "adapt_public_artifacts.py", "--source", str(source), "--kind", "spec-kit", "--output", str(output)
    )
    assert result.returncode == 0, result.stdout
    assert digest_tree(source) == before
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["read_only"] is True
    assert "design" in payload["missing_fields"]
    assert payload["task_summary"]["total"] == 1


def test_public_adapter_rejects_output_inside_source(tmp_path: Path):
    source = tmp_path / "kiro"
    source.mkdir()
    (source / "requirements.md").write_text("# Requirements\n", encoding="utf-8")
    result = run_script(
        "adapt_public_artifacts.py", "--source", str(source), "--kind", "kiro",
        "--output", str(source / "normalized.json"),
    )
    assert result.returncode == 1
    assert "outside the read-only source directory" in result.stdout
