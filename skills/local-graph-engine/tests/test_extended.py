"""Contract tests derived from the v2 acceptance, not from generated outputs."""
import copy
import http.client
import importlib.util
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import threading
import unittest
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import graph_engine as ge
from graph_common import canonical,read_json,write_json
from graph_store import apply_patches,readonly,logical_hash,backup
from graph_data import read_rows,profile,propose_mapping,rows_to_patch,evidence,structural_json
from graph_query import query
from graph_access import execute_query,sql_read,MCPServer,make_server
from graph_analysis import analyze
from graph_interop import bundle,import_bundle,history,source_revision,drop_source,remember,reflect,export_view,serialize_view,export_wiki
from graph_adapters import scan,sqlite_schema,openapi,git_history


def fixture(uri='test://one'):
    return {'schema_version':'graph-patch-v1','source':{'uri':uri,'kind':'test'},'nodes':[
        {'id':x,'kind':'person' if x!='c' else 'team','label':x.upper(),'properties':{'value':i,'timestamp':f'2026-01-0{i+1}T00:00:00Z'},'evidence':evidence('row:'+str(i))}
        for i,x in enumerate('abc')], 'edges':[
        {'source':'a','target':'b','relation':'knows','directed':True,'properties':{'cost':2},'evidence':evidence('row:1')},
        {'source':'b','target':'c','relation':'member_of','directed':True,'properties':{'cost':3},'evidence':evidence('row:2')}]}


class ExtendedTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.db=self.root/'graph.db';ge.init_db(self.db)
    def tearDown(self):self.tmp.cleanup()
    def put(self,p=None):return apply_patches(self.db,[p or fixture()])
    def q(self,**request):return execute_query(self.db,request)
    def fingerprint(self):
        con=readonly(self.db)
        try:return logical_hash(con)
        finally:con.close()

    def test_profile_zero_false_and_missing(self):
        p=profile([{'id':0,'v':False},{'id':1,'v':None}]);cols={v['name']:v for v in p['columns']}
        self.assertEqual(cols['v']['present'],1);self.assertTrue(cols['id']['candidate_key'])
    def test_mapping_domain_neutral(self):
        rows=[{'person':0,'team':'research','enabled':False},{'person':1,'team':'research','enabled':True}]
        mapping={'schema_version':'graph-mapping-v1','namespace':'people','entities':[{'key':'p','kind':'person','id_columns':['person'],'properties':['enabled']},{'key':'t','kind':'team','id_columns':['team']}],'relations':[{'from':'p','to':'t','relation':'member_of'}]}
        patch=rows_to_patch(rows,{'uri':'test://rows','kind':'records'},mapping)
        self.assertEqual(len(patch['nodes']),3);self.assertEqual(len(patch['edges']),2)
        self.assertIn(False,[n['properties'].get('enabled') for n in patch['nodes']]);self.put(patch)
        self.assertEqual(self.q(operation='stats')['nodes'],3)
    def test_no_guessed_relationships(self):
        rows=[{'id':1,'manager':2},{'id':2,'manager':None}]
        patch=rows_to_patch(rows,{'uri':'test://rows','kind':'records'},propose_mapping(rows,'unknown'))
        self.assertEqual(patch['edges'],[])
    def test_input_formats(self):
        formats={'x.csv':'id,name\n0,zero\n1,one\n','x.tsv':'id\tname\n0\tzero\n','x.json':'[{"id":0,"v":false}]','x.jsonl':'{"id":0}\n{"id":1}\n','x.xml':'<rows><row id="0"><name>zero</name></row></rows>'}
        for filename,data in formats.items():
            p=self.root/filename;p.write_text(data);rows=read_rows(p);self.assertTrue(rows)
    def test_duplicate_json_and_headers_rejected(self):
        p=self.root/'x.json';p.write_text('{"id":1,"id":2}')
        with self.assertRaises(ValueError):read_json(p)
        p=self.root/'x.csv';p.write_text('id,id\n1,2\n')
        with self.assertRaises(ValueError):read_rows(p)
    def test_xml_entities_rejected(self):
        p=self.root/'x.xml';p.write_text('<!DOCTYPE a [<!ENTITY x "v">]><a>&x;</a>')
        with self.assertRaises(ValueError):read_rows(p)
    def test_structural_json_and_secrets(self):
        p=structural_json({'token':'do-not-store','v':False},{'uri':'test://json','kind':'json'})
        self.assertNotIn('do-not-store',canonical(p));self.assertIn(False,[n['properties'].get('value') for n in p['nodes']]);self.put(p)
    def test_atomic_batch_cross_source(self):
        a=fixture('test://a');b=fixture('test://b');a['nodes']=a['nodes'][:1];a['edges']=[];b['nodes']=b['nodes'][1:]
        apply_patches(self.db,[a,b]);self.assertEqual(self.q(operation='stats')['edges'],2)
    def test_invalid_batch_rolls_back(self):
        self.put();before=self.fingerprint();good=fixture('test://new');bad=fixture('test://bad');bad['edges'][0]['target']='missing'
        with self.assertRaises(ValueError):apply_patches(self.db,[good,bad])
        self.assertEqual(before,self.fingerprint());self.assertEqual(len(bundle(self.db)['patches']),1)
    def test_idempotency_and_history(self):
        first=self.put();h=self.fingerprint();second=self.put();self.assertEqual(h,self.fingerprint());self.assertFalse(second['mutated']);self.assertEqual(len(history(self.db)['changes']),1)
    def test_source_conflicts_survive_bundle(self):
        a=fixture('test://a');b=fixture('test://b');b['nodes'][0]['properties']['value']=99
        apply_patches(self.db,[b,a]);self.assertEqual(self.q(operation='node',node='a')['node']['properties']['value'],0)
        raw={p['source']['uri']:p for p in bundle(self.db)['patches']}
        self.assertEqual(next(n for n in raw['test://b']['nodes'] if n['id']=='a')['properties']['value'],99)
        self.assertEqual(len(self.q(operation='quality')['attribute_conflicts']),1)
    def test_history_restore(self):
        self.put();prior=history(self.db)['changes'][0]['revision'];p=fixture();p['nodes'][0]['label']='Changed';self.put(p)
        apply_patches(self.db,[source_revision(self.db,'test://one',prior)])
        self.assertEqual(self.q(operation='node',node='a')['node']['label'],'A')
    def test_remove_one_source_preserves_other(self):
        apply_patches(self.db,[fixture('test://a'),fixture('test://b')]);drop_source(self.db,'test://a')
        self.assertEqual(self.q(operation='stats')['nodes'],3)
    def test_optimistic_conflict_no_mutation(self):
        self.put();h=self.fingerprint()
        with self.assertRaises(ValueError):apply_patches(self.db,[fixture()],{'test://one':'wrong'})
        self.assertEqual(h,self.fingerprint())
    def test_rejected_cannot_supply_accepted_properties(self):
        a=fixture('test://a');b=fixture('test://b');b['nodes'][0]['properties']['unverified']='claim'
        for n in b['nodes']:
            for e in n['evidence']:e['status']='rejected'
        b['edges']=[];apply_patches(self.db,[a,b]);self.assertNotIn('unverified',self.q(operation='node',node='a')['node']['properties'])
    def test_path_direction_weight_and_bounds(self):
        self.put();p=self.q(operation='path',node='a',target='c',depth=3,weight='cost')['path'];self.assertEqual(p['nodes'],['a','b','c']);self.assertEqual(p['cost'],5)
        self.assertEqual(self.q(operation='path',node='c',target='a')['path']['nodes'],[])
        self.assertEqual(self.q(operation='path',node='c',target='a',direction='incoming')['path']['nodes'],['c','b','a'])
        self.assertFalse(self.q(operation='path',node='a',target='c',depth=1)['path']['search_complete'])
    def test_subgraph_bounds_reported(self):
        self.put();v=self.q(operation='subgraph',seed='a',depth=2,max_nodes=2)['view'];self.assertTrue(v['metadata']['truncated']);self.assertEqual(len(v['nodes']),2)
        with self.assertRaises(ValueError):self.q(operation='subgraph',max_nodes=2)
    def test_ambiguous_alias_and_bad_requests(self):
        p=fixture();p['nodes'][0]['label']='Same';p['nodes'][1]['label']='Same';self.put(p)
        with self.assertRaises(ValueError):self.q(operation='node',node='Same')
        for kwargs in [{'depth':-1},{'unknown':1},{'min_confidence':float('nan')},{'max_nodes':True}]:
            with self.assertRaises(ValueError):self.q(**kwargs)
    def test_evidence_policy(self):
        p=fixture();p['edges']=[];p['nodes'][0]['evidence'][0]['status']='stale';self.put(p)
        self.assertEqual(self.q(operation='stats')['nodes'],2);self.assertEqual(self.q(operation='stats',statuses=['accepted','stale'])['nodes'],3)
    def test_aggregate_and_timeline(self):
        self.put();a=self.q(operation='aggregate',metric='sum',property='value',group_by='kind')
        self.assertEqual(sum(g['value'] for g in a['groups']),3);self.assertEqual(len(self.q(operation='timeline')['items']),3)
        with self.assertRaises(ValueError):self.q(operation='timeline',**{'from':'2026-01-01'})
    def test_analytics_repeat_and_invalidation(self):
        self.put();a=analyze(self.db,'components');b=analyze(self.db,'components');self.assertEqual(a,b);self.assertEqual(a['groups'],[['a','b','c']])
        ranks=analyze(self.db,'pagerank')['metrics']['pagerank'];self.assertAlmostEqual(sum(ranks.values()),1);self.assertGreater(ranks['c'],ranks['a'])
        p=fixture();p['nodes'][0]['label']='Different';self.put(p);self.assertIsNone(export_view(self.db)['metadata']['community_run_id'])
    def test_scc_cycle(self):
        p=fixture();p['edges'].append({'source':'c','target':'a','relation':'returns','directed':True,'properties':{},'evidence':evidence('x')});self.put(p)
        self.assertEqual(analyze(self.db,'scc')['groups'],[['a','b','c']]);self.assertEqual(analyze(self.db,'cycles')['groups'],[['a','b','c']])
    @unittest.skipUnless(importlib.util.find_spec('networkx'),'optional NetworkX unavailable')
    def test_networkx_community(self):
        self.put();a=analyze(self.db,'communities','networkx');self.assertTrue(a['groups']);self.assertEqual(a,analyze(self.db,'communities','networkx'))
    def test_federation_namespace_and_idempotency(self):
        self.put();other=self.root/'other.db';ge.init_db(other);data=bundle(self.db)
        import_bundle(other,data,'archive');con=readonly(other)
        try:self.assertEqual(query(con,{'operation':'stats'})['nodes'],3)
        finally:con.close()
        self.assertFalse(import_bundle(other,data,'archive')['mutated'])
    def test_exports_wiki_and_backup(self):
        self.put();view=export_view(self.db)
        for fmt in ['json','dot','mermaid','graphml','csv']:self.assertTrue(serialize_view(view,fmt))
        ET.fromstring(serialize_view(view,'graphml'));export_wiki(view,self.root/'wiki');self.assertTrue((self.root/'wiki'/'index.md').exists())
        out=self.root/'copy.db';backup(self.db,out);c=readonly(out)
        try:self.assertEqual(logical_hash(c),self.fingerprint())
        finally:c.close()
        with self.assertRaises(ValueError):backup(self.db,self.db)
    def test_output_alias_refused(self):
        p=self.root/'source.json';p.write_text('original')
        with self.assertRaises(ValueError):write_json(p,{'x':1},[p])
        self.assertEqual(p.read_text(),'original')
    def test_sql_readonly(self):
        self.put();self.assertEqual(sql_read(self.db,'select count(*) from nodes')['rows'],[[3]])
        for s in ["DELETE FROM nodes","select load_extension('x')","ATTACH DATABASE ':memory:' AS evil",'select 1; delete from nodes']:
            with self.assertRaises((sqlite3.Error,ValueError)):sql_read(self.db,s)
        self.assertEqual(self.q(operation='stats')['nodes'],3)
    def test_memory_not_canonical(self):
        self.put();h=self.fingerprint();remember(self.db,'Where is A?',['a'],'useful');self.assertEqual(h,self.fingerprint());self.assertEqual(reflect(self.db)['nodes'][0]['useful'],1)
    def test_local_documents_and_ast(self):
        folder=self.root/'input';folder.mkdir();(folder/'a.py').write_text('def target():\n    return 1\ndef caller():\n    return target()\n');(folder/'notes.md').write_text('# Notes\n[Code](a.py)\n')
        r=scan(folder,'docs');self.assertEqual(r['status'],'pass');apply_patches(self.db,r['patches'])
        self.assertIn('function',self.q(operation='stats')['kinds']);self.assertIn('may_resolve_to',self.q(operation='stats',statuses=['accepted','ambiguous'])['relations'])
    def test_invalid_code_stops_scan(self):
        folder=self.root/'input';folder.mkdir();(folder/'bad.py').write_text('def bad(:')
        self.assertEqual(scan(folder,'docs')['status'],'fail')
    def test_sqlite_rows_and_foreign_keys(self):
        source=self.root/'source.db';c=sqlite3.connect(source);c.executescript('CREATE TABLE teams(id INTEGER PRIMARY KEY);CREATE TABLE people(id INTEGER PRIMARY KEY,team INTEGER REFERENCES teams(id));INSERT INTO teams VALUES(1);INSERT INTO people VALUES(0,1);');c.close();before=source.read_bytes()
        self.assertEqual(read_rows(source,table='people')[0]['id'],0);self.put(sqlite_schema(source,'db'));self.assertEqual(source.read_bytes(),before)
        self.assertGreater(self.q(operation='stats')['edges'],0)
    def test_openapi(self):
        source=self.root/'api.json';source.write_text(json.dumps({'openapi':'3.1.0','paths':{'/people':{'get':{'responses':{'200':{'content':{'application/json':{'schema':{'$ref':'#/components/schemas/Person'}}}}}}}},'components':{'schemas':{'Person':{'type':'object'}}}}))
        self.put(openapi(source,'api'));self.assertTrue(self.q(operation='stats')['nodes'])
    def test_git_history(self):
        folder=self.root/'git';folder.mkdir()
        def git(*args):subprocess.run(['git','-C',str(folder),*args],check=True,capture_output=True)
        git('init');git('config','user.name','Fixture');git('config','user.email','fixture@example.invalid')
        (folder/'x.txt').write_text('a');git('add','.');git('commit','-m','one');(folder/'x.txt').write_text('b');git('add','.');git('commit','-m','two')
        p=git_history(folder,'git',5);self.put(p);self.assertEqual(self.q(operation='stats')['kinds']['commit'],2)
        labels={n['label'] for n in p['nodes'] if n['kind']=='commit'};self.assertEqual(labels,{'one','two'})
    def test_mcp_lifecycle_and_readonly(self):
        self.put();s=MCPServer(self.db)
        self.assertIn('error',s.handle({'jsonrpc':'2.0','id':0,'method':'tools/list'}))
        init=s.handle({'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-11-25','capabilities':{},'clientInfo':{'name':'test','version':'1'}}});self.assertEqual(init['result']['protocolVersion'],'2025-11-25')
        self.assertIsNone(s.handle({'jsonrpc':'2.0','method':'notifications/initialized'}))
        tools=s.handle({'jsonrpc':'2.0','id':2,'method':'tools/list'});self.assertTrue(tools['result']['tools'][0]['annotations']['readOnlyHint'])
        call=s.handle({'jsonrpc':'2.0','id':3,'method':'tools/call','params':{'name':'local_graph_query','arguments':{'operation':'stats'}}});self.assertEqual(call['result']['structuredContent']['nodes'],3)
    def test_mcp_stdio_real_process(self):
        self.put();messages=[{'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-11-25','capabilities':{},'clientInfo':{'name':'test','version':'1'}}},{'jsonrpc':'2.0','method':'notifications/initialized'},{'jsonrpc':'2.0','id':2,'method':'tools/call','params':{'name':'local_graph_query','arguments':{'operation':'stats'}}}]
        p=subprocess.run([sys.executable,'-B',str(ROOT/'scripts'/'graph.py'),'--db',str(self.db),'mcp'],input='\n'.join(map(json.dumps,messages))+'\n',text=True,capture_output=True)
        self.assertEqual(p.returncode,0,p.stderr);responses=[json.loads(x) for x in p.stdout.splitlines()];self.assertEqual(len(responses),2);self.assertEqual(responses[-1]['result']['structuredContent']['nodes'],3)
    def test_local_http_authority(self):
        from test_live_security import fixture
        self.put();page=self.root/'viewer.html';page.write_text(fixture());server=make_server(self.db,page,0)
        t=threading.Thread(target=server.serve_forever,daemon=True);t.start()
        try:
            client=http.client.HTTPConnection('127.0.0.1',server.server_port,timeout=3)
            client.request('GET','/');initial=client.getresponse();bootstrap=initial.read().decode('utf-8')
            import re
            token=json.loads(re.search(r'<script id="local-graph-session" type="application/json">(\{.*?\})</script>',bootstrap).group(1))['token']
            client.request('POST','/api/query',json.dumps({'operation':'stats'}),{'X-Local-Graph-Token':token,'Content-Type':'application/json'});r=client.getresponse();data=r.read();self.assertEqual(r.status,200,data);self.assertEqual(json.loads(data)['nodes'],3)
            client.request('POST','/api/query','{}',{'Origin':'http://evil.invalid','X-Local-Graph-Token':token});r=client.getresponse();r.read();self.assertEqual(r.status,403);client.close()
        finally:server.shutdown();server.server_close();t.join()
    @unittest.skipUnless(importlib.util.find_spec('openpyxl'),'optional openpyxl unavailable')
    def test_xlsx_optional(self):
        import openpyxl
        p=self.root/'rows.xlsx';w=openpyxl.Workbook();w.active.append(['id','enabled']);w.active.append([0,False]);w.save(p);w.close()
        self.assertEqual(read_rows(p),[{'id':0,'enabled':False}])
    @unittest.skipUnless(importlib.util.find_spec('yaml'),'optional yaml unavailable')
    def test_yaml_optional(self):
        p=self.root/'rows.yaml';p.write_text('- id: 0\n  enabled: false\n');self.assertEqual(read_rows(p),[{'id':0,'enabled':False}])

if __name__=='__main__':unittest.main()
