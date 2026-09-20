import importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('m',ROOT/'scripts/validate_generation_receipt.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def data():return json.loads((ROOT/'assets/templates/generation-receipt.json.template').read_text())
def test_template_valid():assert m.validate(data())==[]
def test_v1_rejected():d=data();d['receipt_version']=1;assert 'receipt_version:unsupported' in m.validate(d)
