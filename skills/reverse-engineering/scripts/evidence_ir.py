#!/usr/bin/env python3
"""Evidence-backed intermediate graph from static parsers and optional adapters.

A node/edge is evidence *about* syntax/metadata/call sites; never a proof of
runtime reachability, resolution or behavioral equivalence. SQLite is optional,
local and append-only per exact source SHA. All raw untrusted reports are data.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sqlite3
import sys
from typing import Any
from behavior_lab import DataError, strict_json
from json_writer import write_exclusive

MAX_REPORT=32*1024*1024
MAX_NODES=50000
MAX_EDGES=100000


def sha(v:bytes)->str:return hashlib.sha256(v).hexdigest()

def label_hash(v:str)->str:return sha(v.encode('utf-8'))[:20]

def norm(text:Any, size=512)->str:return str(text)[:size]


def normalize(report:dict,report_sha:str)->dict:
    nodes:dict[str,dict]={};edges:dict[str,dict]={}
    def node(kind:str,label:str,level:str,anchor:str,artifact:str=''):
        ident=f'{report_sha[:12]}:{kind}:{label_hash(artifact+":"+anchor+":"+label)}'
        if len(nodes)>=MAX_NODES and ident not in nodes:raise DataError('node budget exceeded')
        nodes[ident]={'id':ident,'kind':kind,'label':norm(label),'evidence_level':level,
                      'anchor':norm(anchor,1024),'artifact':norm(artifact),'report_sha256':report_sha}
        return ident
    def edge(source:str,target:str,kind:str,level:str,anchor:str):
        ident=f'{report_sha[:12]}:edge:{label_hash(source+":"+target+":"+kind+":"+anchor)}'
        if len(edges)>=MAX_EDGES and ident not in edges:raise DataError('edge budget exceeded')
        edges[ident]={'id':ident,'source':source,'target':target,'kind':kind,
                      'evidence_level':level,'anchor':norm(anchor,1024),'report_sha256':report_sha}

    source=node('report',report_sha,'recorded','sha256:'+report_sha)
    raw_items=report.get('results') if isinstance(report.get('results'),list) else [report]
    for index,item in enumerate(raw_items[:5000]):
        if not isinstance(item,dict):continue
        path=norm(item.get('path',item.get('source_path',f'entry:{index}')))
        format_name=norm(item.get('format','unknown'))
        artifact=node('artifact',path,'declared',path)
        edge(source,artifact,'contains','declared',path)
        level='decoded_call_site'
        metadata=item.get('module',item)
        if not isinstance(metadata,dict):continue
        kinds={'dotnet-cli','jvm','jvm-class','wasm','dex','android-archive','openapi','javascript'}
        if format_name in kinds or isinstance(metadata.get('methods'),list):
            methods=[]
            if format_name=='dotnet-cli':
                methods=[(m,m.get('owner','')+'.'+m.get('name',''),m.get('body',{}).get('cil',{}).get('calls',[]))
                         for m in metadata.get('methods',[]) if isinstance(m,dict)]
            elif format_name in ('jvm','jvm-class'):
                methods=[(m,metadata.get('class_name','')+'.'+m.get('name','')+m.get('descriptor',''),m.get('calls',[]))
                         for m in metadata.get('methods',[]) if isinstance(m,dict)]
            elif format_name=='wasm':
                methods=[(m,'func#'+str(m.get('index')), (m.get('body') or {}).get('calls',[]))
                         for m in metadata.get('functions',[]) if isinstance(m,dict)]
            elif format_name=='dex':
                methods=[(m,c.get('name','')+'.'+m.get('name',''),m.get('invokes',[]))
                         for c in metadata.get('classes',[]) if isinstance(c,dict)
                         for m in c.get('methods',[]) if isinstance(m,dict)]
            for m,name,calls in methods[:20000]:
                declared=node('method',str(name),'declared',path+':'+norm(m.get('token',m.get('method_id',''))),path)
                edge(artifact,declared,'declares','declared',path)
                for call in calls[:1000] if isinstance(calls,list) else []:
                    if not isinstance(call,dict):continue
                    target=call.get('target')
                    text=norm(call.get('owner','')+'.'+call.get('name','') if call.get('name') else target if target else call.get('token','unresolved'))
                    dest=node('call-target-candidate',text,'unresolved',path+':'+norm(call.get('offset',call.get('at',''))),path)
                    edge(declared,dest,'calls-at-site',level,path+':'+norm(call.get('offset','?')))
        for obj in item.get('operations',[]) if isinstance(item.get('operations'),list) else []:
            if isinstance(obj,dict):
                target=node('api-operation',norm(obj.get('method','')+' '+obj.get('path','')),'declared',path,path)
                edge(artifact,target,'declares','declared',path)
        for obj in item.get('references',[]) if isinstance(item.get('references'),list) else []:
            if isinstance(obj,dict):
                target=node('reference-candidate',norm(obj.get('target',obj.get('name','unknown'))),'lexical_candidate',path+':'+norm(obj.get('line','?')),path)
                edge(artifact,target,'references','lexical_candidate',path+':'+norm(obj.get('line','?')))
        for obj in metadata.get('symbols',[]) if isinstance(metadata.get('symbols'),list) else []:
            if isinstance(obj,dict):
                label=norm(obj.get('name',obj.get('symbol','unknown')))
                target=node('symbol',label,obj.get('evidence_level','declared'),path+':'+norm(obj.get('address',obj.get('line','?'))),path)
                edge(artifact,target,'declares',obj.get('evidence_level','declared'),path)
                for ref in obj.get('references',[]) if isinstance(obj.get('references'),list) else []:
                    dest=node('call-target-candidate',norm(ref),'unresolved',path,path)
                    edge(target,dest,'calls-at-site','decoded_call_site',path)
    # Optional dynamic evidence is represented separately from static declarations.
    # Temporal proximity, route shapes, DOM changes and offline fixtures DO NOT
    # prove backend handler execution or actual network reachability.
    if report.get('mode') == 'web-investigation':
        fixture = report.get('evidence_type') == 'trusted-offline-html-fixture'
        level = 'fixture_observed' if fixture else 'runtime_observed'
        for step in report.get('steps', [])[:100]:
            if not isinstance(step, dict):
                continue
            index = step.get('index', '?')
            action = node('browser-action', norm(step.get('type', 'unknown')), level, 'step:' + str(index))
            edge(source, action, 'records-browser-step', level, 'step:' + str(index))
            dom = step.get('dom', {})
            if isinstance(dom, dict) and isinstance(dom.get('text_sha256'), str):
                observed = node('dom-snapshot', dom['text_sha256'][:64], level, 'dom-after:' + str(index))
                edge(action, observed, 'observed-after-action', level, 'dom-after:' + str(index))
        for i, event in enumerate(report.get('events', [])[:1500]):
            if not isinstance(event, dict) or event.get('observed') is not True:
                continue
            kind = event.get('kind')
            if kind not in ('request','response'):
                continue
            label = str(event.get('method', event.get('status', '?'))) + ' ' + str(event.get('path','?'))
            request = node('browser-' + kind, norm(label), 'runtime_observed', 'event:' + str(i))
            edge(source, request, 'records-network-metadata', 'runtime_observed', 'event:' + str(i))
        for i, link in enumerate(report.get('links', [])[:1000]):
            if not isinstance(link, dict):
                continue
            src = node('browser-page', str(link.get('from', '?')), 'fixture_observed' if fixture else 'runtime_observed', 'link-from:' + str(i))
            dst = node('browser-page', str(link.get('to', '?')), 'declared', 'link-to:' + str(i))
            edge(src, dst, 'declares-link-to', 'declared', 'link:' + str(i))
            edge(source, src, 'records-browser-page', level, 'link:' + str(i))
    elif report.get('mode') == 'web-route-correlation':
        for i, match in enumerate(report.get('matches', [])[:5000]):
            if not isinstance(match, dict):
                continue
            observed = node('observed-http-route', norm(str(match.get('method', '?')) + ' ' + str(match.get('observed_path', '?'))),
                            'runtime_observed', 'match-event:' + str(match.get('event_index', '?')))
            declared = node('declared-api-route', norm(str(match.get('method', '?')) + ' ' + str(match.get('declared_route', '?'))),
                            'declared', 'contract-operation:' + str(match.get('operation_index', '?')))
            edge(source, observed, 'contains-route-match', 'recorded', 'match:' + str(i))
            edge(observed, declared, 'candidate-route-shape-match', 'inferred', 'match:' + str(i))
    return {'schema_version':'1.0','mode':'evidence-ir','report_sha256':report_sha,
            'nodes':sorted(nodes.values(),key=lambda n:n['id']),
            'edges':sorted(edges.values(),key=lambda n:n['id']),
            'completeness':'recognized static evidence only; dynamic call targets unresolved'}


def create_schema(db:sqlite3.Connection)->None:
    db.executescript('''
    CREATE TABLE IF NOT EXISTS sources (source_sha TEXT PRIMARY KEY, mode TEXT NOT NULL, node_count INTEGER NOT NULL, edge_count INTEGER NOT NULL);
    CREATE TABLE IF NOT EXISTS nodes (id TEXT PRIMARY KEY, source_sha TEXT NOT NULL REFERENCES sources(source_sha), kind TEXT NOT NULL, label TEXT NOT NULL, evidence_level TEXT NOT NULL, anchor TEXT NOT NULL, artifact TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS edges (id TEXT PRIMARY KEY, source_sha TEXT NOT NULL REFERENCES sources(source_sha), source_id TEXT NOT NULL REFERENCES nodes(id), target_id TEXT NOT NULL REFERENCES nodes(id), kind TEXT NOT NULL, evidence_level TEXT NOT NULL, anchor TEXT NOT NULL);
    CREATE INDEX IF NOT EXISTS idx_node_source ON nodes(source_sha);
    CREATE INDEX IF NOT EXISTS idx_edge_source ON edges(source_sha);
    CREATE INDEX IF NOT EXISTS idx_node_kind ON nodes(kind);
    ''')


def persist(db_path:Path,reports:list[dict])->list[dict]:
    db_path.parent.mkdir(parents=True,exist_ok=True)
    outcomes=[]
    with sqlite3.connect(db_path) as db:
        db.execute('PRAGMA foreign_keys=ON')
        with db:
            create_schema(db)
            for graph in reports:
                source=graph['report_sha256']
                if db.execute('SELECT 1 FROM sources WHERE source_sha=?',(source,)).fetchone():
                    outcomes.append({'source_sha256':source,'status':'unchanged-reused'})
                    continue
                db.execute('INSERT INTO sources VALUES (?,?,?,?)',(source,graph['mode'],len(graph['nodes']),len(graph['edges'])))
                db.executemany('INSERT INTO nodes VALUES (?,?,?,?,?,?,?)', [(
                    n['id'],source,n['kind'],n['label'],n['evidence_level'],n['anchor'],n['artifact']) for n in graph['nodes']])
                db.executemany('INSERT INTO edges VALUES (?,?,?,?,?,?,?)', [(
                    e['id'],source,e['source'],e['target'],e['kind'],e['evidence_level'],e['anchor']) for e in graph['edges']])
                outcomes.append({'source_sha256':source,'status':'imported','nodes':len(graph['nodes']),'edges':len(graph['edges'])})
    return outcomes


def export(db_path:Path)->dict:
    if not db_path.is_file():raise DataError('SQLite graph file missing')
    with sqlite3.connect(db_path.resolve().as_uri()+'?mode=ro',uri=True) as db:
        db.execute('PRAGMA foreign_keys=ON')
        db.row_factory=sqlite3.Row
        sources=[dict(r) for r in db.execute('SELECT * FROM sources ORDER BY source_sha')]
        nodes=[dict(r) for r in db.execute('SELECT * FROM nodes ORDER BY id LIMIT 50001')]
        edges=[dict(r) for r in db.execute('SELECT * FROM edges ORDER BY id LIMIT 100001')]
        if len(nodes)>MAX_NODES or len(edges)>MAX_EDGES:
            raise DataError('export budget exceeded')
    return {'schema_version':'1.0','mode':'graphview-export','sources':sources,'nodes':nodes,'edges':edges,
            'completeness':'all persisted bounded evidence records, not all software behavior'}


def ingest(reports:list[Path],db_path:Path|None=None)->dict:
    output=[]
    for path in reports:
        if path.is_symlink() or not path.is_file() or path.stat().st_size>MAX_REPORT:
            raise DataError('report must be bounded nonsymlink file')
        raw=path.read_bytes()
        report=strict_json(raw.decode('utf-8'))
        if not isinstance(report,dict):raise DataError('report must be JSON object')
        output.append(normalize(report,sha(raw)))
    result={'schema_version':'1.0','mode':'evidence-ir-batch','reports':output}
    if db_path:result['sqlite_import']=persist(db_path,output)
    return result


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('command',choices=['build','export'])
    ap.add_argument('reports',nargs='*',type=Path)
    ap.add_argument('--sqlite',type=Path)
    ap.add_argument('-o','--output',required=True,type=Path)
    a=ap.parse_args(argv)
    try:
        if a.command=='build':
            if not a.reports:raise DataError('at least one report required')
            inputs=a.reports+[a.sqlite] if a.sqlite else a.reports
            if any(a.output.resolve()==p.resolve() for p in inputs):raise DataError('output aliases input')
            result=ingest(a.reports,a.sqlite)
        else:
            if not a.sqlite or a.reports:raise DataError('export requires --sqlite and no reports')
            if a.output.resolve()==a.sqlite.resolve():raise DataError('output aliases database')
            result=export(a.sqlite)
        write_exclusive(a.output,json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n',a.reports+([a.sqlite] if a.sqlite else []))
        return 0
    except (OSError,ValueError,sqlite3.DatabaseError) as exc:
        print(json.dumps({'error':str(exc)}),file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
