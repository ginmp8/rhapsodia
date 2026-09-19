from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Iterable

NOISE_DIRS = {'.git', '__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache', 'node_modules'}
NOISE_FILES = {'.DS_Store'}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def is_noise(rel: Path) -> bool:
    return any(part in NOISE_DIRS for part in rel.parts) or rel.name in NOISE_FILES or rel.suffix == '.pyc'


def iter_files(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob('*')):
        rel = path.relative_to(root)
        if is_noise(rel):
            continue
        if path.is_symlink():
            yield path
        elif path.is_file():
            yield path


def tree_manifest(root: Path, *, reject_symlinks: bool = False) -> list[dict]:
    rows: list[dict] = []
    for path in iter_files(root):
        rel = path.relative_to(root).as_posix()
        if path.is_symlink():
            if reject_symlinks:
                raise ValueError(f'symlink is not portable benchmark evidence: {rel}')
            rows.append({'path': rel, 'type': 'symlink', 'target': os.readlink(path)})
        else:
            rows.append({'path': rel, 'type': 'file', 'size': path.stat().st_size, 'sha256': sha256_file(path)})
    return rows


def tree_hash(root: Path, *, reject_symlinks: bool = False) -> str:
    payload = json.dumps(tree_manifest(root, reject_symlinks=reject_symlinks), sort_keys=True, separators=(',', ':')).encode('utf-8')
    return sha256_bytes(payload)


def parse_frontmatter_text(text: str) -> tuple[dict[str, str], list[str]]:
    errors: list[str] = []
    normalized = text.replace('\r\n', '\n')
    if not normalized.startswith('---\n'):
        return {}, ['SKILL.md missing opening frontmatter fence']
    end = normalized.find('\n---\n', 4)
    if end < 0:
        return {}, ['SKILL.md missing closing frontmatter fence']
    block = normalized[4:end]
    data: dict[str, str] = {}
    current: str | None = None
    for raw in block.splitlines():
        if not raw.strip() or raw.lstrip().startswith('#'):
            continue
        if not raw.startswith((' ', '\t')) and ':' in raw:
            key, value = raw.split(':', 1)
            current = key.strip()
            value = value.strip()
            if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                value = value[1:-1]
            data[current] = value
        elif current:
            data[current] = (data[current] + ' ' + raw.strip()).strip()
        else:
            errors.append(f'unparseable frontmatter line: {raw.strip()}')
    return data, errors


def parse_frontmatter(path: Path) -> tuple[dict[str, str], list[str]]:
    return parse_frontmatter_text(path.read_text(encoding='utf-8', errors='replace'))


def canonical_future_path(path: str | Path) -> Path:
    try:
        return Path(path).expanduser().resolve(strict=False)
    except RuntimeError as exc:
        raise ValueError(f'path contains a symbolic-link cycle: {path}') from exc


def paths_alias(left: str | Path, right: str | Path) -> bool:
    a = canonical_future_path(left)
    b = canonical_future_path(right)
    if os.path.normcase(str(a)) == os.path.normcase(str(b)):
        return True
    try:
        return os.path.samefile(a, b)
    except (FileNotFoundError, OSError):
        return False


def path_is_inside(root: str | Path, candidate: str | Path) -> bool:
    root_path = canonical_future_path(root)
    child_path = canonical_future_path(candidate)
    try:
        child_path.relative_to(root_path)
        return True
    except ValueError:
        return False


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


def stage_bytes(destination: Path, data: bytes) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f'.{destination.name}.', suffix='.tmp', dir=destination.parent)
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


def transactional_commit(staged_targets: list[tuple[Path, Path]]) -> list[dict]:
    token = hashlib.sha256(os.urandom(32)).hexdigest()[:16]
    backups: dict[Path, Path] = {}
    committed: list[Path] = []
    recovery: list[dict] = []
    try:
        for _, target in staged_targets:
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists() or target.is_symlink():
                backup = target.with_name(f'.{target.name}.benchmark-backup-{token}')
                if backup.exists() or backup.is_symlink():
                    raise RuntimeError(f'backup path already exists: {backup}')
                os.replace(target, backup)
                backups[target] = backup

        for staged, target in staged_targets:
            os.replace(staged, target)
            committed.append(target)
            fsync_dir(target.parent)

        for backup in backups.values():
            if backup.exists() or backup.is_symlink():
                backup.unlink()
        for _, target in staged_targets:
            fsync_dir(target.parent)
        return recovery
    except Exception as exc:
        rollback_errors: list[dict] = []
        for target in reversed(committed):
            if not (target.exists() or target.is_symlink()):
                continue
            failed = target.with_name(f'.{target.name}.benchmark-failed-{token}')
            try:
                os.replace(target, failed)
                recovery.append({'kind': 'failed-candidate', 'target': str(target), 'preserved_at': str(failed)})
            except Exception as rollback_exc:
                rollback_errors.append({'target': str(target), 'error': str(rollback_exc)})
        for target, backup in backups.items():
            if not (backup.exists() or backup.is_symlink()):
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


def atomic_write_text(path: Path, text: str) -> None:
    staged = stage_bytes(path, text.encode('utf-8'))
    try:
        transactional_commit([(staged, path)])
    finally:
        if staged.exists():
            staged.unlink()


def dump_json(data: object, out: str | Path | None = None) -> None:
    text = json.dumps(data, indent=2, ensure_ascii=False, sort_keys=False) + '\n'
    if out is None:
        print(text, end='', flush=True)
    else:
        atomic_write_text(Path(out), text)


def extract_local_refs(markdown: str) -> list[str]:
    refs: set[str] = set()
    for raw in re.findall(r'\[[^\]]*\]\(([^)]+)\)', markdown):
        ref = raw.strip().split('#', 1)[0].strip().strip('<>')
        if not ref or ref.startswith(('#', 'http://', 'https://', 'mailto:', 'skills://', 'sandbox:')):
            continue
        if Path(ref).is_absolute() or '..' in Path(ref).parts:
            refs.add(ref)
            continue
        refs.add(ref.replace('\\', '/'))
    return sorted(refs)
