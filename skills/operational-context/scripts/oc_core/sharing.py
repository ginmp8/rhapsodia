"""Explicit pointer exchange and cooperative work leases; never authority transfer."""
from __future__ import annotations
import hmac
import time
import uuid
from .common import HASH_RE, RuntimeFault, atomic_write, bounded, canonical, confined, fields, number, read_bytes, safe_text, sha, strict_json
from .registry import freshness


def export_refs(cache, request: dict) -> dict:
    fields(request,{'kind','ids','approved'},{'budget_bytes'})
    if request['approved'] is not True or (not isinstance(request['kind'],str) or request['kind'] not in {'artifact','evidence'}):
        raise RuntimeFault('APPROVAL_REQUIRED','Cross-workspace metadata export must be explicitly approved.')
    if not isinstance(request['ids'],list) or not 1<=len(request['ids'])<=64:
        raise RuntimeFault('INVALID_INPUT','Select 1..64 exact reference IDs; no global export.')
    if any(not isinstance(k,str) for k in request['ids']) or len(set(request['ids'])) != len(request['ids']):
        raise RuntimeFault('INVALID_INPUT','Reference IDs must be distinct strings.')
    records=[]
    for key in request['ids']:
        value=cache.get(request['kind'],key)
        if freshness(cache,value)!='current':raise RuntimeFault('STALE_REFERENCE','Only current local references may be exported.')
        records.append({'source_id':key,'kind':request['kind'],'content_sha256':value['sha256']})
    body={'schema':'reference-exchange/v1','source_scope':cache.scope,'records':records,
          'authority':'untrusted-reference-only','paths_included':False,'expires_at':int(time.time())+3600}
    return bounded({**body,'exchange_id':sha(body)},number(request.get('budget_bytes',8192),128,65536))


def import_refs(cache, request: dict) -> dict:
    fields(request,{'exchange','approved','allowed_source_scope'})
    if request['approved'] is not True:
        raise RuntimeFault('APPROVAL_REQUIRED','Cross-workspace import must be explicitly approved.')
    value=request['exchange']
    fields(value,{'schema','source_scope','records','authority','paths_included','expires_at','exchange_id','output_bytes'})
    body={k:v for k,v in value.items() if k not in {'exchange_id','output_bytes'}}
    if value['schema']!='reference-exchange/v1' or sha(body)!=value['exchange_id'] or value['source_scope']!=request['allowed_source_scope']:
        raise RuntimeFault('INVALID_EXCHANGE','Exchange identity or explicitly allowlisted source differs.')
    if not isinstance(value['source_scope'],str) or not HASH_RE.fullmatch(value['source_scope']) or value['authority']!='untrusted-reference-only' or value['paths_included'] is not False:
        raise RuntimeFault('INVALID_EXCHANGE','Unsafe exchange metadata.')
    if value['output_bytes'] != len(canonical(value)):
        raise RuntimeFault('INVALID_EXCHANGE','Exchange byte accounting differs from its payload.')
    expiry=number(value['expires_at'],1,10**11)
    if not time.time()<expiry<=time.time()+3605:
        raise RuntimeFault('EXPIRED_EXCHANGE','Exchange is expired or beyond the one-hour import window.')
    if not isinstance(value['records'],list) or not 1<=len(value['records'])<=64:
        raise RuntimeFault('INVALID_EXCHANGE','Invalid exchange record count.')
    for item in value['records']:
        fields(item,{'source_id','kind','content_sha256'})
        if (not isinstance(item['kind'],str) or item['kind'] not in {'artifact','evidence'}) or any(not isinstance(item[k],str) or not HASH_RE.fullmatch(item[k]) for k in ('source_id','content_sha256')):
            raise RuntimeFault('INVALID_EXCHANGE','Reference identities must be exact SHA-256 values.')
    key=cache.put('foreign',dict(body,import_status='quarantined',locally_verified=False))
    return {'status':'quarantined','id':key,'automatic_reuse':False,'domain_approval':False,
            'notice':'Imported pointers never enter local evidence/action lookups. Resolve matching local bytes through an authorized owner.'}


