"""Supplementary public boundary checks; no hosted-model or IDE assertions."""
import concurrent.futures
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from oc_core.common import RuntimeFault, canonical
from oc_core.store import Cache
from oc_core import sharing
CLI=Path(__file__).resolve().parents[1]/'scripts/operational.py'

class Boundaries(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.cache=Cache(self.root)
    def call(self,command,data,entry=CLI):
        return subprocess.run([sys.executable,'-I','-S','-B',str(entry),'--workspace',str(self.root),command],
                              input=json.dumps(data),text=True,capture_output=True,timeout=15)
    def test_unknown_owner_never_enables_fanout(self):
        from oc_core.policy import decide
        units=[{'id':str(i),'effect':'read','estimated_ms':1000,'independent':True} for i in range(2)]
        self.assertEqual(decide({'units':units,'host_parallel':True,'spawn_ms':1,'synthesis_ms':1})['strategy'],'sequential')
    def test_boolean_generation_is_not_integer_fence(self):
        req={'operation':'acquire','resource':'work','holder':'a'}
        current=sharing.lease(self.cache,req)
        with self.assertRaises(RuntimeFault):
            sharing.lease(self.cache,dict(req,operation='renew',token=current['token'],generation=True))
    def test_concurrent_acquire_has_one_winner(self):
        def acquire(holder):return self.call('lease',{'operation':'acquire','resource':'same-work','holder':holder})
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            results=list(pool.map(acquire,['one','two']))
        self.assertEqual(sorted(p.returncode for p in results),[0,5])
        for p in results:self.assertNotIn('Traceback',p.stderr)
    def test_unknown_lock_never_stolen(self):
        self.cache.root.mkdir(parents=True)
        lock=self.cache.root/'.writer.lock';lock.write_text('unknown owner')
        with self.assertRaises(RuntimeFault):self.cache.put('artifact',{'example':True})
        self.assertEqual(lock.read_text(),'unknown owner')
    def test_approved_output_excerpt_bounded(self):
        (self.root/'log.txt').write_text('detail line\n'*1000)
        p=self.call('output-card',{'path':'log.txt','observed_status':'failed','include_excerpt':True,
                                 'approved_content':True,'tail_lines':200,'budget_bytes':1024})
        self.assertEqual(p.returncode,0,p.stdout+p.stderr)
        result=json.loads(p.stdout)
        self.assertLessEqual(len(canonical(result)),1024)
        self.assertTrue(result['content_omitted'])
    def test_copied_skill_runs_without_repository_or_site_packages(self):
        with tempfile.TemporaryDirectory() as t:
            target=Path(t)/'portable';shutil.copytree(CLI.parents[1],target)
            p=self.call('describe',{},entry=target/'scripts/operational.py')
        self.assertEqual(p.returncode,0,p.stdout+p.stderr)
        self.assertEqual(len(json.loads(p.stdout)['commands']),22)
    def test_duplicate_json_keys_rejected_at_cli_boundary(self):
        p=subprocess.run([sys.executable,'-I','-S','-B',str(CLI),'--workspace',str(self.root),'usage'],
                         input='{"provider":"openai","provider":"other","usage":{}}',
                         text=True,capture_output=True,timeout=15)
        self.assertNotEqual(p.returncode,0)
        self.assertEqual(json.loads(p.stdout)['status'],'error')
        self.assertNotIn('Traceback',p.stderr)

if __name__=='__main__':unittest.main()
