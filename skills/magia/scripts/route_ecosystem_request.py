#!/usr/bin/env python3
"""Resolve one current SDD owner and an authority-safe handoff sequence without mutation."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from typing import Any

INTENT_OWNER={
 "intake":"nomia","governance":"nomia","roadmap":"nomia","status":"nomia","reporting":"nomia","release":"nomia",
 "planning":"mago","requirements":"mago","design":"mago","tasks":"mago","reconcile":"mago",
 "implementation":"magia","debug":"magia","tests":"magia","validation":"magia","execution-docs":"magia",
}
ORDER=("nomia","mago","magia")
HANDOFF={('nomia','mago'):'nomia_to_mago',('mago','magia'):'mago_to_magia',('magia','mago'):'magia_to_mago',('mago','nomia'):'mago_to_nomia',('magia','nomia'):'magia_to_nomia'}

def route(intents:list[str],current_owner:str|None=None)->dict[str,Any]:
 clean=[]
 for value in intents:
  intent=str(value).strip().lower()
  if intent not in INTENT_OWNER: raise ValueError(f"unsupported intent: {intent}")
  if intent not in clean: clean.append(intent)
 owners=[]
 for owner in ORDER:
  if any(INTENT_OWNER[i]==owner for i in clean): owners.append(owner)
 # Governed implementation cannot skip planning.
 if current_owner in (None, 'nomia') and 'nomia' in owners and 'magia' in owners and 'mago' not in owners: owners.insert(owners.index('magia'),'mago')
 if current_owner:
  if current_owner not in {'nomia','mago','magia'}: raise ValueError('invalid current_owner')
  if current_owner in owners: owners.remove(current_owner)
  owners.insert(0,current_owner)
 if not owners: raise ValueError('at least one intent is required')
 handoffs=[]
 for a,b in zip(owners,owners[1:]):
  key=(a,b)
  if key not in HANDOFF: raise ValueError(f"no authority-safe handoff from {a} to {b}")
  handoffs.append(HANDOFF[key])
 return {"status":"resolved","authority":"read_only_projection","current_owner":owners[0],"owner_sequence":owners,"handoff_sequence":handoffs,"mutation_owner_count":1,"intents":clean}

def main(argv=None)->int:
 p=argparse.ArgumentParser(description=__doc__); p.add_argument('--intent',action='append',required=True,choices=sorted(INTENT_OWNER)); p.add_argument('--current-owner',choices=('nomia','mago','magia')); p.add_argument('--json-output'); args=p.parse_args(argv)
 try: out=route(args.intent,args.current_owner); rc=0
 except ValueError as exc: out={"status":"blocked","reason":str(exc),"authority":"read_only_projection"}; rc=2
 text=json.dumps(out,indent=2,sort_keys=True)+'\n'
 if args.json_output: Path(args.json_output).write_text(text,encoding='utf-8')
 print(text,end=''); return rc
if __name__=='__main__': raise SystemExit(main())
