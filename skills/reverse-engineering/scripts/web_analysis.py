#!/usr/bin/env python3
"""Offline JavaScript, Electron, source-map, HAR and OpenAPI evidence extraction.

Static artifacts only: no JS evaluation, network access, browser automation or
secret/value capture. Lexical JS edges are candidates, not resolved AST imports.
"""
from __future__ import annotations
import argparse
import base64
import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from json_writer import write_exclusive
from urllib.parse import urlsplit, parse_qsl

MAX_INPUT=32*1024*1024
MAX_FILES=4000
MAX_LINES=150000
MAX_POINTS=200000
MAX_NETWORK=10000
B64='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'

class WebError(ValueError):pass


def bounded(path:Path, max_bytes=MAX_INPUT)->bytes:
    if not path.is_file() or path.is_symlink():raise WebError('expected a regular non-symlink file')
    if path.stat().st_size>max_bytes:raise WebError('input byte budget exceeded')
    return path.read_bytes()


def vlq_decode(text:str,index:int)->tuple[int,int]:
    value=0; shift=0
    while index<len(text) and shift<=35:
        char=text[index];index+=1
        if char not in B64:raise WebError(f'invalid VLQ base64 character {char!r}')
        n=B64.index(char)
        value|=(n&31)<<shift
        shift+=5
        if n&32==0:
            result=-(value>>1) if value&1 else value>>1
            return result,index
    raise WebError('overlong or truncated VLQ')


def map_segments(obj:dict):
    if obj.get('version')!=3:raise WebError('only Source Map v3 supported')
    if not isinstance(obj.get('sources'),list) or not isinstance(obj.get('mappings'),str):
        raise WebError('invalid source map format')
    sources=obj['sources'];names=obj.get('names',[])
    if not isinstance(names,list):raise WebError('invalid names field')
    line=0;source=0;original_line=0;original_col=0;name_index=0
    result=[]
    for encoded_line in obj['mappings'].split(';'):
        col=0
        for part in encoded_line.split(','):
            if not part:continue
            fields=[];i=0
            while i<len(part):
                v,i=vlq_decode(part,i);fields.append(v)
            if len(fields) not in (1,4,5):raise WebError(f'invalid mapping segment with {len(fields)} fields')
            col+=fields[0]
            if col<0:raise WebError('negative generated column')
            record={'generated_line':line+1,'generated_column':col}
            if len(fields)>1:
                source+=fields[1];original_line+=fields[2];original_col+=fields[3]
                if not 0<=source<len(sources) or original_line<0 or original_col<0:
                    raise WebError('source map segment indexes invalid')
                record.update({'source_index':source, 'original_line':original_line+1,
                               'original_column':original_col,'source':str(sources[source])[:4096]})
                if len(fields)>4:
                    name_index+=fields[4]
                    if not 0<=name_index<len(names):raise WebError('name source map index invalid')
                    record['name']=str(names[name_index])[:512]
            result.append(record)
            if len(result)>MAX_POINTS:raise WebError('source map point budget exceeded')
        line+=1
    return result


def load_map(path:Path):
    content=bounded(path).decode('utf-8-sig','strict')
    if path.suffix=='.map' or content.lstrip().startswith('{'):
        obj=json.loads(content)
        if 'version' in obj and 'mappings' in obj:return obj
    matches=list(re.finditer(r'(?m)^\s*(?://|/\*)[#@]\s*sourceMappingURL\s*=\s*(\S+)',content))
    if not matches:raise WebError('no embedded source map; supply .map explicitly')
    url=matches[-1].group(1).rstrip('*/')
    if not url.startswith('data:'):raise WebError('external sourceMappingURL is not loaded automatically')
    if ';base64,' not in url:raise WebError('only base64 inline source maps supported')
    raw=base64.b64decode(url.split(';base64,',1)[1], validate=True)
    if len(raw)>MAX_INPUT:raise WebError('inline map budget exceeded')
    return json.loads(raw)


def analyze_sourcemap(path:Path, query_line=None, query_col=0):
    obj=load_map(path)
    points=map_segments(obj)
    embedded=obj.get('sourcesContent',[])
    contents=[]
    for i,s in enumerate(obj['sources']):
        value=embedded[i] if isinstance(embedded,list) and i<len(embedded) else None
        contents.append({'source':str(s)[:4096], 'embedded':isinstance(value,str),
                         'sha256':hashlib.sha256(value.encode('utf-8')).hexdigest() if isinstance(value,str) else None})
    outcome={'format':'source-map-v3','generated_file':obj.get('file'),
             'source_root':obj.get('sourceRoot',''), 'sources':contents,
             'segments':len(points), 'mapped_segments':sum('source' in p for p in points),
             'sha256':hashlib.sha256(bounded(path)).hexdigest(),
             'evidence_level':'source-map line/column declarations, not proof source was shipped or executed'}
    if query_line is not None:
        matched=[p for p in points if p['generated_line']==query_line and p['generated_column']<=query_col]
        outcome['lookup']={'line':query_line,'column':query_col,'closest_segment':max(matched,key=lambda x:x['generated_column']) if matched else None}
    return outcome

