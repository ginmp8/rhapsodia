"""Focused acceptance of research-backed opt-in and portable core capabilities."""
from __future__ import annotations
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

SCRIPTS=Path(__file__).resolve().parents[1]/'scripts'
sys.path.insert(0,str(SCRIPTS))
from behavior_lab import DataError, load_corpus, strict_json
from effect_capture import snapshot, changes, CaptureError
import execution_policy
import probe_engine
import state_inference
import evidence_ir
import tool_adapters
import interface_traces
import web_investigator
from oracle_runner import run_one
from behavioral_pipeline import run_pair


class TestFullCapabilities(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
    def file(self,name,text):
        p=self.root/name
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(text,encoding='utf-8')
        return p
    def corpus(self):
        cases=[{'id':'s1','schema_version':'2.0','input':{'actions':[{'action':'open','id':1}, {'action':'close'}]},
                'observation':{'steps':[{'action_index':0,'output':True,'state':{'phase':'open'}},
                                        {'action_index':1,'output':False,'state':{'phase':'closed'}}],
                               'output':False}}]
        return self.file('cases.jsonl',''.join(json.dumps(x)+'\n' for x in cases))

    def test_typed_v2_values_and_v1_compat(self):
        p=self.file('typed.jsonl',json.dumps({'id':'c','schema_version':'2.0','input':{'a':{
            '$type':'bigint','decimal':'123456789012345678901234567890'},
            'b':{'$type':'datetime-offset','iso8601':'2026-10-12T00:57:00-03:00'},
            'c':{'$type':'undefined'}},'observation':{'output':{
            '$type':'float-special','value':'-0'}}})+'\n')
        self.assertIn('c',load_corpus(p))
        for invalid in ({'$type':'bigint','decimal':'012'}, {'$type':'float-special','value':'oops'},
                        {'$type':'datetime-offset','iso8601':'2026-10-12'}, {'$type':'bytes','base64':'???'},
                        {'$type':'not-supported'}):
            p.write_text(json.dumps({'id':'x','schema_version':'2.0','input':invalid,'observation':{'output':1}})+'\n')
            with self.assertRaises(DataError):load_corpus(p)
        p.write_text(json.dumps({'id':'legacy','input':None,'observation':{'output':None}})+'\n')
        self.assertIn('legacy',load_corpus(p))

    def test_file_effect_snapshot_and_trusted_capture(self):
        cwd=self.root/'cwd';cwd.mkdir()
        before=snapshot(cwd)
        (cwd/'state.txt').write_text('fresh')
        after=snapshot(cwd)
        self.assertEqual(changes(before,after)[0]['operation'],'create')
        script=self.file('trusted.py',"from pathlib import Path\nimport json,sys\nvalue=json.loads(sys.stdin.readline())\nPath('made.txt').write_text(str(value['number']))\nprint(json.dumps({'output':value['number']}))\n")
        status,obs=run_one([sys.executable,str(script)],{'number':4},cwd,3,10240,512,capture_fs=True)
        self.assertEqual(status,'ok')
        self.assertEqual(obs['effects'][0]['path'],'made.txt')
        status2,obs2=run_one([sys.executable,str(script)],{'number':5},cwd,3,10240,512,capture_fs=True)
        self.assertEqual(status2,'ok')
        self.assertEqual(obs2['effects'][0]['operation'],'modify')
        try:
            (cwd/'linked').symlink_to(script)
        except (OSError,NotImplementedError):
            pass  # symlink creation may require Windows Developer Mode
        else:
            with self.assertRaises(CaptureError):snapshot(cwd)

    def test_trusted_pipeline_rejects_unresettable_shrinker(self):
        with self.assertRaises(DataError):
            run_pair(self.root/'x',self.root/'cmd',self.root/'other',self.root,self.root,
                     self.root/'out',execute_authorized=True,capture_fs=True,shrink_trials=1)

    def test_adaptive_probes_and_seeded_fuzz(self):
        corpus=self.corpus()
        a=probe_engine.generate(corpus,max_cases=60,seed=23,fuzz=True)
        b=probe_engine.generate(corpus,max_cases=60,seed=23,fuzz=True)
        self.assertEqual(a,b)
        self.assertGreater(len(a['cases']),10)
        self.assertLessEqual(len(a['cases']),60)
        self.assertTrue(all('observation' not in c and c['status']=='unobserved' for c in a['cases']))
        original={probe_engine.canonical(r['input']) for r in load_corpus(corpus).values()}
        self.assertFalse(any(probe_engine.canonical(c['input']) in original for c in a['cases']))
        feedback=self.file('feedback.json',json.dumps({'findings':[{'id':'s1','class':'differential_mismatch'}]}))
        self.assertTrue(probe_engine.generate(corpus,feedback,max_cases=3)['cases'])

    def test_openapi_seeds(self):
        api=self.file('openapi.json',json.dumps({'paths':{'/customer':{'get':{},'post':{}}}}))
        seeds=probe_engine.generate(None,openapi=api,max_cases=10)
        self.assertTrue(any(x['input'].get('path')=='/customer' for x in seeds['cases']))

    def test_state_inference_and_coverage_gaps(self):
        doc=state_inference.infer(load_corpus(self.corpus()),alphabet=[{'action':'open','id':1},{'action':'missing'}])
        self.assertEqual(doc['cases_with_steps'],1)
        self.assertEqual(len(doc['transitions']),2)
        self.assertTrue(doc['missing_transition_probes'])
        self.assertEqual(doc['conflicts'],[])
        cases=load_corpus(self.corpus());another=json.loads(json.dumps(cases['s1']))
        another['id']='s2';another['observation']['steps'][0]['state']={'phase':'DIFFERENT'}
        cases['s2']=another
        self.assertTrue(state_inference.infer(cases)['conflicts'])
        with self.assertRaises(DataError):
            state_inference.active_capture([{'action':'open'}],self.root/'cmd',self.root)

    def test_graph_ir_sqlite_idempotence_and_export(self):
        raw={'results':[{'path':'Demo.class','format':'jvm','module':{'class_name':'Demo','methods':[
            {'name':'go','descriptor':'()V','calls':[{'owner':'java/lang/Math','name':'abs','offset':3}]}]}}]}
        report=self.file('report.json',json.dumps(raw))
        db=self.root/'graph.sqlite'
        result=evidence_ir.ingest([report],db)
        self.assertGreater(len(result['reports'][0]['nodes']),2)
        self.assertTrue(any(e['kind']=='calls-at-site' for e in result['reports'][0]['edges']))
        again=evidence_ir.ingest([report],db)
        self.assertEqual(again['sqlite_import'][0]['status'],'unchanged-reused')
        exported=evidence_ir.export(db)
        self.assertEqual(len(exported['sources']),1)
        self.assertEqual(len(exported['edges']),len(result['reports'][0]['edges']))

    def test_static_policy_and_oci_fail_closed(self):
        self.assertTrue(execution_policy.preflight('static')['allowed'])
        for mode in ('trusted-local','oci-pinned'):
            with self.assertRaises(DataError):execution_policy.preflight(mode)
        with self.assertRaises(DataError):
            execution_policy.preflight('oci-pinned',authorized=True,isolated_approved=True,
                                       image='image:latest')
        with patch('execution_policy.shutil.which',return_value='/usr/bin/docker'):
            conf=execution_policy.preflight('oci-pinned',authorized=True,isolated_approved=True,
                                           image='local/oracle@sha256:'+('a'*64))
        args=conf['executable_argv']
        self.assertIn('--network=none',args)
        self.assertIn('--read-only',args)
        self.assertIn('--pull=never',args)
        self.assertFalse(any('--mount' in a or '--volume' in a for a in args))

    def test_optional_decompiler_adapters_mock_and_roslyn(self):
        self.assertIn('ilspy',tool_adapters.detect()['available'])
        target=self.file('sample.dll','placeholder not an actual assembly')
        with self.assertRaises(DataError):
            tool_adapters.run('ilspy',target,self.root/'no')
        def emulate(cmd,cwd,env,timeout,stdout_path,stderr_path):
            out=Path(cmd[cmd.index('-o')+1]);out.mkdir(parents=True,exist_ok=True)
            (out/'Demo.cs').write_text('class Demo {}')
            stdout_path.write_bytes(b'');stderr_path.write_bytes(b'')
            return 0
        fake_tool=self.root/'fake-ilspycmd';fake_tool.write_bytes(b'#!/bin/sh\n');fake_tool.chmod(0o755)
        with patch('tool_adapters.bounded_process',side_effect=emulate):
            report=tool_adapters.run('ilspy',target,self.root/'decompiled',authorized=True,
                                     environment_approved=True,tool_override=fake_tool.resolve())
        self.assertTrue((self.root/'decompiled'/'Demo.cs').exists())
        self.assertEqual(report['provider'],'ilspy')
        bad=self.file('roslyn.json',json.dumps({'symbols':[{'name':'N.C.M','kind':'method'}]}))
        result=tool_adapters.import_roslyn(bad)
        self.assertFalse(result['compilation_identity_supplied'])
        self.assertEqual(result['symbols'][0]['evidence_level'],'unverified_semantic_export')
        cmd=tool_adapters.build_command('ghidra','/bin/analyzeHeadless',target,self.root/'build')
        self.assertIn('-postScript',cmd)
        self.assertIn('-deleteProject',cmd)

    def test_har_redaction_and_openapi_extraction(self):
        doc=self.file('capture.har',json.dumps({'log':{'entries':[{'request':{
            'method':'POST','url':'https://example.com/thing?key=secret','headers':[{'name':'X-API-Key','value':'supersecret'}],
            'postData':{'text':'private'}},'response':{'status':201}}]}}))
        result=interface_traces.inspect(doc,'har')
        self.assertEqual(result['operations'][0]['path'],'/thing')
        self.assertNotIn('secret',json.dumps(result))
        with self.assertRaises(DataError):
            interface_traces.request_parts({'method':'GET','path':'//attacker.com'},'http://localhost')
        with self.assertRaises(DataError):
            interface_traces.request_parts({'method':'GET','path':'/','headers':{'Authorization':'private'}},'http://localhost')
        with self.assertRaises(DataError):
            interface_traces.origin_url('https://public.example.org')

    def test_real_local_http_replay_and_nonredirect(self):
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path=='/redirect':
                    self.send_response(302);self.send_header('Location','http://evil.invalid/');self.end_headers();return
                body=b'{"ok":true}';self.send_response(200)
                self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(body)
            def log_message(self,*args):pass
        server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        self.addCleanup(lambda:(server.shutdown(),server.server_close(),thread.join(timeout=2)))
        cases=self.file('http-input.jsonl',''.join(json.dumps({'id':n,'input':{'method':'GET','path':p}})+'\n'
                                                  for n,p in (('a','/hello'),('b','/redirect'))))
        with self.assertRaises(DataError):
            interface_traces.replay(cases,f'http://127.0.0.1:{server.server_port}')
        result=interface_traces.replay(cases,f'http://127.0.0.1:{server.server_port}',authorized=True,include_json_body=True)
        self.assertEqual(result['completed'],2)
        self.assertEqual(result['cases'][0]['observation']['output']['json'],{'ok':True})
        self.assertEqual(result['cases'][1]['observation']['output']['http_status'],302)
        self.assertEqual(result['cases'][0]['observation']['effects'][0]['kind'],'http')

    def test_browser_adapter_policy_without_playwright(self):
        p=self.file('actions.json',json.dumps([{'type':'goto','path':'/'}, {'type':'text-hash','selector':'h1'}]))
        self.assertEqual(len(web_investigator.checked_actions(p)),2)
        with self.assertRaises(DataError):
            web_investigator.inspect_browser(mode='capture',origin='http://localhost',actions=[{'type':'goto','path':'/'}])
        self.file('actions.json',json.dumps([{'type':'goto','path':'//outside.com'}]))
        with self.assertRaises(DataError):web_investigator.checked_actions(p)


if __name__=='__main__':unittest.main()
