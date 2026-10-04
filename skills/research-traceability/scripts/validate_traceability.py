#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from _common import atomic_write_json, sha256_file

ID_PATTERNS = {
    'sources': re.compile(r'^S-[0-9]{3,}$'),
    'findings': re.compile(r'^F-[0-9]{3,}$'),
    'requirements': re.compile(r'^R-[0-9]{3,}$'),
    'changes': re.compile(r'^C-[0-9]{3,}$'),
    'evaluations': re.compile(r'^E-[0-9]{3,}$'),
    'conflicts': re.compile(r'^K-[0-9]{3,}$')
}
ALLOWED = {
    'mode': {'create', 'improve', 'audit', 'refresh'},
    'identity_kind': {'none', 'sha256', 'manifest', 'vcs', 'version', 'declared'},
    'authority': {'primary', 'official', 'academic', 'secondary', 'community', 'user-provided'},
    'evidence_state': {'snapshotted', 'pinned', 'live', 'user-provided'},
    'confidence': {'high', 'medium', 'low'},
    'relevance': {'required', 'useful', 'contextual'},
    'disposition': {'implement', 'already-covered', 'rejected', 'not-applicable', 'uncertain', 'conflict'},
    'priority': {'must', 'should', 'may'},
    'change_kind': {'existing', 'add', 'modify', 'remove'},
    'change_status': {'planned', 'applied', 'reverted'},
    'evaluation_kind': {'deterministic', 'scenario', 'review', 'runtime', 'perceptual'},
    'evaluation_status': {'planned', 'pass', 'fail', 'not-run'},
    'conflict_status': {'unresolved', 'resolved'}
}


def pct(numerator: int, denominator: int) -> float:
    return 100.0 if denominator == 0 else round(100.0 * numerator / denominator, 2)


