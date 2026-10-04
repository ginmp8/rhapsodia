#!/usr/bin/env python3
"""Validate Prompt Architect execution-environment evidence with stdlib only."""
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path
from typing import Any
sys.dont_write_bytecode = True

HEX=set('0123456789abcdef')
ROOT_KEYS={'profile_version','run_id','host','runtime','model','tools','dependencies','locale','timezone','cache_policy','concurrency_policy','hermeticity','controller_identity','inputs','outputs'}

def error(code:str, subject:str, evidence:Any)->dict[str,Any]:
    return {'code':code,'severity':'error','subject':subject,'evidence':evidence}

def nonempty(v:Any,minlen:int=1)->bool:
    return isinstance(v,str) and len(v.strip())>=minlen

def digest_ok(v:Any)->bool:
    if not isinstance(v,str): return False
    raw=v[7:] if v.lower().startswith('sha256:') else v
    raw=raw.lower()
    return len(raw)==64 and all(c in HEX for c in raw)

def reject_unknown(obj:dict[str,Any], allowed:set[str], subject:str, out:list[dict[str,Any]])->None:
    for k in sorted(set(obj)-allowed): out.append(error('UNKNOWN_PROPERTY',f'{subject}.{k}'.strip('.'),'not allowed'))

def validate_subjects(v:Any, subject:str, out:list[dict[str,Any]])->None:
    if not isinstance(v,list) or not v:
        out.append(error('DIGESTED_SUBJECTS_REQUIRED',subject,'expected non-empty array')); return
    seen=set()
    for i,row in enumerate(v):
        loc=f'{subject}[{i}]'
        if not isinstance(row,dict): out.append(error('DIGESTED_SUBJECT_TYPE',loc,'expected object')); continue
        reject_unknown(row,{'subject','sha256'},loc,out)
        name=row.get('subject')
        if not nonempty(name): out.append(error('DIGESTED_SUBJECT_NAME',loc,name))
        elif name in seen: out.append(error('DIGESTED_SUBJECT_DUPLICATE',loc,name))
        else: seen.add(name)
        if not digest_ok(row.get('sha256')): out.append(error('INVALID_SHA256',f'{loc}.sha256',row.get('sha256')))

def validate(data:Any)->list[dict[str,Any]]:
    out=[]
    if not isinstance(data,dict): return [error('ROOT_TYPE','root','expected object')]
    reject_unknown(data,ROOT_KEYS,'',out)
    if data.get('profile_version')!=1: out.append(error('PROFILE_VERSION','profile_version',data.get('profile_version')))
    for k in ('run_id','host','locale','timezone','cache_policy','concurrency_policy'):
        if not nonempty(data.get(k)): out.append(error('REQUIRED_STRING',k,data.get(k)))
    runtime=data.get('runtime')
    if not isinstance(runtime,dict): out.append(error('RUNTIME_REQUIRED','runtime',runtime))
    else:
        reject_unknown(runtime,{'python','os'},'runtime',out)
        for k in ('python','os'):
            if not nonempty(runtime.get(k)): out.append(error('REQUIRED_STRING',f'runtime.{k}',runtime.get(k)))
    model=data.get('model')
    if not isinstance(model,dict): out.append(error('MODEL_REQUIRED','model','use explicit not-applicable values for non-model runs'))
    else:
        reject_unknown(model,{'provider','name','configuration_identity'},'model',out)
        for k in ('provider','name'):
            if not nonempty(model.get(k)): out.append(error('REQUIRED_STRING',f'model.{k}',model.get(k)))
        if not nonempty(model.get('configuration_identity'),3): out.append(error('REQUIRED_STRING','model.configuration_identity',model.get('configuration_identity')))
    for key,needs_version in (('tools',False),('dependencies',True)):
        rows=data.get(key)
        if not isinstance(rows,list): out.append(error('COLLECTION_REQUIRED',key,rows)); continue
        seen=set()
        for i,row in enumerate(rows):
            loc=f'{key}[{i}]'
            if not isinstance(row,dict): out.append(error('COLLECTION_ITEM_TYPE',loc,row)); continue
            reject_unknown(row,{'name','version','identity'},loc,out)
            for field in (('name','identity','version') if needs_version else ('name','identity')):
                if not nonempty(row.get(field)): out.append(error('REQUIRED_STRING',f'{loc}.{field}',row.get(field)))
            if 'version' in row and not isinstance(row['version'],str): out.append(error('STRING_TYPE',f'{loc}.version',row['version']))
            ident=(str(row.get('name','')),str(row.get('identity','')))
            if ident in seen: out.append(error('DUPLICATE_IDENTITY',loc,ident))
            seen.add(ident)
    if data.get('hermeticity','recorded') not in {'recorded','pinned','hermetic'}:
        out.append(error('HERMETICITY_VALUE','hermeticity',data.get('hermeticity')))
    if 'controller_identity' in data and not nonempty(data.get('controller_identity')):
        out.append(error('REQUIRED_STRING','controller_identity',data.get('controller_identity')))
    validate_subjects(data.get('inputs'),'inputs',out); validate_subjects(data.get('outputs'),'outputs',out)
    return out

def identity(data:dict[str,Any])->dict[str,Any]:
    tools=sorted(data.get('tools',[]),key=lambda x:(str(x.get('name','')),str(x.get('identity','')))) if isinstance(data.get('tools'),list) else []
    deps=sorted(data.get('dependencies',[]),key=lambda x:(str(x.get('name','')),str(x.get('version','')),str(x.get('identity','')))) if isinstance(data.get('dependencies'),list) else []
    return {'host':data.get('host'),'runtime':data.get('runtime'),'model':data.get('model'),'tools':tools,'dependencies':deps,'locale':data.get('locale'),'timezone':data.get('timezone'),'cache_policy':data.get('cache_policy'),'concurrency_policy':data.get('concurrency_policy'),'hermeticity':data.get('hermeticity','recorded'),'controller_identity':data.get('controller_identity')}

def identity_sha(data:dict[str,Any])->str:
    raw=json.dumps(identity(data),sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
    return 'sha256:'+hashlib.sha256(raw).hexdigest()

def load(path:str)->Any: return json.loads(Path(path).read_text(encoding='utf-8'))

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('input'); ap.add_argument('--compare'); ap.add_argument('--json',dest='json_output')
    a=ap.parse_args(); left=load(a.input); diagnostics=validate(left); report={'status':'fail' if diagnostics else 'pass','diagnostics':diagnostics}
    if not diagnostics: report['identity_sha256']=identity_sha(left)
    if a.compare:
        right=load(a.compare); rdiag=validate(right); report['compare_diagnostics']=rdiag
        if not diagnostics and not rdiag:
            lid,rid=identity_sha(left),identity_sha(right); report['left_identity_sha256']=lid; report['right_identity_sha256']=rid
            report['environment_equivalent']=lid==rid
            if lid!=rid:
                report['diagnostics'].append(error('ENVIRONMENT_DRIFT','comparison',{'left':lid,'right':rid})); report['status']='fail'
        elif rdiag: report['status']='fail'
    payload=json.dumps(report,indent=2,ensure_ascii=False,sort_keys=True)+'\n'
    if a.json_output: Path(a.json_output).write_text(payload,encoding='utf-8')
    print(payload,end=''); return 0 if report['status']=='pass' else 1
if __name__=='__main__': raise SystemExit(main())
