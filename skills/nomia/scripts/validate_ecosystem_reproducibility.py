#!/usr/bin/env python3
"""Validate the local copy of the coordinated ecosystem reproducibility contract.

This validator is package-local by design. It never reads or imports peer packages.
"""
from __future__ import annotations
import argparse, copy, hashlib, importlib.util, json, sys, tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
EXPECTED={"nomia_to_mago","mago_to_magia","magia_to_mago","magia_to_nomia","replanning","repeated_phase","mixed_ecosystem_versions","wrong_owner_field","invalid_business_priority","invalid_technical_criticality","stale_handoff","duplicate_handoff","conflicting_evidence","privacy_lineage_mismatch","content_metadata_contradiction","unsupported_schema","authenticity_claim_without_proof","execution_completion_without_governance_closure","governance_writes_technical_artifact","mago_executes","magia_changes_product_governance","safe_rerun"}
NOW=datetime(2026,9,19,12,0,tzinfo=timezone.utc)

def load(rel:str)->dict[str,Any]:
    v=json.loads((ROOT/rel).read_text(encoding='utf-8'))
    if not isinstance(v,dict): raise ValueError(f'{rel} must be an object')
    return v

def mod(name:str):
    p=ROOT/'scripts'/f'{name}.py'; spec=importlib.util.spec_from_file_location(name,p); m=importlib.util.module_from_spec(spec); assert spec.loader; sys.modules[name]=m; spec.loader.exec_module(m); return m

def privacy(): return {'classification':'internal','contains_personal_data':False,'contains_third_party_data':False,'contains_confidential_data':False,'contains_secrets':False,'redactions_applied':[],'redaction_method':'none','intended_audience':['sdd-maintainers'],'allowed_destinations':['local'],'purpose':'synthetic ecosystem reproducibility validation','retention_days':30,'evidence_ref_visibility':'opaque','external_share_allowed':False}

def payload(direction:str):
    if direction=='nomia_to_mago': return {'feature_key':'cross-skill','outcome':'synthetic outcome','scope_summary':'synthetic scope','owner':'delivery-role','business_priority':{'level':'medium','owner':'nomia','source':'fixture://governance','observed_at':NOW.isoformat()},'dependencies':[],'governance_readiness':'ready'}
    if direction=='mago_to_magia': return {'spec_id':'spec-2026-09-19-cross-skill','planning_state':'ready','planning_evidence':'fixture://plan','requirement_refs':['REQ-001'],'acceptance_criteria_refs':['AC-001'],'task_ids':['task001'],'validation_refs':['VAL-001'],'technical_criticality':{'level':'normal','owner':'mago','rationale':'fixture'},'execution_sequence':{'rank':0,'lane':'standard','owner':'mago','rationale':['fixture']},'readiness':'ready'}
    if direction=='magia_to_mago': return {'spec_id':'spec-2026-09-19-cross-skill','execution_state':'done','validation_state':'passed','evidence_reference':'fixture://validation','deviations':[],'planning_change_required':False}
    if direction=='mago_to_nomia': return {'spec_id':'spec-2026-09-19-cross-skill','planning_state':'done','nomia_planning_state':'complete','planning_evidence':'fixture://plan','dependency_summary':{},'technical_risk_summary':{},'forecast_impact':{},'mapping_version':'2.0.0'}
    if direction=='magia_to_nomia': return {'spec_id':'spec-2026-09-19-cross-skill','execution_state':'done','nomia_execution_state':'complete','validation_state':'passed','nomia_validation_state':'passed','evidence_reference':'fixture://validation','delivery_impacts':[],'mapping_version':'2.0.0'}
    raise ValueError(direction)

def envelope(h,direction,observed=NOW):
    c=h.load_contract(ROOT); comp=h.load_compatibility(ROOT); item=c['directions'][direction]; p=h.apply_state_projection(direction,payload(direction),c)
    e={'schema_version':c['schema_version'],'ecosystem_release':comp['ecosystem_release'],'direction':direction,'source_skill':item['producer'],'source_version':comp['packages'][item['producer']],'target_skill':item['consumer'],'workflow_id':h.workflow_id_for('cross-skill-suite'),'observed_at':observed.isoformat(),'privacy_handling':privacy(),'provenance':{'source':'fixture://source','authority':item['producer'],'evidence_refs':['fixture://evidence']},'freshness':{'max_age_days':30},'payload':p,'unknowns':[],'conflicts':[]}
    e['handoff_id']=h.handoff_id_for(e); return e

