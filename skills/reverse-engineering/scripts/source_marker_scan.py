#!/usr/bin/env python3
"""Read-only, bounded and redacted source credential-marker discovery.

Pattern candidates are not validated credentials. An empty result does not prove
absence of secrets. Never sends data to third parties or prints candidate values.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys

from behavior_lab import DataError
from json_writer import write_exclusive

PATTERNS={
    'aws-access-key-id': re.compile(r'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b'),
    'github-token': re.compile(r'\bgh[pousr]_[A-Za-z0-9_]{28,255}\b'),
    'github-fine-grained-token': re.compile(r'\bgithub_pat_[A-Za-z0-9_]{22,255}\b'),
    'gitlab-token': re.compile(r'\bglpat-[A-Za-z0-9_-]{18,255}\b'),
    'slack-bot-token': re.compile(r'\bxox[baprs]-[A-Za-z0-9-]{20,255}\b'),
    'generic-credential-assignment': re.compile(
        r'''(?i)\b(?:client_secret|api[_-]?key|access[_-]?token|secret_key)\b\s*[:=]\s*["']([A-Za-z0-9/+=._-]{24,255})["']''')
}
EXCLUDE={'node_modules','.git','.venv','venv','dist','build','obj','bin','__pycache__'}
SUFFIXES={'.py','.js','.jsx','.ts','.tsx','.json','.yaml','.yml','.xml','.html','.env','.properties','.toml','.ini','.config','.cs','.csproj','.txt','.md','.sh','.ps1'}
MAX_FILE=2*1024*1024
MAX_TOTAL=64*1024*1024
MAX_FILES=3000
MAX_FINDINGS=500


def candidate_real(value:str)->bool:
    low=value.lower()
    if any(x in low for x in ('your_', 'placeholder', 'example', 'dummy', 'replace_me', 'changeme', 'xxxx','fake_key', 'sample_')):
        return False
    return len(set(value))>=8 and len(value)>=20


def scan(root:Path)->dict:
    if root.is_symlink() or not root.is_dir():
        raise DataError('source-root must be an existing nonsymlink directory')
    root=root.resolve()
    results=[]
    files=0;total=0;skipped=0;truncated=False
    for current, directories, names in os.walk(root, followlinks=False):
        directories[:] = sorted(d for d in directories
                                if d not in EXCLUDE and not (Path(current)/d).is_symlink())
        for name in sorted(names):
            path = Path(current) / name
            if path.is_symlink():
                skipped += 1
                continue
            if not path.is_file() or path.suffix.lower() not in SUFFIXES:
                continue
            if files >= MAX_FILES or total >= MAX_TOTAL or len(results) >= MAX_FINDINGS:
                truncated = True
                break
            size = path.stat().st_size
            if size > MAX_FILE or total + size > MAX_TOTAL:
                skipped += 1
                continue
            files += 1; total += size
            try:
                raw = path.read_bytes()
                if b'\0' in raw[:1000]:
                    skipped += 1
                    continue
                content = raw.decode('utf-8')
            except (UnicodeDecodeError, OSError):
                skipped += 1
                continue
            for lineno, line in enumerate(content.splitlines(), start=1):
                if len(line) > 4096:
                    skipped += 1
                    continue
                for kind, pattern in PATTERNS.items():
                    for hit in pattern.finditer(line):
                        value = hit.group(1) if kind == 'generic-credential-assignment' else hit.group(0)
                        if not candidate_real(value):
                            continue
                        results.append({'path': path.relative_to(root).as_posix(), 'line': lineno,
                                        'kind': kind, 'marker': '[REDACTED]',
                                        'confidence': 'candidate-needs-review'})
                        if len(results) >= MAX_FINDINGS:
                            truncated = True
                            break
                    if truncated: break
                if truncated: break
            if truncated: break
        if truncated: break
    return {'schema_version':'1.0','mode':'source-secret-markers','root_identity_sha256':hashlib.sha256(str(root).encode()).hexdigest(),
            'files_scanned':files,'bytes_scanned':total,'files_skipped':skipped,
            'findings':results,'truncated':truncated,'scope':'read-only source strings (selected extensions, bounded)',
            'privacy':'Never stores secret values, performs validity checks, or sends data to a remote endpoint',
            'limitations':'Pattern candidates can be false positives; missing patterns, skipped files, and code-generated secrets remain unknown'}


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-root',required=True,type=Path)
    p.add_argument('-o','--output',required=True,type=Path)
    a=p.parse_args(argv)
    try:
        if a.output.resolve().is_relative_to(a.source_root.resolve()):
            raise DataError('output must be outside source-root to maintain read-only scan')
        result=scan(a.source_root)
        write_exclusive(a.output,json.dumps(result,sort_keys=True,indent=2)+'\n',[a.source_root])
        return 0
    except (OSError,ValueError) as exc:
        print(json.dumps({'error':str(exc)}),file=sys.stderr)
        return 2

if __name__=='__main__':
    raise SystemExit(main())
