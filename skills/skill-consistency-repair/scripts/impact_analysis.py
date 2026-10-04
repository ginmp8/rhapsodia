#!/usr/bin/env python3
"""Compute deterministic relation-driven change impact between two skill inventories."""
from __future__ import annotations

import argparse
import json
from collections import deque
from pathlib import Path
from typing import Any


def load(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(data, dict):
        raise ValueError(f'expected JSON object: {path}')
    return data


def hashes(inv: dict[str, Any]) -> dict[str, str]:
    return {str(row['path']): str(row.get('sha256', '')) for row in inv.get('files', []) if isinstance(row, dict) and row.get('path')}


def changed_files(before: dict[str, Any], after: dict[str, Any]) -> dict[str, list[str]]:
    old, new = hashes(before), hashes(after)
    return {
        'added': sorted(set(new) - set(old)),
        'removed': sorted(set(old) - set(new)),
        'changed': sorted(path for path in set(old) & set(new) if old[path] != new[path]),
    }


def analyze(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    changes = changed_files(before, after)
    changed = sorted(set(changes['added'] + changes['removed'] + changes['changed']))
    relations = after.get('relation_graph') or [
        {'source': e['source'], 'target': e['target'], 'relation': e.get('type', 'REFERENCES'), 'detector': e.get('type', 'unknown')}
        for e in after.get('reference_graph', [])
    ]
    reverse: dict[str, set[str]] = {}
    for edge in relations:
        if not isinstance(edge, dict) or not edge.get('source') or not edge.get('target'):
            continue
        reverse.setdefault(str(edge['target']), set()).add(str(edge['source']))

    direct = sorted({source for target in changed for source in reverse.get(target, set()) if source not in changed})
    visited = set(changed)
    queue = deque(changed)
    transitive: set[str] = set()
    while queue:
        target = queue.popleft()
        for source in sorted(reverse.get(target, set())):
            if source in visited:
                continue
            visited.add(source)
            transitive.add(source)
            queue.append(source)

    impacted = sorted(set(changed) | transitive)
    gates: list[str] = []
    def add_gate(name: str) -> None:
        if name not in gates:
            gates.append(name)
    if any(path == 'SKILL.md' or path.startswith('references/') for path in impacted):
        add_gate('consistency-audit')
    if any(path.startswith('scripts/') for path in impacted):
        add_gate('script-syntax-and-target-tests')
    if any(path.startswith(('evals/', 'tests/')) for path in impacted):
        add_gate('evaluator-or-test-integrity')
    if any('package' in path.lower() or path.startswith('assets/templates/') for path in impacted):
        add_gate('package-validation')
    add_gate('final-full-validation')

    return {
        'impact_version': 1,
        'baseline_inventory_identity': before.get('inventory_fingerprint'),
        'candidate_inventory_identity': after.get('inventory_fingerprint'),
        'changes': changes,
        'direct_dependents': direct,
        'transitive_dependents': sorted(transitive),
        'impacted_files': impacted,
        'suggested_gates': gates,
        'claim_boundary': 'Suggested gates are deterministic impact hints; final declared validation remains required.',
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Compute relation-driven change impact between deterministic skill inventories.')
    parser.add_argument('--before', required=True, help='Baseline inventory JSON.')
    parser.add_argument('--after', required=True, help='Candidate inventory JSON.')
    parser.add_argument('--output')
    args = parser.parse_args()
    try:
        result = analyze(load(Path(args.before)), load(Path(args.after)))
    except Exception as exc:
        print(json.dumps({'status': 'fail', 'error': str(exc)}, indent=2))
        return 1
    data = json.dumps(result, indent=2, ensure_ascii=False) + '\n'
    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(data, encoding='utf-8')
    else:
        print(data, end='')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