JS_PATTERNS={
  'esm_import':re.compile(r'\bimport\s+(?:[\w*{},\s]+?\s+from\s+)?[\'\"]([^\'\"]{1,300})[\'\"]'),
  'esm_export_from':re.compile(r'\bexport\s+[^;\n]*?\bfrom\s+[\'\"]([^\'\"]{1,300})[\'\"]'),
  'require':re.compile(r'\brequire\s*\(\s*[\'\"]([^\'\"]{1,300})[\'\"]\s*\)'),
  'dynamic_import':re.compile(r'\bimport\s*\(\s*[\'\"]([^\'\"]{1,300})[\'\"]\s*\)'),
  'electron_ipc_send':re.compile(r'\b(?:ipcRenderer|ipcMain)\.(?:send|invoke|on|handle|once)\s*\(\s*[\'\"]([^\'\"]{1,150})[\'\"]'),
  'express_route':re.compile(r'\b(?:app|router)\.(get|post|put|delete|patch|options|head)\s*\(\s*[\'\"]([^\'\"]{1,300})[\'\"]'),
  'event_listener':re.compile(r'\b(?:addEventListener|addListener|\.on)\s*\(\s*[\'\"]([^\'\"]{1,150})[\'\"]'),
}

def analyze_js(path:Path,allow_node_modules=False):
    root=path.resolve()
    files=[]
    if path.is_file():files=[path]
    else:
        for p in path.rglob('*'):
            if p.is_symlink():continue
            if p.is_file() and p.suffix in ('.js','.jsx','.ts','.tsx','.mjs','.cjs'):
                if not allow_node_modules and any(x in ('node_modules','dist','build','.git') for x in p.parts):continue
                files.append(p)
                if len(files)>MAX_FILES:raise WebError('source file budget exceeded')
    observations=[];errors=[]
    for p in sorted(files):
        try:
            if p.stat().st_size>MAX_INPUT:raise WebError('file byte budget exceeded')
            txt=p.read_text(encoding='utf-8')
            if txt.count('\n')>MAX_LINES:raise WebError('line budget exceeded')
            short=str(p.relative_to(root)) if path.is_dir() else p.name
            for kind,regex in JS_PATTERNS.items():
                for match in regex.finditer(txt):
                    line=txt.count('\n',0,match.start())+1
                    if kind=='express_route':
                        data={'verb':match.group(1).upper(),'path':match.group(2)}
                    else:data={'target':match.group(1)}
                    observations.append({'file':short,'line':line,'kind':kind,**data,
                                         'confidence':'lexical candidate'})
                    if len(observations)>MAX_POINTS:raise WebError('JS reference budget exceeded')
        except (OSError,UnicodeError,WebError) as e:
            errors.append({'path':p.name,'error':str(e)[:180]})
    return {'format':'javascript-static','file_count':len(files),'references':observations,
            'errors':errors,'complete':not errors,
            'evidence_level':'lexical candidates; comments, strings, computed names and dynamic IPC not resolved'}


def normalize_path(path):
    # Treat path segments as identifiers only when strong shape signals exist.
    parts=[]
    for part in path.split('/'):
        if re.fullmatch(r'[0-9a-fA-F]{24,}|\d{4,}|[0-9a-fA-F-]{36}',part):parts.append('{id}')
        else:parts.append(part[:180])
    return '/'.join(parts)[:768]


def shape(value,depth=0):
    if depth>4:return {'type':'too_deep'}
    if value is None:return {'type':'null'}
    if isinstance(value,bool):return {'type':'boolean'}
    if isinstance(value,(int,float)):return {'type':'number'}
    if isinstance(value,str):return {'type':'string'}
    if isinstance(value,list):return {'type':'array','examples':[shape(x,depth+1) for x in value[:2]]}
    if isinstance(value,dict):return {'type':'object','fields':{k[:100]:shape(v,depth+1) for k,v in list(value.items())[:64] if not re.search(r'pass(word)?|secret|token|authoriz|cookie|api.?key',k,re.I)}}
    return {'type':'unknown'}


