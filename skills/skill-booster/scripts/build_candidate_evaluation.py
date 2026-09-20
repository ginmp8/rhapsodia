#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path

def load(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def _find(rows,cid,key):
 for r in rows:
  if isinstance(r,dict) and r.get('candidate_id')==cid:return r
 raise ValueError(f'{key}:candidate_not_found:{cid}')
def _stable_ref(payload):
 b=json.dumps(payload,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode('utf-8')
 return 'sha256:'+hashlib.sha256(b).hexdigest()
def build(contract,cid,candidate_identity,benchmark=None,harness=None,hard_gates=None,metrics=None,level=None,evidence_type='supplied',deficits=None,holdout_status='not-used'):
 if contract.get('contract_version')!=2:raise ValueError('search_contract:unsupported')
 identity=dict(contract['evaluation_identity'])
 resolved_metrics=metrics
 resolved_level=level
 if benchmark is not None:
  if benchmark.get('contract_version')!=3:raise ValueError('benchmark:unsupported_contract')
  row=_find(benchmark.get('candidates',[]),cid,'benchmark')
  if row.get('candidate_identity')!=candidate_identity:raise ValueError('benchmark:candidate_identity_mismatch')
  bident={'evaluator_id':row.get('evaluator_id'),'scenario_set_id':row.get('scenario_set_id'),'policy_id':row.get('policy_id')}
  if bident!=identity:raise ValueError('benchmark:evaluation_identity_mismatch')
  resolved_metrics=row.get('metrics')
  resolved_level=row.get('evaluation_level')
 if harness is not None:
  if harness.get('contract_version')!=3:raise ValueError('harness:unsupported_contract')
  row=_find(harness.get('runs',[]),cid,'harness')
  if row.get('candidate_identity')!=candidate_identity:raise ValueError('harness:candidate_identity_mismatch')
  hident={'evaluator_id':row.get('evaluator_id'),'scenario_set_id':row.get('scenario_set_id'),'policy_id':row.get('evaluation_policy_id')}
  if hident!=identity:raise ValueError('harness:evaluation_identity_mismatch')
  if row.get('holdout_blind') is True and row.get('candidate_saw_evaluator_only_assets') is not False:raise ValueError('harness:holdout_leakage')
 if resolved_level not in contract.get('allowed_evaluation_levels',[]):raise ValueError('evaluation_level:invalid')
 if not isinstance(hard_gates,dict):raise ValueError('hard_gates:required')
 if set(hard_gates)!=set(contract.get('hard_gates',[])):raise ValueError('hard_gates:set_mismatch')
 if not isinstance(resolved_metrics,dict):raise ValueError('metrics:required')
 if set(resolved_metrics)!={o['name'] for o in contract.get('objectives',[])}:raise ValueError('metrics:set_mismatch')
 body={'identity':identity,'level':resolved_level,'evidence_type':evidence_type,'hard_gates':hard_gates,'metrics':resolved_metrics,'deficits':deficits or [],'holdout_status':holdout_status}
 body['evaluation_ref']=_stable_ref({'candidate_id':cid,'candidate_identity':candidate_identity,'evaluation':body})
 return {'contract_version':2,'candidate_id':cid,'candidate_identity':candidate_identity,'evaluation':body}
def main()->int:
 p=argparse.ArgumentParser();p.add_argument('--contract',required=True);p.add_argument('--candidate-id',required=True);p.add_argument('--candidate-identity',required=True);p.add_argument('--benchmark');p.add_argument('--harness');p.add_argument('--hard-gates',required=True);p.add_argument('--metrics');p.add_argument('--level');p.add_argument('--evidence-type',default='supplied');p.add_argument('--deficits');p.add_argument('--holdout-status',default='not-used');p.add_argument('--out',required=True);p.add_argument('--json-output');a=p.parse_args()
 try:
  out=build(load(a.contract),a.candidate_id,a.candidate_identity,load(a.benchmark) if a.benchmark else None,load(a.harness) if a.harness else None,load(a.hard_gates),load(a.metrics) if a.metrics else None,a.level,a.evidence_type,load(a.deficits) if a.deficits else None,a.holdout_status)
  Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n',encoding='utf-8');r={'status':'pass','output':str(Path(a.out).resolve()),'evaluation_ref':out['evaluation']['evaluation_ref']}
 except Exception as exc:r={'status':'fail','error':f'{exc.__class__.__name__}:{exc}'}
 s=json.dumps(r,indent=2,sort_keys=True)+'\n'
 if a.json_output:Path(a.json_output).write_text(s,encoding='utf-8')
 print(s,end='');return 0 if r['status']=='pass' else 2
if __name__=='__main__':sys.exit(main())
