#!/usr/bin/env python3
"""Structural validation only; execution tests are a separate mandatory release gate."""
from __future__ import annotations
import argparse, ast, json, re
from pathlib import Path
from package_evidence import snapshot

def validate(root):
    errors=[]
    try:
        files=snapshot(root)
        text=files['SKILL.md'].decode('utf-8')
        if not text.startswith('---\n') or '\nname: rhapsodia-workspace\n' not in text:errors.append('invalid skill frontmatter')
        for ref in re.findall(r'\[[^\]]+\]\(([^)]+)\)',text):
            if '://' not in ref and ref.split('#')[0] not in files:errors.append('missing reference: '+ref)
        required=['assets/workspace.html','VERSION','release.json','agents/openai.yaml','scripts/workspace.py','scripts/validate_native_contracts.py','references/artifact-actions.schema.json','references/artifact-envelope.schema.json']
        errors.extend('missing '+x for x in required if x not in files)
        for name,data in files.items():
            if name.endswith('.py'):ast.parse(data.decode(),filename=name)
            if name.endswith('.json'):json.loads(data)
        release=json.loads(files['release.json'])
        if release['version']!=files['VERSION'].decode().strip():errors.append('release version mismatch')
    except (ValueError,OSError,SyntaxError,KeyError) as exc:errors.append(str(exc))
    return {'status':'pass' if not errors else 'fail','errors':errors,'evidence_level':'structural'}
def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--target',type=Path,default=Path(__file__).resolve().parents[1]);a=p.parse_args(argv)
    result=validate(a.target);print(json.dumps(result,indent=2));return 0 if result['status']=='pass' else 1
if __name__=='__main__':raise SystemExit(main())