def analyze_har(path:Path,include_shape=False):
    obj=json.loads(bounded(path).decode('utf-8-sig'))
    entries=obj.get('log',{}).get('entries')
    if not isinstance(entries,list):raise WebError('HAR log.entries missing')
    groups={};truncated=len(entries)>MAX_NETWORK
    for n,item in enumerate(entries[:MAX_NETWORK]):
        req=item.get('request',{}) if isinstance(item,dict) else {}
        resp=item.get('response',{}) if isinstance(item,dict) else {}
        url=urlsplit(str(req.get('url','')))
        pathnorm=normalize_path(url.path)
        key=(str(req.get('method','GET')).upper()[:12],url.hostname or '',pathnorm)
        if key not in groups:
            groups[key]={'method':key[0],'host':key[1][:256], 'route':pathnorm,
                         'statuses':{},'query_parameters':set(),'examples':0,'response_shapes':{}}
        out=groups[key];out['examples']+=1
        status=str(resp.get('status','unknown'))[:16]
        out['statuses'][status]=out['statuses'].get(status,0)+1
        for k,_ in parse_qsl(url.query,keep_blank_values=True):
            if not re.search(r'auth|token|key|secret|password|session',k,re.I):out['query_parameters'].add(k[:60])
        if include_shape:
            content=resp.get('content',{})
            if content.get('mimeType','').split(';')[0]=='application/json' and isinstance(content.get('text'),str):
                try:
                    raw=content['text']
                    if len(raw)<1024*1024:
                        parsed=json.loads(raw)
                        out['response_shapes'][status]=shape(parsed)
                except (ValueError,TypeError):pass
    result=[]
    for x in groups.values():
        x['query_parameters']=sorted(x['query_parameters']);result.append(x)
    return {'format':'har-contracts','total_entries':len(entries),'analyzed_entries':min(len(entries),MAX_NETWORK),
            'routes':sorted(result,key=lambda x:(x['host'],x['route'],x['method'])),
            'complete':not truncated,'redaction':'no headers, cookies, request bodies, URL query values or response values',
            'evidence_level':'recorded requests only; not proof all API behavior is covered'}


def analyze_openapi(path:Path):
    obj=json.loads(bounded(path).decode('utf-8'))
    version=str(obj.get('openapi') or obj.get('swagger') or '')
    if not version:raise WebError('not an OpenAPI/Swagger JSON document')
    paths=obj.get('paths',{})
    if not isinstance(paths,dict):raise WebError('paths must be object')
    operations=[]
    for route,path_obj in sorted(paths.items()):
        if not isinstance(path_obj,dict):continue
        for method,decl in sorted(path_obj.items()):
            if method.lower() not in ('get','post','put','patch','delete','options','head','trace') or not isinstance(decl,dict):continue
            ops={'path':route[:500],'method':method.upper(),'operation_id':decl.get('operationId'),
                 'parameters':[{'name':p.get('name'),'in':p.get('in'),'required':p.get('required',False)} for p in decl.get('parameters',[]) if isinstance(p,dict)][:100],
                 'responses':sorted(str(k) for k in decl.get('responses',{})),
                 'has_request_body':bool(decl.get('requestBody'))}
            operations.append(ops)
            if len(operations)>MAX_NETWORK:raise WebError('OpenAPI operation budget exceeded')
    return {'format':'openapi','version':version,'operations':operations,'count':len(operations),
            'evidence_level':'declared contract; not proof deployed implementation follows schema'}


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    sub=p.add_subparsers(dest='cmd',required=True)
    for name in ('js','sourcemap','har','openapi'):
        sp=sub.add_parser(name);sp.add_argument('path',type=Path);sp.add_argument('-o','--output',type=Path)
        if name=='sourcemap':sp.add_argument('--line',type=int);sp.add_argument('--column',type=int,default=0)
        if name=='har':sp.add_argument('--include-schema-shape',action='store_true')
    a=p.parse_args(argv)
    try:
        if a.cmd=='js':v=analyze_js(a.path)
        elif a.cmd=='sourcemap':v=analyze_sourcemap(a.path,a.line,a.column)
        elif a.cmd=='har':v=analyze_har(a.path,a.include_schema_shape)
        else:v=analyze_openapi(a.path)
        s=json.dumps(v,indent=2,ensure_ascii=False)+'\n'
        if a.output:
            if a.path.resolve()==a.output.resolve():raise WebError('output aliases input')
            write_exclusive(a.output,s,[a.path])
        else:print(s,end='')
        return 0 if v.get('complete',True) else 3
    except (WebError,ValueError,UnicodeError,OSError) as e:
        print(f'ERROR: {e}',file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