def main() -> int:
    parser = argparse.ArgumentParser(description='Validate research-to-skill traceability and compute coverage.')
    parser.add_argument('workspace')
    parser.add_argument('--phase', choices=['draft', 'audit', 'final'], default='draft')
    parser.add_argument('--json-output')
    args = parser.parse_args()

    workspace_path = Path(args.workspace).resolve()
    diagnostics: list[dict[str, Any]] = []

    def add(code: str, severity: str, subject: str, evidence: Any, supported_fixes: list[str] | None = None) -> None:
        diagnostics.append({
            'code': code,
            'severity': severity,
            'subject': subject,
            'evidence': evidence,
            'supported_fixes': supported_fixes or []
        })

    try:
        data = json.loads(workspace_path.read_text(encoding='utf-8'))
    except Exception as exc:
        report = {
            'status': 'fail',
            'phase': args.phase,
            'workspace': str(workspace_path),
            'diagnostics': [{
                'code': 'workspace/json-invalid',
                'severity': 'error',
                'subject': str(workspace_path),
                'evidence': str(exc),
                'supported_fixes': ['Repair the JSON syntax without changing semantic evidence.']
            }]
        }
        if args.json_output:
            atomic_write_json(Path(args.json_output), report)
        print(json.dumps(report, indent=2))
        return 1

    if not isinstance(data, dict):
        add('workspace/root-type', 'error', 'workspace', type(data).__name__, ['Use one JSON object as the workspace root.'])
        data = {}

    required_top = ['schema_version', 'mode', 'scope', 'identities', 'sources', 'findings', 'requirements', 'changes', 'evaluations', 'conflicts']
    for key in required_top:
        if key not in data:
            add('workspace/missing-field', 'error', key, 'missing', [f'Add the required top-level field {key}.'])

    if data.get('schema_version') != '1.0':
        add('workspace/schema-version', 'error', 'schema_version', data.get('schema_version'), ['Use schema_version 1.0 or run an explicit migration.'])
    if data.get('mode') not in ALLOWED['mode']:
        add('workspace/mode', 'error', 'mode', data.get('mode'), ['Use create, improve, audit, or refresh.'])

    scope = data.get('scope') if isinstance(data.get('scope'), dict) else {}
    for key in ['research_question', 'target', 'completeness_boundary']:
        if not isinstance(scope.get(key), str) or not scope.get(key, '').strip():
            add('scope/field', 'error', f'scope.{key}', scope.get(key), [f'Provide a non-empty scope.{key}.'])
    if scope.get('completeness_boundary') != 'corpus-bounded':
        add('scope/completeness-boundary', 'error', 'scope.completeness_boundary', scope.get('completeness_boundary'), ['Set completeness_boundary to corpus-bounded.'])

    identities = data.get('identities') if isinstance(data.get('identities'), dict) else {}
    for key in ['research', 'target_baseline', 'evaluators']:
        item = identities.get(key)
        if not isinstance(item, dict):
            add('identity/missing', 'error', f'identities.{key}', item, [f'Add identities.{key} with kind and value.'])
            continue
        if item.get('kind') not in ALLOWED['identity_kind']:
            add('identity/kind', 'error', f'identities.{key}.kind', item.get('kind'), ['Use a supported identity kind.'])
        if not isinstance(item.get('value'), str):
            add('identity/value', 'error', f'identities.{key}.value', item.get('value'), ['Use a string value; use an empty string only with kind=none.'])
        if item.get('kind') != 'none' and not str(item.get('value', '')).strip():
            add('identity/empty-value', 'warning', f'identities.{key}', item, ['Capture the exact manifest, revision, version, or hash when available.'])

    collections: dict[str, list[dict[str, Any]]] = {}
    indexes: dict[str, dict[str, dict[str, Any]]] = {}
    global_ids: set[str] = set()
    for name in ['sources', 'findings', 'requirements', 'changes', 'evaluations', 'conflicts']:
        raw = data.get(name)
        if not isinstance(raw, list):
            add('collection/type', 'error', name, type(raw).__name__, [f'Use a JSON array for {name}.'])
            raw = []
        rows: list[dict[str, Any]] = []
        idx: dict[str, dict[str, Any]] = {}
        for pos, row in enumerate(raw):
            if not isinstance(row, dict):
                add('record/type', 'error', f'{name}[{pos}]', type(row).__name__, ['Use a JSON object for each record.'])
                continue
            rid = row.get('id')
            if not isinstance(rid, str) or not ID_PATTERNS[name].match(rid):
                add('record/id-format', 'error', f'{name}[{pos}].id', rid, [f'Use the canonical {ID_PATTERNS[name].pattern} ID format.'])
                continue
            if rid in idx or rid in global_ids:
                add('record/id-duplicate', 'error', rid, 'duplicate', ['Allocate a new stable ID; never renumber existing records.'])
                continue
            idx[rid] = row
            global_ids.add(rid)
            rows.append(row)
        collections[name] = rows
        indexes[name] = idx

    def require_text(row: dict[str, Any], rid: str, field: str) -> None:
        value = row.get(field)
        if not isinstance(value, str) or not value.strip():
            add('record/text-required', 'error', f'{rid}.{field}', value, [f'Provide a non-empty {field}.'])

    def require_list(row: dict[str, Any], rid: str, field: str, *, nonempty: bool = False) -> list[str]:
        value = row.get(field)
        if not isinstance(value, list) or any(not isinstance(v, str) or not v for v in value):
            add('record/list-required', 'error', f'{rid}.{field}', value, [f'Use an array of non-empty IDs for {field}.'])
            return []
        if len(value) != len(set(value)):
            add('record/list-duplicate', 'error', f'{rid}.{field}', value, ['Remove duplicate IDs without changing order.'])
        if nonempty and not value:
            add('record/list-empty', 'error', f'{rid}.{field}', value, [f'Add at least one ID to {field}.'])
        return value

    for rid, row in indexes['sources'].items():
        require_text(row, rid, 'title')
        require_text(row, rid, 'locator')
        if row.get('authority') not in ALLOWED['authority']:
            add('source/authority', 'error', f'{rid}.authority', row.get('authority'), ['Use a supported authority value.'])
        if row.get('evidence_state') not in ALLOWED['evidence_state']:
            add('source/evidence-state', 'error', f'{rid}.evidence_state', row.get('evidence_state'), ['Use snapshotted, pinned, live, or user-provided.'])
        if not isinstance(row.get('identity'), str):
            add('source/identity-type', 'error', f'{rid}.identity', row.get('identity'), ['Use a string identity.'])
        if row.get('evidence_state') in {'snapshotted', 'pinned'} and not str(row.get('identity', '')).strip():
            add('source/identity-missing', 'error', rid, row.get('evidence_state'), ['Record the immutable hash, manifest, version, or revision.'])
        if row.get('evidence_state') == 'live':
            add('source/live-evidence', 'warning', rid, row.get('locator'), ['Prefer a frozen research artifact or stable source identity when the claim is material.'])

    for rid, row in indexes['findings'].items():
        require_text(row, rid, 'statement')
        sources = require_list(row, rid, 'source_ids', nonempty=True)
        for ref in sources:
            if ref not in indexes['sources']:
                add('trace/missing-source', 'error', f'{rid}.source_ids', ref, ['Add the source record or correct the reference.'])
        if row.get('confidence') not in ALLOWED['confidence']:
            add('finding/confidence', 'error', f'{rid}.confidence', row.get('confidence'), ['Use high, medium, or low.'])
        if row.get('relevance') not in ALLOWED['relevance']:
            add('finding/relevance', 'error', f'{rid}.relevance', row.get('relevance'), ['Use required, useful, or contextual.'])
        disposition = row.get('disposition')
        if disposition not in ALLOWED['disposition']:
            add('finding/disposition', 'error', f'{rid}.disposition', disposition, ['Account for the finding with one supported disposition.'])
        require_text(row, rid, 'rationale')
        reqs = require_list(row, rid, 'requirement_ids')
        conflicts = require_list(row, rid, 'conflict_ids')
        for ref in reqs:
            if ref not in indexes['requirements']:
                add('trace/missing-requirement', 'error', f'{rid}.requirement_ids', ref, ['Add the requirement or correct the reference.'])
        for ref in conflicts:
            if ref not in indexes['conflicts']:
                add('trace/missing-conflict', 'error', f'{rid}.conflict_ids', ref, ['Add the conflict record or correct the reference.'])
        if disposition in {'implement', 'already-covered'} and not reqs:
            add('finding/accepted-without-requirement', 'error', rid, disposition, ['Derive at least one requirement from every accepted finding.'])
        if disposition == 'conflict' and not conflicts:
            add('finding/conflict-without-record', 'error', rid, disposition, ['Link the finding to an explicit conflict record.'])

    for rid, row in indexes['requirements'].items():
        require_text(row, rid, 'statement')
        if row.get('priority') not in ALLOWED['priority']:
            add('requirement/priority', 'error', f'{rid}.priority', row.get('priority'), ['Use must, should, or may.'])
        derived = require_list(row, rid, 'derived_from', nonempty=True)
        changes = require_list(row, rid, 'change_ids')
        evaluations = require_list(row, rid, 'evaluation_ids')
        for ref in derived:
            if ref not in indexes['findings']:
                add('trace/missing-finding', 'error', f'{rid}.derived_from', ref, ['Add the finding or correct the reference.'])
        for ref in changes:
            if ref not in indexes['changes']:
                add('trace/missing-change', 'error', f'{rid}.change_ids', ref, ['Add the change or correct the reference.'])
        for ref in evaluations:
            if ref not in indexes['evaluations']:
                add('trace/missing-evaluation', 'error', f'{rid}.evaluation_ids', ref, ['Add the evaluation or correct the reference.'])
        if args.phase in {'final', 'audit'} and not changes:
            severity = 'warning' if args.phase == 'audit' else 'error'
            add('requirement/no-implementation', severity, rid, 'no change_ids', ['Map existing behavior or define the required change.'])
        if args.phase in {'final', 'audit'} and not evaluations:
            severity = 'warning' if args.phase == 'audit' else 'error'
            add('requirement/no-evaluation', severity, rid, 'no evaluation_ids', ['Define verification for the requirement.'])

    for rid, row in indexes['changes'].items():
        if row.get('kind') not in ALLOWED['change_kind']:
            add('change/kind', 'error', f'{rid}.kind', row.get('kind'), ['Use existing, add, modify, or remove.'])
        require_text(row, rid, 'target')
        require_text(row, rid, 'summary')
        if row.get('status') not in ALLOWED['change_status']:
            add('change/status', 'error', f'{rid}.status', row.get('status'), ['Use planned, applied, or reverted.'])
        satisfies = require_list(row, rid, 'satisfies', nonempty=True)
        for ref in satisfies:
            if ref not in indexes['requirements']:
                add('trace/missing-requirement', 'error', f'{rid}.satisfies', ref, ['Add the requirement or correct the reference.'])
        if args.phase == 'final' and row.get('status') == 'planned':
            add('change/planned-at-final', 'error', rid, row.get('target'), ['Apply, remove, or explicitly revert the planned change before finalization.'])

    for rid, row in indexes['evaluations'].items():
        if row.get('kind') not in ALLOWED['evaluation_kind']:
            add('evaluation/kind', 'error', f'{rid}.kind', row.get('kind'), ['Use a supported evaluation kind.'])
        require_text(row, rid, 'description')
        verifies = require_list(row, rid, 'verifies', nonempty=True)
        for ref in verifies:
            if ref not in indexes['requirements']:
                add('trace/missing-requirement', 'error', f'{rid}.verifies', ref, ['Add the requirement or correct the reference.'])
        status = row.get('status')
        if status not in ALLOWED['evaluation_status']:
            add('evaluation/status', 'error', f'{rid}.status', status, ['Use planned, pass, fail, or not-run.'])
        if not isinstance(row.get('frozen'), bool):
            add('evaluation/frozen-type', 'error', f'{rid}.frozen', row.get('frozen'), ['Use a boolean frozen flag.'])
        if status in {'pass', 'fail'} and not str(row.get('evidence', '')).strip():
            add('evaluation/evidence-missing', 'error', rid, status, ['Record the command, report, reviewer decision, or artifact that supports the result.'])
        if status == 'not-run' and not str(row.get('limitation', '')).strip():
            add('evaluation/not-run-without-limitation', 'error', rid, status, ['Explain the unavailable capability or blocker.'])
        if args.phase == 'final':
            if status == 'planned':
                add('evaluation/planned-at-final', 'error', rid, row.get('description'), ['Run the evaluation or record not-run with a concrete limitation.'])
            elif status == 'fail':
                add('evaluation/failed', 'error', rid, row.get('evidence'), ['Repair the candidate; do not weaken the evaluator.'])
            elif status == 'not-run':
                add('evaluation/not-run', 'warning', rid, row.get('limitation'), ['Do not claim the missing evidence layer.'])
            if row.get('frozen') is not True:
                add('evaluation/not-frozen', 'error', rid, row.get('frozen'), ['Freeze evaluator assets before final acceptance.'])

    for rid, row in indexes['conflicts'].items():
        findings = require_list(row, rid, 'finding_ids', nonempty=True)
        if len(findings) < 2:
            add('conflict/too-few-findings', 'error', rid, findings, ['Link at least two conflicting findings.'])
        for ref in findings:
            if ref not in indexes['findings']:
                add('trace/missing-finding', 'error', f'{rid}.finding_ids', ref, ['Add the finding or correct the reference.'])
        if row.get('status') not in ALLOWED['conflict_status']:
            add('conflict/status', 'error', f'{rid}.status', row.get('status'), ['Use unresolved or resolved.'])
        require_text(row, rid, 'rationale')
        if row.get('status') == 'resolved' and not str(row.get('resolution', '')).strip():
            add('conflict/resolution-missing', 'error', rid, row.get('status'), ['Record how the conflict was resolved.'])
        if row.get('status') == 'unresolved':
            severity = 'warning' if args.phase == 'audit' else ('error' if args.phase == 'final' else 'warning')
            add('conflict/unresolved', severity, rid, findings, ['Resolve the material conflict or keep the run non-final.'])

    # Bidirectional relation symmetry.
    for fid, finding in indexes['findings'].items():
        for rid in finding.get('requirement_ids', []) if isinstance(finding.get('requirement_ids'), list) else []:
            req = indexes['requirements'].get(rid)
            if req is not None and fid not in req.get('derived_from', []):
                add('trace/asymmetric-finding-requirement', 'error', f'{fid}<->{rid}', 'forward only', ['Add the missing reverse derived_from link or remove the invalid forward link.'])
        for kid in finding.get('conflict_ids', []) if isinstance(finding.get('conflict_ids'), list) else []:
            conflict = indexes['conflicts'].get(kid)
            if conflict is not None and fid not in conflict.get('finding_ids', []):
                add('trace/asymmetric-finding-conflict', 'error', f'{fid}<->{kid}', 'forward only', ['Make conflict membership symmetric.'])

    for rid, req in indexes['requirements'].items():
        for fid in req.get('derived_from', []) if isinstance(req.get('derived_from'), list) else []:
            finding = indexes['findings'].get(fid)
            if finding is not None and rid not in finding.get('requirement_ids', []):
                add('trace/asymmetric-finding-requirement', 'error', f'{fid}<->{rid}', 'reverse only', ['Add the missing forward requirement_ids link or remove the invalid derivation.'])
        for cid in req.get('change_ids', []) if isinstance(req.get('change_ids'), list) else []:
            change = indexes['changes'].get(cid)
            if change is not None and rid not in change.get('satisfies', []):
                add('trace/asymmetric-requirement-change', 'error', f'{rid}<->{cid}', 'requirement only', ['Make requirement/change links symmetric.'])
        for eid in req.get('evaluation_ids', []) if isinstance(req.get('evaluation_ids'), list) else []:
            evaluation = indexes['evaluations'].get(eid)
            if evaluation is not None and rid not in evaluation.get('verifies', []):
                add('trace/asymmetric-requirement-evaluation', 'error', f'{rid}<->{eid}', 'requirement only', ['Make requirement/evaluation links symmetric.'])

    for cid, change in indexes['changes'].items():
        for rid in change.get('satisfies', []) if isinstance(change.get('satisfies'), list) else []:
            req = indexes['requirements'].get(rid)
            if req is not None and cid not in req.get('change_ids', []):
                add('trace/asymmetric-requirement-change', 'error', f'{rid}<->{cid}', 'change only', ['Make requirement/change links symmetric.'])

    for eid, evaluation in indexes['evaluations'].items():
        for rid in evaluation.get('verifies', []) if isinstance(evaluation.get('verifies'), list) else []:
            req = indexes['requirements'].get(rid)
            if req is not None and eid not in req.get('evaluation_ids', []):
                add('trace/asymmetric-requirement-evaluation', 'error', f'{rid}<->{eid}', 'evaluation only', ['Make requirement/evaluation links symmetric.'])

    for kid, conflict in indexes['conflicts'].items():
        for fid in conflict.get('finding_ids', []) if isinstance(conflict.get('finding_ids'), list) else []:
            finding = indexes['findings'].get(fid)
            if finding is not None and kid not in finding.get('conflict_ids', []):
                add('trace/asymmetric-finding-conflict', 'error', f'{fid}<->{kid}', 'conflict only', ['Make finding/conflict links symmetric.'])

    # Final semantic-structure coverage checks.
    accepted_findings = [f for f in indexes['findings'].values() if f.get('disposition') in {'implement', 'already-covered'}]
    accepted_with_req = [f for f in accepted_findings if f.get('requirement_ids')]

    implemented_requirements = 0
    verified_requirements = 0
    for rid, req in indexes['requirements'].items():
        changes = [indexes['changes'].get(cid) for cid in req.get('change_ids', []) if cid in indexes['changes']]
        evals = [indexes['evaluations'].get(eid) for eid in req.get('evaluation_ids', []) if eid in indexes['evaluations']]
        if any(c and c.get('status') == 'applied' for c in changes):
            implemented_requirements += 1
        if evals:
            verified_requirements += 1
        if args.phase == 'final':
            if not any(c and c.get('status') == 'applied' for c in changes):
                add('coverage/requirement-not-implemented', 'error', rid, req.get('change_ids', []), ['Apply or map at least one satisfying change.'])
            if not evals:
                add('coverage/requirement-not-verified', 'error', rid, [], ['Add at least one evaluation.'])

    for fid, finding in indexes['findings'].items():
        disposition = finding.get('disposition')
        if args.phase == 'final' and disposition == 'implement':
            reqs = [indexes['requirements'].get(rid) for rid in finding.get('requirement_ids', []) if rid in indexes['requirements']]
            changes = []
            for req in reqs:
                if req:
                    changes.extend(indexes['changes'].get(cid) for cid in req.get('change_ids', []) if cid in indexes['changes'])
            if not any(c and c.get('kind') in {'add', 'modify', 'remove'} and c.get('status') == 'applied' for c in changes):
                add('coverage/implement-finding-not-applied', 'error', fid, finding.get('requirement_ids', []), ['Apply a traced add/modify/remove change or revise the disposition with evidence.'])
        if args.phase == 'final' and disposition == 'already-covered':
            reqs = [indexes['requirements'].get(rid) for rid in finding.get('requirement_ids', []) if rid in indexes['requirements']]
            changes = []
            for req in reqs:
                if req:
                    changes.extend(indexes['changes'].get(cid) for cid in req.get('change_ids', []) if cid in indexes['changes'])
            if not any(c and c.get('kind') == 'existing' and c.get('status') == 'applied' for c in changes):
                add('coverage/already-covered-without-existing-map', 'error', fid, finding.get('requirement_ids', []), ['Map the existing implementation with an applied existing change record.'])

    substantive_changes = [c for c in indexes['changes'].values() if c.get('status') in {'applied', 'planned'}]
    justified_changes = [c for c in substantive_changes if c.get('satisfies')]
    disposition_counts = Counter(str(f.get('disposition')) for f in indexes['findings'].values() if f.get('disposition'))
    unresolved = sum(1 for c in indexes['conflicts'].values() if c.get('status') == 'unresolved')
    not_run = sum(1 for e in indexes['evaluations'].values() if e.get('status') == 'not-run')

    metrics = {
        'source_count': len(indexes['sources']),
        'finding_count': len(indexes['findings']),
        'requirement_count': len(indexes['requirements']),
        'change_count': len(indexes['changes']),
        'evaluation_count': len(indexes['evaluations']),
        'conflict_count': len(indexes['conflicts']),
        'finding_dispositions': dict(sorted(disposition_counts.items())),
        'finding_accounting_percent': pct(sum(disposition_counts.values()), len(indexes['findings'])),
        'accepted_finding_requirement_coverage_percent': pct(len(accepted_with_req), len(accepted_findings)),
        'requirement_implementation_coverage_percent': pct(implemented_requirements, len(indexes['requirements'])),
        'requirement_verification_coverage_percent': pct(verified_requirements, len(indexes['requirements'])),
        'reverse_justification_percent': pct(len(justified_changes), len(substantive_changes)),
        'unresolved_conflicts': unresolved,
        'not_run_evaluations': not_run
    }

    errors = [d for d in diagnostics if d['severity'] == 'error']
    warnings = [d for d in diagnostics if d['severity'] == 'warning']
    status = 'fail' if errors else ('warn' if warnings else 'pass')
    report = {
        'status': status,
        'phase': args.phase,
        'workspace': str(workspace_path),
        'workspace_sha256': sha256_file(workspace_path),
        'metrics': metrics,
        'diagnostics': diagnostics,
        'limitations': [
            'This validator proves structural trace integrity and coverage, not semantic truth of the links.',
            'A 100% matrix is bounded to the recorded corpus and extracted findings, not all knowledge about the subject.'
        ]
    }
    if args.json_output:
        atomic_write_json(Path(args.json_output), report)
    print(json.dumps(report, indent=2))
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
