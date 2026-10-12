#!/usr/bin/env python3
"""Finite, evidence-bound reconstruction obligations and partial-order traces.

Does not infer expected outputs, assume runtime authority, or silently close
coverage gaps. Proof status is about inspected receipts, not universal parity.
"""
from __future__ import annotations

import hashlib
import hmac
import json
from collections import defaultdict,deque
from artifact_index import ArtifactError,digest
from investigation_store import canonical

KINDS = {'positive','negative','malformed','boundary','stateful','failure','concurrency','retry','cancellation'}
AUTHORITY = {'static':0,'user_supplied':0,'recorded':1,'trusted_runtime_receipt':2}
MAX_OBLIGATIONS = 1500


def _ensure_str(s, field, limit=256):
    if not isinstance(s,str) or not s or len(s)>limit:
        raise ArtifactError(f'{field} must be a bounded nonempty string')
    return s


def generate_obligations(graph:dict,limit:int=150) -> list[dict]:
    """Static candidates; not verified requirements or accepted behavior."""
    if not isinstance(graph,dict) or graph.get('format') != 'application-graph-1':
        raise ArtifactError('application graph required')
    obligations=[]
    for node in graph.get('nodes',[]):
        if node.get('role') not in ('route','event-channel','export'):
            continue
        name=node.get('symbol') or node.get('node_id')
        ident='ob_'+digest(str(name).encode('utf8'))[:22]
        category='request-response' if node.get('role')=='route' else ('export-shape' if node['role']=='export' else 'event-protocol')
        obligations.append({'obligation_id':ident,'title':str(name)[:180],
                            'layer':node['role'],'family':category,'required':False,
                            'required_case_kinds':['positive','negative'],
                            'source_evidence_id':None,
                            'provenance':'static-hypothesis','needs_review':True})
    result={ob['obligation_id']:ob for ob in obligations}
    return [result[k] for k in sorted(result)[:max(1,min(limit,MAX_OBLIGATIONS))]]


def _sha256_text(value) -> bool:
    return isinstance(value, str) and len(value)==64 and all(c in '0123456789abcdef' for c in value)


def verify_trusted_receipt(receipt: dict, source_sha256: str, candidate_sha256: str,
                           expected_cases: list, trusted_verifier_key: bytes | None) -> bool:
    """Authenticate finite verification metadata signed by an independent recorder.

    A signature authenticates possession of the operator-provisioned key, not
    execution isolation, tool security or universal input equivalence. The
    signer is deliberately outside this workbench's untrusted analysis path.
    """
    if not isinstance(receipt,dict) or not isinstance(trusted_verifier_key,bytes) or len(trusted_verifier_key)<32:
        return False
    if receipt.get('authority')!='trusted_runtime_receipt' or receipt.get('result')!='pass':
        return False
    if receipt.get('source_sha256')!=source_sha256 or not _sha256_text(source_sha256):
        return False
    if receipt.get('candidate_sha256')!=candidate_sha256 or not _sha256_text(candidate_sha256):
        return False
    if not _sha256_text(receipt.get('corpus_sha256')):
        return False
    cases=receipt.get('cases')
    if not isinstance(cases,list) or len(cases)>64 or any(c not in KINDS for c in cases):
        return False
    if not set(expected_cases).issubset(set(cases)):
        return False
    if not isinstance(receipt.get('recorder'),str) or not receipt['recorder'].strip():
        return False
    signature=receipt.get('attestation_hmac_sha256')
    if not _sha256_text(signature):
        return False
    unsigned={k:v for k,v in receipt.items() if k not in ('receipt_sha256','attestation_hmac_sha256')}
    try:
        serialized=canonical(unsigned)
    except (ValueError,TypeError):
        return False
    if digest(serialized)!=receipt.get('receipt_sha256'):
        return False
    computed=hmac.new(trusted_verifier_key, serialized, hashlib.sha256).hexdigest()
    return hmac.compare_digest(computed, signature)


