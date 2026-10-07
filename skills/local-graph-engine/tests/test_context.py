"""Frozen focused acceptance tests; GRAPH_TARGET selects baseline/candidate."""
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
ROOT=Path(os.environ.get('GRAPH_TARGET',Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(ROOT/'scripts'))
import graph_engine as ge
from graph_access import execute_query
from graph_store import apply_patches
from graph_common import canonical


def fixture():
    ev={'provenance':'MANUAL','confidence':1.0,'locator':'example:1','status':'accepted','details':{'note':'evidence '*150}}
    nodes=[{'id':f'n:{i:02d}','kind':'activity','label':f'Activity {i:02d}','properties':{'description':'details '*200,'status':'ready'},'evidence':[copy.deepcopy(ev)]} for i in range(18)]
    edges=[{'source':nodes[i]['id'],'target':nodes[i+1]['id'],'relation':'precedes','directed':True,'properties':{},'evidence':[copy.deepcopy(ev)]} for i in range(17)]
    edges.append({'source':'n:05','target':'n:02','relation':'revisits','directed':True,'properties':{},'evidence':[copy.deepcopy(ev)]})
    return {'schema_version':'graph-patch-v1','source':{'uri':'example://context-fixture','kind':'example','content_hash':'sha256:fixture'},'nodes':nodes,'edges':edges}

class ContextTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.db=Path(self.tmp.name)/'graph.db';self.patch=fixture();ge.init_db(self.db);apply_patches(self.db,[self.patch])
    def tearDown(self):self.tmp.cleanup()
    def q(self,**kw):return execute_query(self.db,dict(operation='context',seed='n:00',depth=100,budget_bytes=12000,**kw))
    def test_compact_has_evidence_and_no_unrequested_properties(self):
        v=self.q();self.assertEqual(v['schema_version'],'graph-context-v1');self.assertTrue(v['nodes']);self.assertTrue(v['sources'])
        self.assertNotIn('properties',v['nodes'][0]);self.assertTrue(v['nodes'][0]['evidence'])
        for n in v['nodes']:
            for ev in n['evidence']:self.assertIn(ev['source'],v['sources'])
    def test_exact_byte_budget_and_accounting(self):
        for budget in (2048,4096,8192):
            v=execute_query(self.db,{'operation':'context','seed':'n:00','depth':100,'budget_bytes':budget})
            n=len((canonical(v)+'\n').encode());self.assertLessEqual(n,budget);self.assertEqual(v['budget']['output_bytes'],n)
            self.assertEqual(v['budget']['estimated_tokens'],(n+3)//4)
    def test_no_dangling_edges_after_budget(self):
        v=execute_query(self.db,{'operation':'context','seed':'n:00','depth':100,'budget_bytes':4096})
        ids={n['id'] for n in v['nodes']};self.assertTrue(all(e['source'] in ids and e['target'] in ids for e in v['edges']))
        self.assertTrue(v['scope']['truncated']);self.assertFalse(v['scope']['complete_database'])
    def test_opaque_receipt_reuses_same_snapshot_and_profile(self):
        a=self.q();b=self.q(previous=a['receipt']);self.assertTrue(b['reused']);self.assertLess(len(canonical(b)),len(canonical(a)))
        self.assertEqual(b['receipt'],a['receipt']);self.assertEqual(b['nodes'],[]);self.assertEqual(b['edges'],[])
    def test_stale_snapshot_invalidates_receipt(self):
        a=self.q();self.patch['nodes'][0]['label']='Changed';apply_patches(self.db,[self.patch]);b=self.q(previous=a['receipt'])
        self.assertEqual(b['reuse_status'],'invalidated');self.assertEqual(b['reused'],[]);self.assertEqual(b['nodes'][0]['label'],'Changed')
    def test_profile_change_invalidates_receipt(self):
        a=self.q();b=self.q(previous=a['receipt'],properties=['status']);self.assertEqual(b['reuse_status'],'invalidated');self.assertEqual(b['nodes'][0]['properties']['status'],'ready')
    def test_explicit_evidence_detail(self):
        a=self.q(detail='evidence',max_nodes=2);self.assertIn('details',a['nodes'][0]['evidence'][0])
    def test_deterministic_bytes(self):self.assertEqual(canonical(self.q()),canonical(self.q()))
    def test_read_only_database(self):
        before=hashlib.sha256(self.db.read_bytes()).hexdigest();self.q();self.assertEqual(before,hashlib.sha256(self.db.read_bytes()).hexdigest())
    def test_direction_and_depth(self):
        a=execute_query(self.db,{'operation':'context','seed':'n:05','depth':1,'direction':'incoming','budget_bytes':12000})
        self.assertEqual({n['id'] for n in a['nodes']},{'n:05','n:04'});self.assertTrue(a['scope']['depth_boundary'])
    def test_text_search_and_no_match(self):
        a=execute_query(self.db,{'operation':'context','query':'Activity 04','depth':0});self.assertEqual([n['id'] for n in a['nodes']],['n:04'])
        b=execute_query(self.db,{'operation':'context','query':'absent'});self.assertEqual(b['nodes'],[]);self.assertEqual(b['scope']['matched_seeds'],0)
    def test_orientation_without_seed(self):
        a=execute_query(self.db,{'operation':'context','max_nodes':4});self.assertLessEqual(len(a['nodes']),4);self.assertTrue(a['scope']['truncated'])
    def test_rejected_evidence_not_exposed(self):
        self.patch['nodes'][0]['evidence'].append({'provenance':'INFERRED','confidence':.4,'locator':'rejected','status':'rejected','details':{'note':'not-accepted-secret'}})
        apply_patches(self.db,[self.patch]);a=self.q(detail='evidence',max_nodes=1);self.assertNotIn('not-accepted-secret',canonical(a));self.assertNotIn('rejected',canonical(a['nodes'][0]['evidence']))
    def test_edge_only_node_discloses_missing_node_evidence(self):
        self.patch['nodes'][1]['evidence'][0]['status']='stale';apply_patches(self.db,[self.patch]);a=self.q(max_nodes=2)
        node=next(n for n in a['nodes'] if n['id']=='n:01');self.assertTrue(node['evidence_missing']);self.assertEqual(node['evidence'],[])
    def test_unicode_and_hostile_label_budget(self):
        self.patch['nodes'][0]['label']='\u6f22\u5b57</script>\U0001f600';apply_patches(self.db,[self.patch]);a=self.q(max_nodes=1)
        self.assertEqual(a['nodes'][0]['label'],self.patch['nodes'][0]['label']);self.assertEqual(a['budget']['output_bytes'],len((canonical(a)+'\n').encode()))
    def test_invalid_contracts_fail(self):
        for fields in ({'budget_bytes':True},{'budget_bytes':1},{'detail':'raw'},{'properties':'status'},{'previous':{}},{'token_budget':0},{'max_edges':-1},{'unexpected':True}):
            with self.subTest(fields=fields),self.assertRaises(ValueError):execute_query(self.db,dict(operation='context',**fields))
    def test_new_fields_rejected_on_other_operations(self):
        with self.assertRaises(ValueError):execute_query(self.db,{'operation':'stats','budget_bytes':4096})
    def test_token_budget_is_explicit_heuristic(self):
        a=execute_query(self.db,{'operation':'context','seed':'n:00','token_budget':1024});self.assertLessEqual(a['budget']['estimated_tokens'],1024);self.assertIn('heuristic',a['budget']['estimator'])
    def test_cli_uses_same_canonical_bytes(self):
        req=Path(self.tmp.name)/'query.json';req.write_text(json.dumps({'operation':'context','seed':'n:00','budget_bytes':4096}))
        p=subprocess.run([sys.executable,str(ROOT/'scripts/graph.py'),'--db',str(self.db),'query',str(req)],capture_output=True,check=True)
        a=json.loads(p.stdout);self.assertEqual(len(p.stdout),a['budget']['output_bytes']);self.assertLessEqual(len(p.stdout),4096)
    def test_oversized_required_seed_fails_not_silent_empty(self):
        self.patch['nodes'][0]['label']='x'*8000;apply_patches(self.db,[self.patch])
        with self.assertRaises(ValueError):execute_query(self.db,{'operation':'context','seed':'n:00','budget_bytes':2048})

if __name__=='__main__':unittest.main()