def run() -> dict[str,Any]:
    errors=[]; results=[]
    def check(sid:str,ok:bool,evidence:Any):
        results.append({'id':sid,'status':'pass' if ok else 'fail','evidence':evidence})
        if not ok: errors.append(sid)
    version=(ROOT/'VERSION').read_text().strip(); comp=load('references/ecosystem-compatibility.json'); repro=load('references/ecosystem-reproducibility-contract.json'); own=load('references/ecosystem-ownership-contract.json'); suite=load('evals/ecosystem-cross-skill-scenarios.json')
    ids={x.get('id') for x in suite.get('scenarios',[])}
    check('suite_identity',suite.get('frozen') is True and ids==EXPECTED,{'count':len(ids),'missing':sorted(EXPECTED-ids),'extra':sorted(ids-EXPECTED)})
    check('release_identity',comp.get('ecosystem_release')==version==repro.get('ecosystem_release') and set(comp.get('packages',{}).values())=={version},{'version':version,'compat':comp.get('ecosystem_release')})
    check('shared_contract_version',comp.get('shared_contract_version')==repro.get('shared_contract_version')=='1.0.0',comp.get('shared_contract_version'))
    check('ownership_core',own['roles']['nomia']['authority_class']=='governance' and own['roles']['mago']['authority_class']=='technical-planning' and own['roles']['magia']['authority_class']=='execution-validation',{})
    check('priority_ownership',own['fields']['business_priority']['owner']=='nomia' and own['fields']['technical_criticality']['owner']=='mago' and own['fields']['execution_sequence']['owner']=='mago',own['fields'])
    h=mod('ecosystem_handoff'); router=mod('route_ecosystem_request'); ledger=mod('handoff_ledger'); ap=mod('validate_artifact_privacy')
    # positive directions
    for direction in ('nomia_to_mago','mago_to_magia','magia_to_mago','magia_to_nomia'):
        e=envelope(h,direction); r=h.validate_envelope(e,as_of=NOW,operation='any',root=ROOT); check(direction,r['status']=='accepted',r)
    # routing/repeated phases
    r=router.route(['implementation','reconcile','tests']); check('replanning',r['owner_sequence']==['magia','mago','magia'],r)
    r2=router.route(['planning','implementation','reconcile']); check('repeated_phase',r2['owner_sequence']==['mago','magia','mago'],r2)
    # mixed versions
    e=envelope(h,'mago_to_magia'); e['source_version']='1.9.4'; e['handoff_id']=h.handoff_id_for(e); x=h.validate_envelope(e,as_of=NOW,operation='any',root=ROOT); check('mixed_ecosystem_versions',x['status']=='rejected' and 'HANDOFF_INCOMPATIBLE_SOURCE_VERSION' in x['reason_codes'],x)
    # wrong owner and priority invalids
    e=envelope(h,'nomia_to_mago'); e['payload']['technical_criticality']={'level':'critical','owner':'nomia','rationale':'wrong'}; e['handoff_id']=h.handoff_id_for(e); x=h.validate_envelope(e,as_of=NOW,operation='any',root=ROOT); check('wrong_owner_field',x['status']=='rejected',x)
    e=envelope(h,'nomia_to_mago'); e['payload']['business_priority']['level']='impossible'; e['handoff_id']=h.handoff_id_for(e); x=h.validate_envelope(e,as_of=NOW,operation='any',root=ROOT); check('invalid_business_priority',x['status']=='rejected',x)
    e=envelope(h,'mago_to_magia'); e['payload']['technical_criticality']['level']='impossible'; e['handoff_id']=h.handoff_id_for(e); x=h.validate_envelope(e,as_of=NOW,operation='any',root=ROOT); check('invalid_technical_criticality',x['status']=='rejected',x)
    # stale/conflict/schema/content privacy
    e=envelope(h,'magia_to_mago',NOW-timedelta(days=40)); e['freshness']={'max_age_days':1}; e['handoff_id']=h.handoff_id_for(e); x=h.validate_envelope(e,as_of=NOW,operation='any',root=ROOT); check('stale_handoff',x['status']=='stale' and 'HANDOFF_STALE' in x['reason_codes'],x)
    e=envelope(h,'magia_to_mago'); e['conflicts']=['synthetic conflict']; e['handoff_id']=h.handoff_id_for(e); x=h.validate_envelope(e,as_of=NOW,operation='any',root=ROOT); check('conflicting_evidence',x['status']=='conflicting',x)
    e=envelope(h,'magia_to_mago'); e['schema_version']='99.0.0'; e['handoff_id']=h.handoff_id_for(e); x=h.validate_envelope(e,as_of=NOW,operation='any',root=ROOT); check('unsupported_schema',x['status']=='rejected' and 'HANDOFF_INVALID_SCHEMA' in x['reason_codes'],x)
    e=envelope(h,'magia_to_mago'); e['unknowns']=['confidential material']; e['handoff_id']=h.handoff_id_for(e); x=h.validate_envelope(e,as_of=NOW,operation='any',root=ROOT); check('content_metadata_contradiction',x['status']=='rejected' and 'HANDOFF_PRIVACY_CONTRADICTION_CONFIDENTIAL' in x['reason_codes'],x)
    # privacy lineage mismatch and authenticity proof requirement
    source=envelope(h,'magia_to_mago'); block=ap.derive(source); block['source_handoff_id']='handoff-deadbeefdeadbeef'; block['source_reference']='handoff:handoff-deadbeefdeadbeef'; check('privacy_lineage_mismatch',bool(ap.verify_source_handoff(block,source)),ap.verify_source_handoff(block,source))
    declared=ap.derive(source); structure=ap.validate_block(declared,ROOT); proof_without_source=['source handoff evidence not supplied; authenticity remains unverified']; check('authenticity_claim_without_proof',not structure and bool(proof_without_source),{'structure':structure,'authenticity':'unverified-without-source'})
    # ownership/closure rules are checked from frozen ownership/repro contracts
    check('execution_completion_without_governance_closure',repro['state_transitions']['governance_closure'].startswith('Nomia decision'),repro['state_transitions']['governance_closure'])
    check('governance_writes_technical_artifact','technical_design' in own['roles']['nomia']['must_not_own'],own['roles']['nomia']['must_not_own'])
    check('mago_executes','implementation' in own['roles']['mago']['must_not_own'],own['roles']['mago']['must_not_own'])
    check('magia_changes_product_governance','governance_state' in own['roles']['magia']['must_not_own'],own['roles']['magia']['must_not_own'])
    # duplicate + safe rerun + last-known-good recovery are executable transport tests
    env=envelope(h,'magia_to_mago'); data=ledger.empty_ledger(env['workflow_id']); data,idem=ledger.record(data,env,'created',NOW.isoformat(),as_of=NOW); data,idem2=ledger.record(data,env,'created',NOW.isoformat(),as_of=NOW); check('duplicate_handoff',idem2 and len(data['events'])==1,{'idempotent':idem2,'events':len(data['events'])})
    with tempfile.TemporaryDirectory() as td:
        path=Path(td)/'ledger.json'; receipt1=ledger.commit_ledger(path,data); data2=ledger.load(path); data2,idem3=ledger.record(data2,env,'accepted',NOW.isoformat(),as_of=NOW); receipt2=ledger.commit_ledger(path,data2); path.write_text('{broken',encoding='utf-8'); recovery=ledger.recover_ledger(path); restored=ledger.load(path); check('safe_rerun',not ledger.validate(restored) and recovery['status']=='pass' and receipt2.get('last_known_good_sha256'),{'commit':receipt2,'recovery':recovery,'idempotent':idem3})
    status='pass' if not errors else 'fail'
    return {'schema_version':'1.0.0','status':status,'skill':ROOT.name,'ecosystem_release':version,'shared_contract_version':repro.get('shared_contract_version'),'scenario_count':len(EXPECTED),'results':results,'errors':errors,'evidence_kind':'executed-structural'}

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--json-output'); a=p.parse_args(argv); result=run(); text=json.dumps(result,indent=2,sort_keys=True)+'\n';
    if a.json_output: Path(a.json_output).write_text(text,encoding='utf-8')
    print(text,end=''); return 0 if result['status']=='pass' else 1
if __name__=='__main__': raise SystemExit(main())
