"""Independent negative cases for the shared artifact data contract."""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import copy
import tempfile
import unittest
from pathlib import Path
import artifact_protocol as protocol


def record(path='docs/specs/sample/tasks.md'):
    return {'schema_version':'1.0.0','artifact_id':'mago:sample:tasks','producer':'mago','artifact_type':'tasks',
            'work_item_id':'sample','workflow_id':None,'title':'Bounded planning tasks',
            'state':{'dimension':'planning','value':'planned'},'lifecycle':'active',
            'created_at':'2026-10-03T12:00:00Z','updated_at':'2026-10-03T12:00:00Z',
            'source':{'path':path,'sha256':'0'*64},'relations':[],
            'privacy':{'classification':'internal','allowed_destinations':['local'],'contains_secrets':False,'external_share_allowed':False},
            'provenance':{'kind':'authored','evidence_refs':[],'source_handoff_id':None}}

class NativeConsistencyGuards(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.repo=Path(self.tmp.name)
        self.record=record();p=self.repo/self.record['source']['path'];p.parent.mkdir(parents=True);p.write_text('# Bounded plan\n')
        self.record['source']['sha256']=protocol.digest(p.read_bytes())
        self.manifest=Path(str(p)+'.artifact.json');self.manifest.write_bytes(protocol.canonical_bytes(self.record))
        self.receipt={'schema_version':'1.0.0','owner':'mago','workflow_id':None,'validation':'passed','artifact_actions':[
            {'artifact_id':self.record['artifact_id'],'artifact_type':'tasks','action':'created','source_path':self.record['source']['path'],
             'manifest_path':self.manifest.relative_to(self.repo).as_posix(),'source_sha256':self.record['source']['sha256'],
             'manifest_sha256':protocol.digest(self.manifest.read_bytes()),'previous_manifest_sha256':None,'reason':'Publish validated plan'}]}
    def tearDown(self):self.tmp.cleanup()
    def test_positive_created_receipt(self):protocol.validate_actions(self.receipt,self.repo)
    def test_unchanged_requires_matching_prior_revision(self):
        self.receipt['artifact_actions'][0]['action']='unchanged'
        with self.assertRaises(protocol.ContractError):protocol.validate_actions(self.receipt,self.repo)
    def test_updated_requires_prior_revision(self):
        self.receipt['artifact_actions'][0]['action']='updated'
        with self.assertRaises(protocol.ContractError):protocol.validate_actions(self.receipt,self.repo)
    def test_updated_cannot_claim_identical_revision(self):
        a=self.receipt['artifact_actions'][0];a['action']='updated';a['previous_manifest_sha256']=a['manifest_sha256']
        with self.assertRaises(protocol.ContractError):protocol.validate_actions(self.receipt,self.repo)
    def test_receipt_reason_rejects_secret_material(self):
        self.receipt['artifact_actions'][0]['reason']='Bearer '+'a'*32
        with self.assertRaises(protocol.ContractError):protocol.validate_actions(self.receipt,self.repo)
    def test_windows_reserved_characters_rejected(self):
        for char in '*?"<>|':
            with self.subTest(char=char):
                with self.assertRaises(protocol.ContractError):protocol.safe_relative('docs/item'+char+'.md')
    def test_symlink_in_repository_ancestor_rejected(self):
        real=self.repo/'real';(real/'repo').mkdir(parents=True)
        link=self.repo/'link';link.symlink_to(real,target_is_directory=True)
        with self.assertRaises(protocol.ContractError):protocol.confined(link/'repo','docs/file.md')

if __name__=='__main__':unittest.main()
