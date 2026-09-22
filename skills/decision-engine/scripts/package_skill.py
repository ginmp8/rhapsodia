#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, os, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

EXCLUDED_NAMES={'.DS_Store','__pycache__'}
EXCLUDED_SUFFIXES={'.pyc','.pyo','.zip'}

def sha256_file(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()

def files_for(root):
    out=[]
    for p in sorted(root.rglob('*'), key=lambda p:p.relative_to(root).as_posix()):
        if p.is_symlink(): raise ValueError(f'symlink not allowed: {p.relative_to(root)}')
        if not p.is_file(): continue
        rel=p.relative_to(root)
        if any(part in EXCLUDED_NAMES for part in rel.parts) or p.suffix in EXCLUDED_SUFFIXES: continue
        out.append((p,rel.as_posix()))
    return out

def tree_hash(entries):
    h=hashlib.sha256()
    for p,rel in entries:
        b=p.read_bytes(); rb=rel.encode('utf-8')
        h.update(len(rb).to_bytes(4,'big')); h.update(rb); h.update(len(b).to_bytes(8,'big')); h.update(b)
    return h.hexdigest()

def ensure_outside(target, path):
    rp=path.resolve(strict=False)
    try: rp.relative_to(target); raise ValueError(f'output must be outside target: {path}')
    except ValueError as exc:
        if str(exc).startswith('output must'): raise
    return rp

def restore(path, backup):
    if backup and backup.exists(): os.replace(backup,path)
    elif path.exists(): path.unlink()

def main():
    ap=argparse.ArgumentParser(description='Validate and deterministically package Decision Engine.')
    ap.add_argument('--target',required=True,type=Path); ap.add_argument('--output',required=True,type=Path); ap.add_argument('--receipt',type=Path)
    a=ap.parse_args(); target=a.target.resolve()
    if not (target/'SKILL.md').is_file(): raise SystemExit('missing target SKILL.md')
    output=ensure_outside(target,a.output); receipt=ensure_outside(target,a.receipt) if a.receipt else output.with_suffix(output.suffix+'.receipt.json')
    if output.suffix.lower()!='.zip': raise SystemExit('output must end in .zip')
    if output==receipt: raise SystemExit('output and receipt must differ')
    output.parent.mkdir(parents=True,exist_ok=True); receipt.parent.mkdir(parents=True,exist_ok=True)
    validator=target/'scripts/validate_skill.py'
    proc=subprocess.run([sys.executable,str(validator),str(target)],cwd=target,text=True,capture_output=True)
    if proc.returncode!=0:
        sys.stderr.write(proc.stdout+proc.stderr); return proc.returncode
    entries=files_for(target); candidate_hash=tree_hash(entries)
    tmpdir=Path(tempfile.mkdtemp(prefix='.decision-engine-package-',dir=output.parent))
    zip_tmp=tmpdir/'skill.zip'; receipt_tmp=tmpdir/'receipt.json'
    try:
        with zipfile.ZipFile(zip_tmp,'w',compression=zipfile.ZIP_STORED) as z:
            for p,rel in entries:
                info=zipfile.ZipInfo(f'decision-engine/{rel}',date_time=(1980,1,1,0,0,0)); info.compress_type=zipfile.ZIP_STORED; info.create_system=3; info.external_attr=(0o100644 & 0xFFFF)<<16
                z.writestr(info,p.read_bytes())
        with zipfile.ZipFile(zip_tmp,'r') as z:
            names=z.namelist()
            expected=[f'decision-engine/{rel}' for _,rel in entries]
            if names!=expected: raise ValueError('archive entry order/content mismatch')
            bad=z.testzip()
            if bad: raise ValueError(f'archive CRC failed: {bad}')
        archive_hash=sha256_file(zip_tmp)
        payload={"receipt_version":1,"status":"committed","stage":"validated-staged","target":"decision-engine","candidate_sha256":candidate_hash,"archive_sha256":archive_hash,"file_count":len(entries),"validation":"pass","archive_format":"zip-stored-normalized-v1","atomic_replace":True,"last_good_preserved_on_failure":True}
        receipt_tmp.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding='utf-8')
        out_backup=tmpdir/'old.zip' if output.exists() else None; rec_backup=tmpdir/'old.receipt' if receipt.exists() else None
        if out_backup: os.replace(output,out_backup)
        if rec_backup: os.replace(receipt,rec_backup)
        try:
            os.replace(zip_tmp,output); os.replace(receipt_tmp,receipt)
        except Exception:
            restore(output,out_backup); restore(receipt,rec_backup); raise
        print(json.dumps({**payload,"output":str(output),"receipt":str(receipt)},indent=2,sort_keys=True)); return 0
    finally:
        shutil.rmtree(tmpdir,ignore_errors=True)
if __name__=='__main__': raise SystemExit(main())
