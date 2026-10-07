"""Contract and access integration, with fixed source-backed expected behavior."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest
import test_context as base
from graph_access import MCPServer, QUERY_SCHEMA
from measure_context import measure_context

class ContextIntegrationTests(unittest.TestCase):
    setUp = base.ContextTests.setUp
    tearDown = base.ContextTests.tearDown
    q = base.ContextTests.q
    def test_mcp_advertises_context_contract(self):
        self.assertIn('context',QUERY_SCHEMA['properties']['operation']['enum'])
        self.assertIn('budget_bytes',QUERY_SCHEMA['properties']);self.assertIn('previous',QUERY_SCHEMA['properties'])
    def test_mcp_returns_context_without_writes(self):
        m=MCPServer(self.db)
        m.handle({'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-11-25','capabilities':{},'clientInfo':{}}})
        m.handle({'jsonrpc':'2.0','method':'notifications/initialized'})
        r=m.handle({'jsonrpc':'2.0','id':2,'method':'tools/call','params':{'name':'local_graph_query','arguments':{'operation':'context','seed':'n:00','budget_bytes':4096}}})['result']
        self.assertFalse(r['isError']);self.assertEqual(r['structuredContent']['schema_version'],'graph-context-v1')
        self.assertEqual(json.loads(r['content'][0]['text']),r['structuredContent'])
    @unittest.skipUnless(importlib.util.find_spec('jsonschema'), 'optional JSON Schema validator unavailable')
    def test_request_result_and_reused_contract(self):
        import jsonschema
        schema=json.loads((base.ROOT/'contracts/graph-context-v1.schema.json').read_text())
        a=self.q();b=self.q(previous=a['receipt']);jsonschema.validate(a,schema);jsonschema.validate(b,schema)
        query_schema=json.loads((base.ROOT/'contracts/graph-query-v1.schema.json').read_text())
        jsonschema.validate({'operation':'context','budget_bytes':4096,'previous':a['receipt']},query_schema)
        for bad in [{'operation':'find','budget_bytes':4096},{'operation':'context','max_nodes':501}]:
            with self.assertRaises(jsonschema.ValidationError):jsonschema.validate(bad,query_schema)
    def test_measurement_is_same_selection_and_snapshot(self):
        m=measure_context(self.db,{'operation':'context','seed':'n:00','depth':100,'budget_bytes':12000})
        self.assertLess(m['compact_envelope_bytes'],m['rich_records_bytes']);self.assertLess(m['repeat_envelope_bytes'],m['compact_envelope_bytes'])
        self.assertEqual(m['selected_nodes'],self.q()['scope']['selected_nodes']);self.assertIn('Not measured model tokens',m['limits'][0])
    def test_measurement_rejects_hidden_previous_or_wrong_operation(self):
        for r in [{'operation':'stats'},{'operation':'context','previous':self.q()['receipt']}]:
            with self.assertRaises(ValueError):measure_context(self.db,r)
    def test_conflicting_source_assertions_are_flagged(self):
        p=copy.deepcopy(self.patch);p['source']['uri']='example://conflicting-source';p['nodes'][0]['label']='Conflicting interpretation'
        base.apply_patches(self.db,[p]);v=self.q();self.assertTrue(v['nodes'][0]['attribute_conflict'])
    def test_zero_edge_budget_discloses_exclusions(self):
        v=self.q(max_edges=0);self.assertEqual(v['edges'],[]);self.assertTrue(v['scope']['edge_boundary']);self.assertTrue(v['scope']['truncated'])
    def test_partial_receipt_sends_missing_records(self):
        a=self.q();receipt=copy.deepcopy(a['receipt']);receipt['items'].pop('n:n:00')
        b=self.q(previous=receipt);self.assertEqual([n['id'] for n in b['nodes']],['n:00']);self.assertTrue(b['sources']);self.assertTrue(b['reused'])

if __name__=='__main__':unittest.main()
