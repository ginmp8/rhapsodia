#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

REQUIRED_REFS = [
    'references/reproducible-workflow.md',
    'references/source-and-license.md',
    'references/topic-map.md',
    'references/api-command-guide.md',
    'references/app-architecture.md',
    'references/execution-state-and-reruns.md',
    'references/widgets-forms-and-callbacks.md',
    'references/layout-navigation-and-pages.md',
    'references/dataframes-charts-and-editors.md',
    'references/caching-connections-and-performance.md',
    'references/files-uploads-downloads-and-media.md',
    'references/llm-chat-and-rag-apps.md',
    'references/auth-secrets-and-security.md',
    'references/testing-and-apptest.md',
    'references/deployment-and-operations.md',
    'references/troubleshooting.md',
    'references/recipes.md',
    'references/anti-patterns.md',
    'references/production-review-rubric.md',
]

REQUIRED_ASSETS = [
    'assets/templates/app.py.template',
    'assets/templates/chat-app.py.template',
    'assets/templates/multipage-app.py.template',
    'assets/templates/apptest-test.py.template',
    'assets/templates/dockerfile.template',
    'assets/templates/review-report.md.template',
    'examples/review-example.md',
    'examples/request-patterns.md',
]

REQUIRED_CONTRACTS = ['references/reproducibility-contract.json']

REQUIRED_EVALS = [
    'evals/activation-scenarios.json',
    'evals/reproducibility-scenarios.json',
]

BAD_MARKERS = [
    'TO' + 'DO',
    'FIX' + 'ME',
    'lorem' + ' ipsum',
    'your' + '_api' + '_key' + '_here',
    '[' + 'severity' + ']',
    'finding' + ' - evidence',
    '- ' + (chr(46) * 3),
    'Required fixes before release' + '\n' + '- ' + (chr(46) * 3),
    '[' + 'approve | approve with reservations | reject' + ']',
]

TEXT_SUFFIXES = {'.md', '.py', '.json', '.yaml', '.yml', '.toml', '.template'}
LOCAL_REF_RE = re.compile(r'`((?:references|assets|examples|evals|scripts)/[^`]+)`')


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def tree_hash(root: Path) -> tuple[str, int, int]:
    rows: list[dict[str, Any]] = []
    total = 0
    for path in sorted(p for p in root.rglob('*') if p.is_file()):
        rel = path.relative_to(root).as_posix()
        size = path.stat().st_size
        total += size
        rows.append({'path': rel, 'size': size, 'sha256': sha256_file(path)})
    payload = json.dumps(rows, sort_keys=True, separators=(',', ':')).encode('utf-8')
    return hashlib.sha256(payload).hexdigest(), len(rows), total


