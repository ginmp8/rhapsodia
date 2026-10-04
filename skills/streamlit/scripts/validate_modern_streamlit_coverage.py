#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path

REQUIRED = [
    'references/version-and-source-resolution.md',
    'references/design-accessibility-and-theme.md',
    'references/custom-components-v2.md',
    'references/server-asgi.md',
    'references/authentication-authorization-and-trust.md',
    'scripts/resolve_streamlit_context.py',
    'evals/modern-api-scenarios.json',
]


def main() -> int:
    parser = argparse.ArgumentParser(description='Validate version-aware modern Streamlit coverage additions.')
    parser.add_argument('target', nargs='?', default='.')
    parser.add_argument('--json', dest='json_path')
    args = parser.parse_args()
    root = Path(args.target).resolve()
    checks = []

    def check(code: str, ok: bool, subject: str, evidence: object) -> None:
        checks.append({'code': code, 'status': 'pass' if ok else 'fail', 'subject': subject, 'evidence': evidence})

    skill = (root / 'SKILL.md').read_text(encoding='utf-8')
    for rel in REQUIRED:
        path = root / rel
        check('resource/present', path.is_file(), rel, {'exists': path.is_file()})
        check('resource/integrated', rel in skill, rel, {'listed_in_skill': rel in skill})

    resolver = root / 'scripts/resolve_streamlit_context.py'
    if resolver.is_file():
        try:
            ast.parse(resolver.read_text(encoding='utf-8'), filename=str(resolver))
            check('resolver/parse', True, 'scripts/resolve_streamlit_context.py', {})
        except SyntaxError as exc:
            check('resolver/parse', False, 'scripts/resolve_streamlit_context.py', {'line': exc.lineno, 'error': exc.msg})

    modern = root / 'evals/modern-api-scenarios.json'
    if modern.is_file():
        try:
            data = json.loads(modern.read_text(encoding='utf-8'))
            scenarios = data.get('scenarios', [])
            ids = [x.get('id') for x in scenarios if isinstance(x, dict)]
            check('eval/count', len(scenarios) >= 10, str(modern.relative_to(root)), {'count': len(scenarios)})
            check('eval/unique-ids', bool(ids) and len(ids) == len(set(ids)) and all(ids), str(modern.relative_to(root)), {'count': len(ids), 'unique': len(set(ids))})
        except Exception as exc:
            check('eval/json', False, str(modern.relative_to(root)), {'error': str(exc)})

    api = (root / 'references/api-command-guide.md').read_text(encoding='utf-8')
    check('api-guide/non-authoritative', 'not the authority for exact current signatures' in api, 'references/api-command-guide.md', {})
    check('routing/version-first', 'version-and-source-resolution.md' in skill and skill.index('version-and-source-resolution.md') < skill.index('api-command-guide.md'), 'SKILL.md', {})
    check('routing/components-v2', 'custom-components-v2.md' in skill, 'SKILL.md', {})
    check('routing/asgi', 'server-asgi.md' in skill, 'SKILL.md', {})

    failures = [c for c in checks if c['status'] == 'fail']
    receipt = {'receipt_version': 1, 'status': 'pass' if not failures else 'fail', 'stage': 'modern-coverage', 'target': str(root), 'checks': checks, 'errors': len(failures)}
    rendered = json.dumps(receipt, indent=2, sort_keys=True)
    if args.json_path:
        out = Path(args.json_path).resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        tmp = out.with_name(out.name + '.tmp')
        tmp.write_text(rendered + '\n', encoding='utf-8')
        tmp.replace(out)
    print(rendered)
    return 0 if not failures else 1


if __name__ == '__main__':
    raise SystemExit(main())
