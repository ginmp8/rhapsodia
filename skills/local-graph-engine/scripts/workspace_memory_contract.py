"""Bounded, source-pinned workspace knowledge; never command execution or authority."""
from __future__ import annotations
import hashlib
import os
from pathlib import Path
import platform
import re
import stat
import sys
from graph_common import canonical, digest

MAX_INPUT = 65536
MAX_FILE = 8 * 1024 * 1024
KEY = re.compile(r'[a-z0-9][a-z0-9-]{0,95}\Z')
HASH = re.compile(r'[0-9a-f]{64}\Z')
ENV = re.compile(r'[A-Za-z_][A-Za-z0-9_]{0,127}\Z')
PRIVATE = {'.git', '.aws', '.azure', '.ssh', '.kube', '.gnupg', '.npmrc', '.pypirc'}
PUBLIC_ENV = {'.env.example', '.env.sample', '.env.template'}
SECRET = re.compile(r'(?i)(?:AKIA|ASIA)[A-Z0-9]{16}|(?:gh[pousr]_|github_pat_)[A-Za-z0-9_]{16,}|eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+|-----BEGIN [A-Z ]*PRIVATE KEY-----|(?:password|passwd|secret|access[_-]?key|api[_-]?key|token|authorization)\s*[=:]\s*(?!<|\$\{|\{\{|\[REDACTED\])[^\s]{3,}|https?://[^\s/?]+:[^\s/@]+@|https?://[^\s]*[?&](?:code|token|key|signature)=')


