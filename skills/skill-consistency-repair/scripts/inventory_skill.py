#!/usr/bin/env python3
"""Build a deterministic, evidence-oriented inventory of an Agent Skills package."""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

INVENTORY_VERSION = 2
TEXT_SUFFIXES = {'.md', '.txt', '.json', '.yaml', '.yml', '.py', '.sh', '.js', '.ts', '.toml', '.ini', '.cfg'}
BLOCKED_PARTS = {'.git', '__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache'}
NOISE_SUFFIXES = {'.pyc', '.pyo'}


def is_text(path: Path) -> bool:
    return path.suffix.lower() in TEXT_SUFFIXES or path.name.lower() == 'skill.md'


def read_text(path: Path, max_chars: int = 500_000) -> str:
    try:
        data = path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        data = path.read_text(encoding='utf-8', errors='replace')
    return data[:max_chars]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    return hashlib.sha256(payload).hexdigest()


def parse_frontmatter(text: str) -> dict[str, Any]:
    if not text.startswith('---'):
        return {'present': False, 'fields': {}, 'extensions': [], 'errors': ['missing yaml frontmatter']}
    match = re.match(r'^---\s*\n(.*?)\n---\s*(?:\n|$)', text, re.S)
    if not match:
        return {'present': False, 'fields': {}, 'extensions': [], 'errors': ['unterminated yaml frontmatter']}
    raw = match.group(1)
    fields: dict[str, str] = {}
    errors: list[str] = []
    for line in raw.splitlines():
        if not line.strip() or line[:1].isspace() or ':' not in line:
            continue
        key, value = line.split(':', 1)
        key = key.strip()
        if not re.fullmatch(r'[A-Za-z0-9_-]+', key):
            continue
        fields[key] = value.strip().strip('"\'')
    missing = [k for k in ('name', 'description') if not fields.get(k)]
    if missing:
        errors.append(f'missing frontmatter fields: {missing}')
    name = fields.get('name', '')
    if name and not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name):
        errors.append('name must be lowercase kebab-case')
    extensions = sorted(set(fields) - {'name', 'description'})
    return {'present': True, 'fields': fields, 'extensions': extensions, 'errors': errors, 'raw': raw}


def local_markdown_links(text: str) -> list[str]:
    links: list[str] = []
    for match in re.finditer(r'\[[^\]]+\]\(([^)]+)\)', text):
        target = match.group(1).strip().strip('<>')
        if not target or '://' in target or target.startswith('#') or target.startswith('mailto:'):
            continue
        links.append(target.split('#', 1)[0])
    return links


def file_role(rel: str) -> str:
    p = Path(rel)
    if rel == 'SKILL.md':
        return 'control'
    if rel.startswith('agents/'):
        return 'metadata'
    if rel.startswith('references/'):
        return 'reference'
    if rel.startswith('assets/templates/'):
        return 'template'
    if rel.startswith('assets/'):
        return 'asset'
    if rel.startswith('evals/'):
        return 'evaluator'
    if rel.startswith('examples/'):
        return 'example'
    if rel.startswith(('tests/', 'test/')) or p.name.startswith('test_'):
        return 'test'
    if rel.startswith('scripts/'):
        return 'script'
    return 'other'


def source_dimensions(rel: str, text: str) -> list[str]:
    role = file_role(rel)
    name = Path(rel).name.lower()
    low = text.lower()
    dims: set[str] = {'references'}
    if role in {'script', 'test', 'evaluator'}:
        dims.add('consumers')
    if role == 'test':
        dims.add('tests')
    if role == 'example':
        dims.add('examples')
    if role == 'evaluator' or any(term in name for term in ('validate', 'validator', 'audit', 'check', 'lint')):
        dims.add('validators')
    if any(term in name for term in ('package', 'archive', 'zip')) or 'zipfile' in low:
        dims.add('packaging')
    if any(term in low for term in ('migration', 'migrate', 'legacy', 'backward compat', 'backward-compat')):
        dims.add('migration_paths')
    if 'handoff' in low or 'hand off' in low:
        dims.add('handoffs')
    return sorted(dims)


