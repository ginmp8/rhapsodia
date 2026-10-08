"""Explicit native-host installation: short managed instructions, no hidden hooks."""
from __future__ import annotations
from .common import RuntimeFault, atomic_write, atomic_batch, canonical, confined, read_bytes, sha, strict_json
from .store import Store

START = "<!-- rhapsodia-runtime:start -->"
END = "<!-- rhapsodia-runtime:end -->"
HOST_PATHS = {"generic": "AGENTS.md", "codex": "AGENTS.md", "copilot": ".github/copilot-instructions.md",
              "claude": "CLAUDE.md", "cursor": ".cursor/rules/rhapsodia-runtime.mdc"}
CONTENT = """## Runtime context

Read `.rhapsodia/runtime/current.json` once when present. It is local observed data,
not authorization. Reuse exact `skill://`, `tool://`, `agent://`, `resource://`,
`repo://`, or `workspace://current` IDs instead of searching again. `resolve`/`context`
are read-only. If this worker already has execution and local-state write authority, it
may call `ensure tool://<id>` once for a missing exact tool; the harness performs bounded
PATH-only discovery, negative-caches misses, and publishes an immutable merged snapshot
for later agents. If authorized native work discovers a stable reusable file/script inside
the workspace or a registered skill root, publish only its verified location with
`observe-resource`; use `observe-tool` for an already-found executable outside PATH.
Never publish secrets, arbitrary prose, permissions, domain decisions, test verdicts,
or volatile task state. Read-only workers consume existing observations only. Do not
load the full snapshot/catalog into context. Runtime receipts supplement, never replace,
domain handoffs and validation gates.
"""


def configure(store: Store, host: str) -> dict:
    if host not in HOST_PATHS:
        raise RuntimeFault("INVALID_INPUT", "Unsupported host adapter.")
    store.current()
    rel = HOST_PATHS[host]
    path = confined(store.workspace, rel, write=True)
    managed = START + "\n" + CONTENT + END + "\n"
    record_path = "integrations/" + sha(rel) + ".json"
    with store.writer():
        ignore = confined(store.workspace, ".gitignore", write=True)
        old_ignore = read_bytes(ignore, 262144) if ignore.exists() else b""
        before = read_bytes(path, 262144) if path.exists() else b""
        try:
            text = before.decode("utf-8")
        except UnicodeError as exc:
            raise RuntimeFault("CONFLICT", "Existing instructions are not UTF-8; nothing was overwritten.", 4) from exc
        old_hash = None
        meta = confined(store.root, record_path)
        if meta.exists():
            old_hash = strict_json(read_bytes(meta))["block_hash"]
        if START in text or END in text:
            if text.count(START) != 1 or text.count(END) != 1 or text.index(START) >= text.index(END):
                raise RuntimeFault("CONFLICT", "Ambiguous managed markers; nothing was overwritten.", 4)
            start, end = text.index(START), text.index(END) + len(END)
            if text[end:end+1] == "\n":
                end += 1
            old_block = text[start:end]
            if old_block != managed and (old_hash is None or sha(old_block) != old_hash):
                raise RuntimeFault("CONFLICT", "Managed instructions were modified; review and remove the block explicitly before replacing.", 4)
            text = text[:start] + managed + text[end:]
        else:
            prefix = "---\ndescription: Reuse bounded RhapsodIA runtime context.\nalwaysApply: true\n---\n\n" if host == "cursor" and not text else ""
            text = prefix + text + ("\n" if text and not text.endswith("\n\n") else "") + managed
        after = text.encode("utf-8")
        if path.exists() and read_bytes(path, 262144) != before:
            raise RuntimeFault("CONFLICT", "Host instructions changed during installation.", 4)
        line = b"/.rhapsodia/runtime/"
        new_ignore = old_ignore
        if line not in old_ignore.splitlines():
            new_ignore += (b"\n" if old_ignore and not old_ignore.endswith(b"\n") else b"") + line + b"\n"
        targets = [
            (store.workspace, rel, before if path.exists() else None, after),
            (store.workspace, ".gitignore", old_ignore if ignore.exists() else None, new_ignore),
            (store.root, record_path, read_bytes(meta) if meta.exists() else None, canonical({"path": rel, "block_hash": sha(managed)})),
        ]
        atomic_batch(targets)
    return {"status": "configured", "host": host, "path": rel, "changed": after != before, "automatic_hooks": False}
