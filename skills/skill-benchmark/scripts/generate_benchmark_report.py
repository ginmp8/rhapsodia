#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path

from _common import dump_json, extract_local_refs, path_is_inside, paths_alias, stage_bytes, transactional_commit, tree_hash, parse_frontmatter
from benchmark_identity import DEFAULT_EVALUATOR_PATHS, identity as evaluator_identity
from validate_portability import validate as validate_portability, normalize_hosts
from validate_scenario_results import load_json, validate_payload

SKILL_ROOT = Path(__file__).resolve().parents[1]


def list_files(root: Path, max_depth: int = 5) -> list[str]:
    rows: list[str] = []
    for path in sorted(root.rglob('*')):
        rel = path.relative_to(root)
        if any(part in {'.git', 'node_modules', '__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache'} for part in rel.parts):
            continue
        if len(rel.parts) > max_depth:
            continue
        rows.append(rel.as_posix() + ('/' if path.is_dir() else ''))
    return rows


def count_files(root: Path) -> int:
    return sum(1 for p in root.rglob('*') if p.is_file() and not any(part in {'.git', 'node_modules', '__pycache__'} for part in p.relative_to(root).parts)) if root.exists() else 0


def has_any(text: str, terms: list[str]) -> bool:
    lower = text.lower()
    return any(term in lower for term in terms)


def asset_integration(root: Path, corpus: str) -> tuple[str, list[str]]:
    assets_root = root / 'assets'
    if not assets_root.exists():
        return 'absent', []
    assets = [p for p in assets_root.rglob('*') if p.is_file()]
    if not assets:
        return 'absent', []
    lower = corpus.lower()
    unreferenced: list[str] = []
    for path in assets:
        rel = path.relative_to(root).as_posix()
        if rel == 'assets/icon.svg' and (root / 'agents' / 'openai.yaml').exists():
            continue
        if rel.lower() not in lower and path.name.lower() not in lower:
            unreferenced.append(rel)
    return ('integrated' if not unreferenced else 'partially integrated'), unreferenced



def has_scaffold_markers(root: Path) -> bool:
    patterns = [re.compile(r'\[TODO', re.I), re.compile(r'\bTODO\s*:', re.I), re.compile(r'replace with actual', re.I), re.compile(r'this is a placeholder', re.I)]
    for path in sorted(root.rglob('*')):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if any(part in {'.git', 'node_modules', '__pycache__'} for part in path.relative_to(root).parts):
            continue
        if rel.startswith('assets/templates/') or path.suffix.lower() not in {'.md', '.py', '.js', '.json', '.yaml', '.yml', '.txt'}:
            continue
        text = path.read_text(encoding='utf-8', errors='replace')
        for line in text.splitlines():
            if 're.compile' in line or 're.search' in line or 'SCAFFOLD' in line:
                continue
            if any(pattern.search(line) for pattern in patterns):
                return True
    return False

