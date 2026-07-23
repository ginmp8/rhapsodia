#!/usr/bin/env python3
"""Validate routing contracts and execute every routeable canonical scenario."""
import argparse,importlib.util,json,re
from collections import Counter
from pathlib import Path
CATS={'single_owner','multi_intent','ambiguous','non_activation','adversarial','edge_case'}; OWNERS={'nomia','mago','magia','none'}
EDGE={('nomia','mago'):'nomia_to_mago',('mago','magia'):'mago_to_magia',('magia','mago'):'magia_to_mago',('mago','nomia'):'mago_to_nomia',('magia','nomia'):'magia_to_nomia'}
CASES={'ROUTE-E-001':['validation'],'ROUTE-E-002':['status'],'ROUTE-E-003':['tests'],'ROUTE-E-004':['requirements'],'ROUTE-M-001':['intake','planning','implementation','reconcile','release'],'ROUTE-M-002':['roadmap','planning'],'ROUTE-M-003':['design','implementation'],'ROUTE-M-004':['implementation','reconcile','release'],'ROUTE-M-005':['validation','reporting'],'ROUTE-M-006':['implementation','reconcile','tests'],'ROUTE-S-001':['intake'],'ROUTE-S-002':['release'],'ROUTE-S-003':['planning'],'ROUTE-S-004':['reconcile'],'ROUTE-S-005':['implementation'],'ROUTE-S-006':['debug'],'ROUTE-X-001':['governance','planning'],'ROUTE-X-002':['planning'],'ROUTE-X-003':['implementation','reconcile'],'ROUTE-X-004':['governance','planning','implementation']}
STALE=[re.compile(x,re.I) for x in (r"docs/boards/[^\s\"']+/v1(?:/|\b)",r'\bcycle[ _-]?version\b',r'\bcycle\s+\d{4}\.\d{2}\b',r'\bspec\d{3,}\b',r'\bcycle_id\s*[:=]?\s*v\d+\b')]
def load(p): return json.loads(p.read_text())
def strings(v):
 if isinstance(v,str): yield v
 elif isinstance(v,list):
  for x in v: yield from strings(x)
 elif isinstance(v,dict):
  for x in v.values(): yield from strings(x)
def module(root):
 p=root/'scripts/route_ecosystem_request.py'; s=importlib.util.spec_from_file_location('router',p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
def local_errors(root):
 out=[]
 for p in [root/'examples/activation-scenarios.json',*sorted((root/'evals').glob('*.json'))]:
  if not p.is_file(): continue
  try: items=load(p); items=items.get('scenarios',[]) if isinstance(items,dict) else items
  except Exception as exc: out.append(f'{p.relative_to(root)} is invalid JSON: {exc}'); continue
  if not isinstance(items,list): continue
  for i,item in enumerate(items):
   if not isinstance(item,dict): continue
   blob='\n'.join(strings(item)); low=blob.lower()
   if ('legacy' in low or 'migration' in low) and ('adapt' in low or 'migration' in low): continue
   for pat in STALE:
    if m:=pat.search(blob): out.append(f'{p.relative_to(root)} scenario {item.get("id",i)} uses retired current-path vocabulary: {m.group(0)}')
 return out
def validate(root):
 err=[]; version=(root/'VERSION').read_text().strip(); contract=load(root/'references/ecosystem-routing-contract.json'); corpus=load(root/'evals/ecosystem-routing-scenarios.json')
 if contract.get('contract_id')!='nomia-mago-magia-routing-v1': err.append('unexpected routing contract_id')
 if contract.get('ecosystem_release')!=version: err.append('routing contract release does not match VERSION')
 if corpus.get('contract_id')!=contract.get('contract_id') or corpus.get('ecosystem_release')!=version: err.append('routing corpus contract/release mismatch')
 allowed=set(contract.get('allowed_handoffs',[])); scenarios=corpus.get('scenarios',[]); counts=Counter(); seen=set(); executed=0
 if not isinstance(scenarios,list) or not scenarios: err.append('routing corpus must have scenarios'); scenarios=[]
 try: router=module(root)
 except Exception as exc: err.append(f'local router could not be loaded: {exc}'); router=None
 for i,s in enumerate(scenarios):
  if not isinstance(s,dict): err.append(f'scenario {i} is not an object'); continue
  sid,cat,first,seq,mutate=(s.get(k) for k in ('id','category','expected_first_owner','owner_sequence','mutation_allowed_after_owner_resolution'))
  if not isinstance(sid,str) or not re.fullmatch(r'ROUTE-[A-Z]-\d{3}',sid): err.append(f'scenario {i} has invalid id {sid!r}')
  elif sid in seen: err.append(f'duplicate routing scenario id {sid}')
  seen.add(sid)
  if cat not in CATS: err.append(f'{sid}: invalid category {cat!r}')
  else: counts[cat]+=1
  if first not in OWNERS: err.append(f'{sid}: invalid first owner {first!r}')
  if not isinstance(seq,list) or any(x not in OWNERS-{'none'} for x in seq): err.append(f'{sid}: invalid owner_sequence'); seq=[]
  if first=='none':
   if seq or mutate is not False: err.append(f'{sid}: unresolved owner must prohibit mutation with empty sequence')
   if sid in CASES: err.append(f'{sid}: unresolved scenario cannot have executable input')
  else:
   if not seq or seq[0]!=first: err.append(f'{sid}: sequence must begin with expected_first_owner')
   if sid not in CASES: err.append(f'{sid}: missing executable router input')
   elif router:
    try: result=router.route(CASES[sid])
    except Exception as exc: err.append(f'{sid}: router raised {exc}')
    else:
     executed+=1; expected=[EDGE[p] for p in zip(seq,seq[1:])]
     if (result.get('current_owner'),result.get('owner_sequence'),result.get('handoff_sequence'),result.get('mutation_owner_count'))!=(first,seq,expected,1): err.append(f'{sid}: executable router result mismatch')
  for a,b in zip(seq,seq[1:]):
   if f'{a}_to_{b}' not in allowed: err.append(f'{sid}: unsupported owner transition {a}_to_{b}')
  blob='\n'.join(strings(s))
  for pat in STALE:
   if m:=pat.search(blob): err.append(f'{sid}: routing corpus uses retired vocabulary {m.group(0)}')
 if set(CASES)!={s['id'] for s in scenarios if isinstance(s,dict) and s.get('expected_first_owner')!='none'}: err.append('executable router input ids must exactly match routeable scenarios')
 for cat in CATS:
  if counts[cat]<4: err.append(f'routing category {cat} has {counts[cat]}; expected at least 4')
 if 'ecosystem-routing-contract.md' not in (root/'SKILL.md').read_text(): err.append('SKILL.md must reference the distributed routing contract')
 err+=local_errors(root)
 return {'status':'pass' if not err else 'fail','errors':err,'warnings':[],'scenario_count':len(scenarios),'executed_route_count':executed,'counts':dict(counts),'measurement_kind':corpus.get('measurement_kind')}
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__); p.add_argument('--target',default=str(Path(__file__).resolve().parents[1])); p.add_argument('--json-output'); a=p.parse_args(argv); result=validate(Path(a.target).resolve())
 if a.json_output: Path(a.json_output).write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print(f"status: {result['status']}\nscenario_count: {result['scenario_count']}\nexecuted_route_count: {result['executed_route_count']}")
 for e in result['errors']: print(f'ERROR: {e}')
 return 0 if result['status']=='pass' else 1
if __name__=='__main__': raise SystemExit(main())
