#!/usr/bin/env python3
"""Scan added text lines in Git history for likely credential exposure."""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path

# Loading the bundled detector is read-only; do not create __pycache__ inside the skill package.
sys.dont_write_bytecode = True

def _load_detector():
    sibling = Path(__file__).with_name("scan_secrets.py")
    spec = importlib.util.spec_from_file_location("secure_code_review_scan_secrets", sibling)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load bundled scan_secrets.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module

_DETECTOR = _load_detector()
SEVERITY_ORDER = _DETECTOR.SEVERITY_ORDER
scan_line = _DETECTOR.scan_line

SCHEMA_VERSION=1
COMMIT_PREFIX='@@SCR_COMMIT@@'
HUNK_RE=re.compile(r'^@@ -(?:\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@')

def hid(commit,path,line,rule,base_id):
    m=f'{commit}\n{path}\n{line}\n{rule}\n{base_id}'.encode()
    return 'scrh-'+hashlib.sha256(m).hexdigest()[:16]

def atomic_write(path: Path, text: str, *, input_root: Path):
    path=path.expanduser()
    if path.exists() and path.is_symlink(): raise ValueError(f'Refusing symbolic-link output path: {path}')
    try:
        if path.resolve(strict=False)==input_root.resolve(strict=True): raise ValueError('Output path aliases repository input')
    except OSError as exc: raise ValueError(f'Could not resolve output/input path safely: {exc}') from exc
    path.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix=f'.{path.name}.',suffix='.tmp',dir=str(path.parent))
    try:
        with os.fdopen(fd,'w',encoding='utf-8') as h:
            h.write(text); h.flush(); os.fsync(h.fileno())
        os.replace(tmp,path)
    except Exception:
        try: os.unlink(tmp)
        except OSError: pass
        raise

def scan(repo: Path, revision: str) -> dict:
    git=shutil.which('git')
    if not git: raise RuntimeError('git executable is unavailable')
    probe=subprocess.run([git,'-C',str(repo),'rev-parse','--is-inside-work-tree'],text=True,capture_output=True)
    if probe.returncode!=0 or probe.stdout.strip()!='true': raise RuntimeError('target is not a readable Git work tree')
    cmd=[git,'-c','core.quotePath=false','-C',str(repo),'log',revision,f'--format={COMMIT_PREFIX}%H','--no-color','-p','--no-ext-diff','--no-textconv','--unified=0','--','.']
    p=subprocess.run(cmd,text=True,capture_output=True,errors='replace')
    if p.returncode!=0: raise RuntimeError(p.stderr.strip() or f'git log failed with exit {p.returncode}')
    commit=''; path=''; new_line=None
    commits=set(); files=set(); added_lines=0; findings=[]
    for raw in p.stdout.splitlines():
        if raw.startswith(COMMIT_PREFIX):
            commit=raw[len(COMMIT_PREFIX):].strip(); commits.add(commit); path=''; new_line=None; continue
        if raw.startswith('+++ '):
            value=raw[4:]
            if value=='/dev/null': path=''
            elif value.startswith('b/'): path=value[2:]
            else: path=value
            if path: files.add((commit,path))
            continue
        m=HUNK_RE.match(raw)
        if m:
            new_line=int(m.group(1)); continue
        if new_line is None or not path: continue
        if raw.startswith('+') and not raw.startswith('+++'):
            text=raw[1:]; added_lines+=1
            for f in scan_line(f'{commit}:{path}',new_line,text):
                findings.append({
                    'id':hid(commit,path,new_line,f.rule,f.id), 'commit':commit, 'path':path, 'line':new_line,
                    'severity':f.severity,'confidence':f.confidence,'rule':f.rule,'evidence':f.evidence
                })
            new_line+=1
        elif raw.startswith('-') and not raw.startswith('---'):
            continue
        elif raw.startswith('\\'):
            continue
        else:
            new_line+=1
    dedup={f['id']:f for f in findings}
    ordered=sorted(dedup.values(),key=lambda x:(SEVERITY_ORDER[x['severity']],x['commit'],x['path'],x['line'],x['rule'],x['id']))
    summary={s:sum(1 for f in ordered if f['severity']==s) for s in ('critical','high','medium','low')}
    return {'schema_version':1,'status':'complete','scope':'git-history','target':str(repo),'revision':revision,'summary':summary,
            'scan_stats':{'commits_scanned':len(commits),'files_with_added_lines':len(files),'added_lines_scanned':added_lines,'findings':len(ordered)},
            'findings':ordered}

def render_text(d):
    lines=[f"Target: {d['target']}",f"Revision: {d['revision']}",f"Status: {d['status']}","Findings:"]
    if not d['findings']: lines.append('- none in scanned added-line history coverage')
    else:
        for f in d['findings']: lines.append(f"- [{f['severity']}/{f['confidence']}] {f['commit']} {f['path']}:{f['line']} {f['rule']} ({f['id']}): {f['evidence']}")
    return '\n'.join(lines)+'\n'

def main():
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('repository'); ap.add_argument('--revision',default='--all'); ap.add_argument('--format',choices=['text','json'],default='text'); ap.add_argument('--output')
    a=ap.parse_args(); authored=Path(a.repository).expanduser()
    if authored.is_symlink(): ap.error(f'Refusing symbolic-link repository target: {authored}')
    if not authored.exists() or not authored.is_dir(): ap.error(f'Repository directory does not exist: {authored}')
    repo=authored.resolve()
    try: d=scan(repo,a.revision)
    except RuntimeError as e: ap.error(str(e))
    out=json.dumps(d,indent=2,sort_keys=True)+'\n' if a.format=='json' else render_text(d)
    if a.output:
        try: atomic_write(Path(a.output),out,input_root=repo)
        except (ValueError,OSError) as e: ap.error(str(e))
    else: sys.stdout.write(out); sys.stdout.flush()
    return 0
if __name__=='__main__': raise SystemExit(main())