def static_score(root: Path, skill_text: str, fm: dict[str, str], portability: dict) -> tuple[dict[str, int], list[dict], dict]:
    body = skill_text.split('\n---\n', 1)[-1] if '\n---\n' in skill_text else skill_text
    lower = body.lower()
    description = fm.get('description', '')
    refs = extract_local_refs(skill_text)
    missing_refs = [ref for ref in refs if Path(ref).is_absolute() or '..' in Path(ref).parts or not (root / ref).exists()]
    reference_count = count_files(root / 'references')
    script_count = count_files(root / 'scripts')
    asset_count = count_files(root / 'assets')
    eval_count = count_files(root / 'evals')
    corpus_parts = [skill_text]
    for folder in ('references', 'scripts', 'examples', 'evals'):
        base = root / folder
        if not base.exists():
            continue
        for path in base.rglob('*'):
            if path.is_file() and path.suffix.lower() in {'.md', '.py', '.js', '.json', '.yaml', '.yml', '.txt', '.template'}:
                corpus_parts.append(path.read_text(encoding='utf-8', errors='replace'))
    corpus = '\n'.join(corpus_parts)
    asset_status, unreferenced_assets = asset_integration(root, corpus)
    line_count = len(skill_text.splitlines())
    scaffold = has_scaffold_markers(root)

    desc_trigger = has_any(description, ['use when', 'when asked', 'quando', 'use for', 'trigger'])
    desc_exclusion = has_any(description, ['do not use', 'não use', 'except', 'unless'])
    clear_scope = has_any(lower, ['purpose', 'scope', 'boundar', 'non-goal', 'do not use', 'mission'])
    ordered_workflow = bool(re.search(r'(?m)^\s*(?:\d+\.|[-*]\s+\*\*[^*]+\*\*)', body)) and has_any(lower, ['workflow', 'process', 'steps', 'sequence', 'mode'])
    validation = has_any(lower, ['validation', 'validate', 'acceptance', 'gate', 'test', 'check'])
    stop_conditions = has_any(lower, ['stop condition', 'stop before', 'failure', 'blocked', 'cannot'])
    output_contract = has_any(lower, ['output contract', 'report must', 'output', 'deliverable', 'format'])
    examples_or_templates = has_any(lower, ['example', 'scenario', 'template']) or (root / 'assets' / 'templates').exists()
    progressive = reference_count > 0 and has_any(lower, ['progressive', 'load only', 'references/'])
    validators_present = any('validate' in p.name.lower() for p in (root / 'scripts').glob('*')) if (root / 'scripts').exists() else False
    portable_core = bool(portability.get('portable_core'))

    scope = min(15, (5 if len(description) >= 80 else 2) + (4 if clear_scope else 1) + (3 if desc_exclusion else 1) + (3 if fm.get('name') else 0))
    trigger = min(15, (7 if desc_trigger else 2) + (3 if 100 <= len(description) <= 1024 else 1) + (3 if desc_exclusion else 1) + (2 if len(description.split()) >= 20 else 0))
    workflow = min(15, (7 if ordered_workflow else 3) + (4 if validation else 1) + (4 if stop_conditions else 1))
    output = min(15, (7 if output_contract else 2) + (4 if examples_or_templates else 1) + (4 if has_any(lower, ['evidence', 'quality', 'criteria', 'acceptance']) else 1))
    if missing_refs:
        resources = 3
    elif asset_status == 'partially integrated':
        resources = 7
    elif reference_count + script_count + asset_count + eval_count == 0:
        resources = 8
    else:
        resources = 10
    validation_score = min(10, (4 if validation else 1) + (3 if validators_present or eval_count else 0) + (3 if stop_conditions else 1))
    context = min(10, (4 if line_count <= 500 else 1) + (3 if progressive or line_count <= 180 else 1) + (3 if not scaffold else 0))
    maintainability = min(10, (2 if fm.get('name') and fm.get('description') else 0) + (2 if not missing_refs else 0) + (2 if portable_core else 0) + (2 if not scaffold else 0) + (2 if validation or validators_present else 0))

    scores = {
        'scope': scope,
        'trigger': trigger,
        'workflow': workflow,
        'output': output,
        'resources': resources,
        'validation': validation_score,
        'context': context,
        'maintainability': maintainability,
    }
    gates = [
        {'gate': 'Valid SKILL.md exists', 'status': 'pass' if (root / 'SKILL.md').is_file() else 'fail', 'evidence': 'root SKILL.md', 'blocker': True},
        {'gate': 'Frontmatter has name and description', 'status': 'pass' if fm.get('name') and fm.get('description') else 'fail', 'evidence': 'parsed frontmatter', 'blocker': True},
        {'gate': 'Description is specific and actionable', 'status': 'pass' if trigger >= 10 else 'warn', 'evidence': f'{len(description)} characters', 'blocker': False},
        {'gate': 'Scope is clear', 'status': 'pass' if scope >= 10 else 'warn', 'evidence': 'static scope heuristic', 'blocker': False},
        {'gate': 'Expected input is clear', 'status': 'pass' if has_any(lower, ['input', 'target', 'path', 'source']) else 'warn', 'evidence': 'input/target guidance scan', 'blocker': False},
        {'gate': 'Expected output is clear', 'status': 'pass' if output_contract else 'fail', 'evidence': 'output contract scan', 'blocker': True},
        {'gate': 'No unresolved scaffold markers', 'status': 'pass' if not scaffold else 'fail', 'evidence': 'package text scan', 'blocker': True},
        {'gate': 'No material contradictions', 'status': 'review', 'evidence': 'requires qualitative semantic review', 'blocker': False},
        {'gate': 'Referenced local resources exist', 'status': 'pass' if not missing_refs else 'fail', 'evidence': f'checked_refs={len(refs)} missing={len(missing_refs)}', 'blocker': True},
        {'gate': 'Resources are useful and referenced correctly', 'status': 'pass' if asset_status in {'absent', 'integrated'} and not missing_refs else 'warn', 'evidence': f'assets={asset_status}, unreferenced_assets={len(unreferenced_assets)}', 'blocker': False},
        {'gate': 'Quality criteria or validation exists', 'status': 'pass' if validation or validators_present else 'warn', 'evidence': 'validation/test/gate scan', 'blocker': False},
        {'gate': 'Portable core is host-neutral', 'status': 'pass' if portable_core else 'fail', 'evidence': 'portable-core structural validation', 'blocker': True},
        {'gate': 'No volatile data hardcoded as stable knowledge', 'status': 'review', 'evidence': 'requires qualitative review', 'blocker': False},
        {'gate': 'Structure is maintainable', 'status': 'pass' if maintainability >= 7 else 'warn', 'evidence': 'static maintainability heuristic', 'blocker': False},
    ]
    inventory = {
        'line_count': line_count,
        'description_chars': len(description),
        'references': reference_count,
        'scripts': script_count,
        'assets': asset_count,
        'evals': eval_count,
        'asset_status': asset_status,
        'unreferenced_assets': unreferenced_assets,
        'local_refs': refs,
        'missing_local_refs': missing_refs,
        'openai_adapter': (root / 'agents' / 'openai.yaml').exists(),
    }
    return scores, gates, inventory


