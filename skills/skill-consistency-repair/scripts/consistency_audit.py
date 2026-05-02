#!/usr/bin/env python3
"""Audit a target skill for internal consistency issues."""
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

CATEGORIES = {
    'package_structure',
    'activation_scope',
    'ownership_role',
    'resource_integration',
    'workflow_modes',
    'validation_packaging',
    'evidence_contract',
}

STOP_WORDS = {
    'the', 'and', 'for', 'with', 'when', 'use', 'skill', 'target', 'user', 'this', 'that', 'from',
    'work', 'workflow', 'mode', 'modes', 'file', 'files', 'output', 'outputs', 'artifact', 'artifacts',
}


def finding(fid: str, severity: str, category: str, title: str, evidence: str, problem: str, repair: str, gate: str, confidence: str = 'medium') -> dict[str, str]:
    return {
        'id': fid,
        'severity': severity,
        'category': category,
        'title': title,
        'evidence': evidence,
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


def check_broken_links(target: Path, inv: dict[str, Any], findings: list[dict[str, str]]) -> None:
    paths = existing_rel_paths(target)
    n = 1
    for link in inv.get('links', []):
        source = link['source']
        raw = link['target'].strip()
        if not raw or raw.startswith('#') or '://' in raw:
            continue
        source_dir = Path(source).parent
        resolved = (source_dir / raw).as_posix() if source_dir.as_posix() != '.' else raw
        resolved = str(Path(resolved).as_posix())
        if resolved not in paths and raw not in paths:
            findings.append(finding(
                f'L{n:03}', 'blocker', 'package_structure', 'broken local markdown link',
                f'{source} -> {raw}',
                'A local markdown link points to a file that does not exist in the target package.',
                'Fix the link, add the referenced file, or remove the link if the resource is obsolete.',
                'Re-run consistency_audit.py and verify broken local link count is zero.',
                'high',
            ))
            n += 1


def check_frontmatter(inv: dict[str, Any], findings: list[dict[str, str]]) -> None:
    fm = inv.get('frontmatter', {})
    if inv.get('skill_file_count') != 1:
        findings.append(finding(
            'S001', 'blocker', 'package_structure', 'target must contain exactly one SKILL.md',
            f"skill_files={inv.get('skill_files')}",
            'A skill package must resolve to a single root skill entrypoint before safe repair or packaging.',
            'Select or restructure the target so exactly one root SKILL.md is present.',
            'inventory_skill.py reports skill_file_count == 1.',
            'high',
        ))
    for idx, err in enumerate(fm.get('errors', []), start=1):
        findings.append(finding(
            f'F{idx:03}', 'blocker', 'package_structure', 'invalid or weak SKILL.md frontmatter',
            'SKILL.md frontmatter', err,
            'Use frontmatter with only lowercase name and lowercase description fields.',
            'Re-run audit and confirm no frontmatter errors remain.',
            'high',
        ))


def check_description(skill_text: str, inv: dict[str, Any], findings: list[dict[str, str]]) -> None:
    desc = inv.get('frontmatter', {}).get('fields', {}).get('description', '')
    if not desc:
        return
    if len(desc.split()) < 25:
        findings.append(finding(
            'A001', 'high', 'activation_scope', 'activation description is too thin',
            'SKILL.md frontmatter description',
            'The description may not give enough trigger and boundary signal for reliable activation.',
            'Expand the description with positive triggers, negative boundaries, owned outputs, and adjacent-skill exclusions.',
            'Audit confirms description contains clear triggers and negative boundaries.',
            'medium',
        ))
    negative_markers = ['do not use', 'do not activate', 'not use', 'avoid', 'unless']
    if not any(marker in desc.lower() for marker in negative_markers):
        findings.append(finding(
            'A002', 'medium', 'activation_scope', 'activation description lacks negative boundary',
            'SKILL.md frontmatter description',
            'The description says when to use the skill but does not clearly say when not to use it.',
            'Add concise negative triggers to prevent activation over adjacent workflows.',
            'Description includes explicit non-use cases.',
            'medium',
        ))
    desc_words = words(desc)
    body_words = words(skill_text[:5000])
    if desc_words and body_words and len(desc_words & body_words) / max(len(desc_words), 1) < 0.35:
        findings.append(finding(
            'A003', 'medium', 'activation_scope', 'frontmatter vocabulary drifts from body',
            'SKILL.md description versus body',
            'The activation description uses terms that are weakly represented in the body, which may indicate stale activation text or missing workflow details.',
            'Align description and body vocabulary around the same role, owned outputs, and boundaries.',
            'Re-run audit and inspect frontmatter/body overlap plus reviewer judgment.',
            'low',
        ))


def check_required_sections(skill_text: str, findings: list[dict[str, str]]) -> None:
    required = ['scope', 'required input', 'mode', 'workflow', 'stop condition', 'output contract']
    lower = skill_text.lower()
    missing = [section for section in required if section not in lower]
    if missing:
        findings.append(finding(
            'W001', 'high', 'workflow_modes', 'missing mature control-plane sections',
            'SKILL.md body',
            f'Missing or weak section signals: {missing}.',
            'Add compact sections for scope, required inputs, mode selection, workflow, stop conditions, and output contract.',
            'Audit no longer reports missing mature control-plane sections.',
            'medium',
        ))


def check_role_contradictions(skill_text: str, findings: list[dict[str, str]]) -> None:
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
                f'The skill appears to both allow/own and prohibit {term}-related behavior.',
                'Clarify mode-specific authority: either own the behavior, restrict it to specific modes, or move it to handoff.',
                'Reviewer confirms positive and negative rules are no longer contradictory.',
                'medium',
            ))
            idx += 1


