#!/usr/bin/env python3
"""Validate and deterministically package an Agent Skills-compatible skill."""

from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
import zipfile
from pathlib import Path
from typing import Any

from _common import dump_json, extract_local_refs, parse_frontmatter, path_is_inside, paths_alias, sha256_file, stage_bytes, transactional_commit, tree_hash
from validate_portability import normalize_hosts, validate as validate_portability

EXCLUDED_DIRS = {'.git', '__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache', 'node_modules', 'reports', 'test-results', 'benchmark-reports'}
EXCLUDED_FILES = {'.DS_Store', 'test-results.json', 'hardening-audit.json'}
SENSITIVE = [re.compile(r'^\.env(?:\..+)?$', re.I), re.compile(r'.*\.(?:pem|p12|pfx|key)$', re.I), re.compile(r'^(?:credentials|secrets?)(?:\..+)?$', re.I)]
SCAFFOLD = [re.compile(r'\[TODO', re.I), re.compile(r'\bTODO\s*:', re.I), re.compile(r'replace with actual', re.I), re.compile(r'this is a placeholder', re.I)]
TEXT_SUFFIXES = {'.md', '.txt', '.yaml', '.yml', '.json', '.py', '.js', '.sh', '.toml'}


def sensitive_name(name: str) -> bool:
    return any(pattern.fullmatch(name) or pattern.match(name) for pattern in SENSITIVE)


def package_files(target: Path) -> tuple[list[Path], list[dict]]:
    files: list[Path] = []
    excluded: list[dict] = []
    for path in sorted(target.rglob('*')):
        rel = path.relative_to(target)
        if any(part in EXCLUDED_DIRS for part in rel.parts):
            if path.is_file():
                excluded.append({'path': rel.as_posix(), 'reason': 'excluded directory'})
            continue
        if path.is_symlink():
            raise ValueError(f'symlink is not portable package content: {rel.as_posix()}')
        if not path.is_file():
            continue
        if path.name in EXCLUDED_FILES or sensitive_name(path.name) or path.name.endswith(('~', '.swp', '.swo')):
            excluded.append({'path': rel.as_posix(), 'reason': 'excluded or sensitive-looking file'})
            continue
        files.append(path)
    return files, excluded


def validate_folder(target: Path, hosts: list[str]) -> dict:
    portability = validate_portability(target, hosts)
    errors = [item.get('evidence', 'portability error') for item in portability.get('errors', [])]
    warnings = [item.get('evidence', 'portability warning') for item in portability.get('warnings', [])]
    skill_md = target / 'SKILL.md'
    if skill_md.is_file():
        text = skill_md.read_text(encoding='utf-8', errors='replace')
        for ref in extract_local_refs(text):
            if Path(ref).is_absolute() or '..' in Path(ref).parts:
                errors.append(f'unsafe local reference: {ref}')
            elif not (target / ref).exists():
                errors.append(f'referenced path missing: {ref}')
    try:
        files, _ = package_files(target)
    except Exception as exc:
        errors.append(str(exc))
        files = []
    if not files:
        errors.append('no packageable files found')
    for path in files:
        rel = path.relative_to(target).as_posix()
        if path.suffix.lower() not in TEXT_SUFFIXES or rel.startswith('assets/templates/'):
            continue
        text = path.read_text(encoding='utf-8', errors='replace')
        for line_no, line in enumerate(text.splitlines(), 1):
            if 're.compile' in line or 're.search' in line:
                continue
            if any(pattern.search(line) for pattern in SCAFFOLD):
                errors.append(f'residual scaffold marker: {rel}:{line_no}')
    return {'status': 'pass' if not errors else 'fail', 'errors': errors, 'warnings': warnings, 'portability': portability}


