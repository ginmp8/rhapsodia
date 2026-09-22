#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path

MANIFEST=Path('contracts/integration-manifest.json')
ROLES={'owner','owner-producer'}

def sha256_file(path:Path)->str:
 h=hashlib.sha256()
 with path.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()

def load_root(root:Path)->tuple[dict|None,list[str]]:
 errors=[];path=root/MANIFEST
 if not path.is_file():return None,[f'manifest:missing:{root}']
 try:d=json.loads(path.read_text(encoding='utf-8'))
 except Exception as exc:return None,[f'manifest:unreadable:{root}:{exc.__class__.__name__}']
 if not isinstance(d,dict):return None,[f'manifest:invalid_root:{root}']
 if d.get('manifest_version')!=1:errors.append(f'manifest:unsupported_version:{root}')
 if d.get('skill')!=root.name:errors.append(f'manifest:skill_name_mismatch:{root}')
 for section in ('exports','imports'):
  if not isinstance(d.get(section),list):errors.append(f'manifest:{section}_invalid:{root}')
 seen_exports=set();seen_imports=set()
 for i,e in enumerate(d.get('exports',[]) if isinstance(d.get('exports'),list) else []):
  if not isinstance(e,dict):errors.append(f'export:{i}:invalid:{root}');continue
  cid=e.get('contract_id')
  if not isinstance(cid,str) or not cid:errors.append(f'export:{i}:contract_id_invalid:{root}')
  elif cid in seen_exports:errors.append(f'export:{i}:duplicate_contract:{cid}:{root}')
  else:seen_exports.add(cid)
  if not isinstance(e.get('version'),int) or isinstance(e.get('version'),bool) or e['version']<=0:errors.append(f'export:{i}:version_invalid:{root}')
  if e.get('role') not in ROLES:errors.append(f'export:{i}:role_invalid:{root}')
  paths=e.get('surface_paths')
  if not isinstance(paths,list) or not paths:errors.append(f'export:{i}:surface_paths_invalid:{root}')
  else:
   for rel in paths:
    if not isinstance(rel,str) or not rel or not (root/rel).is_file():errors.append(f'export:{i}:surface_missing:{rel}:{root}')
 for i,e in enumerate(d.get('imports',[]) if isinstance(d.get('imports'),list) else []):
  if not isinstance(e,dict):errors.append(f'import:{i}:invalid:{root}');continue
  cid=e.get('contract_id')
  if not isinstance(cid,str) or not cid:errors.append(f'import:{i}:contract_id_invalid:{root}')
  elif cid in seen_imports:errors.append(f'import:{i}:duplicate_contract:{cid}:{root}')
  else:seen_imports.add(cid)
  versions=e.get('accepted_versions')
  if not isinstance(versions,list) or not versions or any(not isinstance(v,int) or isinstance(v,bool) or v<=0 for v in versions):errors.append(f'import:{i}:accepted_versions_invalid:{root}')
 return d,errors

