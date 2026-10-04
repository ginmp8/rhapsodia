from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_portability.py"
QUALITY_GATE = ROOT / "scripts" / "juiced_quality_gate.py"


def run_validator(target: Path, hosts: str, surfaces: str = "") -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    cmd = [sys.executable, str(VALIDATOR), str(target), "--hosts", hosts]
    if surfaces:
        cmd.extend(["--surfaces", surfaces])
    return subprocess.run(cmd, capture_output=True, text=True, env=env)


def run_quality(target: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [sys.executable, str(QUALITY_GATE), str(target), "--profile", "portable"],
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
            "portable-core", "openai", "codex", "claude", "copilot", "cursor"
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


def test_distribution_surfaces_map_to_semantic_profiles_without_forks() -> None:
    with tempfile.TemporaryDirectory() as td:
        skill = make_skill(Path(td))
        result = run_validator(skill, "portable-core", "copilot-vscode,copilot-visual-studio")
        assert result.returncode == 0, result.stderr or result.stdout
        report = json.loads(result.stdout)
        assert "copilot" in report["resolved_hosts"]
        assert report["surface_results"]["copilot-vscode"]["semantic_profile"] == "copilot"
        assert report["surface_results"]["copilot-visual-studio"]["semantic_profile"] == "copilot"
        assert report["surface_results"]["copilot-vscode"]["runtime_verified"] is False


def test_host_specific_frontmatter_is_rejected_from_portable_core() -> None:
    with tempfile.TemporaryDirectory() as td:
        skill = make_skill(Path(td))
        path = skill / "SKILL.md"
        text = path.read_text(encoding="utf-8").replace(
            "description: Portable demo used to validate multi-host profiles.\n",
            "description: Portable demo used to validate multi-host profiles.\npaths: src/**\n",
        )
        path.write_text(text, encoding="utf-8")
        result = run_validator(skill, "all")
        assert result.returncode == 1, result.stdout
        report = json.loads(result.stdout)
        codes = {item.get("code") for item in report.get("errors", [])}
        assert "HOST_EXTENSION_IN_CORE" in codes
        assert "PORTABLE_CORE" in codes


def test_frontmatter_parser_fails_closed_on_unsupported_nested_yaml() -> None:
    with tempfile.TemporaryDirectory() as td:
        skill = make_skill(Path(td))
        (skill / "SKILL.md").write_text(
            "---\nname: demo-skill\ndescription: Portable demo.\nmetadata:\n    nested: value\n---\n\n# Demo\n",
            encoding="utf-8",
        )
        result = run_validator(skill, "portable-core")
        assert result.returncode == 1, result.stdout
        report = json.loads(result.stdout)
        assert any(
            "metadata entries must use exactly two spaces" in item.get("evidence", "")
            for item in report.get("errors", [])
        )


def test_validator_has_no_external_python_dependency_warning() -> None:
    result = run_validator(ROOT, "all", "all")
    assert result.returncode == 0, result.stderr or result.stdout
    report = json.loads(result.stdout)
    assert not any(item.get("code") == "PYTHON_EXTERNAL_DEPENDENCY" for item in report.get("warnings", []))


def test_quality_gate_warns_when_reference_is_hidden_from_skill_control_plane() -> None:
    with tempfile.TemporaryDirectory() as td:
        skill = make_skill(Path(td))
        refs = skill / "references"
        refs.mkdir()
        (refs / "hidden.md").write_text("# Hidden\n", encoding="utf-8")
        result = run_quality(skill)
        report = json.loads(result.stdout)
        assert any("not directly discoverable" in warning for warning in report.get("warnings", []))


def test_creator_documents_artifact_selection_and_surface_separation() -> None:
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8").lower()
    assert "artifact selection" in text
    assert "distribution surfaces" in text
    assert "copilot-visual-studio" in text
    assert "model-neutral" in text


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
    test_distribution_surfaces_map_to_semantic_profiles_without_forks()
    test_host_specific_frontmatter_is_rejected_from_portable_core()
    test_frontmatter_parser_fails_closed_on_unsupported_nested_yaml()
    test_validator_has_no_external_python_dependency_warning()
    test_quality_gate_warns_when_reference_is_hidden_from_skill_control_plane()
    test_creator_documents_artifact_selection_and_surface_separation()
    test_delegated_authority_boundary_is_explicit()
    print("ok")
