"""Pure advisory policies. The supervisor remains the sole orchestration owner."""
from __future__ import annotations
import math
from .common import RuntimeFault, fields, number, safe_text


def _time(value):
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or value<0:
        raise RuntimeFault('INVALID_INPUT','Estimates must be finite non-negative numbers.')
    return value


def decide(request: dict) -> dict:
    fields(request,{'units'},{'host_parallel','spawn_ms','synthesis_ms','max_parallel','required_verifier','remaining_delegations','token_budget','estimated_tokens'})
    for flag in ('host_parallel','required_verifier'):
        if flag in request and type(request[flag]) is not bool:
            raise RuntimeFault('INVALID_INPUT','Host and gate flags must be boolean.')
    units=request['units']
    if not isinstance(units,list) or not 1<=len(units)<=4:
        raise RuntimeFault('INVALID_INPUT','Use 1..4 bounded work units per phase.')
    for unit in units:
        fields(unit,{'id','effect'},{'estimated_ms','independent','depends_on','owner'})
        safe_text(unit['id'],96)
        if 'owner' in unit:safe_text(unit['owner'],96)
        if 'independent' in unit and type(unit['independent']) is not bool:
            raise RuntimeFault('INVALID_INPUT','Independence must be explicitly boolean.')
        if 'depends_on' in unit:
            if not isinstance(unit['depends_on'],list) or len(unit['depends_on'])>4:
                raise RuntimeFault('INVALID_INPUT','Dependencies must be a bounded array.')
            for dependency in unit['depends_on']:safe_text(dependency,96)
        if 'estimated_ms' in unit:_time(unit['estimated_ms'])
        if not isinstance(unit['effect'],str) or unit['effect'] not in {'read','write','verify'}:
            raise RuntimeFault('INVALID_INPUT','Unknown work-unit effect.')
    if len({u['id'] for u in units})!=len(units):
        raise RuntimeFault('INVALID_INPUT','Work-unit IDs must be unique.')
    limit=number(request.get('max_parallel',4),1,4)
    remaining=number(request.get('remaining_delegations',24),0,24)
    result={'schema':'delegation-advice/v1','strategy':'single' if len(units)==1 else 'sequential',
            'max_parallel':1,'required_verifier':request.get('required_verifier',False),'advisory_only':True,
            'execution_authority':False,'reason':'default-single-canonical-worker'}
    if len(units)>remaining:
        return dict(result,strategy='blocked',reason='delegation-budget-exhausted')
    if len(units)==1:return result
    if any(u['effect']!='read' for u in units):
        return dict(result,reason='canonical-writer-or-verifier-must-remain-ordered')
    if not request.get('host_parallel') or limit<len(units):
        return dict(result,reason='host-or-parallel-budget-unavailable')
    if any('owner' not in u for u in units):
        return dict(result,reason='owner-not-established')
    if len({u.get('owner') for u in units})>1:
        return dict(result,reason='cross-owner-work-must-not-fanout')
    if any(u.get('independent') is not True or u.get('depends_on') for u in units):
        return dict(result,reason='independence-not-established')
    if any('estimated_ms' not in u for u in units) or 'spawn_ms' not in request or 'synthesis_ms' not in request:
        return dict(result,reason='cost-estimates-unavailable')
    durations=[_time(u['estimated_ms']) for u in units]
    serial=sum(durations)
    parallel=max(durations)+_time(request['spawn_ms'])*len(units)+_time(request['synthesis_ms'])
    if 'token_budget' in request:
        budget=number(request['token_budget'],0,10**9)
        if 'estimated_tokens' not in request or number(request['estimated_tokens'],0,10**9)>budget:
            return dict(result,reason='token-budget-unproven-or-exceeded')
    if serial<=0 or parallel>serial*0.9:
        return dict(result,reason='estimated-overhead-not-amortized',estimated_serial_ms=serial,estimated_parallel_ms=parallel)
    return dict(result,strategy='read-only-fanout',max_parallel=len(units),reason='independent-read-work-with-estimated-benefit',
                estimated_serial_ms=serial,estimated_parallel_ms=parallel)


def retrieval(request: dict) -> dict:
    fields(request,{'has_exact_refs','relationship_question','repeated_query','graph_available'})
    if any(type(v) is not bool for v in request.values()):
        raise RuntimeFault('INVALID_INPUT','Retrieval signals must be booleans.')
    strategy='exact-refs' if request['has_exact_refs'] else 'bounded-text-or-symbol-search'
    if not request['has_exact_refs'] and all(request[k] for k in ('relationship_question','repeated_query','graph_available')):
        strategy='budgeted-local-graph'
    return {'strategy':strategy,'full_graph_required':False,'advisory_only':True,'fallback':'bounded-text-or-symbol-search'}
