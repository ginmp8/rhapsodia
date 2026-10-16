#!/usr/bin/env python3
"""Relate captured browser request metadata to declared API route shapes.

Produces lexical/inferred candidates, never execution proof for backend methods.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

from behavior_lab import DataError,strict_json
from json_writer import write_exclusive


def load(path):
    if path.is_symlink() or not path.is_file() or path.stat().st_size>16*1024*1024:
        raise DataError('bounded regular evidence JSON file required')
    raw=path.read_bytes()
    result=strict_json(raw.decode('utf-8'))
    if not isinstance(result,dict):
        raise DataError('evidence must be JSON object')
    return result,hashlib.sha256(raw).hexdigest()


def route_matches(observed:str,declared:str)->bool:
    if not isinstance(observed,str) or not isinstance(declared,str):
        return False
    if len(observed)>512 or len(declared)>512 or not declared.startswith('/') or not observed.startswith('/'):
        return False
    # Match strictly one segment for a declared URI-template {parameter}.
    parts=declared.split('/')
    regex='^'+'/'.join('[^/]+' if re.fullmatch(r'\{[a-zA-Z_][a-zA-Z0-9_]*\}',x) else re.escape(x) for x in parts)+'$'
    return bool(re.fullmatch(regex,observed))


def correlate(trace,contract,ts='',cs=''):
    if trace.get('mode')!='web-investigation':
        raise DataError('expected web investigation result')
    operations=contract.get('operations',[])
    if not isinstance(operations,list) or len(operations)>10000:
        raise DataError('contracts must have bounded operations array')
    requests=[(i,item) for i,item in enumerate(trace.get('events',[])) if isinstance(item,dict) and item.get('kind')=='request' and item.get('observed') is True]
    matches=[];unmatched=[]
    for i,req in requests[:1500]:
        found=[]
        for j,op in enumerate(operations):
            if not isinstance(op,dict):continue
            if str(op.get('method','')).upper()==req.get('method') and route_matches(req.get('path',''),op.get('path','')):
                found.append({'event_index':i,'operation_index':j,'method':req['method'],
                              'observed_path':req['path'],'declared_route':op['path'],
                              'level':'inferred','reason':'method and route shape match; no backend execution proof'})
        if found:matches.extend(found[:20])
        else:unmatched.append({'event_index':i,'method':req.get('method'),
                               'path':req.get('path')})
    return {'schema_version':'1.0','mode':'web-route-correlation','trace_sha256':ts,
            'contract_sha256':cs,'matches':matches[:5000],'unmatched_requests':unmatched[:1500],
            'unmatched_truncated':len(unmatched)>1500,'matches_truncated':len(matches)>5000,
            'evidence_level':'inferred',
            'limitations':'Shape/capture association is not proof a server handler ran; fixture network requests are excluded.'}


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--trace',required=True,type=Path)
    p.add_argument('--contracts',required=True,type=Path)
    p.add_argument('-o','--output',required=True,type=Path)
    a=p.parse_args(argv)
    try:
        if a.trace.resolve()==a.contracts.resolve():raise DataError('trace/contracts must be independent')
        t,ts=load(a.trace);c,cs=load(a.contracts)
        result=correlate(t,c,ts,cs)
        write_exclusive(a.output,json.dumps(result,sort_keys=True,indent=2)+'\n',[a.trace,a.contracts])
        return 0
    except (OSError,ValueError) as exc:
        print(json.dumps({'error':str(exc)}),file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
