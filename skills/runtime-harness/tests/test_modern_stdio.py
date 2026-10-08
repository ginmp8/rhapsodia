"""Public modern/legacy stdio interoperability plus observation freshness."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from runtime_core.store import Store
from runtime_core.common import RuntimeFault
from runtime_core import capabilities
CLI=Path(__file__).resolve().parents[1]/'scripts/runtime.py'
META={'io.modelcontextprotocol/protocolVersion':'2026-07-28','io.modelcontextprotocol/clientCapabilities':{}}
class ModernStdio(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.store=Store(self.root);self.store.initialize([])
    def exchange(self,messages):
        p=subprocess.run([sys.executable,'-I','-S','-B',str(CLI),'--workspace',str(self.root),'mcp'],
                         input=''.join(json.dumps(m)+'\n' for m in messages),text=True,capture_output=True,timeout=15)
        self.assertEqual(p.returncode,0,p.stdout+p.stderr);self.assertNotIn('Traceback',p.stderr)
        return [json.loads(line) for line in p.stdout.splitlines()]
    def rpc(self,method,id=1):return {'jsonrpc':'2.0','id':id,'method':method,'params':{'_meta':META}}
    def test_modern_stdio_without_initialize(self):
        r=self.exchange([self.rpc('server/discover'),self.rpc('tools/list',2)])
        self.assertEqual(r[0]['result']['resultType'],'complete')
        self.assertEqual(r[1]['result']['tools'][0]['name'],'runtime_query')
    def test_modern_request_does_not_initialize_legacy_state(self):
        r=self.exchange([self.rpc('server/discover'),{'jsonrpc':'2.0','id':2,'method':'tools/list'}])
        self.assertEqual(r[1]['error']['code'],-32002)
    def test_legacy_initialize_then_modern_request(self):
        init={'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-11-25','capabilities':{},'clientInfo':{'name':'fixture','version':'1'}}}
        r=self.exchange([init,{'jsonrpc':'2.0','method':'notifications/initialized'},self.rpc('server/discover',2),{'jsonrpc':'2.0','id':3,'method':'tools/list'}])
        self.assertEqual(r[0]['result']['protocolVersion'],'2025-11-25')
        self.assertEqual(r[1]['result']['resultType'],'complete')
        self.assertNotIn('resultType',r[2]['result'])
    def test_available_observation_requires_available_target(self):
        with self.assertRaises(RuntimeFault):
            capabilities.attempt(self.store,{'target':'tool://not-observed','outcome':'available','strategy':'path'})
    def test_transient_observation_expires(self):
        capabilities.attempt(self.store,{'target':'tool://python','outcome':'transient','strategy':'path'})
        observed=max(x['observed_at'] for x in self.store.current()[1]['attempts'].values())
        with patch('runtime_core.capabilities.time.time',return_value=observed+31):
            self.assertEqual(capabilities.history(self.store,{'target':'tool://python'})['observations'],[])
    def test_search_fingerprint_invalidates_history(self):
        capabilities.attempt(self.store,{'target':'tool://python','outcome':'missing','strategy':'path'})
        with patch('runtime_core.capabilities.search_fingerprint',return_value='a'*64):
            self.assertEqual(capabilities.history(self.store,{'target':'tool://python'})['observations'],[])

if __name__=='__main__':unittest.main()
