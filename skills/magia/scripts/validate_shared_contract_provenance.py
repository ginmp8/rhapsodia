#!/usr/bin/env python3
"""Validate local generated copies of shared ecosystem contracts against release provenance."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path


def digest(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()

def validate(root: Path) -> dict:
    errors=[]
    path=root/"references/ecosystem-contract-provenance.json"
    try: data=json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc: return {"status":"fail","errors":[f"invalid provenance: {exc}"]}
    version=(root/"VERSION").read_text(encoding="utf-8").strip()
    if data.get("ecosystem_release") != version: errors.append("provenance release does not match VERSION")
    if data.get("runtime_independent_local_copies") is not True: errors.append("provenance must preserve runtime-independent local copies")
    files=data.get("files")
    if not isinstance(files,dict) or not files: errors.append("provenance files must be a non-empty object"); files={}
    for rel, expected in sorted(files.items()):
        candidate=root/rel
        if not candidate.is_file(): errors.append(f"missing shared generated file: {rel}")
        elif digest(candidate) != expected: errors.append(f"shared file digest mismatch: {rel}")
    return {"status":"pass" if not errors else "fail","errors":errors,"checked":len(files),"ecosystem_release":version}

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument("--target",default=str(Path(__file__).resolve().parents[1])); parser.add_argument("--json-output")
    args=parser.parse_args(argv); result=validate(Path(args.target).resolve())
    if args.json_output: Path(args.json_output).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(f"status: {result['status']}"); print(f"checked: {result.get('checked',0)}")
    for error in result["errors"]: print(f"ERROR: {error}")
    return 0 if result["status"]=="pass" else 1
if __name__=="__main__": raise SystemExit(main())
