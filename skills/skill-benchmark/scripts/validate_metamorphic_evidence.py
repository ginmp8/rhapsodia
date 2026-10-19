#!/usr/bin/env python3
"""Check *structural* metamorphic evidence and mechanically check selected relations.

Does not execute LLMs, verify the truth of input-equivalence claims, or confirm faults.
The result is evidence-admissibility diagnostics, not a capability benchmark score.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

HASH = re.compile(r'^[a-f0-9]{64}$')
RELATIONS = {'same-route': 'route', 'same-stop': 'stop', 'same-constraints': 'constraints', 'same-authority': 'authority'}
STATUSES = {'executed', 'supplied', 'planned', 'not-run'}
ARMS = {'baseline', 'candidate', 'single'}


def _valid_record(record: Any, seen: set[str], errors: list[str]) -> dict[str, Any]:
    if not isinstance(record, dict):
        errors.append('relation must be an object')
        return {}
    rid = record.get('id')
    if not isinstance(rid, str) or not rid.strip() or rid in seen:
        errors.append('relation id missing or duplicated')
        return {}
    seen.add(rid)
    for field in ('base_case_id', 'variant_case_id', 'transformation', 'precondition_evidence'):
        if not isinstance(record.get(field), str) or not record[field].strip():
            errors.append(f'{rid}.{field} must be a nonempty string')
    if record.get('base_case_id') == record.get('variant_case_id'):
        errors.append(f'{rid}: base and variant must differ')
    relation = record.get('relation')
    if relation not in RELATIONS:
        errors.append(f'{rid}: relation must be one of {sorted(RELATIONS)}')
        return {}
    status = record.get('evidence_status')
    if status not in STATUSES:
        errors.append(f'{rid}: invalid evidence_status')
        return {}
    if status not in {'executed', 'supplied'}:
        return {'id': rid, 'relation': relation, 'status': 'not-measured'}
    base, variant = record.get('base'), record.get('variant')
    if not isinstance(base, dict) or not isinstance(variant, dict):
        errors.append(f'{rid}: observed/supplied relation requires base and variant objects')
        return {}
    field = RELATIONS[relation]
    if field not in base or field not in variant:
        errors.append(f'{rid}: missing observable field {field} in base or variant')
        return {}
    left, right = base[field], variant[field]
    if relation == 'same-constraints':
        if not all(isinstance(x, list) and len(x) == len(set(map(str, x))) and all(isinstance(i, str) and i for i in x) for x in (left, right)):
            errors.append(f'{rid}: constraints must contain unique, nonempty strings')
            return {}
        left, right = sorted(left), sorted(right)
    elif relation == 'same-stop':
        if type(left) is not bool or type(right) is not bool:
            errors.append(f'{rid}: stop must be boolean')
            return {}
    elif not all(isinstance(x, str) and x.strip() for x in (left, right)):
        errors.append(f'{rid}: {field} must be a nonempty string')
        return {}
    return {'id': rid, 'relation': relation, 'status': 'consistent' if left == right else 'candidate-violation'}


def validate(payload: Any) -> dict[str, Any]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return {'valid': False, 'errors': ['root must be an object'], 'results': []}
    if payload.get('schema_version') != 1:
        errors.append('schema_version must equal 1')
    if payload.get('arm') not in ARMS:
        errors.append('arm must be baseline, candidate or single')
    for field in ('suite_sha256', 'evaluator_sha256', 'runtime_sha256'):
        if not isinstance(payload.get(field), str) or not HASH.fullmatch(payload[field]):
            errors.append(f'{field} must be 64-character lowercase hex SHA-256')
    if payload.get('evaluator_visibility') not in {'candidate-visible', 'evaluator-only'}:
        errors.append('evaluator_visibility must be candidate-visible or evaluator-only')
    if not isinstance(payload.get('trial_policy'), str) or not payload.get('trial_policy').strip():
        errors.append('trial_policy must be a nonempty string')
    if not isinstance(payload.get('relations'), list) or not payload['relations']:
        errors.append('relations must be a nonempty array')
        rows = []
    else:
        seen: set[str] = set()
        rows = [_valid_record(r, seen, errors) for r in payload['relations']]
    rows = [x for x in rows if x]
    statuses = {key: sum(1 for x in rows if x['status'] == key) for key in ('consistent', 'candidate-violation', 'not-measured')}
    return {
        'valid': not errors,
        'errors': errors,
        'counts': statuses,
        'results': rows,
        'claim_limit': 'structural-check-only; MR candidate violations require semantic adjudication; no executed model call verified',
    }


def compare(base: Any, cand: Any, br: dict[str, Any], cr: dict[str, Any]) -> dict[str, Any]:
    issues = []
    if not br['valid'] or not cr['valid']:
        issues.append('invalid input evidence')
    if base.get('arm') != 'baseline' or cand.get('arm') != 'candidate':
        issues.append('comparison requires baseline and candidate arms')
    for field in ('suite_sha256', 'evaluator_sha256', 'runtime_sha256', 'evaluator_visibility', 'trial_policy'):
        if base.get(field) != cand.get(field):
            issues.append(f'{field} mismatch')
    def keyed(p: Any) -> dict[str, tuple[str, str, str, str, str]]:
        return {x['id']: (x.get('base_case_id'),x.get('variant_case_id'),x.get('transformation'),x.get('relation'),x.get('precondition_evidence')) for x in p.get('relations',[]) if isinstance(x,dict) and isinstance(x.get('id'),str)}
    if keyed(base) != keyed(cand):
        issues.append('relation/input specification mismatch')
    bb = {x['id']: x['status'] for x in br['results']}
    cc = {x['id']: x['status'] for x in cr['results']}
    aligned = sorted(set(bb)&set(cc)) if not issues else []
    return {
        'comparable': not issues,
        'reasons': issues,
        'paired_relation_count': len(aligned),
        'baseline_candidate_violations': sum(bb[i]=='candidate-violation' for i in aligned),
        'candidate_candidate_violations': sum(cc[i]=='candidate-violation' for i in aligned),
        'claim_limit': 'paired diagnostic evidence only; correlated relations are not independent trials; no proof of model improvement',
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument('--input', type=Path)
    mode.add_argument('--baseline', type=Path)
    p.add_argument('--candidate', type=Path)
    p.add_argument('--json-output', type=Path)
    args = p.parse_args()
    if bool(args.baseline) != bool(args.candidate):
        p.error('--baseline and --candidate must be supplied together')
    try:
        if args.input:
            result = validate(json.loads(args.input.read_text(encoding='utf-8')))
            ok = result['valid']
        else:
            base = json.loads(args.baseline.read_text(encoding='utf-8'))
            cand = json.loads(args.candidate.read_text(encoding='utf-8'))
            br, cr = validate(base), validate(cand)
            result = {'baseline': br, 'candidate': cr, 'comparison': compare(base,cand,br,cr)}
            ok = br['valid'] and cr['valid'] and result['comparison']['comparable']
    except (OSError, ValueError, UnicodeError) as exc:
        result = {'valid': False, 'errors': [f'input read/JSON error: {exc}']}
        ok = False
    content = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + '\n'
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(content, encoding='utf-8')
    print(content, end='')
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
