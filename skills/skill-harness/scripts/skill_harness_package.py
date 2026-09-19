#!/usr/bin/env python3
"""Validate and atomically package one Agent Skills-compatible folder as skill.zip."""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import secrets
import stat
import sys
import tempfile
import zipfile
from pathlib import Path

sys.dont_write_bytecode = True
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
VALIDATOR_PATH = SCRIPT_DIR / 'skill_harness_validate.py'
from _harness_common import canonical_future_path, dump_json, fsync_dir, parse_frontmatter_scalars, path_is_inside, paths_alias, sha256_file, stage_bytes, tree_hash

EXCLUDE_DIRS = {'.git', '.hg', '.svn', '__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache', 'node_modules', 'dist', 'build', 'reports', '.reports', 'artifacts', 'scratch', '.scratch', 'tmp', 'temp', 'coverage', '.coverage'}
EXCLUDE_SUFFIXES = {'.pyc', '.pyo', '.zip'}
EXCLUDE_NAMES = {'.DS_Store'}
ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)


def load_validator_module():
    spec = importlib.util.spec_from_file_location('skill_harness_validate', VALIDATOR_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def should_exclude(path: Path, target: Path) -> bool:
    rel = path.relative_to(target)
    return bool(set(rel.parts) & EXCLUDE_DIRS or path.name in EXCLUDE_NAMES or path.suffix.lower() in EXCLUDE_SUFFIXES)


def iter_package_files(target: Path):
    for path in sorted(target.rglob('*')):
        if path.is_symlink():
            if not should_exclude(path, target):
                raise ValueError(f'portable packaging rejects symlinks: {path.relative_to(target).as_posix()}')
            continue
        if path.is_file() and not should_exclude(path, target):
            yield path


def add_file(zipf: zipfile.ZipFile, path: Path, arcname: str) -> None:
    data = path.read_bytes()
    info = zipfile.ZipInfo(arcname, date_time=ZIP_TIMESTAMP)
    perm = stat.S_IMODE(path.stat().st_mode) or 0o644
    info.external_attr = (perm & 0xFFFF) << 16
    info.compress_type = zipfile.ZIP_DEFLATED
    zipf.writestr(info, data)


def target_exists(path: Path) -> bool:
    return path.exists() or path.is_symlink()


def transactional_commit(staged_targets: list[tuple[Path, Path]]) -> list[dict]:
    token = secrets.token_hex(8)
    backups: dict[Path, Path] = {}
    committed: list[Path] = []
    recovery: list[dict] = []
    try:
        for _, target in staged_targets:
            target.parent.mkdir(parents=True, exist_ok=True)
            if target_exists(target):
                backup = target.with_name(f'.{target.name}.harness-backup-{token}')
                os.replace(target, backup)
                backups[target] = backup
        for staged, target in staged_targets:
            os.replace(staged, target)
            committed.append(target)
            fsync_dir(target.parent)
        for backup in backups.values():
            if target_exists(backup):
                backup.unlink()
        return recovery
    except Exception as exc:
        rollback_errors = []
        for target in reversed(committed):
            if not target_exists(target):
                continue
            failed = target.with_name(f'.{target.name}.harness-failed-{token}')
            try:
                os.replace(target, failed)
                recovery.append({'kind': 'failed-candidate', 'target': str(target), 'preserved_at': str(failed)})
            except Exception as rollback_exc:
                rollback_errors.append({'target': str(target), 'error': str(rollback_exc)})
        for target, backup in backups.items():
            if not target_exists(backup):
                continue
            try:
                os.replace(backup, target)
                fsync_dir(target.parent)
            except Exception as rollback_exc:
                recovery.append({'kind': 'previous-output-backup', 'target': str(target), 'preserved_at': str(backup)})
                rollback_errors.append({'target': str(target), 'error': str(rollback_exc)})
        for staged, target in staged_targets:
            if staged.exists():
                recovery.append({'kind': 'staged-candidate', 'target': str(target), 'preserved_at': str(staged)})
        raise RuntimeError(json.dumps({'commit_error': str(exc), 'rollback_errors': rollback_errors, 'recovery': recovery})) from exc


def write_failure(report: dict, report_path: Path | None) -> None:
    # Never destroy a prior last-good report merely to record a new failed attempt.
    if report_path is not None and not target_exists(report_path):
        dump_json(report, str(report_path))
    else:
        dump_json(report, None)


def package_skill(target, output, report_path=None, strict=False, profile='portable'):
    target = Path(target).expanduser().resolve(strict=True)
    authored_output = Path(output).expanduser()
    resolved_output = canonical_future_path(authored_output)
    resolved_report = canonical_future_path(report_path) if report_path else None

    preflight = {'status': 'fail', 'stage': 'preflight', 'packaged': False, 'output': str(authored_output), 'profile': profile}
    if authored_output.suffix.lower() != '.zip' or resolved_output.suffix.lower() != '.zip':
        return {**preflight, 'code': 'output/extension', 'error': 'package output must use and resolve to .zip'}
    if resolved_output.exists() and not resolved_output.is_file():
        return {**preflight, 'code': 'output/not-file', 'error': 'package output target must be a file path'}
    if path_is_inside(target, resolved_output):
        return {**preflight, 'code': 'output/inside-target', 'error': 'package output must be outside the target skill root'}
    if resolved_report is not None:
        if Path(report_path).suffix.lower() != '.json' or resolved_report.suffix.lower() != '.json':
            return {**preflight, 'code': 'report/extension', 'error': 'package report must use and resolve to .json'}
        if resolved_report.exists() and not resolved_report.is_file():
            return {**preflight, 'code': 'report/not-file', 'error': 'package report target must be a file path'}
        if path_is_inside(target, resolved_report):
            return {**preflight, 'code': 'report/inside-target', 'error': 'package report must be outside the target skill root'}
        if paths_alias(resolved_output, resolved_report):
            return {**preflight, 'code': 'output/target-alias', 'error': 'package and report outputs must not alias'}

    validator = load_validator_module()
    validation = validator.validate_package(target, profile=profile)
    blocker_failures = [g for g in validation['gates'] if not g['passed'] and g['severity'] == 'blocker']
    major_failures = [g for g in validation['gates'] if not g['passed'] and g['severity'] == 'major']
    if blocker_failures or (strict and major_failures):
        return {
            'status': 'fail', 'stage': 'validation', 'packaged': False, 'output': str(resolved_output),
            'profile': profile, 'validation': validation, 'error': 'validation gates failed',
            'excluded_dirs': sorted(EXCLUDE_DIRS), 'excluded_suffixes': sorted(EXCLUDE_SUFFIXES),
        }

    fm = parse_frontmatter_scalars(target / 'SKILL.md')
    skill_name = fm.get('name', '')
    if not skill_name:
        return {'status': 'fail', 'stage': 'preflight', 'packaged': False, 'error': 'SKILL.md name is required'}

    resolved_output.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f'.{resolved_output.name}.', suffix='.tmp', dir=resolved_output.parent)
    os.close(fd)
    staged_zip = Path(temp_name)
    staged_report = None
    try:
        files = list(iter_package_files(target))
        with zipfile.ZipFile(staged_zip, 'w', compression=zipfile.ZIP_DEFLATED) as zipf:
            for path in files:
                rel = path.relative_to(target).as_posix()
                add_file(zipf, path, f'{skill_name}/{rel}')
        with staged_zip.open('rb') as handle:
            os.fsync(handle.fileno())
        with zipfile.ZipFile(staged_zip, 'r') as zipf:
            bad = zipf.testzip()
            entries = zipf.namelist()
            if bad:
                raise RuntimeError(f'zip CRC failure: {bad}')
            if any(not entry.startswith(skill_name + '/') for entry in entries):
                raise RuntimeError('archive contains entries outside the canonical skill root')

        receipt = {
            'receipt_version': 2,
            'status': 'pass',
            'stage': 'committed',
            'packaged': True,
            'profile': profile,
            'target': str(target),
            'skill_name': skill_name,
            'output': str(resolved_output),
            'source_tree_sha256': tree_hash(target),
            'package_sha256': sha256_file(staged_zip),
            'package_bytes': staged_zip.stat().st_size,
            'file_count': len(files),
            'archive_entries': entries,
            'validation': validation,
            'excluded_dirs': sorted(EXCLUDE_DIRS),
            'excluded_suffixes': sorted(EXCLUDE_SUFFIXES),
            'output_preserved_on_failure': True,
            'recovery': [],
        }
        staged_targets = [(staged_zip, resolved_output)]
        if resolved_report is not None:
            staged_report = stage_bytes(resolved_report, (json.dumps(receipt, indent=2, sort_keys=True) + '\n').encode('utf-8'))
            staged_targets.append((staged_report, resolved_report))
        transactional_commit(staged_targets)
        if resolved_report is None:
            dump_json(receipt, None)
        return receipt
    except Exception as exc:
        recovery = []
        try:
            parsed = json.loads(str(exc))
            if isinstance(parsed, dict):
                recovery = parsed.get('recovery', [])
        except Exception:
            pass
        for staged in (staged_zip, staged_report):
            if staged is not None and staged.exists() and not any(r.get('preserved_at') == str(staged) for r in recovery):
                try:
                    staged.unlink()
                except OSError:
                    recovery.append({'kind': 'staged-candidate', 'preserved_at': str(staged)})
        return {
            'status': 'fail', 'stage': 'package', 'packaged': False, 'output': str(resolved_output),
            'profile': profile, 'validation': validation, 'error': str(exc),
            'output_preserved': target_exists(resolved_output), 'recovery': recovery,
        }


def main():
    parser = argparse.ArgumentParser(description='Validate and package an Agent Skills-compatible folder as skill.zip.')
    parser.add_argument('--target', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--report')
    parser.add_argument('--strict', action='store_true')
    parser.add_argument('--profile', choices=('portable', 'openai', 'claude', 'copilot', 'cursor'), default='portable')
    args = parser.parse_args()
    report_path = Path(args.report).expanduser() if args.report else None
    result = package_skill(args.target, args.output, report_path=report_path, strict=args.strict, profile=args.profile)
    if result.get('status') == 'pass':
        if not args.report:
            pass  # success receipt already emitted by package_skill
    else:
        write_failure(result, report_path)
    raise SystemExit(0 if result.get('packaged') else 1)


if __name__ == '__main__':
    main()