def check_resource_integration(target: Path, inv: dict[str, Any], skill_text: str, findings: list[dict[str, str]]) -> None:
    all_text = skill_text
    text_files = []
    for f in inv.get('files', []):
        if f.get('is_text'):
            p = target / f['path']
            if p.exists():
                text_files.append(f['path'])
                if f['path'] != 'SKILL.md':
                    all_text += '\n' + read_text(p, 100_000)
    all_text_lower = all_text.lower()
    idx = 1
    for f in inv.get('files', []):
        path = f['path']
        if path == 'SKILL.md' or path.startswith('agents/'):
            continue
        if path.startswith(('references/', 'scripts/', 'assets/templates/', 'examples/', 'evals/')):
            basename = Path(path).name.lower()
            stem = Path(path).stem.lower()
            referenced = path.lower() in all_text_lower or basename in all_text_lower or stem in all_text_lower
            if not referenced:
                severity = 'medium' if path.startswith(('references/', 'scripts/', 'assets/templates/')) else 'low'
                findings.append(finding(
                    f'R{idx:03}', severity, 'resource_integration', 'supporting resource may be unintegrated',
                    path,
                    'The resource exists but is not referenced by name or path in inspected text resources.',
                    'Integrate it through a loading rule, workflow step, script consumer, validation gate, or remove it if it is placeholder/obsolete.',
                    'Re-run audit and confirm useful resources are integrated or intentionally removed.',
                    'medium',
                ))
                idx += 1
    for hit in inv.get('placeholder_hits', []):
        findings.append(finding(
            f'P{idx:03}', 'medium', 'resource_integration', 'placeholder or scaffold marker remains',
            f"{hit['path']} contains {hit['term']}",
            'The package appears to contain scaffold, TODO, placeholder, or example residue.',
            'Replace with real target-specific content or remove the placeholder file if unused.',
            'Audit placeholder count is zero except inside template files where placeholders are intentional.',
            'medium',
        ))
        idx += 1


def check_scripts(target: Path, inv: dict[str, Any], findings: list[dict[str, str]]) -> None:
    idx = 1
    for f in inv.get('files', []):
        path = f['path']
        if not path.startswith('scripts/') or not path.endswith('.py'):
            continue
        text = read_text(target / path)
        if 'argparse' not in text and 'click' not in text and 'if __name__' not in text:
            findings.append(finding(
                f'C{idx:03}', 'medium', 'validation_packaging', 'script lacks obvious cli contract',
                path,
                'The script does not expose an obvious command-line entrypoint, which makes repeatable validation harder.',
                'Add argparse/main or document why the script is imported-only and how it is used.',
                'Script has a documented CLI or a declared import-only consumer.',
                'medium',
            ))
            idx += 1


