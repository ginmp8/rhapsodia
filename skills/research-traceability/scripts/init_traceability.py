#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from _common import atomic_write_json


def identity(kind: str, value: str) -> dict[str, str]:
    return {'kind': kind, 'value': value}


def main() -> int:
    parser = argparse.ArgumentParser(description='Initialize a research-to-skill traceability workspace.')
    parser.add_argument('--mode', required=True, choices=['create', 'improve', 'audit', 'refresh'])
    parser.add_argument('--research-question', required=True)
    parser.add_argument('--target', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--research-identity-kind', default='declared', choices=['none', 'sha256', 'manifest', 'vcs', 'version', 'declared'])
    parser.add_argument('--research-identity', default='')
    parser.add_argument('--target-identity-kind', default='none', choices=['none', 'sha256', 'manifest', 'vcs', 'version', 'declared'])
    parser.add_argument('--target-identity', default='')
    parser.add_argument('--evaluator-identity-kind', default='none', choices=['none', 'sha256', 'manifest', 'vcs', 'version', 'declared'])
    parser.add_argument('--evaluator-identity', default='')
    args = parser.parse_args()

    output = Path(args.output).expanduser().resolve(strict=False)
    if output.exists():
        print(f'ERROR: output already exists: {output}')
        return 1

    data = {
        'schema_version': '1.0',
        'mode': args.mode,
        'scope': {
            'research_question': args.research_question.strip(),
            'target': args.target.strip(),
            'completeness_boundary': 'corpus-bounded'
        },
        'identities': {
            'research': identity(args.research_identity_kind, args.research_identity),
            'target_baseline': identity(args.target_identity_kind, args.target_identity),
            'evaluators': identity(args.evaluator_identity_kind, args.evaluator_identity)
        },
        'sources': [],
        'findings': [],
        'requirements': [],
        'changes': [],
        'evaluations': [],
        'conflicts': []
    }
    atomic_write_json(output, data)
    print(output)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
