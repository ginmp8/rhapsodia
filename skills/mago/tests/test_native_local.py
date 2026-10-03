from __future__ import annotations
import copy, importlib, json, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from artifact_protocol import ContractError, canonical_bytes, digest, validate_actions
from native_artifacts import policy,publish,resolve_owned_root

class NativeLocalTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.repo=Path(self.tmp.name);self.rules=policy()
  kind=next(x for x in self.rules['artifact_types'] if x in {'feature','technical-design','implementation-notes'})
  dim={'nomia':'governance','mago':'planning','magia':'execution'}[self.rules['producer']]
  self.source=self.repo/self.rules['default_root']/'sample'/f'{kind}.md';self.source.parent.mkdir(parents=True);self.source.write_text('# Synthetic source\n')
  self.request={'artifact':{'schema_version':'1.0.0','artifact_id':self.rules['producer']+':sample:'+kind,'producer':self.rules['producer'],'artifact_type':kind,'work_item_id':'sample','workflow_id':None,'title':'Synthetic sample','state':{'dimension':dim,'value':'draft'},'lifecycle':'active','created_at':'2026-10-03T12:00:00Z','updated_at':'2026-10-03T12:00:00Z','source':{'path':self.source.relative_to(self.repo).as_posix(),'sha256':'0'*64},'relations':[],'privacy':{'classification':'internal','allowed_destinations':['local'],'contains_secrets':False,'external_share_allowed':False},'provenance':{'kind':'authored','evidence_refs':[],'source_handoff_id':None}},'expected_manifest_sha256':None,'reason':'Synthetic publication'}
 def tearDown(self):self.tmp.cleanup()
 def test_publish_without_board_or_workspace(self):
  result=publish(self.repo,self.request);validate_actions(result,self.repo)
  self.assertEqual(result['artifact_actions'][0]['action'],'created');self.assertFalse((self.repo/'docs/boards').exists());self.assertFalse((self.repo/'.rhapsodia').exists())
 def test_idempotent(self):
  publish(self.repo,self.request);self.assertEqual(publish(self.repo,self.request)['artifact_actions'][0]['action'],'unchanged')
 def test_stale_source(self):
  receipt=publish(self.repo,self.request);self.source.write_text('changed')
  with self.assertRaises(ContractError):validate_actions(receipt,self.repo)
 def test_revision_guard(self):
  receipt=publish(self.repo,self.request);self.source.write_text('changed')
  with self.assertRaisesRegex(ContractError,'REVISION_CONFLICT'):publish(self.repo,self.request)
  self.request['expected_manifest_sha256']=receipt['artifact_actions'][0]['manifest_sha256'];self.assertEqual(publish(self.repo,self.request)['artifact_actions'][0]['action'],'updated')
 def test_owner_violation(self):
  self.request['artifact']['producer']='foreign'
  with self.assertRaises(ContractError):publish(self.repo,self.request)
 def test_cross_owner_root(self):
  for other in self.rules['other_owner_roots']:
   with self.subTest(other=other),self.assertRaises(ContractError):resolve_owned_root(self.repo,other)
 def test_symlink(self):
  self.source.unlink();self.source.symlink_to(self.repo/'elsewhere.md')
  with self.assertRaises(ContractError):publish(self.repo,self.request)
 def test_legacy_override_invariants(self):
  mod=importlib.import_module(self.rules['producer']+'_utils');cycle='cycle-2026-10-03-example'
  path=self.repo/'docs/boards/example/2026/cycles'/cycle
  self.assertEqual(mod.resolve_board_root(self.repo,board_root_override=path),path)
  for override,kwargs in [(self.repo.parent/path.name,{}),(path/'child',{}),(path,{'board_id':'wrong'}),(path,{'year':'2025'}),(path,{'cycle_id':'cycle-2026-10-02-example'})]:
   with self.subTest(override=override,kwargs=kwargs),self.assertRaises(ValueError):mod.resolve_board_root(self.repo,board_root_override=override,**kwargs)
 def test_impossible_date_rejected_and_leap_day_accepted(self):
  mod=importlib.import_module(self.rules['producer']+'_utils')
  with self.assertRaises(ValueError):mod.parse_spec_id('spec-2026-02-30-example')
  self.assertEqual(mod.parse_spec_id('spec-2028-02-29-example')['date'],'2028-02-29')
if __name__=='__main__':unittest.main()
