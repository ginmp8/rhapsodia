from __future__ import annotations

import importlib.util
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_skill_improver_package.py"

spec = importlib.util.spec_from_file_location("skill_improver_validator", VALIDATOR)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def validate(root: Path) -> list[str]:
    return module.validate_command_evaluator_examples(root)


def copy_skill() -> tuple[tempfile.TemporaryDirectory, Path]:
    td = tempfile.TemporaryDirectory()
    target = Path(td.name) / "skill-improver"
    shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
    return td, target


def test_package_owned_evaluator_example_uses_one_existing_canonical_path():
    assert validate(ROOT) == []


def test_missing_package_owned_evaluator_is_rejected():
    td, target = copy_skill()
    try:
        sample = target / "examples" / "sample-run.md"
        text = sample.read_text(encoding="utf-8").replace(
            "<SKILL_IMPROVER_ROOT>/examples/eval_skill.py",
            "<SKILL_IMPROVER_ROOT>/examples/missing_eval.py",
        )
        sample.write_text(text, encoding="utf-8")
        errors = validate(target)
        assert any("evaluator file does not exist" in error for error in errors)
    finally:
        td.cleanup()


def test_evaluator_and_benchmark_lock_must_match():
    td, target = copy_skill()
    try:
        sample = target / "examples" / "sample-run.md"
        text = sample.read_text(encoding="utf-8").replace(
            "--benchmark-lock-path <SKILL_IMPROVER_ROOT>/examples/eval_skill.py",
            "--benchmark-lock-path <SKILL_IMPROVER_ROOT>/scripts/static_skill_score.py",
            1,
        )
        sample.write_text(text, encoding="utf-8")
        errors = validate(target)
        assert any("evaluator path and benchmark lock differ" in error for error in errors)
    finally:
        td.cleanup()


def test_relative_package_evaluator_path_is_rejected():
    td, target = copy_skill()
    try:
        sample = target / "examples" / "sample-run.md"
        text = sample.read_text(encoding="utf-8").replace(
            "<SKILL_IMPROVER_ROOT>/examples/eval_skill.py",
            "../../evals/eval_skill.py",
        )
        sample.write_text(text, encoding="utf-8")
        errors = validate(target)
        assert any("must use <SKILL_IMPROVER_ROOT>/" in error for error in errors)
    finally:
        td.cleanup()
