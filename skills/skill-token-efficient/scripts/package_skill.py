#!/usr/bin/env python3
import argparse,os,sys,zipfile
from pathlib import Path
B={'.git','__pycache__','.pytest_cache','.mypy_cache','.ruff_cache','node_modules'}; X={'.pyc','.pyo','.zip'}
def main():
 p=argparse.ArgumentParser(); p.add_argument('--target',required=True); p.add_argument('--output',required=True); p.add_argument('--validate',action='store_true'); a=p.parse_args(); t=Path(a.target).resolve(); o=Path(a.output).resolve(); o=o if o.suffix=='.zip' else o/'skill.zip'
 r=[x for x in t.rglob('SKILL.md') if not any(y in B for y in x.relative_to(t).parts)]
 if len(r)!=1: print(f'ERROR: expected one SKILL.md, found {len(r)}',file=sys.stderr); return 1
 s=r[0].read_text(encoding='utf-8',errors='replace')
 if 'name:' not in s or 'description:' not in s: print('ERROR: bad frontmatter',file=sys.stderr); return 1
 o.parent.mkdir(parents=True,exist_ok=True); c=0
 with zipfile.ZipFile(o,'w',zipfile.ZIP_DEFLATED) as z:
  for root,dirs,fs in os.walk(t):
   dirs[:]=[d for d in dirs if d not in B]
   for f in sorted(fs):
    q=Path(root)/f
    if q.suffix not in X and not q.is_symlink(): z.write(q,q.relative_to(t).as_posix()); c+=1
 if not c: print('ERROR: empty archive',file=sys.stderr); return 1
 print(f'wrote {o}')
 if a.validate:
  n=zipfile.ZipFile(o).namelist(); bad=[x for x in n if x.endswith('.zip') or '__pycache__' in x or '/.git/' in '/'+x]
  if n.count('SKILL.md')!=1 or bad: print('ERROR: invalid archive',file=sys.stderr); return 1
  print(f'validated {o} ({len(n)} files)')
 return 0
if __name__=='__main__': raise SystemExit(main())
