"""Frozen acceptance checks for artifact metadata, path safety and schema parity."""
from __future__ import annotations
import copy
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from artifact_protocol import (ContractError, atomic_write, canonical_bytes, confined, digest,
                               discover, load_json, schema_errors, schema_for, validate_record)

def record(source='docs/specs/sample/technical-design.md', content=b'# Technical design\n'):
    return {'schema_version':'1.0.0','artifact_id':'mago:sample:design','producer':'mago',
            'artifact_type':'technical-design','work_item_id':'sample','workflow_id':None,
            'title':'Example design','state':{'dimension':'planning','value':'ready'},
            'lifecycle':'active','created_at':'2026-10-03T12:00:00Z','updated_at':'2026-10-03T12:00:00Z',
            'source':{'path':source,'sha256':digest(content)},'relations':[],
            'privacy':{'classification':'internal','allowed_destinations':['local'],
                       'contains_secrets':False,'external_share_allowed':False},
            'provenance':{'kind':'authored','evidence_refs':[],'source_handoff_id':None}}

class ProtocolTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.root=Path(self.temp.name)
        self.value=record(); self.source=self.root/self.value['source']['path']
        self.source.parent.mkdir(parents=True); self.source.write_bytes(b'# Technical design\n')
        self.manifest=Path(str(self.source)+'.artifact.json')
        self.manifest.write_bytes(canonical_bytes(self.value))
    def tearDown(self): self.temp.cleanup()
    def test_valid_record(self): validate_record(self.value,self.root,self.manifest)
    def test_stale_source(self):
        self.source.write_text('changed')
        with self.assertRaisesRegex(ContractError,'STALE_SOURCE'):validate_record(self.value,self.root,self.manifest)
    def test_missing_source(self):
        self.source.unlink()
        with self.assertRaisesRegex(ContractError,'INVALID_SOURCE'):validate_record(self.value,self.root,self.manifest)
    def test_no_metadata_authority_in_removed_source(self):
        self.value['lifecycle']='removed'
        with self.assertRaisesRegex(ContractError,'REMOVED_SOURCE'):validate_record(self.value,self.root,self.manifest)
        self.source.unlink();validate_record(self.value,self.root,self.manifest)
    def test_source_sidecar_location(self):
        with self.assertRaisesRegex(ContractError,'SIDECAR'):validate_record(self.value,self.root,self.root/'elsewhere.json')
    def test_unknown_fields(self):
        self.value['future_field']=True
        with self.assertRaises(ContractError):validate_record(self.value)
    def test_nested_unknown_fields(self):
        self.value['state']['authority']='god-mode'
        with self.assertRaises(ContractError):validate_record(self.value)
    def test_wrong_owner_namespace(self):
        self.value['producer']='nomia'
        with self.assertRaisesRegex(ContractError,'NAMESPACE'):validate_record(self.value)
    def test_impossible_dates(self):
        for stamp in ['2026-02-30T12:00:00Z','2026-13-01T12:00:00Z','2026-10-03T25:00:00Z']:
            with self.subTest(stamp=stamp):
                value=copy.deepcopy(self.value);value['created_at']=stamp
                with self.assertRaises(ContractError):validate_record(value)
    def test_valid_leap_day(self):
        self.value['created_at']='2024-02-29T00:00:00Z';validate_record(self.value)
    def test_inverted_dates(self):
        self.value['updated_at']='2026-10-02T00:00:00Z'
        with self.assertRaisesRegex(ContractError,'INVERTED'):validate_record(self.value)
    def test_no_derived_source(self):
        self.value['source']['path']='.rhapsodia/catalog/catalog.json'
        with self.assertRaisesRegex(ContractError,'DERIVED'):validate_record(self.value)
    def test_local_confidential_allowed_public_denied(self):
        self.value['privacy']['classification']='confidential';validate_record(self.value)
        self.value['privacy']['allowed_destinations']=['public']
        with self.assertRaisesRegex(ContractError,'PUBLIC_EXPORT'):validate_record(self.value)
    def test_boolean_is_not_integer(self):
        self.value['privacy']['contains_secrets']=0
        with self.assertRaises(ContractError):validate_record(self.value)
    def test_duplicate_relations(self):
        self.value['relations']=[{'type':'implements','target':'nomia:sample:feature'}]*2
        with self.assertRaises(ContractError):validate_record(self.value)
    def test_self_relation(self):
        self.value['relations']=[{'type':'depends_on','target':self.value['artifact_id']}]
        with self.assertRaisesRegex(ContractError,'SELF_RELATION'):validate_record(self.value)
    def test_duplicate_json_keys(self):
        p=self.root/'bad.json';p.write_text('{"a":1,"a":2}')
        with self.assertRaisesRegex(ContractError,'DUPLICATE'):load_json(p)
    def test_nonfinite_json(self):
        p=self.root/'bad.json';p.write_text('{"a":NaN}')
        with self.assertRaises(ContractError):load_json(p)
    def test_portable_path_rejections(self):
        for path in ['../escape','/etc/passwd','docs/../escape','docs//a','docs/./a','C:\\temp\\a','docs/.env','docs/key.pem','docs/CON','docs/a.']:
            with self.subTest(path=path):
                with self.assertRaises(ContractError):confined(self.root,path)
    def test_symlink_source_rejected(self):
        self.source.unlink();self.source.symlink_to(self.manifest)
        with self.assertRaises(ContractError):validate_record(self.value,self.root,self.manifest)
    def test_symlink_directory_rejected(self):
        (self.root/'outside-link').symlink_to(self.source.parent,target_is_directory=True)
        with self.assertRaises(ContractError):confined(self.root,'outside-link/file.md')
    def test_hardlink_rejected(self):
        os.link(self.source,self.root/'alias.md')
        with self.assertRaises(ContractError):validate_record(self.value,self.root,self.manifest)
    def test_discover_sorted_idempotent(self):
        self.assertEqual(discover(self.root,['docs']),[self.manifest])
        self.assertEqual(discover(self.root,['docs','docs/specs']),[self.manifest])
    def test_discovery_missing_optional_root(self):self.assertEqual(discover(self.root,['not-present']),[])
    def test_secret_content_is_not_echoed(self):
        material='-----BEGIN '+'PRIVATE KEY-----'
        self.source.write_text(material)
        try:validate_record(self.value,self.root,self.manifest)
        except ContractError as exc:self.assertNotIn(material,str(exc))
        else:self.fail('secret source accepted')
    def test_failed_replace_keeps_previous_bytes(self):
        p=self.root/'out';p.write_bytes(b'last-good')
        with patch('artifact_protocol.os.replace',side_effect=OSError('injected')):
            with self.assertRaises(OSError):atomic_write(p,b'new')
        self.assertEqual(p.read_bytes(),b'last-good')
        self.assertEqual(list(self.root.glob('.out-*.tmp')),[])
    def test_stdlib_validator_matches_jsonschema(self):
        from jsonschema import Draft202012Validator,FormatChecker
        schema=schema_for('artifact-envelope.schema.json')
        reference=Draft202012Validator(schema,format_checker=FormatChecker())
        candidates=[self.value]
        for key in self.value:
            value=copy.deepcopy(self.value);value.pop(key);candidates.append(value)
            for invalid in [None,False,123,[],{},'']:
                value=copy.deepcopy(self.value);value[key]=invalid;candidates.append(value)
        for key in ['source','state','privacy','provenance']:
            value=copy.deepcopy(self.value);value[key]['extra']=1;candidates.append(value)
        for i,value in enumerate(candidates):
            with self.subTest(index=i):self.assertEqual(not schema_errors(value,schema),reference.is_valid(value))

if __name__=='__main__':unittest.main()