def parse_frontmatter(text: str) -> tuple[dict[str, str], str | None]:
    if not text.startswith('---\n'):
        return {}, 'missing YAML frontmatter'
    end = text.find('\n---\n', 4)
    if end < 0:
        return {}, 'unterminated YAML frontmatter'
    block = text[4:end]
    data: dict[str, str] = {}
    for raw in block.splitlines():
        line = raw.strip()
        if not line:
            continue
        if ':' not in line:
            return {}, f'invalid frontmatter line: {raw}'
        key, value = line.split(':', 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        data[key] = value
    return data, None


def write_json_atomic(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f'.{path.name}.tmp')
    temp.write_text(json.dumps(data, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    temp.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('root', nargs='?', default='.')
    parser.add_argument('--json', dest='json_path')
    args = parser.parse_args()

    root = Path(args.root).resolve()
    checks: list[dict[str, Any]] = []

    def check(code: str, ok: bool, subject: str, evidence: Any, severity: str = 'error') -> None:
        checks.append({
            'code': code,
            'status': 'pass' if ok else 'fail',
            'subject': subject,
            'severity': severity,
            'evidence': evidence,
        })

    skill = root / 'SKILL.md'
    check('package/skill-md-present', skill.is_file(), 'SKILL.md', {'exists': skill.is_file()})
    skill_text = skill.read_text(encoding='utf-8') if skill.is_file() else ''

    frontmatter, fm_error = parse_frontmatter(skill_text) if skill_text else ({}, 'missing SKILL.md')
    check('frontmatter/parse', fm_error is None, 'SKILL.md', {'error': fm_error})
    check('frontmatter/keys', set(frontmatter) == {'name', 'description'}, 'SKILL.md', {'keys': sorted(frontmatter)})
    check('frontmatter/name', frontmatter.get('name') == 'streamlit', 'SKILL.md', {'name': frontmatter.get('name')})
    desc = frontmatter.get('description', '')
    check('frontmatter/description', len(desc) >= 120 and 'streamlit' in desc.lower(), 'SKILL.md', {'length': len(desc)})

    for ref in REQUIRED_REFS:
        path = root / ref
        check('reference/present', path.is_file(), ref, {'exists': path.is_file()})
        if path.is_file():
            check('reference/nontrivial', path.stat().st_size >= 1000, ref, {'bytes': path.stat().st_size})
            check('skill/reference-listed', ref in skill_text, ref, {'listed': ref in skill_text})

    for asset in REQUIRED_ASSETS:
        path = root / asset
        check('asset/present', path.is_file(), asset, {'exists': path.is_file()})
        if path.is_file():
            check('asset/nontrivial', path.stat().st_size >= 400, asset, {'bytes': path.stat().st_size})

    for contract in REQUIRED_CONTRACTS:
        path = root / contract
        check('contract/present', path.is_file(), contract, {'exists': path.is_file()})
        check('skill/contract-listed', contract in skill_text, contract, {'listed': contract in skill_text})
        if path.is_file():
            try:
                data = json.loads(path.read_text(encoding='utf-8'))
                check('contract/version', data.get('contract_version') == 1, contract, {'contract_version': data.get('contract_version')})
                check('contract/modes', data.get('primary_modes') == ['build','debug','review','test','deploy','optimize','migrate','reference'], contract, {'primary_modes': data.get('primary_modes')})
                check('contract/stagnation-limit', data.get('repair', {}).get('stagnation_limit') == 2, contract, {'stagnation_limit': data.get('repair', {}).get('stagnation_limit')})
                check('contract/freeze-after-pass', data.get('delivery', {}).get('freeze_after_pass') is True, contract, {'freeze_after_pass': data.get('delivery', {}).get('freeze_after_pass')})
            except Exception as exc:
                check('contract/json', False, contract, {'error': str(exc)})

    for ev in REQUIRED_EVALS:
        path = root / ev
        check('eval/present', path.is_file(), ev, {'exists': path.is_file()})
        if path.is_file():
            try:
                data = json.loads(path.read_text(encoding='utf-8'))
                scenarios = data.get('scenarios', [])
                check('eval/json', isinstance(scenarios, list), ev, {'scenario_count': len(scenarios) if isinstance(scenarios, list) else None})
            except Exception as exc:
                check('eval/json', False, ev, {'error': str(exc)})

    activation = root / 'evals/activation-scenarios.json'
    if activation.is_file():
        try:
            data = json.loads(activation.read_text(encoding='utf-8'))
            scenarios = data.get('scenarios', [])
            types = {s.get('type') for s in scenarios if isinstance(s, dict)}
            check('eval/activation-count', len(scenarios) >= 12, activation.relative_to(root).as_posix(), {'count': len(scenarios)})
            for expected in ['should_activate', 'should_not_activate', 'ambiguous', 'edge_case']:
                check('eval/activation-type', expected in types, activation.relative_to(root).as_posix(), {'required': expected, 'types': sorted(x for x in types if x)})
        except Exception:
            pass

    repro = root / 'evals/reproducibility-scenarios.json'
    if repro.is_file():
        try:
            data = json.loads(repro.read_text(encoding='utf-8'))
            scenarios = data.get('scenarios', [])
            groups = {s.get('group') for s in scenarios if isinstance(s, dict)}
            ids = [s.get('id') for s in scenarios if isinstance(s, dict)]
            check('eval/repro-count', len(scenarios) >= 8, repro.relative_to(root).as_posix(), {'count': len(scenarios)})
            for expected in ['core', 'edge', 'regression', 'adversarial', 'holdout']:
                check('eval/repro-group', expected in groups, repro.relative_to(root).as_posix(), {'required': expected, 'groups': sorted(x for x in groups if x)})
            check('eval/repro-unique-ids', len(ids) == len(set(ids)) and all(ids), repro.relative_to(root).as_posix(), {'count': len(ids), 'unique': len(set(ids))})
        except Exception:
            pass

    app_py = root / 'app.py'
    check('package/no-root-app', not app_py.exists(), 'app.py', {'exists': app_py.exists()})

    for m in LOCAL_REF_RE.finditer(skill_text):
        rel = m.group(1)
        check('skill/local-reference', (root / rel).exists(), rel, {'exists': (root / rel).exists()})

    for path in sorted(root.rglob('*')):
        if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue
        rel = path.relative_to(root).as_posix()
        text = path.read_text(encoding='utf-8', errors='ignore')
        for marker in BAD_MARKERS:
            check('content/no-scaffold-marker', marker.lower() not in text.lower(), rel, {'marker': marker})
        if path.suffix == '.py':
            try:
                ast.parse(text, filename=rel)
                check('python/parse', True, rel, {})
            except SyntaxError as exc:
                check('python/parse', False, rel, {'line': exc.lineno, 'error': exc.msg})

    agent = root / 'agents/openai.yaml'
    agent_text = agent.read_text(encoding='utf-8') if agent.is_file() else ''
    check('agent/openai-present', agent.is_file(), 'agents/openai.yaml', {'exists': agent.is_file()})
    check('agent/display-name', 'display_name:' in agent_text, 'agents/openai.yaml', {})
    check('agent/short-description', 'short_description:' in agent_text, 'agents/openai.yaml', {})

    tree_sha, file_count, total_bytes = tree_hash(root)
    check('package/size-limit', total_bytes <= 25 * 1024 * 1024, str(root), {'bytes': total_bytes, 'limit': 25 * 1024 * 1024})

    failures = [c for c in checks if c['status'] == 'fail' and c['severity'] == 'error']
    warnings = [c for c in checks if c['status'] == 'fail' and c['severity'] == 'warning']
    receipt = {
        'receipt_version': 1,
        'status': 'pass' if not failures else 'fail',
        'stage': 'validation',
        'target': str(root),
        'checks': checks,
        'errors': len(failures),
        'warnings': len(warnings),
        'metrics': {'file_count': file_count, 'total_bytes': total_bytes},
        'hashes': {'target_tree_sha256': tree_sha},
    }

    if args.json_path:
        write_json_atomic(Path(args.json_path).resolve(), receipt)

    if failures:
        print('FAIL')
        for item in failures:
            print(f"- {item['code']}: {item['subject']} {json.dumps(item['evidence'], sort_keys=True)}")
        return 1

    print('PASS')
    if args.json_path:
        print(Path(args.json_path).resolve())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
