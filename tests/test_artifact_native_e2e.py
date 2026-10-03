"""Execute the native producer pipeline in an isolated repository, without a Board."""
from __future__ import annotations
import hashlib,json,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
class ArtifactNativeE2ETests(unittest.TestCase):
 def test_owner_pipeline_publication_execution_and_rebuild(self):
  with tempfile.TemporaryDirectory() as td:
   repo=Path(td)
   def call(owner,script,*args):
    p=subprocess.run([sys.executable,'-B',str(ROOT/'skills'/owner/'scripts'/script),*map(str,args)],capture_output=True,text=True)
    self.assertEqual(p.returncode,0,p.stdout+p.stderr);return p.stdout
   def data(name,value):
    path=repo/name;path.write_text(json.dumps(value));return path
   # Governance has its own schema and local work-item identity, never a minted spec ID.
   call('nomia','write_ops_scaffold.py','docs/product/sample/ops.yaml','--repo-root',repo,'--work-item','sample')
   call('nomia','validate_ops.py',repo/'docs/product/sample/ops.yaml')
   call('mago','native_planning.py','identity','--repo-root',repo,'--work-item','sample','--created-at','2026-10-03T12:00:00Z')
   plan=repo/'docs/specs/sample';identity=plan/'planning-identity.json'
   # Use the unchanged canonical task contract fixture, not a relaxed E2E-only task shape.
   import importlib.util
   spec=importlib.util.spec_from_file_location('native_task_fixture',ROOT/'skills/mago/tests/test_optional_task_phases_v2.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
   (plan/'tasks.md').write_text(m.document().replace('  - Decisions: DECISION-001','  - Decisions: none'))
   (plan/'prd.md').write_text('# Requirements\n### REQ-001 Result\nBounded request.\n### AC-001 Result\n- Requirements: REQ-001\n')
   (plan/'validation.md').write_text('# Validation\n### VAL-001 Check\n- Requirements: REQ-001\n- Acceptance: AC-001\n- Tasks: task001, task002, task003\n')
   (plan/'notes.md').write_text('# Planning notes\nPlanning-only rationale and sources.\n')
   call('mago','native_planning.py','validate','--repo-root',repo,'--work-item','sample')
   before={p:p.read_bytes() for p in (repo/'docs').rglob('*') if p.is_file()}
   (repo/'src').mkdir();(repo/'src/app.py').write_text('value = 42\n')
   req={'schema_version':'1.0.0','mode':'ralph','work_item_id':'sample','spec_id':'spec-2026-10-03-sample','task_id':'task001','requirements':['REQ-001'],'acceptance':['AC-001'],'validations':['VAL-001'],'planning_sources':[{'path':p.relative_to(repo).as_posix(),'sha256':sha(p)} for p in (identity,plan/'tasks.md')],'candidate_roots':['src'],'checks':[{'validation_ref':'VAL-001','argv':[sys.executable,'-c',"from pathlib import Path;scope={};exec(Path('src/app.py').read_text(),scope);assert scope['value']==42"],'cwd':'.','timeout_seconds':10}],'dependency_receipts':[]}
   result=json.loads(call('magia','native_execution.py','run','--repo-root',repo,'--input',data('run-request.json',req),'--trust-command'))
   receipt=repo/result['receipt_path'];call('magia','native_execution.py','close','--repo-root',repo,'--input',receipt)
   self.assertEqual(before,{p:p.read_bytes() for p in before})
   # Publish sidecars only through each producer's own command, then consume them generically.
   items=[('nomia','ops','governance','intake','docs/product/sample/ops.yaml'),('mago','tasks','planning','ready','docs/specs/sample/tasks.md'),('magia','execution-receipt','execution','validated',result['receipt_path'])]
   ids=[]
   for owner,kind,dim,state,path in items:
    aid=owner+':sample:'+kind
    artifact={'schema_version':'1.0.0','artifact_id':aid,'producer':owner,'artifact_type':kind,'work_item_id':'sample','workflow_id':None,'title':'Synthetic native pipeline','state':{'dimension':dim,'value':state},'lifecycle':'active','created_at':'2026-10-03T12:00:00Z','updated_at':'2026-10-03T12:00:00Z','source':{'path':path,'sha256':'0'*64},'relations':[{'type':'implements','target':ids[-1]}] if ids else [],'privacy':{'classification':'internal','allowed_destinations':['local'],'contains_secrets':False,'external_share_allowed':False},'provenance':{'kind':'authored','evidence_refs':[],'source_handoff_id':None}}
    request={'artifact':artifact,'expected_manifest_sha256':None,'reason':'Executed synthetic E2E publication'}
    actions=json.loads(call(owner,'native_artifacts.py','publish','--repo-root',repo,'--input',data('publish-request.json',request)))
    call(owner,'native_artifacts.py','validate-actions','--repo-root',repo,'--input',data('actions.json',actions));ids.append(aid)
   sources={p:p.read_bytes() for p in (repo/'docs').rglob('*') if p.is_file()}
   call('rhapsodia-workspace','workspace.py','index','--repo-root',repo);call('rhapsodia-workspace','workspace.py','render','--repo-root',repo)
   catalog=repo/'.rhapsodia/catalog/catalog.json';original=catalog.read_bytes();self.assertEqual(len(json.loads(original)['entries']),3)
   self.assertEqual(sources,{p:p.read_bytes() for p in sources});catalog.unlink();call('rhapsodia-workspace','workspace.py','index','--repo-root',repo);self.assertEqual(catalog.read_bytes(),original)
   self.assertFalse((repo/'docs/boards').exists())