def metric_pct(num: int, den: int) -> str:
    return 'not measured' if den == 0 else f'{100.0 * num / den:.1f}%'


def behavioral_metrics(validation: dict | None) -> tuple[list[tuple[str, str, str, str]], list[dict]]:
    if not validation or validation.get('status') != 'pass':
        rows = [('Activation precision', 'not measured', 'planned', 'No valid executed/supplied scenario results'), ('Activation recall', 'not measured', 'planned', 'No valid executed/supplied scenario results'), ('Output conformance', 'not measured', 'planned', 'No valid executed/supplied scenario results'), ('Criteria coverage', 'not measured', 'planned', 'No criteria-level evidence supplied'), ('Robustness', 'not measured', 'planned', 'No edge-case execution evidence'), ('Rework rate', 'not measured', 'planned', 'No valid rework evidence')]
        return rows, []
    scenarios = validation['rows']
    complete = [r for r in scenarios if isinstance(r, dict) and r.get('actual_activation') is not None and r.get('output_conforms') is not None and r.get('needs_rework') is not None]
    expected_yes = [r for r in complete if r.get('expected_activation') is True]
    actual_yes = [r for r in complete if r.get('actual_activation') is True]
    true_positive = [r for r in actual_yes if r.get('expected_activation') is True]
    conforming = [r for r in complete if r.get('output_conforms') is True]
    edges = [r for r in complete if r.get('category') == 'edge_case']
    robust_edges = [r for r in edges if r.get('output_conforms') is True and r.get('needs_rework') is False]
    rework = [r for r in complete if r.get('needs_rework') is True]
    status = 'measured' if validation.get('metadata', {}).get('evidence_origin') == 'executed' and validation.get('provenance_status') == 'pinned' else 'supplied'
    notes = 'Identity-bound scenario evidence' if validation.get('provenance_status') == 'pinned' else 'Valid but unpinned scenario evidence; do not use for strict version deltas'
    metrics = [
        ('Activation precision', metric_pct(len(true_positive), len(actual_yes)), status, notes),
        ('Activation recall', metric_pct(len(true_positive), len(expected_yes)), status, notes),
        ('Output conformance', metric_pct(len(conforming), len(complete)), status, notes),
        ('Criteria coverage', 'not measured', 'planned', 'No criteria-level result field in portable schema'),
        ('Robustness', metric_pct(len(robust_edges), len(edges)), status, notes),
        ('Rework rate', metric_pct(len(rework), len(complete)), status, notes),
    ]
    return metrics, scenarios


