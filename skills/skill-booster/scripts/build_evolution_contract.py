#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path

def load(path:Path):return json.loads(path.read_text(encoding='utf-8'))
def stable_id(path:Path)->str:
 d=load(path);payload=json.dumps(d,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode('utf-8')
 return 'sha256:'+hashlib.sha256(payload).hexdigest()
def resolve(base:Path,ref:str)->Path:
 p=Path(ref);return p if p.is_absolute() else (base/p).resolve()
def map_status(s:str)->str:
 return {'planned':'proposed','applied':'proposed','accepted':'accepted','rejected':'rejected','reverted':'rejected'}.get(s,s if s in {'proposed','accepted','validated','rejected','deprecated'} else 'proposed')
def build(handoff:dict,base:Path)->dict:
 refs=handoff['artifact_refs']
 cap_p=resolve(base,refs['capability_map']);hyp_p=resolve(base,refs['hypothesis_pool']);tr_p=resolve(base,refs['transformation_registry']);ev_p=resolve(base,refs['evaluation_plan'])
 cap=load(cap_p);tr=load(tr_p);ev=load(ev_p);hyp=load(hyp_p)
 target=handoff['target_identity']
 identities=[]
 if isinstance(cap.get('target'),dict):identities.append(cap['target'].get('identity'))
 if isinstance(hyp.get('target'),dict):identities.append(hyp['target'].get('identity'))
 identities.extend([tr.get('target_identity'),ev.get('target_identity')])
 bad=[x for x in identities if x and x!=target]
 if bad:raise ValueError('artifact target identity mismatch')
 if ev.get('schema_version')!=2:raise ValueError('evaluation plan schema_version must be 2')
 finalist_policy=ev.get('finalist_policy')
 if not isinstance(finalist_policy,dict):raise ValueError('evaluation plan finalist policy missing')
 if handoff.get('finalist_policy')!=finalist_policy:raise ValueError('finalist policy mismatch between handoff and evaluation plan')
 invariants=[]
 for c in cap.get('capabilities',[]):
  if isinstance(c,dict):invariants.extend(x for x in c.get('invariants',[]) if isinstance(x,str) and x)
 invariants=sorted(set(invariants))
 transformed=[]
 for item in tr.get('transformations',[]):
  if not isinstance(item,dict) or not item.get('id'):continue
  effects=item.get('capability_effects') or item.get('capability_refs') or []
  transformed.append({
   'id':item['id'],'status':map_status(item.get('status','planned')),
   'depends_on':sorted(set(item.get('depends_on',[]))),
   'conflicts_with':sorted(set(item.get('conflicts_with',[]))),
   'capability_effects':sorted(set(effects)),
   'violates_invariants':sorted(set(item.get('violates_invariants',[]))),
   'addresses':sorted(set(item.get('addresses',[]))),
  })
 return {
  'contract_version':4,'search_id':handoff['search_id'],'target_identity':target,'target_class':handoff['target_class'],
  'baseline_candidate_id':handoff['baseline_candidate_id'],'canonical_candidate_id':handoff['canonical_candidate_id'],
  'input_identities':{'capability_map_id':stable_id(cap_p),'hypothesis_pool_id':stable_id(hyp_p),'transformation_registry_id':stable_id(tr_p),'evaluation_plan_id':stable_id(ev_p)},
  'interfaces':{'mutation_interface_id':handoff['mutation_interface']['interface_id'],'evaluation_interface_id':handoff['evaluation_interface']['interface_id']},
  'budget':handoff['budget'],'hard_gates':handoff['hard_gates'],'objectives':handoff['objectives'],'evaluation_identity':handoff['evaluation_identity'],
  'allowed_evaluation_levels':handoff['allowed_evaluation_levels'],'allowed_operators':handoff['allowed_operators'],'preserve_roles':handoff['preserve_roles'],
  'selection_policy':handoff['selection_policy'],'finalist_policy':finalist_policy,'capability_invariants':invariants,'transformation_registry':transformed,
 }
def main()->int:
 ap=argparse.ArgumentParser();ap.add_argument('--handoff',required=True);ap.add_argument('--out',required=True);ap.add_argument('--json-output');a=ap.parse_args()
 hp=Path(a.handoff).resolve()
 try:
  h=load(hp);contract=build(h,hp.parent);Path(a.out).write_text(json.dumps(contract,indent=2,sort_keys=True)+"\n",encoding='utf-8');report={'status':'pass','output':str(Path(a.out).resolve())}
 except Exception as exc:report={'status':'fail','error':f'{exc.__class__.__name__}:{exc}'}
 payload=json.dumps(report,indent=2,sort_keys=True)+"\n"
 if a.json_output:Path(a.json_output).write_text(payload,encoding='utf-8')
 print(payload,end='');return 0 if report['status']=='pass' else 2
if __name__=='__main__':sys.exit(main())
