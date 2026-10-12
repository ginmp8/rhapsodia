#!/usr/bin/env python3
"""Read-only, bounded forensic intake for user-supplied files, folders and archives.

Python 3.10+ stdlib only. Never executes target content, extracts archives,
resolves URLs, downloads packages or uses a shell.
"""
from __future__ import annotations

import argparse
import collections
import contextlib
import dataclasses
import hashlib
import json
import os
import posixpath
import re
import stat
import struct
import sys
import tarfile
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any, Iterator

CHUNK = 65536
MAX_LEXICAL_LINE = 8192
SKIP_DIRS = {'.git', 'node_modules', '.venv', 'venv', '__pycache__', '.next', '.turbo'}
TEXT_EXTENSIONS = {'.ts', '.tsx', '.js', '.jsx', '.mjs', '.cjs', '.mts', '.cts', '.json', '.jsonc', '.yaml', '.yml', '.toml', '.xml', '.html', '.css', '.scss', '.cs', '.csproj', '.props', '.targets', '.py', '.pyi', '.rs', '.go', '.java', '.kt', '.swift', '.c', '.cc', '.cpp', '.h', '.hpp', '.sql', '.sh', '.ps1', '.md', '.txt', '.lock', '.gradle', '.properties', '.vue', '.svelte', '.graphql', '.proto', '.tf', '.tfvars'}
SOURCE_EXTENSIONS = {'.ts', '.tsx', '.js', '.jsx', '.mjs', '.cjs', '.mts', '.cts', '.py', '.csproj', '.props', '.targets', '.html', '.htm'}
SYMBOL_EXTENSIONS = {'.cs', '.py', '.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs', '.java', '.go', '.rs'}
TYPE_DECL = re.compile(r'^\s*(?:(?:public|protected|private|internal|static|sealed|abstract|partial|readonly|file|unsafe|export|default|declare)\s+)*(class|interface|struct|enum|record(?:\s+(?:class|struct))?)\s+([A-Za-z_]\w*)')
CS_METHOD_DECL = re.compile(r'^\s*(?:(?:public|protected|private|internal|static|async|virtual|override|abstract|sealed|extern|unsafe|partial|new)\s+)+[A-Za-z_][\w<>,.\[\]?]*\s+([A-Za-z_]\w*)\s*(?:<[^>]+>)?\s*\(')
PY_SYMBOL_DECL = re.compile(r'^\s*(?:(async)\s+)?(def|class)\s+([A-Za-z_]\w*)\b')
JS_SYMBOL_DECL = re.compile(r'^\s*(?:(?:export|default|declare)\s+)*(?:(?:async)\s+)?(function|class|interface|type|enum)\s+([A-Za-z_$][\w$]*)')
JS_EXPORT_BINDING = re.compile(r'^\s*export\s+(?:(?:default|declare)\s+)?(?:const|let)\s+([A-Za-z_$][\w$]*)\s*=')
JS_ARROW_DECL = re.compile(r'^\s*(?:export\s+)?(?:const|let)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:(?:async)\s+)?(?:\([^)]*\)|[A-Za-z_$][\w$]*)\s*=>')
GO_FUNC_DECL = re.compile(r'^\s*func\s+(?:\([^)]*\)\s*)?([A-Za-z_]\w*)\s*\(')
RUST_FUNC_DECL = re.compile(r'^\s*(?:pub(?:\([^)]*\))?\s+)?(?:async\s+)?fn\s+([A-Za-z_]\w*)\s*[<(]')
SECRET_PATTERNS = [
    (re.compile(r'(?i)(authorization\s*[:=]\s*bearer\s+)[^\s,"\']+'), r'\1[REDACTED]'),
    (re.compile(r'(?i)((?:password|secret|api[_-]?key|access[_-]?token|client[_-]?secret)\s*[=:]\s*["\']?)[^\s,"\']{4,}'), r'\1[REDACTED]'),
    (re.compile(r'AKIA[0-9A-Z]{16}'), '[REDACTED_AWS_KEY]'),
    (re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----.*'), '[REDACTED_PRIVATE_KEY]'),
]
JS_IMPORT = re.compile(r'''(?:\b(?:import|export)\b[^\n;]*?\bfrom\s*|\bimport\s*\(\s*|\brequire\s*\(\s*|\bimport\s+)["']([^"']{1,512})["']''')
PY_FROM = re.compile(r'^\s*from\s+(\.+[\w.]*)\s+import\b')
PROJECT_REF = re.compile(r'<ProjectReference\s+[^>]*Include\s*=\s*["\']([^"\']+)["\']', re.I)
HTML_ASSET = re.compile(r'<(?:script|link|img)\b[^>]*?\b(?:src|href)\s*=\s*["\']([^"\']+)["\']', re.I)


class IntakeError(Exception):
    """The requested static input cannot be inspected under current limits."""


@dataclasses.dataclass(frozen=True)
class Limits:
    max_files: int = 12000
    max_item_bytes: int = 32 * 1024 * 1024
    max_total_bytes: int = 256 * 1024 * 1024
    max_text_bytes: int = 512 * 1024
    max_matches: int = 150
    max_edges: int = 15000


@dataclasses.dataclass
class Member:
    path: str
    size: int
    token: Any
    compressed: int | None = None
    reason: str | None = None


def safe_archive_name(name: str) -> str:
    # Harmless tar './' prefixes are conventional; parent traversals are not.
    while name.startswith('./'):
        name = name[2:]
    # No archive extraction is performed, but reject dangerous identities anyway.
    if not name or '\x00' in name or '\\' in name or name.startswith('/'):
        raise IntakeError(f'unsafe archive path: {name!r}')
    parts = name.rstrip('/').split('/')
    if not parts or any(p in ('', '.', '..') for p in parts) or ':' in parts[0]:
        raise IntakeError(f'unsafe archive path: {name!r}')
    return '/'.join(parts)


def detect_format(head: bytes, name: str) -> str:
    if head.startswith(b'\x7fELF'):
        return 'elf'
    if head.startswith(b'\x00asm'):
        return 'wasm'
    if head.startswith(b'SQLite format 3\x00'):
        return 'sqlite'
    if head.startswith(b'%PDF-'):
        return 'pdf'
    if head.startswith(b'\x89PNG\r\n\x1a\n'):
        return 'png'
    if head.startswith(b'\xff\xd8\xff'):
        return 'jpeg'
    if head.startswith((b'GIF87a', b'GIF89a')):
        return 'gif'
    if head.startswith(b'\xca\xfe\xba\xbe'):
        # CAFEBABE is shared by Java .class and big-endian Mach-O fat.
        # Do not claim an unambiguous identification from four bytes alone.
        if len(head) >= 8:
            minor, major = struct.unpack_from('>HH', head, 4)
            if major in range(45, 81) and minor in (0, 0xFFFF):
                return 'java-class-candidate'
            count = struct.unpack_from('>I', head, 4)[0]
            if 1 <= count <= 32 and len(head) >= 8 + 20 * count:
                return 'mach-o-fat-candidate'
        return 'java-class-or-mach-o-fat'
    if head[:4] in (b'\xfe\xed\xfa\xce', b'\xce\xfa\xed\xfe', b'\xfe\xed\xfa\xcf', b'\xcf\xfa\xed\xfe', b'\xbe\xba\xfe\xca'):
        return 'mach-o'
    if head.startswith(b'dex\n'):
        return 'dex'
    if head.startswith(b'MZ'):
        return 'managed-pe' if is_managed_pe(head) else 'pe-or-dos'
    if head.startswith(b'PK\x03\x04'):
        return 'zip-member-or-archive'
    if head.startswith(b'\x1f\x8b'):
        return 'gzip'
    if head.startswith(b'7z\xbc\xaf\x27\x1c'):
        return '7z'
    ext = PurePosixPath(name).suffix.lower()
    if ext in TEXT_EXTENSIONS or PurePosixPath(name).name in ('Dockerfile', 'Makefile', '.gitignore', '.env.example', 'LICENSE', 'AGENTS.md'):
        return 'text-by-name'
    if head and b'\x00' not in head and sum(b < 9 or (13 < b < 32) for b in head) <= max(2, len(head) // 50):
        return 'text-likely'
    return 'binary-or-unknown'


def is_managed_pe(head: bytes) -> bool:
    # Presence of an IMAGE_DIRECTORY_ENTRY_COM_DESCRIPTOR is a marker, not IL decoding.
    try:
        if len(head) < 0x40:
            return False
        pe_offset = struct.unpack_from('<I', head, 0x3C)[0]
        if pe_offset > len(head) - 24 or head[pe_offset:pe_offset + 4] != b'PE\0\0':
            return False
        opt_start = pe_offset + 24
        opt_size = struct.unpack_from('<H', head, pe_offset + 20)[0]
        magic = struct.unpack_from('<H', head, opt_start)[0]
        dirs = {0x10B: 96, 0x20B: 112}.get(magic)
        if dirs is None or opt_size < dirs + 8 * 15:
            return False
        data = opt_start + dirs + 14 * 8
        if data + 8 > min(len(head), opt_start + opt_size):
            return False
        rva, size = struct.unpack_from('<II', head, data)
        return rva != 0 and size >= 0x48
    except (IndexError, ValueError, struct.error):
        return False


class Reader:
    def __init__(self, target: Path, limits: Limits, include_dependencies: bool = False):
        self.target = target.expanduser().resolve()
        self.limits = limits
        self.include_dependencies = include_dependencies
        self.mode: str | None = None
        self.handle: Any = None
        self.members: list[Member] = []
        self.notes: list[str] = []
        self.partial = False

    def __enter__(self) -> 'Reader':
        if not self.target.exists():
            raise IntakeError(f'input not found: {self.target}')
        if self.target.is_dir():
            self.mode = 'directory'
            self._directory_members()
        elif self.target.is_file() and zipfile.is_zipfile(self.target):
            self.mode = 'zip'
            self.handle = zipfile.ZipFile(self.target, 'r')
            self._zip_members()
        elif self.target.is_file() and tarfile.is_tarfile(self.target):
            self.mode = 'tar'
            self.handle = tarfile.open(self.target, 'r:*')
            self._tar_members()
        elif self.target.is_file():
            self.mode = 'file'
            self.members = [Member(self.target.name, self.target.stat().st_size, self.target)]
        else:
            raise IntakeError('non-regular or unreadable input')
        self.members.sort(key=lambda x: x.path)
        return self

    def __exit__(self, *exc: Any) -> None:
        if self.handle is not None:
            self.handle.close()

    def _add(self, member: Member) -> None:
        if len(self.members) >= self.limits.max_files:
            if not self.partial:
                self.notes.append(f'file count exceeds {self.limits.max_files}; inventory truncated')
                self.partial = True
            return
        self.members.append(member)

    def _directory_members(self) -> None:
        for parent, dirs, files in os.walk(self.target, followlinks=False):
            if self.partial and len(self.members) >= self.limits.max_files:
                break
            chosen = []
            for d in sorted(dirs):
                path = Path(parent) / d
                if path.is_symlink():
                    self.notes.append(f'symlink directory skipped: {path.relative_to(self.target).as_posix()}')
                    self.partial = True
                elif not self.include_dependencies and d in SKIP_DIRS:
                    self.notes.append(f'excluded directory: {path.relative_to(self.target).as_posix()}')
                    self.partial = True
                else:
                    chosen.append(d)
            dirs[:] = chosen
            for name in sorted(files):
                path = Path(parent) / name
                rel = path.relative_to(self.target).as_posix()
                st = path.lstat()
                if not stat.S_ISREG(st.st_mode):
                    self.notes.append(f'non-regular file skipped: {rel}')
                    self.partial = True
                    continue
                self._add(Member(rel, st.st_size, path))

    def _zip_members(self) -> None:
        if len(self.handle.infolist()) > self.limits.max_files:
            self.partial = True
            self.notes.append(f'zip contains more than {self.limits.max_files} entries')
        seen: set[str] = set()
        for info in self.handle.infolist():
            if info.is_dir():
                safe_archive_name(info.filename)
                continue
            rel = safe_archive_name(info.filename)
            if rel in seen:
                raise IntakeError(f'duplicate archive member path: {rel}')
            seen.add(rel)
            is_link = (info.external_attr >> 16) & 0o170000 == 0o120000
            reason = 'symlink-not-read' if is_link else ('encrypted-not-read' if info.flag_bits & 1 else None)
            self._add(Member(rel, info.file_size, info, info.compress_size, reason))

    def _tar_members(self) -> None:
        seen: set[str] = set()
        for info in self.handle:
            if len(self.members) >= self.limits.max_files:
                self.partial = True
                self.notes.append(f'tar member limit {self.limits.max_files} reached; inventory truncated')
                break
            if info.isdir():
                if info.name.rstrip('/') in ('.', ''):
                    continue
                safe_archive_name(info.name.rstrip('/'))
                continue
            rel = safe_archive_name(info.name)
            if rel in seen:
                raise IntakeError(f'duplicate archive member path: {rel}')
            seen.add(rel)
            self._add(Member(rel, info.size, info, None, None if info.isfile() else 'non-regular-entry-not-read'))

    @contextlib.contextmanager
    def open(self, member: Member) -> Iterator[Any]:
        if member.reason:
            raise IntakeError(f'{member.path}: {member.reason}')
        if self.mode in ('directory', 'file'):
            # Refuse final-component symlinks even if an attacker swaps a member.
            flags = os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0)
            with os.fdopen(os.open(str(member.token), flags), 'rb') as fp:
                if not stat.S_ISREG(os.fstat(fp.fileno()).st_mode):
                    raise IntakeError('not a regular file')
                yield fp
        elif self.mode == 'zip':
            with self.handle.open(member.token, 'r') as fp:
                yield fp
        else:
            fp = self.handle.extractfile(member.token)
            if fp is None:
                raise IntakeError('tar member cannot be opened')
            with fp:
                yield fp


def sha256_path(path: Path, max_bytes: int) -> str | None:
    if path.is_dir() or path.stat().st_size > max_bytes:
        return None
    digest = hashlib.sha256()
    with path.open('rb') as fp:
        for block in iter(lambda: fp.read(CHUNK), b''):
            digest.update(block)
    return digest.hexdigest()


def archive_profile(reader: Reader) -> str | None:
    if reader.mode not in ('zip', 'tar'):
        return None
    names = {m.path.lower() for m in reader.members}
    if 'androidmanifest.xml' in names and any(x.endswith('classes.dex') for x in names):
        return 'android-apk'
    if any(n.startswith('payload/') and '.app/' in n for n in names):
        return 'apple-ipa'
    if 'word/document.xml' in names:
        return 'office-docx'
    if 'xl/workbook.xml' in names:
        return 'office-xlsx'
    if 'ppt/presentation.xml' in names:
        return 'office-pptx'
    if any(n.endswith('.nuspec') for n in names):
        return 'nuget-package'
    if any(n.endswith('.dist-info/metadata') for n in names):
        return 'python-wheel'
    if 'meta-inf/manifest.mf' in names and any(n.endswith('.class') for n in names):
        return 'java-jar'
    return reader.mode


def inventory(reader: Reader) -> dict[str, Any]:
    limits = reader.limits
    budget = 0
    entries: list[dict[str, Any]] = []
    notes = list(reader.notes)
    complete = not reader.partial
    for member in reader.members:
        rec: dict[str, Any] = {'path': member.path, 'size': member.size, 'sha256': None, 'kind': None, 'status': 'ok'}
        if member.compressed is not None:
            rec['compressed_size'] = member.compressed
        reason = member.reason
        if member.size > limits.max_item_bytes:
            reason = reason or 'item-exceeds-limit'
        elif budget + member.size > limits.max_total_bytes:
            reason = reason or 'total-byte-budget-exceeded'
        elif member.compressed is not None and member.size > 8192 and member.size / max(1, member.compressed) > 250:
            reason = reason or 'suspicious-compression-ratio'
        if reason:
            rec.update(status='skipped', reason=reason)
            entries.append(rec)
            complete = False
            continue
        try:
            digest = hashlib.sha256()
            head = bytearray()
            consumed = 0
            with reader.open(member) as stream:
                while True:
                    buf = stream.read(CHUNK)
                    if not buf:
                        break
                    consumed += len(buf)
                    if consumed > min(limits.max_item_bytes, member.size + 1, limits.max_total_bytes - budget + 1):
                        raise IntakeError('declared-size-or-budget-exceeded-on-read')
                    if len(head) < 8192:
                        head.extend(buf[:8192 - len(head)])
                    digest.update(buf)
            if consumed != member.size:
                raise IntakeError(f'file size changed or archive header mismatch: declared={member.size}, got={consumed}')
            rec['sha256'] = digest.hexdigest()
            rec['kind'] = detect_format(bytes(head), member.path)
            budget += consumed
        except (OSError, EOFError, RuntimeError, zipfile.BadZipFile, tarfile.TarError, IntakeError) as exc:
            rec.update(status='error', reason=type(exc).__name__ + ': ' + str(exc)[:160])
            complete = False
        entries.append(rec)
    by_kind = dict(sorted(collections.Counter(e['kind'] for e in entries if e['status'] == 'ok').items()))
    by_ext = dict(sorted(collections.Counter(PurePosixPath(e['path']).suffix.lower() or '[none]' for e in entries).items()))
    hash_material = json.dumps([[e['path'], e['sha256'], e['size'], e['status']] for e in entries], ensure_ascii=True, separators=(',', ':')).encode()
    return {
        'schema_version': 1,
        'operation': 'inventory',
        'input': str(reader.target),
        'input_type': reader.mode,
        'package_kind': archive_profile(reader),
        'input_sha256': sha256_path(reader.target, limits.max_total_bytes) if reader.mode != 'directory' else None,
        'inventory_sha256': hashlib.sha256(hash_material).hexdigest(),
        'limits': dataclasses.asdict(limits),
        'complete': complete,
        'file_count': len(entries),
        'readable_count': sum(e['status'] == 'ok' for e in entries),
        'total_verified_bytes': budget,
        'by_kind': by_kind,
        'by_extension': by_ext,
        'notes': notes[:70],
        'notes_omitted': max(0, len(notes) - 70),
        'files': entries,
    }


def decode_bounded(reader: Reader, member: Member, limit: int) -> tuple[str | None, bool]:
    if member.size > reader.limits.max_item_bytes or member.reason:
        return None, True
    with reader.open(member) as fp:
        raw = fp.read(limit + 1)
    truncated = len(raw) > limit or member.size > limit
    raw = raw[:limit]
    if raw.startswith((b'\xff\xfe', b'\xfe\xff')):
        encoding = 'utf-16'
    else:
        if b'\x00' in raw[:4096]:
            return None, truncated
        encoding = 'utf-8-sig'
    return raw.decode(encoding, errors='replace'), truncated


def searchable(record: dict[str, Any]) -> bool:
    if record['status'] != 'ok':
        return False
    return PurePosixPath(record['path']).suffix.lower() in TEXT_EXTENSIONS or record['kind'] in ('text-likely', 'text-by-name')


def redact(line: str, width: int = 320) -> str:
    for regex, replacement in SECRET_PATTERNS:
        line = regex.sub(replacement, line)
    return line[:width] + (' [TRUNCATED]' if len(line) > width else '')


def search(reader: Reader, query: str, limits: Limits, *, case_sensitive: bool) -> dict[str, Any]:
    if not query or len(query) > 512 or '\n' in query:
        raise IntakeError('search expression must be a nonempty single-line literal <=512 chars')
    inv = inventory(reader)
    found: list[dict[str, Any]] = []
    member_by_path = {m.path: m for m in reader.members}
    complete = inv['complete']
    truncated_files = []
    needle = query if case_sensitive else query.casefold()
    for record in inv['files']:
        if not searchable(record):
            continue
        text, truncated = decode_bounded(reader, member_by_path[record['path']], limits.max_text_bytes)
        if text is None:
            complete = False
            continue
        if truncated:
            complete = False
            truncated_files.append(record['path'])
        for line_no, line in enumerate(text.splitlines(), 1):
            line_compare = line if case_sensitive else line.casefold()
            if needle in line_compare:
                if len(found) == limits.max_matches:
                    complete = False
                    break
                found.append({'path': record['path'], 'line': line_no, 'snippet': redact(line.strip()), 'artifact_sha256': record['sha256']})
        if len(found) >= limits.max_matches:
            complete = False
            break
    return {
        'schema_version': 1, 'operation': 'search', 'input': inv['input'],
        'inventory_sha256': inv['inventory_sha256'], 'query': query,
        'case_sensitive': case_sensitive, 'matches': found,
        'complete': complete, 'truncated_text_files': truncated_files[:50],
        'limitations': ([] if complete else ['search coverage is partial; absence is not established']),
    }


def reference_candidates(source: str, target: str, kind: str) -> list[tuple[str, str]]:
    source_dir = posixpath.dirname(source)
    if kind == 'project-reference':
        target = target.replace('\\', '/')
    elif kind == 'python-relative':
        leading = len(target) - len(target.lstrip('.'))
        tail = target[leading:].replace('.', '/')
        prefix = posixpath.normpath(posixpath.join(source_dir, *(['..'] * max(0, leading - 1))))
        base = posixpath.join(prefix, tail) if tail else prefix
        return [(p, 'heuristic') for p in (base + '.py', posixpath.join(base, '__init__.py'))]
    elif not target.startswith(('./', '../')) and kind != 'html-local':
        return []
    if kind == 'html-local':
        if target.startswith(('/', '//', '#')) or '://' in target or target.startswith('data:'):
            return []
        target = target.split('?', 1)[0].split('#', 1)[0]
    base = posixpath.normpath(posixpath.join(source_dir, target))
    if base == '..' or base.startswith('../') or base.startswith('/'):
        return []
    extensions = ('.ts', '.tsx', '.js', '.jsx', '.mts', '.mjs', '.cjs', '.json')
    candidates = [(base, 'exact')]
    if kind == 'javascript-import':
        if base.endswith('.js'):
            candidates.extend((base[:-3] + ext, 'heuristic') for ext in ('.ts', '.tsx', '.jsx'))
        candidates.extend((base + ext, 'heuristic') for ext in extensions)
        candidates.extend((posixpath.join(base, 'index' + ext), 'heuristic') for ext in extensions)
    return candidates


def scan_imports(path: str, text: str) -> Iterator[tuple[int, str, str]]:
    ext = PurePosixPath(path).suffix.lower()
    for line_no, line in enumerate(text.splitlines(), 1):
        if len(line) > MAX_LEXICAL_LINE:
            continue
        if ext in ('.ts', '.tsx', '.js', '.jsx', '.mjs', '.cjs', '.mts', '.cts'):
            for match in JS_IMPORT.finditer(line):
                yield line_no, 'javascript-import', match.group(1)
        elif ext == '.py':
            match = PY_FROM.search(line)
            if match:
                yield line_no, 'python-relative', match.group(1)
        elif ext in ('.csproj', '.props', '.targets'):
            for match in PROJECT_REF.finditer(line):
                yield line_no, 'project-reference', match.group(1)
        elif ext in ('.html', '.htm'):
            for match in HTML_ASSET.finditer(line):
                yield line_no, 'html-local', match.group(1)


def graph(reader: Reader, limits: Limits, focus: str | None = None, depth: int = 2) -> dict[str, Any]:
    inv = inventory(reader)
    known = {r['path']: r for r in inv['files'] if r['status'] == 'ok'}
    members = {m.path: m for m in reader.members}
    edges: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []
    partial = not inv['complete']
    truncated_sources: list[str] = []
    for path, rec in sorted(known.items()):
        if PurePosixPath(path).suffix.lower() not in SOURCE_EXTENSIONS:
            continue
        text, truncated = decode_bounded(reader, members[path], limits.max_text_bytes)
        if text is None:
            partial = True
            continue
        if truncated:
            partial = True
            truncated_sources.append(path)
        if any(len(line) > MAX_LEXICAL_LINE for line in text.splitlines()):
            partial = True
            truncated_sources.append(path)
        for line, relation, raw in scan_imports(path, text):
            if len(edges) + len(unresolved) >= limits.max_edges:
                partial = True
                break
            candidates = reference_candidates(path, raw, relation)
            matches = [(target, quality) for target, quality in candidates if target in known]
            if matches:
                target, quality = matches[0]
                edges.append({'source': path, 'target': target, 'kind': relation,
                              'line': line, 'import': raw, 'resolution': quality,
                              'source_sha256': rec['sha256'], 'target_sha256': known[target]['sha256']})
            else:
                # External specifiers are not claimed to be missing files.
                unresolved.append({'source': path, 'line': line, 'kind': relation,
                                   'specifier': raw, 'reason': 'external-or-unresolved'})
        if len(edges) + len(unresolved) >= limits.max_edges:
            partial = True
            break
    all_nodes = {e['source'] for e in edges} | {e['target'] for e in edges}
    if focus:
        seeds = sorted(k for k in known if focus.casefold() in k.casefold())
        if len(seeds) != 1:
            raise IntakeError(f'focus must resolve uniquely; found {len(seeds)} matches: {seeds[:15]}')
        selected = set(seeds)
        frontier = set(seeds)
        for _ in range(depth):
            frontier = {e['target'] for e in edges if e['source'] in frontier} | {e['source'] for e in edges if e['target'] in frontier}
            frontier -= selected
            selected |= frontier
        edges = [e for e in edges if e['source'] in selected and e['target'] in selected]
        unresolved = [r for r in unresolved if r['source'] in selected]
        all_nodes = selected
    nodes = [{'path': path, 'sha256': known[path]['sha256'], 'kind': known[path]['kind']} for path in sorted(all_nodes)]
    return {
        'schema_version': 1, 'operation': 'graph', 'input': inv['input'],
        'inventory_sha256': inv['inventory_sha256'], 'complete': not partial,
        'focus': focus, 'depth': depth if focus else None,
        'scope': 'static syntactic references only; unresolved != missing and edges != runtime execution',
        'limits': dataclasses.asdict(limits), 'node_count': len(nodes),
        'edge_count': len(edges), 'unresolved_count': len(unresolved),
        'truncated_sources': truncated_sources[:40], 'nodes': nodes, 'edges': edges,
        'unresolved': unresolved[:300], 'unresolved_omitted': max(0, len(unresolved) - 300),
    }


def symbol_candidates(path: str, line: str) -> Iterator[tuple[str, str]]:
    ext = PurePosixPath(path).suffix.lower()
    if ext == '.py':
        m = PY_SYMBOL_DECL.match(line)
        if m:
            yield ('function' if m.group(2) == 'def' else 'type'), m.group(3)
    elif ext in ('.cs', '.java'):
        m = TYPE_DECL.match(line)
        if m:
            yield 'type', m.group(2)
        m = CS_METHOD_DECL.match(line)
        if m:
            yield 'method-candidate', m.group(1)
    elif ext in ('.ts', '.tsx', '.js', '.jsx', '.mjs', '.cjs'):
        m = JS_SYMBOL_DECL.match(line)
        if m:
            yield ('type' if m.group(1) in ('class', 'interface', 'type', 'enum') else 'function'), m.group(2)
        m = JS_EXPORT_BINDING.match(line)
        if m:
            yield 'exported-binding-candidate', m.group(1)
        else:
            m = JS_ARROW_DECL.match(line)
            if m:
                yield 'arrow-function-candidate', m.group(1)
    elif ext == '.go':
        m = GO_FUNC_DECL.match(line)
        if m:
            yield 'function', m.group(1)
    elif ext == '.rs':
        m = RUST_FUNC_DECL.match(line)
        if m:
            yield 'function', m.group(1)


def symbols(reader: Reader, limits: Limits, name: str | None, max_symbols: int) -> dict[str, Any]:
    inv = inventory(reader)
    members = {m.path: m for m in reader.members}
    found = []
    partial = not inv['complete']
    truncated_sources = []
    for rec in inv['files']:
        if rec['status'] != 'ok' or PurePosixPath(rec['path']).suffix.lower() not in SYMBOL_EXTENSIONS:
            continue
        content, truncated = decode_bounded(reader, members[rec['path']], limits.max_text_bytes)
        if content is None:
            partial = True
            continue
        if truncated:
            partial = True
            truncated_sources.append(rec['path'])
        for line_no, line in enumerate(content.splitlines(), 1):
            if len(line) > MAX_LEXICAL_LINE:
                partial = True
                continue
            for kind, symbol_name in symbol_candidates(rec['path'], line):
                if name is not None and name.casefold() not in symbol_name.casefold():
                    continue
                if len(found) >= max_symbols:
                    partial = True
                    break
                found.append({'path': rec['path'], 'line': line_no, 'name': symbol_name,
                              'kind': kind, 'candidate': True,
                              'snippet': redact(line.strip(), 240), 'sha256': rec['sha256']})
            if len(found) >= max_symbols:
                partial = True
                break
        if len(found) >= max_symbols:
            partial = True
            break
    return {'schema_version': 1, 'operation': 'symbols', 'input': inv['input'],
            'inventory_sha256': inv['inventory_sha256'], 'name_filter': name,
            'complete': not partial, 'symbol_count': len(found), 'symbols': found,
            'truncated_sources': truncated_sources[:40],
            'scope': 'regex-based declaration candidates; not an AST, compiler symbol table or call graph'}


def diff_targets(left: Path, right: Path, limits: Limits, strip: int, include_dependencies: bool) -> dict[str, Any]:
    with Reader(left, limits, include_dependencies) as l, Reader(right, limits, include_dependencies) as r:
        a, b = inventory(l), inventory(r)
    def indexed(inv: dict[str, Any]) -> dict[str, Any]:
        out = {}
        for rec in inv['files']:
            components = rec['path'].split('/')
            if len(components) <= strip:
                continue
            path = '/'.join(components[strip:])
            if path in out:
                raise IntakeError(f'colliding normalized path: {path}')
            out[path] = rec
        return out
    x, y = indexed(a), indexed(b)
    added = sorted(set(y) - set(x))
    removed = sorted(set(x) - set(y))
    modified, unchanged, unknown = [], [], []
    for path in sorted(set(x) & set(y)):
        one, two = x[path], y[path]
        if one['sha256'] is None or two['sha256'] is None:
            unknown.append(path)
        elif one['sha256'] == two['sha256']:
            unchanged.append(path)
        else:
            modified.append(path)
    return {
        'schema_version': 1, 'operation': 'diff', 'left': a['input'], 'right': b['input'],
        'left_inventory_sha256': a['inventory_sha256'], 'right_inventory_sha256': b['inventory_sha256'],
        'strip_components': strip, 'complete': a['complete'] and b['complete'] and not unknown,
        'added': added, 'removed': removed, 'modified': modified,
        'unchanged_count': len(unchanged), 'unknown': unknown,
        'limitation': None if a['complete'] and b['complete'] and not unknown else 'partial input coverage; do not infer missing behavior',
    }


def binary_strings(reader: Reader, limits: Limits, min_chars: int, max_strings: int) -> dict[str, Any]:
    if reader.mode != 'file':
        raise IntakeError('strings accepts one regular file; choose an extracted member explicitly')
    member = reader.members[0]
    if member.size > limits.max_item_bytes:
        raise IntakeError('binary exceeds per-item byte limit')
    with reader.open(member) as fp:
        data = fp.read(limits.max_item_bytes + 1)
    if len(data) > limits.max_item_bytes:
        raise IntakeError('binary exceeds per-item byte limit')
    ascii_pattern = re.compile(rb'[\x20-\x7e]{' + str(min_chars).encode() + rb',}')
    utf16_pattern = re.compile(rb'(?:[\x20-\x7e]\x00){' + str(min_chars).encode() + rb',}')
    hits = []
    stopped = False
    for encoding, pattern in [('ascii', ascii_pattern), ('utf-16le', utf16_pattern)]:
        for match in pattern.finditer(data):
            if len(hits) >= max_strings + 1:
                stopped = True
                break
            hits.append({'offset': match.start(), 'encoding': encoding,
                         'value': redact(match.group().decode('latin1') if encoding == 'ascii' else match.group().decode('utf-16le'), 180)})
        if stopped:
            break
    hits.sort(key=lambda x: (x['offset'], x['encoding']))
    return {'schema_version': 1, 'operation': 'strings', 'input': str(reader.target),
            'sha256': hashlib.sha256(data).hexdigest(), 'kind': detect_format(data[:8192], member.path),
            'complete': not stopped and len(hits) <= max_strings, 'string_count_at_least': len(hits),
            'strings': hits[:max_strings], 'limitation': 'printable strings do not establish semantics or executability'}


def emit(result: dict[str, Any], output: str | None, protected_inputs: list[Path]) -> None:
    content = json.dumps(result, indent=2, ensure_ascii=False) + '\n'
    if output:
        target = Path(output).expanduser().resolve()
        if not target.parent.is_dir():
            raise IntakeError('output parent directory does not exist')
        for source in protected_inputs:
            source = source.expanduser().resolve()
            if source.is_dir() and target.is_relative_to(source):
                raise IntakeError('refusing to write output inside analyzed directory')
        # x mode prevents overwrites and accidental replacement of evidence.
        with target.open('x', encoding='utf-8') as fp:
            fp.write(content)
        print(f'written {target} ({len(content.encode("utf-8"))} bytes)')
    else:
        sys.stdout.write(content)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version', action='version', version='reverse-engineering recon 1.0.0')
    sub = parser.add_subparsers(dest='command', required=True)
    def common(p: argparse.ArgumentParser) -> None:
        p.add_argument('--max-files', type=int, default=12000)
        p.add_argument('--max-item-mib', type=int, default=32)
        p.add_argument('--max-total-mib', type=int, default=256)
        p.add_argument('--max-text-kib', type=int, default=512)
        p.add_argument('--include-dependencies', action='store_true')
        p.add_argument('-o', '--output', help='new JSON file (never overwrites)')
    p = sub.add_parser('inventory', help='hash and fingerprint bounded files/archive members')
    p.add_argument('path'); common(p)
    p = sub.add_parser('search', help='line-anchored literal search with basic secret redaction')
    p.add_argument('path'); p.add_argument('literal'); p.add_argument('--case-sensitive', action='store_true')
    p.add_argument('--max-matches', type=int, default=150); common(p)
    p = sub.add_parser('graph', help='bounded static graph for common source import forms')
    p.add_argument('path'); p.add_argument('--focus', help='unique file path substring')
    p.add_argument('--depth', type=int, default=2); p.add_argument('--max-edges', type=int, default=15000); common(p)
    p = sub.add_parser('symbols', help='line-anchored lexical declaration candidates')
    p.add_argument('path'); p.add_argument('--name', help='case-insensitive symbol-name fragment')
    p.add_argument('--max-symbols', type=int, default=3000); common(p)
    p = sub.add_parser('diff', help='content-addressed comparison of two artifacts')
    p.add_argument('left'); p.add_argument('right'); p.add_argument('--strip-components', type=int, default=0); common(p)
    p = sub.add_parser('strings', help='read-only ASCII/UTF-16LE strings with byte offsets')
    p.add_argument('path'); p.add_argument('--min-chars', type=int, default=5)
    p.add_argument('--max-strings', type=int, default=150); common(p)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    a = parser.parse_args(argv)
    integers = [a.max_files, a.max_item_mib, a.max_total_mib, a.max_text_kib]
    if any(not 1 <= n <= 1048576 for n in integers):
        parser.error('all resource limits must be positive integers <=1048576')
    limits = Limits(max_files=a.max_files, max_item_bytes=a.max_item_mib * 1048576,
                    max_total_bytes=a.max_total_mib * 1048576, max_text_bytes=a.max_text_kib * 1024,
                    max_matches=getattr(a, 'max_matches', 150), max_edges=getattr(a, 'max_edges', 15000))
    if limits.max_item_bytes > limits.max_total_bytes:
        parser.error('max-item-mib must be <= max-total-mib')
    if getattr(a, 'depth', 0) < 0 or getattr(a, 'max_edges', 1) <= 0 or getattr(a, 'max_symbols', 1) <= 0 or getattr(a, 'max_matches', 1) <= 0 or getattr(a, 'max_strings', 1) <= 0 or getattr(a, 'min_chars', 4) < 4:
        parser.error('depth must be >=0; matches, edges and strings limits must be >0; min-chars >=4')
    try:
        if a.command == 'diff':
            if a.strip_components < 0:
                raise IntakeError('strip-components must be >=0')
            result = diff_targets(Path(a.left), Path(a.right), limits, a.strip_components, a.include_dependencies)
        else:
            with Reader(Path(a.path), limits, a.include_dependencies) as reader:
                if a.command == 'inventory':
                    result = inventory(reader)
                elif a.command == 'search':
                    result = search(reader, a.literal, limits, case_sensitive=a.case_sensitive)
                elif a.command == 'graph':
                    result = graph(reader, limits, a.focus, a.depth)
                elif a.command == 'symbols':
                    result = symbols(reader, limits, a.name, a.max_symbols)
                else:
                    result = binary_strings(reader, limits, a.min_chars, a.max_strings)
        protected = [Path(a.left), Path(a.right)] if a.command == 'diff' else [Path(a.path)]
        emit(result, a.output, protected)
    except (IntakeError, OSError, tarfile.TarError, zipfile.BadZipFile, ValueError, UnicodeError) as e:
        print(f'ERROR: {e}', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