def planned_scenarios() -> list[dict]:
    path = SKILL_ROOT / 'evals' / 'activation-scenarios.json'
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
        return [row for row in data.get('scenarios', []) if row.get('category') in {'should_activate', 'should_not_activate', 'ambiguous', 'edge_case'}]
    except Exception:
        return []


def make_report(target: Path, report_path: Path, results_path: Path | None, source_manifest: Path | None, hosts: list[str]) -> tuple[str, dict]:
    skill_md = target / 'SKILL.md'
    if not skill_md.is_file():
        raise ValueError('target lacks root SKILL.md')
    skill_text = skill_md.read_text(encoding='utf-8', errors='replace')
    fm, fm_errors = parse_frontmatter(skill_md)
    if fm_errors or not fm.get('name') or not fm.get('description'):
        raise ValueError('invalid SKILL.md frontmatter: ' + '; '.join(fm_errors or ['name/description missing']))

    portability = validate_portability(target, hosts)
    scores, gates, inventory = static_score(target, skill_text, fm, portability)
    total = sum(scores.values())
    blocker_fail = any(g['status'] == 'fail' and g['blocker'] for g in gates)
    review_pending = any(g['status'] == 'review' for g in gates)
    if blocker_fail or total < 70:
        verdict = 'reject'
    elif total >= 85 and not review_pending:
        verdict = 'approve'
    else:
        verdict = 'approve with reservations'
    maturity = 'reference-grade skill' if total >= 90 else 'mature skill' if total >= 85 else 'developing skill' if total >= 70 else 'immature skill'

    target_hash = tree_hash(target, reject_symlinks=True)
    source_path = str(target)
    source_status = 'live-unfrozen'
    manifest_data = None
    if source_manifest:
        manifest_data = json.loads(source_manifest.read_text(encoding='utf-8'))
        if manifest_data.get('snapshot_root') != str(target.resolve()):
            raise ValueError('source manifest snapshot_root does not match benchmark target')
        if manifest_data.get('source_tree_sha256') != target_hash:
            raise ValueError('source manifest hash does not match benchmark target bytes')
        source_path = manifest_data.get('source_root', source_path)
        source_status = 'frozen-snapshot'

    evaluator = evaluator_identity(SKILL_ROOT, DEFAULT_EVALUATOR_PATHS)
    results_validation = None
    if results_path:
        results_validation = validate_payload(load_json(results_path))
        if results_validation['status'] != 'pass':
            raise ValueError('scenario results validation failed: ' + '; '.join(results_validation['errors']))
        meta = results_validation.get('metadata', {})
        if meta.get('target_identity_sha256') and meta.get('target_identity_sha256') != target_hash:
            raise ValueError('scenario results target_identity_sha256 does not match benchmark target')
        if meta.get('evaluator_identity_sha256') and meta.get('evaluator_identity_sha256') != evaluator['evaluator_sha256']:
            raise ValueError('scenario results evaluator_identity_sha256 does not match current evaluator')
        if meta.get('scenario_suite_sha256') and meta.get('scenario_suite_sha256') != evaluator.get('scenario_suite_sha256'):
            raise ValueError('scenario results scenario_suite_sha256 does not match current scenario suite')

    metrics, supplied_scenarios = behavioral_metrics(results_validation)
    scenario_source = supplied_scenarios or planned_scenarios()
    by_category = {category: [row for row in scenario_source if row.get('category') == category] for category in ('should_activate', 'should_not_activate', 'ambiguous', 'edge_case')}

    gate_rows = '\n'.join(f"| {g['gate']} | {g['status']} | {g['evidence']} | {'fix before approval' if g['status']=='fail' else 'review' if g['status']=='review' else 'none'} |" for g in gates)
    tree = '\n'.join(list_files(target)) or '(empty)'
    score_rows = [
        ('Scope and specialization', 15, scores['scope'], 'name, description, boundaries', 'tighten boundaries/non-goals'),
        ('Trigger description', 15, scores['trigger'], f"{inventory['description_chars']} character description", 'add concrete triggers/exclusions'),
        ('Execution workflow', 15, scores['workflow'], 'workflow/validation/stop markers', 'make ordering and failure handling explicit'),
        ('Output quality', 15, scores['output'], 'output contract/templates/evidence markers', 'tighten output acceptance'),
        ('Supporting resources', 10, scores['resources'], f"refs={inventory['references']} scripts={inventory['scripts']} assets={inventory['assets']} asset_status={inventory['asset_status']}", 'integrate useful resources; remove only obsolete scaffold'),
        ('Validation and acceptance criteria', 10, scores['validation'], 'validators/evals/stop rules', 'add deterministic gates where useful'),
        ('Context efficiency', 10, scores['context'], f"{inventory['line_count']} SKILL.md lines", 'move branch detail to shallow references'),
        ('Maintainability', 10, scores['maintainability'], f"portable_core={portability.get('portable_core')}", 'keep host adapters optional and test update path'),
    ]
    score_table = '\n'.join(f'| {name} | {weight} | {score} | {evidence} | {improvement} |' for name, weight, score, evidence, improvement in score_rows)
    metric_table = '\n'.join(f'| {name} | {value} | {status} | {notes} |' for name, value, status, notes in metrics)

    def scenario_table(category: str, decision: str) -> str:
        rows = by_category.get(category, [])[:10]
        if not rows:
            return '| - | No scenario available | missing evidence | blocked |'
        lines = []
        for row in rows:
            rid = row.get('id', '-')
            prompt = str(row.get('prompt', '')).replace('|', '\\|')
            if category == 'ambiguous':
                expected = 'clarify or proceed only with explicit assumptions'
            elif category == 'edge_case':
                expected = 'fail safely without fabricated evidence'
            elif category == 'should_activate':
                expected = 'skill should activate'
            else:
                expected = 'skill should not activate'
            status = 'supplied' if supplied_scenarios else 'planned'
            lines.append(f'| {rid} | {prompt} | {expected} | {status} |')
        return '\n'.join(lines)

    behavioral_state = 'measured/supplied' if results_validation else 'not measured; planned only'
    failed_gates = [g['gate'] for g in gates if g['status'] == 'fail']
    missing_evidence = ['semantic contradiction review', 'volatile/stale knowledge review']
    if not results_validation:
        missing_evidence.append('executed or supplied behavioral scenario results')
    if source_status != 'frozen-snapshot':
        missing_evidence.append('frozen target snapshot identity')

    report = f'''# Skill Benchmark: {fm['name']}

## 1. Executive summary

- Target skill: `{fm['name']}`
- Target source: `{source_path}`
- Benchmark date: `{date.today().isoformat()}`
- Report path: `{report_path}`
- Overall score: `{total}/100`
- Maturity classification: `{maturity}`
- Verdict: `{verdict}`
- Evidence state: `{source_status}`

Static scoring is evidence-backed but does not prove runtime behavior. Behavioral metrics are `{behavioral_state}`. Semantic review items remain explicit rather than being auto-passed.

## 2. Scorecard

| Dimension | Weight | Score | Evidence | Main improvement |
|---|---:|---:|---|---|
{score_table}
| **Total** | **100** | **{total}** |  |  |

## 3. Gate evaluation

| Gate | Status | Evidence | Required action |
|---|---|---|---|
{gate_rows}

## 4. Static structure inventory

```text
{tree}
```

- `SKILL.md` lines: `{inventory['line_count']}`
- Description length: `{inventory['description_chars']}` characters
- References: `{inventory['references']}` files
- Scripts: `{inventory['scripts']}` files
- Assets: `{inventory['assets']}` files
- Evals: `{inventory['evals']}` files
- Asset integration status: `{inventory['asset_status']}`
- Missing local references: `{', '.join(inventory['missing_local_refs']) if inventory['missing_local_refs'] else 'none'}`
- OpenAI adapter: `{'present (optional)' if inventory['openai_adapter'] else 'absent'}`
- Portable core: `{portability.get('portable_core')}`

## 5. Behavioral metrics

| Metric | Result | Status | Notes |
|---|---:|---|---|
{metric_table}

## 6. Scenario suite

### 6.1 Should activate

| ID | Prompt | Expected result | Status |
|---|---|---|---|
{scenario_table('should_activate', 'activate')}

### 6.2 Should not activate

| ID | Prompt | Expected result | Status |
|---|---|---|---|
{scenario_table('should_not_activate', 'nonactivate')}

### 6.3 Ambiguous prompts

| ID | Prompt | Expected decision rule | Status |
|---|---|---|---|
{scenario_table('ambiguous', 'clarify')}

### 6.4 Edge cases

| ID | Prompt | Expected behavior | Status |
|---|---|---|---|
{scenario_table('edge_case', 'safe-fail')}

## 7. Evidence-based findings

### Strengths

1. Static evidence is bound to target hash `{target_hash}`.
2. Evaluator identity is `{evaluator['evaluator_sha256']}`.
3. Host-specific adapters do not contribute bonus points to the portable-core score.

### Weaknesses

1. Failed gates: `{', '.join(failed_gates) if failed_gates else 'none'}`.
2. Static inspection cannot independently prove semantic consistency or runtime activation quality.
3. Version deltas are trustworthy only when target/evaluator/scenario identities are comparable.

### Missing evidence

{chr(10).join(f'{i+1}. {item}' for i, item in enumerate(missing_evidence))}

## 8. Top prioritized improvements

| Priority | Improvement | Impact | Effort | Owner action |
|---:|---|---|---|---|
| 1 | Fix blocker gates | high | variable | Repair only evidence-backed failures |
| 2 | Execute identity-bound scenario suite | high | medium | Record target/evaluator hashes with results |
| 3 | Complete semantic contradiction/staleness review | high | low-medium | Record inspected evidence and judgment |
| 4 | Tighten activation description where trigger score is weak | medium | low | Add concrete trigger/exclusion language |
| 5 | Preserve portable core and isolate host adapters | medium | low | Keep host-only metadata optional |

## 9. Risks if used as-is

| Risk | Severity | Why it matters | Mitigation |
|---|---|---|---|
| False confidence from static-only scoring | medium | Static markers do not prove runtime behavior | Execute scenario suite |
| Non-comparable version deltas | high | Different evaluator or scenario identity invalidates delta claims | Freeze evaluator and scenario inputs |
| Mutable-source drift | high | Live files can change after inspection | Benchmark an immutable snapshot |
| Host-specific coupling | medium | A skill may work on one host but fail elsewhere | Validate portable core and requested host profiles |

## 10. Suggested improved description

```yaml
description: {fm['description']}
```

Retain the current description when it already states task, trigger contexts, artifacts, and exclusions; otherwise refine it without adding host-private invocation syntax.

## 11. Suggested ideal file structure

```text
{fm['name']}/
  SKILL.md
  references/          # optional portable guidance
  scripts/             # optional self-contained helpers
  assets/              # optional templates/resources
  evals/               # optional planned scenarios
  agents/
    openai.yaml         # optional OpenAI adapter; not required by portable core
```

## 12. Verdict

`{verdict}`

Minimum next action: resolve blocker gates and missing evidence before making stronger readiness claims.

## 13. Benchmark metadata

- Benchmark method: `{'static + behavioral evidence' if results_validation else 'static'}`
- Evidence sources: `{source_path}`
- Source evidence state: `{source_status}`
- Target tree SHA-256: `{target_hash}`
- Evaluator SHA-256: `{evaluator['evaluator_sha256']}`
- Scenario suite SHA-256: `{evaluator.get('scenario_suite_sha256') or 'not-available'}`
- Scenario provenance: `{results_validation.get('provenance_status') if results_validation else 'planned-only'}`
- Requested host profiles: `{', '.join(hosts)}`
- Portable-core validation: `{portability.get('status')}`
- Generated by: `skill-benchmark`
- Last updated: `{date.today().isoformat()}`
'''
    receipt = {
        'receipt_version': 2,
        'status': 'pass',
        'stage': 'generated',
        'target_name': fm['name'],
        'target_source': source_path,
        'source_evidence_state': source_status,
        'target_identity_sha256': target_hash,
        'evaluator_identity_sha256': evaluator['evaluator_sha256'],
        'scenario_suite_sha256': evaluator.get('scenario_suite_sha256'),
        'scenario_provenance': results_validation.get('provenance_status') if results_validation else 'planned-only',
        'score': total,
        'verdict': verdict,
        'portable_core': portability.get('portable_core'),
        'requested_hosts': hosts,
        'report_path': str(report_path),
    }
    return report, receipt


