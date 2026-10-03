#!/usr/bin/env python3
"""Portable artifact data contract. Never imports or executes repository content."""
from __future__ import annotations

import hashlib
import json
import os
import re
import stat
import tempfile
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any, Iterator

VERSION = '1.0.0'
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_RECORD_BYTES = 128 * 1024
MAX_RECORDS = 10000
FORBIDDEN_PARTS = {'.git', '.hg', '.svn', 'node_modules', '__pycache__', '.venv', 'venv'}
SENSITIVE_SUFFIXES = {'.pem', '.key', '.p12', '.pfx', '.crt', '.kdbx'}
SECRET_RE = re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\b(?:gh[pousr]_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16})\b|\bBearer\s+[A-Za-z0-9._~+/-]{20,}', re.I)

class ContractError(ValueError):
    """A safe diagnostic code; callers must not print untrusted document content."""

def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + '\n').encode('utf-8')

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def no_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ContractError('DUPLICATE_JSON_KEY')
        result[key] = value
    return result

def load_json(path: Path, limit: int = MAX_RECORD_BYTES) -> Any:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > limit:
        raise ContractError('INVALID_JSON_FILE')
    try:
        return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=no_duplicate_keys,
                          parse_constant=lambda value: (_ for _ in ()).throw(ContractError('NONFINITE_JSON')))
    except (UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ContractError('INVALID_JSON') from exc

def safe_relative(value: str) -> PurePosixPath:
    if not isinstance(value, str) or not value or len(value) > 1100 or '\\' in value or ':' in value:
        raise ContractError('INVALID_RELATIVE_PATH')
    if any(c in value for c in '*?"<>|'):
        raise ContractError('NONPORTABLE_PATH')
    parts = value.split('/')
    if any(not p or p in {'.', '..'} or p.endswith((' ', '.')) or any(ord(c) < 32 for c in p) for p in parts):
        raise ContractError('INVALID_RELATIVE_PATH')
    if any(p.lower() in FORBIDDEN_PARTS or p.lower().startswith('.env') for p in parts):
        raise ContractError('PROTECTED_PATH')
    if any(re.fullmatch(r'(con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\..*)?', p, re.I) for p in parts):
        raise ContractError('NONPORTABLE_PATH')
    path = PurePosixPath(value)
    if path.is_absolute() or path.suffix.lower() in SENSITIVE_SUFFIXES:
        raise ContractError('PROTECTED_PATH')
    return path

def repository_root(root: Path) -> Path:
    """Reject aliases before resolution erases evidence of a symlink ancestor."""
    root = Path(root)
    if any(part.is_symlink() for part in (root, *root.parents)):
        raise ContractError('SYMLINK_ROOT')
    base = root.resolve(strict=True)
    if not base.is_dir():
        raise ContractError('REPOSITORY_NOT_DIRECTORY')
    return base

def confined(root: Path, relative: str, *, must_exist: bool = False, regular: bool = False) -> Path:
    base = repository_root(root)
    rel = safe_relative(relative)
    path = base
    for part in rel.parts:
        path = path / part
        if path.is_symlink():
            raise ContractError('SYMLINK_PATH')
    resolved = path.resolve(strict=must_exist)
    if not resolved.is_relative_to(base) or resolved == base:
        raise ContractError('PATH_ESCAPE')
    if regular:
        if not path.is_file() or path.stat().st_nlink != 1:
            raise ContractError('NOT_EXCLUSIVE_REGULAR_FILE')
    return path

def timestamp(value: str) -> datetime:
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z', value):
        raise ContractError('INVALID_TIMESTAMP')
    try:
        return datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ')
    except ValueError as exc:
        raise ContractError('INVALID_TIMESTAMP') from exc

def schema_errors(value: Any, schema: dict, location: str = '$') -> list[str]:
    """Validate every keyword used by the bundled closed schemas, without network I/O."""
    errors = []
    if 'anyOf' in schema:
        return [] if any(not schema_errors(value, item, location) for item in schema['anyOf']) else [location + ':ANY_OF']
    if 'const' in schema and (type(value) is not type(schema['const']) or value != schema['const']):
        errors.append(location + ':CONST')
    if 'enum' in schema and not any(type(value) is type(v) and value == v for v in schema['enum']):
        errors.append(location + ':ENUM')
    kind = schema.get('type')
    types = {'object': dict, 'array': list, 'string': str, 'boolean': bool, 'integer': int, 'null': type(None)}
    if kind and (kind not in types or type(value) is not types[kind]):
        return errors + [location + ':TYPE']
    if isinstance(value, dict):
        properties = schema.get('properties', {})
        if any(k not in value for k in schema.get('required', [])):
            errors.append(location + ':REQUIRED')
        if schema.get('additionalProperties') is False and any(k not in properties for k in value):
            errors.append(location + ':UNKNOWN_PROPERTY')
        for key, sub in properties.items():
            if key in value:
                errors.extend(schema_errors(value[key], sub, location + '.' + key))
    if isinstance(value, list):
        if len(value) < schema.get('minItems', 0) or len(value) > schema.get('maxItems', MAX_RECORDS):
            errors.append(location + ':ITEM_COUNT')
        if schema.get('uniqueItems') and len({digest(canonical_bytes(v)) for v in value}) != len(value):
            errors.append(location + ':DUPLICATE_ITEM')
        for item in value:
            errors.extend(schema_errors(item, schema.get('items', {}), location + '[]'))
    if isinstance(value, str):
        if len(value) < schema.get('minLength', 0) or len(value) > schema.get('maxLength', 100000):
            errors.append(location + ':LENGTH')
        if 'pattern' in schema and re.search(schema['pattern'], value) is None:
            errors.append(location + ':PATTERN')
        if schema.get('format') == 'date-time':
            try:
                timestamp(value)
            except ContractError:
                errors.append(location + ':DATE_TIME')
    return errors

def schema_for(name: str) -> dict:
    return load_json(Path(__file__).resolve().parents[1] / 'references' / name)

def source_bytes(path: Path) -> bytes:
    if path.is_symlink() or not path.is_file() or path.stat().st_nlink != 1:
        raise ContractError('INVALID_SOURCE_FILE')
    if path.stat().st_size > MAX_SOURCE_BYTES:
        raise ContractError('SOURCE_TOO_LARGE')
    data = path.read_bytes()
    if SECRET_RE.search(data.decode('utf-8', errors='replace')):
        raise ContractError('SECRET_MATERIAL_REJECTED')
    return data

def validate_record(record: Any, repo: Path | None = None, manifest: Path | None = None) -> None:
    errors = schema_errors(record, schema_for('artifact-envelope.schema.json'))
    if errors:
        raise ContractError('INVALID_ENVELOPE:' + ','.join(errors[:8]))
    if not record['artifact_id'].startswith(record['producer'] + ':'):
        raise ContractError('PRODUCER_NAMESPACE_MISMATCH')
    if timestamp(record['created_at']) > timestamp(record['updated_at']):
        raise ContractError('INVERTED_ARTIFACT_DATES')
    safe_relative(record['source']['path'])
    if record['source']['path'].split('/')[0] == '.rhapsodia':
        raise ContractError('DERIVED_SOURCE_FORBIDDEN')
    privacy = record['privacy']
    if 'public' in privacy['allowed_destinations'] and (privacy['classification'] != 'public' or not privacy['external_share_allowed']):
        raise ContractError('PUBLIC_EXPORT_DENIED')
    if privacy['classification'] != 'public' and privacy['external_share_allowed']:
        raise ContractError('PRIVACY_CONTRADICTION')
    if SECRET_RE.search(json.dumps(record)):
        raise ContractError('SECRET_METADATA_REJECTED')
    if any(r['target'] == record['artifact_id'] for r in record['relations']):
        raise ContractError('SELF_RELATION')
    if repo is not None:
        source = confined(repo, record['source']['path'])
        expected_manifest = Path(str(source) + '.artifact.json')
        if manifest is not None and manifest != expected_manifest:
            raise ContractError('MANIFEST_NOT_SOURCE_SIDECAR')
        if record['lifecycle'] == 'removed':
            if source.exists():
                raise ContractError('REMOVED_SOURCE_STILL_EXISTS')
        elif digest(source_bytes(source)) != record['source']['sha256']:
            raise ContractError('STALE_SOURCE_HASH')

def discover(repo: Path, roots: list[str]) -> list[Path]:
    found = set()
    for relative in roots:
        if isinstance(relative,str) and relative.split('/')[0].startswith('.'):
            raise ContractError('HIDDEN_SOURCE_ROOT')
        root = confined(repo, relative)
        if not root.exists():
            continue
        if not root.is_dir():
            raise ContractError('SOURCE_ROOT_NOT_DIRECTORY')
        for current, dirs, files in os.walk(root, followlinks=False):
            here = Path(current)
            if len(here.relative_to(repo.resolve()).parts) > 40:
                raise ContractError('SCAN_DEPTH_LIMIT')
            # Symlinks within an explicitly indexed tree are errors, never silently followed.
            for name in dirs + files:
                if (here / name).is_symlink():
                    raise ContractError('SYMLINK_IN_SOURCE_TREE')
            dirs[:] = sorted(d for d in dirs if d.lower() not in FORBIDDEN_PARTS and not d.startswith('.'))
            for name in sorted(files):
                if name.endswith('.artifact.json'):
                    path = confined(repo, (here / name).relative_to(repo.resolve()).as_posix(), must_exist=True, regular=True)
                    found.add(path)
                    if len(found) > MAX_RECORDS:
                        raise ContractError('RECORD_LIMIT')
    return sorted(found)

@contextmanager
def exclusive_lock(path: Path) -> Iterator[None]:
    if path.is_symlink():
        raise ContractError('UNSAFE_LOCK')
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise ContractError('WRITE_LOCK_HELD') from exc
    try:
        with os.fdopen(fd, 'w') as handle:
            handle.write(str(os.getpid()))
            handle.flush()
            os.fsync(handle.fileno())
        yield
    finally:
        path.unlink(missing_ok=True)

def atomic_write(path: Path, data: bytes) -> None:
    """Commit one output without truncating the last good file on failure."""
    if path.is_symlink() or (path.exists() and (not path.is_file() or path.stat().st_nlink != 1)):
        raise ContractError('UNSAFE_OUTPUT')
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix='.' + path.name + '-', suffix='.tmp', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temp, 0o600)
        os.replace(temp, path)
    finally:
        Path(temp).unlink(missing_ok=True)

