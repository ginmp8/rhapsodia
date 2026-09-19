#!/usr/bin/env python3
"""Audit an Agent Skills package for structural and contract consistency."""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from inventory_skill import read_text, scan_target  # noqa: E402

REPORT_VERSION = 2
CATEGORIES = {
    'package_structure', 'activation_scope', 'ownership_role', 'resource_integration',
    'workflow_modes', 'validation_packaging', 'evidence_contract', 'authority_conflict',
}
RESOURCE_STATUSES = {
    'current', 'duplicate', 'obsolete', 'migration-only', 'contradictory',
    'orphaned', 'integrable', 'blocked', 'unknown',
}
STOP_WORDS = {
    'the', 'and', 'for', 'with', 'when', 'use', 'skill', 'target', 'user', 'this', 'that', 'from',
    'work', 'workflow', 'mode', 'modes', 'file', 'files', 'output', 'outputs', 'artifact', 'artifacts',
}


def finding(fid: str, severity: str, category: str, title: str, evidence: str, problem: str, repair: str,
            gate: str, confidence: str = 'medium', subjects: list[str] | None = None,
            evidence_label: str = 'inspected') -> dict[str, Any]:
    return {
        'id': fid,
        'severity': severity,
        'category': category,
        'title': title,
        'subjects': subjects or [],
        'evidence': evidence,
        'evidence_label': evidence_label,
        'problem': problem,
        'repair': repair,
        'gate': gate,
        'confidence': confidence,
    }


def words(text: str) -> set[str]:
    return {w.lower() for w in re.findall(r'[a-zA-Z][a-zA-Z0-9_-]{2,}', text) if w.lower() not in STOP_WORDS}


def load_skill_text(target: Path) -> str:
    path = target / 'SKILL.md'
    return read_text(path) if path.exists() else ''


def existing_rel_paths(target: Path) -> set[str]:
    return {p.relative_to(target).as_posix() for p in target.rglob('*') if p.is_file()}


def check_broken_links(target: Path, inv: dict[str, Any], findings: list[dict[str, Any]]) -> None:
    paths = existing_rel_paths(target)
    n = 1
    for link in inv.get('links', []):
        source = link['source']
        raw = link['target'].strip()
        if not raw or raw.startswith('#') or '://' in raw:
            continue
        source_dir = Path(source).parent
        resolved = (source_dir / raw).as_posix() if source_dir.as_posix() != '.' else raw
        resolved = Path(resolved).as_posix()
        if resolved not in paths and raw not in paths:
            findings.append(finding(
                f'L{n:03}', 'blocker', 'package_structure', 'broken local markdown link',
                f'{source} -> {raw}',
                'A local markdown link points to a resource that does not exist in the target package.',
                'Repair the link only when the intended resource is evidenced; otherwise keep the inconsistency explicit.',
                'Re-run the same audit and verify broken local link count is zero.',
                'high', [source, raw],
            ))
            n += 1


def check_frontmatter(inv: dict[str, Any], findings: list[dict[str, Any]]) -> None:
    fm = inv.get('frontmatter', {})
    if inv.get('skill_file_count') != 1:
        findings.append(finding(
            'S001', 'blocker', 'package_structure', 'target must contain exactly one SKILL.md',
            f"skill_files={inv.get('skill_files')}",
            'The target does not resolve to one unambiguous skill root.',
            'Select or restructure the target so exactly one root SKILL.md is present.',
            'scripts/inventory_skill.py reports skill_file_count == 1.',
            'high', inv.get('skill_files', []),
        ))
    for idx, err in enumerate(fm.get('errors', []), start=1):
        findings.append(finding(
            f'F{idx:03}', 'blocker', 'package_structure', 'invalid SKILL.md frontmatter',
            'SKILL.md frontmatter', err,
            'Keep portable name/description fields valid; preserve intentional host-specific extensions as adapters.',
            'Re-run audit and confirm frontmatter errors are zero.',
            'high', ['SKILL.md'],
        ))