def main() -> int:
    parser = argparse.ArgumentParser(description='Generate a portable, identity-bound skill benchmark report.')
    parser.add_argument('--target', required=True)
    parser.add_argument('--out', help='Output directory or explicit .md report path. Defaults outside the target.')
    parser.add_argument('--results', help='Optional validated scenario results JSON.')
    parser.add_argument('--source-manifest', help='Optional snapshot manifest from snapshot_target.py.')
    parser.add_argument('--hosts', default='portable-core', help='portable-core,openai,claude,copilot,cursor,all')
    parser.add_argument('--json-output', help='Optional success receipt JSON path; defaults beside report.')
    args = parser.parse_args()

    try:
        target = Path(args.target).expanduser().resolve(strict=True)
        if not target.is_dir():
            raise ValueError(f'target is not a directory: {target}')
        fm, _ = parse_frontmatter(target / 'SKILL.md') if (target / 'SKILL.md').is_file() else ({}, [])
        name = fm.get('name') or target.name
        if args.out:
            authored = Path(args.out).expanduser()
            report_path = authored if authored.suffix.lower() == '.md' else authored / name / 'skill-benchmark.md'
        else:
            report_path = target.parent / 'benchmark-output' / name / 'skill-benchmark.md'
        report_path = report_path.resolve(strict=False)
        receipt_path = Path(args.json_output).expanduser().resolve(strict=False) if args.json_output else report_path.with_suffix('.receipt.json')
        if path_is_inside(target, report_path) or path_is_inside(target, receipt_path):
            raise ValueError('report/receipt outputs must be outside the benchmark target')
        if paths_alias(report_path, receipt_path):
            raise ValueError('report and receipt outputs must not alias each other')
        if Path(args.results).resolve(strict=True) in {report_path, receipt_path} if args.results else False:
            raise ValueError('output must not alias scenario results input')

        hosts = normalize_hosts(args.hosts)
        report, receipt = make_report(target, report_path, Path(args.results).resolve(strict=True) if args.results else None, Path(args.source_manifest).resolve(strict=True) if args.source_manifest else None, hosts)
        report_bytes = report.encode('utf-8')
        receipt['report_sha256'] = __import__('hashlib').sha256(report_bytes).hexdigest()
        report_stage = stage_bytes(report_path, report_bytes)
        receipt_stage = stage_bytes(receipt_path, (json.dumps(receipt, indent=2, ensure_ascii=False) + '\n').encode('utf-8'))
        try:
            transactional_commit([(report_stage, report_path), (receipt_stage, receipt_path)])
        finally:
            report_stage.unlink(missing_ok=True)
            receipt_stage.unlink(missing_ok=True)
        dump_json(receipt)
        return 0
    except Exception as exc:
        dump_json({'receipt_version': 2, 'status': 'fail', 'stage': 'generate', 'error': str(exc), 'last_good_preserved_on_failure': True})
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
