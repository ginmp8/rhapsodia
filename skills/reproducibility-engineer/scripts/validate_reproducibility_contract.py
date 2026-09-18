#!/usr/bin/env python3
from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
import json
from pathlib import Path

ALLOWED_CEILINGS = {'unclassified','objective-artifact','tool-action','research-analytic','constrained-subjective'}
VAR_CLASSES = {'mechanical','constrained-heuristic','model-judgment','external-nondeterminism','schema-type'}


def main() -> int:
    ap = argparse.ArgumentParser(description='Validate a reproducibility contract using only the Python standard library.')
    ap.add_argument('contract')
    ap.add_argument('--strict', action='store_true')
    args = ap.parse_args()

    path = Path(args.contract)
    errors = []
    warnings = []
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except Exception as exc:
        print(json.dumps({'status':'fail','errors':[f'invalid JSON: {exc}']}, indent=2))
        return 1

    required = ['contract_version','target','ceiling','protected_paths','hard_gates','variability','evaluators','scenario_groups','acceptance','delivery']
    for key in required:
        if key not in data:
            errors.append(f'missing key: {key}')

    if data.get('contract_version') != 1:
        errors.append('contract_version must be 1')
    ceiling = data.get('ceiling')
    if ceiling not in ALLOWED_CEILINGS:
        errors.append(f'unsupported ceiling: {ceiling!r}')
    if args.strict and ceiling == 'unclassified':
        errors.append('strict validation requires a classified ceiling')

    target = data.get('target', {})
    if not isinstance(target, dict) or not target.get('name') or not target.get('path'):
        errors.append('target must contain non-empty name and path')
    if not isinstance(data.get('protected_paths', []), list):
        errors.append('protected_paths must be a list')
    if not isinstance(data.get('hard_gates', []), list) or len(data.get('hard_gates', [])) < 1:
        errors.append('hard_gates must be a non-empty list')

    variability = data.get('variability', [])
    if not isinstance(variability, list):
        errors.append('variability must be a list')
    else:
        ids = set()
        for i, item in enumerate(variability):
            if not isinstance(item, dict):
                errors.append(f'variability[{i}] must be an object')
                continue
            for key in ['id','surface','class','target_control','validation']:
                if not item.get(key):
                    errors.append(f'variability[{i}] missing {key}')
            if item.get('class') not in VAR_CLASSES:
                errors.append(f'variability[{i}] unsupported class: {item.get("class")!r}')
            if item.get('id') in ids:
                errors.append(f'duplicate variability id: {item.get("id")}')
            ids.add(item.get('id'))

    evaluators = data.get('evaluators', [])
    if not isinstance(evaluators, list):
        errors.append('evaluators must be a list')
    else:
        for i, item in enumerate(evaluators):
            if not isinstance(item, dict):
                errors.append(f'evaluators[{i}] must be an object')
                continue
            for key in ['id','type','metric']:
                if not item.get(key):
                    errors.append(f'evaluators[{i}] missing {key}')
            if not item.get('command') and not item.get('manual_review'):
                warnings.append(f'evaluators[{i}] has neither command nor manual_review')

    acceptance = data.get('acceptance', {})
    if not isinstance(acceptance, dict):
        errors.append('acceptance must be an object')
    else:
        if acceptance.get('weaken_hard_gates_to_pass') is not False:
            errors.append('weaken_hard_gates_to_pass must be false')
        if acceptance.get('freeze_after_pass') is not True:
            errors.append('freeze_after_pass must be true')
        limit = acceptance.get('stagnation_limit')
        if not isinstance(limit, int) or limit < 1:
            errors.append('stagnation_limit must be an integer >= 1')

    source_integrity = data.get('source_integrity')
    source_keys = [
        'snapshot_material_evidence_before_analysis',
        'immutable_pinned_vcs_reads_when_supported',
        'reject_source_alias_escape',
        'rebaseline_if_source_identity_changes',
    ]
    if source_integrity is not None:
        if not isinstance(source_integrity, dict):
            errors.append('source_integrity must be an object when present')
        else:
            for key in source_keys:
                if source_integrity.get(key) is not True:
                    errors.append(f'source_integrity.{key} must be true when source_integrity is declared')
    elif args.strict:
        warnings.append('strict validation: source_integrity is absent; legacy contracts remain valid but do not declare the newer source-identity controls')

    delivery = data.get('delivery', {})
    if not isinstance(delivery, dict):
        errors.append('delivery must be an object')
    else:
        legacy_delivery_keys = ['atomic_when_applicable', 'package_exact_frozen_candidate']
        for key in legacy_delivery_keys:
            if delivery.get(key) is not True:
                errors.append(f'delivery.{key} must be true')
        advanced_delivery_keys = [
            'reject_output_aliases_before_write',
            'preserve_last_good_on_failure',
            'preserve_recovery_on_rollback_failure',
            'durable_complete_receipts',
        ]
        missing_advanced = [key for key in advanced_delivery_keys if delivery.get(key) is not True]
        if missing_advanced:
            warnings.append('delivery does not declare all advanced integrity controls: ' + ', '.join(missing_advanced))

    if args.strict:
        if not variability:
            errors.append('strict validation requires at least one variability item')
        if not evaluators:
            errors.append('strict validation requires at least one evaluator or review gate')

    report = {'status':'fail' if errors else ('warn' if warnings else 'pass'),'errors':errors,'warnings':warnings}
    print(json.dumps(report, indent=2))
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
