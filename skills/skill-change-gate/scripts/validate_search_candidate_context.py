from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path
OPS={'transformation-merge','backcross','repair-crossover','bounded-mutation'}

def _s(v):return isinstance(v,str) and bool(v.strip())
def _sl(v,empty=True):return isinstance(v,list) and (empty or bool(v)) and all(_s(x) for x in v) and len(v)==len(set(v))
def _sig(base,ts):
 p=json.dumps({'base_parent_id':base,'transformation_ids':sorted(ts)},sort_keys=True,separators=(',',':'),ensure_ascii=False).encode();return hashlib.sha256(p).hexdigest()
def validate(d):
 e=[]
 for k in ('context_version','search_id','candidate_id','candidate_identity','base_parent_id','donor_parent_ids','operator','transformation_ids','request_signature','generation_receipt_identity','evaluation_identity'):
  if k not in d:e.append(f'missing:{k}')
 if e:return sorted(e)
 if d['context_version']!=3:e.append('context_version:unsupported')
 for k in ('search_id','candidate_id','candidate_identity','base_parent_id','request_signature','generation_receipt_identity'):
  if not _s(d.get(k)):e.append(f'{k}:invalid')
 if d.get('operator') not in OPS:e.append('operator:invalid')
 donors=d.get('donor_parent_ids')
 if not _sl(donors):e.append('donor_parent_ids:invalid');donors=[]
 base=d.get('base_parent_id');cid=d.get('candidate_id')
 if base in donors:e.append('donor_parent_ids:contains_base')
 if cid==base or cid in donors:e.append('candidate:self_parent')
 ts=d.get('transformation_ids')
 if not _sl(ts,False):e.append('transformation_ids:invalid')
 if _s(base) and isinstance(ts,list) and ts and all(_s(x) for x in ts):
  if d.get('request_signature')!=_sig(base,ts):e.append('request_signature:mismatch')
 ev=d.get('evaluation_identity')
 if not isinstance(ev,dict):e.append('evaluation_identity:invalid')
 else:
  for k in ('evaluator_id','scenario_set_id','policy_id'):
   if not _s(ev.get(k)):e.append(f'evaluation_identity.{k}:invalid')
 return sorted(set(e))
def main():
 p=argparse.ArgumentParser();p.add_argument('context');a=p.parse_args();d=json.loads(Path(a.context).read_text());e=validate(d);print(json.dumps({'status':'pass' if not e else 'fail','context_version':3,'errors':e},indent=2,sort_keys=True));return 0 if not e else 2
if __name__=='__main__':sys.exit(main())
