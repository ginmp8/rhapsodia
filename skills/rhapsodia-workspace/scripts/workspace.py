#!/usr/bin/env python3
"""Discover, validate, index and render source-owned artifacts without modifying them."""
from __future__ import annotations
import argparse
from collections import defaultdict
import json
from pathlib import Path
import sys
from artifact_protocol import (ContractError, atomic_write, canonical_bytes, confined,
                               digest, discover, exclusive_lock, load_json, validate_record)

PACKAGE=Path(__file__).resolve().parents[1]

def _dependency_cycles(records):
    edges={r['artifact_id']:[x['target'] for x in r['relations'] if x['type']=='depends_on'] for r in records}
    indegree={key:0 for key in edges}
    for targets in edges.values():
        for target in targets:
            if target in indegree:indegree[target]+=1
    queue=sorted(key for key,value in indegree.items() if value==0)
    visited=0
    while queue:
        item=queue.pop();visited+=1
        for target in edges[item]:
            if target in indegree:
                indegree[target]-=1
                if indegree[target]==0:queue.append(target)
    if visited!=len(edges):raise ContractError('DEPENDENCY_CYCLE')

def build_catalog(repo: Path, roots: list[str] | None=None, destination='local') -> dict:
    roots=sorted(set(roots or ['docs']))
    repo=repo.resolve(strict=True)
    entries=[];ids=set();identities=[]
    for path in discover(repo,roots):
        record=load_json(path);validate_record(record,repo,path)
        if record['artifact_id'] in ids:raise ContractError('DUPLICATE_ARTIFACT_ID')
        if destination not in record['privacy']['allowed_destinations']:
            raise ContractError('DESTINATION_NOT_AUTHORIZED')
        if destination=='public' and (record['privacy']['classification']!='public' or not record['privacy']['external_share_allowed']):
            raise ContractError('PUBLIC_EXPORT_DENIED')
        ids.add(record['artifact_id']);manifest_sha=digest(path.read_bytes())
        rel=path.relative_to(repo).as_posix()
        entries.append({'record':record,'manifest_path':rel,'manifest_sha256':manifest_sha})
        identities.append({'path':rel,'manifest_sha256':manifest_sha,'source_sha256':record['source']['sha256']})
    entries.sort(key=lambda e:e['record']['artifact_id'])
    records=[e['record'] for e in entries]
    active=[r for r in records if r['lifecycle']!='removed']
    _dependency_cycles(active)
    active_ids={r['artifact_id'] for r in active}
    diagnostics=[]
    for record in active:
        for relation in record['relations']:
            if relation['target'] not in active_ids:
                diagnostics.append({'severity':'warning','code':'UNRESOLVED_RELATION','artifact_id':record['artifact_id'],
                                    'target':relation['target']})
    fingerprint=digest(canonical_bytes({'version':'1.0.0','roots':roots,'sources':identities,'destination':destination}))
    return {'schema_version':'1.0.0','kind':'derived-artifact-catalog','authority':'non-authoritative',
            'source_roots':roots,'destination':destination,'source_fingerprint':fingerprint,
            'latest_source_update':max((r['updated_at'] for r in records),default=None),
            'entries':entries,'diagnostics':sorted(diagnostics,key=lambda d:(d['artifact_id'],d['target']))}

