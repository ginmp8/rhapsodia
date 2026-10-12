#!/usr/bin/env python3
"""Offline OpenAPI/HAR contract extraction and explicit authorized HTTP replay.

No embedded URLs are fetched while inspecting. Replay uses an exact operator
allowlisted origin and a no-redirect client; no headers/bodies are logged by
default. Captures finite observable HTTP responses, not business equivalence.
"""
from __future__ import annotations
import argparse
from collections import Counter
import base64
import hashlib
import json
from pathlib import Path
import socket
import sys
from urllib.parse import urlsplit, urlencode, urlunsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.error import HTTPError, URLError
from behavior_lab import DataError, strict_json
from oracle_runner import json_lines
from json_writer import write_exclusive

MAX_CAPTURE=256*1024
MAX_CASES=200
VERBS={'GET','POST','PUT','PATCH','DELETE','HEAD','OPTIONS'}
DENIED_HEADERS={'authorization','cookie','proxy-authorization','x-api-key','set-cookie',
                'host','content-length','transfer-encoding','connection','proxy-connection',
                'forwarded','x-forwarded-host','x-forwarded-for','x-forwarded-proto',
                'upgrade','te','trailer','expect'}


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        return None


def inspect(path:Path,kind:str)->dict:
    if path.is_symlink() or not path.is_file() or path.stat().st_size>32*1024*1024:
        raise DataError('bounded regular JSON file required')
    obj=strict_json(path.read_text('utf-8'))
    if not isinstance(obj,dict):raise DataError('document must be object')
    operations=[]
    if kind=='openapi':
        if not isinstance(obj.get('paths'),dict):raise DataError('OpenAPI paths required')
        for route,verbs in sorted(obj['paths'].items()):
            if not isinstance(verbs,dict) or not isinstance(route,str):continue
            for verb,spec in sorted(verbs.items()):
                if verb.upper() not in VERBS or not isinstance(spec,dict):continue
                responses=spec.get('responses',{})
                operations.append({'method':verb.upper(),'path':route[:512],
                                   'declared_responses':sorted(str(k) for k in responses) if isinstance(responses,dict) else [],
                                   'evidence_level':'declared'})
    elif kind=='har':
        entries=obj.get('log',{}).get('entries',[])
        if not isinstance(entries,list):raise DataError('HAR entries required')
        counts=Counter()
        for record in entries[:10000]:
            if not isinstance(record,dict):continue
            req=record.get('request',{});resp=record.get('response',{})
            if not isinstance(req,dict) or not isinstance(resp,dict):continue
            url=urlsplit(str(req.get('url','')))
            method=str(req.get('method','')).upper()
            if method not in VERBS:continue
            counts[(method,url.path or '/',int(resp.get('status') or 0))]+=1
        operations=[{'method':m,'path':p[:512],'status':s,'count':count,'evidence_level':'recorded_har_metadata'}
                    for (m,p,s),count in sorted(counts.items())]
    else:raise DataError('kind must be har or openapi')
    return {'schema_version':'1.0','format':kind,'input_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'operations':operations[:10000],'truncated':len(operations)>10000,
            'redaction':'queries, headers, cookies and bodies omitted by design',
            'limitations':'declared or captured metadata, not live endpoint validation'}


def origin_url(base:str,*,allow_nonlocal:bool=False)->str:
    url=urlsplit(base)
    if (url.scheme not in ('http','https') or not url.hostname or url.username or url.password or
        url.path not in ('','/') or url.query or url.fragment):
        raise DataError('base must be an absolute bare http(s) origin without credentials')
    local=url.hostname.lower() in ('localhost','127.0.0.1','::1')
    if not local and not allow_nonlocal:
        raise DataError('nonlocal origin requires explicit --allow-nonlocal approval and isolated network policy')
    return f'{url.scheme}://{url.netloc}'


