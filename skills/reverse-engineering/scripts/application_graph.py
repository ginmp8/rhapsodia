#!/usr/bin/env python3
"""Independent, read-only application graph and bounded feature tracing.

Recognizes lexical JS/TS/Electron conventions; never executes code or resolves
computed imports, framework runtime dispatch or transpilation semantics.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import PurePosixPath, Path
from collections import defaultdict, deque
from artifact_index import VirtualArtifact, ArtifactError, digest, strict_json

JS = ('.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs', '.mts', '.cts', '.vue', '.svelte')
MAX_SOURCE = 2 * 1024 * 1024
MAX_GRAPH_EDGES = 28000
MAX_TRACE_NODES = 2000

# These expressions only identify concrete spelled-out tokens; they are not a JS parser.
PATTERNS = {
    'esm-import': re.compile(r'\bimport\s+(?:type\s+)?(?:[^;\n]*?\s+from\s+)?["\']([^"\'\n]+)["\']'),
    'esm-reexport': re.compile(r'\bexport\s+(?:\*|\{[^}\n]{1,500}\})\s+from\s+["\']([^"\'\n]+)["\']'),
    'require': re.compile(r'\brequire\s*\(\s*["\']([^"\'\n]+)["\']\s*\)'),
    'dynamic-import': re.compile(r'\bimport\s*\(\s*["\']([^"\'\n]+)["\']\s*\)'),
    'ipc-send': re.compile(r'\b(?:ipcRenderer|ipcMain|webContents)\.(?:send|sendSync|invoke)\s*\(\s*["\']([^"\'\n]+)["\']'),
    'ipc-listen': re.compile(r'\b(?:ipcRenderer|ipcMain)\.(?:on|once|handle)\s*\(\s*["\']([^"\'\n]+)["\']'),
    'event-emit': re.compile(r'\b(?:\.emit|dispatchEvent)\s*\(\s*["\']([^"\'\n]+)["\']'),
    'route': re.compile(r'\b(?:app|router|server)\.(get|post|put|patch|delete|all)\s*\(\s*["\']([^"\'\n]+)["\']'),
    'export-symbol': re.compile(r'\bexport\s+(?:(?:default|declare|abstract|async|const|let|var|type)\s+)*?(?:function|class|interface|type|const|let|var|enum)\s+([A-Za-z_$][\w$]*)'),
    'napi': re.compile(r'["\']([^"\'\n]+\.node)["\']'),
}


def _lexical_no_comments(source: str) -> str:
    """Mask JS comments without modifying string contents or line positions."""
    out = list(source)
    state = 'code'
    i = 0
    while i < len(source):
        c = source[i]
        nxt = source[i+1] if i + 1 < len(source) else ''
        if state == 'code':
            if c == '/' and nxt == '/':
                out[i] = out[i+1] = ' '
                state = 'line'
                i += 2
                continue
            if c == '/' and nxt == '*':
                out[i] = out[i+1] = ' '
                state = 'block'
                i += 2
                continue
            if c in ('"', "'", '`'):
                state = c
        elif state == 'line':
            if c == '\n':
                state = 'code'
            else:
                out[i] = ' '
        elif state == 'block':
            if c == '*' and nxt == '/':
                out[i] = out[i+1] = ' '
                state = 'code'
                i += 2
                continue
            if c != '\n':
                out[i] = ' '
        else:
            if c == '\\':
                i += 2
                continue
            if c == state:
                state = 'code'
        i += 1
    return ''.join(out)


def _id(label: str) -> str:
    return 'n_' + hashlib.sha256(label.encode('utf-8')).hexdigest()[:18]


def _edge_id(left: str, right: str, kind: str, line: int) -> str:
    return 'e_' + hashlib.sha256(f'{left}\0{right}\0{kind}\0{line}'.encode()).hexdigest()[:20]


def _role(name: str, package: dict) -> str:
    name2 = name.lower()
    for key in ('main', 'preload'):
        if package.get(key) == name.lstrip('./'):
            return 'electron-' + key
    if re.search(r'(^|/)(?:preload)(?:\.|/)', name2):
        return 'electron-preload'
    if re.search(r'(^|/)(?:main|background)(?:\.|/)', name2) and 'electron' in str(package).lower():
        return 'electron-main-candidate'
    if 'renderer' in name2:
        return 'renderer-candidate'
    if name2.endswith('.node'):
        return 'native-addon'
    return 'module'


def _read_package(artifact: VirtualArtifact) -> dict:
    possibilities = sorted(n for n in artifact.entries if n.endswith('package.json'))
    for name in possibilities:
        if name.count('/') > 2:
            continue
        try:
            val = strict_json(artifact.read(name, 256 * 1024))
            if isinstance(val, dict):
                return {k: val[k] for k in ('name', 'main', 'module', 'type', 'exports', 'imports', 'browser') if k in val}
        except (ArtifactError, ValueError):
            pass
    return {}


def _resolve(spec: str, owner: str, paths: set[str], package: dict) -> tuple[str | None, str]:
    if spec.startswith('node:'):
        return None, 'node-builtin'
    if spec.startswith('.'):
        bits = owner.split('/')[:-1]
        for seg in spec.split('/'):
            if seg in ('', '.'):
                continue
            if seg == '..':
                if not bits:
                    return None, 'outside-artifact'
                bits.pop()
            else:
                bits.append(seg)
        candidate = '/'.join(bits)
    elif spec.startswith('#'):
        mapping = package.get('imports', {})
        if not isinstance(mapping, dict) or not isinstance(mapping.get(spec), str):
            return None, 'package-import-condition-unresolved'
        candidate = mapping[spec].removeprefix('./')
    elif spec == package.get('name') and isinstance(package.get('main'), str):
        candidate = package['main'].removeprefix('./')
    else:
        return None, 'external-package-or-runtime-resolution'
    # NodeNext TS repositories conventionally spell emitted .js/.mjs/.cjs in
    # their source imports. A fallback link is a lexical candidate, not proof
    # that a configured compiler will resolve it the same way.
    ts_fallback={'.js':('.ts','.tsx','.mts'),'.mjs':('.mts',),
                 '.cjs':('.cts',),'.jsx':('.tsx',)}
    source_alternatives=[]
    for suffix,extensions in ts_fallback.items():
        if candidate.endswith(suffix):
            source_alternatives=[candidate[:-len(suffix)]+ext for ext in extensions]
            break
    possibilities=[candidate,*source_alternatives]
    possibilities.extend(candidate + ext for ext in JS + ('.json', '.node'))
    possibilities.extend(candidate + '/index' + ext for ext in JS + ('.json', '.node'))
    found = [p for p in possibilities if p in paths]
    if len(found) == 1:
        return found[0], 'typescript-source-fallback' if found[0] in source_alternatives else 'file-extension-fallback'
    if found:
        return found[0], 'ambiguous-file-resolution'
    return None, 'missing-or-bundled-module'


def analyze_application(artifact: VirtualArtifact, max_files: int = 2500,
                        max_edges: int = MAX_GRAPH_EDGES) -> dict:
    package = _read_package(artifact)
    max_files = max(1, min(max_files, 5000))
    max_edges = max(1, min(max_edges, MAX_GRAPH_EDGES))
    names = sorted(k for k in artifact.entries if k.lower().endswith(JS))
    included = names[:max_files]
    all_paths = set(artifact.entries)
    graph_nodes: dict[str,dict] = {}
    edges: list[dict] = []
    findings = []
    unknowns = []
    for path in included:
        graph_nodes[_id(path)] = {'node_id':_id(path),'path':path,'role':_role(path,package),
                                  'evidence':'declared-file','size':artifact.entries[path].size}
        try:
            raw = artifact.read(path, MAX_SOURCE)
            source = _lexical_no_comments(raw.decode('utf-8', 'strict'))
        except (ArtifactError, UnicodeError) as exc:
            unknowns.append({'path':path,'reason':f'unreadable JS source: {type(exc).__name__}'})
            continue
        for kind, pattern in PATTERNS.items():
            for match in pattern.finditer(source):
                if len(edges) >= max_edges:
                    break
                line = source.count('\n',0,match.start()) + 1
                if kind == 'export-symbol':
                    sym = match.group(1)
                    if len(sym) > 200:continue
                    key='export:'+path+':'+sym
                    label=_id(key)
                    graph_nodes[label]={'node_id':label,'path':path,'symbol':sym,'role':'export','evidence':'lexical-candidate'}
                    edges.append({'edge_id':_edge_id(_id(path),label,kind,line),'from':_id(path),
                                  'to':label,'kind':'export','line':line,'evidence':'lexical-candidate'})
                    continue
                value = match.group(2) if kind=='route' else match.group(1)
                if not value or len(value)>500:continue
                if kind in ('esm-import','esm-reexport','require','dynamic-import','napi'):
                    resolved, status = _resolve(value,path,all_paths,package)
                    target_label = _id(resolved) if resolved else _id(kind+':'+value)
                    if resolved is None:
                        graph_nodes.setdefault(target_label,{'node_id':target_label,'path':None,'symbol':value,
                                                             'role':'unresolved-reference','evidence':'lexical-candidate'})
                    else:
                        graph_nodes.setdefault(target_label,{'node_id':target_label,'path':resolved,
                                                             'role':_role(resolved,package),'evidence':'declared-file'})
                    edge_kind=kind
                else:
                    target_name = ('route:'+match.group(1).upper()+':'+value if kind=='route' else
                                   'channel:'+value)
                    target_label=_id(target_name)
                    graph_nodes.setdefault(target_label,{'node_id':target_label,'path':None,'symbol':target_name,
                                                         'role':'route' if kind=='route' else 'event-channel',
                                                         'evidence':'lexical-candidate'})
                    status='literal-name'
                    edge_kind=kind
                edges.append({'edge_id':_edge_id(_id(path),target_label,kind,line),'from':_id(path),
                              'to':target_label,'kind':edge_kind,'line':line,
                              'specifier':value,'resolution':status,'evidence':'lexical-candidate'})
            if len(edges) >= max_edges:
                unknowns.append({'path':path,'reason':'edge budget reached'})
                break
        if len(edges) >= max_edges:
            break
    if len(names)>max_files:
        unknowns.append({'reason':'JS module count limit','omitted_count':len(names)-max_files})
    if artifact.skips:
        unknowns.append({'reason':'source inventory had skipped members','skipped_count':len(artifact.skips)})
    return {'format':'application-graph-1', 'source_sha256':artifact.source_sha(),
            'source_kind':artifact.kind, 'package':package,'nodes':sorted(graph_nodes.values(),key=lambda x:x['node_id']),
            'edges':sorted(edges,key=lambda x:x['edge_id']), 'js_files_seen':len(included),
            'unknowns':unknowns,'complete':not unknowns,
            'evidence_level':'Declared file paths and lexical candidates only. Static edges do not prove runtime execution.'}


def trace_feature(graph: dict, query: str, depth: int = 4, direction: str = 'both',
                  max_nodes: int = 150, include_unresolved: bool = True) -> dict:
    if not isinstance(query,str) or not query or len(query)>180:
        raise ArtifactError('trace query must be a nonempty bounded string')
    if direction not in ('out','in','both'):
        raise ArtifactError('invalid graph direction')
    depth=max(0,min(int(depth),12))
    max_nodes=max(1,min(int(max_nodes),MAX_TRACE_NODES))
    nodes={n['node_id']:n for n in graph.get('nodes',[])}
    matches=sorted((n for n in nodes.values() if query.casefold() in
                   ' '.join(str(n.get(k,'')) for k in ('path','symbol','role')).casefold()
                   and (include_unresolved or n['role'] != 'unresolved-reference')), key=lambda x:x['node_id'])
    seeds=[n['node_id'] for n in matches[:min(max_nodes,40)]]
    adjacency=defaultdict(list)
    for edge in graph.get('edges',[]):
        if direction in ('out','both'):
            adjacency[edge['from']].append((edge['to'],edge))
        if direction in ('in','both'):
            adjacency[edge['to']].append((edge['from'],edge))
    work_queue=deque((s,0) for s in seeds)
    visited=set(seeds)
    edges={}
    trunc=False
    while work_queue:
        current,d=work_queue.popleft()
        if d>=depth:continue
        for neighbor,e in sorted(adjacency.get(current,[]),key=lambda pair:pair[1]['edge_id']):
            if len(visited)>=max_nodes and neighbor not in visited:
                trunc=True;continue
            edges[e['edge_id']]=e
            if neighbor not in visited:
                visited.add(neighbor);work_queue.append((neighbor,d+1))
    return {'query':query,'source_sha256':graph.get('source_sha256'),
            'seed_ids':seeds,'seed_match_count':len(matches),'nodes':[nodes[i] for i in sorted(visited)],
            'edges':[edges[i] for i in sorted(edges)], 'truncated':trunc or len(matches)>len(seeds),
            'unknowns':graph.get('unknowns',[]),
            'conclusion_ceiling':'bounded lexical reachability, not verified call path or runtime behavior'}


def compare_applications(before:dict, after:dict, max_items:int=500) -> dict:
    before_nodes={n['path'] for n in before.get('nodes',[]) if n.get('path')}
    after_nodes={n['path'] for n in after.get('nodes',[]) if n.get('path')}
    def shapes(data):
        nodes={node['node_id']: node for node in data.get('nodes',[])}
        result=set()
        for e in data.get('edges',[]):
            src=nodes.get(e['from'],{}).get('path')
            to=nodes.get(e['to'],{})
            if src:
                result.add((src,e['kind'],to.get('path') or to.get('symbol') or '',e.get('specifier','')))
        return result
    bef=shapes(before);aft=shapes(after)
    add=sorted(aft-bef);remove=sorted(bef-aft)
    return {'previous_source_sha256':before.get('source_sha256'),
            'current_source_sha256':after.get('source_sha256'),
            'added_modules':sorted(after_nodes-before_nodes)[:max_items],
            'removed_modules':sorted(before_nodes-after_nodes)[:max_items],
            'added_edges':[list(x) for x in add[:max_items]],
            'removed_edges':[list(x) for x in remove[:max_items]],
            'truncated':any(len(x)>max_items for x in (add,remove,after_nodes-before_nodes,before_nodes-after_nodes)),
            'complete':bool(before.get('complete') and after.get('complete')),
            'unknowns':[x for x in ('previous graph partial' if not before.get('complete') else None,
                                   'current graph partial' if not after.get('complete') else None) if x],
            'claim_ceiling':'changes in a bounded lexical application graph; not behavioral equivalence'}
