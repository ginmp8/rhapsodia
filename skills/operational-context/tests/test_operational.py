"""Portable behavior, boundary, failure and public CLI regression checks."""
from __future__ import annotations
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from oc_core import actions, context, metrics, policy, registry, sharing
from oc_core.common import RuntimeFault, canonical, file_hash, sha
from oc_core.store import Cache
CLI = Path(__file__).resolve().parents[1] / 'scripts' / 'operational.py'

class OperationalTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);(self.root/'src').mkdir()
        (self.root/'src/a.txt').write_text('one\ntwo\nthree\n');(self.root/'contract.md').write_text('Mandatory gate stays required.\n')
        self.cache=Cache(self.root)
    def action(self):
        return {'task_class':'codegen','argv':['generator','--offline'],'input_roots':['src'],'toolchain_digest':'a'*64,
                'environment_digest':'b'*64,'config_digest':'c'*64,'policy_digest':'d'*64,'closure_complete':True,
                'hermetic':True,'network':False,'requires_fresh':False,'requires_independent':False}
    def stored_action(self):
        request=self.action();key=actions.action_key(self.cache,request)
        (self.root/'result.txt').write_text('generated')
        receipt={'schema':'action-result/v1','producer':'magia','action_digest':key['action_digest'],'status':'passed',
                 'output_files':{'result.txt':file_hash(self.root/'result.txt')}}
        (self.root/'receipt.json').write_bytes(canonical(receipt))
        result=actions.store_result(self.cache,{'action':request,'receipt_path':'receipt.json'})
        return request,result
    def pack(self,**extra):
        return context.build(self.cache,{'task_id':'unit','goal':'Review selected change','required':[{'path':'contract.md','role':'contract'}],**extra})
    def artifact(self):
        return registry.publish(self.cache,{'kind':'artifact','path':'src/a.txt','owner':'magia','label':'candidate'})
    def event(self,arm='baseline',sample=0,**kw):
        return {'run_id':'run-'+arm,'event_id':'event-'+str(sample),'scenario_id':'scenario','host':'generic',
                'model':'fixed-model','config_digest':'a'*64,'input_digest':'b'*64,'evaluator_digest':'c'*64,
                'cache_state':'warm','sample':sample,'phase':'end-to-end','arm':arm,'duration_ms':100,'quality_pass':True,
                'provider':'openai','usage':{'input_tokens':100,'input_tokens_details':{'cached_tokens':80},'output_tokens':20},**kw}
    def cli(self,command,request,expected=0):
        p=subprocess.run([sys.executable,'-I','-S','-B',str(CLI),'--workspace',str(self.root),command],
                         input=json.dumps(request),text=True,capture_output=True,timeout=15)
        self.assertEqual(p.returncode,expected,p.stdout+p.stderr);self.assertNotIn('Traceback',p.stderr)
        return json.loads(p.stdout)
    def test_pack_deterministic_and_no_write(self):
        a=self.pack();self.assertEqual(a,self.pack());self.assertEqual(a['output_bytes'],len(canonical(a)))
        self.assertFalse(self.cache.root.exists());self.assertEqual(context.verify(self.cache,a)['status'],'current')
    def test_pack_stale_on_contract_change(self):
        p=self.pack();(self.root/'contract.md').write_text('changed')
        self.assertFalse(context.verify(self.cache,p)['required_complete'])
    def test_mandatory_budget_fails_without_writing(self):
        with self.assertRaises(RuntimeFault):self.pack(budget_bytes=128)
        self.assertFalse(self.cache.root.exists())
    def test_optional_budget_is_explicit(self):
        required=self.pack();budget=required['output_bytes']+80
        pack=self.pack(optional=[{'path':'src/a.txt'}],budget_bytes=budget)
        self.assertTrue(pack['incomplete']);self.assertEqual(pack['omitted_optional'],['src/a.txt'])
    def test_text_requires_approval(self):
        with self.assertRaises(RuntimeFault):self.pack(include_text=True)
    def test_line_slice_pins_whole_file(self):
        p=self.pack(optional=[{'path':'src/a.txt','start_line':2,'end_line':2}],include_text=True,approved_content=True)
        self.assertEqual(p['optional'][0]['text'],'two\n');(self.root/'src/a.txt').write_text('changed\ntwo\nthree\n')
        self.assertEqual(context.verify(self.cache,p)['status'],'stale')
    def test_malformed_pack_fails_closed(self):
        p=self.pack();p['optional']=[None];p['pack_id']=sha({k:v for k,v in p.items() if k not in {'pack_id','output_bytes'}})
        with self.assertRaises(RuntimeFault):context.verify(self.cache,p)
    def test_private_and_traversal_paths_rejected(self):
        for path in ['../escape','.env','.git/config','/absolute','src/../contract.md']:
            with self.subTest(path=path),self.assertRaises(RuntimeFault):self.pack(required=[{'path':path}])
    def test_symlink_rejected(self):
        (self.root/'src/link').symlink_to(self.root/'contract.md')
        with self.assertRaises(RuntimeFault):self.pack(optional=[{'path':'src/link'}])
    def test_prefix_hash_excludes_dynamic_tail(self):
        req={'static_refs':[{'path':'contract.md'}],'dynamic_tail':'first','approved_content':True}
        a=context.prefix(self.cache,req);b=context.prefix(self.cache,dict(req,dynamic_tail='second'))
        self.assertEqual(a['prefix_sha256'],b['prefix_sha256']);self.assertIsNone(a['cache_hit'])
    def test_registry_hash_and_expiry(self):
        key=self.artifact()['id'];v=self.cache.get('artifact',key)
        with patch('oc_core.registry.time.time',return_value=v['observed_at']+86401):self.assertEqual(registry.freshness(self.cache,v),'expired')
        (self.root/'src/a.txt').write_text('changed');self.assertEqual(registry.freshness(self.cache,v),'stale')
    def test_evidence_requires_producer_match(self):
        (self.root/'r.json').write_bytes(canonical({'producer':'mago','status':'pass'}))
        with self.assertRaises(RuntimeFault):registry.publish(self.cache,{'kind':'evidence','path':'r.json','owner':'magia','label':'proof'})
    def test_evidence_added_file_invalidates(self):
        receipt={'producer':'magia','status':'passed','candidate_files':actions.inventory(self.cache,['src']),'request':{'candidate_roots':['src']}}
        (self.root/'r.json').write_bytes(canonical(receipt));p=registry.publish(self.cache,{'kind':'evidence','path':'r.json','owner':'magia','label':'proof'})
        (self.root/'src/b.txt').write_text('new')
        q=registry.query(self.cache,{'kind':'evidence','ids':[p['id']]});self.assertEqual(q['records'][0]['freshness'],'stale');self.assertFalse(q['records'][0]['domain_approval'])
    def test_object_corruption_rejected(self):
        key=self.artifact()['id'];(self.cache.root/'artifact'/f'{key}.json').write_text('{}')
        with self.assertRaises(RuntimeFault):self.cache.get('artifact',key)
    def test_foreign_scope_copy_rejected(self):
        key=self.artifact()['id'];other=self.root/'other';other.mkdir();target=Cache(other)
        directory=target.root/'artifact';directory.mkdir(parents=True);(directory/f'{key}.json').write_bytes((self.cache.root/'artifact'/f'{key}.json').read_bytes())
        with self.assertRaises(RuntimeFault):target.get('artifact',key)
    def test_action_hit_keeps_gates_external(self):
        a,s=self.stored_action();r=actions.lookup(self.cache,{'action':a,'id':s['id']})
        self.assertEqual(r['status'],'hit');self.assertFalse(r['domain_approval'])
    def test_each_action_dimension_invalidates(self):
        a,s=self.stored_action()
        for field in ['toolchain_digest','environment_digest','config_digest','policy_digest']:
            with self.subTest(field=field):self.assertEqual(actions.lookup(self.cache,{'action':dict(a,**{field:'f'*64})})['status'],'miss')
        changed=dict(a,argv=['generator','--different']);self.assertEqual(actions.lookup(self.cache,{'action':changed})['status'],'miss')
    def test_input_addition_deletion_and_mutation_miss(self):
        a,s=self.stored_action();(self.root/'src/added.txt').write_text('new')
        self.assertEqual(actions.lookup(self.cache,{'action':a})['status'],'miss');(self.root/'src/added.txt').unlink()
        (self.root/'src/a.txt').write_text('changed');self.assertEqual(actions.lookup(self.cache,{'action':a})['status'],'miss')
        (self.root/'src/a.txt').unlink();self.assertEqual(actions.lookup(self.cache,{'action':a})['status'],'miss')
    def test_receipt_and_output_mutation_miss(self):
        a,s=self.stored_action();(self.root/'result.txt').write_text('altered');self.assertEqual(actions.lookup(self.cache,{'action':a})['status'],'miss')
        (self.root/'result.txt').write_text('generated');(self.root/'receipt.json').write_text('{}');self.assertEqual(actions.lookup(self.cache,{'action':a})['status'],'miss')
    def test_unsafe_actions_bypass(self):
        for change in [{'network':True},{'hermetic':False},{'closure_complete':False},{'requires_fresh':True},{'requires_independent':True},{'task_class':'test'}]:
            with self.subTest(change=change):self.assertEqual(actions.lookup(self.cache,{'action':dict(self.action(),**change)})['status'],'bypass')
    def test_action_symlink_not_silently_ignored(self):
        (self.root/'src/link').symlink_to(self.root/'contract.md')
        with self.assertRaises(RuntimeFault):actions.action_key(self.cache,self.action())
    def test_missing_usage_is_not_zero(self):
        u=metrics.normalize_usage('generic',{});self.assertIsNone(u['input_tokens']);self.assertIsNone(u['billed_tokens'])
    def test_cached_tokens_not_added_twice(self):
        u=metrics.normalize_usage('openai',{'input_tokens':100,'input_tokens_details':{'cached_tokens':80}})
        self.assertEqual(u['input_tokens'],100);self.assertEqual(u['uncached_input_tokens'],20)
    def test_anthropic_counts_are_explicit(self):
        u=metrics.normalize_usage('anthropic',{'input_tokens':10,'cache_read_input_tokens':80,'cache_creation_input_tokens':20,'output_tokens':5})
        self.assertEqual(u['input_tokens'],110)
    def test_normalized_event_is_idempotent(self):
        a=metrics.event(self.event());self.assertEqual(a,metrics.event(a))
    def test_unavailable_counters_stay_unavailable(self):
        u=metrics.normalize_usage('anthropic',{'input_tokens':10});self.assertIsNone(u['input_tokens'])
    def test_metric_rejects_prompt_field_and_nonfinite(self):
        for change in [{'prompt':'secret'},{'duration_ms':float('nan')},{'input_digest':'not-a-digest'}]:
            with self.subTest(change=change),self.assertRaises(RuntimeFault):metrics.event(self.event(**change))
    def test_metrics_do_not_sum_parallel_duration(self):
        metrics.record(self.cache,self.event());self.assertIsNone(metrics.summary(self.cache,{})['wall_clock_total_ms'])
    def test_duplicate_metric_id_conflict_detected(self):
        metrics.record(self.cache,self.event());metrics.record(self.cache,self.event(duration_ms=200))
        with self.assertRaises(RuntimeFault):metrics.summary(self.cache,{})
    def test_compare_detects_confounds(self):
        with self.assertRaises(RuntimeFault):metrics.compare({'baseline':[self.event()],'candidate':[self.event('candidate',model='other')]})
    def test_compare_does_not_claim_slowdown_as_improvement(self):
        result=metrics.compare({'baseline':[self.event(sample=i) for i in range(2)],'candidate':[self.event('candidate',sample=i,duration_ms=200) for i in range(2)]})
        self.assertFalse(result['measured_improvement_claim_allowed'])
    def test_compare_quality_regression_blocks_claim(self):
        result=metrics.compare({'baseline':[self.event(sample=i) for i in range(2)],'candidate':[self.event('candidate',sample=i,duration_ms=50,quality_pass=False) for i in range(2)]})
        self.assertFalse(result['quality_gate']);self.assertFalse(result['measured_improvement_claim_allowed'])
    def test_parallel_only_independent_readers(self):
        units=[{'id':str(i),'effect':'read','owner':'mago','estimated_ms':1000,'independent':True} for i in range(2)]
        req={'units':units,'host_parallel':True,'spawn_ms':10,'synthesis_ms':10}
        self.assertEqual(policy.decide(req)['strategy'],'read-only-fanout')
        units[0]['effect']='write';self.assertEqual(policy.decide(req)['strategy'],'sequential')
    def test_delegation_unknown_estimates_sequential(self):
        r=policy.decide({'units':[{'id':'a','effect':'read'},{'id':'b','effect':'read'}],'host_parallel':True})
        self.assertEqual(r['strategy'],'sequential')
    def test_retrieval_does_not_force_graph(self):
        req={'has_exact_refs':True,'relationship_question':True,'repeated_query':True,'graph_available':True}
        self.assertEqual(policy.retrieval(req)['strategy'],'exact-refs')
    def test_cross_workspace_import_quarantined(self):
        key=self.artifact()['id'];exchange=sharing.export_refs(self.cache,{'kind':'artifact','ids':[key],'approved':True})
        self.assertNotIn('path',json.dumps(exchange['records']));other=self.root/'other';other.mkdir();cache=Cache(other)
        r=sharing.import_refs(cache,{'exchange':exchange,'approved':True,'allowed_source_scope':self.cache.scope})
        self.assertEqual(r['status'],'quarantined');self.assertEqual(cache.keys('artifact'),[]);self.assertEqual(cache.keys('action'),[])
    def test_exchange_rejects_missing_consent_and_wrong_scope(self):
        key=self.artifact()['id']
        with self.assertRaises(RuntimeFault):sharing.export_refs(self.cache,{'kind':'artifact','ids':[key],'approved':False})
        e=sharing.export_refs(self.cache,{'kind':'artifact','ids':[key],'approved':True})
        with self.assertRaises(RuntimeFault):sharing.import_refs(self.cache,{'exchange':e,'approved':True,'allowed_source_scope':'a'*64})
    def test_lease_cas_fencing_and_release(self):
        req={'operation':'acquire','resource':'src/a.txt','holder':'writer-a'};a=sharing.lease(self.cache,req)
        with self.assertRaises(RuntimeFault):sharing.lease(self.cache,dict(req,holder='writer-b'))
        owns={'resource':req['resource'],'holder':req['holder'],'token':a['token'],'generation':a['generation']}
        self.assertEqual(sharing.lease(self.cache,dict(owns,operation='check'))['status'],'current')
        sharing.lease(self.cache,dict(owns,operation='release'));b=sharing.lease(self.cache,dict(req,holder='writer-b'))
        self.assertGreater(b['generation'],a['generation'])
        with self.assertRaises(RuntimeFault):sharing.lease(self.cache,dict(owns,operation='renew'))
    def test_graph_is_projection_without_paths(self):
        key=self.artifact()['id'];g=sharing.graph(self.cache,{'kind':'artifact','ids':[key]})
        self.assertEqual(g['schema_version'],'graph-patch-v1');self.assertNotIn(str(self.root),json.dumps(g))
    def test_public_cli_standalone(self):
        r=self.cli('pack',{'task_id':'one','goal':'Review','required':[{'path':'contract.md'}]});self.assertTrue(r['required_complete'])
    def test_malformed_enums_return_json_error(self):
        cases=[('action-key',dict(self.action(),task_class=[])),('index',{'kind':[],'owner':'magia','path':'src/a.txt','label':'test'}),
               ('delegate',{'units':[{'id':'a','effect':[]}]}),('lease',{'operation':[],'resource':'a','holder':'b'}),
               ('pack',{'task_id':'a','goal':'b','required':[{'path':123}]})]
        for cmd,req in cases:
            with self.subTest(command=cmd):self.assertEqual(self.cli(cmd,req,2)['status'],'error')
    def test_output_card_keeps_log_external(self):
        (self.root/'build.log').write_text('line\n'*300)
        r=self.cli('output-card',{'path':'build.log','observed_status':'failed','budget_bytes':1024})
        self.assertTrue(r['content_omitted']);self.assertNotIn('excerpt',r);self.assertEqual(r['sha256'],file_hash(self.root/'build.log'))

if __name__=='__main__':unittest.main()
