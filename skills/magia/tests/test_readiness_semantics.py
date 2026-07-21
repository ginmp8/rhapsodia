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


def test_readiness_rejects_negated_objective_non_acceptance_and_placeholder_check(tmp_path: Path):
    root, spec_id = build_board(tmp_path)
    package = root / "specs" / spec_id
    (package / "prd.md").write_text(
        "# PRD\n\n"
        "## Objective\n\n"
        "This document intentionally has no concrete objective.\n\n"
        "## Non-Acceptance Notes\n\n"
        "- This is not an acceptance criterion.\n",
        encoding="utf-8",
    )
    (package / "validation.md").write_text(
        "# Validation Plan\n\n## Planned Checks\n\n- manual placeholder with no expected result\n",
        encoding="utf-8",
    )

    readiness = load_script("validate_execution_readiness.py")
    errors = readiness.collect_errors(root, spec_id, "task001")
    assert any("observable objective" in error for error in errors)
    assert any("acceptance criterion" in error for error in errors)
    assert any("planned validation check" in error for error in errors)


def test_readiness_requires_objective_inside_a_canonical_section(tmp_path: Path):
    root, spec_id = build_board(tmp_path)
    package = root / "specs" / spec_id
    (package / "prd.md").write_text(
        "# PRD\n\n"
        "This paragraph has enough words but is only introductory context.\n\n"
        "## Acceptance Criteria\n\n"
        "- A filtered export contains only the selected columns.\n",
        encoding="utf-8",
    )

    readiness = load_script("validate_execution_readiness.py")
    errors = readiness.collect_errors(root, spec_id, "task001")
    assert any("observable objective" in error for error in errors)


def test_readiness_accepts_manual_check_with_explicit_action_and_expected_outcome(tmp_path: Path):
    root, spec_id = build_board(tmp_path)
    package = root / "specs" / spec_id
    (package / "validation.md").write_text(
        "# Validation Plan\n\n"
        "## Planned Checks\n\n"
        "- Manually export two selected columns and verify that the output contains exactly those columns.\n",
        encoding="utf-8",
    )

    readiness = load_script("validate_execution_readiness.py")
    errors = readiness.collect_errors(root, spec_id, "task001")
    assert not any("planned validation check" in error for error in errors)
