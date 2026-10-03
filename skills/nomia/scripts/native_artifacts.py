#!/usr/bin/env python3
"""Publish only this skill's source-owned artifact metadata and action receipts.

Source bodies are authored by the domain owner, never by Workspace. A source edit
without republishing is intentionally detected as stale by every consumer.
"""
from __future__ import annotations
import argparse
import copy
import json
import os
from pathlib import Path
import sys
from artifact_protocol import (ContractError, atomic_write, canonical_bytes, confined,
                               digest, discover, exclusive_lock, load_json, source_bytes,
                               validate_actions, validate_record)

from artifact_protocol import repository_root, SECRET_RE

PACKAGE = Path(__file__).resolve().parents[1]

def policy():
    return load_json(PACKAGE / 'references/artifact-native-policy.json')

def resolve_owned_root(repo: Path, relative: str | None = None) -> Path:
    rules = policy()
    relative = relative or rules['default_root']
    root = confined(repo, relative)
    if relative.split('/')[0].startswith('.'):
        raise ContractError('HIDDEN_ARTIFACT_ROOT')
    for other in rules['other_owner_roots']:
        other_root = repo.resolve() / other
        if root == other_root or root.is_relative_to(other_root) or other_root.is_relative_to(root):
            raise ContractError('CROSS_OWNER_ROOT')
    if root.exists():
        for descriptor in discover(repo, [root.relative_to(repo.resolve()).as_posix()]):
            existing=load_json(descriptor)
            validate_record(existing)
            if existing['producer'] != rules['producer']:
                raise ContractError('FOREIGN_PRODUCER_IN_OWNED_ROOT')
    return root

def publish(repo: Path, request: dict, artifact_root: str | None = None) -> dict:
    if not isinstance(request, dict) or set(request) != {'artifact','expected_manifest_sha256','reason'}:
        raise ContractError('INVALID_PUBLICATION_REQUEST')
    if not isinstance(request['reason'], str) or not 1 <= len(request['reason']) <= 500:
        raise ContractError('INVALID_PUBLICATION_REASON')
    if not request['reason'].strip() or SECRET_RE.search(request['reason']):
        raise ContractError('INVALID_PUBLICATION_REASON')
    expected = request['expected_manifest_sha256']
    if expected is not None and (not isinstance(expected,str) or len(expected)!=64 or any(c not in '0123456789abcdef' for c in expected)):
        raise ContractError('INVALID_EXPECTED_REVISION')
    rules = policy()
    record = copy.deepcopy(request['artifact'])
    if not isinstance(record,dict) or record.get('producer') != rules['producer']:
        raise ContractError('CROSS_OWNER_PUBLICATION')
    if not isinstance(record.get('state'), dict):
        raise ContractError('INVALID_PUBLICATION_STATE')
    if record.get('artifact_type') not in rules['artifact_types'] or record['state'].get('dimension') not in rules['dimensions']:
        raise ContractError('OUTSIDE_PRODUCER_AUTHORITY')
    owned_root = resolve_owned_root(repo,artifact_root)
    try: source = confined(repo,record['source']['path'])
    except (KeyError,TypeError) as exc: raise ContractError('INVALID_SOURCE') from exc
    if not source.is_relative_to(owned_root) or source==owned_root:
        raise ContractError('OUTSIDE_OWNED_ARTIFACT_ROOT')
    manifest = Path(str(source)+'.artifact.json')
    owned_root.mkdir(parents=True,exist_ok=True)
    with exclusive_lock(owned_root/'.artifact-write.lock'):
        before = manifest.read_bytes() if manifest.exists() and not manifest.is_symlink() else None
        if manifest.is_symlink(): raise ContractError('SYMLINK_MANIFEST')
        previous = load_json(manifest) if before else None
        old_hash = digest(before) if before else None
        if previous:
            # Previous source may intentionally have changed; validate metadata, not old source hash.
            validate_record(previous)
            for key in ('artifact_id','producer','artifact_type','work_item_id','created_at'):
                if previous[key] != record.get(key): raise ContractError('IMMUTABLE_ARTIFACT_IDENTITY')
            if record['updated_at'] < previous['updated_at']:
                raise ContractError('UPDATED_AT_REGRESSION')
        elif expected is not None:
            raise ContractError('MISSING_EXPECTED_RECORD')
        if record.get('lifecycle') == 'removed':
            if previous is None: raise ContractError('REMOVAL_REQUIRES_PRIOR_RECORD')
            record['source']['sha256']=previous['source']['sha256']
        else:
            record['source']['sha256']=digest(source_bytes(source))
        validate_record(record,repo,manifest)
        for peer in discover(repo,[owned_root.relative_to(repo.resolve()).as_posix()]):
            if peer!=manifest and load_json(peer).get('artifact_id')==record['artifact_id']:
                raise ContractError('DUPLICATE_ARTIFACT_ID')
        after=canonical_bytes(record)
        if before==after:
            action='unchanged'
        else:
            if before is not None and expected!=old_hash:
                raise ContractError('REVISION_CONFLICT')
            action = 'removed' if record['lifecycle']=='removed' else 'deprecated' if record['lifecycle']=='deprecated' else 'updated' if before else 'created'
            # Recheck content immediately before committing descriptor bytes.
            validate_record(record,repo,manifest)
            atomic_write(manifest,after)
        receipt={'schema_version':'1.0.0','owner':rules['producer'],'workflow_id':record['workflow_id'],
                 'artifact_actions':[{'artifact_id':record['artifact_id'],'artifact_type':record['artifact_type'],
                  'action':action,'source_path':record['source']['path'],
                  'manifest_path':manifest.relative_to(repo.resolve()).as_posix(),
                  'source_sha256':None if record['lifecycle']=='removed' else record['source']['sha256'],
                  'manifest_sha256':digest(after),'previous_manifest_sha256':old_hash,
                  'reason':request['reason']}],'validation':'passed'}
        validate_actions(receipt,repo)
        return receipt

