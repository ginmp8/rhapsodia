#!/usr/bin/env python3
"""Deterministic, bounded structure-aware fuzz/probe *inputs*, never predicted outputs.

Uses supplied corpus and optionally prior differential findings to prioritize new
queries. Emitted rows have no observation and must be executed against a trusted
reference before they can be treated as characterization evidence.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import random
import sys
from pathlib import Path
from typing import Any, Iterator
from behavior_lab import DataError, load_corpus, strict_json
from json_writer import write_exclusive


def canonical(v: Any) -> str:
    return json.dumps(v, sort_keys=True, ensure_ascii=False, allow_nan=False, separators=(',', ':'))


def mutations(v: Any, depth: int = 0) -> Iterator[tuple[Any, str]]:
    if depth > 3:
        return
    if isinstance(v, bool):
        yield not v, 'flip-bool'
    elif isinstance(v, (float, int)):
        for n in (0, 1, -1, 2**31-1, 2**31, 2**53, -2**53):
            if v != n:
                yield n, 'numeric-boundary'
    elif isinstance(v, str):
        for s in ('', ' ', '\u0000', '\n', 'é', '\u200d', v + ' ', v * 2 if len(v) < 512 else v[:128]):
            if s != v:
                yield s, 'text-boundary'
    elif isinstance(v, dict):
        for key in sorted(v):
            removed = dict(v)
            del removed[key]
            yield removed, 'missing-key'
            for child, reason in list(mutations(v[key], depth+1))[:12]:
                replaced = dict(v)
                replaced[key] = child
                yield replaced, f'{key}:{reason}'
        yield {}, 'empty-object'
    elif isinstance(v, list):
        yield [], 'empty-list'
        if v:
            yield list(reversed(v)), 'list-reversal'
            yield v + [v[-1]], 'duplicate-last'
            for i in range(min(len(v), 5)):
                yield v[:i] + v[i+1:], 'remove-item'
                for child, reason in list(mutations(v[i], depth+1))[:8]:
                    replaced = list(v)
                    replaced[i] = child
                    yield replaced, f'item{i}:{reason}'
    elif v is None:
        for x in (False, 0, '', [], {}):
            yield x, 'null-boundary'


def boundary_inputs(source: Any) -> Iterator[tuple[Any, str]]:
    yield from mutations(source)
    if isinstance(source, dict) and isinstance(source.get('actions'), list):
        seq = source['actions']
        if seq:
            yield {**source, 'actions': seq + [seq[-1]]}, 'retry-last-action'
            yield {**source, 'actions': seq * 2}, 'repeat-sequence'
            yield {**source, 'actions': seq[:-1]}, 'drop-terminal-action'


def openapi_seeds(path: Path) -> list[tuple[str, Any]]:
    obj = strict_json(path.read_text('utf-8'))
    if not isinstance(obj, dict) or not isinstance(obj.get('paths'), dict):
        raise DataError('OpenAPI JSON must contain paths object')
    rows=[]
    for route, methods in sorted(obj['paths'].items()):
        if not isinstance(route, str) or not route.startswith('/') or len(route) > 512 or not isinstance(methods, dict):
            continue
        for method in sorted(methods):
            if method.lower() in ('get','post','put','patch','delete','head','options'):
                rows.append((f'openapi:{method.upper()}:{route}', {'method': method.upper(), 'path': route,
                             'query': {}, 'headers': {}, 'body': None}))
            if len(rows) >= 300:
                return rows
    return rows


def generate(reference: Path | None, comparison: Path | None = None, openapi: Path | None = None,
             *, max_cases: int = 100, seed: int = 0, fuzz: bool = False, coverage: Path | None = None) -> dict:
    if not 1 <= max_cases <= 1000:
        raise DataError('max_cases out of bounds (1..1000)')
    if not any((reference, openapi)):
        raise DataError('reference corpus or OpenAPI JSON required')
    rng=random.Random(seed)
    bases: list[tuple[str, Any]]=[]
    observed=set()
    if reference:
        rows=load_corpus(reference)
        for k,r in sorted(rows.items()):
            bases.append((k,r['input']))
            observed.add(canonical(r['input']))
    if openapi:
        bases.extend(openapi_seeds(openapi))
    rare_priority={}
    if coverage:
        coverage_obj=strict_json(coverage.read_text('utf-8'))
        if not isinstance(coverage_obj,dict) or not isinstance(coverage_obj.get('by_case'),dict):
            raise DataError('coverage JSON needs by_case dictionary: id -> observed identifiers')
        appearances={}
        for entries in coverage_obj['by_case'].values():
            if not isinstance(entries,list) or any(not isinstance(e,str) or len(e)>512 for e in entries):
                raise DataError('coverage entries must be lists of bounded strings')
            for item in set(entries):appearances[item]=appearances.get(item,0)+1
        for name,entries in coverage_obj['by_case'].items():
            rare_priority[name]=sum(1.0/appearances[e] for e in set(entries))
        bases.sort(key=lambda pair:(-rare_priority.get(pair[0],0),pair[0]))
    if comparison:
        report=strict_json(comparison.read_text('utf-8'))
        if not isinstance(report,dict) or not isinstance(report.get('findings'),list):
            raise DataError('comparison must contain findings array')
        important={str(f.get('id')) for f in report['findings'] if isinstance(f,dict) and f.get('class')=='differential_mismatch'}
        bases.sort(key=lambda item:(item[0] not in important,-rare_priority.get(item[0],0),item[0]))
    emitted=[];seen=set(observed)
    for name, base in bases:
        plans=list(boundary_inputs(base))
        if fuzz:
            # Repeat the structure-aware mutator under a local deterministic seed;
            # never invent expected outputs or treat random inputs as domain-valid.
            rng.shuffle(plans)
            for candidate,_ in plans[:min(16,len(plans))]:
                plans.extend(list(boundary_inputs(candidate))[:6])
        for candidate,reason in plans:
            if len(emitted)>=max_cases:break
            key=canonical(candidate)
            if key in seen or len(key)>128*1024:continue
            seen.add(key)
            emitted.append({'id': 'probe-' + hashlib.sha256(key.encode('utf-8')).hexdigest()[:16],
                            'kind':'fuzz-hypothesis' if fuzz else 'probe-hypothesis',
                            'input':candidate, 'based_on':name, 'reason':reason,
                            'status':'unobserved'})
        if len(emitted)>=max_cases:break
    return {'schema_version':'1.0', 'mode':'fuzz' if fuzz else 'adaptive-probes',
            'seed':seed, 'reference_sha256':hashlib.sha256(reference.read_bytes()).hexdigest() if reference else None,
            'comparison_sha256':hashlib.sha256(comparison.read_bytes()).hexdigest() if comparison else None,
            'coverage_sha256':hashlib.sha256(coverage.read_bytes()).hexdigest() if coverage else None,
            'cases':emitted,'case_count':len(emitted),'oracle':'none',
            'warning':'Inputs are unobserved hypotheses, not golden-master output. Validate against a trusted reference.'}


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode',choices=['generate','fuzz'])
    p.add_argument('--reference',type=Path)
    p.add_argument('--comparison',type=Path)
    p.add_argument('--openapi',type=Path)
    p.add_argument('--coverage',type=Path,help='External observed coverage: by_case id->edge identifiers; guidance only')
    p.add_argument('--seed',type=int,default=0)
    p.add_argument('--max-cases',type=int,default=100)
    p.add_argument('-o','--output',required=True,type=Path)
    a=p.parse_args(argv)
    try:
        result=generate(a.reference,a.comparison,a.openapi,max_cases=a.max_cases,seed=a.seed,fuzz=a.mode=='fuzz',coverage=a.coverage)
        if a.output.resolve() in {p.resolve() for p in (a.reference,a.comparison,a.openapi,a.coverage) if p}:
            raise DataError('output aliases input')
        # NDJSON can directly feed trusted oracle_runner; report goes to stdout.
        payload=''.join(canonical(row)+'\n' for row in result['cases'])
        write_exclusive(a.output,payload,[p for p in (a.reference,a.comparison,a.openapi,a.coverage) if p])
        print(json.dumps({k:v for k,v in result.items() if k!='cases'},ensure_ascii=False))
        return 0
    except (DataError, OSError, ValueError) as exc:
        print(json.dumps({'error':str(exc)},ensure_ascii=False),file=sys.stderr)
        return 2

if __name__=='__main__':raise SystemExit(main())
