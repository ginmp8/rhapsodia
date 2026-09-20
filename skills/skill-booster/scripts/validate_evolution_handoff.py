from __future__ import annotations
import argparse,json,sys
from pathlib import Path
DIRS={'maximize','minimize'}
LEVELS={'L0-structural','L1-deterministic','L2-focused','L3-harness','L4-benchmark','L5-holdout'}
OPS={'transformation-merge','backcross','repair-crossover','bounded-mutation'}
FINALIST_HOLDOUT_POLICIES={'not-required','blind-pass-required'}

def _nonempty(v):return isinstance(v,str) and bool(v.strip())
def validate(d):
 e=[]
 required=('handoff_version','contract_version','search_id','mode','target_identity','target_class','baseline_candidate_id','canonical_candidate_id','artifact_refs','evaluation_identity','hard_gates','objectives','budget','mutation_interface','evaluation_interface','allowed_evaluation_levels','allowed_operators','preserve_roles','selection_policy','finalist_policy')
 for k in required:
  if k not in d:e.append(f'missing:{k}')
 if e:return sorted(set(e))
 if d['handoff_version']!=4:e.append('handoff_version:unsupported')
 if d['contract_version']!=4:e.append('contract_version:unsupported')
 if d['mode']!='evolutionary-optimization':e.append('mode:invalid')
 for k in ('search_id','target_identity','target_class','baseline_candidate_id','canonical_candidate_id'):
  if not _nonempty(d.get(k)):e.append(f'{k}:invalid')
 if d.get('baseline_candidate_id')==d.get('canonical_candidate_id'):e.append('candidate_ids:baseline_equals_canonical')
 refs=d.get('artifact_refs',{})
 if not isinstance(refs,dict):e.append('artifact_refs:invalid')
 else:
  for k in ('capability_map','hypothesis_pool','transformation_registry','evaluation_plan'):
   if not _nonempty(refs.get(k)):e.append(f'artifact_refs.{k}:invalid')
 b=d.get('budget',{})
 for k in ('initial_variants','max_active_candidates','max_total_candidates','finalists','stagnant_rounds','max_recombination_proposals_per_round'):
  if not isinstance(b.get(k),int) or isinstance(b.get(k),bool) or b[k]<=0:e.append(f'budget.{k}:invalid')
 if all(isinstance(b.get(k),int) and not isinstance(b.get(k),bool) for k in ('initial_variants','max_active_candidates','max_total_candidates','finalists')):
  if b['max_total_candidates']>20:e.append('budget:max_total_candidates_exceeds_20')
  if b['max_active_candidates']>b['max_total_candidates']:e.append('budget:active_exceeds_total')
  if b['initial_variants']>b['max_active_candidates']:e.append('budget:initial_exceeds_active')
  if b['finalists']>b['max_active_candidates']:e.append('budget:finalists_exceed_active')
 ev=d.get('evaluation_identity',{})
 if not isinstance(ev,dict):e.append('evaluation_identity:invalid')
 else:
  for k in ('evaluator_id','scenario_set_id','policy_id'):
   if not _nonempty(ev.get(k)):e.append(f'evaluation_identity.{k}:invalid')
 gates=d.get('hard_gates')
 if not isinstance(gates,list) or not gates or any(not _nonempty(x) for x in gates) or len(gates)!=len(set(gates)):e.append('hard_gates:invalid')
 objs=d.get('objectives')
 if not isinstance(objs,list) or not objs:e.append('objectives:invalid')
 else:
  names=[]
  for i,o in enumerate(objs):
   if not isinstance(o,dict) or not _nonempty(o.get('name')):e.append(f'objectives[{i}]:invalid');continue
   names.append(o['name'])
   if o.get('direction') not in DIRS:e.append(f'objectives[{i}].direction:invalid')
   md=o.get('min_delta')
   if not isinstance(md,(int,float)) or isinstance(md,bool) or md<0:e.append(f'objectives[{i}].min_delta:invalid')
  if len(names)!=len(set(names)):e.append('objectives:duplicate')
 for k,cid,version in (('mutation_interface','skill-opt.candidate-request',2),('evaluation_interface','skill-opt.candidate-evaluation',2)):
  v=d.get(k,{})
  if not isinstance(v,dict) or not _nonempty(v.get('owner')) or not _nonempty(v.get('interface_id')):e.append(f'{k}:invalid');continue
  if v.get('contract_id')!=cid:e.append(f'{k}.contract_id:invalid')
  if v.get('version')!=version:e.append(f'{k}.version:unsupported')
 levels=d.get('allowed_evaluation_levels')
 if not isinstance(levels,list) or not levels or set(levels)-LEVELS or len(levels)!=len(set(levels)):e.append('allowed_evaluation_levels:invalid')
 ops=d.get('allowed_operators')
 if not isinstance(ops,list) or not ops or set(ops)-OPS or len(ops)!=len(set(ops)):e.append('allowed_operators:invalid')
 preserve=d.get('preserve_roles')
 if not isinstance(preserve,list) or any(not _nonempty(x) for x in preserve) or len(preserve)!=len(set(preserve)):e.append('preserve_roles:invalid')
 p=d.get('selection_policy',{})
 if not isinstance(p,dict) or p.get('id')!='pareto-then-novelty-v3':e.append('selection_policy.id:unsupported')
 else:
  if p.get('eligible_evidence_types')!=['measured','supplied']:e.append('selection_policy.eligible_evidence_types:invalid')
  if p.get('comparison_level_policy')!='same-level':e.append('selection_policy.comparison_level_policy:invalid')
  if p.get('holdout_failure_policy')!='eliminate-blind-fail':e.append('selection_policy.holdout_failure_policy:invalid')
  n=p.get('novelty_policy',{})
  if not isinstance(n,dict) or n.get('id')!='transformation-jaccard-v1' or n.get('source')!='derived':e.append('selection_policy.novelty_policy:invalid')
  if p.get('uncertainty_policy')!='margin-plus-min-delta-v1':e.append('selection_policy.uncertainty_policy:invalid')
 fp=d.get('finalist_policy',{})
 if not isinstance(fp,dict):e.append('finalist_policy:invalid')
 else:
  minimum=fp.get('minimum_evaluation_level');holdout=fp.get('holdout_policy')
  if minimum not in LEVELS:e.append('finalist_policy.minimum_evaluation_level:invalid')
  elif isinstance(levels,list) and minimum not in levels:e.append('finalist_policy.minimum_evaluation_level:not_allowed')
  if holdout not in FINALIST_HOLDOUT_POLICIES:e.append('finalist_policy.holdout_policy:invalid')
  if holdout=='blind-pass-required' and minimum!='L5-holdout':e.append('finalist_policy:blind_holdout_requires_l5')
 return sorted(set(e))

def main():
 p=argparse.ArgumentParser();p.add_argument('handoff');p.add_argument('--json-output');a=p.parse_args()
 try:d=json.loads(Path(a.handoff).read_text(encoding='utf-8'));e=validate(d)
 except Exception as exc:d={};e=[f'handoff:unreadable:{exc.__class__.__name__}']
 r={'status':'pass' if not e else 'fail','handoff_version':4,'errors':e};s=json.dumps(r,indent=2,sort_keys=True)+"\n"
 if a.json_output:Path(a.json_output).write_text(s,encoding='utf-8')
 print(s,end='');return 0 if not e else 2
if __name__=='__main__':sys.exit(main())
