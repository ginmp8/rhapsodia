from __future__ import annotations
import argparse,json,sys
from pathlib import Path

SCRIPT_DIR=Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:sys.path.insert(0,str(SCRIPT_DIR))
from _common import metric_value

EVIDENCE_TYPES={'measured','supplied','derived','planned','unknown'}
GATE_VALUES={'pass','fail','not-run','blocked'}
HOLDOUT={'not-used','blind-pass','blind-fail','revealed-development'}

def _s(v):return isinstance(v,str) and bool(v.strip())

def validate(contract:dict,envelope:dict)->list[str]:
 e=[]
 if envelope.get('contract_version')!=2:e.append('contract_version:unsupported')
 for k in ('candidate_id','candidate_identity'):
  if not _s(envelope.get(k)):e.append(f'{k}:invalid')
 ev=envelope.get('evaluation')
 if not isinstance(ev,dict):return sorted(set(e+['evaluation:invalid']))
 if not _s(ev.get('evaluation_ref')):e.append('evaluation_ref:invalid')
 ident=ev.get('identity')
 if not isinstance(ident,dict):e.append('identity:invalid')
 else:
  for k in ('evaluator_id','scenario_set_id','policy_id'):
   if not _s(ident.get(k)):e.append(f'identity.{k}:invalid')
  if ident!=contract.get('evaluation_identity'):e.append('identity:mismatch')
 level=ev.get('level')
 if level not in set(contract.get('allowed_evaluation_levels',[])):e.append('level:invalid')
 if ev.get('evidence_type') not in EVIDENCE_TYPES:e.append('evidence_type:invalid')
 gates=ev.get('hard_gates')
 expected_gates=set(contract.get('hard_gates',[]))
 if not isinstance(gates,dict):e.append('hard_gates:invalid')
 else:
  if set(gates)!=expected_gates:e.append('hard_gates:set_mismatch')
  for name,val in gates.items():
   if val not in GATE_VALUES:e.append(f'hard_gates.{name}:invalid')
 metrics=ev.get('metrics')
 expected_metrics={o.get('name') for o in contract.get('objectives',[]) if isinstance(o,dict)}
 if not isinstance(metrics,dict):e.append('metrics:invalid')
 else:
  if set(metrics)!=expected_metrics:e.append('metrics:set_mismatch')
  for name,val in metrics.items():
   if metric_value(val) is None:e.append(f'metrics.{name}:invalid')
 deficits=ev.get('deficits')
 if not isinstance(deficits,list) or any(not _s(x) for x in deficits) or len(deficits)!=len(set(deficits)):e.append('deficits:invalid')
 hs=ev.get('holdout_status','not-used')
 if hs not in HOLDOUT:e.append('holdout_status:invalid')
 if level=='L5-holdout' and hs=='not-used':e.append('holdout_status:required_for_l5')
 return sorted(set(e))

def main()->int:
 p=argparse.ArgumentParser();p.add_argument('--contract',required=True);p.add_argument('--evaluation',required=True);p.add_argument('--json-output');a=p.parse_args()
 try:
  c=json.loads(Path(a.contract).read_text(encoding='utf-8'));v=json.loads(Path(a.evaluation).read_text(encoding='utf-8'));e=validate(c,v)
 except Exception as exc:e=[f'evaluation:unreadable:{exc.__class__.__name__}']
 r={'status':'pass' if not e else 'fail','contract_version':2,'errors':e};s=json.dumps(r,indent=2,sort_keys=True)+'\n'
 if a.json_output:Path(a.json_output).write_text(s,encoding='utf-8')
 print(s,end='');return 0 if not e else 2
if __name__=='__main__':sys.exit(main())