def write_zip(target: Path, archive: Path, files: list[Path], root_name: str) -> list[str]:
    names: list[str] = []
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in files:
            rel = path.relative_to(target).as_posix()
            arc = f'{root_name}/{rel}'
            info = zipfile.ZipInfo(arc, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            mode = 0o755 if path.suffix.lower() in {'.py', '.sh'} else 0o644
            info.external_attr = mode << 16
            zf.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
            names.append(arc)
    with archive.open('rb') as handle:
        os.fsync(handle.fileno())
    return names


def validate_archive(zip_path: Path) -> dict[str, Any]:
    errors: list[str] = []
    if not zip_path.is_file():
        return {'status': 'fail', 'errors': [f'zip does not exist: {zip_path}'], 'file_count': 0}
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            bad = zf.testzip()
            names = [name for name in zf.namelist() if not name.endswith('/')]
            if bad:
                errors.append(f'corrupt archive member: {bad}')
            top = sorted({name.split('/', 1)[0] for name in names if name})
            if len(top) != 1:
                errors.append(f'archive must contain exactly one top-level skill directory, found {top}')
            root = top[0] if top else ''
            if f'{root}/SKILL.md' not in names:
                errors.append('archive missing root SKILL.md')
            for name in names:
                if name.startswith('/') or '..' in Path(name).parts:
                    errors.append(f'unsafe archive path: {name}')
            if root and f'{root}/SKILL.md' in names:
                text = zf.read(f'{root}/SKILL.md').decode('utf-8', errors='replace')
                temp = Path(root)  # name only for consistency check below
                fm_name_match = re.search(r'(?m)^name:\s*([^\n]+)$', text)
                if fm_name_match and fm_name_match.group(1).strip().strip('"\'') != root:
                    errors.append('archive root does not match SKILL.md name')
    except zipfile.BadZipFile:
        names = []
        errors.append('archive is not a readable zip file')
    return {'status': 'pass' if not errors else 'fail', 'errors': errors, 'file_count': len(names), 'size_bytes': zip_path.stat().st_size if zip_path.exists() else 0}


def emit_failure(stage: str, receipt_path: Path | None, **extra: Any) -> int:
    receipt = {'receipt_version': 2, 'status': 'fail', 'stage': stage, 'last_good_preserved_on_failure': True, 'recovery': [], **extra}
    if receipt_path is not None and not (receipt_path.exists() or receipt_path.is_symlink()):
        try:
            dump_json(receipt, receipt_path)
        except Exception:
            pass
    dump_json(receipt)
    return 1


def package(target: Path, output: Path, receipt_path: Path | None, hosts: list[str]) -> tuple[int, dict]:
    target = target.expanduser().resolve(strict=True)
    output = output.expanduser().resolve(strict=False)
    receipt_path = receipt_path.expanduser().resolve(strict=False) if receipt_path else None
    if output.suffix.lower() != '.zip':
        return 1, {'stage': 'preflight', 'error': 'output must use a .zip extension'}
    if path_is_inside(target, output):
        return 1, {'stage': 'preflight', 'error': 'output must be outside the target skill folder'}
    if output.exists() and not output.is_file():
        return 1, {'stage': 'preflight', 'error': 'output target must be a normal file'}
    if receipt_path:
        if receipt_path.suffix.lower() != '.json':
            return 1, {'stage': 'preflight', 'error': 'receipt must use a .json extension'}
        if path_is_inside(target, receipt_path):
            return 1, {'stage': 'preflight', 'error': 'receipt must be outside the target skill folder'}
        if paths_alias(output, receipt_path):
            return 1, {'stage': 'preflight', 'error': 'package and receipt outputs must not alias'}

    validation = validate_folder(target, hosts)
    if validation['status'] != 'pass':
        return 1, {'stage': 'validation', 'validation': validation}
    fm, _ = parse_frontmatter(target / 'SKILL.md')
    root_name = fm.get('name', '')
    if not root_name:
        return 1, {'stage': 'validation', 'error': 'SKILL.md name missing'}
    files, excluded = package_files(target)
    candidate_hash_before = tree_hash(target, reject_symlinks=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f'.{output.name}.', suffix='.tmp', dir=output.parent)
    os.close(fd)
    stage = Path(tmp_name)
    try:
        write_zip(target, stage, files, root_name)
        archive_validation = validate_archive(stage)
        candidate_hash_after = tree_hash(target, reject_symlinks=True)
        if candidate_hash_after != candidate_hash_before:
            archive_validation.setdefault('errors', []).append('target changed while packaging')
            archive_validation['status'] = 'fail'
        if archive_validation['status'] != 'pass':
            return 1, {'stage': 'package_verify', 'validation': validation, 'archive': archive_validation}
        receipt = {
            'receipt_version': 2,
            'status': 'pass',
            'stage': 'committed',
            'target': str(target),
            'skill_name': root_name,
            'candidate_sha256': candidate_hash_before,
            'archive_sha256': sha256_file(stage),
            'archive_bytes': stage.stat().st_size,
            'file_count': len(files),
            'excluded': excluded,
            'requested_hosts': hosts,
            'portability': validation['portability'],
            'atomic_replace': True,
            'last_good_preserved_on_failure': True,
            'recovery': [],
            'output': str(output),
        }
        staged_targets = [(stage, output)]
        receipt_stage = None
        if receipt_path:
            receipt_stage = stage_bytes(receipt_path, (json.dumps(receipt, indent=2, ensure_ascii=False) + '\n').encode('utf-8'))
            staged_targets.append((receipt_stage, receipt_path))
        transactional_commit(staged_targets)
        if receipt_path:
            receipt['receipt_sha256'] = sha256_file(receipt_path)
        return 0, receipt
    finally:
        if stage.exists():
            stage.unlink()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Build and validate a portable Agent Skills package zip.')
    parser.add_argument('--target')
    parser.add_argument('--output')
    parser.add_argument('--validate-only', help='Validate an existing package zip without creating a new one.')
    parser.add_argument('--json-output', help='Optional success receipt path. Existing last-good receipts are preserved on failure.')
    parser.add_argument('--hosts', default='portable-core', help='portable-core,openai,claude,copilot,cursor,all')
    args = parser.parse_args(argv)

    if args.validate_only:
        result = {'mode': 'validate-only', 'archive': validate_archive(Path(args.validate_only).resolve())}
        result['status'] = result['archive']['status']
        if args.json_output:
            dump_json(result, args.json_output)
        dump_json(result)
        return 0 if result['status'] == 'pass' else 1
    if not args.target or not args.output:
        return emit_failure('arguments', Path(args.json_output) if args.json_output else None, error='--target and --output are required unless --validate-only is used')
    try:
        hosts = normalize_hosts(args.hosts)
        code, detail = package(Path(args.target), Path(args.output), Path(args.json_output) if args.json_output else None, hosts)
        if code != 0:
            return emit_failure(detail.pop('stage', 'package'), Path(args.json_output) if args.json_output else None, **detail)
        dump_json(detail)
        return 0
    except Exception as exc:
        return emit_failure('package', Path(args.json_output) if args.json_output else None, error=str(exc))


if __name__ == '__main__':
    raise SystemExit(main())
