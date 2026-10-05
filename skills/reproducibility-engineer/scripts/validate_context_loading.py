#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

from _common import dump_json, markdown_local_links, parse_frontmatter

PREVIEW_LIMIT = 40
CONTROL_LIMIT = 100


def has_any(text: str, patterns: list[str]) -> bool:
    low = text.lower()
    return any(pattern.lower() in low for pattern in patterns)


def main() -> int:
    ap = argparse.ArgumentParser(description='Validate progressive context-loading structure for an Agent Skill package.')
    ap.add_argument('--target', required=True)
    ap.add_argument('--json', dest='json_out')
    args = ap.parse_args()

    root = Path(args.target).resolve()
    skill_md = root / 'SKILL.md'
    diagnostics: list[dict] = []
    checks: list[dict] = []

    def check(code: str, ok: bool, subject: str, evidence: dict | None = None) -> None:
        row = {'code': code, 'status': 'pass' if ok else 'fail', 'subject': subject, 'evidence': evidence or {}}
        checks.append(row)
        if not ok:
            diagnostics.append(row)

    if not skill_md.is_file():
        check('CONTEXT_ROOT_SKILL', False, 'SKILL.md', {'reason': 'missing root SKILL.md'})
        dump_json({'status': 'fail', 'target': str(root), 'checks': checks, 'diagnostics': diagnostics}, args.json_out)
        return 1

    text = skill_md.read_text(encoding='utf-8', errors='replace')
    lines = text.splitlines()
    first100 = '\n'.join(lines[:CONTROL_LIMIT])
    fm = parse_frontmatter(skill_md)
    long_skill = len(lines) > CONTROL_LIMIT

    check('CONTEXT_DESCRIPTION', bool(fm.get('description')), 'SKILL.md frontmatter', {'line_count': len(lines)})
    if long_skill:
        check('CONTEXT_TOP100_SCOPE', has_any(first100, ['## at a glance', '## mission', '## purpose', '## scope']), 'SKILL.md:first100')
        check('CONTEXT_TOP100_ROUTING', has_any(first100, ['## modes', 'router', 'routing']), 'SKILL.md:first100')
        check('CONTEXT_TOP100_WORKFLOW', has_any(first100, ['workflow at a glance', 'quick start', '## workflow', '## process']), 'SKILL.md:first100')
        check('CONTEXT_TOP100_INVARIANTS', has_any(first100, ['core invariants', 'non-negotiable', 'core rules', 'authority', 'constraints', 'guardrails']), 'SKILL.md:first100')
        check('CONTEXT_TOP100_CONTROL_MODEL', has_any(first100, ['runtime/script', 'schema/type', 'validator/gate', 'control layer', 'control model']), 'SKILL.md:first100')
    else:
        for code in ['CONTEXT_TOP100_SCOPE', 'CONTEXT_TOP100_ROUTING', 'CONTEXT_TOP100_WORKFLOW', 'CONTEXT_TOP100_INVARIANTS', 'CONTEXT_TOP100_CONTROL_MODEL']:
            check(code, True, 'SKILL.md:first100', {'not_applicable': True, 'line_count': len(lines)})

    all_refs = sorted((root / 'references').glob('*.md')) if (root / 'references').is_dir() else []
    direct_targets = {target.split('#', 1)[0] for target in markdown_local_links(skill_md)}
    direct_ref_paths = {target for target in direct_targets if target.startswith('references/') and target.endswith('.md')}
    missing_direct = [p.relative_to(root).as_posix() for p in all_refs if p.relative_to(root).as_posix() not in direct_ref_paths]
    check('CONTEXT_DIRECT_REFERENCE_TOPOLOGY', not missing_direct, 'SKILL.md -> references/*.md', {'missing_direct': missing_direct, 'reference_count': len(all_refs)})

    if long_skill and all_refs:
        first100_links = {target.split('#', 1)[0] for target in markdown_local_links_from_text(first100)}
        check('CONTEXT_TOP100_REFERENCE_POINTERS', any(target.startswith('references/') for target in first100_links), 'SKILL.md:first100', {'first100_reference_links': sorted(first100_links)})
    else:
        check('CONTEXT_TOP100_REFERENCE_POINTERS', True, 'SKILL.md:first100', {'not_applicable': not bool(all_refs)})

    long_markdown: list[str] = []
    preview_failures: list[dict] = []
    for path in all_refs:
        ref_lines = path.read_text(encoding='utf-8', errors='replace').splitlines()
        if len(ref_lines) <= CONTROL_LIMIT:
            continue
        rel = path.relative_to(root).as_posix()
        long_markdown.append(rel)
        preview = '\n'.join(ref_lines[:PREVIEW_LIMIT]).lower()
        missing = []
        if '## at a glance' not in preview:
            missing.append('At a Glance')
        if '## contents' not in preview:
            missing.append('Contents')
        if missing:
            preview_failures.append({'path': rel, 'missing': missing, 'line_count': len(ref_lines)})
    check('CONTEXT_LONG_MARKDOWN_PREVIEW', not preview_failures, 'references/*.md', {'long_markdown': long_markdown, 'failures': preview_failures})

    report = {
        'status': 'pass' if not diagnostics else 'fail',
        'target': str(root),
        'evidence_type': 'structural-context-loading-only',
        'control_surface': {
            'skill_md_lines': len(lines),
            'control_limit_lines': CONTROL_LIMIT,
            'long_skill_contract_applies': long_skill,
            'support_preview_limit_lines': PREVIEW_LIMIT,
        },
        'checks': checks,
        'diagnostics': diagnostics,
        'limitations': [
            'This validator proves structural discoverability, not semantic correctness or behavioral quality.',
            'A direct reference link proves reachability, not that every branch instruction is sufficient or current.',
        ],
    }
    dump_json(report, args.json_out)
    return 0 if not diagnostics else 1


def markdown_local_links_from_text(text: str) -> list[str]:
    links = []
    for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', text):
        target = target.strip().strip('<>')
        if not target or target.startswith(('#', 'http://', 'https://', 'mailto:', 'skills://', 'sandbox:')):
            continue
        links.append(target)
    return links


if __name__ == '__main__':
    raise SystemExit(main())
