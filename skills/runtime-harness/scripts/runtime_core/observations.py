"""Explicit bounded discovery and mechanically verifiable shared observations."""
from __future__ import annotations
import os
from pathlib import Path
import time
from .common import ID_RE, RuntimeFault, confined, file_hash, number, relative_parts
from .environment import DEFAULT_NEGATIVE_TTL, DEFAULT_POSITIVE_TTL, discover_tool, search_fingerprint, tool_record
from .query import reference_list, resource_key, resolve, result_for
from .store import Store


def _tool_name(uri: str) -> str:
    if not uri.startswith("tool://"):
        raise RuntimeFault("INVALID_INPUT", "ensure and observe-tool accept only tool:// IDs.")
    name = uri[len("tool://"):]
    parts = relative_parts(name)
    if len(parts) != 1 or not ID_RE.fullmatch(name):
        raise RuntimeFault("INVALID_INPUT", "Invalid logical tool ID.")
    return name


def ensure(store: Store, refs: list[str], *, negative_ttl: int = DEFAULT_NEGATIVE_TTL, budget: int = 8192) -> dict:
    """Discover only requested tools; missing observations are negative-cached by PATH fingerprint."""
    refs = reference_list(refs)
    number(negative_ttl, 1, 86400)
    names = [_tool_name(uri) for uri in refs]
    _, snapshot = store.current()
    now = time.time()
    fingerprint = search_fingerprint()
    updates = {}
    discovery = False
    for name in names:
        old = snapshot["tools"].get(name)
        live = resolve(snapshot, "tool://" + name) if old is not None else {"status": "missing"}
        if live["status"] == "available":
            continue
        if old is not None and old["status"] == "missing":
            fresh = now - old["observed_at"] <= old["ttl_seconds"]
            if fresh and old.get("search_fingerprint") == fingerprint:
                continue
        updates[name] = discover_tool(name, negative_ttl=negative_ttl)
        discovery = True
    if updates:
        store.publish_observations(tools=updates)
    return result_for(store, refs, budget=budget, discovery_performed=discovery)


def observe_tool(store: Store, uri: str, path: Path, *, ttl: int = DEFAULT_POSITIVE_TTL, budget: int = 8192) -> dict:
    name = _tool_name(uri)
    number(ttl, 1, 86400)
    absolute = Path(os.path.abspath(path))
    if not absolute.is_file():
        raise RuntimeFault("INVALID_INPUT", "Observed tool path must be an existing file.")
    if os.name != "nt" and not os.access(absolute, os.X_OK):
        raise RuntimeFault("INVALID_INPUT", "Observed POSIX tool must be executable.")
    record = tool_record(name, str(absolute), verified=False, source="explicit", ttl_seconds=ttl)
    store.publish_observations(tools={name: record})
    return result_for(store, [uri], budget=budget, discovery_performed=True)


def _resource_descriptor(snapshot: dict, path: Path) -> tuple[str, str | None, str]:
    absolute = Path(os.path.abspath(path))
    if absolute.is_symlink() or not absolute.is_file():
        raise RuntimeFault("INVALID_INPUT", "Shared resources must be existing nonsymlink files.")
    # Prefer a registered skill base when applicable so another workspace can rebind it.
    candidates = []
    for name, skill in snapshot["skills"].items():
        root = Path(skill["root"])
        try:
            rel = absolute.relative_to(root)
        except ValueError:
            continue
        candidates.append((len(root.parts), "skill", name, root, rel))
    workspace = Path(snapshot["workspace"])
    try:
        rel = absolute.relative_to(workspace)
    except ValueError:
        pass
    else:
        candidates.append((len(workspace.parts), "workspace", None, workspace, rel))
    if not candidates:
        raise RuntimeFault("UNSAFE_PATH", "Shared resources must be inside the workspace or a registered skill root.")
    _, base, owner, root, rel = max(candidates, key=lambda item: item[0])
    rel_text = rel.as_posix()
    safe = confined(root, rel_text)
    if safe != absolute:
        raise RuntimeFault("UNSAFE_PATH", "Resource path did not resolve inside its approved root.")
    return base, owner, rel_text


def observe_resource(store: Store, uri: str, path: Path, *, ttl: int = DEFAULT_POSITIVE_TTL, budget: int = 8192) -> dict:
    key = resource_key(uri)
    number(ttl, 1, 86400)
    _, snapshot = store.current()
    base, owner, relative = _resource_descriptor(snapshot, path)
    absolute = Path(os.path.abspath(path))
    record = {"uri": uri, "kind": "resource", "base": base, "relative_path": relative,
              "observed_sha256": file_hash(absolute), "source": "explicit", "observed_at": time.time(),
              "ttl_seconds": ttl}
    if owner is not None:
        record["owner"] = owner
    store.publish_observations(resources={key: record})
    result = result_for(store, [uri], budget=budget, discovery_performed=True)
    if result["records"][0]["status"] == "available":
        result["status"] = "stored"
    # Recompute identity/accounting after the presentation status change.
    from .common import bounded, sha
    result.pop("output_bytes", None)
    result["etag"] = sha({"operation": "observe-resource", "body": {k: v for k, v in result.items() if k != "etag"}})
    return bounded(result, budget)
