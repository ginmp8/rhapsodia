#!/usr/bin/env python3
"""Validate the skill-improver package contract."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

TEXT_EXTS = {
    '.md', '.txt', '.yaml', '.yml', '.json', '.template'
}

REQUIRED_FILES = [
    'SKILL.md',
    'references/autoresearch-adaptation.md',
    'references/benchmark-integration.md',
    'references/evaluation-contract.md',
    'references/hypothesis-catalog.md',
    'references/harness-design.md',
    'references/report-template.md',
    'references/execution-runbook.md',
    'examples/sample-run.md',
    'examples/eval_skill.py',
    'scripts/skill_improver_loop.py',
    'scripts/static_skill_score.py',
    'scripts/validate_skill_improver_package.py',
    'scripts/package_skill.py',
    'evals/activation-scenarios.json',
    'assets/templates/improvement-run-report.md.template',
    'assets/templates/patch-decision-record.md.template',
    'references/evolution-candidate-execution.md',
    'assets/templates/generation-receipt.json.template',
    'scripts/validate_candidate_request.py',
    'scripts/validate_generation_receipt.py',
    'contracts/integration-manifest.json',
]

REQUIRED_CATEGORIES = {
    'should_activate': 5,
    'should_not_activate': 5,
    'ambiguous': 5,
    'edge_case': 5,
    'regression': 5,
}

REFERENCE_PATTERN = re.compile(
    r'`([^`]+\.(?:md|py|json|yaml|yml|template|sh|js))`|'
    r'\(([^)]+\.(?:md|py|json|yaml|yml|template|sh|js))\)'
)


def read_text(path: Path) -> str:
    return path.read_text(encoding='utf-8', errors='replace')


def parse_frontmatter(text: str) -> dict[str, str]:
    match = re.match(r'^---\n(.*?)\n---', text, re.DOTALL)
    if not match:
        return {}
    data: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ':' in line:
            key, value = line.split(':', 1)
            data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def referenced_paths(root: Path) -> list[str]:
    refs: set[str] = set()
    root_resolved = root.resolve()

    for path in sorted(root.rglob('*')):
        if not path.is_file() or path.suffix.lower() not in TEXT_EXTS:
            continue
        rel_dir = path.parent.relative_to(root)
        text = read_text(path)
        for match in REFERENCE_PATTERN.finditer(text):
            raw = match.group(1) or match.group(2) or ''
            if raw.startswith(('http://', 'https://', '/', '#')):
                continue
            if '*' in raw:
                continue
            clean = raw.lstrip('./')
            if clean.startswith('.skill-improver/'):
                continue

            direct = root / clean
            if direct.exists():
                refs.add(clean)
                continue

            sibling = (root / rel_dir / clean).resolve()
            try:
                sibling.relative_to(root_resolved)
            except ValueError:
                pass
            else:
                if sibling.exists():
                    refs.add(sibling.relative_to(root).as_posix())
                    continue

            refs.add(clean)
    return sorted(refs)


def find_placeholder_markers(root: Path) -> list[str]:
    token = 'TO' + 'DO'
    markers = [
        f'[{token}',
        f'{token}:',
        'T' + 'BD:',
        'FIX' + 'ME',
        'REPLACE' + '_ME',
    ]
    hits: list[str] = []
    for path in sorted(root.rglob('*')):
        if not path.is_file() or path.suffix.lower() not in TEXT_EXTS:
            continue
        for lineno, line in enumerate(read_text(path).splitlines(), 1):
            if any(marker in line for marker in markers):
                hits.append(f'{path.relative_to(root)}:{lineno}')
    return hits


def validate_scenarios(path: Path) -> tuple[dict[str, int], list[str]]:
    errors: list[str] = []
    try:
        payload = json.loads(read_text(path))
    except Exception as exc:
        return {}, [f'scenario JSON could not be parsed: {exc}']

    if not isinstance(payload, dict):
        return {}, ['scenario file must contain an object']
    if payload.get('target_skill') != 'skill-improver':
        errors.append('scenario target_skill must be skill-improver')
    if payload.get('status') not in {'planned', 'measured'}:
        errors.append('scenario suite status must be planned or measured')
    data = payload.get('scenarios')
    if not isinstance(data, list):
        return {}, errors + ['scenario file must contain a scenarios list']

    counts = {name: 0 for name in REQUIRED_CATEGORIES}
    ids: set[str] = set()
    required_fields = ['id', 'type', 'prompt', 'expected_behavior', 'acceptance_criteria']

    for idx, item in enumerate(data):
        if not isinstance(item, dict):
            errors.append(f'scenario at index {idx} is not an object')
            continue
        for field in required_fields:
            if field not in item or item[field] in (None, '', []):
                errors.append(f'scenario {idx} missing {field}')
        sid = str(item.get('id', ''))
        if sid in ids:
            errors.append(f'duplicate scenario id {sid}')
        ids.add(sid)
        category = item.get('type')
        if category in counts:
            counts[category] += 1
        else:
            errors.append(f'scenario {sid or idx} has unknown type {category}')
        criteria = item.get('acceptance_criteria')
        if not isinstance(criteria, list) or not criteria or any(not isinstance(x, str) or not x.strip() for x in criteria):
            errors.append(f'scenario {sid or idx} has invalid acceptance_criteria')

    for category, minimum in REQUIRED_CATEGORIES.items():
        if counts.get(category, 0) < minimum:
            errors.append(f'category {category} has {counts.get(category, 0)} scenarios, expected at least {minimum}')
    return counts, errors


def validate_python_scripts(root: Path) -> list[str]:
    errors: list[str] = []
    for script in sorted((root / 'scripts').glob('*.py')):
        try:
            compile(read_text(script), str(script), 'exec')
        except Exception as exc:
            errors.append(f'{script.relative_to(root)}: {exc}')
    return errors

def validate_command_evaluator_examples(root: Path) -> list[str]:
    """Validate concrete package-owned command-evaluator examples.

    A command evaluator runs with the target skill as cwd, while benchmark-lock
    paths are resolved from the git root. Concrete package-owned examples must
    therefore use one absolute package-root placeholder for both surfaces so
    the executed evaluator and frozen evaluator identity cannot diverge.
    """
    errors: list[str] = []
    fence_pattern = re.compile(r'```(?:text|bash|sh)?\n(.*?)```', re.DOTALL)
    eval_pattern = re.compile(r"--eval-command\s+(['\"])(.*?)\1", re.DOTALL)
    lock_pattern = re.compile(r"--benchmark-lock-path\s+([^\s\\]+)")
    python_path_pattern = re.compile(r'(?P<path><SKILL_IMPROVER_ROOT>/[^\s\"\']+\.py|(?:\.{0,2}/)[^\s\"\']+\.py)')
    package_prefix = '<SKILL_IMPROVER_ROOT>/'

    for doc in [root / 'examples' / 'sample-run.md', root / 'references' / 'execution-runbook.md']:
        if not doc.is_file():
            continue
        for index, block_match in enumerate(fence_pattern.finditer(read_text(doc)), 1):
            block = block_match.group(1)
            if '--evaluator command' not in block or '--eval-command' not in block:
                continue

            eval_match = eval_pattern.search(block)
            if not eval_match:
                continue
            eval_command = eval_match.group(2)
            path_match = python_path_pattern.search(eval_command)
            if not path_match:
                # Generic placeholders such as <EVALUATOR COMMAND> are allowed.
                continue

            evaluator_path = path_match.group('path')
            lock_match = lock_pattern.search(block)
            subject = f'{doc.relative_to(root)} fenced command #{index}'
            if not lock_match:
                errors.append(f'{subject}: concrete evaluator example is missing --benchmark-lock-path')
                continue
            lock_path = lock_match.group(1).strip("'\"")

            if not evaluator_path.startswith(package_prefix):
                errors.append(
                    f'{subject}: concrete package evaluator must use '
                    f'{package_prefix}... instead of relative path {evaluator_path}'
                )
                continue
            if not lock_path.startswith(package_prefix):
                errors.append(
                    f'{subject}: benchmark lock must use the same absolute package-root '
                    f'placeholder as evaluator path; got {lock_path}'
                )
                continue
            if evaluator_path != lock_path:
                errors.append(
                    f'{subject}: evaluator path and benchmark lock differ: '
                    f'{evaluator_path} != {lock_path}'
                )
                continue

            relative = evaluator_path[len(package_prefix):]
            resolved = (root / relative).resolve()
            try:
                resolved.relative_to(root.resolve())
            except ValueError:
                errors.append(f'{subject}: evaluator escapes package root: {evaluator_path}')
                continue
            if not resolved.is_file():
                errors.append(f'{subject}: evaluator file does not exist: {relative}')

    return errors


def validate_template_consumption(root: Path) -> list[str]:
    errors: list[str] = []
    runner = root / 'scripts' / 'skill_improver_loop.py'
    runner_text = read_text(runner) if runner.exists() else ''
    required_templates = [
        'improvement-run-report.md.template',
        'patch-decision-record.md.template',
    ]
    for template_name in required_templates:
        template = root / 'assets' / 'templates' / template_name
        if not template.is_file():
            errors.append(f'missing template: assets/templates/{template_name}')
        if template_name not in runner_text:
            errors.append(f'template is not consumed by runner: assets/templates/{template_name}')
    if 'render_template(' not in runner_text:
        errors.append('runner does not expose a template rendering path')
    if 'write_patch_decision_records(' not in runner_text:
        errors.append('runner does not write patch decision records from templates')
    return errors



def validate_integration_manifest(root: Path) -> list[str]:
    path = root / 'contracts' / 'integration-manifest.json'
    if not path.is_file():
        return ['missing integration manifest: contracts/integration-manifest.json']
    try:
        manifest = json.loads(read_text(path))
    except Exception as exc:
        return [f'integration manifest invalid JSON: {exc}']
    errors: list[str] = []
    if manifest.get('manifest_version') != 1:
        errors.append('integration-manifest:manifest_version')
    if manifest.get('skill') != 'skill-improver':
        errors.append('integration-manifest:skill')
    exports = manifest.get('exports')
    if not isinstance(exports, list):
        errors.append('integration-manifest:exports')
        exports = []
    receipt = [x for x in exports if isinstance(x, dict) and x.get('contract_id') == 'skill-opt.candidate-generation-receipt']
    if len(receipt) != 1 or receipt[0].get('version') != 3:
        errors.append('integration-manifest:export:skill-opt.candidate-generation-receipt:v3')
    else:
        paths = receipt[0].get('surface_paths')
        if not isinstance(paths, list) or not paths:
            errors.append('integration-manifest:skill-opt.candidate-generation-receipt:surface_paths')
        else:
            for rel in paths:
                if not isinstance(rel, str) or not (root / rel).is_file():
                    errors.append(f'integration-manifest:skill-opt.candidate-generation-receipt:missing_surface:{rel}')
    imports = manifest.get('imports')
    if not isinstance(imports, list):
        errors.append('integration-manifest:imports')
        imports = []
    request = [x for x in imports if isinstance(x, dict) and x.get('contract_id') == 'skill-opt.candidate-request']
    if len(request) != 1 or 2 not in request[0].get('accepted_versions', []):
        errors.append('integration-manifest:import:skill-opt.candidate-request:v2')
    return errors

def main() -> int:
    parser = argparse.ArgumentParser(
        description='Validate skill-improver package readiness.'
    )
    parser.add_argument('--target', type=Path, required=True)
    parser.add_argument('--json-output', type=Path)
    args = parser.parse_args()

    root = args.target.resolve()
    gates: dict[str, str] = {}
    errors: list[str] = []

    skill_files = list(root.rglob('SKILL.md')) if root.exists() else []
    gates['exactly_one_skill_md'] = 'pass' if len(skill_files) == 1 else 'fail'
    if len(skill_files) != 1:
        errors.append(f'expected exactly one SKILL.md, found {len(skill_files)}')

    missing_required = [rel for rel in REQUIRED_FILES if not (root / rel).is_file()]
    gates['required_files_exist'] = 'pass' if not missing_required else 'fail'
    if missing_required:
        errors.append('missing required files or non-file entries: ' + ', '.join(missing_required))

    skill_md = root / 'SKILL.md'
    fm = parse_frontmatter(read_text(skill_md)) if skill_md.exists() else {}
    expected_frontmatter_keys = {'name', 'description'}
    frontmatter_ok = (
        set(fm.keys()) == expected_frontmatter_keys
        and bool(fm.get('name'))
        and bool(fm.get('description'))
        and fm.get('name') == fm.get('name', '').lower()
        and fm.get('description') == fm.get('description', '').lower()
    )
    gates['frontmatter'] = 'pass' if frontmatter_ok else 'fail'
    if gates['frontmatter'] == 'fail':
        errors.append('frontmatter must include only lowercase name and description')

    placeholders = find_placeholder_markers(root)
    gates['no_unresolved_placeholders'] = 'pass' if not placeholders else 'fail'
    if placeholders:
        errors.append('placeholder markers found: ' + ', '.join(placeholders))

    refs = referenced_paths(root)
    missing_refs = [rel for rel in refs if not (root / rel).exists()]
    gates['referenced_files_exist'] = 'pass' if not missing_refs else 'fail'
    if missing_refs:
        errors.append('missing referenced files: ' + ', '.join(missing_refs))

    scenario_counts, scenario_errors = validate_scenarios(
        root / 'evals' / 'activation-scenarios.json'
    )
    gates['scenario_suite'] = 'pass' if not scenario_errors else 'fail'
    errors.extend(scenario_errors)

    compile_errors = validate_python_scripts(root)
    gates['python_scripts_compile'] = 'pass' if not compile_errors else 'fail'
    errors.extend(compile_errors)

    template_errors = validate_template_consumption(root)
    gates['asset_templates_consumed'] = 'pass' if not template_errors else 'fail'
    errors.extend(template_errors)

    evaluator_example_errors = validate_command_evaluator_examples(root)
    gates['command_evaluator_examples'] = 'pass' if not evaluator_example_errors else 'fail'
    errors.extend(evaluator_example_errors)

    integration_errors = validate_integration_manifest(root)
    gates['integration_manifest'] = 'pass' if not integration_errors else 'fail'
    errors.extend(integration_errors)

    disallowed_names = {'.DS_Store', 'test-results.json', 'skill-benchmark.md'}
    disallowed_suffixes = {'.pyc', '.pyo', '.zip'}
    disallowed_dirs = {'__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache', '.git', '.skill-improver', '.hardening-work'}
    disallowed_artifacts: list[str] = []
    for candidate in sorted(root.rglob('*')):
        rel_parts = candidate.relative_to(root).parts
        if any(part in disallowed_dirs or part.startswith('hardening-') for part in rel_parts):
            disallowed_artifacts.append(candidate.relative_to(root).as_posix())
        elif candidate.is_file() and (candidate.name in disallowed_names or candidate.suffix.lower() in disallowed_suffixes):
            disallowed_artifacts.append(candidate.relative_to(root).as_posix())
    gates['package_hygiene'] = 'pass' if not disallowed_artifacts else 'fail'
    if disallowed_artifacts:
        errors.append('disallowed package artifacts found: ' + ', '.join(disallowed_artifacts))

    result = {
        'status': 'pass' if not errors else 'fail',
        'gates': gates,
        'scenario_counts': scenario_counts,
        'errors': errors,
        'target': str(root),
    }
    payload = json.dumps(result, indent=2, sort_keys=True)
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(payload + '\n', encoding='utf-8')
    print(payload)
    return 0 if not errors else 1


if __name__ == '__main__':
    raise SystemExit(main())
