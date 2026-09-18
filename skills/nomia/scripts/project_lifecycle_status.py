#!/usr/bin/env python3
"""Render an authority-neutral lifecycle status projection from validated handoffs and ledger events."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from typing import Any
import ecosystem_handoff
import handoff_ledger

CLASS_RANK={'public':0,'internal':1,'confidential':2,'restricted':3}

def project(envelopes:list[dict[str,Any]],ledger:dict[str,Any]|None=None)->dict[str,Any]:
 if not envelopes: raise ValueError('at least one handoff is required')
 workflows={str(item.get('workflow_id') or '') for item in envelopes}
 if len(workflows)!=1: raise ValueError('handoffs must share exactly one workflow_id')
 workflow_id=next(iter(workflows))
 validated=[]
 for item in envelopes:
  result=ecosystem_handoff.validate_envelope(item,operation='any')
  if result['status'] not in {'accepted','draft'}: raise ValueError('invalid handoff: '+'; '.join(result['reasons']))
  validated.append(item)
 ledger_states={}
 if ledger is not None:
  errors=handoff_ledger.validate(ledger)
  if errors: raise ValueError('invalid ledger: '+'; '.join(errors))
  if ledger.get('workflow_id')!=workflow_id: raise ValueError('ledger workflow does not match handoffs')
  for event in ledger['events']: ledger_states[event['handoff_id']]=event['state']
 last=validated[-1]; current_owner=last['target_skill']
 state=ledger_states.get(last['handoff_id'],'unknown')
 pending=last['handoff_id'] if state in {'unknown','created','accepted','replayed'} else None
 blockers=[]
 for item in validated:
  blockers.extend(str(v) for v in item.get('unknowns') or [])
  blockers.extend(str(v) for v in item.get('conflicts') or [])
 classification=max((item['privacy_handling']['classification'] for item in validated),key=lambda v:CLASS_RANK[v])
 return {
  'authority':'non_authoritative_projection','workflow_id':workflow_id,'current_owner':current_owner,
  'next_owner':'unknown','pending_handoff':pending,'last_handoff_state':state,
  'handoff_count':len(validated),'blockers':list(dict.fromkeys(blockers)),
  'canonical_sources':[{'handoff_id':item['handoff_id'],'direction':item['direction'],'source_skill':item['source_skill']} for item in validated],
  'privacy_classification':classification,'evidence_references':'opaque-count-only',
 }

def main(argv=None)->int:
 p=argparse.ArgumentParser(description=__doc__); p.add_argument('--handoff',action='append',required=True); p.add_argument('--ledger'); p.add_argument('--output',required=True); args=p.parse_args(argv)
 try:
  envelopes=[json.loads(Path(v).read_text(encoding='utf-8')) for v in args.handoff]
  ledger=json.loads(Path(args.ledger).read_text(encoding='utf-8')) if args.ledger else None
  out=project(envelopes,ledger); Path(args.output).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n',encoding='utf-8'); print(json.dumps({'status':'pass','output':str(Path(args.output).resolve())},indent=2)); return 0
 except (OSError,ValueError,json.JSONDecodeError) as exc:
  print(json.dumps({'status':'error','error':str(exc)},indent=2)); return 2
if __name__=='__main__': raise SystemExit(main())