def assess_obligations(obligations:list,bindings:list,verification_records:list,
                       unknowns:list|None=None, trusted_verifier_key:bytes|None=None) -> dict:
    """Claim finite closure only for independently authenticated matching receipts."""
    if not all(isinstance(v,list) for v in (obligations,bindings,verification_records)):
        raise ArtifactError('obligations, bindings and verifications must be arrays')
    if len(obligations)>MAX_OBLIGATIONS or len(bindings)>MAX_OBLIGATIONS*2 or len(verification_records)>MAX_OBLIGATIONS*3:
        raise ArtifactError('obligation ledger budget exceeded')
    by_id=defaultdict(list)
    for binding in bindings:
        if not isinstance(binding,dict):raise ArtifactError('invalid binding')
        by_id[_ensure_str(binding.get('obligation_id'),'binding obligation_id')].append(binding)
    receipts=defaultdict(list)
    for receipt in verification_records:
        if not isinstance(receipt,dict):raise ArtifactError('invalid verification record')
        receipts[_ensure_str(receipt.get('obligation_id'),'receipt obligation_id')].append(receipt)
    ids=set();results=[]
    for obligation in obligations:
        if not isinstance(obligation,dict):raise ArtifactError('invalid obligation')
        ident=_ensure_str(obligation.get('obligation_id'),'obligation_id')
        if ident in ids:raise ArtifactError('duplicated obligation id')
        ids.add(ident)
    for obligation in obligations:
        ident=obligation['obligation_id']
        title=_ensure_str(obligation.get('title'),'title',512)
        required=obligation.get('required') is True
        needs_review=obligation.get('needs_review') is True
        cases=obligation.get('required_case_kinds',[])
        if not isinstance(cases,list) or not cases or len(cases)>len(KINDS) or any(x not in KINDS for x in cases) or len(set(cases))!=len(cases):
            raise ArtifactError('invalid required case kinds')
        reasons=[]
        bb=by_id.get(ident,[])
        candidate_sha256=None
        if len(bb)!=1:
            reasons.append('missing-or-ambiguous-unique-binding')
        else:
            binding=bb[0]
            if not isinstance(binding.get('owner'),str) or not binding['owner'].strip():
                reasons.append('missing-implementation-owner')
            if not isinstance(binding.get('contract_type'),str) or not binding['contract_type'].strip():
                reasons.append('missing-parser-or-domain-type')
            candidate_sha256=binding.get('candidate_sha256')
            if not _sha256_text(candidate_sha256):
                reasons.append('missing-candidate-code-identity')
            fixtures=binding.get('fixtures',{})
            if not isinstance(fixtures,dict):
                reasons.append('invalid-fixture-map')
            else:
                for case in cases:
                    if not isinstance(fixtures.get(case),str) or not fixtures[case]:
                        reasons.append('missing-fixture-'+case)
        expected_source=obligation.get('authority_sha256')
        if not _sha256_text(expected_source):
            reasons.append('missing-frozen-reference-identity')
        supporting=receipts.get(ident,[])
        if not supporting:
            reasons.append('missing-verification-receipt')
        else:
            verified=[r for r in supporting if verify_trusted_receipt(r,expected_source,candidate_sha256,
                                                                       cases,trusted_verifier_key)]
            if not verified:
                reasons.append('no-authenticated-matching-receipt')
                if any(r.get('authority')=='trusted_runtime_receipt' for r in supporting):
                    reasons.append('reported-trust-receipt-needs-independent-authentication')
            if any(r.get('result')!='pass' for r in supporting):
                reasons.append('conflicting-or-failing-verification-receipt')
        dependencies=obligation.get('dependencies',[])
        if not isinstance(dependencies,list):
            raise ArtifactError('invalid obligation dependency list')
        for dep in dependencies:
            if dep not in ids or dep==ident:
                reasons.append('unresolved-or-self-dependency-'+str(dep)[:80])
        if needs_review:
            reasons.append('static-hypothesis-not-reviewed')
        if unknowns:
            reasons.append('source-coverage-has-unresolved-unknowns')
        status='unknown' if needs_review else ('blocked' if reasons else 'ready')
        results.append({'obligation_id':ident,'title':title,'required':required,'status':status,
                        'blockers':sorted(set(reasons)),'required_case_kinds':cases})
    required=[x for x in results if x['required']]
    readiness=('unknown' if not required else
               ('ready' if all(x['status']=='ready' for x in required) else 'incomplete'))
    return {'format':'reconstruction-obligation-ledger-1','readiness':readiness,
            'obligations':sorted(results,key=lambda x:x['obligation_id']),
            'required_count':len(required), 'closed_required_count':sum(x['status']=='ready' for x in required),
            'unresolved_unknown_count':len(unknowns or []),
            'evidence_ceiling':'Ready means signed matching finite tests only. HMAC does not prove independent execution or universal equivalence; assess signer and environment separately.'}


def _closure(graph:dict[str,set[str]]) -> dict[str,list[str]]:
    result={}
    for key in graph:
        visited=set();waiting=list(graph[key])
        while waiting:
            n=waiting.pop()
            if n==key:
                raise ArtifactError('cyclic happens-before relation')
            if n in visited:continue
            visited.add(n)
            waiting.extend(graph[n])
        result[key]=sorted(visited)
    return result


def _events(trace:dict) -> dict:
    events=trace.get('events')
    if not isinstance(events,list) or len(events)>750:
        raise ArtifactError('event trace must be bounded array')
    nodes={};deps={}
    for item in events:
        if not isinstance(item,dict):raise ArtifactError('invalid event record')
        event_id=_ensure_str(item.get('id'),'event id')
        if event_id in nodes:raise ArtifactError('duplicate event id')
        if not isinstance(item.get('before',[]),list):raise ArtifactError('invalid before relation')
        if len(item.get('before',[]))>64:
            raise ArtifactError('event predecessor count bound')
        deps[event_id]=set(item.get('before',[]))
        nodes[event_id]=item.get('payload',None)
    if any(ref not in nodes for values in deps.values() for ref in values):
        raise ArtifactError('dangling happens-before predecessor')
    return {'payloads':nodes,'order':_closure(deps)}


def compare_partial_order(reference:dict,candidate:dict) -> dict:
    """Compare event identity/payload and reachability, not arbitrary interleaving."""
    left=_events(reference);right=_events(candidate)
    issues=[]
    for group in ('payloads','order'):
        for event_id in sorted(set(left[group])|set(right[group])):
            if left[group].get(event_id,object())!=right[group].get(event_id,object()):
                issues.append({'kind':group,'event_id':event_id,
                               'reason':'missing-or-different'})
                if len(issues)>=100:break
        if len(issues)>=100:break
    return {'format':'partial-order-comparison-1','status':'finite-match' if not issues else 'mismatch',
            'differences':issues,'truncated':len(issues)>=100,
            'claim_ceiling':'Identified events and transitively ordered constraints match; does not prove unobserved concurrency.'}
