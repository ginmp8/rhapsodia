from __future__ import annotations
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

class NativeExecutionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.repo=Path(self.tmp.name)
        (self.repo/'src').mkdir();(self.repo/'src/app.py').write_text('value = 42\n')
        self.req={'schema_version':'1.0.0','mode':'adhoc','work_item_id':'sample','spec_id':None,'task_id':None,
                  'requirements':['REQ-001'],'acceptance':['AC-001'],'validations':['VAL-001'],'planning_sources':[],
                  'candidate_roots':['src'],'checks':[{'validation_ref':'VAL-001','argv':[sys.executable,'-c','assert 2 + 2 == 4'], 'cwd':'.','timeout_seconds':5}],
                  'dependency_receipts':[]}
    def tearDown(self):self.tmp.cleanup()
    def call(self,command,request=None,path=None,expected=0,extra=()):
        if path is None:
            path=self.repo/'request.json';path.write_text(json.dumps(request or self.req))
        run=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/native_execution.py'),command,'--repo-root',str(self.repo),'--input',str(path),*extra],text=True,capture_output=True)
        self.assertEqual(run.returncode,expected,run.stdout+run.stderr)
        return json.loads(run.stdout)
    def run_check(self,expected=0):return self.call('run',expected=expected,extra=['--trust-command'])
    def test_command_requires_explicit_trust(self):self.call('run',expected=1)
    def test_real_command_recorded_and_closed_without_board(self):
        run=self.run_check();receipt=self.repo/run['receipt_path'];value=json.loads(receipt.read_text())
        self.assertEqual(value['checks'][0]['returncode'],0);self.assertEqual(value['evidence_kind'],'executed')
        closed=self.call('close',path=receipt);self.assertEqual(closed['planning_files_modified'],False)
        self.assertFalse((self.repo/'docs/boards').exists());self.assertFalse((self.repo/'docs/specs').exists())
        self.assertEqual(self.call('close',path=receipt)['status'],'unchanged')
    def test_failed_command_cannot_close(self):
        self.req['checks'][0]['argv']=[sys.executable,'-c','raise SystemExit(7)'];run=self.run_check(expected=1)
        value=json.loads((self.repo/run['receipt_path']).read_text());self.assertEqual(value['checks'][0]['returncode'],7)
        self.call('close',path=self.repo/run['receipt_path'],expected=1)
    def test_stale_candidate_invalidates_proof(self):
        run=self.run_check();(self.repo/'src/app.py').write_text('value = 43\n')
        self.call('close',path=self.repo/run['receipt_path'],expected=1)
    def test_validation_ref_cannot_be_omitted(self):
        self.req['validations'].append('VAL-002');self.run_check(expected=1)
    def test_source_mutation_during_check_blocks_receipt(self):
        self.req['checks'][0]['argv']=[sys.executable,'-c',"from pathlib import Path;Path('src/app.py').write_text('changed')"]
        self.run_check(expected=1);self.assertEqual(list(self.repo.rglob('*execution-state.json')),[])
    def test_timeout_is_not_a_pass(self):
        self.req['checks'][0]['argv']=[sys.executable,'-c','import time;time.sleep(2)'];self.req['checks'][0]['timeout_seconds']=1
        run=self.run_check(expected=1);receipt=json.loads((self.repo/run['receipt_path']).read_text());self.assertIsNone(receipt['checks'][0]['returncode'])
    def test_executed_command_identity_must_match_request(self):
        run=self.run_check();p=self.repo/run['receipt_path'];value=json.loads(p.read_text());value['checks'][0]['argv']=['fabricated'];p.write_text(json.dumps(value))
        self.call('validate',path=p,expected=1)
    def test_protected_candidate_root_fails(self):
        self.req['candidate_roots']=['docs/implementation'];self.run_check(expected=1)
    def ralph(self):
        root=self.repo/'docs/specs/sample';root.mkdir(parents=True)
        identity=root/'planning-identity.json';identity.write_text(json.dumps({'schema_version':'1.0.0','producer':'mago','work_item_id':'sample','spec_id':'spec-2026-10-03-sample','created_at':'2026-10-03T12:00:00Z'}))
        task=root/'tasks.md';task.write_text('- [ ] task001: Synthetic task\n  - Requirements: REQ-001\n  - Acceptance: AC-001\n  - Validations: VAL-001\n  - Dependencies: none\n')
        self.req.update({'mode':'ralph','spec_id':'spec-2026-10-03-sample','task_id':'task001','planning_sources':[{'path':p.relative_to(self.repo).as_posix(),'sha256':digest(p)} for p in (identity,task)]})
        return task,identity
    def test_ralph_preserves_planning_source_bytes(self):
        task,identity=self.ralph();before={p:p.read_bytes() for p in (task,identity)}
        run=self.run_check();self.call('close',path=self.repo/run['receipt_path']);self.assertEqual(before,{p:p.read_bytes() for p in before})
    def test_ralph_cannot_redefine_acceptance(self):
        self.ralph();self.req['acceptance']=['AC-002'];self.run_check(expected=1)
    def test_ralph_cannot_skip_dependency(self):
        task,identity=self.ralph();task.write_text(task.read_text().replace('Dependencies: none','Dependencies: task002'))
        self.req['planning_sources'][-1]['sha256']=digest(task);self.run_check(expected=1)
    def test_planning_source_change_invalidates_receipt(self):
        task,_=self.ralph();run=self.run_check();task.write_text(task.read_text()+'changed intent\n')
        self.call('close',path=self.repo/run['receipt_path'],expected=1)
    def test_new_candidate_file_invalidates_receipt(self):
        run=self.run_check();(self.repo/'src/new.py').write_text('new = 1\n');self.call('validate',path=self.repo/run['receipt_path'],expected=1)
    def test_symlink_candidate_rejected(self):
        (self.repo/'src/link.py').symlink_to(self.repo/'src/app.py');self.run_check(expected=1)

if __name__=='__main__':unittest.main()
