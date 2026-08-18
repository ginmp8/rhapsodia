#!/usr/bin/env python3
"""Validate the quick, standard, and governed structural reference journeys."""
from __future__ import annotations
import argparse,json
from pathlib import Path
REQUIRED_PROFILES={'quick','standard','governed'}
OWNER_SEQUENCE=['nomia','mago','magia','mago','nomia']
HANDOFF_SEQUENCE=['nomia_to_mago','mago_to_magia','magia_to_mago','mago_to_nomia']
def validate(path:Path)->list[str]:
 errors=[]
 try: data=json.loads(path.read_text(encoding='utf-8'))
 except Exception as exc: return [f'invalid reference journey file: {exc}']
 if data.get('evidence_status')!='structural-fixture; not production execution': errors.append('reference journeys must not claim production evidence')
 items=data.get('journeys')
 if not isinstance(items,list): return errors+['journeys must be a list']
 profiles={item.get('profile') for item in items if isinstance(item,dict)}
 if profiles!=REQUIRED_PROFILES: errors.append(f'profiles must be exactly {sorted(REQUIRED_PROFILES)}')
 ids=set()
 for i,item in enumerate(items):
  if not isinstance(item,dict): errors.append(f'journeys[{i}] must be an object'); continue
  if item.get('id') in ids: errors.append(f'duplicate journey id: {item.get("id")}')
  ids.add(item.get('id'))
  if item.get('owner_sequence')!=OWNER_SEQUENCE: errors.append(f'{item.get("id")}: owner sequence changed')
  if item.get('handoff_sequence')!=HANDOFF_SEQUENCE: errors.append(f'{item.get("id")}: handoff sequence changed')
  if not isinstance(item.get('validation'),list) or len(item['validation'])<2: errors.append(f'{item.get("id")}: validation is insufficient')
  if item.get('rollback_exercised') is not True: errors.append(f'{item.get("id")}: rollback exercise is required')
  if not isinstance(item.get('privacy_case'),str) or not item['privacy_case'].strip(): errors.append(f'{item.get("id")}: privacy case is required')
 return errors
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__); p.add_argument('--input',default=str(Path(__file__).resolve().parents[1]/'examples/reference-journeys.json')); p.add_argument('--json-output'); args=p.parse_args(argv)
 errors=validate(Path(args.input)); result={'status':'pass' if not errors else 'fail','errors':errors,'evidence_status':'structural-fixture; not production execution'}; text=json.dumps(result,indent=2,sort_keys=True)+'\n'
 if args.json_output: Path(args.json_output).write_text(text,encoding='utf-8')
 print(text,end=''); return 0 if not errors else 1
if __name__=='__main__': raise SystemExit(main())
