from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Iterable

NOISE_DIRS = {'.git', '.hg', '.svn', '__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache', 'node_modules', 'dist', 'build'}
NOISE_FILES = {'.DS_Store'}
SECRET_NAME_PATTERNS = [
    re.compile(r'^\.env(?:\..+)?$', re.I),
    re.compile(r'^id_rsa(?:\.pub)?$', re.I),
    re.compile(r'.*\.(?:pem|p12|pfx|key)$', re.I),
    re.compile(r'^(?:credentials|secrets?)(?:\..+)?$', re.I),
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def is_noise(path: Path) -> bool:
    return any(part in NOISE_DIRS for part in path.parts) or path.name in NOISE_FILES or path.suffix.lower() in {'.pyc', '.pyo'}


def is_secret_like(path: str | Path) -> bool:
    name = Path(path).name
    return any(pattern.match(name) for pattern in SECRET_NAME_PATTERNS)


def iter_files(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob('*')):
        rel = path.relative_to(root)
        if is_noise(rel):
            continue
        if path.is_symlink() or path.is_file():
            yield path


def tree_manifest(root: Path) -> list[dict]:
    rows = []
    for path in iter_files(root):
        rel = path.relative_to(root).as_posix()
        if path.is_symlink():
            rows.append({'path': rel, 'type': 'symlink', 'target': os.readlink(path)})
        elif path.is_file():
            rows.append({'path': rel, 'type': 'file', 'size': path.stat().st_size, 'sha256': sha256_file(path)})
    return rows


def tree_hash(root: Path) -> str:
    payload = json.dumps(tree_manifest(root), sort_keys=True, separators=(',', ':')).encode('utf-8')
    return hashlib.sha256(payload).hexdigest()


def parse_frontmatter_scalars(skill_md: Path) -> dict[str, str]:
    text = skill_md.read_text(encoding='utf-8', errors='replace')
    if not text.startswith('---\n'):
        return {}
    end = text.find('\n---\n', 4)
    if end < 0:
        return {}
    result: dict[str, str] = {}
    current_key: str | None = None
    for raw in text[4:end].splitlines():
        if not raw.strip() or raw.lstrip().startswith('#'):
            continue
        if not raw.startswith((' ', '\t')) and ':' in raw:
            key, value = raw.split(':', 1)
            current_key = key.strip()
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
                value = value[1:-1]
            result[current_key] = value
        elif current_key and raw.startswith((' ', '\t')):
            # Keep multiline scalars useful without pretending to parse nested YAML maps.
            if result.get(current_key):
                result[current_key] += ' ' + raw.strip()
    return result


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
    base = canonical_future_path(root)
    path = canonical_future_path(candidate)
    try:
        path.relative_to(base)
        return True
    except ValueError:
        return False


def fsync_dir(directory: Path) -> None:
    if os.name == 'nt':
        return
    try:
        fd = os.open(directory, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(fd)
    except OSError:
        pass
    finally:
        os.close(fd)


def stage_bytes(target: Path, data: bytes) -> Path:
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f'.{target.name}.', suffix='.tmp', dir=target.parent)
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


def atomic_write_bytes(path: str | Path, data: bytes) -> None:
    target = Path(path)
    tmp = stage_bytes(target, data)
    try:
        os.replace(tmp, target)
        fsync_dir(target.parent)
    except Exception:
        if tmp.exists():
            tmp.unlink()
        raise


def dump_json(data: object, out: str | None = None) -> None:
    payload = (json.dumps(data, indent=2, sort_keys=False) + '\n').encode('utf-8')
    if out:
        atomic_write_bytes(out, payload)
    else:
        sys.stdout.write(payload.decode('utf-8'))
        sys.stdout.flush()
