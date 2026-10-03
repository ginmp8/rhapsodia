#!/usr/bin/env python3
"""Explicit, owner-scoped copy migration from retained Boards to native artifacts.

No source Board file is rewritten or deleted. Plan is read-only. Apply is opt-in,
idempotent, conflict-rejecting and recoverable using a producer-local journal.
"""
from __future__ import annotations
import argparse
from datetime import date
import json
import os
from pathlib import Path
import re
import shutil
import sys
from artifact_protocol import (ContractError,atomic_write,canonical_bytes,confined,digest,exclusive_lock,
                               load_json,source_bytes,timestamp,validate_record)
from native_artifacts import policy,resolve_owned_root

NAMES = {'nomia': {'ops.yaml': 'ops', 'status.md': 'status', 'stakeholder-brief.md': 'stakeholder-brief', 'replanning.md': 'replanning', 'portfolio.yaml': 'portfolio', 'portfolio.md': 'portfolio', 'roadmap.yaml': 'roadmap', 'roadmap.md': 'roadmap', 'feature-map.yaml': 'feature-map', 'rfc-proposals.md': 'governance-rfc', 'governance-decisions.md': 'governance-decision', 'release-notes.md': 'release-notes', 'internal-notes.md': 'internal-notes', 'feature-report.md': 'feature-report'}}


def legacy_root(repo:Path,relative:str)->Path:
    root=confined(repo,relative,must_exist=True)
    match=re.fullmatch(r'docs/boards/([a-z0-9]+(?:-[a-z0-9]+)*)/(\d{4})/cycles/cycle-(\d{4}-\d{2}-\d{2})-([a-z0-9]+(?:-[a-z0-9]+)*)',relative)
    if not match:raise ContractError('NONCANONICAL_LEGACY_ROOT')
    try:parsed=date.fromisoformat(match.group(3))
    except ValueError as exc:raise ContractError('INVALID_LEGACY_DATE') from exc
    if str(parsed.year)!=match.group(2):raise ContractError('LEGACY_YEAR_CONFLICT')
    return root

def plan(repo:Path,board:str,observed_at:str,artifact_root:str|None=None)->dict:
    timestamp(observed_at);root=legacy_root(repo,board);rules=policy();owner=rules['producer']
    target_root=resolve_owned_root(repo,artifact_root);items=[];excluded=[]
    for current,dirs,files in os.walk(root,followlinks=False):
        here=Path(current)
        for name in dirs+files:
            if (here/name).is_symlink():raise ContractError('SYMLINK_IN_LEGACY_TREE')
        dirs[:]=sorted(d for d in dirs if not d.startswith('.'))
        for name in sorted(files):
            path=here/name;rel=path.relative_to(repo).as_posix();within=path.relative_to(root)
            kind=NAMES[owner].get(name)
            if kind is None:
                excluded.append({'source':rel,'reason':'not-an-owned-recognized-artifact'});continue
            parts=within.parts
            if len(parts)>=3 and parts[0]=='specs':
                match=re.fullmatch(r'spec-(\d{4}-\d{2}-\d{2})-([a-z0-9]+(?:-[a-z0-9]+)*)',parts[1])
                if not match:raise ContractError('INVALID_LEGACY_SPEC_ID')
                try:date.fromisoformat(match.group(1))
                except ValueError as exc:raise ContractError('INVALID_LEGACY_SPEC_DATE') from exc
                work=match.group(2);tail=Path(*parts[2:]).as_posix()
            else:
                work='cycle-'+root.name.removeprefix('cycle-');tail=within.as_posix()
            destination=(target_root/work/tail).relative_to(repo).as_posix()
            # Relative source path forms the suffix to avoid collisions between .md/.yaml pairs.
            suffix=re.sub(r'[^a-z0-9]+','-',tail.lower()).strip('-')
            content=source_bytes(path)
            record={'schema_version':'1.0.0','artifact_id':owner+':'+work+':'+suffix,'producer':owner,
                    'artifact_type':kind,'work_item_id':work,'workflow_id':None,'title':work+' / '+kind,
                    'state':{'dimension':rules['dimensions'][0],'value':'unknown'},'lifecycle':'active',
                    'created_at':observed_at,'updated_at':observed_at,'source':{'path':destination,'sha256':digest(content)},
                    'relations':[],'privacy':{'classification':'internal','allowed_destinations':['local'],
                    'contains_secrets':False,'external_share_allowed':False},
                    'provenance':{'kind':'migrated','evidence_refs':['legacy:'+rel,'sha256:'+digest(content)],'source_handoff_id':None}}
            validate_record(record)
            items.append({'source':rel,'source_sha256':digest(content),'artifact':record})
    return {'schema_version':'1.0.0','owner':owner,'legacy_root':board,'artifact_root':target_root.relative_to(repo).as_posix(),
            'items':sorted(items,key=lambda x:x['source']),'excluded':excluded,
            'semantics':'copy-only; original content and identity evidence retained; status is unknown, never inferred'}

