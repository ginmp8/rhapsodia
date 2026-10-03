from __future__ import annotations
import json
import hashlib
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
BOARD='docs/boards/example/2026/cycles/cycle-2026-10-03-delivery'
class MigrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.repo=Path(self.tmp.name);self.spec=self.repo/BOARD/'specs/spec-2026-10-03-sample';self.spec.mkdir(parents=True)
        for name in ['prd.md','tasks.md','validation.md','ops.yaml','implementation-notes.md']:(self.spec/name).write_text('# Synthetic source '+name+'\n')
    def tearDown(self):self.tmp.cleanup()
    def call(self,owner,command,args=(),expected=0):
        p=subprocess.run([sys.executable,'-B',str(ROOT/'skills'/owner/'scripts/migrate_artifacts.py'),command,'--repo-root',str(self.repo),*args],capture_output=True,text=True)
        self.assertEqual(p.returncode,expected,p.stdout+p.stderr);return json.loads(p.stdout)
    def plan(self,owner='mago'):
        return self.call(owner,'plan',['--legacy-root',BOARD,'--observed-at','2026-10-03T12:00:00Z'])
    def apply(self,plan,owner='mago',expected=0):
        path=self.repo/'plan.json';path.write_text(json.dumps(plan));return self.call(owner,'apply',['--plan',str(path)],expected)
    def test_plan_is_read_only(self):
        before={p.relative_to(self.repo):p.read_bytes() for p in self.repo.rglob('*') if p.is_file()};plan=self.plan()
        after={p.relative_to(self.repo):p.read_bytes() for p in self.repo.rglob('*') if p.is_file()}
        self.assertEqual(before,after);self.assertEqual(len(plan['items']),3)
    def test_each_owner_migrates_only_its_artifacts(self):
        for owner,count in [('mago',3),('nomia',1),('magia',1)]:
            plan=self.plan(owner);self.assertEqual(len(plan['items']),count);self.apply(plan,owner)
            for item in plan['items']:self.assertEqual((self.repo/item['source']).read_bytes(),(self.repo/item['artifact']['source']['path']).read_bytes())
    def test_idempotent_replay(self):
        plan=self.plan();self.apply(plan);self.assertEqual(self.apply(plan)['status'],'unchanged')
    def test_original_source_drift_rejected_before_write(self):
        plan=self.plan();(self.spec/'prd.md').write_text('changed');self.apply(plan,expected=1)
        self.assertFalse((self.repo/'docs/specs').exists())
    def test_target_conflict_preserved(self):
        plan=self.plan();target=self.repo/plan['items'][0]['artifact']['source']['path'];target.parent.mkdir(parents=True);target.write_text('user content')
        self.apply(plan,expected=1);self.assertEqual(target.read_text(),'user content')
    def test_cross_owner_plan_rejected(self):self.apply(self.plan(),owner='nomia',expected=1)
    def test_legacy_root_escape_rejected(self):self.call('mago','plan',['--legacy-root','../outside','--observed-at','2026-10-03T12:00:00Z'],expected=1)
    def test_native_index_does_not_require_legacy_board_after_migration(self):
        self.apply(self.plan());shutil.rmtree(self.repo/'docs/boards')
        p=subprocess.run([sys.executable,'-B',str(ROOT/'skills/rhapsodia-workspace/scripts/workspace.py'),'validate','--repo-root',str(self.repo)],capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stdout+p.stderr)
    def test_migration_never_invents_completed_state(self):
        plan=self.plan();self.assertTrue(all(x['artifact']['state']['value']=='unknown' for x in plan['items']))
    def interrupted(self,owner='mago'):
        plan=self.plan(owner);item=plan['items'][0]
        root=self.repo/plan['artifact_root'];target=self.repo/item['artifact']['source']['path']
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((self.repo/item['source']).read_bytes())
        value={'owner':owner,'plan_sha256':'a'*64,'created':[{'path':target.relative_to(self.repo).as_posix(),'sha256':hashlib.sha256(target.read_bytes()).hexdigest()}]}
        journal=root/'.migration-journal.json';journal.write_text(json.dumps(value))
        return root,target,journal,value
    def test_recovery_requires_explicit_exact_journal_approval(self):
        for owner in ('mago','magia','nomia'):
            with self.subTest(owner=owner):
                root,target,journal,value=self.interrupted(owner)
                self.call(owner,'recover',expected=1);self.assertTrue(target.exists())
                approval=self.call(owner,'recovery-plan')['journal_sha256']
                result=self.call(owner,'recover',['--journal-sha256',approval])
                self.assertEqual(result['status'],'recovered');self.assertFalse(target.exists());self.assertFalse(journal.exists())
                self.assertTrue((self.spec/'tasks.md').exists())
    def test_recovery_refuses_to_delete_subsequent_user_edits(self):
        root,target,journal,value=self.interrupted();target.write_text('edited after interruption')
        approval=self.call('mago','recovery-plan')['journal_sha256']
        self.call('mago','recover',['--journal-sha256',approval],expected=1)
        self.assertEqual(target.read_text(),'edited after interruption');self.assertTrue(journal.exists())
    def test_recovery_finalizes_already_committed_copy(self):
        root,target,journal,value=self.interrupted();receipt=root/'.migration-receipts'/('a'*64+'.json')
        receipt.parent.mkdir();receipt.write_text(json.dumps({'status':'pass','owner':'mago','plan_sha256':'a'*64}))
        approval=self.call('mago','recovery-plan')['journal_sha256']
        result=self.call('mago','recover',['--journal-sha256',approval])
        self.assertEqual(result['status'],'finalized');self.assertTrue(target.exists());self.assertFalse(journal.exists())
    def test_recovery_rejects_cross_root_journal_before_any_deletion(self):
        root,target,journal,value=self.interrupted()
        value['created'].append({'path':(self.spec/'tasks.md').relative_to(self.repo).as_posix(),'sha256':hashlib.sha256((self.spec/'tasks.md').read_bytes()).hexdigest()})
        journal.write_text(json.dumps(value));approval=self.call('mago','recovery-plan')['journal_sha256']
        self.call('mago','recover',['--journal-sha256',approval],expected=1)
        self.assertTrue(target.exists());self.assertTrue((self.spec/'tasks.md').exists())
    def test_source_symlink_rejected(self):
        (self.spec/'alias.md').symlink_to(self.spec/'prd.md');self.call('mago','plan',['--legacy-root',BOARD,'--observed-at','2026-10-03T12:00:00Z'],expected=1)

if __name__=='__main__':unittest.main()
