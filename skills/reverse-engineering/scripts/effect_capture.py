#!/usr/bin/env python3
"""Bounded read-only metadata/hash snapshots for *trusted* process working directories.

This is not isolation, syscall monitoring, or proof that no external effects occurred.
Only regular files below an explicitly selected directory are observed.
"""
from __future__ import annotations
import hashlib
import os
import stat
from pathlib import Path

class CaptureError(ValueError):
    pass


def snapshot(root: Path, *, max_files: int = 500, max_bytes: int = 32 * 1024 * 1024,
             max_file_bytes: int = 8 * 1024 * 1024) -> dict:
    """Read bounded file bytes (no content persisted); fail on incomplete snapshot."""
    if root.is_symlink() or not root.is_dir():
        raise CaptureError('snapshot root must be an existing nonsymlink directory')
    records: dict[str, dict] = {}
    total = 0
    for base, dirs, files in os.walk(root, topdown=True, followlinks=False):
        parent = Path(base)
        clean_dirs = []
        for name in sorted(dirs):
            sub = parent / name
            if sub.is_symlink():
                raise CaptureError('snapshot contains a symlink directory')
            clean_dirs.append(name)
        dirs[:] = clean_dirs
        for name in sorted(files):
            path = parent / name
            relative = path.relative_to(root).as_posix()
            if len(records) >= max_files:
                raise CaptureError('snapshot file budget exceeded')
            info = path.lstat()
            if not stat.S_ISREG(info.st_mode):
                raise CaptureError('snapshot contains a symlink/special file')
            if info.st_size > max_file_bytes or total + info.st_size > max_bytes:
                raise CaptureError('snapshot byte budget exceeded')
            total += info.st_size
            # No-follow where supported; data are hashed in memory, never serialized.
            fd = os.open(path, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0))
            try:
                st = os.fstat(fd)
                if not stat.S_ISREG(st.st_mode) or st.st_size > max_file_bytes:
                    raise CaptureError('snapshot file changed type or size')
                h = hashlib.sha256()
                read_bytes = 0
                with os.fdopen(fd, 'rb', closefd=False) as stream:
                    while chunk := stream.read(128 * 1024):
                        read_bytes += len(chunk)
                        if read_bytes > max_file_bytes:
                            raise CaptureError('snapshot file grew beyond limit')
                        h.update(chunk)
                records[relative] = {'sha256': h.hexdigest(), 'size': read_bytes}
            finally:
                os.close(fd)
    return records


def changes(before: dict, after: dict) -> list[dict]:
    results = []
    for path in sorted(before.keys() | after.keys()):
        a, b = before.get(path), after.get(path)
        if a == b:
            continue
        operation = 'create' if a is None else 'delete' if b is None else 'modify'
        results.append({'kind': 'file', 'operation': operation, 'path': path,
                        'before': a, 'after': b, 'capture': 'working-directory-file-hashes'})
    return results
