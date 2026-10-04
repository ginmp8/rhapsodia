#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import json
import re
from pathlib import Path

from _common import atomic_write_json, is_secret_like, iter_files, markdown_local_links, parse_frontmatter

NAME_RE = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
MAX_BYTES = 25 * 1024 * 1024


def run_validation(root: Path) -> dict:
    root = root.resolve()
    diagnostics: list[dict] = []

    def add(code: str, severity: str, subject: str, evidence) -> None:
        diagnostics.append({'code': code, 'severity': severity, 'subject': subject, 'evidence': evidence})

    if not root.is_dir():
        add('package/root', 'error', str(root), 'not a directory')
        return {'status': 'fail', 'target': str(root), 'diagnostics': diagnostics}

    skill_md = root / 'SKILL.md'
    if not skill_md.is_file():
        add('package/root-skill-md', 'error', 'SKILL.md', 'missing')
        return {'status': 'fail', 'target': str(root), 'diagnostics': diagnostics}

    nested = [p.relative_to(root).as_posix() for p in root.rglob('SKILL.md') if p != skill_md]
    if nested:
        add('package/nested-skill', 'error', 'SKILL.md', nested)

    fm = parse_frontmatter(skill_md)
    name = fm.get('name', '')
    description = fm.get('description', '')
    if not name or not NAME_RE.fullmatch(name) or len(name) > 64:
        add('frontmatter/name', 'error', 'name', name)
    if not description or len(description) > 1024:
        add('frontmatter/description', 'error', 'description', {'length': len(description)})
    if name and root.name != name:
        add('frontmatter/name-directory', 'warning', root.name, {'name': name})

    total_bytes = 0
    json_errors: list[dict] = []
    python_errors: list[dict] = []
    broken_links: list[dict] = []
    escaping_links: list[dict] = []
    symlinks: list[str] = []
    secrets: list[str] = []
    archives: list[str] = []

    for path in iter_files(root):
        rel = path.relative_to(root).as_posix()
        if path.is_symlink():
            symlinks.append(rel)
            continue
        total_bytes += path.stat().st_size
        if is_secret_like(rel):
            secrets.append(rel)
        if path.suffix.lower() == '.json':
            try:
                json.loads(path.read_text(encoding='utf-8'))
            except Exception as exc:
                json_errors.append({'path': rel, 'error': str(exc)})
        if path.suffix.lower() == '.py':
            try:
                ast.parse(path.read_text(encoding='utf-8'), filename=rel)
            except SyntaxError as exc:
                python_errors.append({'path': rel, 'error': f'{exc.msg} line {exc.lineno}'})
        if path.suffix.lower() in {'.zip', '.tar', '.gz', '.tgz'}:
            archives.append(rel)

    for md in [p for p in iter_files(root) if not p.is_symlink() and p.suffix.lower() == '.md']:
        for target in markdown_local_links(md):
            candidate = (md.parent / target).resolve()
            try:
                candidate.relative_to(root)
            except ValueError:
                escaping_links.append({'source': md.relative_to(root).as_posix(), 'target': target})
                continue
            if not candidate.exists():
                broken_links.append({'source': md.relative_to(root).as_posix(), 'target': target})

    if symlinks:
        add('filesystem/symlinks', 'error', 'package', symlinks)
    if secrets:
        add('security/secret-like-files', 'error', 'package', secrets)
    if json_errors:
        add('syntax/json', 'error', 'json', json_errors)
    if python_errors:
        add('syntax/python', 'error', 'python', python_errors)
    if broken_links:
        add('references/broken-links', 'error', 'markdown', broken_links)
    if escaping_links:
        add('references/outside-root', 'warning', 'markdown', escaping_links)
    if archives:
        add('package/nested-archives', 'warning', 'package', archives)
    if total_bytes > MAX_BYTES:
        add('package/size', 'error', str(total_bytes), {'limit': MAX_BYTES})

    openai = root / 'agents' / 'openai.yaml'
    if openai.exists():
        text = openai.read_text(encoding='utf-8', errors='replace')
        for field in ['interface:', 'display_name:', 'short_description:']:
            if field not in text:
                add('metadata/openai-field', 'warning', 'agents/openai.yaml', field)

    errors = [d for d in diagnostics if d['severity'] == 'error']
    warnings = [d for d in diagnostics if d['severity'] == 'warning']
    return {
        'status': 'fail' if errors else ('warn' if warnings else 'pass'),
        'target': str(root),
        'diagnostics': diagnostics,
        'metrics': {'total_bytes': total_bytes}
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Run portable static validation on one target skill.')
    parser.add_argument('--target', required=True)
    parser.add_argument('--json-output')
    args = parser.parse_args()
    report = run_validation(Path(args.target))
    if args.json_output:
        atomic_write_json(Path(args.json_output), report)
    print(json.dumps(report, indent=2))
    return 1 if report['status'] == 'fail' else 0


if __name__ == '__main__':
    raise SystemExit(main())
