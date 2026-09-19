from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "analyze_execution_waves.py"


def run_case(tmp_path: Path, data: dict, *, expect: int = 0) -> dict:
    source = tmp_path / "tasks.json"
    source.write_text(json.dumps(data), encoding="utf-8")
    result = subprocess.run([sys.executable, str(SCRIPT), "--input", str(source)], capture_output=True, text=True)
    assert result.returncode == expect, result.stderr
    return json.loads(result.stdout)


def task(task_id: str, *, depends=None, paths=None, surfaces=None, parallel=True):
    return {
        "id": task_id,
        "depends_on": depends or [],
        "parallel": parallel,
        "write_paths": paths or [],
        "contract_surfaces": surfaces or [],
    }


def test_independent_tasks_form_parallel_wave(tmp_path: Path):
    result = run_case(tmp_path, {"tasks": [task("a", paths=["src/a.py"]), task("b", paths=["src/b.py"])]})
    assert result["status"] == "parallel-safe"
    assert result["waves"][0]["mode"] == "parallel"
    assert result["waves"][0]["tasks"] == ["a", "b"]


def test_dependencies_create_sequential_layers(tmp_path: Path):
    result = run_case(tmp_path, {"tasks": [task("a", paths=["src/a.py"]), task("b", depends=["a"], paths=["src/b.py"])]})
    assert [wave["tasks"] for wave in result["waves"]] == [["a"], ["b"]]


def test_path_overlap_forces_sequential_fallback(tmp_path: Path):
    result = run_case(tmp_path, {"tasks": [task("a", paths=["src/api"]), task("b", paths=["src/api/client.py"])]})
    assert result["status"] == "sequential-required"
    assert any("overlapping write paths" in reason for reason in result["fallback_reasons"])


def test_shared_contract_forces_sequential_fallback(tmp_path: Path):
    result = run_case(tmp_path, {"tasks": [task("a", paths=["a"], surfaces=["event:orders"]), task("b", paths=["b"], surfaces=["event:orders"])]})
    assert result["status"] == "sequential-required"
    assert any("shared contract surfaces" in reason for reason in result["fallback_reasons"])


def test_missing_scope_or_permission_forces_sequential(tmp_path: Path):
    result = run_case(tmp_path, {"tasks": [task("a", paths=[]), task("b", paths=["b"], parallel=False)]})
    assert result["status"] == "sequential-required"
    assert any("write scope missing" in reason for reason in result["fallback_reasons"])
    assert any("parallel permission missing" in reason for reason in result["fallback_reasons"])


def test_cycle_is_blocked(tmp_path: Path):
    result = run_case(tmp_path, {"tasks": [task("a", depends=["b"], paths=["a"]), task("b", depends=["a"], paths=["b"])]}, expect=1)
    assert result["status"] == "blocked"
    assert "cycle" in result["errors"][0]
