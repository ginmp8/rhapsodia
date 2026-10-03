#!/usr/bin/env python3
"""Data-only, deterministic package construction with external tree-bound evidence."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import tempfile
import zipfile

REQUIRED_GATES={'structure','tests','contracts'}
SKIP_DIRS={'.git','__pycache__','.pytest_cache','.mypy_cache','.ruff_cache','reports','generated-evidence','evidence'}
SKIP_FILES={'.DS_Store','.coverage'}
SKIP_SUFFIXES={'.pyc','.pyo','.tmp'}
DENIED_SUFFIXES={'.pem','.key','.p12','.pfx','.zip'}
MAX_FILE_BYTES=16*1024*1024
MAX_TREE_BYTES=128*1024*1024
SECRET_PATTERN=re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\bAKIA[0-9A-Z]{16}\b|\bgh[pousr]_[A-Za-z0-9]{30,}\b')


def file_hash(data:bytes)->str:return hashlib.sha256(data).hexdigest()

def json_bytes(value)->bytes:return (json.dumps(value,sort_keys=True,indent=2)+'\n').encode()

def no_symlink_path(path:Path)->None:
    for part in [path,*path.parents]:
        if part.is_symlink():raise ValueError('symbolic links are not allowed')

def outside(target:Path,path:Path)->Path:
    no_symlink_path(path)
    resolved=path.resolve()
    if resolved==target.resolve() or resolved.is_relative_to(target.resolve()):raise ValueError('output/evidence must be outside the target tree')
    if resolved.exists() and (not resolved.is_file() or resolved.stat().st_nlink!=1):raise ValueError('output/evidence must be an exclusive regular file')
    return resolved

def snapshot(target:Path)->dict[str,bytes]:
    no_symlink_path(target);root=target.resolve(strict=True);files={};folded=set();total=0
    for current,dirs,names in os.walk(root,followlinks=False):
        here=Path(current)
        for name in dirs+names:
            if (here/name).is_symlink():raise ValueError('symbolic links are not allowed')
        dirs[:]=sorted(d for d in dirs if d not in SKIP_DIRS)
        for name in sorted(names):
            path=here/name;relative=path.relative_to(root).as_posix()
            if name in SKIP_FILES or name.startswith('.coverage.') or path.suffix in SKIP_SUFFIXES:continue
            if name.lower().startswith('.env') or path.suffix.lower() in DENIED_SUFFIXES:
                raise ValueError('unsafe package path: '+relative)
            if not path.is_file() or path.stat().st_nlink!=1:raise ValueError('non-regular package entry')
            if relative.casefold() in folded:raise ValueError('nonportable case-colliding package paths')
            folded.add(relative.casefold())
            if path.stat().st_size>MAX_FILE_BYTES:raise ValueError('package file exceeds safety bound')
            data=path.read_bytes();total+=len(data)
            if total>MAX_TREE_BYTES:raise ValueError('package tree exceeds safety bound')
            if SECRET_PATTERN.search(data):raise ValueError('sensitive package content rejected: '+relative)
            files[relative]=data
    if 'SKILL.md' not in files:raise ValueError('missing root SKILL.md')
    if sum(p.endswith('SKILL.md') for p in files)!=1:raise ValueError('exactly one root skill required')
    return dict(sorted(files.items()))

def snapshot_digest(files:dict[str,bytes])->str:
    return file_hash(json_bytes([{'path':path,'sha256':file_hash(data),'size':len(data)} for path,data in files.items()]))

def tree_digest(target:Path)->str:return snapshot_digest(snapshot(target))

def verify_evidence(target:Path,path:Path|None,files:dict[str,bytes]|None=None)->dict:
    if path is None:raise ValueError('external validation evidence is required; package code is never executed')
    evidence=outside(target,path)
    if not evidence.is_file() or evidence.stat().st_size>2*1024*1024:raise ValueError('invalid validation evidence file')
    def unique(pairs):
        result={}
        for key,value in pairs:
            if key in result:raise ValueError('duplicate evidence JSON key')
            result[key]=value
        return result
    value=json.loads(evidence.read_text(encoding='utf-8'),object_pairs_hook=unique,parse_constant=lambda x: (_ for _ in ()).throw(ValueError('nonfinite evidence JSON')))
    if not isinstance(value,dict) or set(value)!={'schema_version','evidence_kind','target_tree_sha256','runner_sha256','gates'}:raise ValueError('invalid validation evidence fields')
    if not isinstance(value,dict) or value.get('schema_version')!='1.0.0' or value.get('evidence_kind')!='executed':raise ValueError('invalid validation evidence contract')
    if value.get('target_tree_sha256')!=snapshot_digest(files if files is not None else snapshot(target)):
        raise ValueError('stale validation evidence: target_tree_sha256 mismatch')
    gates=value.get('gates')
    if not isinstance(gates,list) or len(gates)!=len(REQUIRED_GATES) or {g.get('name') for g in gates if isinstance(g,dict)}!=REQUIRED_GATES:
        raise ValueError('required validation gates are missing or duplicated')
    for gate in gates:
        if not isinstance(gate,dict) or set(gate)!={'name','status','returncode','command','output_sha256'}:raise ValueError('invalid validation gate fields')
        if gate.get('status')!='pass' or type(gate.get('returncode')) is not int or gate['returncode']!=0:
            raise ValueError('validation gate did not pass')
        if not isinstance(gate.get('command'),list) or not gate['command'] or not all(isinstance(x,str) and x for x in gate['command']):
            raise ValueError('validation command evidence missing')
        if not re.fullmatch('[a-f0-9]{64}',str(gate.get('output_sha256',''))):raise ValueError('validation output hash missing')
    if not re.fullmatch('[a-f0-9]{64}',str(value.get('runner_sha256',''))):raise ValueError('runner identity missing')
    return value

def atomic_bytes(path:Path,data:bytes)->None:
    no_symlink_path(path);path.parent.mkdir(parents=True,exist_ok=True)
    fd,name=tempfile.mkstemp(prefix='.'+path.name+'-',suffix='.tmp',dir=path.parent)
    try:
        with os.fdopen(fd,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
        os.replace(name,path)
    finally:Path(name).unlink(missing_ok=True)

def deterministic_zip(target:Path,output:Path,*,root_name:str|None=None,evidence:Path|None=None,require_evidence:bool=True,archive_validator=None)->dict:
    output=outside(target,output)
    if evidence is not None and outside(target,evidence)==output:raise ValueError('archive must not alias validation evidence')
    files=snapshot(target);source_digest=snapshot_digest(files)
    if require_evidence:verify_evidence(target,evidence,files)
    if root_name is None:
        text=files['SKILL.md'].decode('utf-8')
        match=re.search(r'(?m)^name:\s*([a-z0-9-]+)\s*$',text)
        root_name=match.group(1) if match else target.name
    if not re.fullmatch('[a-z0-9][a-z0-9-]*',root_name):raise ValueError('invalid archive root')
    output.parent.mkdir(parents=True,exist_ok=True)
    fd,temporary=tempfile.mkstemp(prefix='.'+output.name+'-',suffix='.tmp',dir=output.parent);os.close(fd)
    try:
        stage=Path(temporary)
        with zipfile.ZipFile(stage,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
            for relative,data in files.items():
                info=zipfile.ZipInfo(root_name+'/'+relative,(2026,1,1,0,0,0));info.create_system=3
                info.external_attr=0o100644<<16;info.compress_type=zipfile.ZIP_DEFLATED
                archive.writestr(info,data)
        with zipfile.ZipFile(stage) as archive:
            if archive.testzip():raise ValueError('archive CRC failure')
            if {name.split('/',1)[1]:archive.read(name) for name in archive.namelist()}!=files:raise ValueError('archive content mismatch')
        if archive_validator:
            result=archive_validator(stage)
            errors=result if isinstance(result,list) else result.get('errors',[])
            if errors:raise ValueError('staged archive validation failed: '+'; '.join(errors[:5]))
        if tree_digest(target)!=source_digest:raise ValueError('source changed during packaging')
        archive_hash=file_hash(stage.read_bytes())
        os.replace(stage,output)
        return {'output':str(output),'file_count':len(files),'size_bytes':output.stat().st_size,'excluded':[],
                'candidate_tree_sha256':source_digest,'archive_sha256':archive_hash,'target_code_executed':False,
                'validation_evidence_sha256':file_hash(evidence.read_bytes()) if evidence else None}
    finally:Path(temporary).unlink(missing_ok=True)