def lease(cache, request: dict) -> dict:
    fields(request,{'operation','resource','holder'},{'ttl_seconds','token','generation'})
    op=request['operation']
    if not isinstance(op,str) or op not in {'acquire','renew','release','check'}:raise RuntimeFault('INVALID_INPUT','Unknown lease operation.')
    resource=safe_text(request['resource'],256);holder=safe_text(request['holder'],128)
    if 'generation' in request:number(request['generation'],1,10**12)
    if 'token' in request:
        token=safe_text(request['token'],32)
        if len(token)!=32 or any(c not in '0123456789abcdef' for c in token):
            raise RuntimeFault('INVALID_INPUT','Lease token must be the exact issued hexadecimal nonce.')
    rel='leases/'+sha(resource)+'.json'
    if op=='check':
        path=confined(cache.root,rel)
        if not path.exists():return {'status':'unheld','advisory_only':True}
        state=strict_json(read_bytes(path))
        _lease_shape(state,resource)
        valid=_owns(state,request) and state['expires_at']>time.time()
        return {'status':'current' if valid else 'not-owned-or-expired','generation':state['generation'],'advisory_only':True}
    ttl=number(request.get('ttl_seconds',60),1,300)
    with cache.writer():
        path=confined(cache.root,rel,write=True)
        state=strict_json(read_bytes(path)) if path.exists() else None
        now=time.time()
        if state is not None:_lease_shape(state,resource)
        if op=='acquire':
            if state is not None and state['expires_at']>now:
                raise RuntimeFault('LEASE_HELD','Existing live cooperative lease cannot be stolen.',5)
            state={'schema':'work-lease/v1','resource':resource,'holder':holder,'token':uuid.uuid4().hex,
                   'generation':state['generation']+1 if state else 1,'expires_at':now+ttl}
        else:
            if state is None or not _owns(state,request) or state['expires_at']<=now:
                raise RuntimeFault('STALE_LEASE','Token, holder, generation or expiry changed; do not write.',4)
            state=dict(state,expires_at=now+ttl if op=='renew' else 0)
        atomic_write(cache.root,rel,canonical(state))
    return {**state,'status':'released' if op=='release' else 'held','advisory_only':True,
            'notice':'This coordinates consenting workers only. It does not authorize edits or lock native applications; canonical single-writer rules still apply.'}


def _lease_shape(state,resource):
    fields(state,{'schema','resource','holder','token','generation','expires_at'})
    if state['schema']!='work-lease/v1' or state['resource']!=resource or not isinstance(state['token'],str) or len(state['token'])!=32:
        raise RuntimeFault('CORRUPT_LEASE','Lease shape or identity changed.')
    safe_text(state['holder'],128);number(state['generation'],1,10**12)
    if isinstance(state['expires_at'],bool) or not isinstance(state['expires_at'],(int,float)):
        raise RuntimeFault('CORRUPT_LEASE','Invalid expiry.')


def _owns(state,request):
    token=request.get('token')
    return isinstance(token,str) and hmac.compare_digest(token,state['token']) and state['holder']==request['holder'] and state['generation']==request.get('generation')


def graph(cache, request: dict) -> dict:
    fields(request,{'kind','ids'})
    if (not isinstance(request['kind'],str) or request['kind'] not in {'artifact','evidence'}) or not isinstance(request['ids'],list) or not 1<=len(request['ids'])<=64:
        raise RuntimeFault('INVALID_INPUT','Select at most 64 explicit artifact/evidence IDs.')
    if any(not isinstance(k,str) for k in request['ids']) or len(set(request['ids'])) != len(request['ids']):
        raise RuntimeFault('INVALID_INPUT','Graph IDs must be distinct strings.')
    nodes=[];edges=[];seen=set();scope='operational:'+cache.scope[:24]
    for key in request['ids']:
        value=cache.get(request['kind'],key)
        evidence=[{'provenance':'EXTRACTED','confidence':1.0,'status':'accepted','locator':'operational-object:'+key,
                   'details':{'meaning':'Index membership and content pin only; not execution approval.'}}]
        nodes.append({'id':scope+':'+key,'kind':request['kind'].title(),'label':request['kind'],
                      'properties':{'sha256':value['sha256'],'freshness':freshness(cache,value),'owner':value['owner']},'evidence':evidence})
        if len(edges) + len(value.get('candidate_files',{})) > 2048:
            raise RuntimeFault('BUDGET_EXCEEDED','Select fewer evidence records for graph export.')
        for path,pin in sorted(value.get('candidate_files',{}).items()):
            target=scope+':content:'+pin
            if target not in seen:
                seen.add(target)
                nodes.append({'id':target,'kind':'Content','label':'Pinned candidate content','properties':{'sha256':pin},'evidence':evidence})
            edges.append({'source':scope+':'+key,'target':target,'relation':'references','directed':True,'evidence':evidence})
    body={'schema_version':'graph-patch-v1','source':{'uri':'operational-context:'+cache.scope,'kind':'operational-index',
           'content_hash':sha({'nodes':nodes,'edges':edges}),'metadata':{'projection':'reference-only','absolute_paths_included':False}},'nodes':nodes,'edges':edges}
    if len(canonical(body))>1024*1024:raise RuntimeFault('BUDGET_EXCEEDED','Select fewer records for graph export.')
    return body
