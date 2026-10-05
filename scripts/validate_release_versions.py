#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SEMVER_RE=re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")

def main()->int:
 ap=argparse.ArgumentParser(description="Validate package-release version consistency.")
 ap.add_argument("--expected-version")
 a=ap.parse_args()
 catalog=json.loads((ROOT/"marketplace/catalog.json").read_text(encoding="utf-8"))
 expected=catalog["plugin"]["version"];errors=[]
 if not isinstance(expected,str) or not SEMVER_RE.fullmatch(expected):errors.append("plugin.version is not valid SemVer")
 if catalog["marketplace"]["version"]!=expected:errors.append("marketplace.version != plugin.version")
 if a.expected_version and expected!=a.expected_version:errors.append(f"package release {expected!r} != expected {a.expected_version!r}")
 for rel in [".claude-plugin/plugin.json",".cursor-plugin/plugin.json",".github/plugin/plugin.json",".codex-plugin/plugin.json"]:
  p=ROOT/rel
  if p.is_file():
   d=json.loads(p.read_text(encoding="utf-8"))
   if d.get("version")!=expected:errors.append(f"{rel}: version {d.get('version')!r} != {expected!r}")
 for rel in [".claude-plugin/marketplace.json",".cursor-plugin/marketplace.json",".github/plugin/marketplace.json"]:
  p=ROOT/rel
  if not p.is_file():continue
  d=json.loads(p.read_text(encoding="utf-8"))
  versions=[]
  if isinstance(d.get("version"),str):versions.append(("version",d["version"]))
  meta=d.get("metadata")
  if isinstance(meta,dict) and isinstance(meta.get("version"),str):versions.append(("metadata.version",meta["version"]))
  for i,item in enumerate(d.get("plugins",[]) if isinstance(d.get("plugins"),list) else []):
   if isinstance(item,dict) and isinstance(item.get("version"),str):versions.append((f"plugins[{i}].version",item["version"]))
  for field,value in versions:
   if value!=expected:errors.append(f"{rel}: {field} {value!r} != {expected!r}")
 m=ROOT/"MANIFEST.json"
 if m.is_file() and json.loads(m.read_text(encoding="utf-8")).get("package_version")!=expected:errors.append("MANIFEST.json package_version diverges")
 print(json.dumps({"status":"pass" if not errors else "fail","release_version":expected,"expected_version":a.expected_version,"errors":errors},indent=2))
 return 0 if not errors else 1
if __name__=="__main__":raise SystemExit(main())