def recover_lock(repo: Path, artifact_root: str | None = None) -> dict:
    root=resolve_owned_root(repo,artifact_root);lock=root/'.artifact-write.lock'
    if lock.is_symlink():raise ContractError('UNSAFE_LOCK')
    if not lock.exists():return {'status':'unchanged'}
    raw=lock.read_bytes()
    try:pid=int(raw)
    except ValueError as exc:raise ContractError('INVALID_LOCK_REQUIRES_MANUAL_REVIEW') from exc
    if pid<=0:raise ContractError('INVALID_LOCK_REQUIRES_MANUAL_REVIEW')
    try:os.kill(pid,0)
    except ProcessLookupError:pass
    except (PermissionError,OSError) as exc:raise ContractError('LOCK_OWNER_NOT_PROVEN_DEAD') from exc
    else:raise ContractError('LOCK_OWNER_LIVE')
    if lock.read_bytes()!=raw:raise ContractError('LOCK_CHANGED')
    lock.unlink()
    return {'status':'recovered','scope':'metadata-publication-lock-only'}

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['publish','validate-actions','validate-artifact','recover-lock'])
    parser.add_argument('--repo-root',required=True,type=Path)
    parser.add_argument('--input',type=Path)
    parser.add_argument('--artifact-root')
    args=parser.parse_args(argv)
    try:
        repo=repository_root(args.repo_root)
        if args.command=='recover-lock': result=recover_lock(repo,args.artifact_root)
        else:
            if args.input is None:raise ContractError('INPUT_REQUIRED')
            value=load_json(args.input)
            if args.command=='publish':result=publish(repo,value,args.artifact_root)
            elif args.command=='validate-actions':validate_actions(value,repo);result={'status':'pass'}
            else:validate_record(value,repo,args.input.resolve());result={'status':'pass'}
        print(canonical_bytes(result).decode(),end='');return 0
    except (ContractError,OSError,ValueError,KeyError,TypeError) as exc:
        code=str(exc) if isinstance(exc,ContractError) else type(exc).__name__
        print(json.dumps({'status':'fail','code':code}));return 1

if __name__=='__main__':raise SystemExit(main())
