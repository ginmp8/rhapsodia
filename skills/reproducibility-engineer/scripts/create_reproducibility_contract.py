#!/usr/bin/env python3
from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
import json
from pathlib import Path

from _common import dump_json, parse_frontmatter, sha256_file


def main() -> int:
    ap = argparse.ArgumentParser(description='Create a reproducibility-contract scaffold from a target and optional audit.')
    ap.add_argument('--target', required=True)
    ap.add_argument('--audit')
    ap.add_argument('--out', required=True)
    args = ap.parse_args()

    root = Path(args.target).resolve()
    skill_md = root / 'SKILL.md'
    if not skill_md.is_file():
        print('missing root SKILL.md')
        return 1
    fm = parse_frontmatter(skill_md)
    audit = {}
    if args.audit:
        audit = json.loads(Path(args.audit).read_text(encoding='utf-8'))

    contract = {
        'contract_version': 2,
        'target': {
            'name': fm.get('name', root.name),
            'path': str(root),
            'baseline_identity': sha256_file(skill_md),
        },
        'ceiling': 'unclassified',
        'protected_paths': [],
        'hard_gates': [
            'target-package-valid',
            'frozen-evaluator-unchanged',
            'no-blocking-regression'
        ],
        'variability': [],
        'evaluators': [],
        'scenario_groups': ['activation','non-activation','ambiguous','core','edge','regression','adversarial','holdout'],
        'acceptance': {
            'behavioral_improvement_required_for_improvement_claim': True,
            'freeze_after_pass': True,
            'stagnation_limit': 2,
            'weaken_hard_gates_to_pass': False
        },
        'source_integrity': {
            'snapshot_material_evidence_before_analysis': True,
            'immutable_pinned_vcs_reads_when_supported': True,
            'reject_source_alias_escape': True,
            'rebaseline_if_source_identity_changes': True
        },
        'self_hosting': {
            'enabled': False,
            'generation_id': '',
            'controller_identity': '',
            'baseline_identity': '',
            'candidate_identity': '',
            'max_self_recursion_depth': 1,
            'controller_read_only': True,
            'evaluator_outside_candidate_surface': True,
            'promotion_external_to_candidate': True,
            'last_known_good_identity': ''
        },
        'delivery': {
            'atomic_when_applicable': True,
            'hash_receipt_when_useful': True,
            'package_exact_frozen_candidate': True,
            'reject_output_aliases_before_write': True,
            'preserve_last_good_on_failure': True,
            'preserve_recovery_on_rollback_failure': True,
            'durable_complete_receipts': True
        },
        'baseline_structural_maturity': audit.get('structural_maturity'),
        'notes': ['Classify ceiling and fill variability/evaluators before material mutation.']
    }
    dump_json(contract, args.out)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
