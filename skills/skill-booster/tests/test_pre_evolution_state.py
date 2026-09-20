import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_pre_evolution_state.py"
TEMPLATES = ROOT / "assets" / "templates"


def run(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)


def test_templates_validate_together():
    result = run(
        "--capability-map", str(TEMPLATES / "capability-map.json.template"),
        "--transformation-registry", str(TEMPLATES / "transformation-registry.json.template"),
        "--experiment-registry", str(TEMPLATES / "experiment-registry.json.template"),
        "--evaluation-plan", str(TEMPLATES / "evaluation-plan.json.template"),
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)["status"] == "pass"


def test_unknown_capability_reference_fails(tmp_path):
    cap = json.loads((TEMPLATES / "capability-map.json.template").read_text())
    trans = json.loads((TEMPLATES / "transformation-registry.json.template").read_text())
    trans["transformations"][0]["capability_refs"] = ["cap.unknown"]
    cap_path = tmp_path / "cap.json"
    trans_path = tmp_path / "trans.json"
    cap_path.write_text(json.dumps(cap))
    trans_path.write_text(json.dumps(trans))
    result = run("--capability-map", str(cap_path), "--transformation-registry", str(trans_path))
    assert result.returncode != 0
    assert "CAPABILITY_REF_UNKNOWN" in result.stdout
