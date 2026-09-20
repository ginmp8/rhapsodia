#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path

from _common import dump_json, extract_local_refs, parse_frontmatter

KNOWN_HOSTS = {'portable-core', 'openai', 'codex', 'claude', 'copilot', 'cursor'}
PRIVATE_TOKENS = {
    'skills__read': 'OpenAI/ChatGPT private skill tool name',
    'tools.skills__': 'OpenAI/ChatGPT private skill namespace',
    'functions.exec': 'OpenAI/ChatGPT private orchestration tool name',
    'python_user_visible': 'OpenAI/ChatGPT private execution tool name',
    'container.exec': 'OpenAI/ChatGPT private execution tool name',
    '/home/oai/': 'OpenAI sandbox-specific filesystem path',
    'sandbox:/mnt/data': 'OpenAI sandbox-specific artifact path',
}
COMMON_FRONTMATTER = {'name', 'description', 'license', 'compatibility', 'metadata', 'allowed-tools'}
CURSOR_ONLY_FRONTMATTER = {'paths', 'disable-model-invocation', 'icon', 'color'}


def normalize_hosts(raw: str) -> list[str]:
    hosts = [item.strip().lower() for item in raw.split(',') if item.strip()]
    if not hosts:
        hosts = ['portable-core']
    if 'all' in hosts:
        hosts = ['portable-core', 'openai', 'codex', 'claude', 'copilot', 'cursor']
    if 'portable-core' not in hosts:
        hosts.insert(0, 'portable-core')
    unknown = sorted(set(hosts) - KNOWN_HOSTS)
    if unknown:
        raise ValueError('unknown host profile(s): ' + ', '.join(unknown))
    return list(dict.fromkeys(hosts))


def frontmatter_keys(path: Path) -> set[str]:
    text = path.read_text(encoding='utf-8', errors='replace').replace('\r\n', '\n')
    match = re.match(r'^---\n(.*?)\n---(?:\n|$)', text, re.DOTALL)
    if not match:
        return set()
    keys: set[str] = set()
    for line in match.group(1).splitlines():
        if line and not line[:1].isspace():
            item = re.match(r'^([A-Za-z0-9_-]+):', line)
            if item:
                keys.add(item.group(1))
    return keys


