#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from _common import dump_json, sha256_file

DEFAULT_EVALUATOR_PATHS = [
    'references/benchmark-rubric.md',
    'references/test-scenarios.md',
    'references/report-template.md',
    'scripts/_common.py',
    'scripts/benchmark_identity.py',
    'scripts/generate_benchmark_report.py',
    'scripts/validate_benchmark_report.py',
    'scripts/validate_scenario_results.py',
    'scripts/validate_portability.py',
]
DEFAULT_SCENARIO_SUITE = 'evals/activation-scenarios.json'


def identity(root: Path, paths: list[str]) -> dict:
    root = root.resolve(strict=True)
    rows: list[dict] = []
    for rel in paths:
        path = root / rel
        if not path.is_file():
            raise FileNotFoundError(f'evaluator file missing: {rel}')
        rows.append({'path': rel, 'size': path.stat().st_size, 'sha256': sha256_file(path)})
    payload = json.dumps(rows, sort_keys=True, separators=(',', ':')).encode('utf-8')
    scenario_path = root / DEFAULT_SCENARIO_SUITE
    scenario_suite_sha256 = sha256_file(scenario_path) if scenario_path.is_file() else None
    return {
        'manifest_version': 1,
        'evaluator_root': str(root),
        'evaluator_sha256': hashlib.sha256(payload).hexdigest(),
        'scenario_suite_sha256': scenario_suite_sha256,
        'files': rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Compute the frozen evaluator identity for skill-benchmark.')
    parser.add_argument('--root', default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument('--path', action='append', dest='paths')
    parser.add_argument('--json', dest='json_output')
    args = parser.parse_args()
    try:
        report = identity(Path(args.root), args.paths or DEFAULT_EVALUATOR_PATHS)
        report['status'] = 'pass'
    except Exception as exc:
        report = {'status': 'fail', 'error': str(exc)}
    if args.json_output:
        dump_json(report, args.json_output)
    dump_json(report)
    return 0 if report['status'] == 'pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())
