#!/usr/bin/env python3
"""Validate portable behavioral scenario evidence for skill-benchmark.

Schema v2 remains readable for compatibility. Schema v3 adds repeated trials,
runtime identity, suite semantics, grader calibration metadata, and efficiency
observations without changing v2 meaning.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from _common import dump_json

ALLOWED_CATEGORIES = {'should_activate', 'should_not_activate', 'ambiguous', 'edge_case'}
V2_REQUIRED_FIELDS = {'id', 'category', 'prompt', 'expected_activation', 'actual_activation', 'output_conforms', 'quality_score', 'needs_rework'}
V3_SCENARIO_FIELDS = {'id', 'category', 'prompt', 'expected_activation', 'trials'}
V3_TRIAL_FIELDS = {'trial_id', 'actual_activation', 'output_conforms', 'quality_score', 'needs_rework'}
SHA_RE = re.compile(r'^[0-9a-f]{64}$')
ALLOWED_ARMS = {'without-skill', 'length-control', 'baseline', 'parent', 'candidate', 'single'}
ALLOWED_EVALUATOR_VISIBILITY = {'hidden', 'candidate-visible', 'not-applicable'}
ALLOWED_SUITE_ROLES = {'diagnostic', 'capability', 'regression', 'holdout'}
ALLOWED_DISTRIBUTIONS = {'diagnostic-balanced', 'production-representative', 'custom'}
ALLOWED_GRADER_TYPES = {'deterministic', 'llm', 'human', 'mixed'}
ALLOWED_CALIBRATION = {'pass', 'review', 'fail', 'not-run'}
EFFICIENCY_FIELDS = ('input_tokens', 'output_tokens', 'latency_ms', 'tool_calls', 'cost_usd')


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8', errors='replace'))


def is_bool_or_null(value: Any) -> bool:
    return value is None or isinstance(value, bool)


def _valid_number(value: Any, *, minimum: float = 0.0) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and value >= minimum


def _validate_common_meta(meta: dict[str, Any], errors: list[str], warnings: list[str], version: int) -> None:
    for field in ('target_identity_sha256', 'evaluator_identity_sha256', 'scenario_suite_sha256', 'runtime_profile_sha256'):
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
    if arm in {'baseline', 'parent', 'candidate', 'single', 'length-control'} and meta.get('target_identity_sha256') is None:
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

    if version >= 3:
        if not meta.get('evaluator_identity_sha256'):
            errors.append('schema v3 requires evaluator_identity_sha256')
        if not meta.get('scenario_suite_sha256'):
            errors.append('schema v3 requires scenario_suite_sha256')
        if not meta.get('runtime_profile_sha256'):
            errors.append('schema v3 requires runtime_profile_sha256')
        if meta.get('suite_role') not in ALLOWED_SUITE_ROLES:
            errors.append(f'schema v3 suite_role must be one of {sorted(ALLOWED_SUITE_ROLES)}')
        if meta.get('distribution_profile') not in ALLOWED_DISTRIBUTIONS:
            errors.append(f'schema v3 distribution_profile must be one of {sorted(ALLOWED_DISTRIBUTIONS)}')
        grader_type = meta.get('grader_type', 'deterministic')
        if grader_type not in ALLOWED_GRADER_TYPES:
            errors.append(f'grader_type must be one of {sorted(ALLOWED_GRADER_TYPES)}')
        calibration = meta.get('grader_calibration')
        if grader_type in {'llm', 'mixed'}:
            if not isinstance(calibration, dict):
                warnings.append('model-based grader declared without grader_calibration evidence')
            else:
                status = calibration.get('status')
                if status not in ALLOWED_CALIBRATION:
                    errors.append(f'grader_calibration.status must be one of {sorted(ALLOWED_CALIBRATION)}')
                if status == 'pass':
                    csha = calibration.get('calibration_set_sha256')
                    if not isinstance(csha, str) or not SHA_RE.fullmatch(csha):
                        errors.append('grader_calibration.calibration_set_sha256 is required when calibration passes')
                agreement = calibration.get('human_agreement')
                if agreement is not None and (not _valid_number(agreement) or agreement > 1):
                    errors.append('grader_calibration.human_agreement must be in 0..1 when present')
                for field in ('position_balanced', 'length_controlled', 'abstention_supported'):
                    value = calibration.get(field)
                    if value is not None and not isinstance(value, bool):
                        errors.append(f'grader_calibration.{field} must be boolean when present')
        if meta.get('distribution_profile') == 'diagnostic-balanced':
            warnings.append('diagnostic-balanced evidence does not establish production prevalence')


def _validate_v2(data: dict[str, Any], errors: list[str], warnings: list[str]) -> tuple[list[dict[str, Any]], dict[str, int]]:
    scenarios = data.get('scenarios')
    if not isinstance(scenarios, list):
        errors.append('scenario results must include a scenarios array')
        return [], {}
    if not scenarios:
        errors.append('scenario results array is empty')
    seen_ids: set[str] = set()
    categories: dict[str, int] = {}
    rows: list[dict[str, Any]] = []
    for index, item in enumerate(scenarios):
        label = f'row {index}'
        if not isinstance(item, dict):
            errors.append(f'{label} must be an object')
            continue
        sid = item.get('id')
        label = str(sid or label)
        missing = sorted(V2_REQUIRED_FIELDS - set(item))
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
        if quality is not None and (not _valid_number(quality) or quality > 5):
            errors.append(f'{label} quality_score must be null or a number from 0 to 5')
        row = dict(item)
        row['scenario_id'] = sid
        row['trial_id'] = None
        rows.append(row)
    return rows, categories


def _validate_v3(data: dict[str, Any], errors: list[str], warnings: list[str]) -> tuple[list[dict[str, Any]], dict[str, int]]:
    scenarios = data.get('scenarios')
    if not isinstance(scenarios, list):
        errors.append('schema v3 must include a scenarios array')
        return [], {}
    if not scenarios:
        errors.append('scenario results array is empty')
    seen_ids: set[str] = set()
    categories: dict[str, int] = {}
    rows: list[dict[str, Any]] = []
    for index, scenario in enumerate(scenarios):
        if not isinstance(scenario, dict):
            errors.append(f'scenario[{index}] must be an object')
            continue
        sid = scenario.get('id')
        label = str(sid or f'scenario[{index}]')
        missing = sorted(V3_SCENARIO_FIELDS - set(scenario))
        if missing:
            errors.append(f'{label} missing fields: {missing}')
        if not isinstance(sid, str) or not sid.strip():
            errors.append(f'{label} has invalid id')
        elif sid in seen_ids:
            errors.append(f'duplicate scenario id: {sid}')
        else:
            seen_ids.add(sid)
        category = scenario.get('category')
        if category not in ALLOWED_CATEGORIES:
            errors.append(f'{label} has invalid category: {category!r}')
        else:
            categories[category] = categories.get(category, 0) + 1
        prompt = scenario.get('prompt')
        if not isinstance(prompt, str) or not prompt.strip():
            errors.append(f'{label} prompt must be a non-empty string')
        expected = scenario.get('expected_activation')
        if not isinstance(expected, bool):
            errors.append(f'{label} expected_activation must be boolean')
        trials = scenario.get('trials')
        if not isinstance(trials, list) or not trials:
            errors.append(f'{label}.trials must be a non-empty array')
            continue
        if len(trials) < 2:
            warnings.append(f'{label} has fewer than two trials; strong stochastic claims will be inconclusive')
        trial_ids: set[str] = set()
        for tindex, trial in enumerate(trials):
            tlabel = f'{label}.trial[{tindex}]'
            if not isinstance(trial, dict):
                errors.append(f'{tlabel} must be an object')
                continue
            tmissing = sorted(V3_TRIAL_FIELDS - set(trial))
            if tmissing:
                errors.append(f'{tlabel} missing fields: {tmissing}')
            tid = trial.get('trial_id')
            if not isinstance(tid, str) or not tid.strip():
                errors.append(f'{tlabel}.trial_id must be non-empty')
            elif tid in trial_ids:
                errors.append(f'{label} duplicate trial_id: {tid}')
            else:
                trial_ids.add(tid)
            for field in ('actual_activation', 'output_conforms', 'needs_rework'):
                if not is_bool_or_null(trial.get(field)):
                    errors.append(f'{tlabel}.{field} must be boolean or null')
            quality = trial.get('quality_score')
            if quality is not None and (not _valid_number(quality) or quality > 5):
                errors.append(f'{tlabel}.quality_score must be null or a number from 0 to 5')
            for field in EFFICIENCY_FIELDS:
                value = trial.get(field)
                if value is not None and not _valid_number(value):
                    errors.append(f'{tlabel}.{field} must be a non-negative number when present')
            rows.append({
                'id': sid,
                'scenario_id': sid,
                'trial_id': tid,
                'category': category,
                'prompt': prompt,
                'expected_activation': expected,
                'actual_activation': trial.get('actual_activation'),
                'output_conforms': trial.get('output_conforms'),
                'quality_score': quality,
                'needs_rework': trial.get('needs_rework'),
                **{field: trial.get(field) for field in EFFICIENCY_FIELDS},
            })
    return rows, categories


def validate_payload(data: Any) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(data, dict):
        return {'status': 'fail', 'errors': ['scenario results must use a versioned v2 object envelope or v3 object envelope'], 'warnings': [], 'checks': {}, 'rows': [], 'metadata': {}, 'provenance_status': 'invalid'}
    version = data.get('schema_version')
    if version not in {2, 3}:
        return {'status': 'fail', 'errors': ['scenario results must declare schema_version: 2 or 3'], 'warnings': [], 'checks': {}, 'rows': [], 'metadata': {}, 'provenance_status': 'invalid'}
    meta = {key: value for key, value in data.items() if key != 'scenarios'}
    _validate_common_meta(meta, errors, warnings, version)
    if version == 2:
        rows, categories = _validate_v2(data, errors, warnings)
        shape = 'envelope-v2'
    else:
        rows, categories = _validate_v3(data, errors, warnings)
        shape = 'envelope-v3'

    measured_rows = 0
    incomplete_rows = 0
    for row in rows:
        if row.get('actual_activation') is None or row.get('output_conforms') is None or row.get('needs_rework') is None:
            incomplete_rows += 1
        else:
            measured_rows += 1

    arm = meta.get('arm_type')
    pin_fields = ['evaluator_identity_sha256', 'scenario_suite_sha256']
    if arm != 'without-skill':
        pin_fields.insert(0, 'target_identity_sha256')
    if version >= 3:
        pin_fields.append('runtime_profile_sha256')
    provenance_status = 'pinned' if all(meta.get(field) for field in pin_fields) else 'unpinned'
    if provenance_status != 'pinned':
        warnings.append('scenario envelope is valid but comparison identity is incomplete; strict comparison claims must remain unpinned')
    if incomplete_rows:
        warnings.append(f'{incomplete_rows} trial rows are incomplete and cannot support fully measured behavioral metrics')

    scenario_ids = {row.get('scenario_id') for row in rows if row.get('scenario_id')}
    trial_ids = {(row.get('scenario_id'), row.get('trial_id')) for row in rows}
    checks = {
        'shape': shape,
        'schema_version': version,
        'scenario_count': len(scenario_ids),
        'trial_row_count': len(rows),
        'measured_rows': measured_rows,
        'incomplete_rows': incomplete_rows,
        'category_counts': categories,
        'trial_keys_unique': len(trial_ids) == len(rows),
        'target_identity_present': bool(meta.get('target_identity_sha256')),
        'evaluator_identity_present': bool(meta.get('evaluator_identity_sha256')),
        'runtime_profile_identity_present': bool(meta.get('runtime_profile_sha256')),
        'arm_type': arm,
        'host_profile': meta.get('host_profile'),
        'suite_role': meta.get('suite_role'),
        'distribution_profile': meta.get('distribution_profile'),
        'grader_type': meta.get('grader_type'),
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
