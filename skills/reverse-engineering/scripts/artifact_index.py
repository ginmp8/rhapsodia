#!/usr/bin/env python3
"""Bounded read-only virtual files for source trees, ZIP, TAR and Electron ASAR.

Never extracts archive entries, follows links, evaluates manifests or runs payloads.
All caller-supplied names and bytes stay lower-trust evidence.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import stat
import struct
import tarfile
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Iterator

MAX_ITEMS = 12000
MAX_MEMBER = 16 * 1024 * 1024
MAX_TOTAL = 96 * 1024 * 1024
MAX_HEADER = 12 * 1024 * 1024
MAX_ARCHIVE = 384 * 1024 * 1024


class ArtifactError(ValueError):
    """Malformed, out-of-scope, unsafe or unsupported artifact."""


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _identity(name: str) -> str:
    if not name or '\x00' in name or '\\' in name or name.startswith('/'):
        raise ArtifactError('invalid archive name')
    if re.match(r'^[A-Za-z]:', name):
        raise ArtifactError('absolute drive path refused')
    parts = name.split('/')
    if any(p in ('', '.', '..') for p in parts):
        raise ArtifactError('noncanonical archive name')
    if len(parts) > 64 or len(name) > 1200:
        raise ArtifactError('archive name budget exceeded')
    return name


def strict_json(raw: bytes) -> object:
    def pairs(items):
        out = {}
        for k, value in items:
            if k in out:
                raise ArtifactError('duplicate JSON key')
            out[k] = value
        return out
    try:
        parsed=json.loads(raw.decode('utf-8-sig'), object_pairs_hook=pairs,
                          parse_constant=lambda value: (_ for _ in ()).throw(ArtifactError('nonfinite JSON number')))
        stack=[parsed]
        while stack:
            obj=stack.pop()
            if isinstance(obj,str):
                if any(0xd800<=ord(ch)<=0xdfff for ch in obj):
                    raise ArtifactError('unpaired surrogate in JSON')
            elif isinstance(obj,dict):
                stack.extend(obj.keys())
                stack.extend(obj.values())
            elif isinstance(obj,list):
                stack.extend(obj)
        return parsed
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ArtifactError('invalid JSON data') from exc


@dataclass(frozen=True)
class Entry:
    path: str
    size: int
    kind: str
    offset: int | None = None
    expected_sha256: str | None = None


class VirtualArtifact:
    """Read-only file facade over exactly one bounded input artifact."""

    def __init__(self, path: Path, max_items: int = MAX_ITEMS):
        self.path = path.absolute()
        self.max_items = max(1, min(max_items, MAX_ITEMS))
        self.entries: dict[str, Entry] = {}
        self.skips: list[dict] = []
        self.kind = ''
        self._names_casefold: set[str] = set()
        self._asar_data_offset = 0
        self._aggregate = 0
        if path.is_symlink() or not path.exists():
            raise ArtifactError('missing or symlink source')
        if path.is_dir():
            self.kind = 'directory'
            self._directory()
        elif path.is_file() and path.stat().st_size <= MAX_ARCHIVE:
            if zipfile.is_zipfile(path):
                self.kind = 'zip'
                self._zip()
            elif path.name.lower().endswith('.asar'):
                self.kind = 'asar'
                self._asar()
            elif tarfile.is_tarfile(path):
                self.kind = 'tar'
                self._tar()
            else:
                self.kind = 'file'
                self._register(path.name, path.stat().st_size, 'file')
        else:
            raise ArtifactError('input not a supported regular file or input byte budget exceeded')

    def _skip(self, path: str, reason: str) -> None:
        if len(self.skips) < MAX_ITEMS:
            self.skips.append({'path': path[:180], 'reason': reason})

    def _register(self, name: str, size: int, kind: str, offset: int | None = None,
                  expected_sha256: str | None = None) -> None:
        try:
            name = _identity(name)
        except ArtifactError as exc:
            self._skip(name, str(exc))
            return
        fold = name.casefold()
        if name in self.entries or fold in self._names_casefold:
            self._skip(name, 'duplicate or case-colliding path')
            return
        if len(self.entries) >= self.max_items:
            self._skip(name, 'member count bound')
            return
        if size < 0 or size > MAX_MEMBER:
            self._skip(name, 'member size bound')
            return
        if self._aggregate + size > MAX_TOTAL:
            self._skip(name, 'total readable byte bound')
            return
        self.entries[name] = Entry(name, size, kind, offset, expected_sha256)
        self._names_casefold.add(fold)
        self._aggregate += size

    def _directory(self) -> None:
        root = self.path
        files_seen = 0
        for folder, dirs, files in os.walk(root, followlinks=False):
            permitted=[]
            for directory in sorted(dirs):
                if directory=='.git' or (Path(folder)/directory).is_symlink():
                    self._skip(str((Path(folder)/directory).relative_to(root)), 'excluded metadata or symlink directory')
                else:
                    permitted.append(directory)
            dirs[:]=permitted
            for name in sorted(files):
                files_seen += 1
                if files_seen > self.max_items:
                    self._skip('<directory>', 'directory visit count bound')
                    return
                p = Path(folder) / name
                try:
                    if p.is_symlink() or not p.is_file():
                        self._skip(str(p.relative_to(root)), 'non-regular file or symlink')
                    else:
                        self._register(p.relative_to(root).as_posix(), p.stat().st_size, 'file')
                except OSError as exc:
                    self._skip(name, f'filesystem error: {type(exc).__name__}')

    def _zip(self) -> None:
        with zipfile.ZipFile(self.path) as archive:
            for info in archive.infolist()[:self.max_items + 1]:
                if info.is_dir():
                    continue
                mode = info.external_attr >> 16
                if stat.S_ISLNK(mode) or (mode and stat.S_IFMT(mode) not in (0, stat.S_IFREG)):
                    self._skip(info.filename, 'non-regular ZIP member')
                    continue
                if info.flag_bits & 1:
                    self._skip(info.filename, 'encrypted member')
                    continue
                if info.file_size > 0 and info.file_size > max(info.compress_size, 1) * 250:
                    self._skip(info.filename, 'decompression ratio bound')
                    continue
                self._register(info.filename, info.file_size, 'zip')
            if len(archive.infolist()) > self.max_items:
                self._skip('<zip>', 'entry count bound')

    def _tar(self) -> None:
        with tarfile.open(self.path, 'r:*') as archive:
            for i, info in enumerate(archive):
                if i >= self.max_items:
                    self._skip('<tar>', 'entry count bound')
                    return
                if info.isfile():
                    self._register(info.name, info.size, 'tar')
                elif not info.isdir():
                    self._skip(info.name, 'link/special TAR member')

    def _asar(self) -> None:
        length = self.path.stat().st_size
        with self.path.open('rb') as stream:
            prefix = stream.read(16)
            if len(prefix) != 16:
                raise ArtifactError('truncated ASAR header')
            pickle_a, body_a, pickle_b, str_len = struct.unpack('<IIII', prefix)
            if (pickle_a != 4 or body_a < 8 or body_a != pickle_b + 4 or
                    pickle_b > MAX_HEADER or str_len > pickle_b - 4 or 16 + str_len > length):
                # Pickle layout is two objects: [payload=4,headerSize] then [payload,jsonSize,json].
                # The second object starts at byte 8; header-size is its total serialized size.
                raise ArtifactError('unsupported ASAR Pickle header')
            raw = stream.read(str_len)
            if len(raw) != str_len:
                raise ArtifactError('truncated ASAR JSON header')
        tree = strict_json(raw)
        if not isinstance(tree, dict) or not isinstance(tree.get('files'), dict):
            raise ArtifactError('invalid ASAR tree')
        self._asar_data_offset = 8 + body_a
        self._asar_walk(tree['files'], '', length, 0)

    def _asar_walk(self, tree: dict, prefix: str, length: int, depth: int) -> None:
        if depth > 48:
            self._skip(prefix, 'ASAR directory depth exceeded')
            return
        for name, node in sorted(tree.items()):
            if not isinstance(name, str) or not isinstance(node, dict):
                self._skip(prefix, 'invalid ASAR node')
                continue
            route = (prefix + '/' if prefix else '') + name
            if 'files' in node and isinstance(node['files'], dict):
                self._asar_walk(node['files'], route, length, depth + 1)
                continue
            if node.get('unpacked') or 'link' in node:
                self._skip(route, 'external/unpacked or linked ASAR entry')
                continue
            try:
                size = node['size']
                if type(size) is not int or type(node['offset']) is not str or not node['offset'].isdecimal():
                    raise ValueError('malformed offset/size')
                off = int(node['offset']) + self._asar_data_offset
                if off < self._asar_data_offset or off + size > length:
                    raise ValueError('out-of-range content offset')
                integrity = node.get('integrity')
                expected = None
                if isinstance(integrity, dict) and integrity.get('algorithm') == 'SHA256':
                    expected = integrity.get('hash')
                    if not isinstance(expected, str) or not re.fullmatch('[a-fA-F0-9]{64}', expected):
                        expected = None
                self._register(route, size, 'asar', off, expected)
            except (KeyError, ValueError) as exc:
                self._skip(route, 'invalid ASAR content coordinates')

    def read(self, name: str, limit: int = MAX_MEMBER) -> bytes:
        entry = self.entries.get(name)
        if entry is None:
            raise ArtifactError('unavailable or refused entry')
        if entry.size > min(MAX_MEMBER, limit):
            raise ArtifactError('requested member exceeds read limit')
        if self.kind == 'directory':
            candidate = self.path
            for part in name.split('/'):
                candidate = candidate / part
                if candidate.is_symlink():
                    raise ArtifactError('symlink introduced after inventory')
            if not candidate.is_file():
                raise ArtifactError('file changed after inventory')
            if os.open in os.supports_dir_fd and hasattr(os, 'O_NOFOLLOW'):
                # POSIX openat walk keeps every directory component pinned by fd.
                flags=os.O_RDONLY | os.O_NOFOLLOW
                current=os.open(self.path, flags | os.O_DIRECTORY)
                try:
                    for part in name.split('/')[:-1]:
                        nextfd=os.open(part, flags | os.O_DIRECTORY, dir_fd=current)
                        os.close(current)
                        current=nextfd
                    filefd=os.open(name.split('/')[-1], flags, dir_fd=current)
                    try:
                        if not stat.S_ISREG(os.fstat(filefd).st_mode):
                            raise ArtifactError('refused non-regular directory entry')
                        with os.fdopen(filefd,'rb') as handle:
                            filefd=-1
                            blob=handle.read(entry.size+1)
                    finally:
                        if filefd!=-1:os.close(filefd)
                finally:
                    os.close(current)
            else:
                # Fallback: best-effort check; OS lacks POSIX fd-relative nofollow.
                with candidate.open('rb') as handle:
                    blob = handle.read(entry.size + 1)
        elif self.kind == 'file':
            if self.path.is_symlink():
                raise ArtifactError('source became symlink')
            open_flags=os.O_RDONLY | getattr(os,'O_NOFOLLOW',0)
            descriptor=os.open(self.path,open_flags)
            with os.fdopen(descriptor,'rb') as handle:
                if not stat.S_ISREG(os.fstat(handle.fileno()).st_mode):
                    raise ArtifactError('refused non-regular file')
                blob = handle.read(entry.size + 1)
        elif self.kind == 'zip':
            with zipfile.ZipFile(self.path) as archive, archive.open(name) as handle:
                blob = handle.read(entry.size + 1)
        elif self.kind == 'tar':
            with tarfile.open(self.path, 'r:*') as archive:
                info = archive.getmember(name)
                handle = archive.extractfile(info)
                if handle is None:
                    raise ArtifactError('TAR member unavailable')
                with handle:
                    blob = handle.read(entry.size + 1)
        elif self.kind == 'asar':
            with self.path.open('rb') as handle:
                handle.seek(entry.offset)
                blob = handle.read(entry.size)
        else:
            raise ArtifactError('unhandled input kind')
        if len(blob) != entry.size:
            raise ArtifactError('member changed or truncated')
        if entry.expected_sha256 and digest(blob).lower() != entry.expected_sha256.lower():
            raise ArtifactError('ASAR integrity digest mismatch')
        return blob

    def inventory(self, offset: int = 0, limit: int = 100) -> dict:
        limit = max(1, min(limit, 250))
        offset = max(0, offset)
        entries = sorted(self.entries.values(), key=lambda x: x.path)
        return {'source_kind': self.kind, 'source_sha256': self.source_sha(),
                'count': len(entries), 'total_readable_bytes': self._aggregate,
                'items': [{'path': e.path, 'size': e.size, 'kind': e.kind} for e in entries[offset:offset+limit]],
                'next_offset': offset + limit if offset + limit < len(entries) else None,
                'skipped_count': len(self.skips), 'skips': self.skips[:80],
                'complete': not self.skips}

    def source_sha(self) -> str:
        if self.kind != 'directory':
            stream = hashlib.sha256()
            with self.path.open('rb') as file:
                for chunk in iter(lambda: file.read(1024 * 1024), b''):
                    stream.update(chunk)
            return stream.hexdigest()
        records = []
        for name in sorted(self.entries):
            try:
                data = self.read(name)
                records.append([name, digest(data)])
            except ArtifactError:
                records.append([name, 'inaccessible'])
        return digest(json.dumps(records,separators=(',',':')).encode('utf-8'))


def resolve_scoped(root: Path, supplied: str, allow_directory: bool = True) -> Path:
    """Reject path escape/symlinks, including a symlink in any existing component."""
    if not isinstance(supplied, str) or not supplied or '\x00' in supplied:
        raise ArtifactError('path is required')
    root = root.resolve(strict=True)
    p = Path(supplied)
    if not p.is_absolute():
        p = root / p
    absolute = p.absolute()
    if not absolute.is_relative_to(root):
        raise ArtifactError('path outside configured read root')
    for ancestor in (absolute, *absolute.parents):
        if ancestor == root:
            break
        if ancestor.is_symlink():
            raise ArtifactError('symlink component refused')
    if not absolute.exists() or (not allow_directory and not absolute.is_file()):
        raise ArtifactError('input does not exist or is not a regular file')
    return absolute
