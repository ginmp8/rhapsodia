#!/usr/bin/env python3
from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
import json
import os
import secrets
import subprocess
import tempfile
import zipfile
from pathlib import Path

from _common import (
    canonical_future_path,
    dump_json,
    is_noise,
    path_is_inside,
    paths_alias,
    parse_frontmatter,
    sha256_file,
    tree_hash,
)


def stage_bytes(parent: Path, name: str, data: bytes) -> Path:
    parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f'.{name}.', suffix='.tmp', dir=parent)
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, 'wb') as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        return tmp
    except Exception:
        if tmp.exists():
            tmp.unlink()
        raise


def fsync_file(path: Path) -> None:
    with path.open('rb') as handle:
        os.fsync(handle.fileno())


def fsync_dir(path: Path) -> None:
    if os.name == 'nt':
        return
    try:
        fd = os.open(path, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(fd)
    except OSError:
        pass
    finally:
        os.close(fd)


def target_exists(path: Path) -> bool:
    return path.exists() or path.is_symlink()


def transactional_commit(staged_targets: list[tuple[Path, Path]]) -> dict:
    token = secrets.token_hex(8)
    backups: dict[Path, Path] = {}
    committed: list[Path] = []
    recovery: list[dict] = []
    try:
        for _, target in staged_targets:
            target.parent.mkdir(parents=True, exist_ok=True)
            if target_exists(target):
                backup = target.with_name(f'.{target.name}.repro-backup-{token}')
                if target_exists(backup):
                    raise RuntimeError(f'backup path already exists: {backup}')
                os.replace(target, backup)
                backups[target] = backup

        for staged, target in staged_targets:
            os.replace(staged, target)
            committed.append(target)
            fsync_dir(target.parent)

        for backup in backups.values():
            if target_exists(backup):
                backup.unlink()
        for _, target in staged_targets:
            fsync_dir(target.parent)
        return {'status': 'pass', 'recovery': []}
    except Exception as exc:
        rollback_errors = []
        for target in reversed(committed):
            if not target_exists(target):
                continue
            failed = target.with_name(f'.{target.name}.repro-failed-{token}')
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

        raise RuntimeError(json.dumps({
            'commit_error': str(exc),
            'rollback_errors': rollback_errors,
            'recovery': recovery,
        })) from exc


def fail(stage: str, error: str, json_out: str | None, **extra) -> int:
    receipt = {'status': 'fail', 'stage': stage, 'error': error, **extra}
    destination = json_out
    if destination:
        requested = Path(destination).expanduser()
        if requested.exists() or requested.is_symlink():
            destination = None
    try:
        dump_json(receipt, destination)
    except Exception:
        dump_json(receipt, None)
    return 1


def main() -> int:
    ap = argparse.ArgumentParser(description='Validate and atomically package one frozen skill candidate.')
    ap.add_argument('--target', required=True)
    ap.add_argument('--output', required=True)
    ap.add_argument('--json', dest='json_out')
    ap.add_argument('--profile', choices=('portable', 'openai'), default='portable')
    ap.add_argument('--strict-openai-metadata', action='store_true', help='Backward-compatible alias for --profile openai.')
    args = ap.parse_args()

    profile = 'openai' if args.strict_openai_metadata else args.profile
    root = Path(args.target).resolve()
    authored_output = Path(args.output).expanduser()
    output = canonical_future_path(authored_output)

    if authored_output.suffix.lower() != '.zip':
        return fail('preflight', 'output must use a .zip extension', args.json_out, code='output/extension', output=str(authored_output))
    if output.suffix.lower() != '.zip':
        return fail('preflight', 'output must resolve to a .zip target after symbolic links are resolved', args.json_out, code='output/resolved-extension', output=str(authored_output), resolved_output=str(output))
    if output.exists() and not output.is_file():
        return fail('preflight', 'output target must be a file path, not a directory or special file', args.json_out, code='output/not-file', output=str(output))
    if path_is_inside(root, output):
        return fail('preflight', 'output must be outside the target skill folder to preserve frozen candidate identity', args.json_out, code='output/inside-target', output=str(output))

    receipt_path = None
    if args.json_out:
        authored_receipt = Path(args.json_out).expanduser()
        receipt_path = canonical_future_path(authored_receipt)
        if authored_receipt.suffix.lower() != '.json' or receipt_path.suffix.lower() != '.json':
            return fail('preflight', 'receipt output must use and resolve to a .json extension', None, code='receipt/extension', receipt=str(authored_receipt), resolved_receipt=str(receipt_path))
        if receipt_path.exists() and not receipt_path.is_file():
            return fail('preflight', 'receipt target must be a file path, not a directory or special file', None, code='receipt/not-file', receipt=str(receipt_path))
        if path_is_inside(root, receipt_path):
            return fail('preflight', 'receipt output must be outside the frozen target skill folder', None, code='receipt/inside-target', receipt=str(receipt_path))
        if paths_alias(output, receipt_path):
            return fail('preflight', 'package output and receipt output must not alias the same target', None, code='output/target-alias', output=str(output), receipt=str(receipt_path))

    skill_name = parse_frontmatter(root / 'SKILL.md').get('name', '') if (root / 'SKILL.md').is_file() else ''
    if not skill_name:
        return fail('preflight', 'SKILL.md must contain a non-empty name before packaging', args.json_out)

    validator = Path(__file__).with_name('validate_target_package.py')
    cmd = [sys.executable, str(validator), '--target', str(root), '--profile', profile]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        return fail('validation', 'target package validation failed', args.json_out, profile=profile, validator_exit=proc.returncode, stdout=proc.stdout, stderr=proc.stderr)

    output.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f'.{output.name}.', suffix='.tmp', dir=output.parent)
    os.close(fd)
    package_stage = Path(tmp_name)
    receipt_stage = None
    included = []

    try:
        with zipfile.ZipFile(package_stage, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
            for p in sorted(root.rglob('*')):
                if p.is_symlink() or not p.is_file():
                    continue
                rel = p.relative_to(root)
                if is_noise(rel):
                    continue
                arc = (Path(skill_name) / rel).as_posix()
                zf.write(p, arc)
                included.append(arc)
        fsync_file(package_stage)

        with zipfile.ZipFile(package_stage, 'r') as zf:
            bad = zf.testzip()
            names = zf.namelist()
            if bad:
                raise RuntimeError(f'zip CRC failure: {bad}')
            if len(names) != len(included) or set(names) != set(included):
                raise RuntimeError('zip entry set differs from included file set')
            if any(not name.startswith(skill_name + '/') for name in names):
                raise RuntimeError('zip contains entries outside the canonical skill-name root')

        package_sha = sha256_file(package_stage)
        source_sha = tree_hash(root)
        receipt = {
            'receipt_version': 2,
            'status': 'pass',
            'stage': 'committed',
            'profile': profile,
            'target': str(root),
            'skill_name': skill_name,
            'output': str(output),
            'source_tree_sha256': source_sha,
            'package_sha256': package_sha,
            'package_bytes': package_stage.stat().st_size,
            'file_count': len(included),
            'validator_exit': proc.returncode,
            'output_preserved_on_failure': True,
            'recovery': [],
        }

        staged_targets = [(package_stage, output)]
        if receipt_path is not None:
            receipt_bytes = (json.dumps(receipt, indent=2, sort_keys=False) + '\n').encode('utf-8')
            receipt_stage = stage_bytes(receipt_path.parent, receipt_path.name, receipt_bytes)
            staged_targets.append((receipt_stage, receipt_path))

        transactional_commit(staged_targets)
        package_stage = Path('')
        receipt_stage = None

        if args.json_out is None:
            dump_json(receipt, None)
        return 0
    except Exception as exc:
        recovery = []
        try:
            parsed = json.loads(str(exc))
            if isinstance(parsed, dict):
                recovery = parsed.get('recovery', [])
        except Exception:
            pass
        if package_stage and str(package_stage) and package_stage.exists():
            try:
                package_stage.unlink()
            except OSError:
                recovery.append({'kind': 'staged-candidate', 'preserved_at': str(package_stage)})
        if receipt_stage is not None and receipt_stage.exists():
            try:
                receipt_stage.unlink()
            except OSError:
                recovery.append({'kind': 'staged-receipt', 'preserved_at': str(receipt_stage)})
        return fail('package', str(exc), args.json_out, profile=profile, output_preserved=target_exists(output), recovery=recovery)


if __name__ == '__main__':
    raise SystemExit(main())