def structural_validate(root: Path) -> tuple[dict, dict[str, str], set[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if not root.is_dir():
        return {'status': 'fail', 'errors': [f'target is not a directory: {root}'], 'warnings': []}, {}, set()
    skill_files = [p for p in root.rglob('SKILL.md') if p.is_file()]
    if skill_files != [root / 'SKILL.md']:
        errors.append(f'target must contain exactly one root SKILL.md, found {len(skill_files)}')
    skill_md = root / 'SKILL.md'
    fm: dict[str, str] = {}
    keys: set[str] = set()
    if skill_md.is_file():
        fm, parse_errors = parse_frontmatter(skill_md)
        errors.extend(parse_errors)
        keys = frontmatter_keys(skill_md)
        name = fm.get('name', '')
        description = fm.get('description', '')
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name or ''):
            errors.append('name must be lowercase hyphen-case')
        if len(name) > 64:
            errors.append('name must be at most 64 characters')
        if not description:
            errors.append('description must be non-empty')
        if len(description) > 1024:
            errors.append('description must be at most 1024 characters')
        if name and root.name != name:
            warnings.append(f'directory name {root.name!r} differs from frontmatter name {name!r}')
        text = skill_md.read_text(encoding='utf-8', errors='replace')
        for ref in extract_local_refs(text):
            if Path(ref).is_absolute() or '..' in Path(ref).parts:
                errors.append(f'unsafe local reference: {ref}')
            elif not (root / ref).exists():
                errors.append(f'missing local reference: {ref}')
    return {'status': 'pass' if not errors else 'fail', 'errors': errors, 'warnings': warnings}, fm, keys


def scan_private_tokens(root: Path) -> list[dict]:
    findings: list[dict] = []
    excluded = {'references/host-portability.md', 'scripts/validate_portability.py'}
    for path in sorted(root.rglob('*')):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if rel in excluded or rel.startswith('agents/'):
            continue
        if path.suffix.lower() not in {'.md', '.py', '.js', '.json', '.yaml', '.yml', '.txt', '.template'}:
            continue
        text = path.read_text(encoding='utf-8', errors='replace')
        for token, reason in PRIVATE_TOKENS.items():
            if token in text:
                findings.append({'code': 'HOST_PRIVATE_CORE', 'severity': 'error', 'evidence': f'{rel}: {token}', 'reason': reason})
    return findings


def scan_python_dependencies(root: Path) -> list[dict]:
    stdlib = set(getattr(sys, 'stdlib_module_names', ()))
    findings: list[dict] = []
    scripts = root / 'scripts'
    if not scripts.exists():
        return findings
    local_modules = {p.stem for p in scripts.glob('*.py')}
    for script in sorted(scripts.glob('*.py')):
        try:
            tree = ast.parse(script.read_text(encoding='utf-8'), filename=str(script))
        except SyntaxError as exc:
            findings.append({'code': 'PYTHON_SYNTAX', 'severity': 'error', 'evidence': f'{script.name}:{exc.lineno}', 'reason': exc.msg})
            continue
        imports: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name.split('.', 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split('.', 1)[0])
        if stdlib:
            for name in sorted(imports):
                if name not in stdlib and name not in local_modules:
                    findings.append({'code': 'PYTHON_EXTERNAL_DEPENDENCY', 'severity': 'warning', 'evidence': f'{script.name}: {name}', 'reason': 'external dependency may not exist on every host'})
    return findings


def validate_openai_adapter(root: Path) -> tuple[str, list[dict]]:
    adapter = root / 'agents' / 'openai.yaml'
    if not adapter.exists():
        return 'not-present', []
    text = adapter.read_text(encoding='utf-8', errors='replace')
    findings: list[dict] = []
    for required in ('interface:', 'display_name:', 'short_description:'):
        if required not in text:
            findings.append({'code': 'OPENAI_ADAPTER_FIELD', 'severity': 'error', 'evidence': required, 'reason': 'OpenAI adapter is present but incomplete'})
    if 'products:' in text:
        findings.append({'code': 'OPENAI_ADAPTER_LEGACY_FIELD', 'severity': 'warning', 'evidence': 'products:', 'reason': 'legacy product policy should not be required for portable behavior'})
    return ('fail' if any(item['severity'] == 'error' for item in findings) else 'pass'), findings


def validate(root: Path, hosts: list[str]) -> dict:
    root = root.resolve()
    structural, fm, keys = structural_validate(root)
    findings: list[dict] = []
    findings.extend({'code': 'STRUCTURE', 'severity': 'error', 'evidence': error, 'reason': 'portable structure validation failed'} for error in structural['errors'])
    findings.extend(scan_private_tokens(root))
    findings.extend(scan_python_dependencies(root))

    unknown = sorted(keys - COMMON_FRONTMATTER - CURSOR_ONLY_FRONTMATTER)
    for key in unknown:
        findings.append({'code': 'UNKNOWN_FRONTMATTER', 'severity': 'warning', 'evidence': key, 'reason': 'unknown frontmatter may not be interpreted consistently across hosts'})
    cursor_only = sorted(keys & CURSOR_ONLY_FRONTMATTER)
    if cursor_only and any(host not in {'portable-core', 'cursor'} for host in hosts):
        for key in cursor_only:
            findings.append({'code': 'CURSOR_FRONTMATTER_IN_CORE', 'severity': 'warning', 'evidence': key, 'reason': 'Cursor-specific frontmatter should remain optional for cross-host behavior'})
    if 'allowed-tools' in keys and len(hosts) > 2:
        findings.append({'code': 'EXPERIMENTAL_ALLOWED_TOOLS', 'severity': 'warning', 'evidence': 'allowed-tools', 'reason': 'tool-permission semantics vary by host'})

    core_errors = [item for item in findings if item['severity'] == 'error']
    host_results: dict[str, dict] = {'portable-core': {'status': 'fail' if core_errors else 'pass', 'adapter': 'none-required'}}

    if 'claude' in hosts:
        errors: list[dict] = []
        tokens = set(str(fm.get('name', '')).split('-'))
        reserved = tokens & {'anthropic', 'claude'}
        for token in sorted(reserved):
            finding = {'code': 'CLAUDE_RESERVED_NAME', 'severity': 'error', 'evidence': token, 'reason': 'Claude custom skills reserve anthropic/claude in names'}
            findings.append(finding)
            errors.append(finding)
        host_results['claude'] = {'status': 'fail' if core_errors or errors else 'pass', 'adapter': 'none-required'}
    if 'openai' in hosts or 'codex' in hosts:
        adapter, adapter_findings = validate_openai_adapter(root)
        findings.extend(adapter_findings)
        host_errors = [item for item in adapter_findings if item['severity'] == 'error']
        host_status = 'fail' if core_errors or host_errors else 'pass'
        if 'openai' in hosts:
            host_results['openai'] = {'status': host_status, 'adapter': adapter}
        if 'codex' in hosts:
            host_results['codex'] = {'status': host_status, 'adapter': adapter}
    if 'copilot' in hosts:
        host_results['copilot'] = {'status': 'fail' if core_errors else 'pass', 'adapter': 'none-required'}
    if 'cursor' in hosts:
        host_results['cursor'] = {'status': 'fail' if core_errors else 'pass', 'adapter': 'none-required'}

    errors = [item for item in findings if item['severity'] == 'error']
    warnings = [item for item in findings if item['severity'] == 'warning']
    status = 'fail' if errors or any(item['status'] == 'fail' for item in host_results.values()) else 'pass'
    return {
        'status': status,
        'requested_hosts': hosts,
        'portable_core': host_results['portable-core']['status'] == 'pass',
        'host_results': host_results,
        'runtime_verified': False,
        'runtime_note': 'structural portability only; behavioral/runtime claims require execution on each host',
        'errors': errors,
        'warnings': warnings,
        'structural_validation': structural,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Validate skill-benchmark portability across Agent Skills-compatible hosts.')
    parser.add_argument('--target', required=True)
    parser.add_argument('--hosts', default='portable-core', help='portable-core,openai,codex,claude,copilot,cursor,all')
    parser.add_argument('--json', dest='json_output')
    args = parser.parse_args()
    try:
        report = validate(Path(args.target), normalize_hosts(args.hosts))
    except Exception as exc:
        report = {'status': 'fail', 'errors': [{'code': 'PORTABILITY_EXCEPTION', 'severity': 'error', 'evidence': str(exc), 'reason': 'validator exception'}], 'warnings': []}
    if args.json_output:
        dump_json(report, args.json_output)
    dump_json(report)
    return 0 if report.get('status') == 'pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())
