from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import copy,json,sys,tempfile,unittest
from pathlib import Path
import native_execution as execution
from artifact_protocol import ContractError,digest

class ExecutionConsistencyGuards(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.repo=Path(self.tmp.name)
        (self.repo/'src').mkdir();(self.repo/'src/app.py').write_text('value = 42\n')
        root=self.repo/'docs/specs/sample';root.mkdir(parents=True)
        self.ident=root/'planning-identity.json';self.ident.write_text(json.dumps({'schema_version':'1.0.0','producer':'mago','work_item_id':'sample','spec_id':'spec-2026-10-03-sample','created_at':'2026-10-03T12:00:00Z'}))
        self.tasks=root/'tasks.md';self.tasks.write_text('- [ ] task001: First task\n  - Requirements: REQ-001\n  - Acceptance: AC-001\n  - Validations: VAL-001\n  - Dependencies: none\n- [ ] task002: Second task\n  - Requirements: REQ-001\n  - Acceptance: AC-001\n  - Validations: VAL-001\n  - Dependencies: task001\n')
        self.req={'schema_version':'1.0.0','mode':'ralph','work_item_id':'sample','spec_id':'spec-2026-10-03-sample','task_id':'task001',
                  'requirements':['REQ-001'],'acceptance':['AC-001'],'validations':['VAL-001'],
                  'planning_sources':[{'path':p.relative_to(self.repo).as_posix(),'sha256':digest(p.read_bytes())} for p in [self.ident,self.tasks]],
                  'candidate_roots':['src'],'checks':[{'validation_ref':'VAL-001','argv':[sys.executable,'-c','assert True'],'cwd':'.','timeout_seconds':5}],
                  'dependency_receipts':[]}
    def tearDown(self):self.tmp.cleanup()
    def test_identity_and_task_source_must_be_colocated(self):
        other=self.repo/'docs/specs/other/tasks.md';other.parent.mkdir();other.write_bytes(self.tasks.read_bytes())
        self.req['planning_sources'][1]={'path':other.relative_to(self.repo).as_posix(),'sha256':digest(other.read_bytes())}
        with self.assertRaises(ContractError):execution.validate_request(self.repo,self.req)
    def test_duplicate_task_identity_rejected(self):
        self.tasks.write_text(self.tasks.read_text()+'\n'+self.tasks.read_text());self.req['planning_sources'][1]['sha256']=digest(self.tasks.read_bytes())
        with self.assertRaises(ContractError):execution.validate_request(self.repo,self.req)
    def test_artifact_ancestor_cannot_be_candidate_root(self):
        with self.assertRaises(ContractError):execution.tree(self.repo,['docs'])
    def test_nonoverlapping_similar_prefix_is_allowed(self):
        root=self.repo/'docs/productivity';root.mkdir();(root/'guide.md').write_text('Guide\n')
        self.assertIn('docs/productivity/guide.md',execution.tree(self.repo,['docs/productivity']))
    def test_dependency_receipt_is_historical_not_current_candidate_proof(self):
        result=execution.run(self.repo,self.req);receipt=self.repo/result['receipt_path']
        (self.repo/'src/app.py').write_text('value = 43\n')
        with self.assertRaises(ContractError):execution.validate_receipt(self.repo,receipt)
        dependent=copy.deepcopy(self.req);dependent['task_id']='task002'
        dependent['dependency_receipts']=[{'path':receipt.relative_to(self.repo).as_posix(),'sha256':digest(receipt.read_bytes()),'task_id':'task001'}]
        result=execution.run(self.repo,dependent)
        self.assertEqual(result['status'],'passed');execution.validate_receipt(self.repo,self.repo/result['receipt_path'])
    def test_historical_dependency_hash_is_still_required(self):
        result=execution.run(self.repo,self.req);receipt=self.repo/result['receipt_path']
        dependent=copy.deepcopy(self.req);dependent['task_id']='task002'
        dependent['dependency_receipts']=[{'path':receipt.relative_to(self.repo).as_posix(),'sha256':'0'*64,'task_id':'task001'}]
        with self.assertRaises(ContractError):execution.run(self.repo,dependent)
if __name__=='__main__':unittest.main()
