from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Iterable

NOISE_DIRS = {'.git', '__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache', 'node_modules'}
NOISE_FILES = {'.DS_Store'}
SECRET_NAME_PATTERNS = [
    re.compile(r'^\.env(?:\..+)?$', re.I),
    re.compile(r'^id_rsa(?:\.pub)?$', re.I),
    re.compile(r'.*\.(?:pem|p12|pfx|key)$', re.I),
    re.compile(r'^(?:credentials|secrets?)(?:\..+)?$', re.I),
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def is_noise(path: Path) -> bool:
    return any(part in NOISE_DIRS for part in path.parts) or path.name in NOISE_FILES or path.suffix == '.pyc'


def iter_files(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob('*')):
        if path.is_symlink():
            yield path
            continue
        if path.is_file() and not is_noise(path.relative_to(root)):
            yield path


def tree_manifest(root: Path) -> list[dict]:
    rows = []
    for path in iter_files(root):
        rel = path.relative_to(root).as_posix()
        if path.is_symlink():
            rows.append({'path': rel, 'type': 'symlink', 'target': os.readlink(path)})
        else:
            rows.append({'path': rel, 'type': 'file', 'size': path.stat().st_size, 'sha256': sha256_file(path)})
    return rows


def tree_hash(root: Path) -> str:
    payload = json.dumps(tree_manifest(root), sort_keys=True, separators=(',', ':')).encode('utf-8')
    return hashlib.sha256(payload).hexdigest()


def parse_frontmatter(skill_md: Path) -> dict[str, str]:
    text = skill_md.read_text(encoding='utf-8')
    if not text.startswith('---\n'):
        return {}
    end = text.find('\n---\n', 4)
    if end < 0:
        return {}
    block = text[4:end]
    result: dict[str, str] = {}
    current_key = None
    for raw in block.splitlines():
        if not raw.strip() or raw.lstrip().startswith('#'):
            continue
        if not raw.startswith((' ', '\t')) and ':' in raw:
            key, value = raw.split(':', 1)
            current_key = key.strip()
            value = value.strip()
            if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                value = value[1:-1]
            result[current_key] = value
        elif current_key and raw.startswith((' ', '\t')):
            result[current_key] += ' ' + raw.strip()
    return result


def markdown_local_links(md_path: Path) -> list[str]:
    text = md_path.read_text(encoding='utf-8', errors='replace')
    links = []
    for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', text):
        target = target.strip().strip('<>')
        if not target or target.startswith(('#', 'http://', 'https://', 'mailto:', 'skills://', 'sandbox:')):
            continue
        target = target.split('#', 1)[0].strip()
        if target:
            links.append(target)
    return links


def resolve_local_link(md_path: Path, target: str) -> Path:
    return (md_path.parent / target).resolve()


def is_secret_like(rel: str) -> bool:
    name = Path(rel).name
    return any(p.match(name) for p in SECRET_NAME_PATTERNS)


def canonical_future_path(path: str | Path) -> Path:
    try:
        return Path(path).expanduser().resolve(strict=False)
    except RuntimeError as exc:
        raise ValueError(f'path contains a symbolic-link cycle: {path}') from exc


def paths_alias(left: str | Path, right: str | Path) -> bool:
    left_resolved = canonical_future_path(left)
    right_resolved = canonical_future_path(right)
    if os.path.normcase(str(left_resolved)) == os.path.normcase(str(right_resolved)):
        return True
    try:
        return os.path.samefile(left_resolved, right_resolved)
    except (FileNotFoundError, OSError):
        return False


def path_is_inside(root: str | Path, candidate: str | Path) -> bool:
    root_resolved = canonical_future_path(root)
    candidate_resolved = canonical_future_path(candidate)
    try:
        candidate_resolved.relative_to(root_resolved)
        return True
    except ValueError:
        return False


def _fsync_directory(directory: Path) -> None:
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


def atomic_write_bytes(path: str | Path, data: bytes) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f'.{target.name}.', suffix='.tmp', dir=target.parent)
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, 'wb') as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, target)
        _fsync_directory(target.parent)
    except Exception:
        if tmp.exists():
            tmp.unlink()
        raise


def dump_json(data: object, out: str | None) -> None:
    text = json.dumps(data, indent=2, sort_keys=False) + '\n'
    if out:
        atomic_write_bytes(out, text.encode('utf-8'))
    else:
        sys.stdout.write(text)
        sys.stdout.flush()
