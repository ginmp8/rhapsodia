#!/usr/bin/env python3
"""Validate structure, evidence status, and identity metadata of a benchmark report."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

from _common import dump_json

REQUIRED_SECTIONS = [
    'executive summary',
    'scorecard',
    'gate evaluation',
    'static structure inventory',
    'behavioral metrics',
    'scenario suite',
    'evidence-based findings',
    'top prioritized improvements',
    'risks if used as-is',
    'suggested improved description',
    'suggested ideal file structure',
    'verdict',
    'benchmark metadata',
]
SCAFFOLD_MARKERS = [
    re.compile(r'\[TODO', re.IGNORECASE),
    re.compile(r'\bTODO\s*:', re.IGNORECASE),
    re.compile(r'replace with actual', re.IGNORECASE),
    re.compile(r'this is a placeholder', re.IGNORECASE),
]
VERDICT_RE = re.compile(r'\b(approve|approve with reservations|reject)\b', re.IGNORECASE)
SCORE_RE = re.compile(r'\b(\d{1,3})\s*/\s*100\b')
SHA_RE = re.compile(r'^[0-9a-f]{64}$')


def normalize_heading(line: str) -> str | None:
    match = re.match(r'^#{1,6}\s+(.*)$', line.strip())
    if not match:
        return None
    text = match.group(1).strip().lower()
    text = re.sub(r'^\d+\.\s*', '', text)
    text = re.sub(r'[`*_]+', '', text)
    return text


def find_sections(text: str) -> set[str]:
    return {heading for line in text.splitlines() if (heading := normalize_heading(line))}


def metadata_value(text: str, label: str) -> str | None:
    match = re.search(rf'(?mi)^-\s*{re.escape(label)}:\s*`?([^`\n]+)`?\s*$', text)
    return match.group(1).strip() if match else None


def scan_markers(text: str) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        if any(pattern.search(line) for pattern in SCAFFOLD_MARKERS):
            hits.append({'line': line_no, 'text': line.strip()[:160]})
    return hits


def validate_report(path: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    if not path.exists() or not path.is_file():
        return {'status': 'fail', 'errors': [f'report file not found: {path}'], 'warnings': [], 'checks': {}}

    text = path.read_text(encoding='utf-8', errors='replace')
    lower = text.lower()
    sections = find_sections(text)
    missing_sections = [section for section in REQUIRED_SECTIONS if section not in sections]
    if missing_sections:
        errors.append('missing required sections: ' + ', '.join(missing_sections))

    marker_hits = scan_markers(text)
    if marker_hits:
        errors.append(f'unresolved scaffold markers found: {len(marker_hits)}')
    scores = [int(match.group(1)) for match in SCORE_RE.finditer(text)]
    if not any(0 <= score <= 100 for score in scores):
        errors.append('no score on a 0 to 100 scale found')
    if not VERDICT_RE.search(text):
        errors.append('no benchmark verdict found')
    if 'not measured' not in lower and 'measured' not in lower and 'supplied' not in lower:
        warnings.append('behavioral measurement status is not explicit')

    scenario_keywords = ['should activate', 'should not activate', 'ambiguous', 'edge case']
    missing_scenario_keywords = [keyword for keyword in scenario_keywords if keyword not in lower]
    if missing_scenario_keywords:
        warnings.append('scenario category labels missing or renamed: ' + ', '.join(missing_scenario_keywords))

    target_sha = metadata_value(text, 'Target tree SHA-256')
    evaluator_sha = metadata_value(text, 'Evaluator SHA-256')
    scenario_sha = metadata_value(text, 'Scenario suite SHA-256')
    if target_sha is None or not SHA_RE.fullmatch(target_sha):
        errors.append('benchmark metadata missing valid Target tree SHA-256')
    if evaluator_sha is None or not SHA_RE.fullmatch(evaluator_sha):
        errors.append('benchmark metadata missing valid Evaluator SHA-256')
    if scenario_sha is None or not SHA_RE.fullmatch(scenario_sha):
        errors.append('benchmark metadata missing valid Scenario suite SHA-256')
    evidence_state = metadata_value(text, 'Source evidence state')
    if evidence_state not in {'frozen-snapshot', 'live-unfrozen'}:
        errors.append('benchmark metadata missing recognized Source evidence state')
    if evidence_state == 'live-unfrozen':
        warnings.append('report was generated from a live target; strict before/after comparison requires a frozen snapshot')

    failed_gate_visible = '| fail |' in lower
    checks = {
        'required_sections_present': not missing_sections,
        'scaffold_marker_count': len(marker_hits),
        'score_values_found': scores[:20],
        'verdict_present': bool(VERDICT_RE.search(text)),
        'measurement_status_explicit': any(token in lower for token in ['not measured', 'measured', 'supplied']),
        'scenario_category_labels_present': not missing_scenario_keywords,
        'target_identity_present': bool(target_sha and SHA_RE.fullmatch(target_sha)),
        'evaluator_identity_present': bool(evaluator_sha and SHA_RE.fullmatch(evaluator_sha)),
        'scenario_suite_identity_present': bool(scenario_sha and SHA_RE.fullmatch(scenario_sha)),
        'source_evidence_state': evidence_state,
        'failed_gate_visible': failed_gate_visible,
    }
    return {'status': 'pass' if not errors else 'fail', 'errors': errors, 'warnings': warnings, 'checks': checks}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Validate a generated skill benchmark report.')
    parser.add_argument('--report', required=True)
    parser.add_argument('--json-output')
    args = parser.parse_args(argv)
    result = validate_report(Path(args.report).resolve())
    if args.json_output:
        dump_json(result, args.json_output)
    dump_json(result)
    return 0 if result['status'] == 'pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())
