#!/usr/bin/env python3
"""Portable local data-to-graph workbench. See --help for entry points."""
from __future__ import annotations
import argparse
import importlib.util
import json
import sqlite3
import sys
import time
from pathlib import Path
import graph_engine as ge
from graph_common import read_json,write_json,atomic_write,canonical,digest
from graph_data import read_rows,profile,propose_mapping,rows_to_patch,file_info,structural_json
from graph_store import apply_patches,readonly,backup
from graph_query import query
from graph_adapters import scan,sqlite_schema,openapi,git_history,transcribe
from graph_analysis import analyze
from graph_interop import bundle,import_bundle,diff,history,drop_source,source_revision,remember,reflect,export_view,serialize_view,export_wiki,graphml_patch,save_query,saved_queries
from graph_access import sql_read,serve,mcp_stdio

LEGACY={'init','validate-patch','apply-patch','find','node','neighbors','path','impact','stats','validate-db','export-view'}

def command_token(args):
    skip=False
    for arg in args:
        if skip:skip=False;continue
        if arg=='--db':skip=True;continue
        if arg.startswith('--db='):continue
        if not arg.startswith('-'):return arg
    return None

def parser():
    p=argparse.ArgumentParser(description=__doc__,epilog='Legacy commands remain available: '+', '.join(sorted(LEGACY)))
    p.add_argument('--db',default='.local-graph/graph.db')
    sub=p.add_subparsers(dest='command',required=True)
    sub.add_parser('doctor')
    q=sub.add_parser('journal');q.add_argument('--mode',choices=['delete','wal'],required=True)
    for name in ['inspect','model','ingest']:
        q=sub.add_parser(name);q.add_argument('source');q.add_argument('--namespace');q.add_argument('--table');q.add_argument('--records-path');q.add_argument('--header-row',type=int,default=1);q.add_argument('--max-rows',type=int,default=100000)
        if name=='model':q.add_argument('--output',required=True);q.add_argument('--kind',default='record')
        if name=='ingest':q.add_argument('--mapping');q.add_argument('--structural',action='store_true');q.add_argument('--patch-output')
    for name in ['scan','watch']:
        q=sub.add_parser(name);q.add_argument('source');q.add_argument('--namespace',required=True);q.add_argument('--code-backend',choices=['builtin','tree-sitter'],default='builtin');q.add_argument('--max-files',type=int,default=2000);q.add_argument('--patch-output');q.add_argument('--prune-missing',action='store_true')
        if name=='watch':q.add_argument('--iterations',type=int,default=3);q.add_argument('--interval',type=float,default=10)
    for name in ['schema','openapi','git']:
        q=sub.add_parser(name);q.add_argument('source');q.add_argument('--namespace',required=True);q.add_argument('--patch-output')
        if name=='git':q.add_argument('--max-commits',type=int,default=100)
    q=sub.add_parser('import-graphml');q.add_argument('source');q.add_argument('--namespace',required=True)
    q=sub.add_parser('save-query');q.add_argument('name');q.add_argument('request')
    q=sub.add_parser('saved-query');q.add_argument('name',nargs='?')
    q=sub.add_parser('transcribe');q.add_argument('source');q.add_argument('--model-dir',required=True);q.add_argument('--namespace',required=True);q.add_argument('--patch-output')
    q=sub.add_parser('apply-batch');q.add_argument('input')
    q=sub.add_parser('query');q.add_argument('request',help='JSON request file, or a JSON object')
    q=sub.add_parser('sql');q.add_argument('statement');q.add_argument('--limit',type=int,default=100)
    q=sub.add_parser('analyze');q.add_argument('algorithm',choices=['components','scc','cycles','degree','pagerank','communities','louvain','leiden','betweenness','closeness']);q.add_argument('--backend',choices=['stdlib','networkx'],default='stdlib');q.add_argument('--seed',type=int,default=0)
    q=sub.add_parser('export');q.add_argument('format',choices=['json','graphml','dot','mermaid','csv','wiki']);q.add_argument('output');q.add_argument('--request');q.add_argument('--seed');q.add_argument('--depth',type=int,default=2);q.add_argument('--max-nodes',type=int,default=500)
    q=sub.add_parser('bundle');q.add_argument('output')
    q=sub.add_parser('merge');q.add_argument('input');q.add_argument('--namespace',required=True)
    q=sub.add_parser('diff');q.add_argument('before');q.add_argument('after')
    q=sub.add_parser('backup');q.add_argument('output')
    q=sub.add_parser('history');q.add_argument('--source-uri')
    q=sub.add_parser('drop-source');q.add_argument('source_uri');q.add_argument('--confirm',action='store_true')
    q=sub.add_parser('restore-source');q.add_argument('source_uri');q.add_argument('revision');q.add_argument('--confirm',action='store_true')
    q=sub.add_parser('remember');q.add_argument('question');q.add_argument('--nodes',nargs='+',required=True);q.add_argument('--outcome',choices=['useful','dead_end','corrected'],required=True);q.add_argument('--note',default='')
    sub.add_parser('reflect')
    q=sub.add_parser('serve');q.add_argument('--viewer',required=True,help='Reviewed local-live HTML runtime v1, not an offline/custom page');q.add_argument('--port',type=int,default=8765);q.add_argument('--viewer-sha256',help='Optional expected hash from the render receipt')
    sub.add_parser('mcp')
    return p

