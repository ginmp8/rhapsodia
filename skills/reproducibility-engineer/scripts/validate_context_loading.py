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


PREVIEW_HEADINGS = {'at a glance', 'summary', 'quick reference', 'overview'}
CONTENTS_HEADINGS = {'contents', 'table of contents', 'section map'}
PREVIEW_REQUIRED_SIGNALS = ('purpose', 'load when', 'decision impact')
PREVIEW_EXCEPTION_RE = re.compile(r'<!--\s*context-preview-exception:\s*(generated|vendor|unsafe-to-rewrite)\s*-->', re.I)
GENERIC_PREVIEW_FRAGMENTS = (
    'read this file when the active workflow needs',
    'the decision-critical scope and section map are surfaced here',
    'primary topics:',
    'details below',
    'see contents',
    'see below',
    'when needed',
    'purpose only',
)




def preview_signal_values(lines: list[str]) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in lines:
        clean = re.sub(r'^\s*[-*+]\s*', '', line.strip()).replace('**', '')
        match = re.match(r'^(Purpose|Load when|Decision impact):\s*(.+?)\s*$', clean, re.I)
        if match:
            values[match.group(1).strip().lower()] = match.group(2).strip()
    return values


def preview_value_is_vague(value: str) -> bool:
    low = value.lower().strip()
    words = re.findall(r'[a-z0-9][a-z0-9_/-]*', low)
    if len(words) < 4:
        return True
    return any(fragment in low for fragment in GENERIC_PREVIEW_FRAGMENTS)


def preview_exception(lines: list[str]) -> str | None:
    match = PREVIEW_EXCEPTION_RE.search('\n'.join(lines[:PREVIEW_LIMIT]))
    return match.group(1).lower() if match else None

def h2_headings(lines: list[str]) -> list[str]:
    headings: list[str] = []
    in_fence = False
    fence = None
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(('```', '~~~')):
            marker = stripped[:3]
            if not in_fence:
                in_fence = True
                fence = marker
            elif marker == fence:
                in_fence = False
                fence = None
            continue
        if in_fence:
            continue
        match = re.match(r'^##\s+(.+?)\s*$', line)
        if match:
            headings.append(match.group(1).strip())
    return headings


def material_h2_headings(lines: list[str]) -> list[str]:
    excluded = PREVIEW_HEADINGS | CONTENTS_HEADINGS
    return [heading for heading in h2_headings(lines) if heading.strip().lower() not in excluded]


