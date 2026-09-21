from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_activation_scenarios_use_current_harness_shape():
    data=json.loads((ROOT/'evals/activation-scenarios.json').read_text())
    assert data['target_skill']=='skill-improver'
    scenarios=data['scenarios']
    assert isinstance(scenarios,list) and scenarios
    kinds={x['type'] for x in scenarios}
    assert {'should_activate','should_not_activate','ambiguous','edge_case','regression'} <= kinds
    for item in scenarios:
        assert item['acceptance_criteria']
