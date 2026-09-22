#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re
from pathlib import Path

CONTRACT_ID=re.compile(r'^[A-Z]{2,5}-\d{3}$')
ACT_GROUPS={'activation','non-activation','ambiguous','boundary','adversarial','holdout'}
ACT_ROUTES={'activate','do-not-activate','conditional','activate-constrained','split-handoff','reject-scope-weakening','reject-fabricated-evidence','reject-ownership-expansion'}
ACT_TYPES={'should_activate','should_not_activate','ambiguous','edge_case','regression','adversarial'}
DEC_TYPES={'noul','choice','score'}
DEC_STATUS={'decided','undetermined','blocked','escalate'}
DEC_GROUPS={'core','uncertainty','policy','capability','invalid-contract','calibration','adversarial','portability','evidence-claims','holdout-visible'}

def add(errors, code, subject, detail=''):
    errors.append({'code':code,'subject':subject,'detail':detail})

def load(path, errors, code):
    try: return json.loads(path.read_text(encoding='utf-8'))
    except Exception as exc: add(errors, code, str(path), str(exc)); return {}

def validate_activation(data, errors):
    if data.get('language') != 'en': add(errors,'EV000','activation','language must be en')
    if not isinstance(data.get('suite_version'),str) or not data['suite_version'].strip(): add(errors,'EV001','activation','suite_version')
    if data.get('status') not in {'planned','measured'}: add(errors,'EV002','activation','status')
    scenarios=data.get('scenarios');
    if not isinstance(scenarios,list) or not scenarios: add(errors,'EV003','activation','scenarios'); return
    ids=set(); groups=set()
    for i,row in enumerate(scenarios):
        sid=row.get('id') if isinstance(row,dict) else f'index:{i}'
        if not isinstance(row,dict): add(errors,'EV004',sid,'object required'); continue
        if not isinstance(sid,str) or not sid.strip() or sid in ids: add(errors,'EV005',str(sid),'unique non-empty id')
        ids.add(sid); g=row.get('group'); groups.add(g)
        if g not in ACT_GROUPS: add(errors,'EV006',sid,f'group={g}')
        if row.get('expected_route') not in ACT_ROUTES: add(errors,'EV007',sid,'expected_route')
        if row.get('type') not in ACT_TYPES or row.get('category') != row.get('type'): add(errors,'EV008',sid,'type/category')
        if not isinstance(row.get('prompt'),str) or not row['prompt'].strip(): add(errors,'EV009',sid,'prompt')
        refs=row.get('contract_ids')
        if not isinstance(refs,list) or not refs or any(not isinstance(x,str) or not CONTRACT_ID.fullmatch(x) for x in refs): add(errors,'EV010',sid,'contract_ids')
        if not isinstance(row.get('acceptance_criteria'),list) or not row['acceptance_criteria']: add(errors,'EV011',sid,'acceptance_criteria')
        if row.get('evaluation_tier') not in {'L2-focused','L3-harness','L5-holdout'}: add(errors,'EV012',sid,'evaluation_tier')
        if row.get('visibility') != 'candidate-visible': add(errors,'EV013',sid,'bundled scenarios must be candidate-visible')
    missing=ACT_GROUPS-groups
    if missing: add(errors,'EV014','activation',f'missing groups: {sorted(missing)}')

def validate_decisions(data, errors):
    if data.get('language') != 'en': add(errors,'EV100','decision','language must be en')
    if not isinstance(data.get('suite_version'),str) or not data['suite_version'].strip(): add(errors,'EV101','decision','suite_version')
    if data.get('status') not in {'planned','measured'}: add(errors,'EV102','decision','status')
    scenarios=data.get('scenarios')
    if not isinstance(scenarios,list) or not scenarios: add(errors,'EV103','decision','scenarios'); return
    ids=set(); types=set(); statuses=set(); groups=set()
    for i,row in enumerate(scenarios):
        sid=row.get('id') if isinstance(row,dict) else f'index:{i}'
        if not isinstance(row,dict): add(errors,'EV104',sid,'object required'); continue
        if not isinstance(sid,str) or not sid.strip() or sid in ids: add(errors,'EV105',str(sid),'unique non-empty id')
        ids.add(sid)
        dtype=row.get('decision_type'); status=row.get('expected_status'); group=row.get('group')
        types.add(dtype); statuses.add(status); groups.add(group)
        if dtype not in DEC_TYPES: add(errors,'EV106',sid,'decision_type')
        if status not in DEC_STATUS: add(errors,'EV107',sid,'expected_status')
        if group not in DEC_GROUPS: add(errors,'EV108',sid,f'group={group}')
        if row.get('materiality') not in {'low','medium','high'}: add(errors,'EV109',sid,'materiality')
        if not isinstance(row.get('focus'),str) or not row['focus'].strip(): add(errors,'EV110',sid,'focus')
        refs=row.get('contract_ids')
        if not isinstance(refs,list) or not refs or any(not isinstance(x,str) or not CONTRACT_ID.fullmatch(x) for x in refs): add(errors,'EV111',sid,'contract_ids')
    if types != DEC_TYPES: add(errors,'EV112','decision',f'type coverage: {sorted(types)}')
    if not DEC_STATUS.issubset(statuses): add(errors,'EV113','decision',f'status coverage missing: {sorted(DEC_STATUS-statuses)}')
    for required in {'adversarial','calibration','portability','evidence-claims','holdout-visible'}:
        if required not in groups: add(errors,'EV114','decision',f'missing group: {required}')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('target',type=Path); ap.add_argument('--json-output',type=Path); a=ap.parse_args()
    root=a.target.resolve(); errors=[]
    validate_activation(load(root/'evals/activation-scenarios.json',errors,'EVJSON1'),errors)
    validate_decisions(load(root/'evals/decision-scenarios.json',errors,'EVJSON2'),errors)
    report={'status':'pass' if not errors else 'fail','errors':errors}
    text=json.dumps(report,indent=2,sort_keys=True)+"\n"
    if a.json_output: a.json_output.parent.mkdir(parents=True,exist_ok=True); a.json_output.write_text(text,encoding='utf-8')
    print(text,end=''); return 0 if not errors else 1
if __name__=='__main__': raise SystemExit(main())
