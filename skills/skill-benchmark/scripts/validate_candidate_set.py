from __future__ import annotations
import argparse,json,sys
from pathlib import Path
LEVELS={'L0-structural','L1-deterministic','L2-focused','L3-harness','L4-benchmark','L5-holdout'}

def _nonempty(v):return isinstance(v,str) and bool(v.strip())
def validate(d):
 e=[];version=d.get('contract_version',1);rows=d.get('candidates');candidate_identities=set()
 if version not in {1,2,3,4}:e.append('contract_version:unsupported')
 if not isinstance(rows,list) or not rows:return sorted(set(e+['candidates:invalid']))
 ids=[];refs={};metric_ids=None;keys=('baseline_id','evaluator_id','scenario_set_id')+ (('policy_id',) if version>=2 else tuple())
 for i,r in enumerate(rows):
  if not isinstance(r,dict):e.append(f'candidate[{i}]:invalid');continue
  cid=r.get('candidate_id');ids.append(cid)
  if not _nonempty(cid):e.append(f'candidate[{i}].candidate_id:missing')
  if version>=2:
   if not _nonempty(r.get('candidate_identity')):e.append(f'candidate[{i}].candidate_identity:missing')
   elif version>=4:
    if r.get('candidate_identity') in candidate_identities:e.append('candidate_identity:duplicate')
    candidate_identities.add(r.get('candidate_identity'))
   if not _nonempty(r.get('parent_id')):e.append(f'candidate[{i}].parent_id:missing')
   if r.get('evaluation_level') not in LEVELS:e.append(f'candidate[{i}].evaluation_level:invalid')
  for k in keys:
   if not _nonempty(r.get(k)):e.append(f'candidate[{i}].{k}:missing')
   elif k not in refs:refs[k]=r[k]
   elif refs[k]!=r[k]:e.append(f'comparability:{k}:mismatch')
  metrics=r.get('metrics',{})
  if not isinstance(metrics,dict):e.append(f'candidate[{i}].metrics:invalid');continue
  if version>=3:
   if not metrics:e.append(f'candidate[{i}].metrics:empty')
   current_metric_ids=frozenset(metrics)
   if metric_ids is None:metric_ids=current_metric_ids
   elif metric_ids!=current_metric_ids:e.append('comparability:metrics:mismatch')
  if version>=2:
   for name,val in metrics.items():
    if isinstance(val,bool):e.append(f'candidate[{i}].metrics.{name}:invalid')
    elif isinstance(val,(int,float)):pass
    elif isinstance(val,dict):
     if not isinstance(val.get('value'),(int,float)) or isinstance(val.get('value'),bool):e.append(f'candidate[{i}].metrics.{name}.value:invalid')
     u=val.get('uncertainty',0)
     if not isinstance(u,(int,float)) or isinstance(u,bool) or u<0:e.append(f'candidate[{i}].metrics.{name}.uncertainty:invalid')
    else:e.append(f'candidate[{i}].metrics.{name}:invalid')
 if len(ids)!=len(set(ids)):e.append('candidate_id:duplicate')
 return sorted(set(e))
def main():
 p=argparse.ArgumentParser();p.add_argument('input');a=p.parse_args();d=json.loads(Path(a.input).read_text());e=validate(d);print(json.dumps({'status':'pass' if not e else 'fail','contract_version':d.get('contract_version',1),'errors':e},indent=2,sort_keys=True));return 0 if not e else 2
if __name__=='__main__':sys.exit(main())