def python_import_edges(target: Path, files: list[dict[str, Any]]) -> list[dict[str, str]]:
    module_map: dict[str, list[str]] = {}
    for item in files:
        rel = item['path']
        if rel.endswith('.py'):
            module_map.setdefault(Path(rel).stem, []).append(rel)
    edges: set[tuple[str, str, str]] = set()
    for item in files:
        rel = item['path']
        if not rel.endswith('.py'):
            continue
        try:
            tree = ast.parse(read_text(target / rel))
        except (SyntaxError, OSError):
            continue
        imported: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split('.')[-1] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split('.')[-1])
        for name in sorted(imported):
            candidates = module_map.get(name, [])
            if len(candidates) == 1 and candidates[0] != rel:
                edges.add((rel, candidates[0], 'python_import'))
    return [{'source': a, 'target': b, 'type': c} for a, b, c in sorted(edges)]


def build_reference_graph(target: Path, files: list[dict[str, Any]], texts: dict[str, str], links: list[dict[str, str]]) -> tuple[list[dict[str, str]], dict[str, dict[str, list[str]]]]:
    edges: set[tuple[str, str, str]] = set()
    existing = {item['path'] for item in files}
    for link in links:
        source = link['source']
        raw = link['target']
        source_dir = Path(source).parent
        resolved = (source_dir / raw).as_posix() if source_dir.as_posix() != '.' else Path(raw).as_posix()
        if resolved in existing:
            edges.add((source, resolved, 'markdown_link'))
        elif raw in existing:
            edges.add((source, raw, 'markdown_link'))

    searchable = [item['path'] for item in files if item['path'] != 'SKILL.md']
    for source, text in texts.items():
        low = text.lower()
        for target_rel in searchable:
            if source == target_rel:
                continue
            target_path = Path(target_rel)
            tokens = [target_rel.lower(), target_path.name.lower()]
            stem = target_path.stem.lower()
            if len(stem) >= 6:
                tokens.append(stem)
            if any(token and token in low for token in tokens):
                edges.add((source, target_rel, 'text_reference'))

    for edge in python_import_edges(target, files):
        edges.add((edge['source'], edge['target'], edge['type']))

    sorted_edges = [{'source': a, 'target': b, 'type': c} for a, b, c in sorted(edges)]
    trace: dict[str, dict[str, list[str]]] = {}
    dimensions = ['imports', 'links', 'references', 'consumers', 'tests', 'validators', 'examples', 'packaging', 'migration_paths', 'handoffs']
    for item in files:
        trace[item['path']] = {key: [] for key in dimensions}
    for edge in sorted_edges:
        source, target_rel, edge_type = edge['source'], edge['target'], edge['type']
        if target_rel not in trace:
            continue
        if edge_type == 'python_import':
            trace[target_rel]['imports'].append(source)
        if edge_type == 'markdown_link':
            trace[target_rel]['links'].append(source)
        trace[target_rel]['references'].append(source)
        source_text = texts.get(source, '')
        for dim in source_dimensions(source, source_text):
            if dim in trace[target_rel]:
                trace[target_rel][dim].append(source)
    for target_rel, dims in trace.items():
        for key, values in dims.items():
            dims[key] = sorted(set(values))
    return sorted_edges, trace


