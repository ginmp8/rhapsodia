#!/usr/bin/env python3
"""Inspect / explicitly stamp exact research scope for safe, selective resumption."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from datetime import date
from pathlib import Path
from validate_result import validate
from workspace_contract import load_outline, load_fields, sha256_file


def fingerprint(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False,
                                     separators=(',', ':')).encode('utf-8')).hexdigest()


def current_identity(outline: Path, fields: Path, data: dict, today: str | None = None) -> dict:
    root = Path(__file__).resolve().parents[1]
    version_file = root / 'VERSION'
    spec = load_outline(outline)
    matching = [item for item in spec['items'] if item.get('name') == data.get('name')]
    if len(matching) != 1:
        raise ValueError('result identity does not match exactly one outline item')
    schema = load_fields(fields)
    scope = {'topic': spec.get('topic'), 'output_language': spec.get('output_language'),
             'research': spec.get('research'), 'item': matching[0]}
    contract = {'categories': schema['categories'], 'required': sorted(schema['required'])}
    return {'contract_version': 2,
            'outline_sha256': sha256_file(outline),
            'fields_sha256': sha256_file(fields),
            'scope_fingerprint': fingerprint(scope),
            'fields_contract_fingerprint': fingerprint(contract),
            'skill_version': version_file.read_text(encoding='utf-8').strip() if version_file.exists() else 'unknown',
            'sources_fingerprint': fingerprint(data.get('_sources', [])),
            'recorded_at': today or date.today().isoformat(),
            'freshness_verified': False}


def inspect(outline: Path, fields: Path, result: Path,
            max_age_days: int | None = None, today: str | None = None) -> dict:
    data = json.loads(result.read_text(encoding='utf-8'))
    if not isinstance(data, dict):
        raise ValueError('result must be object')
    verdict = validate(fields, result)
    new = current_identity(outline, fields, data, today)
    stored = data.get('_run')
    reasons = []
    warnings = []
    if not verdict['valid']:
        reasons.append('result-incomplete-or-invalid')
    if not isinstance(stored, dict):
        reasons.append('missing-run-identity')
    else:
        for field in ('scope_fingerprint', 'fields_contract_fingerprint', 'skill_version', 'sources_fingerprint'):
            if stored.get(field) != new[field]:
                reasons.append('changed-' + field)
        if stored.get('outline_sha256') != new['outline_sha256'] or stored.get('fields_sha256') != new['fields_sha256']:
            warnings.append('raw files changed: semantic contracts checked separately')
        if max_age_days is not None:
            if max_age_days < 0:
                raise ValueError('max_age_days must be >= 0')
            try:
                delta = (date.fromisoformat(today or date.today().isoformat()) - date.fromisoformat(stored['recorded_at'])).days
                if delta < 0 or delta > max_age_days:
                    reasons.append('age-outside-policy')
            except (KeyError, TypeError, ValueError):
                reasons.append('invalid-recorded-at')
    return {'safe_to_resume_without_scope_research': not reasons,
            'freshness_verified': False,
            'status': 'reusable-scope-only' if not reasons else 'needs-revalidation',
            'reasons': reasons, 'warnings': warnings, 'current_identity': new,
            'note': 'Identity checks do not confirm external sources remain accurate. Recheck time-sensitive facts.'}


def atomic_stamp(path: Path, new: dict):
    data = json.loads(path.read_text(encoding='utf-8'))
    data['_run'] = new
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', dir=path.parent,
                                     prefix='.research-result-', delete=False) as f:
        temp = Path(f.name)
        try:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write('\n')
            f.flush()
            os.fsync(f.fileno())
        except BaseException:
            temp.unlink(missing_ok=True)
            raise
    os.replace(temp, path)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--outline', required=True)
    p.add_argument('--fields', required=True)
    p.add_argument('--json', required=True)
    p.add_argument('--stamp', action='store_true', help='Write a run identity after completing independent evidence review')
    p.add_argument('--max-age-days', type=int)
    p.add_argument('--today', help='Deterministic YYYY-MM-DD clock for tests')
    a = p.parse_args()
    try:
        if a.today:
            date.fromisoformat(a.today)
        o, f, j = Path(a.outline), Path(a.fields), Path(a.json)
        if a.stamp:
            if not validate(f, j)['valid']:
                raise ValueError('cannot stamp invalid/incomplete research')
            data = json.loads(j.read_text(encoding='utf-8'))
            atomic_stamp(j, current_identity(o, f, data, a.today))
        policy = a.max_age_days
        if policy is None:
            spec = load_outline(o)
            configured = spec.get('research', {}).get('max_age_days')
            if configured not in (None, ''):
                policy = int(configured)
        answer = inspect(o, f, j, policy, a.today)
        print(json.dumps(answer, ensure_ascii=False, indent=2))
        return 0 if answer['safe_to_resume_without_scope_research'] else 1
    except Exception as exc:
        print(json.dumps({'safe_to_resume_without_scope_research': False, 'error': str(exc)}, ensure_ascii=False, indent=2))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
