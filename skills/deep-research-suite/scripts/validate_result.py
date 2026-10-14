#!/usr/bin/env python3
"""Validate field coverage, usable evidence and claim-to-source integrity.

Static validity cannot prove that the source actually supports a claim. It
only proves that referenced evidence exists in the result contract.
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit
from workspace_contract import load_fields

STATES = {'supported', 'contradicted', 'uncertain', 'not_found'}


def is_uncertain(value) -> bool:
    return isinstance(value, str) and '[uncertain]' in value.lower()


def is_empty(value) -> bool:
    return value is None or value == '' or value == [] or value == {}


def find_value(obj, field: str):
    if isinstance(obj, dict):
        if field in obj:
            return True, obj[field]
        for key, value in obj.items():
            if key == 'uncertain' or key.startswith('_'):
                continue
            if isinstance(value, dict):
                found, result = find_value(value, field)
                if found:
                    return True, result
    return False, None


def collect_keys(obj, defined: set[str]) -> set[str]:
    keys = set()
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == 'uncertain' or key.startswith('_'):
                continue
            if key in defined or not isinstance(value, (dict, list)):
                keys.add(key)
            if isinstance(value, (dict, list)):
                keys.update(collect_keys(value, defined))
    elif isinstance(obj, list):
        for value in obj:
            if isinstance(value, (dict, list)):
                keys.update(collect_keys(value, defined))
    return keys


def _valid_url(raw: str) -> bool:
    try:
        p = urlsplit(raw)
        return p.scheme.lower() in ('https', 'http') and bool(p.hostname) and not p.username and not p.password and not any(ord(ch) < 32 for ch in raw)
    except ValueError:
        return False


def validate(fields_path: Path, result_path: Path) -> dict:
    schema = load_fields(fields_path)
    data = json.loads(result_path.read_text(encoding='utf-8'))
    if not isinstance(data, dict):
        raise ValueError('result JSON root must be an object')
    errors: list[str] = []
    warnings: list[str] = []
    uncertain = data.get('uncertain', [])
    if not isinstance(uncertain, list) or any(not isinstance(x, str) for x in uncertain):
        errors.append('uncertain must be an array of field-name strings')
        uncertain = []
    uncertain_fields = set(uncertain)
    unknown_uncertain = uncertain_fields - schema['names']
    if unknown_uncertain:
        warnings.append(f'uncertain lists fields not in schema: {sorted(unknown_uncertain)}')
    keys = collect_keys(data, schema['names'])
    missing_required: list[str] = []
    missing_optional: list[str] = []
    empty_required: list[str] = []
    uncertain_required: list[str] = []
    for field in schema['fields']:
        name = str(field['name'])
        found, value = find_value(data, name)
        required = name in schema['required']
        if not found:
            (missing_required if required else missing_optional).append(name)
        elif required and is_empty(value):
            empty_required.append(name)
        elif required and (name in uncertain_fields or is_uncertain(value)):
            uncertain_required.append(name)
        elif is_uncertain(value) and name not in uncertain_fields:
            warnings.append(f'{name}: [uncertain] marker is not listed in uncertain')
    if 'name' in schema['names'] and not str(data.get('name') or '').strip():
        errors.append('top-level name is needed for stable result identity')
    sources = data.get('_sources', [])
    source_ids: set[str] = set()
    if not isinstance(sources, list):
        errors.append('_sources must be an array')
        sources = []
    for i, source in enumerate(sources):
        if not isinstance(source, dict):
            errors.append(f'_sources[{i}] must be an object')
            continue
        sid = source.get('id', f'legacy:{i}')
        if not isinstance(sid, str) or not sid.strip() or sid in source_ids:
            errors.append(f'_sources[{i}] has invalid/duplicate id')
        else:
            source_ids.add(sid)
        url = source.get('url')
        if not isinstance(url, str) or not _valid_url(url):
            errors.append(f'_sources[{i}] must have a valid HTTP(S) URL without credentials')
        if not source.get('title'):
            warnings.append(f'_sources[{i}] is missing title')
        accessed = source.get('accessed')
        if accessed is not None:
            try:
                date.fromisoformat(accessed)
            except (ValueError, TypeError):
                errors.append(f'_sources[{i}].accessed must be YYYY-MM-DD')
    claims = data.get('_claims', [])
    if not isinstance(claims, list):
        errors.append('_claims must be an array')
        claims = []
    claim_ids: set[str] = set()
    unsupported_claims: list[str] = []
    for i, claim in enumerate(claims):
        if not isinstance(claim, dict):
            errors.append(f'_claims[{i}] must be an object')
            continue
        cid = claim.get('id')
        if not isinstance(cid, str) or not re.fullmatch(r'[A-Za-z0-9][\w.-]{0,127}', cid):
            errors.append(f'_claims[{i}].id is missing or invalid')
            continue
        if cid in claim_ids:
            errors.append(f'duplicate claim id: {cid}')
        claim_ids.add(cid)
        if not isinstance(claim.get('text'), str) or not claim['text'].strip():
            errors.append(f'_claims[{i}].text must not be empty')
        status = claim.get('status')
        if status not in STATES:
            errors.append(f'_claims[{i}].status must be one of {sorted(STATES)}')
        ids = claim.get('source_ids', [])
        if not isinstance(ids, list) or any(not isinstance(sid, str) for sid in ids):
            errors.append(f'_claims[{i}].source_ids must be strings')
            ids = []
        for sid in ids:
            if sid not in source_ids:
                errors.append(f'_claims[{i}]: unknown source id {sid}')
        if status == 'supported' and not ids:
            errors.append(f'_claims[{i}]: supported claim has no source')
        if status != 'supported':
            unsupported_claims.append(cid)
        if status == 'supported' and ids and not claim.get('locator'):
            warnings.append(f'_claims[{i}]: no precise evidence locator supplied')
    if not sources:
        warnings.append('no evidence sources: cannot claim research-ready status')
    if unsupported_claims:
        warnings.append('non-supported claims must be presented as disputed/uncertain, not verified')
    structural_valid = not (missing_required or empty_required or errors)
    ready = structural_valid and not uncertain_required and bool(sources)
    if ready:
        status = 'research-ready-with-disagreements' if unsupported_claims else 'research-ready'
    elif not structural_valid:
        status = 'invalid'
    else:
        status = 'incomplete'
    return {
        'valid': ready,
        'structural_valid': structural_valid,
        'research_ready': ready,
        'status': status,
        'defined_fields': len(schema['names']),
        'required_fields': len(schema['required']),
        'covered_fields': len(schema['names'] & keys),
        'missing_required': sorted(missing_required),
        'missing_optional': sorted(missing_optional),
        'empty_required': sorted(empty_required),
        'uncertain_required': sorted(uncertain_required),
        'unsupported_claims': unsupported_claims,
        'extra_fields': sorted(keys - schema['names']),
        'sources_count': len(sources),
        'claims_count': len(claims),
        'errors': errors,
        'warnings': warnings,
        'note': 'Structural citation links do not verify source content or factual truth.',
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--fields', required=True)
    parser.add_argument('-j', '--json', required=True)
    parser.add_argument('--allow-incomplete', action='store_true', help='Return 0 only for structurally valid, explicitly incomplete results')
    args = parser.parse_args()
    try:
        report = validate(Path(args.fields), Path(args.json))
        print(json.dumps(report, ensure_ascii=False, indent=2))
        if report['valid'] or (args.allow_incomplete and report['structural_valid']):
            return 0
        return 1
    except Exception as exc:
        print(json.dumps({'valid': False, 'error': str(exc)}, ensure_ascii=False, indent=2))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
