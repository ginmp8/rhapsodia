from __future__ import annotations
import copy,json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from artifact_protocol import ContractError,canonical_bytes,digest
from native_artifacts import policy,publish,resolve_owned_root
import migrate_artifacts as migration
import test_native_local as native_fixtures

class PublicationGuards(unittest.TestCase):
    def setUp(self):
        self.fixture=native_fixtures.NativeLocalTests();self.fixture.setUp();self.repo=self.fixture.repo;self.request=self.fixture.request
    def tearDown(self):self.fixture.tearDown()
    def test_secret_reason_rejected_before_publication(self):
        self.request['reason']='Bearer '+'z'*32
        with self.assertRaises(ContractError):publish(self.repo,self.request)
        self.assertFalse(Path(str(self.fixture.source)+'.artifact.json').exists())
    def test_invalid_state_has_contract_error(self):
        self.request['artifact']['state']=[]
        with self.assertRaises(ContractError):publish(self.repo,self.request)
    def test_invalid_existing_metadata_has_contract_error(self):
        Path(str(self.fixture.source)+'.artifact.json').write_text('[]')
        with self.assertRaises(ContractError):resolve_owned_root(self.repo)

class MigrationGuards(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.repo=Path(self.tmp.name)
        self.board='docs/boards/example/2026/cycles/cycle-2026-10-03-example'
        self.legacy=self.repo/self.board/'specs/spec-2026-10-03-sample';self.legacy.mkdir(parents=True)
        names=list(migration.NAMES[policy()['producer']])[:2]
        for name in names:(self.legacy/name).write_text('# Retained legacy artifact\n')
        self.value=migration.plan(self.repo,self.board,'2026-10-03T12:00:00Z')
    def tearDown(self):self.tmp.cleanup()
    def test_readiness_cannot_be_invented_by_copy_migration(self):
        self.value['items'][0]['artifact']['state']['value']='ready'
        with self.assertRaises(ContractError):migration.check_plan(self.repo,self.value)
    def test_migration_must_retain_provenance(self):
        self.value['items'][0]['artifact']['provenance']['kind']='authored'
        with self.assertRaises(ContractError):migration.check_plan(self.repo,self.value)
    def test_duplicate_artifact_ids_rejected(self):
        self.value['items'][1]['artifact']['artifact_id']=self.value['items'][0]['artifact']['artifact_id']
        with self.assertRaises(ContractError):migration.check_plan(self.repo,self.value)
    def test_plan_and_check_preserve_original_bytes(self):
        before={p.name:p.read_bytes() for p in self.legacy.iterdir()};migration.check_plan(self.repo,self.value)
        self.assertEqual(before,{p.name:p.read_bytes() for p in self.legacy.iterdir()})
if __name__=='__main__':unittest.main()
