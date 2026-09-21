#!/usr/bin/env python3
from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
import ast
import json
import os
import re
from pathlib import Path

from _common import dump_json, is_secret_like, iter_files, markdown_local_links, parse_frontmatter

MAX_BYTES = 25 * 1024 * 1024
MAX_NAME = 64
MAX_DESCRIPTION = 1024
NAME_RE = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')


def main() -> int:
    ap = argparse.ArgumentParser(description='Validate one skill package with a portable Agent Skills core and optional host profile.')
    ap.add_argument('--target', required=True)
    ap.add_argument('--json', dest='json_out')
    ap.add_argument('--profile', choices=('portable', 'openai'), default='portable')
    ap.add_argument('--strict-openai-metadata', action='store_true', help='Backward-compatible alias for --profile openai.')
    args = ap.parse_args()

    profile = 'openai' if args.strict_openai_metadata else args.profile
    root = Path(args.target).resolve()
    checks = []
    errors = []
    warnings = []

    def check(code: str, ok: bool, subject: str, evidence=None, severity='error'):
        row = {'code': code, 'status': 'pass' if ok else 'fail', 'subject': subject, 'evidence': evidence or {}}
        checks.append(row)
        if not ok:
            (errors if severity == 'error' else warnings).append({'code': code, 'subject': subject, 'evidence': evidence or {}})

    check('package/root-directory', root.is_dir(), str(root))
    skill_md = root / 'SKILL.md'
    check('package/root-skill-md', skill_md.is_file(), 'SKILL.md')
    if not root.is_dir() or not skill_md.is_file():
        report = {'status': 'fail', 'profile': profile, 'checks': checks, 'errors': errors, 'warnings': warnings}
        dump_json(report, args.json_out)
        return 1

    nested = [p.relative_to(root).as_posix() for p in root.rglob('SKILL.md') if p != skill_md]
    check('package/single-skill-root', not nested, 'SKILL.md', {'nested': nested})

    fm = parse_frontmatter(skill_md)
    name = fm.get('name', '')
    desc = fm.get('description', '')
    valid_name = bool(name) and len(name) <= MAX_NAME and bool(NAME_RE.match(name))
    check('frontmatter/name', valid_name, name or '<missing>', {'length': len(name), 'max': MAX_NAME})
    valid_desc = bool(desc) and len(desc) <= MAX_DESCRIPTION and ('to' + 'do') not in desc.lower()
    check('frontmatter/description', valid_desc, 'description', {'length': len(desc), 'max': MAX_DESCRIPTION})
    check('frontmatter/name-matches-directory', root.name == name, root.name, {'name': name}, severity='warning')

    skill_text = skill_md.read_text(encoding='utf-8', errors='replace')
    marker_pattern = r'\b(?:TO' + r'DO|T' + r'BD|FI' + r'XME|PLACE' + r'HOLDER)\b'
    placeholders = sorted(set(re.findall(marker_pattern, skill_text, flags=re.I)))
    check('content/no-scaffold-markers', not placeholders, 'SKILL.md', {'markers': placeholders})

    openai_meta = root / 'agents' / 'openai.yaml'
    openai_required = profile == 'openai'
    check(
        'metadata/openai-yaml',
        openai_meta.is_file() or not openai_required,
        'agents/openai.yaml',
        {'profile': profile, 'required': openai_required, 'present': openai_meta.is_file()},
    )

    broken = []
    out_of_root_links = []
    md_files = [p for p in iter_files(root) if not p.is_symlink() and p.suffix.lower() == '.md']
    for md in md_files:
        for target in markdown_local_links(md):
            candidate = (md.parent / target).resolve()
            try:
                candidate.relative_to(root)
            except ValueError:
                out_of_root_links.append({'source': md.relative_to(root).as_posix(), 'target': target})
                continue
            if not candidate.exists():
                broken.append({'source': md.relative_to(root).as_posix(), 'target': target})
    check('references/local-links-resolve', not broken, 'markdown links', {'broken': broken})
    check('references/no-package-escape-links', not out_of_root_links, 'markdown links', {'outside': out_of_root_links}, severity='warning')

    total_bytes = 0
    secret_like = []
    symlink_escapes = []
    json_errors = []
    py_errors = []
    archive_noise = []
    for p in iter_files(root):
        rel = p.relative_to(root).as_posix()
        if p.is_symlink():
            resolved = p.resolve()
            try:
                resolved.relative_to(root)
            except ValueError:
                symlink_escapes.append({'path': rel, 'target': os.readlink(p)})
            continue
        total_bytes += p.stat().st_size
        if is_secret_like(rel):
            secret_like.append(rel)
        if p.suffix.lower() == '.json':
            try:
                json.loads(p.read_text(encoding='utf-8'))
            except Exception as exc:
                json_errors.append({'path': rel, 'error': str(exc)})
        if p.suffix.lower() == '.py':
            try:
                ast.parse(p.read_text(encoding='utf-8'), filename=rel)
            except SyntaxError as exc:
                py_errors.append({'path': rel, 'error': f'{exc.msg} line {exc.lineno}'})
        if p.suffix.lower() in {'.zip', '.tar', '.gz', '.tgz'}:
            archive_noise.append(rel)

    check('security/no-secret-like-files', not secret_like, 'package files', {'files': secret_like})
    check('filesystem/no-escaping-symlinks', not symlink_escapes, 'symlinks', {'escapes': symlink_escapes})
    check('syntax/json-parse', not json_errors, 'json files', {'errors': json_errors})
    check('syntax/python-parse', not py_errors, 'python files', {'errors': py_errors})
    check('package/no-nested-archives', not archive_noise, 'archive files', {'files': archive_noise}, severity='warning')
    check('package/size-limit', total_bytes <= MAX_BYTES, str(total_bytes), {'bytes': total_bytes, 'limit': MAX_BYTES})

    status = 'fail' if errors else ('warn' if warnings else 'pass')
    report = {
        'status': status,
        'profile': profile,
        'target': str(root),
        'checks': checks,
        'errors': errors,
        'warnings': warnings,
        'metrics': {'total_bytes': total_bytes, 'markdown_files': len(md_files)},
    }
    dump_json(report, args.json_out)
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
