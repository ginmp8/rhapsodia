from __future__ import annotations
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from artifact_protocol import ContractError,canonical_bytes,digest
from workspace import build_catalog,derived_path,main,project,render
from test_protocol import record

class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.repo=Path(self.tmp.name)
        self.value=record();self.add(self.value)
    def tearDown(self):self.tmp.cleanup()
    def add(self,r):
        src=self.repo/r['source']['path'];src.parent.mkdir(parents=True,exist_ok=True)
        src.write_bytes(b'# Technical design\n');r['source']['sha256']=digest(src.read_bytes())
        Path(str(src)+'.artifact.json').write_bytes(canonical_bytes(r))
    def test_deterministic_index(self):self.assertEqual(build_catalog(self.repo),build_catalog(self.repo))
    def test_no_absolute_paths_in_catalog(self):self.assertNotIn(str(self.repo),json.dumps(build_catalog(self.repo)))
    def test_all_four_projections(self):
        for view in ['portfolio','timeline','relations','skills']:
            with self.subTest(view=view):self.assertEqual(project(build_catalog(self.repo),view)['authority'],'non-authoritative')
    def test_distinct_status_dimensions_not_collapsed(self):
        other=record('docs/product/sample/feature.md');other.update(producer='nomia',artifact_id='nomia:sample:feature',artifact_type='feature',state={'dimension':'governance','value':'pending'})
        self.add(other);p=project(build_catalog(self.repo),'portfolio')
        self.assertEqual({a['dimension'] for a in p['data'][0]['artifacts']},{'governance','planning'})
    def test_duplicate_artifact_id_fails(self):
        other=copy.deepcopy(self.value);other['source']['path']='docs/specs/sample/duplicate.md';self.add(other)
        with self.assertRaisesRegex(ContractError,'DUPLICATE_ARTIFACT'):build_catalog(self.repo)
    def test_unresolved_relations_are_explicit(self):
        self.value['relations']=[{'type':'implements','target':'nomia:sample:missing'}];self.add(self.value)
        self.assertEqual(build_catalog(self.repo)['diagnostics'][0]['code'],'UNRESOLVED_RELATION')
    def test_dependency_cycle_fails(self):
        self.value['relations']=[{'type':'depends_on','target':'nomia:sample:feature'}];self.add(self.value)
        other=record('docs/product/sample/feature.md');other.update(producer='nomia',artifact_id='nomia:sample:feature');other['relations']=[{'type':'depends_on','target':self.value['artifact_id']}];self.add(other)
        with self.assertRaisesRegex(ContractError,'DEPENDENCY_CYCLE'):build_catalog(self.repo)
    def test_nondependency_cycles_allowed(self):
        self.value['relations']=[{'type':'relates_to','target':'nomia:sample:feature'}];self.add(self.value)
        other=record('docs/product/sample/feature.md');other.update(producer='nomia',artifact_id='nomia:sample:feature');other['relations']=[{'type':'relates_to','target':self.value['artifact_id']}];self.add(other)
        self.assertEqual(len(build_catalog(self.repo)['entries']),2)
    def test_generic_producer_is_supported(self):
        other=record('docs/research/sample/note.md');other.update(producer='researcher',artifact_id='researcher:sample:note');self.add(other)
        self.assertEqual(len(build_catalog(self.repo)['entries']),2)
    def test_unknown_schema_fails(self):
        self.value['schema_version']='99.0.0';self.add(self.value)
        with self.assertRaises(ContractError):build_catalog(self.repo)
    def test_public_export_requires_permission(self):
        with self.assertRaises(ContractError):build_catalog(self.repo,destination='public')
        self.value['privacy']={'classification':'public','allowed_destinations':['public','local'],'contains_secrets':False,'external_share_allowed':True};self.add(self.value)
        self.assertEqual(build_catalog(self.repo,destination='public')['destination'],'public')
    def test_source_trees_never_mutated(self):
        before={p.relative_to(self.repo).as_posix():p.read_bytes() for p in (self.repo/'docs').rglob('*') if p.is_file()}
        catalog=build_catalog(self.repo);render(catalog);project(catalog,'relations')
        after={p.relative_to(self.repo).as_posix():p.read_bytes() for p in (self.repo/'docs').rglob('*') if p.is_file()}
        self.assertEqual(before,after)
    def test_delete_catalog_and_rebuild_preserves_fingerprint(self):
        self.assertEqual(main(['index','--repo-root',str(self.repo)]),0)
        path=self.repo/'.rhapsodia/catalog/catalog.json';first=path.read_bytes();shutil.rmtree(self.repo/'.rhapsodia/catalog')
        self.assertEqual(main(['index','--repo-root',str(self.repo)]),0);self.assertEqual(first,path.read_bytes())
    def test_failed_validation_preserves_good_catalog(self):
        main(['index','--repo-root',str(self.repo)]);path=self.repo/'.rhapsodia/catalog/catalog.json';first=path.read_bytes()
        (self.repo/self.value['source']['path']).write_text('drift')
        self.assertEqual(main(['index','--repo-root',str(self.repo)]),1);self.assertEqual(first,path.read_bytes())
    def test_render_rejects_source_output_alias(self):
        self.assertEqual(main(['render','--repo-root',str(self.repo),'--output',self.value['source']['path']]),1)
    def test_render_includes_complete_offline_view(self):
        data=render(build_catalog(self.repo)).decode();self.assertIn('data-view="portfolio"',data);self.assertIn('data-view="timeline"',data);self.assertIn('data-view="relations"',data);self.assertIn('data-view="skills"',data)
        self.assertNotIn('__CATALOG_JSON__',data);self.assertNotIn('<script src=',data);self.assertNotIn('fetch(',data)
    def test_script_tag_in_metadata_is_data(self):
        self.value['title']='</script><script>window.attacked=true</script>';self.add(self.value)
        data=render(build_catalog(self.repo)).decode();self.assertNotIn(self.value['title'],data);self.assertIn('\\u003c/script\\u003e',data)
    def test_empty_state(self):
        shutil.rmtree(self.repo/'docs');catalog=build_catalog(self.repo);self.assertEqual(catalog['entries'],[])
        self.assertIn(b'No artifacts published yet',render(catalog))
    def test_output_symlink_rejected(self):
        (self.repo/'.rhapsodia').symlink_to(self.repo/'docs',target_is_directory=True)
        self.assertEqual(main(['index','--repo-root',str(self.repo)]),1)
    def test_source_drift_between_scan_and_commit_fails(self):
        real=build_catalog(self.repo);changed=copy.deepcopy(real);changed['source_fingerprint']='f'*64
        with patch('workspace.build_catalog',side_effect=[real,changed]):self.assertEqual(main(['index','--repo-root',str(self.repo)]),1)
        self.assertFalse((self.repo/'.rhapsodia/catalog/catalog.json').exists())

if __name__=='__main__':unittest.main()
