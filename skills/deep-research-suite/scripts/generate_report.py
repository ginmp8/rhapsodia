#!/usr/bin/env python3
"""Deterministic Markdown report builder with fail-closed inclusion and citations."""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, OrderedDict
from pathlib import Path
from typing import Any
from urllib.parse import quote
from validate_result import validate, is_empty, is_uncertain
from workspace_contract import load_fields, load_outline

CATEGORY_ALIASES = {
    'Basic Info': ['basic_info'],
    'Technical Features': ['technical_features', 'technical_characteristics'],
    'Performance Metrics': ['performance_metrics', 'performance'],
    'Milestone Significance': ['milestone_significance', 'milestones'],
    'Business Info': ['business_info', 'commercial_info'],
    'Competition & Ecosystem': ['competition_ecosystem', 'competition'],
    'History': ['history'],
    'Market Positioning': ['market_positioning', 'market'],
}


def escape(value: Any) -> str:
    """Escape untrusted text in Markdown (including inline HTML and link syntax)."""
    txt = str(value).replace('\\', '\\\\')
    for ch in '`*_{}[]()#+-.!|':
        txt = txt.replace(ch, '\\' + ch)
    txt = txt.replace('<', '&lt;').replace('>', '&gt;')
    return txt.replace('\r', '').replace('\n', '  \n')


def label(value: str) -> str:
    return str(value).replace('_', ' ').replace('-', ' ').title()


def anchor(value: str) -> str:
    return re.sub(r'[\s_]+', '-', re.sub(r'[^\w\s-]', '', str(value).lower())).strip('-') or 'item'


def safe_url(value: str) -> str:
    # URLs are validated by validate_result; this additionally prevents Markdown
    # link-breaking punctuation and control characters from entering link markup.
    return quote(value, safe=":/?#[]@!$&'*+,;=%~-._")


def category_keys(category: str) -> list[str]:
    generated = re.sub(r'[^a-zA-Z0-9]+', '_', category).strip('_').lower()
    return list(dict.fromkeys([category, generated, *CATEGORY_ALIASES.get(category, [])]))


def find_recursive(data: Any, name: str):
    if isinstance(data, dict):
        if name in data:
            return data[name]
        for k, v in data.items():
            if k.startswith('_') or k == 'uncertain':
                continue
            if isinstance(v, dict):
                result = find_recursive(v, name)
                if result is not None:
                    return result
    return None


def find_field(data: dict, category: str, field: str):
    if field in data:
        return data[field]
    for key in category_keys(category):
        if isinstance(data.get(key), dict) and field in data[key]:
            return data[key][field]
    return find_recursive(data, field)


def clean(value: Any, uncertain: set[str], field: str | None = None):
    if field in uncertain or is_uncertain(value):
        return None
    if isinstance(value, dict):
        d = OrderedDict()
        for k, v in value.items():
            if k.startswith('_') or k == 'uncertain' or k in uncertain:
                continue
            item = clean(v, uncertain, k)
            if not is_empty(item):
                d[k] = item
        return d
    if isinstance(value, list):
        return [v for x in value if not is_empty(v := clean(x, uncertain))]
    return value


def render_value(value: Any, level: int = 0) -> str:
    if isinstance(value, dict):
        lines = []
        for k, v in value.items():
            if isinstance(v, (dict, list)):
                lines += [f'- **{escape(label(k))}:**',
                          *['  ' + item for item in render_value(v, level + 1).splitlines()]]
            else:
                lines.append(f'- **{escape(label(k))}:** {escape(v)}')
        return '\n'.join(lines)
    if isinstance(value, list):
        if all(not isinstance(x, (dict, list)) for x in value):
            if len(value) <= 5 and sum(map(lambda v: len(str(v)), value)) <= 180:
                return ', '.join(escape(v) for v in value)
            return '\n'.join('- ' + escape(v) for v in value)
        return '\n'.join('- ' + render_value(v, level + 1).replace('\n', '\n  ') for v in value)
    return escape(value)


