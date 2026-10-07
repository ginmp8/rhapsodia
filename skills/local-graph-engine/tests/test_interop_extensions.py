import copy
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import graph_engine as ge
from graph_common import canonical
from graph_data import evidence,rows_to_patch,propose_mapping
from graph_interop import export_view,serialize_view,graphml_patch,save_query,saved_queries
from graph_store import apply_patches
from graph_access import execute_query

class InteropExtensions(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.db=self.root/'graph.db';ge.init_db(self.db)
        self.patch={'schema_version':'graph-patch-v1','source':{'uri':'test://rows','kind':'test'},'nodes':[{'id':'a','kind':'person','label':'Alpha research','properties':{},'evidence':evidence('row:1')},{'id':'b','kind':'team','label':'Beta group','properties':{},'evidence':evidence('row:2')}],'edges':[{'source':'a','target':'b','relation':'member_of','directed':True,'properties':{},'evidence':evidence('row:1')}]}
        apply_patches(self.db,[self.patch])
    def tearDown(self):self.temp.cleanup()
    def test_graphml_roundtrip(self):
        p=self.root/'view.graphml';p.write_text(serialize_view(export_view(self.db),'graphml'));patch=graphml_patch(p,'copy')
        self.assertEqual(len(patch['nodes']),2);self.assertEqual(len(patch['edges']),1);self.assertEqual(patch['edges'][0]['relation'],'member_of')
    def test_fts_search(self):
        result=execute_query(self.db,{'operation':'search','query':'research'})
        self.assertEqual(len(result['results']),1);self.assertEqual(result['results'][0]['id'],'a')
    def test_saved_query(self):
        save_query(self.db,'people',{'operation':'stats','kinds':['person']});self.assertEqual(saved_queries(self.db,'people')['nodes'],1);self.assertEqual(len(saved_queries(self.db)['queries']),1)
    def test_explicit_type_mapping_and_original(self):
        rows=[{'id':'001','amount':'12.5','active':'false'}];mapping=propose_mapping(rows,'types');mapping['entities'][0]['types']={'amount':'number','active':'boolean'}
        patch=rows_to_patch(rows,{'uri':'test://typed','kind':'csv'},mapping);n=patch['nodes'][0]
        self.assertEqual(n['properties']['amount'],12.5);self.assertIs(n['properties']['active'],False);self.assertEqual(n['evidence'][0]['details']['observed_properties']['amount'],'12.5');self.assertEqual(n['label'],'001')
    def test_do_not_guess_identity_from_unique_measurement(self):
        mapping=propose_mapping([{'amount':123},{'amount':456}],'x');self.assertEqual(mapping['entities'][0]['id_columns'],[])
    def test_secret_label_rejected(self):
        mapping=propose_mapping([{'id':1,'token':'secret'}],'x');mapping['entities'][0]['label_column']='token'
        with self.assertRaises(ValueError):rows_to_patch([{'id':1,'token':'secret'}],{'uri':'test://x','kind':'csv'},mapping)
    def test_null_optional_properties_compatible(self):
        patch=copy.deepcopy(self.patch);patch['nodes'][0]['properties']=None;patch['source']['metadata']=None;apply_patches(self.db,[patch]);self.assertEqual(execute_query(self.db,{'operation':'node','node':'a'})['node']['properties'],{})
    def test_multiple_observations_same_locator_preserved(self):
        patch=copy.deepcopy(self.patch);patch['nodes'][0]['evidence']+=evidence('row:1',details={'distinct':'second observation'});apply_patches(self.db,[patch]);result=execute_query(self.db,{'operation':'node','node':'a'})
        self.assertEqual(len(result['node']['evidence']),2)
    def test_opposite_undirected_duplicate_rejected(self):
        patch=copy.deepcopy(self.patch);patch['edges'][0]['directed']=False;edge=copy.deepcopy(patch['edges'][0]);edge['source'],edge['target']='b','a';patch['edges'].append(edge)
        self.assertTrue(ge.validate_patch_data(patch));
        with self.assertRaises(ValueError):apply_patches(self.db,[patch])

if __name__=='__main__':unittest.main()
