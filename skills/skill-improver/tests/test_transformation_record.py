import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_transformation_record.py"
TEMPLATE = ROOT / "assets" / "templates" / "transformation-record.json.template"


def run(path):
    return subprocess.run([sys.executable, str(SCRIPT), str(path)], capture_output=True, text=True)


def test_transformation_template_validates():
    result = run(TEMPLATE)
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)["status"] == "pass"


def test_invalid_change_intent_fails(tmp_path):
    data = json.loads(TEMPLATE.read_text())
    data["change_intent"] = "winner"
    path = tmp_path / "record.json"
    path.write_text(json.dumps(data))
    result = run(path)
    assert result.returncode != 0
    assert "change_intent is invalid" in result.stdout
