import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def imports():
    data=json.loads((ROOT/'contracts/integration-manifest.json').read_text())
    return {x['contract_id']:x['accepted_versions'] for x in data['imports']}

def test_change_gate_context_v3_is_required():
    assert imports()['skill-opt.search-candidate-context'] == [3]

def test_generation_receipt_v3_is_required():
    assert imports()['skill-opt.candidate-generation-receipt'] == [3]