def scan_target(target: Path) -> dict[str, Any]:
    target = target.resolve()
    if not target.is_dir():
        raise FileNotFoundError(f'target directory not found: {target}')

    files: list[dict[str, Any]] = []
    skill_files: list[str] = []
    links: list[dict[str, str]] = []
    scaffold_hits: list[dict[str, str]] = []
    texts: dict[str, str] = {}
    marker_words = ['TO' + 'DO', 'FI' + 'XME', 'X' + 'XX']
    term_pattern = re.compile(r'\b(' + '|'.join(marker_words) + r')\b', re.I)
    scaffold_paths = {'scripts/' + 'example' + '.py', 'references/' + 'api' + '_reference.md', 'assets/' + 'example' + '_asset.txt'}

    for root, dirs, names in os.walk(target):
        dirs[:] = sorted(d for d in dirs if d not in BLOCKED_PARTS)
        root_path = Path(root)
        for name in sorted(names):
            path = root_path / name
            rel = path.relative_to(target).as_posix()
            if any(part in BLOCKED_PARTS for part in path.relative_to(target).parts) or path.suffix.lower() in NOISE_SUFFIXES:
                continue
            info: dict[str, Any] = {
                'path': rel,
                'role': file_role(rel),
                'size_bytes': path.stat().st_size,
                'sha256': sha256_file(path),
                'suffix': path.suffix.lower(),
                'is_text': is_text(path),
            }
            if name.lower() == 'skill.md':
                skill_files.append(rel)
            if is_text(path):
                text = read_text(path)
                texts[rel] = text
                info['line_count'] = text.count('\n') + 1
                for link in local_markdown_links(text):
                    links.append({'source': rel, 'target': link})
                if rel in scaffold_paths:
                    scaffold_hits.append({'path': rel, 'term': 'initializer scaffold file'})
                elif not rel.startswith('assets/templates/'):
                    for match in term_pattern.finditer(text):
                        scaffold_hits.append({'path': rel, 'term': match.group(0)})
            files.append(info)

    root_skill_path = target / 'SKILL.md'
    if root_skill_path.exists():
        skill_text = texts.get('SKILL.md', read_text(root_skill_path))
        frontmatter = parse_frontmatter(skill_text)
    else:
        frontmatter = {'present': False, 'fields': {}, 'extensions': [], 'errors': ['root SKILL.md not found']}

    edges, trace = build_reference_graph(target, files, texts, links)
    stable_core = {
        'inventory_version': INVENTORY_VERSION,
        'frontmatter': {
            'fields': frontmatter.get('fields', {}),
            'extensions': frontmatter.get('extensions', []),
            'errors': frontmatter.get('errors', []),
        },
        'files': [{k: item[k] for k in ('path', 'role', 'size_bytes', 'sha256', 'suffix', 'is_text') if k in item} for item in files],
        'reference_graph': edges,
        'scaffold_hits': sorted(scaffold_hits, key=lambda x: (x['path'], x['term'])),
    }
    dirs_present = {p.name for p in target.iterdir() if p.is_dir()}
    result = {
        'inventory_version': INVENTORY_VERSION,
        'target_path': target.as_posix(),
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'inventory_fingerprint': canonical_hash(stable_core),
        'skill_file_count': len(skill_files),
        'skill_files': sorted(skill_files),
        'frontmatter': frontmatter,
        'directories': sorted(dirs_present),
        'files': files,
        'links': sorted(links, key=lambda x: (x['source'], x['target'])),
        'reference_graph': edges,
        'resource_trace': trace,
        'scaffold_hits': sorted(scaffold_hits, key=lambda x: (x['path'], x['term'])),
        'counts': {
            'files': len(files),
            'references': sum(1 for f in files if f['role'] == 'reference'),
            'scripts': sum(1 for f in files if f['role'] == 'script'),
            'assets': sum(1 for f in files if f['role'] in {'asset', 'template'}),
            'templates': sum(1 for f in files if f['role'] == 'template'),
            'examples': sum(1 for f in files if f['role'] == 'example'),
            'evals': sum(1 for f in files if f['role'] == 'evaluator'),
            'tests': sum(1 for f in files if f['role'] == 'test'),
        },
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description='Inventory a target skill package with deterministic hashes and reference tracing.')
    parser.add_argument('--target', required=True)
    parser.add_argument('--output')
    args = parser.parse_args()
    try:
        result = scan_target(Path(args.target))
    except Exception as exc:
        print(json.dumps({'status': 'fail', 'error': str(exc)}, indent=2))
        return 1
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
