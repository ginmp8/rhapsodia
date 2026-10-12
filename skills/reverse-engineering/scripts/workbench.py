#!/usr/bin/env python3
"""Offline multiformat routing for evidence-producing static reverse engineering.

Inspect directories, a single artifact or ZIP/TAR without extraction or target
execution. Each specialist has explicit coverage status; the router never
converts incomplete/unsupported analyses into success.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import struct
import sys
from collections import Counter
from pathlib import Path
from json_writer import write_exclusive

from recon import Reader, Limits, IntakeError, archive_profile
from format_probes import scan_pe
from dotnet_analysis import analyze_dotnet
from jvm_analysis import parse_class
from wasm_semantics import analyze_wasm
from dex_analysis import analyze_dex
from evm_analysis import analyze_evm
from native_symbols import parse_elf as elf_details,parse_pe as pe_details,parse_macho as macho_details,parse_fat_macho as fat_macho_details
from web_analysis import map_segments,WebError,JS_PATTERNS
from app_manifests import parse_android_manifest,parse_plist

MAX_ANALYZED=1000
MAX_STATIC_BYTES=32*1024*1024


def route(path:str,head:bytes):
    suffix=Path(path).suffix.lower()
    if head.startswith(b'\x00asm'):return 'wasm'
    if head.startswith(b'\xca\xfe\xba\xbf') or head.startswith(b'\xbf\xba\xfe\xca') or head.startswith(b'\xbe\xba\xfe\xca'):return 'mach-o-fat'
    if head.startswith(b'\xca\xfe\xba\xbe'):
        # CAFEBABE also identifies fat Mach-O; the second word discriminates.
        if len(head)>=8 and 1 <= int.from_bytes(head[4:8], 'big') <= 32:
            return 'mach-o-fat'
        return 'jvm'
    if head.startswith(b'dex\n'):return 'dex'
    if head.startswith(b'MZ'):return 'pe-or-dotnet'
    if head.startswith(b'\x7fELF'):return 'elf'
    if head[:4] in (b'\xfe\xed\xfa\xce',b'\xce\xfa\xed\xfe',b'\xfe\xed\xfa\xcf',b'\xcf\xfa\xed\xfe'):return 'mach-o'
    if Path(path).name=='AndroidManifest.xml':return 'android-manifest'
    if suffix=='.plist':return 'apple-plist'
    if suffix in ('.evm',):return 'evm'
    if suffix in ('.js','.mjs','.cjs','.ts','.tsx','.jsx'):return 'javascript'
    if suffix=='.map':return 'source-map'
    if suffix=='.har':return 'har'
    if suffix in ('.json',):
        low=path.lower()
        if 'openapi' in low or 'swagger' in low:return 'openapi'
    return None


def inspect_bytes(path:str,raw:bytes,kind:str):
    if kind=='wasm':
        j=analyze_wasm(raw)
        return {'format':kind,'complete':j['code_walk_complete'],
                'functions':len(j['functions']), 'exports':j['exports'][:25],
                'call_count':sum(len(x['body']['calls']) for x in j['functions'] if x['body']),
                'module':j, 'evidence':'WASM bytecode call sites'}
    if kind=='evm':
        j=analyze_evm(raw)
        return {'format':'evm','complete':j['complete_decode'],'candidate_selectors':j['candidate_selectors'],
                'potential_side_effects':j['potential_side_effects'],
                'evidence':'EVM opcode stream, no ABI/stack reconstruction'}
    if kind=='jvm':
        j=parse_class(raw)
        return {'format':kind,'complete':j['complete'] and all(x.get('bytecode_walk_complete',True) for x in j['methods']),
                'class_name':j['class_name'], 'method_count':len(j['methods']),
                'call_count':sum(len(x.get('calls',[])) for x in j['methods']),'module':j,
                'evidence':'JVM constant pool and code attributes'}
    if kind=='dex':
        j=analyze_dex(raw)
        return {'format':kind,'complete':j['code_walk_complete'],'class_count':len(j['classes']),
                'method_count':sum(len(x['methods']) for x in j['classes']),
                'call_count':sum(len(m.get('invokes',[])) for x in j['classes'] for m in x['methods']),
                'module':j,'evidence':'DEX method IDs and supported invoke opcodes'}
    if kind=='pe-or-dotnet':
        j=scan_pe(raw)
        if j.get('has_cli_descriptor') and not (j.get('managed_metadata') or {}).get('warning'):
            clr=analyze_dotnet(raw)
            return {'format':'dotnet-cli','complete':clr['cil_walk_complete'],
                    'type_count':len(clr['types']),'method_count':len(clr['methods']),
                    'call_count':sum(len(m['body'].get('cil',{}).get('calls',[])) for m in clr['methods']),
                    'module':clr,'evidence':'ECMA-335 metadata and supported CIL instruction walk'}
        j['native_symbols']=pe_details(raw)
        return {'format':'pe','complete':True,'module':j,'evidence':'PE imports/exports and static header'}
    if kind=='elf':return {'format':'elf','complete':True,'module':elf_details(raw),'evidence':'ELF imported/exported symbols and relocations'}
    if kind=='mach-o':return {'format':'mach-o','complete':True,'module':macho_details(raw),'evidence':'Mach-O load commands and linked libraries'}
    if kind=='mach-o-fat':return {'format':'fat-mach-o','complete':True,'module':fat_macho_details(raw),
                                   'evidence':'Bounded Mach-O slices and load commands'}
    if kind in ('apple-plist','android-manifest'):
        j=parse_plist(raw) if kind=='apple-plist' else parse_android_manifest(raw)
        return {'format':j['format'],'complete':not j.get('truncated_output',False),
                'module':j,'evidence':j['coverage']}
    if kind=='source-map':
        j=json.loads(raw.decode('utf-8-sig'))
        if not isinstance(j,dict):raise WebError('source-map must be an object')
        points=map_segments(j)
        return {'format':kind,'complete':True,'mapping_count':len(points),'source_count':len(j['sources']),
                'sources':j['sources'][:100], 'evidence':'v3 mapping data; no JS execution'}
    if kind=='javascript':
        t=raw.decode('utf-8')
        findings=[]
        for name,pat in JS_PATTERNS.items():
            for match in pat.finditer(t):
                f={'kind':name,'line':t.count('\n',0,match.start())+1,
                   'target':match.group(2) if name=='express_route' else match.group(1)}
                if name=='express_route':f['method']=match.group(1).upper()
                findings.append(f)
                if len(findings)>2500:break
        return {'format':kind,'complete':len(findings)<=2500,
                'references':findings[:2500],'evidence':'unresolved lexical references'}
    if kind in ('har','openapi'):
        # Large JSON data may contain credentials: do not include raw values.
        from web_analysis import shape, normalize_path
        from urllib.parse import urlsplit
        obj=json.loads(raw.decode('utf-8-sig'))
        if not isinstance(obj,dict):raise WebError(f'{kind} must be a JSON object')
        if kind=='openapi':
            paths=obj.get('paths',{})
            if not isinstance(paths,dict):raise WebError('OpenAPI paths must be an object')
            operations=[{'method':verb.upper(),'path':str(path)[:512]}
                        for path,schema in paths.items() if isinstance(schema,dict)
                        for verb in schema if verb.lower() in ('get','post','put','patch','delete')]
            return {'format':kind,'complete':len(operations)<=1000,
                    'operations':operations[:1000],'evidence':'OpenAPI declared endpoints'}
        records=obj.get('log',{}).get('entries',[])
        if not isinstance(records,list):raise WebError('invalid HAR entries')
        counts=Counter()
        for x in records[:10000]:
            if not isinstance(x,dict):raise WebError('HAR entry must be object')
            req=x.get('request',{});res=x.get('response',{})
            if not isinstance(req,dict) or not isinstance(res,dict):raise WebError('HAR request/response must be objects')
            url=urlsplit(str(req.get('url','')))
            counts[(str(req.get('method','')),url.hostname,normalize_path(url.path),str(res.get('status','')))] +=1
        return {'format':kind,'complete':len(records)<=10000,
                'requests':[{'method':k[0],'host':k[1],'route':k[2],'status':k[3],'count':v}
                            for k,v in sorted(counts.items(),key=lambda item:str(item[0]))],
                'evidence':'recorded HAR requests only; query/header/body redacted'}
    raise ValueError('not a supported provider')


def analyze(path:Path,max_items:int=300,max_item_mib:int=24,include_dependencies:bool=False,full=False):
    if max_items<1 or max_items>MAX_ANALYZED:raise ValueError('--max-items out of bounds')
    if not 1<=max_item_mib<=32:raise ValueError('--max-item-mib out of bounds')
    limits=Limits(max_files=12000,max_item_bytes=max_item_mib*1048576,
                  max_total_bytes=256*1048576,max_text_bytes=512*1024)
    results=[];skips=[];issues=[];counters=Counter();budget=0; total_matched=0
    with Reader(path,limits,include_dependencies) as reader:
        for member in reader.members:
            if member.reason:
                issues.append({'path':member.path,'reason':member.reason})
                continue
            kind=route(member.path, b'')
            if kind is None and not member.path.lower().endswith(('.dll','.exe','.wasm','.dex','.class','.elf','.so','.o','.plist')):
                continue
            total_matched+=1
            if (member.compressed is not None and member.size>8192 and
                member.size>max(1,member.compressed)*200):
                skips.append({'path':member.path,'reason':'compressed expansion ratio exceeded'})
                continue
            if member.size>limits.max_item_bytes or member.size>MAX_STATIC_BYTES:
                skips.append({'path':member.path,'reason':'byte budget exceeded'})
                continue
            if len(results)>=max_items or budget+member.size>256*1048576:
                skips.append({'path':member.path,'reason':'analysis budget reached'})
                continue
            try:
                with reader.open(member) as fd:
                    raw=fd.read(member.size+1)
                if len(raw)!=member.size:raise ValueError('length changed during read')
                kind=route(member.path,raw[:16])
                if not kind:continue
                info=inspect_bytes(member.path,raw,kind)
                counters[info['format']]+=1;budget+=len(raw)
                if not full:
                    info.pop('module',None)
                    if 'references' in info:info['references']=info['references'][:200]
                results.append({'path':member.path,'sha256':hashlib.sha256(raw).hexdigest(), **info})
            except (OSError,ValueError,OverflowError,UnicodeError,RuntimeError,RecursionError,
                    IndexError,KeyError,TypeError,struct.error) as exc:
                issues.append({'path':member.path,'provider':kind,'error':str(exc)[:220]})
        partial=reader.partial or bool(skips or issues) or not results or any(not r['complete'] for r in results)
        return {'schema_version':'1.0','mode':'discover','input':str(path.resolve()),
                'archive_kind':archive_profile(reader),'files_seen':len(reader.members),
                'matched_candidates':total_matched,'analyzed':len(results),
                'results':results,'formats':dict(sorted(counters.items())),
                'skipped':skips[:300], 'errors':issues[:300],
                'complete':not partial,
                'notes':reader.notes,
                'coverage_scope':'selected recognized files and supported static constructs only; not all files, instructions, or runtime behavior',
                'evidence_rule':'static only, approximate or declared details labeled, no target execution; incomplete != passing'}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path',type=Path);parser.add_argument('-o','--output',type=Path)
    parser.add_argument('--max-items',type=int,default=300)
    parser.add_argument('--max-item-mib',type=int,default=24)
    parser.add_argument('--include-dependencies',action='store_true')
    parser.add_argument('--full',action='store_true',help='include full method metadata and bytecode evidence; may be large')
    a=parser.parse_args(argv)
    try:
        out=analyze(a.path,a.max_items,a.max_item_mib,a.include_dependencies,a.full)
        s=json.dumps(out,ensure_ascii=False,indent=2,allow_nan=False)+'\n'
        if a.output:
            if a.output.resolve()==a.path.resolve():raise ValueError('output aliases input')
            write_exclusive(a.output,s,[a.path])
        else:print(s,end='')
        return 0 if out['complete'] else 3
    except (ValueError,IntakeError,OSError) as exc:
        print(f'ERROR: {exc}',file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