class MemoryFault(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code

    def result(self):
        return {'status': 'blocked', 'error': {'code': self.code, 'message': str(self)}}


def text(value, limit=1024):
    if not isinstance(value, str) or not value.strip() or len(value.encode('utf-8')) > limit or any(ord(c) < 32 for c in value):
        raise MemoryFault('INVALID_INPUT', 'Expected bounded nonempty single-line text.')
    if SECRET.search(value):
        raise MemoryFault('SENSITIVE_INPUT', 'Potential credentials detected; supply a sanitized signature or placeholder, never raw logs or secrets.')
    return value


def workspace_path(value: Path) -> Path:
    if not value.is_dir() or value.is_symlink():
        raise MemoryFault('INVALID_ROOT', 'Select an existing workspace directory, not a symbolic link.')
    return value.resolve()


def path_in(root: Path, relative: str, *, state=False) -> Path:
    text(relative, 1024)
    if any(c in relative for c in '\\:%?#'):
        raise MemoryFault('UNSAFE_PATH', 'Only portable relative paths are supported.')
    parts = relative.split('/')
    if any(p in ('', '.', '..') or p.casefold() in PRIVATE or p.casefold().endswith(('.pem', '.key')) or
           (p.casefold().startswith('.env') and p.casefold() not in PUBLIC_ENV) or p.endswith((' ', '.')) or
           re.fullmatch(r'(?i)(con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\..*)?', p) for p in parts):
        raise MemoryFault('UNSAFE_PATH', 'Protected or ambiguous path component.')
    if not state and parts[0].casefold() == '.rhapsodia':
        # Sanitized owner-authored receipts are allowed; never use a DB/pointer as its own evidence.
        if parts[:3] != ['.rhapsodia', 'graph', 'evidence'] or len(parts) < 4:
            raise MemoryFault('UNSAFE_PATH', 'Only explicitly sanitized graph/evidence files may be knowledge sources inside local state.')
    current = root
    for part in parts:
        current = current / part
        if current.is_symlink():
            raise MemoryFault('UNSAFE_PATH', 'Symbolic links are not supported in state or evidence paths.')
        try:
            info = current.stat()
        except FileNotFoundError:
            continue
        if not (stat.S_ISREG(info.st_mode) or stat.S_ISDIR(info.st_mode)) or (state and stat.S_ISREG(info.st_mode) and info.st_nlink > 1):
            raise MemoryFault('UNSAFE_PATH', 'Special or hard-linked state files are not supported.')
    if not current.resolve().is_relative_to(root):
        raise MemoryFault('UNSAFE_PATH', 'Path escapes the selected workspace.')
    return current


def pin(root: Path, relative: str) -> dict:
    path = path_in(root, relative)
    try:
        before = path.stat()
    except FileNotFoundError as exc:
        raise MemoryFault('MISSING_SOURCE', 'A selected source is missing; do not invent its contents.') from exc
    if not stat.S_ISREG(before.st_mode):
        raise MemoryFault('UNSAFE_PATH', 'A source must be a regular file, not a directory or device.')
    if before.st_size > MAX_FILE:
        raise MemoryFault('INPUT_TOO_LARGE', 'Select a source no larger than eight MiB.')
    with path.open('rb') as stream:
        content = stream.read(MAX_FILE + 1)
    after = path.stat()
    if len(content) > MAX_FILE or (before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (after.st_size, after.st_mtime_ns, after.st_ctime_ns):
        raise MemoryFault('STALE_SOURCE', 'Source changed during hashing; read it again before publication.')
    return {'path': relative, 'sha256': hashlib.sha256(content).hexdigest()}


def environment_id() -> str:
    # Persist digests, not environment values, usernames, machine names or absolute tool paths.
    return digest({'os': platform.system(), 'machine': platform.machine(), 'host': platform.node(),
                   'python': os.path.abspath(sys.executable), 'python_version': list(sys.version_info[:3]),
                   'path': os.environ.get('PATH', ''), 'pathext': os.environ.get('PATHEXT', '')})


def normalize(root: Path, value: dict) -> dict:
    required = {'schema', 'key', 'kind', 'title', 'summary', 'tags', 'sources'}
    optional = {'expected_revision', 'symptom', 'cause', 'resolution', 'verification', 'evidence_status',
                'applicability', 'environment_variables', 'ttl_seconds'}
    if not isinstance(value, dict) or not required <= value.keys() or value.keys() - required - optional:
        raise MemoryFault('INVALID_INPUT', 'Missing or unsupported knowledge fields; environment values and raw logs are not accepted.')
    if value['schema'] != 'workspace-knowledge-v1' or value['kind'] not in {'reference', 'remedy'} or not isinstance(value['key'], str) or not KEY.fullmatch(value['key']) or value['key'] in {'root', 'workspace'}:
        raise MemoryFault('INVALID_INPUT', 'Invalid knowledge schema, kind or stable key.')
    result = dict(value)
    result['title'] = text(value['title'], 200)
    result['summary'] = text(value['summary'], 1200)
    tags = value['tags']
    if not isinstance(tags, list) or len(tags) > 16:
        raise MemoryFault('INVALID_INPUT', 'At most sixteen sanitized tags are supported.')
    result['tags'] = sorted(set(text(tag, 80) for tag in tags))
    sources = value['sources']
    if not isinstance(sources, list) or len(sources) > 16 or (value['kind'] == 'reference' and not sources):
        raise MemoryFault('INVALID_INPUT', 'References require one to sixteen content-pinned sources.')
    verified = []
    for source in sources:
        if not isinstance(source, dict) or set(source) != {'path', 'sha256'} or not isinstance(source['sha256'], str) or not HASH.fullmatch(source['sha256']):
            raise MemoryFault('INVALID_INPUT', 'Each source requires only its relative path and SHA-256.')
        actual = pin(root, source['path'])
        if actual != source:
            raise MemoryFault('STALE_SOURCE', 'An observed source pin no longer matches; re-read rather than silently repinning.')
        if actual not in verified:
            verified.append(actual)
    result['sources'] = sorted(verified, key=lambda p: p['path'])
    expected = result.pop('expected_revision', None)
    if expected is not None and (not isinstance(expected, str) or not HASH.fullmatch(expected)):
        raise MemoryFault('INVALID_INPUT', 'Expected revision must be a SHA-256 identity.')
    if value['kind'] == 'reference':
        if set(value) & (optional - {'expected_revision'}):
            raise MemoryFault('INVALID_INPUT', 'Remedy fields cannot be attached to a repository reference.')
    else:
        needed = {'symptom', 'cause', 'resolution', 'verification', 'evidence_status', 'applicability', 'environment_variables', 'ttl_seconds'}
        if not needed <= value.keys():
            raise MemoryFault('INVALID_INPUT', 'A remedy requires applicability, cause, resolution, verification, status and expiry.')
        for field in ('symptom', 'cause', 'resolution', 'verification'):
            result[field] = text(value[field], 1800)
        if value['evidence_status'] not in {'observed-success', 'documented', 'hypothesis', 'failed', 'auth-required'}:
            raise MemoryFault('INVALID_INPUT', 'Unsupported evidence status.')
        applicability = value['applicability']
        allowed = {'os', 'shell', 'shell_version', 'language_mode', 'tool', 'tool_version', 'configuration'}
        if not isinstance(applicability, dict) or not applicability or applicability.keys() - allowed:
            raise MemoryFault('INVALID_INPUT', 'Declare bounded applicability such as shell, language mode or tool version.')
        result['applicability'] = {key: text(item, 200) for key, item in sorted(applicability.items())}
        variables = value['environment_variables']
        if not isinstance(variables, list) or len(variables) > 32 or any(not isinstance(item, str) or not ENV.fullmatch(item) for item in variables):
            raise MemoryFault('INVALID_INPUT', 'Environment metadata contains names only, never values.')
        result['environment_variables'] = sorted(set(variables))
        ttl = value['ttl_seconds']
        if isinstance(ttl, bool) or not isinstance(ttl, int) or not 60 <= ttl <= 2592000:
            raise MemoryFault('INVALID_INPUT', 'Remedy TTL must be 60..2592000 seconds.')
    return result
