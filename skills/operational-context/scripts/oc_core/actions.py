"""Conservative action-result reference cache. No command execution or restoration."""
from __future__ import annotations
import os
from .common import HASH_RE, RuntimeFault, canonical, confined, fields, file_hash, read_bytes, safe_text, sha, strict_json


def inventory(cache, roots: list[str]) -> dict:
    if not isinstance(roots,list) or not 1 <= len(roots) <= 32 or any(not isinstance(p,str) for p in roots) or len(set(roots)) != len(roots):
        raise RuntimeFault("INVALID_INPUT", "Declare 1..32 distinct file/directory input roots.")
    result = {}
    total = 0
    for rel in sorted(roots):
        root=confined(cache.workspace,rel)
        if not root.exists() or rel.startswith('.rhapsodia/cache'):
            raise RuntimeFault("INVALID_INPUT", "Inputs must exist outside the operational cache.")
        if root.is_file():
            files=[root]
        else:
            files=[]
            for directory,dirs,names in os.walk(root,followlinks=False):
                # Never silently skip a protected or redirected dependency.
                for name in dirs+names:
                    path=confined(cache.workspace,(os.path.relpath(os.path.join(directory,name),cache.workspace)).replace(os.sep,'/'))
                    if path.is_file():
                        files.append(path)
                    if len(files)>4096:
                        raise RuntimeFault("INPUT_TOO_LARGE", "Input closure exceeds 4096 files.")
        for path in files:
            relative=path.relative_to(cache.workspace).as_posix()
            total += path.stat().st_size
            if total>128*1024*1024 or len(result)>=4096 and relative not in result:
                raise RuntimeFault("INPUT_TOO_LARGE", "Input closure exceeds bounded hashing limits.")
            result[relative]=file_hash(path)
    return dict(sorted(result.items()))


def action_key(cache, request: dict) -> dict:
    required={'task_class','argv','input_roots','toolchain_digest','environment_digest','config_digest','policy_digest',
              'closure_complete','hermetic','network','requires_fresh','requires_independent'}
    fields(request,required,{'cwd'})
    if not isinstance(request['task_class'],str) or request['task_class'] not in {'build','codegen','lint','test','read'}:
        raise RuntimeFault('INVALID_INPUT','Unsupported action class.')
    argv=request['argv']
    if not isinstance(argv,list) or not 1<=len(argv)<=128:
        raise RuntimeFault('INVALID_INPUT','argv must be an exact bounded array; it is never executed.')
    for arg in argv:
        safe_text(arg,2048)
    for name in ('toolchain_digest','environment_digest','config_digest','policy_digest'):
        if not isinstance(request[name],str) or not HASH_RE.fullmatch(request[name]):
            raise RuntimeFault('INVALID_INPUT','Explicit toolchain, environment, configuration and policy digests are required.')
    for name in ('closure_complete','hermetic','network','requires_fresh','requires_independent'):
        if type(request[name]) is not bool:
            raise RuntimeFault('INVALID_INPUT','Action policy flags must be booleans.')
    cwd=request.get('cwd','.')
    if cwd!='.' and not confined(cache.workspace,cwd).is_dir():
        raise RuntimeFault('INVALID_INPUT','Working directory must exist inside the workspace.')
    pins=inventory(cache,request['input_roots'])
    key={'schema':'action-key/v1','scope':cache.scope,'task_class':request['task_class'],'argv_digest':sha(argv),
         'cwd':cwd,'input_roots':sorted(request['input_roots']),'inputs':pins,
         **{n:request[n] for n in required if n not in {'argv','input_roots','task_class'}}}
    reasons=[]
    if not request['closure_complete']:reasons.append('input-closure-unproven')
    if not request['hermetic'] or request['network']:reasons.append('non-hermetic-or-network')
    if request['requires_fresh'] or request['task_class']=='test':reasons.append('fresh-validation-required')
    if request['requires_independent']:reasons.append('independent-verification-required')
    return {'schema':'action-eligibility/v1','action_digest':sha(key),'key':key,'cache_eligible':not reasons,
            'reasons':reasons,'authority':'caller-attested-reference-only','command_executed':False}


def store_result(cache, request: dict) -> dict:
    fields(request,{'action','receipt_path'})
    action=action_key(cache,request['action'])
    if not action['cache_eligible']:
        raise RuntimeFault('CACHE_INELIGIBLE','Action requires fresh proof or lacks a complete hermetic input declaration.')
    receipt_path=confined(cache.workspace,request['receipt_path'])
    receipt=strict_json(read_bytes(receipt_path))
    fields(receipt,{'schema','producer','action_digest','status','output_files'})
    if receipt['schema']!='action-result/v1' or (not isinstance(receipt['producer'],str) or receipt['producer'] not in {'magia','user'}) or receipt['action_digest']!=action['action_digest'] or receipt['status']!='passed':
        raise RuntimeFault('INVALID_RECEIPT','A matching successful caller-owned action-result/v1 receipt is required.')
    outputs=receipt['output_files']
    if not isinstance(outputs,dict) or not 1<=len(outputs)<=128:
        raise RuntimeFault('INVALID_RECEIPT','Declare 1..128 output files.')
    for rel,pin in outputs.items():
        if not isinstance(pin,str) or not HASH_RE.fullmatch(pin) or file_hash(confined(cache.workspace,rel))!=pin:
            raise RuntimeFault('STALE_OUTPUT','Every output must exist with its exact receipt hash.')
    value={'action_digest':action['action_digest'],'key':action['key'],'receipt_path':request['receipt_path'],
           'receipt_sha256':file_hash(receipt_path),'output_files':outputs,'producer':receipt['producer']}
    key=cache.put('action',value)
    return {'status':'stored','id':key,'action_digest':action['action_digest'],'domain_approval':False}


def lookup(cache, request: dict) -> dict:
    fields(request,{'action'},{'id'})
    action=action_key(cache,request['action'])
    miss={'status':'miss','action_digest':action['action_digest'],'reasons':action['reasons'],'domain_approval':False}
    if not action['cache_eligible']:
        return dict(miss,status='bypass')
    for key in ([request['id']] if 'id' in request else cache.keys('action')):
        try:
            value=cache.get('action',key)
            if value['action_digest']!=action['action_digest'] or value['key']!=action['key']:
                continue
            if file_hash(confined(cache.workspace,value['receipt_path']))!=value['receipt_sha256']:
                continue
            if any(file_hash(confined(cache.workspace,p))!=h for p,h in value['output_files'].items()):
                continue
            return {'status':'hit','id':key,'action_digest':action['action_digest'],'outputs':value['output_files'],
                    'receipt_path':value['receipt_path'],'reuse_policy':'reference-only','domain_approval':False,
                    'notice':'Owner must accept input completeness and reuse policy; no fresh or independent gate is satisfied.'}
        except (RuntimeFault,OSError,KeyError,TypeError):
            continue  # Corrupt/disappeared disposable cache must never become a hit.
    return miss