def check_description(skill_text: str, inv: dict[str, Any], findings: list[dict[str, Any]]) -> None:
    desc = inv.get('frontmatter', {}).get('fields', {}).get('description', '')
    if not desc:
        return
    if len(desc.split()) < 25:
        findings.append(finding(
            'A001', 'high', 'activation_scope', 'activation description is too thin',
            'SKILL.md frontmatter description',
            'The description may not provide enough trigger and boundary signal for reliable activation.',
            'State positive triggers, negative boundaries, owned outputs, and adjacent-skill exclusions concisely.',
            'Reviewer confirms the description and body define the same activation boundary.',
            'medium', ['SKILL.md'],
        ))
    negative_markers = ['do not use', 'do not activate', 'not use', 'avoid', 'unless']
    if not any(marker in desc.lower() for marker in negative_markers):
        findings.append(finding(
            'A002', 'medium', 'activation_scope', 'activation description lacks negative boundary',
            'SKILL.md frontmatter description',
            'The description says when to activate but not when an adjacent workflow owns the request.',
            'Add concise non-activation boundaries.',
            'Description contains explicit non-use cases.',
            'medium', ['SKILL.md'],
        ))
    desc_words = words(desc)
    body_words = words(skill_text[:7000])
    if desc_words and body_words and len(desc_words & body_words) / max(len(desc_words), 1) < 0.30:
        findings.append(finding(
            'A003', 'medium', 'activation_scope', 'frontmatter vocabulary drifts from body',
            'SKILL.md description versus body',
            'Activation vocabulary is weakly represented in the control plane.',
            'Align description and body around the same role, outputs, and boundaries.',
            'Re-run audit and inspect overlap plus semantic review.',
            'low', ['SKILL.md'],
        ))


def check_required_sections(skill_text: str, findings: list[dict[str, Any]]) -> None:
    required = ['scope', 'required input', 'mode', 'workflow', 'stop condition', 'output contract']
    lower = skill_text.lower()
    missing = [section for section in required if section not in lower]
    if missing:
        findings.append(finding(
            'W001', 'high', 'workflow_modes', 'missing mature control-plane sections',
            'SKILL.md body',
            f'Missing or weak section signals: {missing}.',
            'Add compact sections for scope, required inputs, routing, workflow, stop conditions, and outputs.',
            'Audit no longer reports missing mature control-plane sections.',
            'medium', ['SKILL.md'],
        ))


def check_role_contradictions(skill_text: str, findings: list[dict[str, Any]]) -> None:
    lower = skill_text.lower()
    pairs = [
        ('implement', ['do not implement', 'must not implement', 'not implement']),
        ('planning', ['do not plan', 'must not plan', 'not planning']),
        ('governance', ['do not govern', 'must not govern', 'not governance']),
        ('benchmark', ['do not benchmark', 'must not benchmark', 'not benchmark']),
        ('package', ['do not package', 'must not package', 'not package']),
    ]
    idx = 1
    for term, negations in pairs:
        positive = re.search(rf'\b(owns|own|use for|responsible for|may|can)\b[^\n]{{0,100}}\b{term}\w*', lower)
        negative = any(neg in lower for neg in negations)
        if positive and negative:
            findings.append(finding(
                f'O{idx:03}', 'high', 'ownership_role', f'possible contradictory ownership for {term}',
                'SKILL.md body',
                f'The control plane appears to both allow/own and prohibit {term}-related behavior.',
                'Resolve authority by concern and mode; do not erase the contradiction without evidence.',
                'Semantic review confirms the positive and negative rules no longer conflict.',
                'medium', ['SKILL.md'],
            ))
            idx += 1


def duplicate_groups(inv: dict[str, Any]) -> dict[str, list[str]]:
    by_hash: dict[str, list[str]] = {}
    for item in inv.get('files', []):
        by_hash.setdefault(item.get('sha256', ''), []).append(item['path'])
    return {h: sorted(paths) for h, paths in by_hash.items() if h and len(paths) > 1}