def check_plan(repo:Path,value:dict)->tuple[Path,list]:
    if not isinstance(value,dict) or set(value)!={'schema_version','owner','legacy_root','artifact_root','items','excluded','semantics'}:
        raise ContractError('INVALID_MIGRATION_PLAN')
    rules=policy()
    if value['schema_version']!='1.0.0' or value['owner']!=rules['producer']:raise ContractError('MIGRATION_OWNER_MISMATCH')
    legacy=legacy_root(repo,value['legacy_root']);owned=resolve_owned_root(repo,value['artifact_root'])
    if not isinstance(value['items'],list) or len(value['items'])>10000:raise ContractError('MIGRATION_ITEM_LIMIT')
    writes=[];seen=set()
    for item in value['items']:
        if not isinstance(item,dict) or set(item)!={'source','source_sha256','artifact'}:raise ContractError('INVALID_MIGRATION_ITEM')
        source=confined(repo,item['source'],must_exist=True,regular=True)
        if not source.is_relative_to(legacy):raise ContractError('MIGRATION_SOURCE_ESCAPE')
        record=item['artifact'];validate_record(record)
        if record['producer']!=rules['producer'] or record['artifact_type'] not in rules['artifact_types'] or record['state']['dimension'] not in rules['dimensions']:
            raise ContractError('MIGRATION_CROSS_OWNER')
        if NAMES[rules['producer']].get(source.name)!=record['artifact_type']:
            raise ContractError('MIGRATION_UNRECOGNIZED_OWNED_SOURCE')
        target=confined(repo,record['source']['path'])
        if not target.is_relative_to(owned) or target==owned:raise ContractError('MIGRATION_TARGET_ESCAPE')
        data=source_bytes(source)
        if digest(data)!=item['source_sha256'] or digest(data)!=record['source']['sha256']:raise ContractError('MIGRATION_SOURCE_DRIFT')
        for path,payload in [(target,data),(Path(str(target)+'.artifact.json'),canonical_bytes(record))]:
            if path in seen:raise ContractError('DUPLICATE_MIGRATION_TARGET')
            seen.add(path)
            if path.exists() and source_bytes(path)!=payload:raise ContractError('MIGRATION_TARGET_CONFLICT')
            writes.append((path,payload,path.exists()))
    return owned,writes

def recover(repo:Path,artifact_root:str|None=None,*,expected_journal_sha256:str|None=None,internal:bool=False)->dict:
    owned=resolve_owned_root(repo,artifact_root);journal=owned/'.migration-journal.json'
    if not journal.exists():return {'status':'unchanged'}
    raw=source_bytes(journal)
    if not internal and expected_journal_sha256!=digest(raw):raise ContractError('RECOVERY_JOURNAL_APPROVAL_REQUIRED')
    value=load_json(journal,8*1024*1024)
    if value.get('owner')!=policy()['producer'] or not isinstance(value.get('created'),list):raise ContractError('INVALID_MIGRATION_JOURNAL')
    # Validate the full rollback before removing any file; foreign edits are never deleted.
    targets=[]
    for entry in value['created']:
        path=confined(repo,entry['path'])
        if not path.is_relative_to(owned):raise ContractError('RECOVERY_PATH_ESCAPE')
        if path.exists() and digest(source_bytes(path))!=entry['sha256']:raise ContractError('RECOVERY_SOURCE_CHANGED')
        targets.append(path)
    plan_hash=value.get('plan_sha256')
    if not isinstance(plan_hash,str) or not re.fullmatch('[a-f0-9]{64}',plan_hash):raise ContractError('INVALID_MIGRATION_JOURNAL')
    committed=confined(repo,(owned/'.migration-receipts'/(plan_hash+'.json')).relative_to(repo).as_posix())
    if committed.exists():
        receipt=load_json(committed)
        if receipt.get('status')!='pass' or receipt.get('owner')!=value['owner'] or receipt.get('plan_sha256')!=plan_hash:
            raise ContractError('INVALID_MIGRATION_COMMIT_RECEIPT')
        if any(not path.exists() for path in targets):raise ContractError('COMMITTED_MIGRATION_INCOMPLETE')
        journal.unlink()
        return {'status':'finalized','copied_files':len(targets),'originals_untouched':True}
    for path in reversed(targets):path.unlink(missing_ok=True)
    journal.unlink()
    return {'status':'recovered','rolled_back_files':len(targets),'originals_untouched':True}