def contents_items(lines: list[str]) -> list[str] | None:
    in_fence = False
    fence = None
    start = None
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(('```', '~~~')):
            marker = stripped[:3]
            if not in_fence:
                in_fence = True
                fence = marker
            elif marker == fence:
                in_fence = False
                fence = None
            continue
        if in_fence:
            continue
        match = re.match(r'^##\s+(.+?)\s*$', line)
        if match and match.group(1).strip().lower() in CONTENTS_HEADINGS:
            start = index + 1
            break
    if start is None:
        return None

    items: list[str] = []
    for line in lines[start:]:
        if re.match(r'^##\s+', line):
            break
        match = re.match(r'^\s*[-*+]\s+(.+?)\s*$', line)
        if not match:
            continue
        item = match.group(1).strip()
        link = re.fullmatch(r'\[([^\]]+)\]\([^)]+\)', item)
        if link:
            item = link.group(1).strip()
        items.append(item.strip('`'))
    return items


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
        activation_present = has_any(first100, ['## activation and routing', 'use this skill', '**use when:**', 'use when:'])
        non_activation_present = has_any(first100, ['do not use', '**do not use when:**', 'not for', 'out of scope', 'route general optimization'])
        check('CONTEXT_TOP100_ACTIVATION_BOUNDARY', activation_present and non_activation_present, 'SKILL.md:first100', {'activation_present': activation_present, 'non_activation_present': non_activation_present})
        check('CONTEXT_TOP100_WORKFLOW', has_any(first100, ['workflow at a glance', 'quick start', '## workflow', '## process']), 'SKILL.md:first100')
        check('CONTEXT_TOP100_INVARIANTS', has_any(first100, ['core invariants', 'non-negotiable', 'core rules', 'authority', 'constraints', 'guardrails']), 'SKILL.md:first100')
        check('CONTEXT_TOP100_CONTROL_MODEL', has_any(first100, ['runtime/script', 'schema/type', 'validator/gate', 'control layer', 'control model']), 'SKILL.md:first100')
    else:
        for code in ['CONTEXT_TOP100_SCOPE', 'CONTEXT_TOP100_ROUTING', 'CONTEXT_TOP100_ACTIVATION_BOUNDARY', 'CONTEXT_TOP100_WORKFLOW', 'CONTEXT_TOP100_INVARIANTS', 'CONTEXT_TOP100_CONTROL_MODEL']:
            check(code, True, 'SKILL.md:first100', {'not_applicable': True, 'line_count': len(lines)})

    skill_h2 = {heading.lower() for heading in h2_headings(lines)}
    acceptance_applies = long_skill and 'acceptance gates' in skill_h2
    stop_applies = long_skill and 'stop conditions' in skill_h2
    check(
        'CONTEXT_TOP100_ACCEPTANCE_GATES',
        (not acceptance_applies) or has_any(first100, ['acceptance gates', 'acceptance gate']),
        'SKILL.md:first100',
        {'not_applicable': not acceptance_applies},
    )
    check(
        'CONTEXT_TOP100_STOP_CONDITIONS',
        (not stop_applies) or has_any(first100, ['stop conditions', 'stop condition', 'stop early', 'stop when']),
        'SKILL.md:first100',
        {'not_applicable': not stop_applies},
    )

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
    signal_failures: list[dict] = []
    contents_failures: list[dict] = []
    preview_exceptions: list[dict] = []
    warnings: list[dict] = []
    for path in all_refs:
        ref_lines = path.read_text(encoding='utf-8', errors='replace').splitlines()
        if len(ref_lines) <= CONTROL_LIMIT:
            continue
        rel = path.relative_to(root).as_posix()
        long_markdown.append(rel)
        exception = preview_exception(ref_lines)
        if exception:
            row = {'path': rel, 'exception': exception, 'line_count': len(ref_lines)}
            preview_exceptions.append(row)
            warnings.append({'code': 'CONTEXT_LONG_MARKDOWN_PREVIEW_EXCEPTION', 'status': 'warning', 'subject': rel, 'evidence': {'exception': exception}})
            continue

        preview_lines = ref_lines[:PREVIEW_LIMIT]
        preview = '\n'.join(preview_lines).lower()
        missing = []
        if not any(f'## {heading}' in preview for heading in PREVIEW_HEADINGS):
            missing.append('semantic preview heading')
        if not any(f'## {heading}' in preview for heading in CONTENTS_HEADINGS):
            missing.append('Contents')
        if missing:
            preview_failures.append({'path': rel, 'missing': missing, 'line_count': len(ref_lines)})
            continue

        contents_index = next((i for i, line in enumerate(preview_lines) if re.match(r'^##\s+(.+?)\s*$', line) and re.match(r'^##\s+(.+?)\s*$', line).group(1).strip().lower() in CONTENTS_HEADINGS), len(preview_lines))
        signals = preview_signal_values(preview_lines[:contents_index])
        missing_signals = [name for name in PREVIEW_REQUIRED_SIGNALS if name not in signals]
        vague_signals = [name for name, value in signals.items() if name in PREVIEW_REQUIRED_SIGNALS and preview_value_is_vague(value)]
        if missing_signals or vague_signals:
            signal_failures.append({'path': rel, 'missing': missing_signals, 'vague': vague_signals, 'signals': signals})

        expected = material_h2_headings(ref_lines)
        actual = contents_items(ref_lines)
        if actual != expected:
            contents_failures.append({'path': rel, 'expected': expected, 'actual': actual or []})
    check('CONTEXT_LONG_MARKDOWN_PREVIEW', not preview_failures, 'references/*.md', {'long_markdown': long_markdown, 'failures': preview_failures, 'exceptions': preview_exceptions})
    check('CONTEXT_LONG_MARKDOWN_PREVIEW_SIGNALS', not signal_failures, 'references/*.md', {'failures': signal_failures})
    check('CONTEXT_LONG_MARKDOWN_CONTENTS', not contents_failures, 'references/*.md', {'failures': contents_failures})

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
        'warnings': warnings,
        'limitations': [
            'This validator proves structural discoverability, not semantic correctness or behavioral quality.',
            'A direct reference link proves reachability, not that every branch instruction is sufficient or current.',
            'Preview signal checks reject missing and obvious placeholder text, but semantic specificity still requires review.',
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
