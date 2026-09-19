from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "inspect_repository_context.py"


def run_json(repo: Path) -> dict:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(repo), "--format", "json"],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def test_detects_python_tests_contracts_and_planning(tmp_path: Path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text("print('ok')\n", encoding="utf-8")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_app.py").write_text("def test_ok(): assert True\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
    (tmp_path / "openapi.yaml").write_text("openapi: 3.0.0\n", encoding="utf-8")
    (tmp_path / "tasks.md").write_text("# Tasks\n", encoding="utf-8")

    data = run_json(tmp_path)

    assert data["read_only"] is True
    assert data["commands_executed"] == []
    assert "python/pyproject" in data["build_systems"]
    assert "openapi.yaml" in data["contract_signals"]
    assert "tasks.md" in data["planning_markers"]
    assert any(item["name"] == "python" for item in data["languages"])


def test_detects_dotnet_and_node_metadata(tmp_path: Path):
    (tmp_path / "App.csproj").write_text("<Project />\n", encoding="utf-8")
    (tmp_path / "Program.cs").write_text("class Program {}\n", encoding="utf-8")
    (tmp_path / "package.json").write_text('{"scripts":{"test":"x","lint":"y"}}', encoding="utf-8")

    data = run_json(tmp_path)

    assert "dotnet" in data["build_systems"]
    assert "node/package-json" in data["build_systems"]
    assert data["package_scripts"]["package.json"] == ["lint", "test"]
    assert "Program.cs" in data["entrypoint_signals"]


def test_output_is_deterministic(tmp_path: Path):
    (tmp_path / "b.py").write_text("", encoding="utf-8")
    (tmp_path / "a.py").write_text("", encoding="utf-8")
    assert run_json(tmp_path) == run_json(tmp_path)


def test_rejects_symlink_root(tmp_path: Path):
    target = tmp_path / "real"
    target.mkdir()
    link = tmp_path / "link"
    try:
        link.symlink_to(target, target_is_directory=True)
    except OSError:
        pytest.skip("symlink creation unavailable")
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(link)],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "must not be a symlink" in result.stderr
