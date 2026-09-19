#!/usr/bin/env python3
"""Project an ordered SDD lifecycle deterministically without mutation or authority transfer."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def load_contract():
    d=json.loads((ROOT/'references/ecosystem-routing-contract.json').read_text(encoding='utf-8'))
    if not isinstance(d,dict): raise ValueError('routing contract must be an object')
    return d
CONTRACT=load_contract(); OWNER=dict(CONTRACT['intent_owners']); ROLES={'nomia','mago','magia'}; EDGE={tuple(k.split('->',1)):v for k,v in CONTRACT['handoff_edges'].items()}
def _owner_phases(intents:list[str])->tuple[list[str],list[str]]:
    clean=[]; phases=[]
    for raw in intents:
        intent=str(raw).strip().lower()
        if intent not in OWNER: raise ValueError(f'unsupported intent: {intent}')
        clean.append(intent); owner=OWNER[intent]
        if not phases or phases[-1]!=owner: phases.append(owner)
    if not phases: raise ValueError('at least one intent is required')
    return clean,phases
def _bridge_required_transitions(phases:list[str])->list[str]:
    out=[]
    for owner in phases:
        if out and out[-1]=='nomia' and owner=='magia': out.append('mago')
        out.append(owner)
    return out
def _route_id(clean,current_owner,owner_sequence,handoffs):
    body=json.dumps({'intents':clean,'current_owner':current_owner,'owner_sequence':owner_sequence,'handoff_sequence':handoffs,'contract_id':CONTRACT['contract_id'],'schema_version':CONTRACT['schema_version']},sort_keys=True,separators=(',',':')).encode()
    return 'route-'+hashlib.sha256(body).hexdigest()[:16]
def route(intents:list[str],current_owner:str|None=None)->dict[str,object]:
    clean,phases=_owner_phases(intents); normalized_current=None
    if current_owner:
        normalized_current=str(current_owner).strip().lower()
        if normalized_current not in ROLES: raise ValueError('invalid current_owner')
        if phases[0]!=normalized_current: phases.insert(0,normalized_current)
    owner_sequence=_bridge_required_transitions(phases)
    try: handoffs=[EDGE[pair] for pair in zip(owner_sequence,owner_sequence[1:])]
    except KeyError as exc:
        source,target=exc.args[0]; raise ValueError(f'no authority-safe handoff from {source} to {target}') from None
    phase_sequence=[{'index':i+1,'owner':owner} for i,owner in enumerate(owner_sequence)]
    return {'status':'resolved','authority':'read_only_projection','current_owner':owner_sequence[0],'owner_sequence':owner_sequence,'phase_sequence':phase_sequence,'handoff_sequence':handoffs,'mutation_owner_count':1,'intents':clean,'route_id':_route_id(clean,normalized_current,owner_sequence,handoffs),'routing_contract_version':CONTRACT['schema_version'],'shared_contract_version':CONTRACT.get('shared_contract_version')}
def main(argv=None)->int:
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--intent',action='append',required=True,choices=sorted(OWNER)); p.add_argument('--current-owner',choices=sorted(ROLES)); p.add_argument('--json-output'); a=p.parse_args(argv)
    try: result,code=route(a.intent,a.current_owner),0
    except ValueError as exc: result,code={'status':'blocked','reason':str(exc),'authority':'read_only_projection'},2
    text=json.dumps(result,indent=2,sort_keys=True)+'\n';
    if a.json_output: Path(a.json_output).write_text(text,encoding='utf-8')
    print(text,end=''); return code
if __name__=='__main__': raise SystemExit(main())
