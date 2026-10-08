"""Allowlisted, content-free usage events and strict paired comparisons."""
from __future__ import annotations
import math
import statistics
from .common import HASH_RE, RuntimeFault, fields, number, safe_text, sha


def _count(value):
    return None if value is None else number(value,0,10**12)


def normalize_usage(provider: str, usage: dict) -> dict:
    if not isinstance(usage,dict):raise RuntimeFault('INVALID_INPUT','Usage must be a structured object.')
    if usage.get('schema') == 'normalized-usage/v1':
        fields(usage, {'schema','input_tokens','output_tokens','cache_read_tokens','cache_write_tokens',
                       'uncached_input_tokens','billed_tokens','source'})
        for key in ('input_tokens','output_tokens','cache_read_tokens','cache_write_tokens','uncached_input_tokens'):
            _count(usage[key])
        if usage['billed_tokens'] is not None or usage['source'] not in ('provider-reported','unavailable'):
            raise RuntimeFault('INVALID_INPUT','Unsupported normalized usage metadata.')
        if usage['input_tokens'] is not None and usage['cache_read_tokens'] is not None and usage['cache_read_tokens'] > usage['input_tokens']:
            raise RuntimeFault('INVALID_INPUT','Cached input cannot exceed inclusive input.')
        if usage['source'] == 'unavailable' and any(usage[k] is not None for k in ('input_tokens','output_tokens','cache_read_tokens','cache_write_tokens','uncached_input_tokens')):
            raise RuntimeFault('INVALID_INPUT','Unavailable usage cannot contain observed counters.')
        if provider not in ('openai','anthropic','generic'):
            raise RuntimeFault('INVALID_INPUT','Unsupported usage profile.')
        return dict(usage)
    if provider=='openai':
        inp=_count(usage.get('input_tokens',usage.get('prompt_tokens')))
        out=_count(usage.get('output_tokens',usage.get('completion_tokens')))
        details=usage.get('input_tokens_details',usage.get('prompt_tokens_details',{}))
        if not isinstance(details,dict):raise RuntimeFault('INVALID_INPUT','Usage details must be an object.')
        read=_count(details.get('cached_tokens'));write=_count(usage.get('cache_write_tokens'))
        if inp is not None and read is not None and read>inp:
            raise RuntimeFault('INVALID_INPUT','Cached input cannot exceed total input.')
        uncached=None if inp is None or read is None else inp-read
    elif provider=='anthropic':
        uncached=_count(usage.get('input_tokens'));out=_count(usage.get('output_tokens'))
        read=_count(usage.get('cache_read_input_tokens'));write=_count(usage.get('cache_creation_input_tokens'))
        inp=sum([uncached,read,write]) if all(v is not None for v in (uncached,read,write)) else None
    elif provider=='generic':
        inp=_count(usage.get('input_tokens'));out=_count(usage.get('output_tokens'))
        read=_count(usage.get('cache_read_tokens'));write=_count(usage.get('cache_write_tokens'));uncached=None
        if inp is not None and read is not None and read>inp:raise RuntimeFault('INVALID_INPUT','Cached input exceeds total.')
    else:raise RuntimeFault('INVALID_INPUT','Supported usage profiles: generic, openai, anthropic.')
    return {'schema':'normalized-usage/v1','input_tokens':inp,'output_tokens':out,'cache_read_tokens':read,'cache_write_tokens':write,'uncached_input_tokens':uncached,
            'billed_tokens':None,'source':'provider-reported' if usage else 'unavailable'}

IDENTITY=('scenario_id','host','model','config_digest','input_digest','evaluator_digest','cache_state','sample','phase')
REQUIRED=set(IDENTITY)|{'run_id','event_id','arm','duration_ms','quality_pass','provider','usage'}


def event(request: dict) -> dict:
    fields(request,REQUIRED,{'context_bytes','tool_calls','agent_spawns','cache_hit','ttft_ms','cost_usd'})
    for k in set(IDENTITY)-{'sample'} | {'run_id','event_id'}:safe_text(request[k],256)
    for key in ('config_digest','input_digest','evaluator_digest'):
        if not HASH_RE.fullmatch(request[key]):
            raise RuntimeFault('INVALID_INPUT','Comparison identities must be SHA-256 values.')
    number(request['sample'],0,10**6)
    if request['arm'] not in ('baseline','candidate') or request['cache_state'] not in {'cold','warm','unspecified'}:
        raise RuntimeFault('INVALID_INPUT','Invalid experiment arm/cache state.')
    if type(request['quality_pass']) is not bool:raise RuntimeFault('INVALID_INPUT','quality_pass must be an observed boolean.')
    result={k:request[k] for k in REQUIRED if k!='usage'}
    result['usage']=normalize_usage(request['provider'],request['usage'])
    for k in ('duration_ms','ttft_ms','cost_usd'):
        value=request.get(k)
        if value is not None and (isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or value<0):
            raise RuntimeFault('INVALID_INPUT','Timings/cost must be finite non-negative measurements or null.')
        result[k]=value
    for k in ('context_bytes','tool_calls','agent_spawns'):result[k]=_count(request.get(k))
    if request.get('cache_hit') is not None and type(request['cache_hit']) is not bool:raise RuntimeFault('INVALID_INPUT','cache_hit must be boolean or null.')
    result['cache_hit']=request.get('cache_hit')
    return result