def classify_resources(inv: dict[str, Any]) -> list[dict[str, Any]]:
    duplicates = duplicate_groups(inv)
    duplicate_lookup: dict[str, list[str]] = {}
    for paths in duplicates.values():
        for path in paths:
            duplicate_lookup[path] = [p for p in paths if p != path]

    rows: list[dict[str, Any]] = []
    for item in inv.get('files', []):
        path = item['path']
        role = item.get('role', 'other')
        trace = inv.get('resource_trace', {}).get(path, {})
        refs = set(trace.get('references', []))
        migrations = set(trace.get('migration_paths', []))
        evidence: list[str] = []
        semantic_review = False
        status = 'unknown'
        confidence = 'medium'

        if path == 'SKILL.md':
            status, confidence = 'current', 'high'
            evidence.append('root control plane')
        elif path in duplicate_lookup:
            status, confidence = 'duplicate', 'high'
            evidence.append('byte-identical to: ' + ', '.join(duplicate_lookup[path]))
            semantic_review = True
        elif refs and refs.issubset(migrations) and migrations and any(token in path.lower() for token in ('migration', 'legacy', 'compat')):
            status, confidence = 'migration-only', 'medium'
            evidence.append('resource identity signals migration/legacy scope and all detected inbound references originate from migration/legacy-signaled sources')
            semantic_review = True
        elif refs or trace.get('imports') or trace.get('links') or trace.get('consumers') or trace.get('validators') or trace.get('tests') or trace.get('examples'):
            status, confidence = 'current', 'high'
            evidence.append('detected inbound consumer/reference evidence')
        elif role in {'reference', 'script', 'template', 'example', 'evaluator', 'test'}:
            status, confidence = 'orphaned', 'medium'
            evidence.append('no detected inbound graph edge')
            semantic_review = True
        else:
            status, confidence = 'unknown', 'low'
            evidence.append('insufficient machine-readable evidence to prove current, obsolete, or safe-to-remove status')
            semantic_review = True

        rows.append({
            'path': path,
            'role': role,
            'provisional_status': status,
            'confidence': confidence,
            'evidence': evidence,
            'trace': trace,
            'semantic_review_required': semantic_review,
            'deletion_allowed': False,
            'allowed_statuses': sorted(RESOURCE_STATUSES),
        })
    return rows


def check_resource_integration(classifications: list[dict[str, Any]], inv: dict[str, Any], findings: list[dict[str, Any]]) -> None:
    idx = 1
    for row in classifications:
        status, path, role = row['provisional_status'], row['path'], row['role']
        if status == 'orphaned':
            severity = 'medium' if role in {'reference', 'script', 'template', 'evaluator'} else 'low'
            findings.append(finding(
                f'R{idx:03}', severity, 'resource_integration', 'resource has no detected inbound graph edge',
                path,
                'The resource is graph-orphaned, but that does not prove it is obsolete or safe to delete.',
                'Trace consumers, tests, validators, examples, packaging, migration paths, and handoffs; then classify semantically as current, integrable, obsolete, migration-only, blocked, or unknown.',
                'Resource classification contains evidence for the final status; deletion remains blocked unless the removal gate is satisfied.',
                'medium', [path],
            ))
            idx += 1
        elif status == 'duplicate':
            findings.append(finding(
                f'R{idx:03}', 'medium', 'resource_integration', 'byte-identical resource duplication detected',
                path,
                'Identical bytes exist at multiple paths, but consumers may depend on each path independently.',
                'Trace every consumer and authority owner before consolidation; do not delete based only on hash equality.',
                'All consumers are migrated or duplication is explicitly documented.',
                'high', [path],
            ))
            idx += 1
    for hit in inv.get('scaffold_hits', []):
        findings.append(finding(
            f'G{idx:03}', 'medium', 'resource_integration', 'unfinished scaffold marker remains',
            f"{hit['path']} contains {hit['term']}",
            'The package contains an unfinished marker outside an operational template.',
            'Replace it with target-specific content or remove the resource only after the full deletion trace is satisfied.',
            'Audit scaffold-marker count is zero outside intentional templates.',
            'medium', [hit['path']],
        ))
        idx += 1


def check_scripts(target: Path, inv: dict[str, Any], findings: list[dict[str, Any]]) -> None:
    idx = 1
    for item in inv.get('files', []):
        path = item['path']
        if item.get('role') != 'script' or not path.endswith('.py'):
            continue
        text = read_text(target / path)
        if 'argparse' not in text and 'if __name__' not in text:
            findings.append(finding(
                f'C{idx:03}', 'medium', 'validation_packaging', 'script lacks declared CLI/import-only contract',
                path,
                'Repeatable use is unclear because the script exposes neither a CLI nor an explicit import-only role.',
                'Add a CLI contract or document its importer/consumer.',
                'Script has a documented CLI or traced import-only consumer.',
                'medium', [path],
            ))
            idx += 1


