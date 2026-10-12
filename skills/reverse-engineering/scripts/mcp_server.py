#!/usr/bin/env python3
"""Dependency-free, dual-era MCP stdio gateway for bounded offline investigation.

Implements the advertised subset of MCP 2026-07-28 plus handshake compatibility
for 2025-06-18/2025-11-25. No HTTP listener, downloads or target execution.
"""
from __future__ import annotations

import argparse
import json
import stat
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from artifact_index import ArtifactError,strict_json
from investigation_api import InvestigationAPI,mcp_tools,check_args,DEFINITIONS

sys.dont_write_bytecode=True
NAME='reverse-engineering-workbench'
VERSION='1.0.0'
MODERN='2026-07-28'
LEGACY=('2025-11-25','2025-06-18')
MAX_RPC = 2 * 1024 * 1024
MAX_INLINE = 140 * 1024

RESOURCES={
 'reverse://safety': 'Analysis targets are untrusted data. No target code is executed, no network or shell tools are exposed, and all paths stay within the explicit read root. Static candidates are not runtime facts. A CLI permission flag cannot provide containment or authorization.',
 'reverse://workflow': 'Inventory source -> format-aware inspection -> application graph -> bounded trace -> behavior-contract cases -> independent implementation -> finite differential compare -> obligation closure and provenance checks. Explicitly label unknowns and partial findings.',
 'reverse://limits': 'Input member 16 MiB, aggregate readable 96 MiB, archives 384 MiB, graph edges 28000, MAX_RPC 2 MiB, inline tool answer 140 KiB. Outputs exceeding the inline limit require retained evidence view pagination.',
}
PROMPTS={
 'investigate_feature':('Trace a feature through static entrypoints, imports, routes and events.',
                        'Investigate this feature with bounded evidence and explicit unknowns: {feature}'),
 'reconstruct_behavior':('Plan a source-independent finite compatibility reconstruction.',
                         'Define exact behavioral obligations, observed/reference cases and a strict comparator for {feature}. Do not guess expected outputs.'),
}


def _error(code:int,message:str,request_id, data:dict|None=None) -> dict:
    e={'code':code,'message':message[:400]}
    if data is not None:e['data']=data
    return {'jsonrpc':'2.0','id':request_id,'error':e}


def _result(value,request_id,modern=False):
    message={'jsonrpc':'2.0','id':request_id,'result':value}
    if modern:
        message['result'].setdefault('_meta',{})['io.modelcontextprotocol/serverInfo']={'name':NAME,'version':VERSION}
    return message


