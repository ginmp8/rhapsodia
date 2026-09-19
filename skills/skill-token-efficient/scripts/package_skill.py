#!/usr/bin/env python3
"""Build a deterministic skill.zip with atomic delivery and a durable receipt."""
from __future__ import annotations
import argparse, hashlib, json, os, shutil, sys, tempfile, zipfile
from pathlib import Path

BLOCKED_DIRS={".git","__pycache__",".pytest_cache",".mypy_cache",".ruff_cache","node_modules",".venv","venv"}
BLOCKED_SUFFIXES={".pyc",".pyo",".zip"}
FIXED_TIME=(1980,1,1,0,0,0)

def files(root: Path):
    for dirpath, dirs, names in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in BLOCKED_DIRS)
        for name in sorted(names):
            p=Path(dirpath)/name
            if p.suffix.lower() not in BLOCKED_SUFFIXES and not p.is_symlink(): yield p

def tree_hash(root: Path) -> str:
    h=hashlib.sha256()
    for p in files(root):
        rel=p.relative_to(root).as_posix().encode(); data=p.read_bytes()
        h.update(len(rel).to_bytes(4,"big")); h.update(rel); h.update(len(data).to_bytes(8,"big")); h.update(hashlib.sha256(data).digest())
    return h.hexdigest()

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()

def preflight(target: Path, output: Path, receipt: Path|None) -> list[str]:
    errors=[]
    if not target.is_dir(): errors.append("target must be a directory")
    roots=[p for p in target.rglob("SKILL.md") if not any(x in BLOCKED_DIRS for x in p.relative_to(target).parts)] if target.exists() else []
    if len(roots)!=1 or (roots and roots[0]!=target/"SKILL.md"): errors.append(f"expected exactly one root SKILL.md, found {len(roots)}")
    for p,label in [(output,"output"),(receipt,"receipt")]:
        if p is None: continue
        try: p.resolve().relative_to(target.resolve()); errors.append(f"{label} must be outside target")
        except ValueError: pass
    if receipt is not None and output.resolve()==receipt.resolve(): errors.append("output and receipt must differ")
    return errors

def validate_zip(path: Path) -> tuple[bool,list[str],int]:
    errors=[]
    try:
        with zipfile.ZipFile(path) as z:
            names=z.namelist()
            if names.count("SKILL.md")!=1: errors.append("archive must contain one root SKILL.md")
            bad=[n for n in names if n.endswith(".zip") or "__pycache__" in n or "/.git/" in "/"+n]
            if bad: errors.append("archive contains blocked entries: "+", ".join(bad[:10]))
            if names!=sorted(names): errors.append("archive entries are not deterministically sorted")
            for info in z.infolist():
                if info.date_time!=FIXED_TIME: errors.append(f"non-deterministic timestamp: {info.filename}"); break
            return not errors,errors,len(names)
    except Exception as exc:
        return False,[f"invalid zip: {exc}"],0

def build_zip(target: Path, staged: Path) -> int:
    count=0
    with zipfile.ZipFile(staged,"w",zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in files(target):
            arc=p.relative_to(target).as_posix(); info=zipfile.ZipInfo(arc,FIXED_TIME); info.compress_type=zipfile.ZIP_DEFLATED; info.external_attr=(0o755 if p.suffix==".py" else 0o644)<<16
            z.writestr(info,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9); count+=1
    return count

def atomic_commit(staged: Path, output: Path, staged_receipt: Path|None, receipt: Path|None) -> None:
    backups=[]
    try:
        for dest in [output, receipt]:
            if dest is None or not dest.exists(): continue
            backup=dest.with_name(dest.name+".last-good")
            if backup.exists(): backup.unlink()
            os.replace(dest,backup); backups.append((dest,backup))
        os.replace(staged,output)
        if staged_receipt is not None and receipt is not None: os.replace(staged_receipt,receipt)
        for _,backup in backups:
            if backup.exists(): backup.unlink()
    except Exception:
        for dest in [output, receipt]:
            if dest is not None and dest.exists():
                try: dest.unlink()
                except Exception: pass
        for dest,backup in backups:
            if backup.exists(): os.replace(backup,dest)
        raise

def main() -> int:
    ap=argparse.ArgumentParser(description="Package a frozen skill candidate deterministically.")
    ap.add_argument("--target",required=True); ap.add_argument("--output",required=True); ap.add_argument("--receipt"); ap.add_argument("--validate",action="store_true")
    args=ap.parse_args(); target=Path(args.target).resolve(); output=Path(args.output).resolve(); output=output if output.suffix==".zip" else output/"skill.zip"; receipt=Path(args.receipt).resolve() if args.receipt else None
    errors=preflight(target,output,receipt)
    if errors: print(json.dumps({"status":"fail","stage":"preflight","errors":errors},indent=2),file=sys.stderr); return 2
    output.parent.mkdir(parents=True,exist_ok=True)
    if receipt: receipt.parent.mkdir(parents=True,exist_ok=True)
    stage_dir=Path(tempfile.mkdtemp(prefix="skill-package-",dir=str(output.parent)))
    staged=stage_dir/output.name; staged_receipt=stage_dir/(receipt.name if receipt else "receipt.json")
    try:
        count=build_zip(target,staged)
        ok,zip_errors,validated_count=validate_zip(staged)
        if args.validate and not ok:
            print(json.dumps({"status":"fail","stage":"validation","errors":zip_errors},indent=2),file=sys.stderr); return 3
        package_hash=sha256(staged); target_hash=tree_hash(target)
        payload={"receipt_version":1,"status":"pass","stage":"package","target":str(target),"target_tree_sha256":target_hash,"package_path":str(output),"package_sha256":package_hash,"file_count":validated_count if args.validate else count,"deterministic_zip":True,"validated":bool(args.validate)}
        if receipt:
            with staged_receipt.open("w",encoding="utf-8",newline="\n") as f:
                json.dump(payload,f,ensure_ascii=False,indent=2,sort_keys=True); f.write("\n"); f.flush(); os.fsync(f.fileno())
        atomic_commit(staged,output,staged_receipt if receipt else None,receipt)
        print(json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)); return 0
    except Exception as exc:
        print(json.dumps({"receipt_version":1,"status":"fail","stage":"commit","error":str(exc),"output":str(output),"receipt":str(receipt) if receipt else None},indent=2),file=sys.stderr); return 4
    finally:
        shutil.rmtree(stage_dir,ignore_errors=True)

if __name__=="__main__":
    raise SystemExit(main())
