#!/usr/bin/env python3
"""Project an ordered SDD lifecycle without mutation or authority transfer."""
import argparse,json
from pathlib import Path
OWNER={**dict.fromkeys(('intake','governance','roadmap','status','reporting','release'),'nomia'),**dict.fromkeys(('planning','requirements','design','tasks','reconcile'),'mago'),**dict.fromkeys(('implementation','debug','tests','validation','execution-docs'),'magia')}
EDGE={('nomia','mago'):'nomia_to_mago',('mago','magia'):'mago_to_magia',('magia','mago'):'magia_to_mago',('mago','nomia'):'mago_to_nomia',('magia','nomia'):'magia_to_nomia'}
def route(intents,current_owner=None):
 clean=[]; owners=[]
 for raw in intents:
  intent=str(raw).strip().lower()
  if intent not in OWNER: raise ValueError(f'unsupported intent: {intent}')
  clean.append(intent); owner=OWNER[intent]
  if not owners or owners[-1]!=owner: owners.append(owner)
 if not owners: raise ValueError('at least one intent is required')
 out=[]
 for owner in owners:
  if out[-1:] == ['nomia'] and owner=='magia': out.append('mago')
  out.append(owner)
 if current_owner:
  current_owner=str(current_owner).strip().lower()
  if current_owner not in {'nomia','mago','magia'}: raise ValueError('invalid current_owner')
  if out[0]!=current_owner: out.insert(0,current_owner)
 try: handoffs=[EDGE[p] for p in zip(out,out[1:])]
 except KeyError as exc: raise ValueError(f'no authority-safe handoff from {exc.args[0][0]} to {exc.args[0][1]}') from None
 return {'status':'resolved','authority':'read_only_projection','current_owner':out[0],'owner_sequence':out,'handoff_sequence':handoffs,'mutation_owner_count':1,'intents':clean}
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__); p.add_argument('--intent',action='append',required=True,choices=sorted(OWNER)); p.add_argument('--current-owner',choices=('nomia','mago','magia')); p.add_argument('--json-output'); a=p.parse_args(argv)
 try: result,code=route(a.intent,a.current_owner),0
 except ValueError as exc: result,code={'status':'blocked','reason':str(exc),'authority':'read_only_projection'},2
 text=json.dumps(result,indent=2,sort_keys=True)+'\n'
 if a.json_output: Path(a.json_output).write_text(text)
 print(text,end=''); return code
if __name__=='__main__': raise SystemExit(main())