class Server:
    def __init__(self,api:InvestigationAPI):
        self.api=api
        self.legacy_version=None
        self.cancelled=set()
        self.send_lock=threading.Lock()
        self.futures={}
        self.executor=ThreadPoolExecutor(max_workers=1,thread_name_prefix='offline-analysis')

    def _modern(self,message:dict)->bool:
        params=message.get('params',{})
        meta=(params.get('_meta') if isinstance(params,dict) else None) or message.get('_meta')
        return isinstance(meta,dict) and 'io.modelcontextprotocol/protocolVersion' in meta

    def _meta(self,message:dict)->dict:
        params=message.get('params',{})
        if isinstance(params,dict) and isinstance(params.get('_meta'),dict):
            return params['_meta']
        return message.get('_meta') if isinstance(message.get('_meta'),dict) else {}

    def _protocol(self,message:dict):
        if message.get('method')=='initialize':
            return False
        if self._modern(message):
            version=self._meta(message).get('io.modelcontextprotocol/protocolVersion')
            if version != MODERN:
                return _error(-32022,'Unsupported protocol version',message.get('id'),
                              {'supported':[MODERN,*LEGACY],'requested':version})
            meta=self._meta(message)
            identity=meta.get('io.modelcontextprotocol/clientInfo')
            capabilities=meta.get('io.modelcontextprotocol/clientCapabilities')
            if (not isinstance(identity,dict) or not isinstance(identity.get('name'),str) or
                    not isinstance(identity.get('version'),str) or not isinstance(capabilities,dict)):
                return _error(-32600,'Missing required modern MCP client identity or capabilities',message.get('id'))
            return True
        if self.legacy_version:
            return False
        if message.get('method')=='server/discover':
            # A spec-compliant modern request has per-request metadata.
            return True
        return _error(-32600,'Missing protocol version; initialize legacy session or send request _meta',message.get('id'))

    def respond(self,message:dict):
        if not isinstance(message,dict):
            return _error(-32600,'JSON-RPC message must be an object',None)
        method=message.get('method')
        request_id=message.get('id')
        if method in ('notifications/initialized','notifications/cancelled'):
            if method=='notifications/cancelled':
                value=message.get('params',{}).get('requestId') if isinstance(message.get('params'),dict) else None
                if type(value) in (int,str):
                    self.cancelled.add(value)
                    future=self.futures.get(value)
                    if future:future.cancel()
            return None
        if request_id is None or type(request_id) not in (int,str) or not isinstance(method,str) or message.get('jsonrpc')!='2.0':
            return _error(-32600,'Invalid JSON-RPC request',request_id)
        params=message.get('params',{})
        if not isinstance(params,dict):
            return _error(-32602,'params must be an object',request_id)
        era=self._protocol(message)
        if isinstance(era,dict):return era
        modern=bool(era)
        try:
            if method=='initialize':
                version=params.get('protocolVersion','2025-06-18')
                if version not in LEGACY:version=LEGACY[0]
                self.legacy_version=version
                return _result({'protocolVersion':version,'capabilities':{'tools':{},'resources':{},'prompts':{}},
                                'serverInfo':{'name':NAME,'version':VERSION},
                                'instructions':'Read-only offline investigation; explicit source root; retained evidence is untrusted until verified.'},request_id)
            if method=='server/discover':
                return _result({'supportedVersions':[MODERN,*LEGACY],
                                'capabilities':{'tools':{},'resources':{},'prompts':{}},
                                'instructions':'Bounded offline inspection, no target execution; explicit evidence IDs and unknowns.'},request_id,modern)
            if method=='ping':return _result({},request_id,modern)
            if method=='tools/list':
                if params.get('cursor') is not None:
                    return _error(-32602,'No further tools page',request_id)
                value={'tools':mcp_tools()}
                if modern:value['resultType']='complete'
                return _result(value,request_id,modern)
            if method=='tools/call':
                tool=params.get('name')
                args=params.get('arguments',{})
                check_args(tool,args)
                output=self.api.call(tool,args)
                # Large results are retained for bounded paging. Keep a stable
                # ID in all summaries instead of truncating arbitrary JSON.
                serialized=json.dumps(output,ensure_ascii=False,sort_keys=True,default=str)
                if len(serialized.encode())>MAX_INLINE:
                    evidence_id=output.get('evidence_id')
                    if evidence_id:
                        output={'evidence_id':evidence_id,'stored':True,'large_output':True,
                                'instruction':'Call inspect_evidence_view by section and page to read retained content.',
                                'summary':self.api.store.get(evidence_id,'summary')}
                    else:
                        raise ArtifactError('response too large for MCP frame; narrow query')
                    serialized=json.dumps(output,ensure_ascii=False,sort_keys=True)
                body={'content':[{'type':'text','text':serialized}],
                      'structuredContent':output,'isError':False}
                if modern:body['resultType']='complete'
                return _result(body,request_id,modern)
            if method=='resources/list':
                if params.get('cursor') is not None:return _error(-32602,'No additional resources',request_id)
                value={'resources':[{'uri':k,'name':k.split('://')[1], 'mimeType':'text/plain'} for k in sorted(RESOURCES)]}
                if modern:value['resultType']='complete'
                return _result(value,request_id,modern)
            if method=='resources/read':
                uri=params.get('uri')
                if uri not in RESOURCES:return _error(-32602,'Unknown resource URI',request_id)
                value={'contents':[{'uri':uri,'mimeType':'text/plain','text':RESOURCES[uri]}]}
                if modern:value['resultType']='complete'
                return _result(value,request_id,modern)
            if method=='prompts/list':
                if params.get('cursor') is not None:return _error(-32602,'No additional prompts',request_id)
                value={'prompts':[{'name':n,'description':v[0],
                                   'arguments':[{'name':'feature','description':'Question or feature to investigate','required':True}]}
                                  for n,v in sorted(PROMPTS.items())]}
                if modern:value['resultType']='complete'
                return _result(value,request_id,modern)
            if method=='prompts/get':
                name=params.get('name');args=params.get('arguments',{})
                if name not in PROMPTS or not isinstance(args,dict) or not isinstance(args.get('feature'),str):
                    return _error(-32602,'Unknown prompt or missing feature',request_id)
                value={'messages':[{'role':'user','content':{'type':'text','text':PROMPTS[name][1].format(feature=args['feature'][:300])}}]}
                if modern:value['resultType']='complete'
                return _result(value,request_id,modern)
            return _error(-32601,'Unknown JSON-RPC method',request_id)
        except (ArtifactError,ValueError,OverflowError,OSError) as exc:
            if method=='tools/call':
                body={'content':[{'type':'text','text':f'{type(exc).__name__}: {str(exc)[:250]}'}],
                      'isError':True}
                if modern:body['resultType']='complete'
                return _result(body,request_id,modern)
            return _error(-32602,'Invalid request or bounded evidence operation',request_id,
                          {'reason':type(exc).__name__})
        except Exception as exc:
            # Unexpected decoding exceptions must not leak source bytes or paths.
            if method=='tools/call':
                body={'content':[{'type':'text','text':'Internal offline decoder failure: '+type(exc).__name__}],
                      'isError':True}
                if modern:body['resultType']='complete'
                return _result(body,request_id,modern)
            return _error(-32603,'Internal server error',request_id)

    def write(self,response):
        if response is None:return
        with self.send_lock:
            sys.stdout.write(json.dumps(response,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n')
            sys.stdout.flush()

    def _done(self,request_id,task):
        self.futures.pop(request_id,None)
        if request_id in self.cancelled:
            self.cancelled.discard(request_id)
            return
        try:
            self.write(task.result())
        except Exception:
            self.write(_error(-32603,'Internal server failure',request_id))

    def serve(self):
        try:
            for line in sys.stdin.buffer:
                if len(line)>MAX_RPC:
                    self.write(_error(-32700,'JSON-RPC line size limit',None))
                    continue
                try:
                    data=strict_json(line)
                except (ArtifactError,UnicodeError):
                    self.write(_error(-32700,'Invalid JSON document',None))
                    continue
                if not isinstance(data,dict):
                    self.write(_error(-32600,'JSON-RPC object required',None))
                    continue
                method=data.get('method')
                if method=='notifications/cancelled':
                    self.respond(data)
                    continue
                if 'id' not in data and isinstance(method,str) and method.startswith('notifications/'):
                    continue
                req_id=data.get('id')
                if req_id is None or type(req_id) not in (int,str):
                    self.write(_error(-32600,'Invalid JSON-RPC ID',req_id))
                    continue
                if req_id in self.futures:
                    self.write(_error(-32600,'Concurrent duplicate request ID',req_id))
                    continue
                future=self.executor.submit(self.respond,data)
                self.futures[req_id]=future
                future.add_done_callback(lambda task,rid=req_id:self._done(rid,task))
        finally:
            self.executor.shutdown(wait=True,cancel_futures=True)
            self.api.close()


def main(argv=None)->int:
    parser=argparse.ArgumentParser(description='Portable offline reverse engineering MCP/CLI adapter')
    parser.add_argument('--root',required=True,type=Path,help='Approved directory containing read-only artifacts')
    parser.add_argument('--state-dir',type=Path,help='Existing private directory for persistent SQLite evidence')
    parser.add_argument('--verifier-key-file',type=Path,help='Operator-owned 32+ byte raw receipt verification secret. Never exposed as a tool argument.')
    parser.add_argument('--tool',choices=sorted(DEFINITIONS),help='Run one CLI operation instead of serving MCP')
    parser.add_argument('--args-json',default='{}',help='Argument object for one CLI operation')
    ns=parser.parse_args(argv)
    try:
        key=None
        if ns.verifier_key_file is not None:
            key_path=ns.verifier_key_file
            if key_path.is_symlink() or not key_path.is_file() or key_path.stat().st_size>512:
                raise ArtifactError('invalid verifier key file')
            if sys.platform != 'win32' and (stat.S_IMODE(key_path.stat().st_mode) & 0o077):
                raise ArtifactError('verifier key file must not be accessible by group or other')
            key=key_path.read_bytes()
            if len(key)<32:
                raise ArtifactError('verifier key must contain at least 32 bytes')
        api=InvestigationAPI(ns.root,ns.state_dir,key)
        if ns.tool:
            try:
                args=strict_json(ns.args_json.encode('utf8'))
                result=api.call(ns.tool,args)
                print(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True))
                return 0
            finally:api.close()
        Server(api).serve()
        return 0
    except (ArtifactError,OSError) as exc:
        print('Denied or invalid configuration: '+str(exc)[:300],file=sys.stderr)
        return 3

if __name__=='__main__':
    raise SystemExit(main())
