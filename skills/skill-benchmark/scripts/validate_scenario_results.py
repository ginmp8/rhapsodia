#!/usr/bin/env python3
"""Validate portable behavioral scenario evidence for skill-benchmark."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from _common import dump_json

ALLOWED_CATEGORIES = {'should_activate', 'should_not_activate', 'ambiguous', 'edge_case'}
REQUIRED_FIELDS = {'id', 'category', 'prompt', 'expected_activation', 'actual_activation', 'output_conforms', 'quality_score', 'needs_rework'}
SHA_RE = re.compile(r'^[0-9a-f]{64}$')
ALLOWED_ARMS = {'without-skill', 'baseline', 'parent', 'candidate', 'single'}
ALLOWED_EVALUATOR_VISIBILITY = {'hidden', 'candidate-visible', 'not-applicable'}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8', errors='replace'))


def normalize_payload(data: Any) -> tuple[list[dict], dict, str]:
    if not isinstance(data, dict):
        raise ValueError('scenario results must use the versioned v2 object envelope')
    if data.get('schema_version') != 2:
        raise ValueError('scenario results must declare schema_version: 2')
    if not isinstance(data.get('scenarios'), list):
        raise ValueError('scenario results must include a scenarios array')
    meta = {key: value for key, value in data.items() if key != 'scenarios'}
    return data['scenarios'], meta, 'envelope-v2'


def is_bool_or_null(value: Any) -> bool:
    return value is None or isinstance(value, bool)


def validate_payload(data: Any) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        rows, meta, shape = normalize_payload(data)
    except Exception as exc:
        return {'status': 'fail', 'errors': [str(exc)], 'warnings': [], 'checks': {}, 'rows': [], 'metadata': {}, 'provenance_status': 'invalid'}

    if not rows:
        errors.append('scenario results array is empty')
    seen_ids: set[str] = set()
    categories: dict[str, int] = {}
    measured_rows = 0
    incomplete_rows = 0

    for index, item in enumerate(rows):
        label = f'row {index}'
        if not isinstance(item, dict):
            errors.append(f'{label} must be an object')
            continue
        sid = item.get('id')
        label = str(sid or label)
        missing = sorted(REQUIRED_FIELDS - set(item))
        if missing:
            errors.append(f'{label} missing fields: {missing}')
        if not isinstance(sid, str) or not sid.strip():
            errors.append(f'{label} has invalid id')
        elif sid in seen_ids:
            errors.append(f'duplicate id: {sid}')
        else:
            seen_ids.add(sid)

        category = item.get('category')
        if category not in ALLOWED_CATEGORIES:
            errors.append(f'{label} has invalid category: {category!r}')
        else:
            categories[category] = categories.get(category, 0) + 1
        if not isinstance(item.get('prompt'), str) or not item.get('prompt', '').strip():
            errors.append(f'{label} prompt must be a non-empty string')
        if not isinstance(item.get('expected_activation'), bool):
            errors.append(f'{label} expected_activation must be boolean')
        if not is_bool_or_null(item.get('actual_activation')):
            errors.append(f'{label} actual_activation must be boolean or null')
        if not is_bool_or_null(item.get('output_conforms')):
            errors.append(f'{label} output_conforms must be boolean or null')
        if not is_bool_or_null(item.get('needs_rework')):
            errors.append(f'{label} needs_rework must be boolean or null')
        quality = item.get('quality_score')
        if quality is not None and (not isinstance(quality, (int, float)) or isinstance(quality, bool) or quality < 0 or quality > 5):
            errors.append(f'{label} quality_score must be null or a number from 0 to 5')

        actual = item.get('actual_activation')
        conforms = item.get('output_conforms')
        rework = item.get('needs_rework')
        if actual is None or conforms is None or rework is None:
            incomplete_rows += 1
        else:
            measured_rows += 1

    if shape == 'envelope-v2':
        for field in ('target_identity_sha256', 'evaluator_identity_sha256', 'scenario_suite_sha256'):
            value = meta.get(field)
            if value is not None and (not isinstance(value, str) or not SHA_RE.fullmatch(value)):
                errors.append(f'{field} must be a lowercase 64-hex SHA-256 when present')
        origin = meta.get('evidence_origin')
        if origin is not None and origin not in {'executed', 'supplied'}:
            errors.append('evidence_origin must be executed or supplied when present')
        arm = meta.get('arm_type')
        if arm is not None and arm not in ALLOWED_ARMS:
            errors.append(f'arm_type must be one of {sorted(ALLOWED_ARMS)} when present')
        if arm == 'without-skill' and meta.get('target_identity_sha256'):
            errors.append('without-skill arm must omit target_identity_sha256')
        if arm in {'baseline', 'parent', 'candidate', 'single'} and meta.get('target_identity_sha256') is None:
            warnings.append(f'{arm} arm should include target_identity_sha256 for strict comparison claims')
        host_profile = meta.get('host_profile')
        if host_profile is not None and (not isinstance(host_profile, str) or not host_profile.strip()):
            errors.append('host_profile must be a non-empty string when present')
        trace_sha = meta.get('trace_manifest_sha256')
        if trace_sha is not None and (not isinstance(trace_sha, str) or not SHA_RE.fullmatch(trace_sha)):
            errors.append('trace_manifest_sha256 must be lowercase 64-hex when present')
        visibility = meta.get('evaluator_visibility')
        if visibility is not None and visibility not in ALLOWED_EVALUATOR_VISIBILITY:
            errors.append(f'evaluator_visibility must be one of {sorted(ALLOWED_EVALUATOR_VISIBILITY)} when present')
        saw_hidden = meta.get('candidate_saw_evaluator_only_assets')
        if saw_hidden is not None and not isinstance(saw_hidden, bool):
            errors.append('candidate_saw_evaluator_only_assets must be boolean when present')
        if visibility == 'hidden':
            if saw_hidden is True:
                errors.append('hidden evaluator is invalid when candidate saw evaluator-only assets')
            elif saw_hidden is None:
                warnings.append('hidden evaluator declared without candidate_saw_evaluator_only_assets evidence')
        self_improvement = meta.get('self_improvement')
        if self_improvement is not None:
            if not isinstance(self_improvement, dict):
                errors.append('self_improvement must be an object when present')
                self_improvement = {}
            generation_id = self_improvement.get('generation_id')
            if not isinstance(generation_id, str) or not generation_id.strip():
                errors.append('self_improvement.generation_id must be a non-empty string')
            for field in ('controller_identity_sha256', 'baseline_identity_sha256', 'candidate_identity_sha256'):
                value = self_improvement.get(field)
                if not isinstance(value, str) or not SHA_RE.fullmatch(value):
                    errors.append(f'self_improvement.{field} must be lowercase 64-hex')
            controller = self_improvement.get('controller_identity_sha256')
            baseline_id = self_improvement.get('baseline_identity_sha256')
            candidate_id = self_improvement.get('candidate_identity_sha256')
            if isinstance(controller, str) and isinstance(candidate_id, str) and controller == candidate_id:
                errors.append('self-improvement controller and candidate identities must differ')
            if arm == 'candidate' and meta.get('target_identity_sha256') and candidate_id != meta.get('target_identity_sha256'):
                errors.append('candidate target_identity_sha256 must match self_improvement.candidate_identity_sha256')
            if arm == 'baseline' and meta.get('target_identity_sha256') and baseline_id != meta.get('target_identity_sha256'):
                errors.append('baseline target_identity_sha256 must match self_improvement.baseline_identity_sha256')
    provenance_status = 'pinned' if all(meta.get(field) for field in ('target_identity_sha256', 'evaluator_identity_sha256', 'scenario_suite_sha256')) else 'unpinned'
    if provenance_status != 'pinned':
        warnings.append('scenario envelope is valid but target/evaluator identity is incomplete; comparison claims must remain unpinned')
    if incomplete_rows:
        warnings.append(f'{incomplete_rows} rows are incomplete and cannot support fully measured behavioral metrics')

    checks = {
        'shape': shape,
        'row_count': len(rows),
        'measured_rows': measured_rows,
        'incomplete_rows': incomplete_rows,
        'category_counts': categories,
        'ids_unique': len(seen_ids) == len([item for item in rows if isinstance(item, dict) and isinstance(item.get('id'), str)]),
        'target_identity_present': bool(meta.get('target_identity_sha256')),
        'evaluator_identity_present': bool(meta.get('evaluator_identity_sha256')),
        'arm_type': meta.get('arm_type'),
        'host_profile': meta.get('host_profile'),
        'trace_identity_present': bool(meta.get('trace_manifest_sha256')),
        'evaluator_visibility': meta.get('evaluator_visibility'),
        'evaluator_leakage_free': meta.get('candidate_saw_evaluator_only_assets') is False if meta.get('evaluator_visibility') == 'hidden' else None,
        'self_improvement_generation_id': meta.get('self_improvement', {}).get('generation_id') if isinstance(meta.get('self_improvement'), dict) else None,
        'self_improvement_controller_identity': meta.get('self_improvement', {}).get('controller_identity_sha256') if isinstance(meta.get('self_improvement'), dict) else None,
    }
    return {
        'status': 'pass' if not errors else 'fail',
        'errors': errors,
        'warnings': warnings,
        'checks': checks,
        'rows': rows,
        'metadata': meta,
        'provenance_status': provenance_status,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Validate skill-benchmark scenario result JSON.')
    parser.add_argument('--results', required=True, help='Path to scenario results JSON.')
    parser.add_argument('--json-output', help='Optional path for JSON validation evidence.')
    args = parser.parse_args(argv)
    try:
        result = validate_payload(load_json(Path(args.results)))
    except Exception as exc:
        result = {'status': 'fail', 'errors': [str(exc)], 'warnings': [], 'checks': {}, 'rows': [], 'metadata': {}, 'provenance_status': 'invalid'}
    public = {key: value for key, value in result.items() if key != 'rows'}
    if args.json_output:
        dump_json(public, args.json_output)
    dump_json(public)
    return 0 if result['status'] == 'pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())
