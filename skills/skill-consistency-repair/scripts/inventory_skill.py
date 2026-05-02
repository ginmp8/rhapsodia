#!/usr/bin/env python3
"""Inventory a ChatGPT/agent skill package for consistency repair."""
from __future__ import annotations

import argparse
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TEXT_SUFFIXES = {'.md', '.txt', '.json', '.yaml', '.yml', '.py', '.sh', '.js', '.ts', '.toml', '.ini', '.cfg'}
BLOCKED_PARTS = {'.git', '__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache'}


def is_text(path: Path) -> bool:
    return path.suffix.lower() in TEXT_SUFFIXES or path.name in {'SKILL.md', 'skill.md'}


def read_text(path: Path, max_chars: int = 500_000) -> str:
    try:
        data = path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        data = path.read_text(encoding='utf-8', errors='replace')
    return data[:max_chars]


def parse_frontmatter(text: str) -> dict[str, Any]:
    if not text.startswith('---'):
        return {'present': False, 'fields': {}, 'errors': ['missing yaml frontmatter']}
    end = text.find('\n---', 3)
    if end == -1:
        return {'present': False, 'fields': {}, 'errors': ['unterminated yaml frontmatter']}
    raw = text[3:end].strip('\n')
    fields: dict[str, str] = {}
    errors: list[str] = []
    for line in raw.splitlines():
        if not line.strip():
            continue
        if ':' not in line:
            errors.append(f'invalid frontmatter line: {line}')
            continue
        key, value = line.split(':', 1)
        fields[key.strip()] = value.strip().strip('"\'')
    extra = sorted(set(fields) - {'name', 'description'})
    missing = [k for k in ('name', 'description') if k not in fields]
    if extra:
        errors.append(f'extra frontmatter fields: {extra}')
    if missing:
        errors.append(f'missing frontmatter fields: {missing}')
    for key in ('name', 'description'):
        if key in fields and fields[key] != fields[key].lower():
            errors.append(f'{key} should be lowercase')
    return {'present': True, 'fields': fields, 'errors': errors, 'raw': raw}


def local_markdown_links(text: str) -> list[str]:
    links = []
    for match in re.finditer(r'\[[^\]]+\]\(([^)]+)\)', text):
        target = match.group(1).strip()
        if not target or '://' in target or target.startswith('#') or target.startswith('mailto:'):
            continue
        links.append(target.split('#', 1)[0])
    return links


def scan_target(target: Path) -> dict[str, Any]:
    target = target.resolve()
    files: list[dict[str, Any]] = []
    skill_files: list[str] = []
    links: list[dict[str, Any]] = []
    placeholder_hits: list[dict[str, Any]] = []
    marker_words = ['TO' + 'DO', 'FI' + 'XME', 'X' + 'XX']
    term_pattern = re.compile(r'\b(' + '|'.join(marker_words) + r')\b|\{\{[^}]+\}\}', re.I)
    scaffold_paths = {'scripts/' + 'example' + '.py', 'references/' + 'api' + '_reference.md', 'assets/' + 'example' + '_asset.txt'}

    for root, dirs, names in os.walk(target):
        dirs[:] = [d for d in dirs if d not in BLOCKED_PARTS]
        root_path = Path(root)
        for name in sorted(names):
            path = root_path / name
            rel = path.relative_to(target).as_posix()
            if any(part in BLOCKED_PARTS for part in path.parts):
                continue
            info = {
                'path': rel,
                'size_bytes': path.stat().st_size,
                'suffix': path.suffix.lower(),
                'is_text': is_text(path),
            }
            if name.lower() == 'skill.md':
                skill_files.append(rel)
            if is_text(path):
                text = read_text(path)
                info['line_count'] = text.count('\n') + 1
                found_links = local_markdown_links(text)
                for link in found_links:
                    links.append({'source': rel, 'target': link})
                if rel in scaffold_paths:
                    placeholder_hits.append({'path': rel, 'term': 'initializer scaffold file'})
                elif not (rel.startswith('scripts/') or rel.startswith('assets/templates/')):
                    for m in term_pattern.finditer(text):
                        placeholder_hits.append({'path': rel, 'term': m.group(0)})
            files.append(info)

    root_skill_path = target / 'SKILL.md'
    if root_skill_path.exists():
        skill_text = read_text(root_skill_path)
        frontmatter = parse_frontmatter(skill_text)
    else:
        skill_text = ''
        frontmatter = {'present': False, 'fields': {}, 'errors': ['root SKILL.md not found']}

    dirs_present = {p.name for p in target.iterdir() if p.is_dir()} if target.exists() else set()
    return {
        'target_path': target.as_posix(),
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'skill_file_count': len(skill_files),
        'skill_files': skill_files,
        'frontmatter': frontmatter,
        'directories': sorted(dirs_present),
        'files': files,
        'links': links,
        'placeholder_hits': placeholder_hits,
        'counts': {
            'files': len(files),
            'references': sum(1 for f in files if f['path'].startswith('references/')),
            'scripts': sum(1 for f in files if f['path'].startswith('scripts/')),
            'assets': sum(1 for f in files if f['path'].startswith('assets/')),
            'templates': sum(1 for f in files if f['path'].startswith('assets/templates/')),
            'examples': sum(1 for f in files if f['path'].startswith('examples/')),
            'evals': sum(1 for f in files if f['path'].startswith('evals/')),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Inventory a target skill package.')
    parser.add_argument('--target', required=True)
    parser.add_argument('--output', required=False)
    args = parser.parse_args()
    result = scan_target(Path(args.target))
    data = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(data + '\n', encoding='utf-8')
    else:
        print(data)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
