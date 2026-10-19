#!/usr/bin/env python3
"""Deterministic static invariants for selective decision guidance, not model behavior."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]

def main():
    skill=(ROOT/'SKILL.md').read_text(encoding='utf8')
    policy=(ROOT/'references/selective-decision-policy.md').read_text(encoding='utf8')
    contract=(ROOT/'references/behavior-contract.md').read_text(encoding='utf8')
    assert len(skill.splitlines()) <= 100
    assert len(re.search(r'^description: (.+)$',skill,re.M).group(1)) <= 500
    assert 'SEL-001' in contract and 'SEL-002' in contract
    assert 'references/selective-decision-policy.md' in '\n'.join(skill.splitlines()[:100])
    for token in ['blocked','undetermined','escalate','decided','coverage = decided / eligible','selective_error = wrong_decided / decided','false_abstention','decided = 0','calibration_ref','distribution shift','Do not fit/select thresholds','over-refusal','None grants execution permission']:
        assert token.lower() in policy.lower(), token
    suite=json.loads((ROOT/'evals/selective-decision-scenarios.json').read_text())
    assert suite['status']=='planned' and len(suite['scenarios'])>=7
    assert len({c['id'] for c in suite['scenarios']})==len(suite['scenarios'])
    assert 'none' not in [c['expected_status'] for c in suite['scenarios']]
    print('Selective decision structural/risk-coverage guidance: pass (7 candidate-visible planned cases)')
if __name__=='__main__':main()
