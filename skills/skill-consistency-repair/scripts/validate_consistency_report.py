#!/usr/bin/env python3
"""Validate machine-readable consistency audit reports (v1 compatibility, v2 strict contract)."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

V1_REQUIRED_TOP = {'target_path', 'generated_at', 'inventory_summary', 'findings', 'score'}
V2_REQUIRED_TOP = V1_REQUIRED_TOP | {
    'report_version', 'evidence_type', 'inventory_identity', 'authority_contract',
    'classification_contract', 'resource_classification', 'readiness',
}
REQUIRED_FINDING = {
    'id', 'severity', 'category', 'title', 'evidence', 'problem', 'repair', 'gate', 'confidence'
}
V2_FINDING = REQUIRED_FINDING | {'subjects', 'evidence_label'}
VALID_SEVERITIES = {'blocker', 'high', 'medium', 'low'}
VALID_CONFIDENCE = {'high', 'medium', 'low'}
VALID_STATUSES = {
    'current', 'duplicate', 'obsolete', 'migration-only', 'contradictory',
    'orphaned', 'integrable', 'blocked', 'unknown',
}
TRACE_DIMENSIONS = {'imports', 'links', 'references', 'consumers', 'tests', 'validators', 'examples', 'packaging', 'migration_paths', 'handoffs'}


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except Exception as exc:
        return [f'invalid json: {exc}']

    version = data.get('report_version', 1)
    required_top = V2_REQUIRED_TOP if version == 2 else V1_REQUIRED_TOP
    missing = required_top - set(data)
    if missing:
        errors.append(f'missing top-level fields: {sorted(missing)}')

    findings = data.get('findings')
    if not isinstance(findings, list):
        errors.append('findings must be a list')
        return errors
    ids: set[str] = set()
    for i, item in enumerate(findings):
        if not isinstance(item, dict):
            errors.append(f'finding {i} is not an object')
            continue
        required = V2_FINDING if version == 2 else REQUIRED_FINDING
        miss = required - set(item)
        if miss:
            errors.append(f'finding {i} missing fields: {sorted(miss)}')
        if item.get('severity') not in VALID_SEVERITIES:
            errors.append(f'finding {i} invalid severity: {item.get("severity")}')
        if item.get('confidence') not in VALID_CONFIDENCE:
            errors.append(f'finding {i} invalid confidence: {item.get("confidence")}')
        fid = item.get('id')
        if not fid:
            errors.append(f'finding {i} missing id')
        elif fid in ids:
            errors.append(f'duplicate finding id: {fid}')
        ids.add(fid)

    score = data.get('score', {})
    if not isinstance(score, dict) or 'score' not in score or 'status' not in score:
        errors.append('score must include score and status')

    if version == 2:
        identity = data.get('inventory_identity')
        if not isinstance(identity, str) or len(identity) != 64:
            errors.append('inventory_identity must be a SHA-256 hex string')
        contract = data.get('classification_contract', {})
        if set(contract.get('statuses', [])) != VALID_STATUSES:
            errors.append('classification_contract.statuses must match the closed status enum')
        required_trace = set(contract.get('required_deletion_trace_dimensions', []))
        if required_trace != TRACE_DIMENSIONS:
            errors.append('classification_contract required deletion trace dimensions are incomplete')
        rows = data.get('resource_classification')
        if not isinstance(rows, list):
            errors.append('resource_classification must be a list')
        else:
            paths: set[str] = set()
            for i, row in enumerate(rows):
                if not isinstance(row, dict):
                    errors.append(f'resource classification {i} is not an object')
                    continue
                for key in ('path', 'role', 'provisional_status', 'confidence', 'evidence', 'trace', 'semantic_review_required', 'deletion_allowed'):
                    if key not in row:
                        errors.append(f'resource classification {i} missing {key}')
                path_value = row.get('path')
                if path_value in paths:
                    errors.append(f'duplicate resource classification path: {path_value}')
                paths.add(path_value)
                if row.get('provisional_status') not in VALID_STATUSES:
                    errors.append(f'resource classification {i} invalid status: {row.get("provisional_status")}')
                if row.get('deletion_allowed') is not False:
                    errors.append(f'resource classification {i} must not mechanically authorize deletion')
                trace = row.get('trace', {})
                if not isinstance(trace, dict) or not TRACE_DIMENSIONS.issubset(trace):
                    errors.append(f'resource classification {i} trace is missing required dimensions')
        readiness = data.get('readiness', {})
        if readiness.get('status') not in {'not-proven', 'blocked-by-static-findings'}:
            errors.append('readiness.status must not claim publish/package readiness from static audit alone')
    elif version != 1:
        errors.append(f'unsupported report_version: {version}')
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description='Validate a consistency audit JSON report.')
    parser.add_argument('report')
    args = parser.parse_args()
    errors = validate(Path(args.report))
    if errors:
        for err in errors:
            print(f'ERROR: {err}')
        return 1
    print('[OK] consistency report is valid')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
