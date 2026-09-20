import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
VALIDATOR=ROOT/'scripts/validate_skill_improver_package.py'

def run_validator(target: Path):
    p=subprocess.run([sys.executable,str(VALIDATOR),'--target',str(target)],capture_output=True,text=True)
    return p.returncode,json.loads(p.stdout)

def copy_target(tmp_path: Path):
    dst=tmp_path/'skill-improver'
    shutil.copytree(ROOT,dst,ignore=shutil.ignore_patterns('__pycache__','.pytest_cache'))
    return dst

def test_package_validator_requires_generation_receipt_template(tmp_path):
    dst=copy_target(tmp_path)
    (dst/'assets/templates/generation-receipt.json.template').unlink()
    code,report=run_validator(dst)
    assert code != 0
    assert report['status']=='fail'
    assert any('generation-receipt.json.template' in e for e in report['errors'])

def test_package_validator_requires_integration_manifest(tmp_path):
    dst=copy_target(tmp_path)
    (dst/'contracts/integration-manifest.json').unlink()
    code,report=run_validator(dst)
    assert code != 0
    assert report['status']=='fail'
    assert any('integration-manifest.json' in e for e in report['errors'])

def test_package_validator_requires_generation_receipt_v3_export(tmp_path):
    dst=copy_target(tmp_path)
    path=dst/'contracts/integration-manifest.json'
    manifest=json.loads(path.read_text())
    export=next(x for x in manifest['exports'] if x['contract_id']=='skill-opt.candidate-generation-receipt')
    export['version']=2
    path.write_text(json.dumps(manifest,indent=2)+'\n')
    code,report=run_validator(dst)
    assert code != 0
    assert report['status']=='fail'
    assert any('candidate-generation-receipt:v3' in e for e in report['errors'])