def validate_actions(receipt: Any, repo: Path) -> None:
    errors = schema_errors(receipt, schema_for('artifact-actions.schema.json'))
    if errors:
        raise ContractError('INVALID_ACTIONS:' + ','.join(errors[:8]))
    if SECRET_RE.search(json.dumps(receipt)):
        raise ContractError('SECRET_ACTION_METADATA_REJECTED')
    identities = set()
    for action in receipt['artifact_actions']:
        if action['artifact_id'] in identities:
            raise ContractError('DUPLICATE_ACTION')
        identities.add(action['artifact_id'])
        path = confined(repo, action['manifest_path'], must_exist=True, regular=True)
        if digest(path.read_bytes()) != action['manifest_sha256']:
            raise ContractError('STALE_ACTION_RECEIPT')
        record = load_json(path)
        validate_record(record, repo, path)
        if record['producer'] != receipt['owner'] or record['workflow_id'] != receipt['workflow_id']:
            raise ContractError('ACTION_OWNER_OR_WORKFLOW_MISMATCH')
        if any(record[k] != action[k] for k in ('artifact_id', 'artifact_type')) or record['source']['path'] != action['source_path']:
            raise ContractError('ACTION_IDENTITY_MISMATCH')
        expected_sha = None if record['lifecycle'] == 'removed' else record['source']['sha256']
        if action['source_sha256'] != expected_sha:
            raise ContractError('ACTION_SOURCE_MISMATCH')
        if (action['action'] == 'removed' and record['lifecycle'] != 'removed') or (record['lifecycle'] == 'removed' and action['action'] not in {'removed', 'unchanged'}):
            raise ContractError('ACTION_LIFECYCLE_MISMATCH')
        if action['action'] == 'deprecated' and record['lifecycle'] != 'deprecated':
            raise ContractError('ACTION_LIFECYCLE_MISMATCH')
        previous = action['previous_manifest_sha256']
        current = action['manifest_sha256']
        if not action['reason'].strip():
            raise ContractError('EMPTY_ACTION_REASON')
        if action['action'] == 'created' and previous is not None:
            raise ContractError('CREATED_WITH_PREVIOUS_RECORD')
        if action['action'] == 'unchanged' and previous != current:
            raise ContractError('UNCHANGED_REVISION_MISMATCH')
        if action['action'] in {'updated', 'removed'} and (previous is None or previous == current):
            raise ContractError('INVALID_ACTION_REVISION')
        if action['action'] == 'deprecated' and previous == current:
            raise ContractError('INVALID_ACTION_REVISION')

