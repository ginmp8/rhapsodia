from __future__ import annotations

from pathlib import Path

import pytest

from scripts.normalize_public_artifacts import main, normalize


def test_spec_kit_adapter_is_read_only_and_reports_loss(tmp_path: Path):
    (tmp_path / "spec.md").write_text("# Feature\n### Requirement: Export\n- The system SHALL export CSV\n", encoding="utf-8")
    (tmp_path / "plan.md").write_text("# Plan\n", encoding="utf-8")
    (tmp_path / "tasks.md").write_text("- [ ] Implement export\n", encoding="utf-8")
    before = {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    result = normalize(tmp_path, "spec-kit")
    after = {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    assert result["read_only"] is True
    assert result["source_format"] == "spec-kit"
    assert result["tasks"][0]["completed"] is False
    assert result["lossy_mappings"]
    assert before == after


def test_kiro_bug_adapter_keeps_ears_constraints(tmp_path: Path):
    (tmp_path / "bugfix.md").write_text("## Current Behavior\nWHEN invalid input\nTHE SYSTEM SHALL reject it\n## Unchanged Behavior\n", encoding="utf-8")
    (tmp_path / "design.md").write_text("# Design\n", encoding="utf-8")
    (tmp_path / "tasks.md").write_text("- [x] Reproduce bug\n", encoding="utf-8")
    result = normalize(tmp_path, "kiro")
    assert result["source_format"] == "kiro"
    assert len(result["acceptance_criteria"]) == 2
    assert result["tasks"][0]["completed"] is True


def test_openspec_adapter_preserves_delta_operation(tmp_path: Path):
    (tmp_path / "specs/auth").mkdir(parents=True)
    (tmp_path / "proposal.md").write_text("# Proposal\n", encoding="utf-8")
    (tmp_path / "tasks.md").write_text("- [ ] Implement MFA\n", encoding="utf-8")
    (tmp_path / "specs/auth/spec.md").write_text("## ADDED Requirements\n### Requirement: MFA\n#### Scenario: User enrolls\n", encoding="utf-8")
    result = normalize(tmp_path, "openspec")
    assert result["requirements"][0]["operation"] == "added"
    assert result["delta_operations"][0]["operation"] == "added"


def test_adapter_rejects_output_inside_read_only_source(tmp_path: Path):
    (tmp_path / "spec.md").write_text("# Feature\n", encoding="utf-8")
    (tmp_path / "tasks.md").write_text("- [ ] Execute\n", encoding="utf-8")
    output = tmp_path / "normalized.json"
    assert main(["--source", str(tmp_path), "--format", "spec-kit", "--output", str(output)]) == 1
    assert not output.exists()


def test_adapter_rejects_symlinked_source_file(tmp_path: Path):
    outside = tmp_path.parent / f"{tmp_path.name}-outside.md"
    outside.write_text("# Feature\n", encoding="utf-8")
    (tmp_path / "spec.md").symlink_to(outside)
    (tmp_path / "tasks.md").write_text("- [ ] Execute\n", encoding="utf-8")
    with pytest.raises(ValueError, match="symbolic links"):
        normalize(tmp_path, "spec-kit")
