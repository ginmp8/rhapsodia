#!/usr/bin/env python3
"""Create a durable consistency receipt bound to candidate, verifier, policy, and evaluator identities."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from freeze_evaluators import verify as verify_evaluators  # noqa: E402
from inventory_skill import scan_target  # noqa: E402

RECEIPT_VERSION = 2
DEFAULT_VERIFIERS = (
    'scripts/inventory_skill.py',
    'scripts/consistency_audit.py',
    'scripts/validate_consistency_report.py',
    'scripts/create_consistency_receipt.py',
)
DEFAULT_POLICIES = (
    'SKILL.md',
    'references/consistency-taxonomy.md',
    'references/authority-and-conflict-resolution.md',
    'references/report-contract.md',
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    return hashlib.sha256(payload).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(data, dict):
        raise ValueError(f'expected JSON object: {path}')
    return data


def file_hash_map(inventory: dict[str, Any]) -> dict[str, str]:
    return {str(item['path']): str(item.get('sha256', '')) for item in inventory.get('files', []) if isinstance(item, dict) and item.get('path')}


def changed_files(before: dict[str, Any], after: dict[str, Any]) -> dict[str, list[str]]:
    old = file_hash_map(before)
    new = file_hash_map(after)
    return {
        'added': sorted(set(new) - set(old)),
        'removed': sorted(set(old) - set(new)),
        'changed': sorted(path for path in set(old) & set(new) if old[path] != new[path]),
    }


def identity_bundle(target: Path, paths: list[str], label: str) -> dict[str, Any]:
    records: list[dict[str, str]] = []
    for rel in sorted(set(paths)):
        path = (target / rel).resolve()
        try:
            path.relative_to(target)
        except ValueError as exc:
            raise ValueError(f'{label} path escapes target: {rel}') from exc
        if not path.is_file():
            raise FileNotFoundError(f'{label} file not found: {rel}')
        records.append({'path': rel, 'sha256': sha256_file(path)})
    return {'identity_sha256': canonical_hash(records), 'files': records}


def main() -> int:
    parser = argparse.ArgumentParser(description='Create a consistency-repair receipt tied to exact candidate, verifier, policy, and evaluator bytes.')
    parser.add_argument('--target', required=True)
    parser.add_argument('--baseline-inventory', required=True)
    parser.add_argument('--final-report', required=True)
    parser.add_argument('--evaluator-manifest', required=True)
    parser.add_argument('--mode', required=True)
    parser.add_argument('--status', choices=('pass', 'fail', 'blocked', 'partial'), required=True)
    parser.add_argument('--verifier-path', action='append', default=[], help='Additional package-relative verifier/policy implementation path.')
    parser.add_argument('--policy-path', action='append', default=[], help='Additional package-relative policy path.')
    parser.add_argument('--last-known-good')
    parser.add_argument('--out', required=True)
    args = parser.parse_args()

    try:
        target = Path(args.target).resolve()
        out = Path(args.out).resolve()
        try:
            out.relative_to(target)
            raise ValueError('receipt must be written outside the target package so it cannot mutate the frozen candidate')
        except ValueError as exc:
            if str(exc).startswith('receipt must'):
                raise

        baseline_path = Path(args.baseline_inventory).resolve()
        final_report_path = Path(args.final_report).resolve()
        evaluator_manifest_path = Path(args.evaluator_manifest).resolve()
        baseline = load_json(baseline_path)
        final_report = load_json(final_report_path)
        final_inventory = scan_target(target)

        final_identity = final_inventory.get('inventory_fingerprint')
        report_identity = final_report.get('inventory_identity')
        if report_identity != final_identity:
            raise ValueError(f'final report inventory identity {report_identity!r} does not match current candidate {final_identity!r}')

        evaluator_result = verify_evaluators(target, evaluator_manifest_path)
        if evaluator_result.get('status') != 'pass':
            raise ValueError(f'evaluator integrity failed: {evaluator_result}')

        verifier = identity_bundle(target, list(DEFAULT_VERIFIERS) + list(args.verifier_path), 'verifier')
        policies = identity_bundle(target, list(DEFAULT_POLICIES) + list(args.policy_path), 'policy')

        lkg = None
        if args.last_known_good:
            lkg_path = Path(args.last_known_good).resolve()
            if not lkg_path.exists():
                raise FileNotFoundError(f'last-known-good path does not exist: {lkg_path}')
            lkg = {'path': lkg_path.as_posix(), 'sha256': sha256_file(lkg_path) if lkg_path.is_file() else None}

        receipt = {
            'receipt_version': RECEIPT_VERSION,
            'status': args.status,
            'mode': args.mode,
            'target': target.as_posix(),
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'baseline_identity': baseline.get('inventory_fingerprint'),
            'candidate_identity': final_identity,
            'subject': {
                'name': final_inventory.get('frontmatter', {}).get('fields', {}).get('name') or target.name,
                'digest': {'sha256': final_identity},
                'digest_semantics': 'deterministic inventory fingerprint of the frozen candidate tree',
            },
            'verifier': verifier,
            'policies': policies,
            'changes': changed_files(baseline, final_inventory),
            'final_report': {'path': final_report_path.as_posix(), 'sha256': sha256_file(final_report_path)},
            'evaluator_manifest': {'path': evaluator_manifest_path.as_posix(), 'sha256': sha256_file(evaluator_manifest_path), 'verification': evaluator_result},
            'last_known_good': lkg,
            'claim_boundary': 'This receipt binds exact candidate/verifier/policy/evaluator identities and referenced validation evidence. It is not a cryptographic signature, provenance authority, or behavioral/semantic proof by itself.',
        }
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        print(json.dumps({'status': 'pass', 'receipt': out.as_posix(), 'candidate_identity': final_identity, 'verifier_identity': verifier['identity_sha256'], 'policy_identity': policies['identity_sha256']}, indent=2))
        return 0
    except Exception as exc:
        print(json.dumps({'status': 'fail', 'error': str(exc)}, indent=2))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
