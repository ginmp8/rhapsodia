from __future__ import annotations
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
SCOPES={'mago':('docs/specs','technical-design','planning'),'nomia':('docs/product','feature','governance'),'magia':('docs/implementation','implementation-notes','execution')}

def request(owner='mago'):
    root,kind,dim=SCOPES[owner]
    return {'artifact':{'schema_version':'1.0.0','artifact_id':owner+':sample:'+kind,'producer':owner,
            'artifact_type':kind,'work_item_id':'sample','workflow_id':None,'title':'Synthetic sample',
            'state':{'dimension':dim,'value':'draft'},'lifecycle':'active','created_at':'2026-10-03T12:00:00Z',
            'updated_at':'2026-10-03T12:00:00Z','source':{'path':root+'/sample/'+kind+'.md','sha256':'0'*64},
            'relations':[],'privacy':{'classification':'internal','allowed_destinations':['local'],'contains_secrets':False,
                                    'external_share_allowed':False},'provenance':{'kind':'authored','evidence_refs':[],'source_handoff_id':None}},
            'expected_manifest_sha256':None,'reason':'Create synthetic test artifact'}

class NativeArtifactTests(unittest.TestCase):
    def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.repo=Path(self.tmp.name)
    def tearDown(self):self.tmp.cleanup()
    def run_cli(self,owner,req,command='publish',expected=0):
        path=self.repo/'request.json';path.write_text(json.dumps(req))
        p=subprocess.run([sys.executable,'-B',str(ROOT/'skills'/owner/'scripts/native_artifacts.py'),command,
                          '--repo-root',str(self.repo),'--input',str(path)],capture_output=True,text=True)
        self.assertEqual(p.returncode,expected,p.stdout+p.stderr)
        return json.loads(p.stdout)
    def prepare(self,owner='mago'):
        req=request(owner);source=self.repo/req['artifact']['source']['path'];source.parent.mkdir(parents=True,exist_ok=True)
        source.write_text('# Synthetic artifact\n');return req,source
    def test_each_owner_runs_without_peers_or_board(self):
        for owner in SCOPES:
            with self.subTest(owner=owner):
                req,src=self.prepare(owner);result=self.run_cli(owner,req)
                self.assertEqual(result['artifact_actions'][0]['action'],'created')
                self.assertFalse((self.repo/'docs/boards').exists())
                self.run_cli(owner,result,'validate-actions')
    def test_rerun_is_idempotent(self):
        req,src=self.prepare();first=self.run_cli('mago',req);before=Path(str(src)+'.artifact.json').read_bytes()
        second=self.run_cli('mago',req);self.assertEqual(second['artifact_actions'][0]['action'],'unchanged')
        self.assertEqual(before,Path(str(src)+'.artifact.json').read_bytes())
    def test_update_requires_exact_previous_hash(self):
        req,src=self.prepare();first=self.run_cli('mago',req);src.write_text('changed\n')
        req['artifact']['updated_at']='2026-10-03T13:00:00Z'
        result=self.run_cli('mago',req,expected=1);self.assertEqual(result['code'],'REVISION_CONFLICT')
        req['expected_manifest_sha256']=first['artifact_actions'][0]['manifest_sha256']
        result=self.run_cli('mago',req);self.assertEqual(result['artifact_actions'][0]['action'],'updated')
    def test_source_changes_make_old_receipts_stale(self):
        req,src=self.prepare();receipt=self.run_cli('mago',req);src.write_text('changed')
        self.run_cli('mago',receipt,'validate-actions',expected=1)
    def test_wrong_owner_rejected(self):
        req,src=self.prepare('nomia');result=self.run_cli('mago',req,expected=1)
        self.assertEqual(result['code'],'CROSS_OWNER_PUBLICATION')
    def test_cross_owner_path_rejected(self):
        req,src=self.prepare();req['artifact']['source']['path']='docs/product/sample/design.md'
        self.run_cli('mago',req,expected=1)
    def test_cross_owner_dimension_rejected(self):
        req,src=self.prepare();req['artifact']['state']['dimension']='governance';self.run_cli('mago',req,expected=1)
    def test_deprecate(self):
        req,src=self.prepare();first=self.run_cli('mago',req)
        req['expected_manifest_sha256']=first['artifact_actions'][0]['manifest_sha256'];req['artifact']['lifecycle']='deprecated'
        result=self.run_cli('mago',req);self.assertEqual(result['artifact_actions'][0]['action'],'deprecated')
    def test_remove_requires_owner_deletion_and_prior_record(self):
        req,src=self.prepare();first=self.run_cli('mago',req);req['artifact']['lifecycle']='removed'
        req['expected_manifest_sha256']=first['artifact_actions'][0]['manifest_sha256'];self.run_cli('mago',req,expected=1)
        src.unlink();result=self.run_cli('mago',req);self.assertEqual(result['artifact_actions'][0]['action'],'removed')
        self.run_cli('mago',result,'validate-actions');self.run_cli('mago',req)
    def test_immutable_work_item(self):
        req,src=self.prepare();first=self.run_cli('mago',req)
        req['expected_manifest_sha256']=first['artifact_actions'][0]['manifest_sha256'];req['artifact']['work_item_id']='different'
        self.run_cli('mago',req,expected=1)
    def test_live_lock_not_taken_over(self):
        req,src=self.prepare();lock=self.repo/'docs/specs/.artifact-write.lock';lock.write_text(str(__import__('os').getpid()))
        result=self.run_cli('mago',req,expected=1);self.assertEqual(result['code'],'WRITE_LOCK_HELD');self.assertTrue(lock.exists())
    def test_artifact_id_collision(self):
        req,src=self.prepare();self.run_cli('mago',req)
        new=self.repo/'docs/specs/sample/another.md';new.write_text('new');req['artifact']['source']['path']=new.relative_to(self.repo).as_posix()
        result=self.run_cli('mago',req,expected=1);self.assertEqual(result['code'],'DUPLICATE_ARTIFACT_ID')
    def test_forged_action_owner_fails(self):
        req,src=self.prepare();result=self.run_cli('mago',req);result['owner']='nomia'
        self.run_cli('mago',result,'validate-actions',expected=1)

if __name__=='__main__':unittest.main()
