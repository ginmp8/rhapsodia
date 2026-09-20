from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path
OPS={'transformation-merge','backcross','repair-crossover','bounded-mutation'}

def sig(base,ts):
 p=json.dumps({'base_parent_id':base,'transformation_ids':sorted(ts)},sort_keys=True,separators=(',',':'),ensure_ascii=False).encode();return hashlib.sha256(p).hexdigest()
def validate(d):
 e=[]
 req=('request_version','candidate_id','operator','base_parent_id','donor_parent_ids','transformation_ids','expected_capability_effects','reason','request_signature')
 for k in req:
  if k not in d:e.append(f'missing:{k}')
 if e:return sorted(set(e))
 if d['request_version']!=2:e.append('request_version:unsupported')
 for k in ('candidate_id','base_parent_id','reason','request_signature'):
  if not isinstance(d.get(k),str) or not d[k].strip():e.append(f'{k}:invalid')
 if d.get('operator') not in OPS:e.append('operator:invalid')
 donors=d.get('donor_parent_ids')
 if not isinstance(donors,list) or any(not isinstance(x,str) or not x for x in donors) or len(donors)!=len(set(donors)):e.append('donor_parent_ids:invalid');donors=[]
 if d.get('base_parent_id') in donors:e.append('donor_parent_ids:contains_base')
 if d.get('candidate_id') in [d.get('base_parent_id'),*donors]:e.append('candidate:self_parent')
 ts=d.get('transformation_ids')
 if not isinstance(ts,list) or not ts or any(not isinstance(x,str) or not x for x in ts) or len(ts)!=len(set(ts)):e.append('transformation_ids:invalid')
 effects=d.get('expected_capability_effects')
 if not isinstance(effects,list) or any(not isinstance(x,str) or not x for x in effects) or len(effects)!=len(set(effects)):e.append('expected_capability_effects:invalid')
 if isinstance(ts,list) and all(isinstance(x,str) and x for x in ts) and isinstance(d.get('base_parent_id'),str):
  if d.get('request_signature')!=sig(d['base_parent_id'],ts):e.append('request_signature:mismatch')
 return sorted(set(e))
def main():
 p=argparse.ArgumentParser();p.add_argument('request');a=p.parse_args();d=json.loads(Path(a.request).read_text());e=validate(d);print(json.dumps({'status':'pass' if not e else 'fail','contract_version':2,'errors':e},indent=2,sort_keys=True));return 0 if not e else 2
if __name__=='__main__':sys.exit(main())