def request_parts(value:dict,base:str)->tuple[str,str,bytes|None,dict]:
    method=value.get('method')
    path=value.get('path')
    if method not in VERBS or not isinstance(path,str) or not path.startswith('/') or path.startswith('//') or '\\' in path or '?' in path or '#' in path or any(ord(c)<32 for c in path):
        raise DataError('request needs valid method and relative absolute-path without query/fragment')
    if any(s in ('.','..') for s in path.split('/')):raise DataError('dot segments forbidden')
    q=value.get('query',{})
    if not isinstance(q,dict) or any(not isinstance(k,str) or isinstance(v,(dict,list)) for k,v in q.items()):
        raise DataError('query must be shallow primitive dictionary')
    query=urlencode(sorted(q.items()),doseq=False)
    url=base+path+('?' + query if query else '')
    h=value.get('headers',{})
    if not isinstance(h,dict) or any(not isinstance(k,str) or not isinstance(v,str) or k.lower() in DENIED_HEADERS or not k.isascii() or any(c not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-' for c in k) or '\r' in v or '\n' in v for k,v in h.items()):
        raise DataError('unsafe/credential-bearing request header refused')
    if 'json' in value and 'body_base64' in value:raise DataError('ambiguous HTTP request body')
    if 'json' in value:
        body=json.dumps(value['json'],ensure_ascii=False,separators=(',',':'),allow_nan=False).encode('utf-8')
        h={**h,'Content-Type':'application/json'}
    elif 'body_base64' in value:
        encoded=value['body_base64']
        if not isinstance(encoded,str):raise DataError('body_base64 must be string')
        body=base64.b64decode(encoded,validate=True)
    else:body=None
    if body is not None and len(body)>MAX_CAPTURE:raise DataError('request body budget exceeded')
    return method,url,body,h


def replay(cases:Path,origin:str,*,authorized:bool=False,allow_nonlocal:bool=False,
           include_json_body:bool=False,timeout:float=3.0)->dict:
    if not authorized:raise DataError('HTTP replay requires explicit network authorization')
    if not 0.1<=timeout<=15:raise DataError('HTTP timeout budget exceeded')
    base=origin_url(origin,allow_nonlocal=allow_nonlocal)
    opener=build_opener(NoRedirect())
    rows=[]
    for case in json_lines(cases,MAX_CASES):
        value=case['input']
        if not isinstance(value,dict):raise DataError('HTTP case input must be object')
        method,url,body,headers=request_parts(value,base)
        # URL cannot redirect through this client. DNS rebinding/network routes remain the host's concern.
        req=Request(url,data=body,headers=headers,method=method)
        try:
            try:
                response=opener.open(req,timeout=timeout)
            except HTTPError as e:
                response=e   # 4xx/5xx are valid response observations.
            with response:
                payload=response.read(MAX_CAPTURE+1)
                code=response.status
                content_type=response.headers.get('Content-Type','').split(';',1)[0]
            if len(payload)>MAX_CAPTURE:
                rows.append({'id':case['id'],'kind':'http-replay','schema_version':'2.0','input':value,
                             'observation':{'error':{'kind':'response-too-large'}},'runner_status':'invalid-output'})
                continue
            output={'http_status':int(code),'body_sha256':hashlib.sha256(payload).hexdigest(),
                    'body_size':len(payload),'content_type':content_type[:100]}
            if include_json_body and 'json' in content_type:
                try:
                    output['json']=strict_json(payload.decode('utf-8'))
                except (ValueError,UnicodeDecodeError):
                    output['json_parse']='invalid'
            obs={'output':output,'effects':[{'kind':'http','operation':method,'route':value['path'],
                                             'status':int(code),'capture':'client-observed-request'}]}
            status='ok'
        except (URLError,OSError,socket.timeout,TimeoutError) as exc:
            obs={'error':{'kind':'network-failure','class':type(exc).__name__}}
            status='error'
        rows.append({'id':case['id'],'kind':'http-replay','schema_version':'2.0','input':value,
                     'observation':obs,'runner_status':status})
    return {'schema_version':'1.0','origin':base,'cases':rows,'completed':sum(r['runner_status']=='ok' for r in rows),
            'warning':'Live network observations of an operator-approved origin. No server-side effects observed; no OS isolation.'}


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode',choices=['inspect-har','inspect-openapi','replay'])
    p.add_argument('--input',type=Path)
    p.add_argument('--cases',type=Path)
    p.add_argument('--origin')
    p.add_argument('--execute-authorized',action='store_true')
    p.add_argument('--allow-nonlocal',action='store_true')
    p.add_argument('--capture-json',action='store_true')
    p.add_argument('-o','--output',required=True,type=Path)
    a=p.parse_args(argv)
    try:
        if a.mode.startswith('inspect'):
            if not a.input:raise DataError('--input required')
            result=inspect(a.input,a.mode.removeprefix('inspect-'))
            payload=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
        else:
            if not a.cases or not a.origin:raise DataError('--cases/--origin required')
            result=replay(a.cases,a.origin,authorized=a.execute_authorized,
                          allow_nonlocal=a.allow_nonlocal,include_json_body=a.capture_json)
            payload=''.join(json.dumps(v,ensure_ascii=False,sort_keys=True)+'\n' for v in result['cases'])
        protected=[v for v in (a.input,a.cases) if v]
        if any(a.output.resolve()==v.resolve() for v in protected):raise DataError('output aliases input')
        write_exclusive(a.output,payload,protected)
        print(json.dumps({'mode':a.mode,'output':str(a.output),'records':len(result.get('cases',result.get('operations',[])))},ensure_ascii=False))
        return 0
    except (OSError,ValueError) as exc:
        print(json.dumps({'error':str(exc)}),file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
