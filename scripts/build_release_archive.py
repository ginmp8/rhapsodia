#!/usr/bin/env python3
"""Build a deterministic full-project RhapsodIA ZIP and print a SHA-256 receipt."""
from __future__ import annotations
import argparse,hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EXCLUDED_DIRS={".git","__pycache__",".pytest_cache",".mypy_cache",".ruff_cache",".tox",".venv","venv","dist","build",".artifacts"}
EXCLUDED_NAMES={".DS_Store"};EXCLUDED_SUFFIXES={".pyc",".pyo",".zip"}
def include(p:Path)->bool:
 rel=p.relative_to(ROOT)
 if any(x in EXCLUDED_DIRS for x in rel.parts):return False
 if p.name in EXCLUDED_NAMES or p.suffix.lower() in EXCLUDED_SUFFIXES:return False
 if p.name==".env" or p.name.startswith(".env."):return False
 return p.is_file() and not p.is_symlink()
def sha256(p:Path)->str:
 h=hashlib.sha256()
 with p.open("rb") as f:
  for chunk in iter(lambda:f.read(1024*1024),b""):h.update(chunk)
 return h.hexdigest()
def main()->int:
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument("--version",required=True);ap.add_argument("--output",type=Path,required=True);a=ap.parse_args()
 out=a.output.resolve();out.parent.mkdir(parents=True,exist_ok=True);root=f"rhapsodia-{a.version}"
 files=sorted(p for p in ROOT.rglob("*") if include(p) and p.resolve()!=out)
 with zipfile.ZipFile(out,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for p in files:
   rel=p.relative_to(ROOT).as_posix();info=zipfile.ZipInfo(f"{root}/{rel}",date_time=(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=(0o755 if p.suffix==".py" else 0o644)<<16;z.writestr(info,p.read_bytes())
 print(json.dumps({"archive":str(out),"version":a.version,"file_count":len(files),"sha256":sha256(out),"size":out.stat().st_size},indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