def apply(repo:Path,value:dict)->dict:
    owned,writes=check_plan(repo,value);owned.mkdir(parents=True,exist_ok=True)
    journal=owned/'.migration-journal.json'
    with exclusive_lock(owned/'.artifact-write.lock'):
        if journal.exists():raise ContractError('MIGRATION_RECOVERY_REQUIRED')
        owned,writes=check_plan(repo,value)
        new=[(p,d) for p,d,exists in writes if not exists]
        if not new:return {'status':'unchanged','copied_files':0,'originals_untouched':True,'plan_sha256':digest(canonical_bytes(value))}
        entries=[{'path':p.relative_to(repo).as_posix(),'sha256':digest(d)} for p,d in new]
        atomic_write(journal,canonical_bytes({'owner':value['owner'],'created':entries,'plan_sha256':digest(canonical_bytes(value))}))
        try:
            for path,data in new:atomic_write(path,data)
            for item in value['items']:
                manifest=Path(str(repo/item['artifact']['source']['path'])+'.artifact.json')
                validate_record(item['artifact'],repo,manifest)
            result={'status':'pass','copied_files':len(new),'originals_untouched':True,'plan_sha256':digest(canonical_bytes(value)),
                    'owner':value['owner'],'artifact_ids':[x['artifact']['artifact_id'] for x in value['items']]}
            receipt=owned/'.migration-receipts'/(result['plan_sha256']+'.json')
            atomic_write(receipt,canonical_bytes(result))
            journal.unlink()
            return result
        except BaseException:
            recover(repo,value['artifact_root'],internal=True)
            raise

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=['plan','apply','recovery-plan','recover'])
    p.add_argument('--repo-root',required=True,type=Path);p.add_argument('--legacy-root');p.add_argument('--observed-at');p.add_argument('--artifact-root');p.add_argument('--plan',type=Path);p.add_argument('--journal-sha256')
    a=p.parse_args(argv)
    try:
        repo=a.repo_root.resolve(strict=True)
        if a.command=='plan':
            if not a.legacy_root or not a.observed_at:raise ContractError('LEGACY_ROOT_AND_OBSERVED_AT_REQUIRED')
            result=plan(repo,a.legacy_root,a.observed_at,a.artifact_root)
        elif a.command=='apply':
            if not a.plan:raise ContractError('PLAN_REQUIRED')
            result=apply(repo,load_json(a.plan,16*1024*1024))
        elif a.command=='recovery-plan':
            owned=resolve_owned_root(repo,a.artifact_root);journal=owned/'.migration-journal.json'
            if not journal.exists():result={'status':'unchanged'}
            else:
                result={'status':'approval-required','journal_sha256':digest(source_bytes(journal)),'journal':load_json(journal)}
        else:
            owned=resolve_owned_root(repo,a.artifact_root)
            with exclusive_lock(owned/'.artifact-write.lock'):
                result=recover(repo,a.artifact_root,expected_journal_sha256=a.journal_sha256)
        print(canonical_bytes(result).decode(),end='');return 0
    except (ContractError,OSError,ValueError,KeyError,TypeError) as exc:
        print(json.dumps({'status':'fail','code':str(exc) if isinstance(exc,ContractError) else type(exc).__name__}));return 1

if __name__=='__main__':raise SystemExit(main())
