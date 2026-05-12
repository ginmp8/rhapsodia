#!/usr/bin/env python3
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

REQUIRED_REFS = [
    'references/source-and-license.md','references/topic-map.md','references/api-command-guide.md','references/app-architecture.md',
    'references/execution-state-and-reruns.md','references/widgets-forms-and-callbacks.md','references/layout-navigation-and-pages.md',
    'references/dataframes-charts-and-editors.md','references/caching-connections-and-performance.md',
    'references/files-uploads-downloads-and-media.md','references/llm-chat-and-rag-apps.md','references/auth-secrets-and-security.md',
    'references/testing-and-apptest.md','references/deployment-and-operations.md','references/troubleshooting.md','references/recipes.md',
    'references/anti-patterns.md','references/production-review-rubric.md'
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


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    errors = []
    skill = root / 'SKILL.md'
    if not skill.exists():
        errors.append('missing SKILL.md')
    else:
        text = skill.read_text(encoding='utf-8')
        if not text.startswith('---'):
            errors.append('SKILL.md missing YAML frontmatter')
        if 'name: streamlit' not in text:
            errors.append('frontmatter name must be streamlit')
        if 'description:' not in text:
            errors.append('frontmatter description missing')
        for ref in REQUIRED_REFS:
            if ref not in text:
                errors.append(f'SKILL.md does not reference {ref}')
    for ref in REQUIRED_REFS:
        path = root / ref
        if not path.exists():
            errors.append(f'missing reference {ref}')
        elif path.stat().st_size < 1200:
            errors.append(f'reference too small: {ref}')

    if (root / 'app.py').exists():
        errors.append('unexpected root app.py; starter apps must live under assets/templates')
    for asset in REQUIRED_ASSETS:
        path = root / asset
        if not path.exists():
            errors.append(f'missing required asset {asset}')
        elif path.stat().st_size < 400:
            errors.append(f'asset too small: {asset}')

    evals = root / 'evals' / 'activation-scenarios.json'
    if not evals.exists():
        errors.append('missing activation scenarios')
    else:
        data = json.loads(evals.read_text(encoding='utf-8'))
        scenarios = data.get('scenarios', [])
        if len(scenarios) < 12:
            errors.append('expected at least 12 activation scenarios')
        types = {s.get('type') for s in scenarios}
        for expected in ['should_activate','should_not_activate','ambiguous','edge_case']:
            if expected not in types:
                errors.append(f'missing scenario type {expected}')
    for path in root.rglob('*'):
        if path.is_file() and path.suffix in {'.md','.py','.json','.yaml','.toml','.template'}:
            text = path.read_text(encoding='utf-8', errors='ignore')
            for marker in BAD_MARKERS:
                if marker.lower() in text.lower():
                    errors.append(f'{path.relative_to(root)} contains scaffold marker {marker}')
    if errors:
        print('FAIL')
        for e in errors:
            print(f'- {e}')
        return 1
    print('PASS')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
