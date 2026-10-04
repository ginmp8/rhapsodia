#!/usr/bin/env python3
from __future__ import annotations
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 catalog=json.loads((ROOT/"marketplace/catalog.json").read_text(encoding="utf-8"))
 expected=catalog["plugin"]["version"]; errors=[]
 if catalog["marketplace"]["version"]!=expected: errors.append("marketplace.version != plugin.version")
 if expected!="0.3.0": errors.append("package release must remain 0.3.0")
 for rel in [".claude-plugin/plugin.json",".cursor-plugin/plugin.json",".github/plugin/plugin.json",".codex-plugin/plugin.json"]:
  p=ROOT/rel
  if p.is_file():
   d=json.loads(p.read_text(encoding="utf-8"))
   if d.get("version")!=expected: errors.append(f"{rel}: version {d.get('version')!r} != {expected!r}")
 m=ROOT/"MANIFEST.json"
 if m.is_file() and json.loads(m.read_text(encoding="utf-8")).get("package_version")!=expected: errors.append("MANIFEST.json package_version diverges")
 print(json.dumps({"status":"pass" if not errors else "fail","release_version":expected,"errors":errors},indent=2))
 return 0 if not errors else 1
if __name__=="__main__":raise SystemExit(main())
