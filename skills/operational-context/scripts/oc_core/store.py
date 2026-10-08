"""Workspace-confined immutable objects and short cooperative publication locks."""
from __future__ import annotations
from contextlib import contextmanager
from pathlib import Path
import os
import time
import uuid
from .common import HASH_RE, RuntimeFault, atomic_write, canonical, confined, fields, read_bytes, sha, strict_json

KINDS = {"artifact", "evidence", "action", "metric", "pack", "foreign", "lease"}

class Cache:
    def __init__(self, workspace: Path):
        if not workspace.is_dir() or workspace.is_symlink():
            raise RuntimeFault("INVALID_ROOT", "Select one existing canonical workspace directory.")
        self.workspace = workspace.resolve()
        self.root = confined(self.workspace, ".rhapsodia/cache/operational-context", write=True)
        self.scope = sha({"workspace": os.path.normcase(str(self.workspace))})

    @contextmanager
    def writer(self):
        confined(self.workspace, ".rhapsodia/cache/operational-context", write=True)
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        lock = confined(self.root, ".writer.lock", write=True)
        token = canonical({"pid": os.getpid(), "nonce": uuid.uuid4().hex})
        deadline = time.monotonic() + 1.0
        while True:
            try:
                fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
                break
            except FileExistsError as exc:
                if time.monotonic() >= deadline:
                    raise RuntimeFault("BUSY", "Publication lock is busy; no lock takeover was attempted.", 5) from exc
                time.sleep(0.01)
        with os.fdopen(fd, "wb") as stream:
            stream.write(token)
        try:
            yield
        finally:
            if lock.is_file() and not lock.is_symlink() and read_bytes(lock) == token:
                lock.unlink()

    def put(self, kind: str, value: dict) -> str:
        if not isinstance(kind,str) or kind not in KINDS:
            raise RuntimeFault("INVALID_INPUT", "Unsupported cache object kind.")
        body = {"schema": "operational-object/v1", "scope": self.scope, "kind": kind, "value": value}
        key = sha(body)
        if len(canonical(body)) > 4 * 1024 * 1024:
            raise RuntimeFault("INPUT_TOO_LARGE", "Cache object exceeds 4 MiB.")
        with self.writer():
            destination = confined(self.root, kind + '/' + key + '.json')
            if not destination.exists() and len(self.keys(kind)) >= 4096:
                raise RuntimeFault('INDEX_LIMIT','Cache kind is full; prune disposable data offline before publishing.')
            atomic_write(self.root, kind + "/" + key + ".json", canonical(body), immutable=True)
        return key

    def get(self, kind: str, key: str) -> dict:
        if not isinstance(kind,str) or kind not in KINDS or not isinstance(key, str) or not HASH_RE.fullmatch(key):
            raise RuntimeFault("INVALID_INPUT", "Invalid cache object identity.")
        body = strict_json(read_bytes(confined(self.root, kind + "/" + key + ".json")), 4 * 1024 * 1024)
        fields(body, {"schema", "scope", "kind", "value"})
        if sha(body) != key or body["schema"] != "operational-object/v1" or body["scope"] != self.scope or body["kind"] != kind or not isinstance(body["value"], dict):
            raise RuntimeFault("CORRUPT_CACHE", "Cache identity, shape or workspace scope changed.")
        return body["value"]

    def keys(self, kind: str) -> list[str]:
        if not isinstance(kind,str) or kind not in KINDS:
            raise RuntimeFault("INVALID_INPUT", "Unsupported cache object kind.")
        directory = confined(self.root, kind)
        if not directory.exists():
            return []
        result = []
        for path in directory.iterdir():
            if len(result) >= 4096:
                raise RuntimeFault("INDEX_LIMIT", "Bounded index limit reached; request explicit IDs or prune offline.")
            if path.suffix != ".json" or not HASH_RE.fullmatch(path.stem) or path.is_symlink():
                raise RuntimeFault("CORRUPT_CACHE", "Unexpected entry in immutable index.")
            result.append(path.stem)
        return sorted(result)
