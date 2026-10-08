#!/usr/bin/env python3
"""Validate standalone package contracts without executing examples or dependencies."""
from __future__ import annotations
import ast
import json
from pathlib import Path
import re
import sys
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from oc_core.cli import COMMANDS
from oc_core import VERSION


def validate(root):
    errors = []
    for rel in ('SKILL.md', 'VERSION', 'LICENSE', 'contracts/commands.json', 'evals/activation-scenarios.json'):
        if not (root / rel).is_file():
            errors.append('Missing ' + rel)
    if errors:
        return {'status': 'fail', 'errors': errors}
    entry = (root / 'SKILL.md').read_text(encoding='utf-8')
    top = '\n'.join(entry.splitlines()[:100]).lower()
    for term in ('name: operational-context', 'workflow', 'stop conditions', 'critical invariants', 'output contract', 'python 3.10+'):
        if term not in top:
            errors.append('Top-100 missing ' + term)
    if (root / 'VERSION').read_text().strip() != VERSION:
        errors.append('Version differs from executable package version')
    catalog = json.loads((root / 'contracts/commands.json').read_text())
    if set(catalog.get('commands', {})) != set(COMMANDS) or catalog.get('version') != VERSION:
        errors.append('Command catalog differs from CLI/version')
    for name, command in catalog.get('commands', {}).items():
        schema = command.get('request_schema', {})
        if schema.get('type') != 'object' or schema.get('additionalProperties') is not False:
            errors.append('Unbounded request schema: ' + name)
        if not set(schema.get('required', [])) <= schema.get('properties', {}).keys():
            errors.append('Required/properties drift: ' + name)
    groups = {s.get('group') for s in json.loads((root / 'evals/activation-scenarios.json').read_text()).get('scenarios', [])}
    if not {'activation', 'non-activation', 'ambiguous', 'boundary', 'adversarial', 'holdout'} <= groups:
        errors.append('Incomplete declared activation scenario groups')
    imports = set()
    for path in root.rglob('*'):
        if path.is_symlink():
            errors.append('Symlink in package: ' + path.relative_to(root).as_posix())
            continue
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if '__pycache__' in rel.parts or path.suffix == '.pyc' or '.rhapsodia' in rel.parts:
            errors.append('Generated/private residue: ' + rel.as_posix())
        if path.suffix == '.json':
            json.loads(path.read_text(encoding='utf-8'))
        if path.suffix == '.md':
            for link in re.findall(r'\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
                target = link.split('#', 1)[0]
                if not target or '://' in target:
                    continue
                resolved = (path.parent / target).resolve()
                if not resolved.is_relative_to(root.resolve()) or not resolved.is_file():
                    errors.append('Broken/escaping local link: ' + rel.as_posix() + ': ' + link)
        if path.suffix == '.py':
            tree = ast.parse(path.read_text(encoding='utf-8'), feature_version=(3, 10))
            if 'scripts' in rel.parts:
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        imports.update(a.name.split('.')[0] for a in node.names)
                    if isinstance(node, ast.ImportFrom) and node.module and not node.level:
                        imports.add(node.module.split('.')[0])
    unexpected = imports - sys.stdlib_module_names - {'oc_core'}
    if unexpected:
        errors.append('Nonstdlib/peer imports: ' + ','.join(sorted(unexpected)))
    return {'status': 'fail' if errors else 'pass', 'version': VERSION, 'commands': len(COMMANDS),
            'activation_groups': sorted(groups), 'errors': errors,
            'evidence_level': 'structural-local-package', 'native_host_routing_tested': False}


def main():
    try:
        result = validate(ROOT)
    except (OSError, ValueError, SyntaxError) as exc:
        result = {'status': 'fail', 'errors': [str(exc)]}
    print(json.dumps(result, indent=2))
    return 0 if result['status'] == 'pass' else 1

if __name__ == '__main__':
    raise SystemExit(main())
