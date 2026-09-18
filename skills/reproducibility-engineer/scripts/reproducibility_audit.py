#!/usr/bin/env python3
from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
import re
from pathlib import Path

from _common import dump_json, iter_files, markdown_local_links, parse_frontmatter


def any_match(text: str, patterns: list[str]) -> bool:
    low = text.lower()
    return any(p.lower() in low for p in patterns)


def main() -> int:
    ap = argparse.ArgumentParser(description='Static structural reproducibility audit for a skill package.')
    ap.add_argument('--target', required=True)
    ap.add_argument('--json', dest='json_out')
    args = ap.parse_args()

    root = Path(args.target).resolve()
    skill_md = root / 'SKILL.md'
    if not skill_md.is_file():
        dump_json({'status':'fail','target':str(root),'errors':['missing root SKILL.md']}, args.json_out)
        return 1

    skill_text = skill_md.read_text(encoding='utf-8', errors='replace')
    fm = parse_frontmatter(skill_md)
    all_text_parts = [skill_text]
    files = list(iter_files(root))
    for p in files:
        if not p.is_symlink() and p.suffix.lower() in {'.md', '.txt', '.json', '.yaml', '.yml'} and p.stat().st_size <= 512_000:
            try:
                all_text_parts.append(p.read_text(encoding='utf-8', errors='replace'))
            except OSError:
                pass
    corpus = '\n'.join(all_text_parts)

    dirs = {p.name for p in root.iterdir() if p.is_dir()}
    rels = [p.relative_to(root).as_posix() for p in files]
    has_scripts = 'scripts' in dirs and any(r.startswith('scripts/') for r in rels)
    has_evals = 'evals' in dirs and any(r.startswith('evals/') for r in rels)
    has_refs = 'references' in dirs and any(r.startswith('references/') for r in rels)
    has_assets = 'assets' in dirs and any(r.startswith('assets/') for r in rels)
    validator_files = [r for r in rels if re.search(r'(validate|validator|check|lint|test)', Path(r).name, re.I)]
    schema_files = [r for r in rels if re.search(r'(schema|contract)', Path(r).name, re.I)]
    package_files = [r for r in rels if re.search(r'(package|build).*(\.py|\.js|\.mjs|\.sh)$', Path(r).name, re.I)]

    signals = {
        'activation_description_present': bool(fm.get('description')) and ('to' + 'do') not in fm.get('description','').lower(),
        'explicit_modes_or_router': any_match(skill_text, ['## modes', 'mode selection', 'router', 'workflow decision']),
        'output_contract': any_match(skill_text, ['output contract', 'report structure', 'output format']),
        'stop_conditions': any_match(skill_text, ['stop conditions', 'stop condition', 'fail closed']),
        'progressive_loading': has_refs and any_match(skill_text, ['progressive', 'load only', 'read only', 'references/']),
        'scripts_present': has_scripts,
        'schema_or_contract_files': bool(schema_files),
        'validator_files': bool(validator_files),
        'machine_readable_diagnostics': any_match(corpus, ['json receipt', 'machine-readable', 'supported_fixes', 'supported fixes', 'diagnostic code']),
        'evals_present': has_evals,
        'regression_language': any_match(corpus, ['regression', 'golden', 'holdout']),
        'frozen_evaluator_language': any_match(corpus, ['freeze evaluator', 'frozen evaluator', 'evaluator hash', 'immutable baseline']),
        'before_after_comparison': any_match(corpus, ['before/after', 'before and after', 'baseline vs', 'old skill', 'candidate skill']),
        'repair_loop': any_match(corpus, ['repair loop', 'rerun', 'diagnostic', 'smallest fix', 'one causal']),
        'freeze_after_pass': any_match(corpus, ['freeze after pass', 'frozen candidate', 'never edit it afterward', 'do not make unvalidated']),
        'atomic_delivery': any_match(corpus, ['atomic delivery', 'atomically', 'last-good', 'last good']),
        'source_snapshot_integrity': any_match(corpus, ['snapshot_sources.py', 'source snapshot', 'exact source bytes', 'immutable source', 'pinned vcs']),
        'output_alias_preflight': any_match(corpus, ['output alias', 'target-alias', 'canonical output', 'canonicalize output', 'symbolic-link cycle']),
        'recovery_preservation': any_match(corpus, ['recovery path', 'rollback', 'preserve recovery', 'last-good', 'last good']),
        'durable_receipts': any_match(corpus, ['durable receipt', 'receipt_version', 'complete receipt', 'flush/fsync', 'fsync']),
        'hash_receipt': any_match(corpus, ['sha-256', 'sha256', 'hash receipt', 'artifact hash']),
        'package_builder': bool(package_files),
        'evidence_layer_separation': any_match(corpus, ['structural evidence', 'behavioral evidence', 'runtime evidence', 'perceptual evidence']),
        'version_or_migration_contract': any_match(corpus, ['schema_version', 'schema version', 'migration', 'compatibility']),
        'assets_present': has_assets,
    }

    r1 = all(signals[k] for k in ['activation_description_present','output_contract','stop_conditions'])
    r2 = r1 and signals['validator_files'] and (signals['scripts_present'] or signals['schema_or_contract_files'])
    r3 = r2 and signals['evals_present'] and signals['regression_language'] and signals['repair_loop']
    r4 = r3 and signals['freeze_after_pass'] and signals['package_builder'] and signals['evidence_layer_separation'] and (signals['atomic_delivery'] or signals['hash_receipt'])

    maturity = 'R0'
    if r1: maturity = 'R1'
    if r2: maturity = 'R2'
    if r3: maturity = 'R3'
    if r4: maturity = 'R4'

    gaps = []
    if not r1:
        gaps.append('Define activation/boundaries, output contract, and stop conditions.')
    if r1 and not r2:
        gaps.append('Move objective mechanics into scripts/schemas and add independent validators.')
    if r2 and not r3:
        gaps.append('Add executed scenario/regression coverage and diagnostic-driven repair rules.')
    if r3 and not r4:
        gaps.append('Add final freeze, package/delivery integrity, and evidence-layer separation.')
    if not signals['frozen_evaluator_language']:
        gaps.append('Freeze evaluator inputs before candidate mutation for trustworthy comparisons.')
    if not signals['before_after_comparison']:
        gaps.append('Use baseline-vs-candidate paired evaluation for improvement claims.')
    if not signals['version_or_migration_contract']:
        gaps.append('Add explicit version/migration rules when persistent formats or behavior can change incompatibly.')
    if signals['before_after_comparison'] and not signals['source_snapshot_integrity']:
        gaps.append('Capture exact material source bytes before comparison so mutable inputs cannot silently redefine evidence.')
    if signals['package_builder'] and not signals['output_alias_preflight']:
        gaps.append('Canonicalize package/receipt outputs and reject aliases with inputs or sibling targets before writing.')
    if signals['package_builder'] and not signals['recovery_preservation']:
        gaps.append('Preserve last-good outputs and explicit recovery locations when commit or rollback fails.')
    if signals['package_builder'] and not signals['durable_receipts']:
        gaps.append('Emit complete durable stage-aware receipts tied to the exact committed bytes.')

    broken_links = []
    for md in [p for p in files if not p.is_symlink() and p.suffix.lower() == '.md']:
        for target in markdown_local_links(md):
            candidate = (md.parent / target.split('#',1)[0]).resolve()
            try:
                candidate.relative_to(root)
            except ValueError:
                continue
            if not candidate.exists():
                broken_links.append({'source': md.relative_to(root).as_posix(), 'target': target})

    report = {
        'status': 'pass' if not broken_links else 'warn',
        'target': str(root),
        'evidence_type': 'structural-static-only',
        'structural_maturity': maturity,
        'maturity_definition': 'R0 instruction-only; R1 contract-bounded; R2 mechanically validated; R3 regression-controlled; R4 evidence-reproducible.',
        'signals': signals,
        'validator_files': validator_files,
        'schema_or_contract_files': schema_files,
        'package_files': package_files,
        'broken_local_links': broken_links,
        'recommended_next_controls': gaps,
        'limitations': [
            'This audit does not execute target behavior or prove output quality.',
            'Keyword/file signals can miss equivalent implementations with different naming.',
            'Reproducibility ceiling requires semantic review of the target domain.'
        ]
    }
    dump_json(report, args.json_out)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