def project(catalog: dict, view: str) -> dict:
    records=[item['record'] for item in catalog['entries'] if item['record']['lifecycle']!='removed']
    if view=='portfolio':
        groups=defaultdict(list)
        for record in records:
            groups[record['work_item_id']].append({'artifact_id':record['artifact_id'],'producer':record['producer'],
                    'dimension':record['state']['dimension'],'state':record['state']['value'],'title':record['title']})
        data=[{'work_item_id':key,'artifacts':value} for key,value in sorted(groups.items())]
    elif view=='timeline':
        # Update chronology, not invented lifecycle events or stage durations.
        data=[{'artifact_id':r['artifact_id'],'producer':r['producer'],'created_at':r['created_at'],
               'updated_at':r['updated_at'],'state':r['state']} for r in sorted(records,key=lambda r:(r['updated_at'],r['artifact_id']))]
    elif view=='relations':
        data={'nodes':[{'id':r['artifact_id'],'producer':r['producer'],'title':r['title']} for r in records],
              'edges':[{'source':r['artifact_id'],**edge} for r in records for edge in r['relations']]}
    elif view=='skills':
        groups=defaultdict(list)
        for r in records:groups[r['producer']].append(r)
        data=[]
        for producer,items in sorted(groups.items()):
            states=defaultdict(int)
            for r in items:states[r['state']['dimension']+':'+r['state']['value']]+=1
            data.append({'producer':producer,'artifact_count':len(items),'states':dict(sorted(states.items()))})
    else:raise ContractError('UNKNOWN_VIEW')
    return {'schema_version':'1.0.0','authority':'non-authoritative','view':view,
            'source_fingerprint':catalog['source_fingerprint'],'data':data}

def render(catalog: dict) -> bytes:
    template=(PACKAGE/'assets/workspace.html').read_text(encoding='utf-8')
    data=canonical_bytes(catalog).decode('utf-8').replace('&','\\u0026').replace('<','\\u003c').replace('>','\\u003e')
    return template.replace('__CATALOG_JSON__',data).encode('utf-8')

def derived_path(repo: Path,relative: str) -> Path:
    path=confined(repo,relative)
    base=repo/'.rhapsodia'
    # A projection cannot overwrite source files, manifests, transport state or migrations.
    if not (path.is_relative_to(base/'catalog') or path.is_relative_to(base/'views')):
        raise ContractError('OUTPUT_NOT_DERIVED')
    return path

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['discover','index','validate','project','render'])
    parser.add_argument('--repo-root',required=True,type=Path)
    parser.add_argument('--source-root',action='append',dest='roots')
    parser.add_argument('--destination',choices=['local','internal','public'],default='local')
    parser.add_argument('--view',choices=['portfolio','timeline','relations','skills'],default='portfolio')
    parser.add_argument('--output',help='Repository-relative path under .rhapsodia/catalog or .rhapsodia/views only')
    args=parser.parse_args(argv)
    try:
        repo=args.repo_root.resolve(strict=True)
        if args.command=='discover':
            result={'authority':'non-authoritative','manifests':[p.relative_to(repo).as_posix() for p in discover(repo,args.roots or ['docs'])]}
        else:
            catalog=build_catalog(repo,args.roots,args.destination)
            if args.command=='validate':
                result={'status':'pass','record_count':len(catalog['entries']),'source_fingerprint':catalog['source_fingerprint'],'diagnostics':catalog['diagnostics']}
            elif args.command=='project':
                result=project(catalog,args.view)
                if args.output:
                    output=derived_path(repo,args.output)
                    with exclusive_lock(confined(repo,'.rhapsodia/.workspace-write.lock')):atomic_write(output,canonical_bytes(result))
            else:
                relative=args.output or ('.rhapsodia/views/index.html' if args.command=='render' else '.rhapsodia/catalog/catalog.json')
                output=derived_path(repo,relative)
                data=render(catalog) if args.command=='render' else canonical_bytes(catalog)
                with exclusive_lock(confined(repo,'.rhapsodia/.workspace-write.lock')):
                    # Re-read canonical inputs after acquiring the output lock to reject source drift.
                    current=build_catalog(repo,args.roots,args.destination)
                    if current!=catalog:raise ContractError('SOURCE_CHANGED_DURING_PROJECTION')
                    atomic_write(output,data)
                result={'status':'pass','authority':'non-authoritative','record_count':len(catalog['entries']),
                        'output':relative,'sha256':digest(data),'source_fingerprint':catalog['source_fingerprint'],'diagnostics':catalog['diagnostics']}
        print(canonical_bytes(result).decode(),end='');return 0
    except (ContractError,OSError,ValueError,KeyError,TypeError) as exc:
        code=str(exc) if isinstance(exc,ContractError) else type(exc).__name__
        print(json.dumps({'status':'fail','code':code}));return 1

if __name__=='__main__':raise SystemExit(main())
