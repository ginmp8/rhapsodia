from __future__ import annotations
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "skill_improver_loop.py"
spec = importlib.util.spec_from_file_location("skill_improver_loop", SCRIPT)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)

def test_command_argv_does_not_enable_shell_operators():
    argv = module.command_argv('python -c "print(1)" ; python -c "print(2)"')
    assert ';' in argv
    assert argv[0] == 'python'

def test_runner_source_has_no_shell_true():
    text = SCRIPT.read_text(encoding="utf-8")
    assert ("shell" + "=True") not in text

def test_generation_contract_versions_are_unchanged():
    import json
    manifest = json.loads((ROOT/'contracts/integration-manifest.json').read_text())
    export = next(x for x in manifest['exports'] if x['contract_id']=='skill-opt.candidate-generation-receipt')
    request = next(x for x in manifest['imports'] if x['contract_id']=='skill-opt.candidate-request')
    assert export['version'] == 3
    assert request['accepted_versions'] == [2]
