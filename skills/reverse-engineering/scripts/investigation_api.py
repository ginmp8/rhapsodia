#!/usr/bin/env python3
"""Typed operations used by both CLI and MCP; explicit source and state roots."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from artifact_index import ArtifactError, VirtualArtifact, digest, resolve_scoped
from artifact_reports import inspect_binary,inspect_apple_bundle
from application_graph import analyze_application,trace_feature,compare_applications
from reconstruction_contract import assess_obligations,generate_obligations,compare_partial_order
from investigation_store import EvidenceStore, canonical


# JSON Schema contracts are intentionally small, typed and stable; no universal
# shell/HTTP/code execution endpoint is available through this API.
DEFINITIONS={
 'inventory_source':('Read bounded source inventory, ZIP/TAR/ASAR without extraction.',
    {'path':'string','offset':'integer','limit':'integer'},['path']),
 'analyze_application':('Build an offline JS/TS/Electron graph with unresolved edges.',
    {'path':'string','max_files':'integer','max_edges':'integer'},['path']),
 'trace_application':('Trace a named module, exported symbol, event or route within a saved graph.',
    {'evidence_id':'string','query':'string','direction':'string','depth':'integer','max_nodes':'integer'},['evidence_id','query']),
 'compare_applications':('Diff two retained application graphs.',
    {'before_evidence_id':'string','after_evidence_id':'string'},['before_evidence_id','after_evidence_id']),
 'inspect_artifact':('Decode a selected file/member using bounded offline format-aware parsing.',
    {'path':'string','member':'string','mode':'string'},['path']),
 'inspect_apple_bundle':('Read declared Apple Info.plist metadata without executing an app.',
    {'path':'string'},['path']),
 'query_evidence':('Page retained evidence summaries by source or kind.',
    {'kind':'string','artifact_sha256':'string','offset':'integer','limit':'integer'},[]),
 'inspect_evidence_view':('Read a stable saved evidence section/page with explicit identity.',
    {'evidence_id':'string','section':'string','offset':'integer','limit':'integer'},['evidence_id']),
 'export_evidence_bundle':('Export a hash-checked evidence bundle; writes only inside configured state workspace.',
    {'filename':'string'},['filename']),
 'import_evidence_bundle':('Verify and import a bundle from the authorized read root; no trust elevation.',
    {'path':'string'},['path']),
 'build_reconstruction_ledger':('Evaluate finite implementation obligations against binding/receipt metadata.',
    {'graph_evidence_id':'string','obligations':'array','bindings':'array','verification_records':'array'},[]),
 'compare_partial_order':('Compare two event DAGs without falsely imposing a total order.',
    {'reference':'object','candidate':'object'},['reference','candidate']),
 'detect_capabilities':('Show portable parsers, optional manual adapters and authority limits.',
    {},[]),
}


def schema(properties:dict,required:list)->dict:
    return {'type':'object','properties':{k:{'type':kind} for k,kind in properties.items()},
            'required':required,'additionalProperties':False}


def mcp_tools()->list[dict]:
    return [{'name':key,'title':key.replace('_',' ').title(), 'description':detail[0],
             'inputSchema':schema(detail[1],detail[2]),
             'annotations':{'readOnlyHint':key in ('detect_capabilities','query_evidence','inspect_evidence_view')}}
             for key,detail in sorted(DEFINITIONS.items())]


def check_args(tool:str,values:dict)->dict:
    if tool not in DEFINITIONS:raise ArtifactError('unknown named analysis tool')
    if not isinstance(values,dict):raise ArtifactError('tool arguments must be an object')
    _,properties,required=DEFINITIONS[tool]
    if any(k not in properties for k in values):raise ArtifactError('unsupported tool argument')
    if any(k not in values for k in required):raise ArtifactError('missing required tool argument')
    for k,v in values.items():
        kind=properties[k]
        matches={'string':type(v) is str,'integer':type(v) is int,'array':isinstance(v,list),
                 'object':isinstance(v,dict)}
        if not matches[kind]:raise ArtifactError('invalid type for '+k)
        if kind=='string' and len(v)>2000:raise ArtifactError('argument size budget exceeded')
        if kind=='array' and len(v)>1500:raise ArtifactError('argument item budget exceeded')
    return values


class InvestigationAPI:
    def __init__(self,root:Path,state:Path|None=None,trusted_verifier_key:bytes|None=None):
        if not root.is_dir() or root.is_symlink():
            raise ArtifactError('--root must identify a real directory')
        self.root=root.resolve(strict=True)
        self.state=None
        if state is not None:
            if state.is_symlink() or not state.is_dir():
                raise ArtifactError('--state-dir must already exist and not be a symlink')
            self.state=state.resolve(strict=True)
        if trusted_verifier_key is not None and (not isinstance(trusted_verifier_key,bytes) or len(trusted_verifier_key)<32):
            raise ArtifactError('invalid independent receipt verifier key')
        self.trusted_verifier_key=trusted_verifier_key
        self.store=EvidenceStore((self.state/'investigations.sqlite3') if self.state else None)

    def close(self):self.store.close()

    def _path(self,path:str)->Path:
        return resolve_scoped(self.root,path)

    def _artifact(self,path:str)->VirtualArtifact:
        return VirtualArtifact(self._path(path))

    def _graph(self,evidence_id:str)->dict:
        record=self.store.get(evidence_id,'complete')
        if record['kind']!='application_graph':
            raise ArtifactError('selected evidence is not an application graph')
        return record['data']

    def _save(self,kind:str,source_sha:str,result:dict,level:str='declared')->dict:
        descriptor=self.store.put(kind,source_sha,result,level)
        # Large graph payloads remain in SQLite and are always paged.
        if kind=='application_graph':
            return {**descriptor,'source_kind':result['source_kind'],'node_count':len(result['nodes']),
                    'edge_count':len(result['edges']),'js_files_seen':result['js_files_seen'],
                    'complete':result['complete'],'unknowns':result['unknowns'][:35],
                    'next_action':'trace_application with evidence_id, or inspect_evidence_view by section'}
        return {**descriptor,'result':result}

    def call(self,tool:str,arguments:dict|None=None)->dict:
        args=check_args(tool,arguments if arguments is not None else {})
        if tool=='detect_capabilities':
            return {'core':'python-3.10+-stdlib','formats':['directories','zip','tar','asar','js','ts','electron',
                   'pe','elf','mach-o','dotnet-cil','jvm','dex','apk','wasm','evm','har','openapi','sourcemap',
                   'apple-plist','binary-signatures'],
                   'interop':['MCP stdio 2026-07-28','MCP stdio 2025-11-25/2025-06-18','standalone CLI'],
                   'external_engines':'ILSpy/JADX/Ghidra/Kaitai/Roslyn/browser/LLDB/JEB require separate approval and tools.',
                   'authority':'static only via this MCP. Runtime oracles are intentionally not exposed.',
                   'signed_receipt_verifier':self.trusted_verifier_key is not None,
                   'read_root':str(self.root),'persistent':self.state is not None}
        if tool=='inventory_source':
            a=self._artifact(args['path'])
            result=a.inventory(args.get('offset',0),args.get('limit',100))
            return self._save('inventory',result['source_sha256'],result)
        if tool=='analyze_application':
            a=self._artifact(args['path'])
            result=analyze_application(a,args.get('max_files',2500),args.get('max_edges',10000))
            return self._save('application_graph',result['source_sha256'],result,'lexical_candidate')
        if tool=='trace_application':
            source=self._graph(args['evidence_id'])
            result=trace_feature(source,args['query'],args.get('depth',4),args.get('direction','both'),
                                 args.get('max_nodes',100))
            return self._save('feature_trace',source['source_sha256'],result,'lexical_candidate')
        if tool=='compare_applications':
            left=self._graph(args['before_evidence_id']);right=self._graph(args['after_evidence_id'])
            result=compare_applications(left,right)
            return self._save('application_comparison',right['source_sha256'],result,'inferred')
        if tool=='inspect_apple_bundle':
            a=self._artifact(args['path'])
            result=inspect_apple_bundle(a)
            return self._save('artifact_report',result['source_sha256'],result)
        if tool=='inspect_artifact':
            a=self._artifact(args['path'])
            member=args.get('member')
            if member is None:
                if len(a.entries)!=1:
                    raise ArtifactError('select a member from inventory_source for a multi-file artifact')
                member=next(iter(a.entries))
            raw=a.read(member,16*1024*1024)
            mode=args.get('mode','auto')
            if mode in ('pe-resources','elf-notes','auto') and (raw[:4]==b'\x7fELF' or raw.startswith(b'MZ')):
                result=inspect_binary(raw,mode)
            elif mode in ('pe-resources','elf-notes'):
                result=inspect_binary(raw,mode)
            else:
                from workbench import route, inspect_bytes
                actual=route(member,raw[:8192])
                if actual is None:
                    result=inspect_binary(raw,'auto')
                else:
                    try:
                        result=inspect_bytes(member,raw,actual)
                    except Exception as exc:
                        result={'format':actual,'complete':False,
                                'unknowns':['decoder refused input: '+type(exc).__name__],
                                'evidence_level':'format recognized but semantic decoding incomplete'}
            result['member_sha256']=digest(raw)
            result['member_name']=member
            return self._save('binary_report',a.source_sha(),result)
        if tool=='query_evidence':
            return self.store.query(args.get('kind'),args.get('artifact_sha256'),
                                    args.get('offset',0),args.get('limit',60))
        if tool=='inspect_evidence_view':
            return self.store.get(args['evidence_id'],args.get('section','summary'),
                                  args.get('offset',0),args.get('limit',80))
        if tool=='export_evidence_bundle':
            if self.state is None:
                raise ArtifactError('export requires explicit --state-dir')
            filename=args['filename']
            if not filename.endswith('.json') or '/' in filename or '\\' in filename or filename in ('.json','..json'):
                raise ArtifactError('export filename must be a simple .json basename')
            output=self.state/filename
            if output.is_symlink() or output.exists():
                raise ArtifactError('refuse to overwrite existing bundle')
            blob=canonical(self.store.export())+b'\n'
            with output.open('xb') as file:file.write(blob)
            return {'path':str(output),'sha256':digest(blob),'bytes':len(blob)}
        if tool=='import_evidence_bundle':
            path=self._path(args['path'])
            if not path.is_file() or path.stat().st_size>80*1024*1024:
                raise ArtifactError('bundle must be bounded regular file')
            return self.store.import_bundle(path.read_bytes())
        if tool=='build_reconstruction_ledger':
            graph=self._graph(args['graph_evidence_id']) if args.get('graph_evidence_id') else None
            obligations=args.get('obligations')
            if obligations is None:
                obligations=generate_obligations(graph) if graph else []
            result=assess_obligations(obligations,args.get('bindings',[]),args.get('verification_records',[]),
                                     graph.get('unknowns',[]) if graph else [],self.trusted_verifier_key)
            sha=graph['source_sha256'] if graph else '0'*64
            return self._save('obligation_ledger',sha,result,'inferred')
        if tool=='compare_partial_order':
            result=compare_partial_order(args['reference'],args['candidate'])
            return self._save('comparison',digest(canonical(args['reference'])),result,'inferred')
        raise ArtifactError('unsupported tool name')
