#!/usr/bin/env python3
"""Run explicitly trusted skill gates and issue external, tree-bound evidence.

This is the execution boundary. Packaging itself never executes target code.
Only use --trust-target-code after inspecting the target. An unsigned receipt is
not an authentication credential; pass it directly from a trusted validation run.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

# This controller hashes files without importing any target-owned module.
SKIP_DIRS={'.git','__pycache__','.pytest_cache','.mypy_cache','.ruff_cache','reports','generated-evidence','evidence'}
SKIP_SUFFIXES={'.pyc','.pyo','.tmp'}
def digest(data):return hashlib.sha256(data).hexdigest()
def tree_digest(root):
    items=[]
    for current,dirs,files in os.walk(root,followlinks=False):
        here=Path(current)
        if any((here/name).is_symlink() for name in dirs+files):raise ValueError('symlink in target')
        dirs[:]=sorted(d for d in dirs if d not in SKIP_DIRS)
        for name in sorted(files):
            p=here/name
            if name in {'.DS_Store','.coverage'} or name.startswith('.coverage.') or p.suffix in SKIP_SUFFIXES:continue
            if not p.is_file() or p.stat().st_nlink!=1:raise ValueError('nonexclusive target file')
            data=p.read_bytes();items.append({'path':p.relative_to(root).as_posix(),'sha256':digest(data),'size':len(data)})
    items.sort(key=lambda x:x['path']);return digest((json.dumps(items,sort_keys=True,indent=2)+'\n').encode())
def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--target',required=True,type=Path);p.add_argument('--output',required=True,type=Path)
    p.add_argument('--trust-target-code',action='store_true');p.add_argument('--timeout',type=int,default=420)
    a=p.parse_args(argv)
    try:
        if not a.trust_target_code:raise ValueError('explicit --trust-target-code is required before executing validators/tests')
        root=a.target.resolve(strict=True);output=a.output.resolve()
        if a.target.is_symlink() or any(x.is_symlink() for x in [a.output,*a.output.parents]) or output.is_relative_to(root):raise ValueError('unsafe target/evidence path')
        if not 1<=a.timeout<=1800:raise ValueError('timeout must be in 1..1800 seconds')
        before=tree_digest(root)
        structure=[sys.executable,'-B',str(root/'scripts/validate_skill_package.py')]+([str(root)] if json.loads((root/'release.json').read_text()).get('name')=='mago' else ['--target',str(root)])
        gates=[('structure',structure),('tests',[sys.executable,'-B','-m','pytest','-q','-p','no:cacheprovider',str(root/'tests')]),
               ('contracts',[sys.executable,'-B',str(root/'scripts/validate_native_contracts.py')])]
        results=[];env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','PYTHONPATH':str(root/'scripts'),'MAGIA_TEST_SUITE_ACTIVE':'1'}
        for name,command in gates:
            run=subprocess.run(command,cwd=root,env=env,capture_output=True,text=True,timeout=a.timeout)
            result={'name':name,'command':command,'returncode':run.returncode,'status':'pass' if run.returncode==0 else 'fail',
                    'output_sha256':digest((run.stdout+'\n'+run.stderr).encode())}
            results.append(result)
            print(json.dumps({'gate':name,'status':result['status'],'returncode':run.returncode,'tail':(run.stdout+'\n'+run.stderr)[-1500:]}),flush=True)
            if run.returncode:raise ValueError('validation failed; existing evidence left unchanged')
        if before!=tree_digest(root):raise ValueError('source changed during validation')
        receipt={'schema_version':'1.0.0','evidence_kind':'executed','target_tree_sha256':before,
                 'runner_sha256':digest(Path(__file__).read_bytes()),'gates':results}
        output.parent.mkdir(parents=True,exist_ok=True)
        fd,temp=tempfile.mkstemp(prefix='.'+output.name+'-',dir=output.parent)
        try:
            with os.fdopen(fd,'w') as f:json.dump(receipt,f,indent=2,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
            os.replace(temp,output)
        finally:Path(temp).unlink(missing_ok=True)
        print(json.dumps({'status':'pass','evidence':str(output),'target_tree_sha256':before}));return 0
    except (ValueError,OSError,subprocess.TimeoutExpired) as exc:
        print(json.dumps({'status':'fail','error':str(exc)}));return 1
if __name__=='__main__':raise SystemExit(main())
