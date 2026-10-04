#!/usr/bin/env python3
"""Validate consistency audit reports (v1/v2 compatibility, v3 strict contract)."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

V1_REQUIRED_TOP = {'target_path', 'generated_at', 'inventory_summary', 'findings', 'score'}
V2_REQUIRED_TOP = V1_REQUIRED_TOP | {
    'report_version', 'evidence_type', 'inventory_identity', 'authority_contract',
    'classification_contract', 'resource_classification', 'readiness',
}
V3_REQUIRED_TOP = V2_REQUIRED_TOP | {'relation_contract', 'conformance', 'evidence_classes'}
REQUIRED_FINDING = {
    'id', 'severity', 'category', 'title', 'evidence', 'problem', 'repair', 'gate', 'confidence'
}
V2_FINDING = REQUIRED_FINDING | {'subjects', 'evidence_label'}
V3_FINDING = V2_FINDING | {'evidence_class'}
VALID_SEVERITIES = {'blocker', 'high', 'medium', 'low'}
VALID_CONFIDENCE = {'high', 'medium', 'low'}
VALID_STATUSES = {
    'current', 'duplicate', 'obsolete', 'migration-only', 'contradictory',
    'orphaned', 'integrable', 'blocked', 'unknown',
}
TRACE_DIMENSIONS = {'imports', 'links', 'references', 'consumers', 'tests', 'validators', 'examples', 'packaging', 'migration_paths', 'handoffs'}
TRACE_STATES = {'found', 'inspected-none', 'not-inspected', 'unsupported', 'blocked'}
EVIDENCE_CLASSES = {'mechanically-proven', 'behaviorally-proven', 'semantically-supported', 'planned', 'blocked'}
PORTABLE_STATUSES = {'internal-static-pass', 'internal-static-fail', 'not-run', 'blocked'}
HOST_STATUSES = {'pass', 'pass-with-warnings', 'fail', 'not-run', 'blocked', 'not-proven'}
REFERENCE_VALIDATOR_STATUSES = {'pass', 'fail', 'supplemental-not-run', 'blocked'}


def _validate_common_v2(data: dict, errors: list[str], *, version: int) -> None:
    identity = data.get('inventory_identity')
    if not isinstance(identity, str) or len(identity) != 64:
        errors.append('inventory_identity must be a SHA-256 hex string')
    contract = data.get('classification_contract', {})
    if set(contract.get('statuses', [])) != VALID_STATUSES:
        errors.append('classification_contract.statuses must match the closed status enum')
    required_trace = set(contract.get('required_deletion_trace_dimensions', []))
    if required_trace != TRACE_DIMENSIONS:
        errors.append('classification_contract required deletion trace dimensions are incomplete')
    if version >= 3 and set(contract.get('trace_coverage_states', [])) != TRACE_STATES:
        errors.append('classification_contract.trace_coverage_states must match the closed coverage-state enum')

    rows = data.get('resource_classification')
    if not isinstance(rows, list):
        errors.append('resource_classification must be a list')
    else:
        paths: set[str] = set()
        for i, row in enumerate(rows):
            if not isinstance(row, dict):
                errors.append(f'resource classification {i} is not an object')
                continue
            required = {'path', 'role', 'provisional_status', 'confidence', 'evidence', 'trace', 'semantic_review_required', 'deletion_allowed'}
            if version >= 3:
                required.add('trace_coverage')
            for key in sorted(required):
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
            if version >= 3:
                coverage = row.get('trace_coverage', {})
                if not isinstance(coverage, dict) or not TRACE_DIMENSIONS.issubset(coverage):
                    errors.append(f'resource classification {i} trace_coverage is missing required dimensions')
                elif any(not isinstance(v, dict) or v.get('state') not in TRACE_STATES for v in coverage.values()):
                    errors.append(f'resource classification {i} has invalid trace coverage state')
    readiness = data.get('readiness', {})
    if readiness.get('status') not in {'not-proven', 'blocked-by-static-findings'}:
        errors.append('readiness.status must not claim publish/package readiness from static audit alone')


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except Exception as exc:
        return [f'invalid json: {exc}']

    version = data.get('report_version', 1)
    if version == 1:
        required_top = V1_REQUIRED_TOP
    elif version == 2:
        required_top = V2_REQUIRED_TOP
    elif version == 3:
        required_top = V3_REQUIRED_TOP
    else:
        return [f'unsupported report_version: {version}']
    missing = required_top - set(data)
    if missing:
        errors.append(f'missing top-level fields: {sorted(missing)}')

    findings = data.get('findings')
    if not isinstance(findings, list):
        errors.append('findings must be a list')
        return errors
    ids: set[str] = set()
    required_finding = REQUIRED_FINDING if version == 1 else (V2_FINDING if version == 2 else V3_FINDING)
    for i, item in enumerate(findings):
        if not isinstance(item, dict):
            errors.append(f'finding {i} is not an object')
            continue
        miss = required_finding - set(item)
        if miss:
            errors.append(f'finding {i} missing fields: {sorted(miss)}')
        if item.get('severity') not in VALID_SEVERITIES:
            errors.append(f'finding {i} invalid severity: {item.get("severity")}')
        if item.get('confidence') not in VALID_CONFIDENCE:
            errors.append(f'finding {i} invalid confidence: {item.get("confidence")}')
        if version >= 3 and item.get('evidence_class') not in EVIDENCE_CLASSES:
            errors.append(f'finding {i} invalid evidence_class: {item.get("evidence_class")}')
        fid = item.get('id')
        if not fid:
            errors.append(f'finding {i} missing id')
        elif fid in ids:
            errors.append(f'duplicate finding id: {fid}')
        ids.add(fid)

    score = data.get('score', {})
    if not isinstance(score, dict) or 'score' not in score or 'status' not in score:
        errors.append('score must include score and status')

    if version >= 2:
        _validate_common_v2(data, errors, version=version)

    if version == 3:
        relation_contract = data.get('relation_contract', {})
        relations = relation_contract.get('relations')
        if not isinstance(relations, list):
            errors.append('relation_contract.relations must be a list')
        else:
            for i, relation in enumerate(relations):
                if not isinstance(relation, dict) or not {'source', 'target', 'relation', 'detector', 'evidence_class'}.issubset(relation):
                    errors.append(f'relation {i} is missing typed relation fields')
                elif relation.get('evidence_class') not in EVIDENCE_CLASSES:
                    errors.append(f'relation {i} has invalid evidence_class')
        conformance = data.get('conformance', {})
        portable = conformance.get('portable_core_spec', {})
        host = conformance.get('host_compatibility', {})
        ref = conformance.get('reference_validator', {})
        if portable.get('status') not in PORTABLE_STATUSES:
            errors.append('conformance.portable_core_spec has invalid status')
        if host.get('status') not in HOST_STATUSES:
            errors.append('conformance.host_compatibility has invalid status')
        if ref.get('status') not in REFERENCE_VALIDATOR_STATUSES:
            errors.append('conformance.reference_validator has invalid status')
        summary = data.get('evidence_classes', {})
        if not isinstance(summary, dict) or set(summary) != EVIDENCE_CLASSES or any(not isinstance(v, int) or v < 0 for v in summary.values()):
            errors.append('evidence_classes must contain non-negative counts for the closed evidence-class enum')
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