def export_map(manifest):return {e['contract_id']:e for e in (manifest or {}).get('exports',[]) if isinstance(e,dict) and e.get('contract_id')}
def imports(manifest):return [e for e in (manifest or {}).get('imports',[]) if isinstance(e,dict)]
def surface_digest(root:Path,export:dict)->str|None:
 try:
  rows=[(rel,sha256_file(root/rel)) for rel in sorted(export.get('surface_paths',[]))]
  return hashlib.sha256(json.dumps(rows,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
 except OSError:return None

def discover_peers(args,target):
 roots=[];target_manifest,_=load_root(target);target_skill=(target_manifest or {}).get('skill',target.name)
 def add(p,skip_same=False):
  p=Path(p).resolve()
  if p==target or p in roots or not (p/MANIFEST).is_file():return
  if skip_same and (load_root(p)[0] or {}).get('skill')==target_skill:return
  roots.append(p)
 for p in args.peer or []:add(p)
 if args.catalog_root:
  cr=Path(args.catalog_root).resolve()
  if cr.is_dir():
   for p in sorted(cr.iterdir()):
    if p.is_dir():add(p,True)
 return roots

def peer_catalog_fingerprint(peers:list[tuple[Path,dict]])->str|None:
 if not peers:return None
 rows=[]
 for root,m in peers:
  manifest=root/MANIFEST
  digest=hashlib.sha256(manifest.read_bytes()).hexdigest() if manifest.is_file() else 'missing'
  rows.append(f"{m.get('skill','?')}|{root.resolve()}|{digest}")
 return hashlib.sha256("\n".join(sorted(rows)).encode('utf-8')).hexdigest()

def analyze(target:Path,baseline:Path|None,peer_roots:list[Path],require_peer_catalog:bool=False)->dict:
 errors=[];warnings=[]
 tm,te=load_root(target);errors.extend(te)
 bm=None
 if baseline:
  if (baseline/MANIFEST).is_file():bm,be=load_root(baseline);errors.extend(be)
  else:warnings.append('baseline_manifest:missing:new_contract_surface_or_unmanaged_baseline')
 peers=[]
 for root in peer_roots:
  m,e=load_root(root);errors.extend(e)
  if m:peers.append((root,m))
 if not peers:
  if require_peer_catalog:errors.append('peer_catalog:required_but_empty:ecosystem_compatibility_not_proven')
  else:warnings.append('peer_catalog:empty:ecosystem_compatibility_not_proven')
 if tm:
  catalog=[(target,tm)]+peers
  owners={}
  for root,m in catalog:
   for exp in m.get('exports',[]):
    if isinstance(exp,dict) and exp.get('contract_id'):
     owners.setdefault(exp['contract_id'],[]).append((root,m,exp))
  for cid,rows in owners.items():
   if len(rows)>1:errors.append(f'contract:{cid}:multiple_owners:'+','.join(sorted(m.get('skill','?') for _,m,_ in rows)))
  texp=export_map(tm);bexp=export_map(bm)
  if bm:
   for cid,cur in texp.items():
    old=bexp.get(cid)
    if old:
     oldd=surface_digest(baseline,old);curd=surface_digest(target,cur)
     if oldd and curd and oldd!=curd and old.get('version')==cur.get('version'):errors.append(f'contract:{cid}:surface_changed_without_version_bump:v{cur.get("version")}')
   for cid in sorted(set(bexp)-set(texp)):
    consumers=[m.get('skill') for _,m in peers if any(i.get('contract_id')==cid for i in imports(m))]
    if consumers:errors.append(f'contract:{cid}:removed_with_consumers:{",".join(sorted(consumers))}')
  # Validate every known import against the unique owner.
  for _,m in catalog:
   for imp in imports(m):
    cid=imp.get('contract_id');accepted=imp.get('accepted_versions',[]);rows=owners.get(cid,[])
    if len(rows)==1:
     owner_skill=rows[0][1].get('skill');version=rows[0][2].get('version')
     if version not in accepted:errors.append(f'contract:{cid}:consumer_incompatible:{m.get("skill")}:owner_{owner_skill}_v{version}:accepts_{accepted}')
    elif len(rows)==0 and peers:errors.append(f'contract:{cid}:unresolved_import:{m.get("skill")}:accepts_{accepted}')
 status='fail' if errors else ('pass-with-warnings' if warnings else 'pass')
 return {'status':status,'target':str(target),'baseline':str(baseline) if baseline else None,'peer_count':len(peers),'peer_roots':[str(root.resolve()) for root,_ in peers],'peer_catalog_fingerprint':peer_catalog_fingerprint(peers),'peer_catalog_required':require_peer_catalog,'errors':sorted(set(errors)),'warnings':sorted(set(warnings))}

def main()->int:
 ap=argparse.ArgumentParser();ap.add_argument('--target',required=True);ap.add_argument('--baseline');ap.add_argument('--peer',action='append');ap.add_argument('--catalog-root');ap.add_argument('--require-peer-catalog',action='store_true');ap.add_argument('--json-output');a=ap.parse_args()
 target=Path(a.target).resolve();baseline=Path(a.baseline).resolve() if a.baseline else None
 report=analyze(target,baseline,discover_peers(a,target),require_peer_catalog=a.require_peer_catalog);payload=json.dumps(report,indent=2,sort_keys=True)+'\n'
 if a.json_output:Path(a.json_output).write_text(payload,encoding='utf-8')
 print(payload,end='');return 0 if report['status']!='fail' else 2
if __name__=='__main__':sys.exit(main())
