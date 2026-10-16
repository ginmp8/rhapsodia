"""Explicit native-host installation: short managed instructions, no hidden hooks."""
from __future__ import annotations
from .common import RuntimeFault, atomic_write, atomic_batch, canonical, confined, read_bytes, sha, strict_json
from .store import Store

START = "<!-- rhapsodia-runtime:start -->"
END = "<!-- rhapsodia-runtime:end -->"
HOST_PATHS = {"generic": "AGENTS.md", "codex": "AGENTS.md", "copilot": ".github/copilot-instructions.md",
              "claude": "CLAUDE.md", "cursor": ".cursor/rules/rhapsodia-runtime.mdc"}
CONTENT = """## Required Rhapsodia session and reusable memory

Use Harness to prevent repeated environment discovery and Graph to retain structural
and operational knowledge across agents and sessions. Initialization is not a ritual:
reuse relevant verified knowledge rather than rebuilding it each task. The repository and live environment remain authoritative; do not skip necessary source reads or verification.
Reduce redundant context/tool work, not quality. Judge useful verified reuse, not graph size or invocation counts.

When acting as any Rhapsodia agent, before repository search, domain work or delegation,
run the host-discovered runtime-harness `scripts/agent_session.py --workspace <ROOT>
--skills-root <APPROVED_SKILLS_ROOT>` with the approved Python 3.10+ and -I -S -B.
The adapter creates/reuses `.rhapsodia/runtime/current.json` and the actual Local Graph
Engine database `.rhapsodia/graph/workspace.sqlite3`; require both ready receipts.
Only an explicit user request permits --no-harness and/or --no-graph with
--opt-out-reason user-request. Missing permission/capability or corrupt state blocks;
Do not install, bypass policy, silently disable, or fabricate a bootstrap result.
Every Rhapsodia role has private-maintenance scope only for approved helper operations;
this does not expand its domain authority or native host permissions.
Use graph-first lookup per question/scope, fresh exact source reads and bounded discovery
on missing/stale/truncated/insufficient results. Reuse a lookup for the same question and unchanged evidence;
refresh after source, question, scope or environment changes, not for every adjacent read.
Pin and learn only relevant reusable nonduplicate findings, rationale and diagnostic outcomes.
Use stable keys, source pins and expected revisions; do not dump files or transcripts.
Reconcile changed/deleted sources before returning. Preserve history and non-reconstructible learned memory.
When nothing qualifies, report no-new-reusable-knowledge with its reason, not a ritual write.
No relevant lookup topic permits a truthful not-needed explanation, not skipping required bootstrap.
Recipes retain sanitized diagnosis, applicability, outcome and verification, never
credentials, environment values or raw logs. Source history and independent proof stay
separate; partial searches/branch changes cannot justify destructive pruning.
Use runtime resolve/context before ensure/observe; respect source pins and negative TTLs.
Return compact session_memory evidence. Runtime/graph receipts never replace domain
handoffs, fresh validation or independent proof. Standalone registry-only consumers
remain graph-independent; this required pair belongs to the Rhapsodia agent profile.
No helper grants permissions, starts a service, runs a recipe, authenticates or installs.
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
        cache_line = b"/.rhapsodia/cache/"
        if cache_line not in new_ignore.splitlines():
            new_ignore += (b"\n" if new_ignore and not new_ignore.endswith(b"\n") else b"") + cache_line + b"\n"
        graph_line = b"/.rhapsodia/graph/"
        if graph_line not in new_ignore.splitlines():
            new_ignore += (b"\n" if new_ignore and not new_ignore.endswith(b"\n") else b"") + graph_line + b"\n"
        targets = [
            (store.workspace, rel, before if path.exists() else None, after),
            (store.workspace, ".gitignore", old_ignore if ignore.exists() else None, new_ignore),
            (store.root, record_path, read_bytes(meta) if meta.exists() else None, canonical({"path": rel, "block_hash": sha(managed)})),
        ]
        atomic_batch(targets)
    return {"status": "configured", "host": host, "path": rel, "changed": after != before, "automatic_hooks": False}
