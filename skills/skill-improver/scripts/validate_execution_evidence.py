#!/usr/bin/env python3
"""Validate environment or stochastic execution evidence with stdlib only."""
from __future__ import annotations
import argparse, hashlib, importlib.util, json
from pathlib import Path
from typing import Any


def canonical_digest(data: Any) -> str:
    raw=json.dumps(data,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def validate_environment(data: Any) -> dict[str, Any]:
    errors=[]
    if not isinstance(data,dict): return {"status":"fail","errors":["root:expected-object"]}
    if data.get("profile_version") != 1: errors.append("profile_version:expected-1")
    for key in ("host_or_harness","model","reasoning_profile"):
        if not isinstance(data.get(key),str) or not data.get(key): errors.append(f"{key}:required-string")
    tools=data.get("toolset")
    if not isinstance(tools,list) or any(not isinstance(x,str) or not x for x in tools): errors.append("toolset:expected-string-list")
    if len(tools or []) != len(set(tools or [])): errors.append("toolset:duplicates")
    if not isinstance(data.get("environment"),dict): errors.append("environment:expected-object")
    if not isinstance(data.get("budget"),dict): errors.append("budget:expected-object")
    identity={k:v for k,v in data.items() if k != "identity_digest"}
    return {"status":"pass" if not errors else "fail","errors":errors,"identity_digest":canonical_digest(identity)}


def validate_stochastic(data: Any) -> dict[str, Any]:
    module_path = Path(__file__).with_name("summarize_paired_trials.py")
    spec = importlib.util.spec_from_file_location("skill_improver_paired_trials", module_path)
    if spec is None or spec.loader is None:
        return {"status":"fail","errors":["stochastic:unable-to-load-summarizer"]}
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.summarize(data, 3)


def main() -> int:
    ap=argparse.ArgumentParser(description="Validate Skill Improver execution evidence.")
    ap.add_argument("--kind",choices=["environment","stochastic"],required=True)
    ap.add_argument("--input",type=Path,required=True)
    ap.add_argument("--json-output",type=Path)
    args=ap.parse_args()
    try:
        data=json.loads(args.input.read_text(encoding="utf-8"))
        result=validate_environment(data) if args.kind=="environment" else validate_stochastic(data)
    except Exception as exc:
        result={"status":"fail","errors":[f"input:{exc}"]}
    payload=json.dumps(result,indent=2,sort_keys=True)
    if args.json_output:
        args.json_output.parent.mkdir(parents=True,exist_ok=True)
        args.json_output.write_text(payload+"\n",encoding="utf-8")
    print(payload)
    return 0 if result.get("status")=="pass" else 1

if __name__ == "__main__":
    raise SystemExit(main())
