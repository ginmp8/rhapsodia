#!/usr/bin/env python3
"""Read-only, bounded byte and lexical overlap audit against a source ZIP.

A structural/similarity check, NOT a guarantee of conceptual originality.
Does not extract or execute reference archive content.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import tokenize
import zipfile
from pathlib import Path
from collections import defaultdict

MAX_ENTRIES=20_000
MAX_FILE=32*1024*1024
WINDOW=50


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def tokens(data: bytes) -> list[str]:
    try:
        iterator=tokenize.tokenize(io.BytesIO(data).readline)
        return [x.string for x in iterator if x.type not in
                (tokenize.ENCODING, tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE,
                 tokenize.INDENT, tokenize.DEDENT, tokenize.ENDMARKER)]
    except (SyntaxError,UnicodeError,tokenize.TokenError):
        return []


def windows(series: list[str], size: int=WINDOW):
    for pos in range(len(series)-size+1):
        yield pos, tuple(series[pos:pos+size])


def inspect(root: Path, reference: Path) -> dict:
    if not root.is_dir(): raise ValueError('skill must be directory')
    if not zipfile.is_zipfile(reference): raise ValueError('reference must be ZIP')
    files=sorted(p for p in root.rglob('*') if p.is_file())
    if any(p.is_symlink() for p in root.rglob('*')): raise ValueError('symlink in package')
    filenames=[p.relative_to(root).as_posix() for p in files]
    forbidden=[name for name in filenames if
               'upstream' in name.lower() or name.lower().endswith(('.tar.gz','.tgz','.nupkg','.jar','.node')) or
               name.lower().startswith(('third_party/','bridge/','vendor/','node_modules/'))]
    candidates={p.relative_to(root).as_posix():p.read_bytes() for p in files if p.stat().st_size<=MAX_FILE}
    originals: dict[str,str]={}
    reverse:dict[str,list[str]]=defaultdict(list)
    ref_py:dict[str,list[str]]={}
    skipped=0
    with zipfile.ZipFile(reference) as z:
        entries=z.infolist()
        if len(entries)>MAX_ENTRIES: raise ValueError('too many reference entries')
        for info in entries:
            if info.is_dir(): continue
            if info.file_size>MAX_FILE: skipped+=1;continue
            with z.open(info) as f:content=f.read(MAX_FILE+1)
            if len(content)>MAX_FILE: skipped+=1;continue
            key=sha(content)
            originals[info.filename]=key
            reverse[key].append(info.filename)
            if info.filename.endswith('.py'):
                ref_py[info.filename]=tokens(content)
    exact=[{'candidate':name,'reference_paths':reverse[sha(data)]} for name,data in candidates.items()
           if sha(data) in reverse]
    source_grams: dict[tuple[str,...],list[str]]=defaultdict(list)
    for name,vals in ref_py.items():
        for _,fragment in windows(vals):
            if len(source_grams[fragment])<2:
                source_grams[fragment].append(name)
    overlaps=[]
    for name,data in candidates.items():
        if not name.endswith('.py'):continue
        seq=tokens(data)
        for pos,fragment in windows(seq):
            if fragment in source_grams:
                overlaps.append({'candidate':name,'token_offset':pos,'reference':source_grams[fragment][:2]})
                if len(overlaps)>=30:break
    return {'reference':{'archive_sha256':sha(reference.read_bytes()),'checked_files':len(originals),'oversized_skipped':skipped},
            'candidate':{'files':len(filenames),'total_bytes':sum(p.stat().st_size for p in files)},
            'forbidden_bundled_paths':forbidden,'identical_file_hashes':exact,
            'python_50_token_fragment_matches':overlaps,
            'verdict':'PASS_SCOPED_ORIGINALITY_CHECK' if not (forbidden or exact or overlaps or skipped) else 'REVIEW_REQUIRED',
            'claim_scope':'No byte-identical files or 50-token Python overlaps found in checked ZIP content; does not prove absolute code originality, independent invention or licensing clearance.'}


def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('skill_root',type=Path)
    ap.add_argument('reference_zip',type=Path)
    ap.add_argument('-o','--output',type=Path)
    args=ap.parse_args()
    try:
        result=inspect(args.skill_root,args.reference_zip)
        text=json.dumps(result,indent=2,ensure_ascii=False)+'\n'
        if args.output:
            args.output.parent.mkdir(parents=True,exist_ok=True)
            args.output.write_text(text,encoding='utf-8')
        else:print(text,end='')
        return 0 if result['verdict']=='PASS_SCOPED_ORIGINALITY_CHECK' else 1
    except Exception as e:
        print(json.dumps({'error':str(e)}));return 2

if __name__=='__main__':
    raise SystemExit(main())
