"""Additional high-risk gates for optional adapters, source provenance and active probes."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
SCRIPTS=Path(__file__).resolve().parents[1]/'scripts'
sys.path.insert(0,str(SCRIPTS))
from behavior_lab import DataError, load_corpus, compare
import tool_adapters, probe_engine, state_inference, evidence_ir, execution_policy, browser_capture

class ExtraCases(unittest.TestCase):
    def setUp(self):
        self.h=tempfile.TemporaryDirectory();self.addCleanup(self.h.cleanup);self.p=Path(self.h.name)
    def put(self,name,bytestr):
        p=self.p/name;p.parent.mkdir(parents=True,exist_ok=True)
        p.write_bytes(bytestr if isinstance(bytestr,bytes) else bytestr.encode('utf-8'))
        return p

    def test_bounded_process_real_stdout_and_overflow(self):
        cmd=[sys.executable,'-c','print("hello")']
        out=self.p/'stdout';err=self.p/'stderr'
        code=tool_adapters.bounded_process(cmd,str(self.p),{'PATH':''},5,out,err)
        self.assertEqual(code,0);self.assertEqual(out.read_bytes(),b'hello\n')
        large=[sys.executable,'-c','import sys;sys.stdout.write("X"*3000000)']
        with self.assertRaises(DataError):
            tool_adapters.bounded_process(large,str(self.p),{'PATH':''},5,out,err)

    def test_adapter_compositions_and_sensitive_output_refusal(self):
        input_path=self.put('binary.bin',b'\x00')
        out=self.p/'analyzed'
        self.assertEqual(tool_adapters.build_command('jadx','/opt/jadx',input_path,out)[:4],['/opt/jadx','-j','1','-r'])
        schema=self.put('schema.ksy','meta:\n  id: demo\n')
        self.assertIn('-t',tool_adapters.build_command('kaitai','/opt/ksc',input_path,out,schema=schema))
        self.assertIn('--output',tool_adapters.build_command('roslyn','/opt/roslyn-export',input_path,out))
        folder=self.p/'generated';folder.mkdir()
        (folder/'safe.bin').write_bytes(b'safe')
        self.assertEqual(len(tool_adapters.manifest(folder)),1)
        (folder/'huge.bin').write_bytes(b'0'*(tool_adapters.MAX_OUTPUT+1))
        with self.assertRaises(DataError):tool_adapters.manifest(folder)

    def test_real_trusted_active_oracle_with_state_steps(self):
        script=self.put('state_oracle.py','''import json,sys
stim=json.loads(sys.stdin.readline());state=0;steps=[]
for i,action in enumerate(stim['actions']):
 state+=1 if action['action']=='inc' else -1
 steps.append({'action_index':i,'output':state,'state':{'count':state}})
print(json.dumps({'steps':steps,'state':{'count':state}}))
''')
        command=self.put('trusted-argv.json',json.dumps([sys.executable,str(script)]))
        rows=state_inference.active_capture([{'action':'inc'},{'action':'dec'}],command,self.p,
                                             depth=2,max_queries=6,execute_authorized=True,reset_confirmed=True)
        self.assertEqual(len(rows),6)
        self.assertEqual({r['runner_status'] for r in rows},{'ok'})
        self.assertEqual(len(state_inference.infer({r['id']:r for r in rows})['transitions'])>0,True)
        with self.assertRaises(DataError):
            state_inference.aalpy_learn([{'action':'inc'}],command,self.p,authorized=True,reset_confirmed=False)

    def test_coverage_prioritization_and_exact_case_hash(self):
        corpus=self.put('seeds.jsonl',''.join(json.dumps({'id':id,'input':val,'observation':{'output':val}})+'\n'
                  for id,val in (('a',{'x':5}),('b',{'x':7}))))
        cov=self.put('coverage.json',json.dumps({'by_case':{'a':['common'],'b':['rare','common']}}))
        result=probe_engine.generate(corpus,coverage=cov,max_cases=8)
        self.assertEqual(result['cases'][0]['based_on'],'b')
        self.assertEqual(result['coverage_sha256'],hashlib.sha256(cov.read_bytes()).hexdigest())

    def test_legacy_comparator_same_inputs_and_sensitive_no_raw_values(self):
        ref=self.put('reference.jsonl',json.dumps({'id':'a','input':{'n':1},'observation':{'output':1}})+'\n')
        candidate=self.put('candidate.jsonl',json.dumps({'id':'a','input':{'n':2},'observation':{'output':1}})+'\n')
        result=compare(ref,candidate,tolerance=10)
        self.assertEqual(result['verdict'],'DIVERGENCE_OR_INCOMPLETE')
        self.assertIn('/input/n',json.dumps(result))
        self.assertNotIn('"value": 1',json.dumps(result))

    def test_graph_export_no_unsupported_source_upgrade(self):
        source=self.put('legacy.json',json.dumps({'results':[{'format':'javascript','path':'client.js',
            'references':[{'name':'fetchSomething','line':2}]}]}))
        g=evidence_ir.ingest([source])['reports'][0]
        self.assertTrue(any(n['evidence_level']=='lexical_candidate' for n in g['nodes']))
        self.assertFalse(any(n['evidence_level']=='runtime_observed' for n in g['nodes']))

    def test_restriction_browser_url_and_oci_digest(self):
        with self.assertRaises(DataError):browser_capture.safe_actions(self.put('actions.json','[{"type":"goto","path":"//evil"}]'))
        with patch('execution_policy.shutil.which',return_value='/bin/docker'):
            with self.assertRaises(DataError):
                execution_policy.preflight('oci-pinned',authorized=True,isolated_approved=True,
                                           image='repo@sha256:'+'z'*64)

if __name__=='__main__':unittest.main()

class HardenedContracts(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.p=Path(self.tmp.name)

    def test_trusted_oracle_output_must_be_exclusive(self):
        import oracle_runner
        oracle=self.p/'trusted.py'
        oracle.write_text('import sys,json\nprint(json.dumps({"output":1}))\n')
        argv=self.p/'argv.json';argv.write_text(json.dumps([sys.executable,str(oracle)]))
        cases=self.p/'cases.jsonl';cases.write_text(json.dumps({'id':'c','input':{}})+'\n')
        target=self.p/'already-existing.jsonl';target.write_text('do not overwrite')
        result=oracle_runner.main(['--cases',str(cases),'--argv-file',str(argv),
                                    '--cwd',str(self.p),'--output',str(target),'--execute-authorized'])
        self.assertEqual(result,2)
        self.assertEqual(target.read_text(),'do not overwrite')

    def test_http_credential_and_host_headers_refused(self):
        import interface_traces
        for header in ('Host','Content-Length','Forwarded','X-Forwarded-Host','Authorization','Cookie'):
            with self.subTest(header=header),self.assertRaises(DataError):
                interface_traces.request_parts({'method':'GET','path':'/','headers':{header:'evil'}},'http://localhost')

    def test_inference_does_not_promote_failed_runner_to_state_fact(self):
        rows={'bad':{'input':{'actions':[{'action':'inc'}]},'observation':{'steps':[
              {'action_index':0,'state':{'n':1}}]},'runner_status':'timeout'}}
        graph=state_inference.infer(rows)
        self.assertEqual(graph['transitions'],[])
        self.assertEqual(graph['skipped'][0]['reason'],'unverified runner status')
