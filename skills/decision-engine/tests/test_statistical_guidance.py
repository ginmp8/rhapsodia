#!/usr/bin/env python3
"""Deterministic checks of newly declared guidance; not behavioral-model validation."""
from pathlib import Path
import json, re, hashlib

root=Path(__file__).resolve().parents[1]
skill=(root/'SKILL.md').read_text(encoding='utf-8')
assert len(skill.splitlines())<=100, 'Top-100 control plane overflow'
match=re.search(r'(?m)^description: (.+)$',skill)
assert match and len(match.group(1))<=500, 'Description over 500 characters'
assert 'statistical-evidence.md' in skill, 'Missing direct referral'
assert 'When quantitative evidence is outcome-relevant' in skill, 'Missing Top-100 guard'
assert 'Do not run this screen for unrelated decisions' in skill, 'Missing conditionality'
reference=(root/'references/statistical-evidence.md').read_text(encoding='utf-8')
for phrase in ('Simpson','denominator','base rate','collider','p-value','effect size','undetermined','Do not load when','decision-engine/2'):
 assert phrase.lower() in reference.lower(), f'Missing guidance: {phrase}'
assert 'STA-001' in (root/'references/behavior-contract.md').read_text(encoding='utf-8')
evals=json.loads((root/'evals/statistical-evidence-scenarios.json').read_text(encoding='utf-8'))
assert evals['status']=='planned', 'Planned scenarios must not imply runtime evaluation'
assert {f'STAT-0{i}' for i in range(1,8)}=={s['id'] for s in evals['scenarios']}
assert all(s['execution_status']=='not-run' for s in evals['scenarios'])
assert tuple(int(x) for x in (root/'VERSION').read_text().strip().split('.')) >= (2,1,0), 'Statistical guidance requires version 2.1.0 or later'
assert '## [2.1.0]' in (root/'CHANGELOG.md').read_text(encoding='utf-8')
print('Statistical-evidence guidance/description/Top-100 structural checks: pass')
