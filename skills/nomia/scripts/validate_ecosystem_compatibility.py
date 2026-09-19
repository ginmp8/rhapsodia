#!/usr/bin/env python3
"""Validate coordinated package versions and local shared ecosystem contracts."""
from __future__ import annotations
import argparse, json, re
from pathlib import Path
from typing import Any
from ecosystem_handoff import load_compatibility, package_role, package_version
SHARED_FILES=("references/priority-contract.json","references/ecosystem-handoff-contract.json","references/ecosystem-compatibility.json","references/ecosystem-routing-contract.json","references/artifact-privacy-contract.json","references/ecosystem-ownership-contract.json","references/ecosystem-reproducibility-contract.json","evals/ecosystem-cross-skill-scenarios.json","scripts/validate_ecosystem_reproducibility.py","tests/test_ecosystem_reproducibility.py","references/ecosystem-migration.md")
SEMVER_HEADING=re.compile(r"^##\s+\[?(\d+\.\d+\.\d+)\]?\s+-",re.M)
def collect_errors(root:Path,peers:list[Path]|None=None)->list[str]:
 root=root.resolve(); errors=[]; manifest=load_compatibility(root); role=package_role(root); version=package_version(root)
 if manifest.get('schema_version')!='1.0.0' or manifest.get('contract_id')!='nomia-mago-magia-compatibility-v1': errors.append('invalid ecosystem compatibility manifest identity')
 if manifest.get('shared_contract_version')!='1.0.0': errors.append('invalid shared_contract_version')
 expected=str((manifest.get('packages') or {}).get(role) or '')
 if version!=expected or version!=manifest.get('ecosystem_release'): errors.append(f'{role} version {version} does not equal ecosystem release {manifest.get("ecosystem_release")}')
 policy=manifest.get('policy') or {}
 if policy.get('classification')!='coordinated-exact' or policy.get('mixed_versions_allowed') is not False: errors.append('compatibility policy must be coordinated-exact and reject mixed versions')
 changelog=(root/'CHANGELOG.md').read_text(encoding='utf-8'); versions=SEMVER_HEADING.findall(changelog)
 if not versions or versions[0]!=version: errors.append('CHANGELOG latest version must equal package version')
 release=json.loads((root/'release.json').read_text(encoding='utf-8'))
 if release.get('version')!=version or release.get('ecosystem_release')!=version or release.get('shared_contract_version')!=manifest.get('shared_contract_version'): errors.append('release.json identity mismatch')
 for rel in SHARED_FILES:
  if not (root/rel).is_file(): errors.append(f'missing shared contract: {rel}')
 local={rel:(root/rel).read_bytes() for rel in SHARED_FILES if (root/rel).is_file()}; seen={role}
 for peer in peers or []:
  peer=peer.resolve()
  try: pr=package_role(peer); pv=package_version(peer)
  except Exception as exc: errors.append(f'invalid peer {peer}: {exc}'); continue
  seen.add(pr)
  if pv!=version: errors.append(f'peer {pr} version {pv} differs from {version}')
  for rel,data in local.items():
   p=peer/rel
   if not p.is_file(): errors.append(f'peer {pr} missing {rel}')
   elif p.read_bytes()!=data: errors.append(f'peer {pr} differs for {rel}')
 if peers and seen!={'mago','magia','nomia'}: errors.append(f'peer set must cover mago, magia, and nomia; got {sorted(seen)}')
 return list(dict.fromkeys(errors))
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__); p.add_argument('--target',default=str(Path(__file__).resolve().parents[1])); p.add_argument('--peer-root',action='append',default=[]); p.add_argument('--json-output'); a=p.parse_args(argv); root=Path(a.target).resolve(); errors=collect_errors(root,[Path(x).resolve() for x in a.peer_root]); result={'status':'pass' if not errors else 'fail','target':str(root),'role':package_role(root),'version':package_version(root),'errors':errors}; text=json.dumps(result,indent=2,sort_keys=True)+'\n';
 if a.json_output: Path(a.json_output).write_text(text,encoding='utf-8')
 print(text,end=''); return 0 if not errors else 1
if __name__=='__main__': raise SystemExit(main())