def record(cache, request: dict) -> dict:
    value=event(request)
    # Content-addressed records deduplicate identical events; comparison rejects ID conflicts.
    key=cache.put('metric',value)
    return {'status':'recorded','id':key,'raw_prompts_stored':False,'raw_tool_output_stored':False}


def percentile(values: list[float], p: float):
    if not values:return None
    values=sorted(values);position=(len(values)-1)*p;lo=int(position);hi=min(lo+1,len(values)-1)
    return values[lo]+(values[hi]-values[lo])*(position-lo)


def compare(request: dict) -> dict:
    fields(request,{'baseline','candidate'})
    maps=[]
    for arm in ('baseline','candidate'):
        rows=request[arm]
        if not isinstance(rows,list) or not 1<=len(rows)<=4096:
            raise RuntimeFault('INVALID_INPUT','Each arm needs 1..4096 measured rows.')
        mapped={}
        event_ids=set()
        for raw in rows:
            row=event(raw)
            if row['arm']!=arm:raise RuntimeFault('CONFOUNDED','Experiment arm mismatch.')
            key=tuple(row[k] for k in IDENTITY)
            if key in mapped or (row['run_id'],row['event_id']) in event_ids:
                raise RuntimeFault('CONFOUNDED','Duplicate pair identity or event ID.')
            mapped[key]=row;event_ids.add((row['run_id'],row['event_id']))
        maps.append(mapped)
    if maps[0].keys()!=maps[1].keys():
        raise RuntimeFault('CONFOUNDED','Paired scenario, host, model, configuration, input, evaluator and cache-state identities must match.')
    delta=[];before=[];after=[]
    for key in maps[0]:
        b,c=maps[0][key],maps[1][key]
        if b['duration_ms'] is not None and c['duration_ms'] is not None:
            delta.append(c['duration_ms']-b['duration_ms']);before.append(b['duration_ms']);after.append(c['duration_ms'])
    quality=all(r['quality_pass'] for m in maps for r in m.values())
    totals={}
    for metric in ('input_tokens','output_tokens','cache_read_tokens','cache_write_tokens'):
        values=[[r['usage'][metric] for r in m.values()] for m in maps]
        totals[metric]={'baseline':sum(values[0]) if all(v is not None for v in values[0]) else None,
                        'candidate':sum(values[1]) if all(v is not None for v in values[1]) else None}
    complete = len(delta) == len(maps[0]) and len(delta) >= 2
    strata = {tuple(r[k] for k in ('host','model','config_digest','evaluator_digest','cache_state','phase')) for m in maps for r in m.values()}
    latency_win = complete and sum(delta) < 0 and percentile(after,.95) <= percentile(before,.95)
    measured = totals['input_tokens']
    token_win = measured['baseline'] is not None and measured['candidate'] is not None and measured['candidate'] < measured['baseline']
    return {'schema':'paired-efficiency/v1','pairs':len(maps[0]),'timed_pairs':len(delta),'quality_gate':quality,
            'mean_delta_ms':statistics.mean(delta) if delta else None,
            'baseline_p50_ms':percentile(before,.5),'candidate_p50_ms':percentile(after,.5),
            'baseline_p95_ms':percentile(before,.95),'candidate_p95_ms':percentile(after,.95),
            'usage':totals,'measured_improvement_claim_allowed':quality and complete and len(strata)==1 and latency_win and token_win,
            'latency_improved_in_sample':latency_win,'input_tokens_reduced_in_sample':token_win,'comparable_strata':len(strata),
            'confidence_interval_ms':None,'causal_or_population_claim_allowed':False,
            'notice':'Descriptive paired measurements only; sample coverage and uncertainty must accompany any causal or production claim.'}


def summary(cache, request: dict) -> dict:
    fields(request,set(),{'run_id'})
    rows=[cache.get('metric',key) for key in cache.keys('metric')]
    if 'run_id' in request:rows=[r for r in rows if r['run_id']==request['run_id']]
    ids=set()
    for row in rows:
        identity=(row['run_id'],row['event_id'])
        if identity in ids:raise RuntimeFault('EVENT_CONFLICT','Conflicting versions of one event exist; resolve them before reporting.')
        ids.add(identity)
    totals={}
    for key in ('input_tokens','output_tokens','cache_read_tokens','cache_write_tokens'):
        values=[r['usage'][key] for r in rows]
        totals[key]=sum(values) if values and all(v is not None for v in values) else None
    durations=[r['duration_ms'] for r in rows if r['duration_ms'] is not None]
    return {'schema':'efficiency-summary/v1','events':len(rows),'usage':totals,'event_p50_ms':percentile(durations,.5),
            'event_p95_ms':percentile(durations,.95),'all_quality_gates_pass':all(r['quality_pass'] for r in rows) if rows else None,
            'wall_clock_total_ms':None,'notice':'Overlapping event durations are not added as end-to-end wall time. No raw prompts or logs collected.'}
