from __future__ import annotations
import argparse,json,sys
from pathlib import Path
OPS={'transformation-merge','backcross','repair-crossover','bounded-mutation'};ST={'pass','fail','blocked','not-run'}
def _list(v,allow_empty=True):return isinstance(v,list) and (allow_empty or bool(v)) and all(isinstance(x,str) and x for x in v) and len(v)==len(set(v))
def validate(d):
 e=[]
 for k in ('receipt_version','candidate_id','candidate_identity','request_signature','base_parent_id','donor_parent_ids','operator','transformation_ids','changed_files','validation_status','causal_limitations'):
  if k not in d:e.append(f'missing:{k}')
 if e:return sorted(e)
 if d['receipt_version']!=2:e.append('receipt_version:unsupported')
 for k in ('candidate_id','candidate_identity','request_signature','base_parent_id'):
  if not isinstance(d.get(k),str) or not d[k].strip():e.append(f'{k}:invalid')
 if d.get('operator') not in OPS:e.append('operator:invalid')
 if not _list(d.get('donor_parent_ids')):e.append('donor_parent_ids:invalid')
 if not _list(d.get('transformation_ids'),False):e.append('transformation_ids:invalid')
 if not _list(d.get('changed_files')):e.append('changed_files:invalid')
 if not _list(d.get('causal_limitations')):e.append('causal_limitations:invalid')
 if d.get('validation_status') not in ST:e.append('validation_status:invalid')
 return sorted(set(e))
def main():
 p=argparse.ArgumentParser();p.add_argument('receipt');a=p.parse_args();d=json.loads(Path(a.receipt).read_text());e=validate(d);print(json.dumps({'status':'pass' if not e else 'fail','errors':e},indent=2,sort_keys=True));return 0 if not e else 2
if __name__=='__main__':sys.exit(main())