def check_scenarios(target: Path, inv: dict[str, Any], findings: list[dict[str, Any]]) -> None:
    scenario_files = [item['path'] for item in inv.get('files', []) if item.get('role') in {'example', 'evaluator'} and item['path'].endswith('.json')]
    for idx, rel in enumerate(scenario_files, start=1):
        try:
            data = json.loads(read_text(target / rel))
        except Exception as exc:
            findings.append(finding(f'E{idx:03}', 'high', 'evidence_contract', 'scenario json is invalid', rel, str(exc), 'Fix JSON syntax/schema.', 'JSON parser succeeds.', 'high', [rel]))
            continue
        if isinstance(data, dict) and isinstance(data.get('scenarios'), list):
            scenarios = data['scenarios']
        elif isinstance(data, list):
            scenarios = data
        else:
            findings.append(finding(f'E{idx:03}', 'medium', 'evidence_contract', 'scenario file has unsupported shape', rel, 'Expected a JSON array or an object containing a scenarios array.', 'Convert to a supported scenario shape.', 'Scenario audit passes.', 'medium', [rel]))
            continue
        categories = {str(item.get('category')) for item in scenarios if isinstance(item, dict)}
        needed = {'should_activate', 'should_not_activate', 'ambiguous', 'edge_case'}
        missing = sorted(needed - categories)
        if missing:
            findings.append(finding(
                f'E{idx:03}', 'medium', 'evidence_contract', 'scenario suite lacks minimum categories', rel,
                f'Missing categories: {missing}.',
                'Add planned scenarios for each minimum category; keep measurement separate from design.',
                'Audit confirms all minimum scenario categories exist.',
                'medium', [rel],
            ))
        ids: set[str] = set()
        for item in scenarios:
            if not isinstance(item, dict):
                continue
            sid = str(item.get('id', ''))
            if not sid or sid in ids:
                findings.append(finding(
                    f'E{idx:03}I', 'medium', 'evidence_contract', 'scenario ids must be unique and non-empty', rel,
                    f'Duplicate or missing id: {sid!r}.', 'Assign stable unique scenario ids.', 'Scenario audit reports no duplicate ids.', 'high', [rel],
                ))
                break
            ids.add(sid)
            if any(item.get(key) is not None for key in ('actual_activation', 'output_conforms', 'quality_score', 'needs_rework')):
                findings.append(finding(
                    f'E{idx:03}M', 'medium', 'evidence_contract', 'scenario contains measured fields without bound evidence', rel,
                    'Measured fields are populated in a scenario-design resource.',
                    'Keep measured values in executed result evidence, or bind them to an immutable result identity.',
                    'Reviewer confirms planned and measured evidence are separated.',
                    'low', [rel],
                ))
                break


def score(findings: list[dict[str, Any]]) -> dict[str, Any]:
    weights = {'blocker': 30, 'high': 12, 'medium': 5, 'low': 1}
    penalty = sum(weights.get(f['severity'], 1) for f in findings)
    value = max(0, 100 - penalty)
    counts = {sev: sum(1 for f in findings if f['severity'] == sev) for sev in ('blocker', 'high', 'medium', 'low')}
    status = 'pass' if counts['blocker'] == 0 and counts['high'] == 0 else 'fail'
    return {'score': value, 'max_score': 100, 'direction': 'higher-is-better', 'status': status, 'counts': counts, 'meaning': 'static consistency signal only; not package/readiness proof'}


