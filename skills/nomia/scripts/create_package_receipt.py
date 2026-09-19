#!/usr/bin/env python3
"""Create a machine-readable receipt for one frozen package candidate without reading peer packages."""
from __future__ import annotations
import argparse, hashlib, json
from datetime import datetime, timezone
from pathlib import Path

def digest_file(p:Path)->str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def tree_digest(root:Path)->str:
    h=hashlib.sha256(); blocked={'.git','__pycache__','.pytest_cache','.mypy_cache','.ruff_cache'}
    for p in sorted(root.rglob('*')):
        if not p.is_file() or p.is_symlink(): continue
        rel=p.relative_to(root)
        if any(x in blocked for x in rel.parts) or p.suffix in {'.pyc','.pyo','.zip'}: continue
        name=rel.as_posix().encode(); data=p.read_bytes(); h.update(len(name).to_bytes(4,'big')); h.update(name); h.update(len(data).to_bytes(8,'big')); h.update(data)
    return h.hexdigest()

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--target',default=str(Path(__file__).resolve().parents[1])); p.add_argument('--archive',required=True); p.add_argument('--baseline-source-manifest-sha256',required=True); p.add_argument('--validation-summary',action='append',default=[]); p.add_argument('--frozen',action='store_true'); p.add_argument('--output',required=True); a=p.parse_args(argv)
    root=Path(a.target).resolve(); archive=Path(a.archive).resolve(); release=json.loads((root/'release.json').read_text()); repro=json.loads((root/'references/ecosystem-reproducibility-contract.json').read_text())
    if not archive.is_file(): raise SystemExit('archive does not exist')
    out={'receipt_version':'1.0.0','status':'pass','stage':'package','generated_at':datetime.now(timezone.utc).replace(microsecond=0).isoformat(),'skill':release['name'],'version':release['version'],'ecosystem_release':release['ecosystem_release'],'shared_contract_version':repro['shared_contract_version'],'baseline_source_manifest_sha256':a.baseline_source_manifest_sha256,'candidate_tree_sha256':tree_digest(root),'archive_sha256':digest_file(archive),'archive_size_bytes':archive.stat().st_size,'shared_contract_sha256':digest_file(root/'references/ecosystem-reproducibility-contract.json'),'shared_provenance_sha256':digest_file(root/'references/ecosystem-contract-provenance.json'),'validation_summary':a.validation_summary,'frozen':bool(a.frozen)}
    path=Path(a.output); path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n',encoding='utf-8'); print(json.dumps(out,indent=2,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
