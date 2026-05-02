#!/usr/bin/env python3
"""Validate a JSON consistency audit report."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED_TOP = {'target_path', 'generated_at', 'inventory_summary', 'findings', 'score'}
REQUIRED_FINDING = {'id', 'severity', 'category', 'title', 'evidence', 'problem', 'repair', 'gate', 'confidence'}
VALID_SEVERITIES = {'blocker', 'high', 'medium', 'low'}


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except Exception as exc:
        return [f'invalid json: {exc}']
    missing = REQUIRED_TOP - set(data)
    if missing:
        errors.append(f'missing top-level fields: {sorted(missing)}')
    findings = data.get('findings')
    if not isinstance(findings, list):
        errors.append('findings must be a list')
        return errors
    ids = set()
    for i, item in enumerate(findings):
        if not isinstance(item, dict):
            errors.append(f'finding {i} is not an object')
            continue
        miss = REQUIRED_FINDING - set(item)
        if miss:
            errors.append(f'finding {i} missing fields: {sorted(miss)}')
        if item.get('severity') not in VALID_SEVERITIES:
            errors.append(f'finding {i} invalid severity: {item.get("severity")}')
        fid = item.get('id')
        if fid in ids:
            errors.append(f'duplicate finding id: {fid}')
        ids.add(fid)
    score = data.get('score', {})
    if not isinstance(score, dict) or 'score' not in score or 'status' not in score:
        errors.append('score must include score and status')
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description='Validate a consistency audit JSON report.')
    parser.add_argument('report')
    args = parser.parse_args()
    errors = validate(Path(args.report))
    if errors:
        for err in errors:
            print(f'ERROR: {err}')
        return 1
    print('[OK] consistency report is valid')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
