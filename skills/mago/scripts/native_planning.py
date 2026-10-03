#!/usr/bin/env python3
"""Mago-owned planning identity and semantic validation without a Board.

Identity stays a planning concern; the optional Workspace only observes it.
Validation reuses this package's task, technical-design and security contracts.
"""
from __future__ import annotations
import argparse
from datetime import datetime
import json
from pathlib import Path
import re
import sys
from artifact_protocol import ContractError, atomic_write, canonical_bytes, confined, digest, exclusive_lock, load_json, source_bytes, timestamp, discover
from native_artifacts import resolve_owned_root
from mago_utils import parse_spec_id
from validate_package import validate_task_contract, validate_conditional_artifacts, parse_tasks


def work_root(repo:Path,key:str,artifact_root:str|None=None)->Path:
    if not isinstance(key,str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',key):raise ContractError('INVALID_WORK_ITEM_ID')
    owned=resolve_owned_root(repo,artifact_root)
    return confined(repo,(owned/key).relative_to(repo).as_posix())


def identity(repo:Path,key:str,created_at:str,artifact_root:str|None=None)->dict:
    instant=timestamp(created_at);root=work_root(repo,key,artifact_root)
    value={'schema_version':'1.0.0','producer':'mago','work_item_id':key,'spec_id':'spec-'+created_at[:10]+'-'+key,'created_at':created_at}
    parse_spec_id(value['spec_id'])
    owned=root.parent;owned.mkdir(parents=True,exist_ok=True)
    with exclusive_lock(owned/'.artifact-write.lock'):
        path=root/'planning-identity.json'
        if path.exists():
            existing=read_identity(path,key)
            # Caller must reuse the original creation time; a retry never remints identity.
            if existing!=value:raise ContractError('PLANNING_IDENTITY_CONFLICT')
            return {'status':'unchanged','identity':existing,'path':path.relative_to(repo).as_posix()}
        atomic_write(path,canonical_bytes(value))
        return {'status':'created','identity':value,'path':path.relative_to(repo).as_posix()}


def read_identity(path:Path,key:str)->dict:
    source_bytes(path)
    value=load_json(path)
    if not isinstance(value,dict) or set(value)!={'schema_version','producer','work_item_id','spec_id','created_at'}:
        raise ContractError('INVALID_PLANNING_IDENTITY')
    if value['schema_version']!='1.0.0' or value['producer']!='mago' or value['work_item_id']!=key:raise ContractError('PLANNING_IDENTITY_MISMATCH')
    parsed=parse_spec_id(value['spec_id']);timestamp(value['created_at'])
    if parsed['date']!=value['created_at'][:10] or parsed['feature']!=key:raise ContractError('PLANNING_IDENTITY_DATE_CONFLICT')
    return value


def validate(repo:Path,key:str,profile:str='standard',artifact_root:str|None=None)->dict:
    if profile not in {'quick','standard','governed'}:raise ContractError('INVALID_PROFILE')
    root=work_root(repo,key,artifact_root);ident=read_identity(root/'planning-identity.json',key)
    discover(repo,[root.relative_to(repo).as_posix()])
    required=['prd.md','tasks.md','validation.md']+(['notes.md'] if profile!='quick' else [])
    errors=[];warnings=[];bound={}
    for name in required:
        try:
            path=confined(repo,(root/name).relative_to(repo).as_posix(),must_exist=True,regular=True)
            data=source_bytes(path)
            if len(data.strip())<20:errors.append(name+': substantive source content is required')
            bound[path.relative_to(repo).as_posix()]=digest(data)
        except (ContractError,OSError):errors.append(name+': required planning artifact is missing or unsafe')
    if errors:return {'status':'fail','errors':errors,'warnings':warnings,'identity':ident}
    _,task_errors,task_warnings=validate_task_contract(root/'tasks.md',profile)
    errors.extend(task_errors);warnings.extend(task_warnings)
    errors.extend(validate_conditional_artifacts(root))
    # Preserve the profile's requirements-to-proof contract without importing peer skills.
    from render_traceability import parse_file, FILES
    from validate_traceability import validate_projection
    records={};parse_errors=[]
    for name,allowed in FILES.items():
        path=root/name
        if path.exists():
            confined(repo,path.relative_to(repo).as_posix(),must_exist=True,regular=True)
            found,duplicate=parse_file(path,allowed);records.update(found);parse_errors.extend(duplicate)
            bound[path.relative_to(repo).as_posix()]=digest(source_bytes(path))
    if profile!='quick':
        trace=validate_projection({'authoritative':False,'records':records,'render_errors':parse_errors},profile)
        errors.extend(trace['errors'])
        if not trace['coverage']['requirements']:errors.append('standard/governed planning requires explicit REQ/AC/task/VAL traceability')
    # Trigger decisions are owner-authored; the validator enforces completeness, not subjective applicability.
    decision_path=root/'artifact-decisions.json'
    if profile=='governed' or decision_path.exists():
        if not decision_path.is_file():errors.append('governed planning requires artifact-decisions.json')
        else:
            decisions=load_json(decision_path)
            families={'technical-design','contract-spec','migration-strategy','observability-design','operational-requirements','security-and-risk-considerations'}
            if not isinstance(decisions,dict) or set(decisions)!=families:errors.append('artifact decisions must cover all governed trigger families')
            else:
                for family,item in decisions.items():
                    if not isinstance(item,dict) or set(item)!={'required','reason','evidence'} or type(item.get('required')) is not bool or not isinstance(item.get('reason'),str) or not item['reason'].strip() or not isinstance(item.get('evidence'),list) or not item['evidence']:
                        errors.append(family+': explicit applicability, rationale and evidence are required');continue
                    if item['required'] and not (root/(family+'.md')).is_file():errors.append(family+': triggered artifact missing')
            bound[decision_path.relative_to(repo).as_posix()]=digest(source_bytes(decision_path))
    if errors:return {'status':'fail','errors':errors,'warnings':warnings,'identity':ident}
    for path,old in bound.items():
        if digest(source_bytes(confined(repo,path,must_exist=True,regular=True)))!=old:raise ContractError('PLANNING_SOURCE_DRIFT')
    return {'status':'pass','profile':profile,'identity':ident,'errors':[],'warnings':warnings,
            'evidence_level':'static-planning-contract','source_hashes':bound,'runtime_validation_performed':False}


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=['identity','validate'])
    p.add_argument('--repo-root',required=True,type=Path);p.add_argument('--work-item',required=True)
    p.add_argument('--artifact-root');p.add_argument('--created-at');p.add_argument('--profile',choices=['quick','standard','governed'],default='standard')
    a=p.parse_args(argv)
    try:
        repo=a.repo_root.resolve(strict=True)
        if a.command=='identity':
            if not a.created_at:raise ContractError('CREATED_AT_REQUIRED')
            result=identity(repo,a.work_item,a.created_at,a.artifact_root)
        else:result=validate(repo,a.work_item,a.profile,a.artifact_root)
        print(canonical_bytes(result).decode(),end='');return 1 if result['status']=='fail' else 0
    except (OSError,ValueError,KeyError,TypeError) as exc:
        print(json.dumps({'status':'fail','error':str(exc)}));return 1
if __name__=='__main__':raise SystemExit(main())