def check_scenarios(target: Path, inv: dict[str, Any], findings: list[dict[str, str]]) -> None:
    scenario_files = [f['path'] for f in inv.get('files', []) if f['path'].startswith(('examples/', 'evals/')) and f['path'].endswith('.json')]
    for idx, rel in enumerate(scenario_files, start=1):
        try:
            data = json.loads(read_text(target / rel))
        except Exception as exc:
            findings.append(finding(f'E{idx:03}', 'high', 'evidence_contract', 'scenario json is invalid', rel, str(exc), 'Fix JSON syntax/schema.', 'JSON parser succeeds.', 'high'))
            continue
        if isinstance(data, dict) and isinstance(data.get('scenarios'), list):
            data = data['scenarios']
        if not isinstance(data, list):
            findings.append(finding(f'E{idx:03}', 'medium', 'evidence_contract', 'scenario file should be a list or an object with scenarios list', rel, 'Scenario records should be a JSON array or {scenarios: [...]}.', 'Convert scenario file to a supported scenario schema.', 'Scenario validator or audit passes.', 'medium'))
            continue
        categories = {str(item.get('category')) for item in data if isinstance(item, dict)}
        needed = {'should_activate', 'should_not_activate', 'ambiguous', 'edge_case'}
        missing = sorted(needed - categories)
        if missing:
            findings.append(finding(
                f'E{idx:03}', 'medium', 'evidence_contract', 'scenario suite lacks minimum categories', rel,
                f'Missing categories: {missing}.',
                'Add planned scenarios for each minimum category, keeping measured fields null until executed.',
                'Audit confirms all minimum scenario categories exist.',
                'medium',
            ))
        for item in data:
            if isinstance(item, dict) and any(item.get(k) is not None for k in ('actual_activation', 'output_conforms', 'quality_score', 'needs_rework')):
                findings.append(finding(
                    f'E{idx:03}M', 'medium', 'evidence_contract', 'scenario appears measured without validation context', rel,
                    'A scenario contains measured fields. Ensure the report cites supplied or executed scenario evidence.',
                    'Keep measured fields null unless execution evidence is supplied, or attach validated results evidence.',
                    'Reviewer confirms measured-vs-planned evidence separation.',
                    'low',
                ))
                break


def score(findings: list[dict[str, str]]) -> dict[str, Any]:
    weights = {'blocker': 30, 'high': 12, 'medium': 5, 'low': 1}
    penalty = sum(weights.get(f['severity'], 1) for f in findings)
    value = max(0, 100 - penalty)
    counts = {sev: sum(1 for f in findings if f['severity'] == sev) for sev in ('blocker', 'high', 'medium', 'low')}
    status = 'pass' if counts['blocker'] == 0 and counts['high'] == 0 else 'fail'
    return {'score': value, 'max_score': 100, 'direction': 'higher-is-better', 'status': status, 'counts': counts}


def render_markdown(result: dict[str, Any]) -> str:
    lines = [
        '# Skill Consistency Audit',
        '',
        f"- Target: `{result['target_path']}`",
        f"- Generated at: {result['generated_at']}",
        f"- Score: {result['score']['score']} / {result['score']['max_score']}",
        f"- Status: {result['score']['status']}",
        f"- Finding counts: {result['score']['counts']}",
        '',
        '## Inventory Summary',
        '',
        '```json',
        json.dumps(result['inventory_summary'], indent=2, ensure_ascii=False),
        '```',
        '',
        '## Findings',
        '',
    ]
    if not result['findings']:
        lines.append('No consistency findings were detected by the static audit. Review semantic boundaries manually before publishing.')
    for f in result['findings']:
        lines.extend([
            f"### {f['id']} [{f['severity']}] {f['title']}",
            '',
            f"- Category: `{f['category']}`",
            f"- Evidence: {f['evidence']}",
            f"- Problem: {f['problem']}",
            f"- Repair: {f['repair']}",
            f"- Gate: {f['gate']}",
            f"- Confidence: {f['confidence']}",
            '',
        ])
    return '\n'.join(lines).rstrip() + '\n'


def audit(target: Path) -> dict[str, Any]:
    target = target.resolve()
    inv = scan_target(target)
    skill_text = load_skill_text(target)
    findings: list[dict[str, str]] = []
    check_frontmatter(inv, findings)
    check_broken_links(target, inv, findings)
    check_description(skill_text, inv, findings)
    check_required_sections(skill_text, findings)
    check_role_contradictions(skill_text, findings)
    check_resource_integration(target, inv, skill_text, findings)
    check_scripts(target, inv, findings)
    check_scenarios(target, inv, findings)
    summary = {
        'directories': inv.get('directories', []),
        'counts': inv.get('counts', {}),
        'skill_files': inv.get('skill_files', []),
        'frontmatter_errors': inv.get('frontmatter', {}).get('errors', []),
    }
    return {
        'target_path': target.as_posix(),
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'inventory_summary': summary,
        'findings': findings,
        'score': score(findings),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Audit a target skill for internal consistency.')
    parser.add_argument('--target', required=True)
    parser.add_argument('--json-output')
    parser.add_argument('--markdown-output')
    args = parser.parse_args()
    result = audit(Path(args.target))
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