def render_markdown(result: dict[str, Any]) -> str:
    lines = [
        '# Skill Consistency Audit', '',
        f"- Report version: `{result['report_version']}`",
        f"- Target: `{result['target_path']}`",
        f"- Inventory identity: `{result['inventory_identity']}`",
        f"- Static score: {result['score']['score']} / {result['score']['max_score']}",
        f"- Static status: {result['score']['status']}",
        f"- Readiness: {result['readiness']['status']}",
        f"- Finding counts: {result['score']['counts']}", '',
        '## Inventory Summary', '', '```json', json.dumps(result['inventory_summary'], indent=2, ensure_ascii=False), '```', '',
        '## Resource Classification', '',
    ]
    for row in result['resource_classification']:
        lines.append(f"- `{row['path']}` -> **{row['provisional_status']}** ({row['confidence']}); deletion_allowed={str(row['deletion_allowed']).lower()}")
    lines.extend(['', '## Findings', ''])
    if not result['findings']:
        lines.append('No blocking/high findings were detected by the static audit. External/package and semantic gates still apply.')
    for f in result['findings']:
        lines.extend([
            f"### {f['id']} [{f['severity']}] {f['title']}", '',
            f"- Category: `{f['category']}`",
            f"- Subjects: {', '.join(f['subjects']) if f['subjects'] else '-'}",
            f"- Evidence: {f['evidence']}",
            f"- Evidence label: `{f['evidence_label']}`",
            f"- Problem: {f['problem']}",
            f"- Repair: {f['repair']}",
            f"- Gate: {f['gate']}",
            f"- Confidence: {f['confidence']}", '',
        ])
    return '\n'.join(lines).rstrip() + '\n'


def audit(target: Path) -> dict[str, Any]:
    target = target.resolve()
    inv = scan_target(target)
    skill_text = load_skill_text(target)
    findings: list[dict[str, Any]] = []
    check_frontmatter(inv, findings)
    check_broken_links(target, inv, findings)
    check_description(skill_text, inv, findings)
    check_required_sections(skill_text, findings)
    check_role_contradictions(skill_text, findings)
    classifications = classify_resources(inv)
    check_resource_integration(classifications, inv, findings)
    check_scripts(target, inv, findings)
    check_scenarios(target, inv, findings)
    score_data = score(findings)
    summary = {
        'directories': inv.get('directories', []),
        'counts': inv.get('counts', {}),
        'skill_files': inv.get('skill_files', []),
        'frontmatter_errors': inv.get('frontmatter', {}).get('errors', []),
        'reference_edge_count': len(inv.get('reference_graph', [])),
    }
    unresolved = [row['path'] for row in classifications if row['provisional_status'] in {'orphaned', 'unknown'}]
    return {
        'report_version': REPORT_VERSION,
        'target_path': target.as_posix(),
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'evidence_type': 'structural-static-only',
        'inventory_identity': inv.get('inventory_fingerprint'),
        'inventory_summary': summary,
        'authority_contract': {
            'reference': 'references/authority-and-conflict-resolution.md',
            'rule': 'resolve authority by concern; do not silently discard contradictory evidence',
        },
        'classification_contract': {
            'statuses': sorted(RESOURCE_STATUSES),
            'static_classifier_is_provisional': True,
            'absence_of_reference_never_authorizes_deletion': True,
            'required_deletion_trace_dimensions': ['imports', 'links', 'references', 'consumers', 'tests', 'validators', 'examples', 'packaging', 'migration_paths', 'handoffs'],
        },
        'resource_classification': classifications,
        'findings': findings,
        'score': score_data,
        'readiness': {
            'status': 'not-proven' if score_data['status'] == 'pass' else 'blocked-by-static-findings',
            'reason': 'static audit does not prove evaluator integrity, runtime behavior, package validity, or semantic correctness',
            'unresolved_resource_count': len(unresolved),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Audit a target skill for evidence-grounded internal consistency.')
    parser.add_argument('--target', required=True)
    parser.add_argument('--json-output')
    parser.add_argument('--markdown-output')
    args = parser.parse_args()
    try:
        result = audit(Path(args.target))
    except Exception as exc:
        print(json.dumps({'status': 'fail', 'error': str(exc)}, indent=2))
        return 1
    if args.json_output:
        out = Path(args.json_output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    if args.markdown_output:
        out = Path(args.markdown_output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render_markdown(result), encoding='utf-8')
    if not args.json_output and not args.markdown_output:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result['score']['status'] == 'pass' else 2


if __name__ == '__main__':
    raise SystemExit(main())
