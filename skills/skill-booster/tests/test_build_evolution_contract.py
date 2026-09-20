import importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('m',ROOT/'scripts/build_evolution_contract.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def test_build_v3_contract(tmp_path):
 target='sha256:test';
 cap={'schema_version':1,'target':{'name':'x','identity':target,'class':'orchestration-meta'},'capabilities':[{'id':'cap.a','name':'A','kind':'validation','owner':'x','status':'current','resources':[],'consumers':[],'validators':[],'evidence_refs':[],'invariants':['inv.a']}]}
 tr={'schema_version':1,'target_identity':target,'transformations':[{'id':'T1','change_intent':'repair','hypothesis_id':'H1','parent_candidate_ids':['BASELINE'],'capability_refs':['cap.a'],'files':['SKILL.md'],'operation_summary':'x','expected_effect':'y','evaluator_refs':['E'],'depends_on':[],'conflicts_with':[],'status':'planned','evidence_refs':['EV'],'addresses':['d1']}]}
 ev={'schema_version':1,'target_identity':target,'levels':[],'promotion':{}}
 hyp={'schema_version':'2.0','target':{'name':'x','identity':target},'items':[]}
 for n,d in [('cap.json',cap),('tr.json',tr),('ev.json',ev),('hyp.json',hyp)]: (tmp_path/n).write_text(json.dumps(d))
 h=json.loads((ROOT/'assets/templates/evolution-handoff.json.template').read_text());h['target_identity']=target;h['artifact_refs']={'capability_map':'cap.json','hypothesis_pool':'hyp.json','transformation_registry':'tr.json','evaluation_plan':'ev.json'}
 c=m.build(h,tmp_path);assert c['contract_version']==3;assert c['capability_invariants']==['inv.a'];assert c['transformation_registry'][0]['status']=='proposed';assert c['transformation_registry'][0]['addresses']==['d1']


def test_hypothesis_target_mismatch_fails(tmp_path):
 target='sha256:test'
 cap={'schema_version':1,'target':{'name':'x','identity':target,'class':'orchestration-meta'},'capabilities':[]}
 tr={'schema_version':1,'target_identity':target,'transformations':[]}
 ev={'schema_version':1,'target_identity':target,'levels':[],'promotion':{}}
 hyp={'schema_version':'2.0','target':{'name':'x','identity':'sha256:other'},'items':[]}
 for n,d in [('cap.json',cap),('tr.json',tr),('ev.json',ev),('hyp.json',hyp)]: (tmp_path/n).write_text(json.dumps(d))
 h=json.loads((ROOT/'assets/templates/evolution-handoff.json.template').read_text());h['target_identity']=target;h['artifact_refs']={'capability_map':'cap.json','hypothesis_pool':'hyp.json','transformation_registry':'tr.json','evaluation_plan':'ev.json'}
 try:m.build(h,tmp_path)
 except ValueError as exc:assert 'artifact target identity mismatch' in str(exc)
 else:assert False