def other_fields(data: dict, defined: set[str], wrappers: set[str], uncertain: set[str]) -> dict[str, Any]:
    extra: dict[str, Any] = OrderedDict()
    def walk(obj):
        if not isinstance(obj, dict):
            return
        for k, v in obj.items():
            if k == 'uncertain' or k.startswith('_') or k in uncertain or k in defined:
                continue
            if k in wrappers and isinstance(v, dict):
                walk(v)
            else:
                cv = clean(v, uncertain, k)
                if not is_empty(cv) and k not in extra:
                    extra[k] = cv
    walk(data)
    return extra


def infer_summary(records: list[dict], schema: dict) -> list[str]:
    counts: Counter[str] = Counter()
    for data in records:
        uncertain = set(data.get('uncertain', []))
        for category in schema['categories']:
            for field in category['fields']:
                name = field['name']
                if name == 'name' or name in uncertain:
                    continue
                value = clean(find_field(data, category['name'], name), uncertain, name)
                if not is_empty(value) and not isinstance(value, (dict, list)) and len(str(value)) <= 80:
                    counts[name] += 1
    return [name for name, _ in counts.most_common(3)]


def generate(outline: Path, fields: Path, directory: Path, dest: Path,
             allow_partial: bool = False, title: str = '', summary_fields: list[str] | None = None,
             allow_external_output: bool = False) -> dict:
    spec = load_outline(outline)
    schema = load_fields(fields)
    expected = [str(item['name']).strip() for item in spec['items']]
    data_by_name: dict[str, dict] = {}
    invalid: list[dict] = []
    unexpected: list[str] = []
    duplicate_names: set[str] = set()
    for path in sorted(directory.glob('*.json')) if directory.exists() else []:
        try:
            result = validate(fields, path)
            if not result['valid']:
                invalid.append({'file': path.name, 'reason': result['status'],
                                'missing_required': result['missing_required'],
                                'uncertain_required': result['uncertain_required'],
                                'errors': result['errors']})
                continue  # Never silently include invalid/incomplete data even under --allow-partial.
            raw = json.loads(path.read_text(encoding='utf-8'))
            name = raw['name']
            if name not in expected:
                unexpected.append(path.name)
                continue
            if name in data_by_name or name in duplicate_names:
                invalid.append({'file': path.name, 'reason': 'duplicate item name'})
                duplicate_names.add(name)
                data_by_name.pop(name, None)
                continue
            data_by_name[name] = raw
        except (ValueError, OSError, KeyError, json.JSONDecodeError) as exc:
            invalid.append({'file': path.name, 'reason': str(exc)})
    missing = [name for name in expected if name not in data_by_name]
    if (missing or invalid) and not allow_partial:
        return {'generated': False, 'missing_items': missing, 'invalid_results': invalid,
                'unexpected_results': unexpected}
    records = [data_by_name[name] for name in expected if name in data_by_name]
    if not records:
        return {'generated': False, 'error': 'no research-ready results found',
                'missing_items': missing, 'invalid_results': invalid}
    summaries = summary_fields or infer_summary(records, schema)
    anchors: list[str] = []
    used_anchors: set[str] = set()
    for record in records:
        base = anchor(record['name'])
        value = base
        counter = 2
        while value in used_anchors:
            value = f'{base}-{counter}'
            counter += 1
        anchors.append(value)
        used_anchors.add(value)
    lines = ['# ' + escape(title or spec['topic'] or 'Research Report'), '']
    if missing or invalid:
        lines += ['> **PARTIAL REPORT:** Items missing or excluded for invalid/incomplete evidence:',
                  '> ' + escape(', '.join(missing) or '(none)') + '.',
                  '> ' + escape(', '.join(x['file'] for x in invalid) or '(none)') + '.', '']
    lines += ['## Table of contents', '']
    for index, (record, link_anchor) in enumerate(zip(records, anchors), 1):
        uncertain = set(record.get('uncertain', []))
        summary = []
        for field in summaries:
            value = clean(find_recursive(record, field), uncertain, field)
            if not is_empty(value) and not isinstance(value, (dict, list)):
                summary.append(f'{escape(label(field))}: {escape(value)}')
        suffix = ' - ' + ' | '.join(summary) if summary else ''
        lines.append(f'{index}. [{escape(record["name"])}](#{link_anchor}){suffix}')
    lines += ['', '---', '']
    wrappers = {key for category in schema['categories'] for key in category_keys(category['name'])}
    for idx, record in enumerate(records):
        # Explicit HTML anchor, always from a sanitized unique value.
        lines += [f'<a id="{anchors[idx]}"></a>', f'## {escape(record["name"])}', '']
        uncertain = set(record.get('uncertain', []))
        for category in schema['categories']:
            sections = []
            for field in category['fields']:
                key = field['name']
                if key == 'name':
                    continue
                value = clean(find_field(record, category['name'], key), uncertain, key)
                if not is_empty(value):
                    sections += [f'#### {escape(label(key))}', '', render_value(value), '']
            if sections:
                lines += ['### ' + escape(category['name']), '', *sections]
        extras = other_fields(record, schema['names'], wrappers, uncertain)
        if extras:
            lines += ['### Other Info', '']
            for key, value in extras.items():
                lines += ['#### ' + escape(label(key)), '', render_value(value), '']
        sources = {src.get('id', f'legacy:{i}'): src
                   for i, src in enumerate(record.get('_sources', []))}
        claims = record.get('_claims', [])
        if claims:
            lines += ['### Claim evidence', '',
                      '_A source link documents provenance; it does not independently prove factual correctness._', '']
            for claim in claims:
                refs = []
                for sid in claim.get('source_ids', []):
                    source = sources.get(sid)
                    if source:
                        refs.append(f'[{escape(sid)}]({safe_url(source["url"])})')
                citations = ' ' + ' '.join(refs) if refs else ''
                locator = f' ({escape(claim["locator"])})' if claim.get('locator') else ''
                lines.append(f'- **{escape(claim["status"])}** — {escape(claim["text"])}{locator}{citations}')
            lines.append('')
        if sources:
            lines += ['### Sources', '']
            for sid, src in sources.items():
                name = src.get('title') or src.get('url') or 'Source'
                date = f' — accessed {escape(src["accessed"])}' if src.get('accessed') else ''
                lines.append(f'- {escape(sid)}: [{escape(name)}]({safe_url(src["url"])}){date}')
            lines.append('')
    # Protect the source evidence and workspace metadata from accidental alias writes.
    destination = dest.resolve()
    if not allow_external_output and not destination.is_relative_to(outline.resolve().parent):
        raise ValueError('report output outside the workspace requires --allow-external-output')
    protected = {outline.resolve(), fields.resolve()}
    protected.update(path.resolve() for path in directory.glob('*.json') if directory.exists())
    if destination in protected:
        raise ValueError('report output cannot overwrite source/evaluator input')
    dest.parent.mkdir(parents=True, exist_ok=True)
    # Atomic replace: a failed generation cannot corrupt an existing report.
    import os
    import tempfile
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', dir=dest.parent,
                                     prefix='.research-report-', delete=False) as handle:
        temp = Path(handle.name)
        try:
            handle.write('\n'.join(lines).rstrip() + '\n')
            handle.flush()
            os.fsync(handle.fileno())
        except BaseException:
            temp.unlink(missing_ok=True)
            raise
    os.replace(temp, dest)
    return {'generated': True, 'output': str(dest), 'included_items': len(records),
            'missing_items': missing, 'invalid_results': invalid,
            'unexpected_results': unexpected, 'summary_fields': summaries,
            'partial': bool(missing or invalid)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--outline', required=True)
    parser.add_argument('--fields', required=True)
    parser.add_argument('--results-dir', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--title', default='')
    parser.add_argument('--summary-fields', default='')
    parser.add_argument('--allow-partial', action='store_true')
    parser.add_argument('--allow-external-output', action='store_true')
    args = parser.parse_args()
    try:
        result = generate(Path(args.outline), Path(args.fields), Path(args.results_dir),
                          Path(args.output), args.allow_partial, args.title,
                          [x.strip() for x in args.summary_fields.split(',') if x.strip()],
                          args.allow_external_output)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result['generated'] else 2
    except Exception as exc:
        print(json.dumps({'generated': False, 'error': str(exc)}, ensure_ascii=False, indent=2))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
