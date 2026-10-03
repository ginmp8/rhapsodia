#!/usr/bin/env python3
"""Record and close bounded Magia execution without changing Mago or Nomia files.

Execution requires an explicitly trusted argv contract. Evidence is a local audit
receipt, not a signature or proof against a malicious local filesystem owner.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from artifact_protocol import ContractError, atomic_write, canonical_bytes, confined, digest, exclusive_lock, load_json, source_bytes
from native_artifacts import resolve_owned_root
from magia_utils import parse_spec_id

SKIP={'.git','__pycache__','.pytest_cache','.mypy_cache','.ruff_cache','node_modules','bin','obj'}
LIMIT=10000

def now():return datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')
def keyed(value,label):
    if not isinstance(value,str) or not re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*',value):raise ContractError('INVALID_'+label)
    return value

def tree(repo:Path,roots:list[str])->dict:
    if not isinstance(roots,list) or not roots or len(roots)>50 or len(set(roots))!=len(roots):raise ContractError('INVALID_CANDIDATE_ROOTS')
    files={}
    for rel in roots:
        path=confined(repo,rel,must_exist=True)
        if rel.startswith(('docs/product','docs/specs','docs/implementation','.')):raise ContractError('CANDIDATE_ROOT_OVERLAPS_ARTIFACTS')
        paths=[path] if path.is_file() else []
        if path.is_dir():
            for current,dirs,names in os.walk(path,followlinks=False):
                here=Path(current)
                if any((here/name).is_symlink() for name in dirs+names):raise ContractError('CANDIDATE_SYMLINK')
                dirs[:]=sorted(x for x in dirs if x not in SKIP)
                paths.extend(here/name for name in sorted(names) if not name.endswith(('.pyc','.pyo')))
                if len(paths)>LIMIT:raise ContractError('CANDIDATE_FILE_LIMIT')
        for item in paths:
            relative=item.relative_to(repo).as_posix()
            data=source_bytes(confined(repo,relative,must_exist=True,regular=True));files[relative]=digest(data)
            if len(files)>LIMIT:raise ContractError('CANDIDATE_FILE_LIMIT')
    if not files:raise ContractError('EMPTY_CANDIDATE_SCOPE')
    return dict(sorted(files.items()))

def validate_request(repo:Path,data:dict,trail:frozenset[str]=frozenset())->dict:
    fields={'schema_version','mode','work_item_id','spec_id','task_id','requirements','acceptance','validations','planning_sources','candidate_roots','checks','dependency_receipts'}
    if not isinstance(data,dict) or set(data)!=fields or data['schema_version']!='1.0.0':raise ContractError('INVALID_EXECUTION_REQUEST')
    keyed(data['work_item_id'],'WORK_ITEM_ID')
    if data['mode'] not in {'adhoc','ralph'}:raise ContractError('INVALID_EXECUTION_MODE')
    for name,prefix in [('requirements','REQ-'),('acceptance','AC-'),('validations','VAL-')]:
        values=data[name]
        if not isinstance(values,list) or not values or len(set(values))!=len(values) or not all(isinstance(x,str) and re.fullmatch(prefix+'[0-9]{3}',x) for x in values):raise ContractError('INVALID_TRACEABILITY_'+name.upper())
    if not isinstance(data['planning_sources'],list) or len(data['planning_sources'])>100:raise ContractError('INVALID_PLANNING_INPUTS')
    sources={}
    for ref in data['planning_sources']:
        if not isinstance(ref,dict) or set(ref)!={'path','sha256'}:raise ContractError('INVALID_PLANNING_INPUT')
        path=confined(repo,ref['path'],must_exist=True,regular=True)
        if digest(source_bytes(path))!=ref['sha256']:raise ContractError('STALE_PLANNING_INPUT')
        if ref['path'] in sources:raise ContractError('DUPLICATE_PLANNING_INPUT')
        sources[ref['path']]=ref['sha256']
    if data['mode']=='ralph':
        parse_spec_id(data['spec_id'])
        if not isinstance(data['task_id'],str) or not re.fullmatch('task[0-9]{3}',data['task_id']):raise ContractError('INVALID_TASK_ID')
        task_paths=[repo/p for p in sources if Path(p).name=='tasks.md']
        if len(task_paths)!=1:raise ContractError('EXACTLY_ONE_BOUND_TASK_SOURCE_REQUIRED')
        text=source_bytes(task_paths[0]).decode('utf-8')
        match=re.search(r'(?ms)^\s*-\s*\[[ xX]\]\s+'+data['task_id']+r':[^\n]*\n(.*?)(?=^\s*-\s*\[[ xX]\]\s+task[0-9]{3}:|^## |\Z)',text)
        if not match:raise ContractError('TASK_NOT_IN_PLANNING_SOURCE')
        for name,prefix in [('requirements','REQ-'),('acceptance','AC-'),('validations','VAL-')]:
            field=re.search(r'(?mi)^\s*-\s*'+name+r':\s*([^\n]+)',match.group(1))
            if not field or set(data[name])!=set(re.findall(prefix+'[0-9]{3}',field.group(1))):raise ContractError('TASK_TRACEABILITY_MISMATCH')
        identities=[repo/p for p in sources if Path(p).name=='planning-identity.json']
        if len(identities)!=1:raise ContractError('PLANNING_IDENTITY_MISMATCH')
        ident=load_json(identities[0]);parsed=parse_spec_id(data['spec_id'])
        from artifact_protocol import timestamp
        if not isinstance(ident,dict) or set(ident)!={'schema_version','producer','work_item_id','spec_id','created_at'} or ident.get('schema_version')!='1.0.0' or ident.get('producer')!='mago' or ident.get('spec_id')!=data['spec_id'] or ident.get('work_item_id')!=data['work_item_id']:
            raise ContractError('PLANNING_IDENTITY_MISMATCH')
        if timestamp(ident['created_at']).date().isoformat()!=parsed['date'] or parsed['feature']!=data['work_item_id']:
            raise ContractError('PLANNING_IDENTITY_DATE_CONFLICT')
    elif data['spec_id'] is not None or data['task_id'] is not None or data['planning_sources']:
        raise ContractError('ADHOC_MUST_NOT_INVENT_PLANNING_IDENTITY')
    checks=data['checks']
    if not isinstance(checks,list) or not 1<=len(checks)<=50:raise ContractError('INVALID_CHECKS')
    refs=[]
    for check in checks:
        if not isinstance(check,dict) or set(check)!={'validation_ref','argv','cwd','timeout_seconds'}:raise ContractError('INVALID_CHECK_CONTRACT')
        if check['validation_ref'] not in data['validations']:raise ContractError('CHECK_OUTSIDE_PLANNED_VALIDATION')
        refs.append(check['validation_ref']);argv=check['argv']
        if not isinstance(argv,list) or not argv or len(argv)>100 or not all(isinstance(x,str) and x and '\x00' not in x for x in argv):raise ContractError('INVALID_ARGV')
        if type(check['timeout_seconds']) is not int or not 1<=check['timeout_seconds']<=1800:raise ContractError('INVALID_CHECK_TIMEOUT')
        if check['cwd']!='.':
            cwd=confined(repo,check['cwd'],must_exist=True)
            if not cwd.is_dir():raise ContractError('INVALID_CHECK_CWD')
    if set(refs)!=set(data['validations']):raise ContractError('MISSING_PLANNED_VALIDATION')
    deps=data['dependency_receipts']
    if not isinstance(deps,list) or len(deps)>100:raise ContractError('INVALID_DEPENDENCIES')
    seen=set()
    for dep in deps:
        if not isinstance(dep,dict) or set(dep)!={'path','sha256','task_id'}:raise ContractError('INVALID_DEPENDENCY_RECEIPT')
        if dep['task_id']==data['task_id'] or dep['task_id'] in seen:raise ContractError('SELF_OR_DUPLICATE_DEPENDENCY')
        seen.add(dep['task_id'])
        path=confined(repo,dep['path'],must_exist=True,regular=True)
        if digest(source_bytes(path))!=dep['sha256']:raise ContractError('DEPENDENCY_RECEIPT_DRIFT')
        prior=validate_receipt(repo,path,trail)
        if prior.get('status')!='passed' or prior.get('producer')!='magia' or prior.get('task_id')!=dep['task_id'] or prior.get('spec_id')!=data['spec_id']:raise ContractError('DEPENDENCY_NOT_VALIDATED')
    # Dependencies recorded by Mago are mandatory, not a selectable subset.
    if data['mode']=='ralph':
        dep_field=re.search(r'(?mi)^\s*-\s*dependencies:\s*([^\n]+)',match.group(1))
        planned=set(re.findall(r'task[0-9]{3}',dep_field.group(1))) if dep_field else set()
        if seen!=planned:raise ContractError('PLANNED_DEPENDENCY_MISMATCH')
    elif deps:raise ContractError('ADHOC_CANNOT_CLAIM_PLANNED_DEPENDENCIES')
    return tree(repo,data['candidate_roots'])


def run(repo:Path,data:dict,artifact_root:str|None=None)->dict:
    before=validate_request(repo,data);owned=resolve_owned_root(repo,artifact_root)
    owned.mkdir(parents=True,exist_ok=True)
    # Serializes Magia writes only; no locks or edits in planning/governance roots.
    with exclusive_lock(owned/'.artifact-write.lock'):
        start=now();results=[]
        for check in data['checks']:
            cwd=repo if check['cwd']=='.' else confined(repo,check['cwd'],must_exist=True)
            try:
                process=subprocess.run(check['argv'],cwd=cwd,capture_output=True,timeout=check['timeout_seconds'],check=False)
                code=process.returncode;raw=process.stdout+b'\n'+process.stderr;state='pass' if code==0 else 'fail'
            except subprocess.TimeoutExpired as exc:
                code=None;raw=(exc.stdout or b'')+b'\n'+(exc.stderr or b'');state='timeout'
            except OSError as exc:
                code=None;raw=type(exc).__name__.encode();state='blocked'
            results.append({'validation_ref':check['validation_ref'],'argv':check['argv'],'cwd':check['cwd'],
                            'returncode':code,'status':state,'output_sha256':digest(raw)})
        after=validate_request(repo,data)
        if before!=after:raise ContractError('CANDIDATE_CHANGED_DURING_VALIDATION')
        receipt={'schema_version':'1.0.0','producer':'magia','evidence_kind':'executed','work_item_id':data['work_item_id'],
                 'spec_id':data['spec_id'],'task_id':data['task_id'],'status':'passed' if all(x['status']=='pass' for x in results) else 'failed',
                 'started_at':start,'finished_at':now(),'request':data,'request_sha256':digest(canonical_bytes(data)),
                 'candidate_files':before,'checks':results,'runner_sha256':digest(Path(__file__).read_bytes())}
        run_id=digest(canonical_bytes(receipt))[:24]
        output=confined(repo,(owned/data['work_item_id']/'runs'/(run_id+'.json')).relative_to(repo).as_posix())
        if output.exists() and source_bytes(output)!=canonical_bytes(receipt):raise ContractError('RUN_ID_CONFLICT')
        atomic_write(output,canonical_bytes(receipt))
        return {'status':receipt['status'],'receipt_path':output.relative_to(repo).as_posix(),'receipt_sha256':digest(canonical_bytes(receipt)),
                'evidence_level':'local-command-execution','global_delivery_completed':False}


def validate_receipt(repo:Path,path:Path,trail:frozenset[str]=frozenset())->dict:
    key=path.resolve().as_posix()
    if key in trail or len(trail)>=20:raise ContractError('DEPENDENCY_RECEIPT_CYCLE_OR_DEPTH')
    trail=trail|{key}
    receipt=load_json(path,8*1024*1024)
    required={'schema_version','producer','evidence_kind','work_item_id','spec_id','task_id','status','started_at','finished_at','request','request_sha256','candidate_files','checks','runner_sha256'}
    if not isinstance(receipt,dict) or set(receipt)!=required or receipt['schema_version']!='1.0.0' or receipt['producer']!='magia' or receipt['evidence_kind']!='executed':raise ContractError('INVALID_EXECUTION_RECEIPT')
    if receipt['runner_sha256']!=digest(Path(__file__).read_bytes()):raise ContractError('EXECUTION_RUNNER_CHANGED')
    request=receipt['request']
    if receipt['request_sha256']!=digest(canonical_bytes(request)):raise ContractError('EXECUTION_REQUEST_CHANGED')
    if any(receipt[key]!=request[key] for key in ('work_item_id','spec_id','task_id')):raise ContractError('EXECUTION_IDENTITY_MISMATCH')
    current=validate_request(repo,request,trail)
    if receipt['candidate_files']!=current:raise ContractError('STALE_EXECUTION_EVIDENCE')
    if receipt['status']!='passed' or not isinstance(receipt['checks'],list) or len(receipt['checks'])!=len(request['checks']):raise ContractError('EXECUTION_NOT_PASSED')
    for result,check in zip(receipt['checks'],request['checks']):
        if not isinstance(result,dict) or set(result)!={'validation_ref','argv','cwd','returncode','status','output_sha256'}:raise ContractError('INVALID_CHECK_RECEIPT')
        if result['validation_ref']!=check['validation_ref'] or result['argv']!=check['argv'] or result['cwd']!=check['cwd']:raise ContractError('CHECK_CONTRACT_CHANGED')
        if type(result['returncode']) is not int or result['returncode']!=0 or result['status']!='pass' or not re.fullmatch('[a-f0-9]{64}',str(result['output_sha256'])):raise ContractError('CHECK_NOT_PASSED')
    from artifact_protocol import timestamp
    if timestamp(receipt['finished_at'])<timestamp(receipt['started_at']):raise ContractError('INVALID_EXECUTION_TIME')
    return receipt


def close(repo:Path,path:Path,expected:str|None,artifact_root:str|None=None)->dict:
    owned=resolve_owned_root(repo,artifact_root);owned.mkdir(parents=True,exist_ok=True)
    with exclusive_lock(owned/'.artifact-write.lock'):
        receipt=validate_receipt(repo,path)
        target=confined(repo,(owned/receipt['work_item_id']/((receipt['task_id'] or 'adhoc')+'-execution-state.json')).relative_to(repo).as_posix())
        state={'schema_version':'1.0.0','producer':'magia','work_item_id':receipt['work_item_id'],'spec_id':receipt['spec_id'],
               'task_id':receipt['task_id'],'execution_state':'validated','validation_state':'passed',
               'receipt_path':path.relative_to(repo).as_posix(),'receipt_sha256':digest(source_bytes(path)),
               'candidate_files':receipt['candidate_files'],'updated_at':receipt['finished_at']}
        payload=canonical_bytes(state)
        if target.exists():
            old=source_bytes(target)
            if old==payload:return {'status':'unchanged','state_path':target.relative_to(repo).as_posix()}
            if expected!=digest(old):raise ContractError('EXECUTION_STATE_REVISION_CONFLICT')
        elif expected is not None:raise ContractError('EXECUTION_STATE_EXPECTED_MISSING')
        atomic_write(target,payload)
        return {'status':'pass','state_path':target.relative_to(repo).as_posix(),'planning_files_modified':False,'governance_closed':False}


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=['run','validate','close'])
    p.add_argument('--repo-root',required=True,type=Path);p.add_argument('--input',required=True,type=Path);p.add_argument('--artifact-root')
    p.add_argument('--trust-command',action='store_true');p.add_argument('--expected-state-sha256')
    a=p.parse_args(argv)
    try:
        repo=a.repo_root.resolve(strict=True)
        if a.command=='run':
            if not a.trust_command:raise ContractError('EXPLICIT_COMMAND_TRUST_REQUIRED')
            result=run(repo,load_json(a.input,8*1024*1024),a.artifact_root)
        else:
            path=confined(repo,a.input.resolve().relative_to(repo).as_posix(),must_exist=True,regular=True)
            result=close(repo,path,a.expected_state_sha256,a.artifact_root) if a.command=='close' else {'status':'pass','receipt':validate_receipt(repo,path)}
        print(canonical_bytes(result).decode(),end='');return 0 if result['status'] in {'pass','passed','unchanged'} else 1
    except (ContractError,OSError,ValueError,KeyError,TypeError) as exc:
        print(json.dumps({'status':'fail','error':str(exc)}));return 1
if __name__=='__main__':raise SystemExit(main())