def request_value(value):
    if value.lstrip().startswith('{'):
        from graph_common import parse_json
        return parse_json(value)
    return read_json(Path(value))

def persist(db,patches):
    if not db.exists():ge.init_db(db)
    return apply_patches(db,patches)

def execute(args):
    db=Path(args.db).expanduser().resolve();cmd=args.command
    if cmd=='journal':
        from graph_journal import set_journal
        return set_journal(db,args.mode)
    if cmd=='doctor':
        import shutil
        return {'status':'pass','version':ge.PACKAGE_VERSION,'python':sys.version.split()[0],'sqlite':sqlite3.sqlite_version,'core':'stdlib','optional_libraries':{m:bool(importlib.util.find_spec(m)) for m in ['networkx','pypdf','openpyxl','yaml','tree_sitter_language_pack','faster_whisper']},'optional_tools':{m:bool(shutil.which(m)) for m in ['git','dotnet']},'network_required':False,'new_database_journal':'delete','wal_reset_fixed':__import__('graph_journal').wal_reset_fixed()}
    if cmd in ('inspect','model','ingest'):
        path=Path(args.source).resolve()
        mapping=read_json(Path(args.mapping)) if cmd=='ingest' and args.mapping else None
        namespace=args.namespace or (mapping or {}).get('namespace')
        if cmd!='inspect' and not namespace:raise ValueError('choose --namespace or provide it in the mapping')
        if cmd=='ingest' and args.structural:
            if mapping:raise ValueError('structural mode does not use a row mapping')
            patch=structural_json(read_json(path),file_info(path,namespace))
        else:
            rows=read_rows(path,table=args.table,records_path=args.records_path,max_rows=args.max_rows,header_row=args.header_row)
            if cmd=='inspect':return {'status':'pass','profile':profile(rows)}
            if cmd=='model':
                value=propose_mapping(rows,namespace,args.kind);write_json(Path(args.output),value,[path,db]);return {'status':'pass','mapping':value,'output':args.output,'review_required':True}
            mapping=mapping or propose_mapping(rows,namespace)
            if mapping['namespace']!=namespace:raise ValueError('namespace conflicts with the mapping')
            source=file_info(path,namespace)
            if args.table:source['uri']+='/'+__import__('urllib.parse',fromlist=['quote']).quote(args.table,safe='')
            if path.suffix.lower() in ('.db','.sqlite','.sqlite3'):source['content_hash']='sha256:'+digest(rows)
            patch=rows_to_patch(rows,source,mapping)
        if args.patch_output:
            protected=[path,db]+([Path(args.mapping)] if cmd=='ingest' and args.mapping else [])
            write_json(Path(args.patch_output),patch,protected)
        return persist(db,[patch])
    if cmd in ('scan','watch'):
        iterations=args.iterations if cmd=='watch' else 1
        if not 1<=iterations<=1000:raise ValueError('watch iterations must be in [1,1000]')
        if cmd=='watch' and not 0<=args.interval<=3600:raise ValueError('watch interval outside bounds')
        results=[]
        for i in range(iterations):
            result=scan(Path(args.source),args.namespace,args.code_backend,args.max_files)
            if result['status']=='fail':return result
            patches=result.pop('patches')
            if args.prune_missing and db.exists():
                from urllib.parse import quote
                prefix='source://'+quote(args.namespace,safe='')+'/'
                current={p['source']['uri'] for p in patches}
                for old in bundle(db)['patches']:
                    if old['source']['uri'].startswith(prefix) and old['source']['uri'] not in current:
                        old['nodes']=[];old['edges']=[];old['source']['metadata']=dict(old['source'].get('metadata',{}),tombstone=True);patches.append(old)
            if args.patch_output:
                output=Path(args.patch_output).expanduser().absolute()
                root=Path(args.source).resolve()
                if root.is_dir() and (output.resolve().is_relative_to(root) or (output.exists() and any(output.samefile(p) for p in root.rglob('*') if p.is_file() and not p.is_symlink()))):
                    raise ValueError('scan patch output must be outside the source tree and not alias a source')
                write_json(output,{'patches':patches,'coverage':result['coverage']},[db,root])
            mutation=persist(db,patches) if patches else {'status':'pass','mutated':False}
            results.append(dict(mutation,coverage=result['coverage']))
            if i+1<iterations:time.sleep(args.interval)
        return results[0] if cmd=='scan' else {'status':'pass','runs':results,'mode':'foreground bounded polling'}
    if cmd in ('schema','openapi','git','transcribe'):
        path=Path(args.source).resolve()
        patch=sqlite_schema(path,args.namespace) if cmd=='schema' else openapi(path,args.namespace) if cmd=='openapi' else git_history(path,args.namespace,args.max_commits) if cmd=='git' else transcribe(path,Path(args.model_dir).resolve(),args.namespace)
        if args.patch_output:write_json(Path(args.patch_output),patch,[path,db])
        return persist(db,[patch])
    if cmd=='import-graphml':return persist(db,[graphml_patch(Path(args.source).resolve(),args.namespace)])
    if cmd=='save-query':return save_query(db,args.name,request_value(args.request))
    if cmd=='saved-query':return saved_queries(db,args.name)
    if cmd=='apply-batch':
        value=read_json(Path(args.input));patches=value.get('patches') if isinstance(value,dict) else value
        return persist(db,patches)
    if cmd=='query':
        from graph_access import execute_query
        return execute_query(db,request_value(args.request))
    if cmd=='sql':return sql_read(db,args.statement,args.limit)
    if cmd=='analyze':return analyze(db,args.algorithm,args.backend,args.seed)
    if cmd=='export':
        req=request_value(args.request) if args.request else {'seed':args.seed,'depth':args.depth,'max_nodes':args.max_nodes}
        value=export_view(db,req);output=Path(args.output)
        if args.format=='wiki':return export_wiki(value,output)
        protected=[db]+([Path(args.request)] if args.request and not args.request.lstrip().startswith('{') else [])
        atomic_write(output,serialize_view(value,args.format),protected);return {'status':'pass','output':str(output),'nodes':len(value['nodes']),'edges':len(value['edges']),'format':args.format}
    if cmd=='bundle':write_json(Path(args.output),bundle(db),[db]);return {'status':'pass','output':args.output}
    if cmd=='merge':
        path=Path(args.input).resolve()
        if path==db:raise ValueError('cannot merge database into itself')
        value=bundle(path) if path.suffix.lower() in ('.db','.sqlite','.sqlite3') else read_json(path)
        if not db.exists():ge.init_db(db)
        return import_bundle(db,value,args.namespace)
    if cmd=='diff':return diff(read_json(Path(args.before)),read_json(Path(args.after)))
    if cmd=='backup':return backup(db,Path(args.output))
    if cmd=='history':return history(db,args.source_uri)
    if cmd=='drop-source':
        if not args.confirm:raise ValueError('source removal requires --confirm')
        return drop_source(db,args.source_uri)
    if cmd=='restore-source':
        if not args.confirm:raise ValueError('restore requires --confirm')
        return apply_patches(db,[source_revision(db,args.source_uri,args.revision)])
    if cmd=='remember':return remember(db,args.question,args.nodes,args.outcome,args.note)
    if cmd=='reflect':return reflect(db)
    if cmd=='serve':serve(db,Path(args.viewer).expanduser().absolute(),args.port,viewer_sha256=args.viewer_sha256);return None
    if cmd=='mcp':mcp_stdio(db);return None
    raise ValueError('unknown command')

def main(argv=None):
    argv=list(sys.argv[1:] if argv is None else argv)
    if command_token(argv) in LEGACY:return ge.main(argv)
    args=parser().parse_args(argv)
    try:
        result=execute(args)
        if result is not None:
            print(canonical(result) if result.get('schema_version') == 'graph-context-v1' else json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False))
        return 0 if result is None or result.get('status')=='pass' else 1
    except (ValueError,KeyError,TypeError,OSError,RuntimeError,sqlite3.Error) as exc:
        result={'status':'fail','error':str(exc)}
        if args.command=='mcp':print(str(exc),file=sys.stderr)
        else:print(json.dumps(result,ensure_ascii=False,sort_keys=True))
        return 1

if __name__=='__main__':raise SystemExit(main())
