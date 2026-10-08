"""Frozen 0.8.0 additive public-surface checks."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from runtime_core.store import Store
from runtime_core.common import RuntimeFault, canonical, confined, sha
from runtime_core import capabilities, delta
from runtime_core.mcp import Session
from runtime_core.handoff import create
from runtime_core.query import resolve

META={'io.modelcontextprotocol/protocolVersion':'2026-07-28','io.modelcontextprotocol/clientCapabilities':{}}

class Runtime080(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);(self.root/'source.txt').write_text('source')
        self.store=Store(self.root);self.store.initialize([])
    def call(self,method,params=None):
        return Session(self.store).handle({'jsonrpc':'2.0','id':1,'method':method,'params':{'_meta':META,**(params or {})}})
    def test_modern_discovery_without_handshake(self):
        result=self.call('server/discover')['result']
        self.assertEqual(result['resultType'],'complete');self.assertIn('2026-07-28',result['supportedVersions'])
        self.assertEqual(result['cacheScope'],'private');self.assertGreaterEqual(result['ttlMs'],0)
    def test_modern_list_without_handshake(self):
        result=self.call('tools/list')['result'];self.assertEqual(result['tools'][0]['name'],'runtime_query')
        self.assertEqual(result['resultType'],'complete');self.assertIn('ttlMs',result)
    def test_modern_query(self):
        result=self.call('tools/call',{'name':'runtime_query','arguments':{'operation':'status'}})['result']
        self.assertFalse(result['isError']);self.assertEqual(result['resultType'],'complete');self.assertNotIn('ttlMs',result)
    def test_modern_requires_metadata(self):
        got=Session(self.store).handle({'jsonrpc':'2.0','id':1,'method':'server/discover','params':{}})
        self.assertEqual(got['error']['code'],-32602)
    def test_modern_unknown_version(self):
        got=self.call('server/discover',{'_meta':{**META,'io.modelcontextprotocol/protocolVersion':'2099-01-01'}})
        self.assertEqual(got['error']['code'],-32022)
    def test_modern_does_not_initialize_legacy(self):
        s=Session(self.store);s.handle({'jsonrpc':'2.0','id':1,'method':'tools/list','params':{'_meta':META}})
        self.assertEqual(s.handle({'jsonrpc':'2.0','id':2,'method':'tools/list'})['error']['code'],-32002)
    def test_capability_bound_to_tool_and_receipt(self):
        snap=self.store.current()[1];identity=snap['tools']['python']['identity']
        proof={'schema':'capability-observation/v1','capability_uri':'capability://python-json','tool_identity':identity,'available':True,'features':['json']}
        (self.root/'proof.json').write_bytes(canonical(proof))
        capabilities.publish(self.store,{'uri':'capability://python-json','tool':'tool://python','proof':'repo://proof.json','ttl_seconds':300})
        got=resolve(self.store.current()[1],'capability://python-json');self.assertEqual(got['status'],'available');self.assertFalse(got['execution_authority'])
        (self.root/'proof.json').write_text('{}')
        self.assertEqual(resolve(self.store.current()[1],'capability://python-json')['status'],'stale')
    def test_capability_forged_identity_rejected(self):
        (self.root/'proof.json').write_bytes(canonical({'schema':'capability-observation/v1','capability_uri':'capability://python-json','tool_identity':'0'*64,'available':True,'features':[]}))
        with self.assertRaises(RuntimeFault):capabilities.publish(self.store,{'uri':'capability://python-json','tool':'tool://python','proof':'repo://proof.json'})
    def test_attempt_typed_and_bounded(self):
        result=capabilities.attempt(self.store,{'target':'tool://python','outcome':'transient','strategy':'path','duration_ms':12})
        got=capabilities.history(self.store,{'target':'tool://python'})
        self.assertEqual(got['observations'][0]['outcome'],'transient');self.assertFalse(got['execution_authority'])
        self.assertTrue(result['id']);self.assertLessEqual(got['observations'][0]['ttl_seconds'],60)
    def test_attempt_rejects_raw_logs(self):
        with self.assertRaises(RuntimeFault):capabilities.attempt(self.store,{'target':'tool://python','outcome':'denied','strategy':'path','stderr':'secret'})
    def test_delta_roundtrip(self):
        refs=['repo://source.txt','tool://python','workspace://current']
        a=create(self.store,{'task_id':'test','next_action':'review','refs':refs,'summary':'A'*900})['handoff_id']
        b=create(self.store,{'task_id':'test','next_action':'verify','refs':refs,'summary':'A'*900})['handoff_id']
        transport=delta.make(self.store,{'parent_id':a,'target_id':b,'receiver_parent_id':a})
        self.assertEqual(transport['mode'],'delta')
        full=delta.apply(self.store,{'transport':transport,'parent_id':a})
        self.assertEqual(full['handoff_id'],b)
    def test_delta_fallback_without_ack(self):
        a=create(self.store,{'task_id':'test','next_action':'review','refs':['repo://source.txt']})['handoff_id']
        t=delta.make(self.store,{'parent_id':a,'target_id':a})
        self.assertEqual(t['mode'],'full')
        self.assertEqual(delta.apply(self.store,{'transport':t})['handoff_id'],a)
    def test_delta_wrong_parent_rejected(self):
        a=create(self.store,{'task_id':'test','next_action':'review','refs':['repo://source.txt'],'summary':'A'*900})['handoff_id']
        b=create(self.store,{'task_id':'test','next_action':'verify','refs':['repo://source.txt'],'summary':'A'*900})['handoff_id']
        t=delta.make(self.store,{'parent_id':a,'target_id':b,'receiver_parent_id':a})
        with self.assertRaises(RuntimeFault):delta.apply(self.store,{'transport':t,'parent_id':b})
    def test_old_snapshot_read_compatible(self):
        snap=dict(self.store.current()[1]);snap['runtime_version']='1.1.0'
        snap.pop('capabilities',None);snap.pop('attempts',None)
        with self.store.writer():self.store._publish(snap)
        self.assertEqual(self.store.current()[1]['runtime_version'],'1.1.0')

if __name__=='__main__':unittest.main()
