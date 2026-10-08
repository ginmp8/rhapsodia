"""Exact read-only lookups and byte-bounded context; no implicit discovery or writes."""
from __future__ import annotations
from pathlib import Path
from .common import HASH_RE, ID_RE, RuntimeFault, bounded, confined, fields, file_hash, number, relative_parts, sha
from .environment import tool_record
from .store import Store


def reference_list(value) -> list[str]:
    if not isinstance(value, list) or not 1 <= len(value) <= 32 or any(not isinstance(v, str) or len(v) > 1024 for v in value):
        raise RuntimeFault("INVALID_INPUT", "refs must contain 1..32 bounded logical URI strings.")
    if len(set(value)) != len(value):
        raise RuntimeFault("INVALID_INPUT", "Duplicate refs are not allowed.")
    return value


def resource_key(uri: str) -> str:
    if not uri.startswith("resource://"):
        raise RuntimeFault("UNSAFE_PATH", "Expected resource:// logical URI.")
    tail = uri[len("resource://"):]
    parts = relative_parts(tail)
    if any(not ID_RE.fullmatch(part) for part in parts):
        raise RuntimeFault("UNSAFE_PATH", "Resource IDs use slash-separated lowercase letters, digits and hyphens.")
    return "/".join(parts)


def _resolve_resource(snapshot: dict, uri: str) -> dict:
    key = resource_key(uri)
    record = snapshot["resources"].get(key)
    missing = {"uri": uri, "kind": "resource", "status": "missing"}
    if record is None:
        return missing
    if record["base"] == "workspace":
        root = Path(snapshot["workspace"])
    else:
        owner = snapshot["skills"].get(record["owner"])
        if owner is None:
            return missing
        root = Path(owner["root"])
    try:
        path = confined(root, record["relative_path"])
    except RuntimeFault:
        return {**missing, "status": "stale"}
    if not path.is_file():
        return missing
    digest = file_hash(path)
    return {"uri": uri, "kind": "resource", "status": "available", "path": str(path),
            "sha256": digest, "bytes": path.stat().st_size,
            "observed_sha256": record["observed_sha256"],
            "changed_since_observed": digest != record["observed_sha256"]}


def resolve(snapshot: dict, uri: str) -> dict:
    if "://" not in uri:
        raise RuntimeFault("UNSAFE_PATH", "Expected a local logical URI.")
    scheme, tail = uri.split("://", 1)
    if scheme not in {"tool", "skill", "repo", "agent", "workspace", "resource"}:
        raise RuntimeFault("UNSAFE_PATH", "Remote and unsupported URI schemes are not allowed.")
    if scheme == "resource":
        return _resolve_resource(snapshot, uri)
    parts = relative_parts(tail)
    missing = {"uri": uri, "kind": scheme, "status": "missing"}
    if scheme == "tool":
        if len(parts) != 1 or not ID_RE.fullmatch(tail):
            raise RuntimeFault("UNSAFE_PATH", "Invalid logical tool ID.")
        old = snapshot["tools"].get(tail)
        if old is None:
            return missing
        if old["status"] == "missing":
            return {**missing, "source": old["source"], "observed_at": old["observed_at"], "ttl_seconds": old["ttl_seconds"]}
        try:
            current = tool_record(tail, old["argv"][0], version=old.get("version"), verified=old["verified"],
                                  source=old["source"], observed_at=old["observed_at"], ttl_seconds=old["ttl_seconds"],
                                  search_space=old.get("search_fingerprint"))
        except (OSError, RuntimeFault):
            return {**missing, "status": "stale"}
        if current["identity"] != old["identity"]:
            current["status"] = "stale"
        return current
    if scheme == "workspace":
        if tail != "current":
            raise RuntimeFault("UNSAFE_PATH", "Only workspace://current is supported.")
        return {"uri": uri, "kind": "workspace", "status": "available", "path": snapshot["workspace"], "identity": snapshot["scope"]}
    root = Path(snapshot["workspace"])
    if scheme == "skill":
        name = parts[0]
        if not ID_RE.fullmatch(name):
            raise RuntimeFault("UNSAFE_PATH", "Invalid skill ID.")
        record = snapshot["skills"].get(name)
        if record is None:
            return missing
        root = Path(record["root"])
        if root.is_symlink():
            raise RuntimeFault("UNSAFE_PATH", "The registered skill root was replaced by a symbolic link.")
        tail = "/".join(parts[1:]) if len(parts) > 1 else "SKILL.md"
    elif scheme == "agent":
        if len(parts) != 1 or not ID_RE.fullmatch(tail):
            raise RuntimeFault("UNSAFE_PATH", "Invalid agent ID.")
        record = snapshot["agents"].get(tail)
        if record is None:
            return missing
        tail = record["relative_path"]
    path = confined(root, tail)
    if not path.is_file():
        return missing
    return {"uri": uri, "kind": scheme, "status": "available", "path": str(path), "sha256": file_hash(path), "bytes": path.stat().st_size}


def result_for(store: Store, refs: list[str], *, budget: int = 8192, discovery_performed: bool | None = None) -> dict:
    key, snapshot = store.current()
    records = [resolve(snapshot, uri) for uri in refs]
    body = {"schema": "runtime-result-v1", "snapshot_id": key,
            "status": "ok" if all(r["status"] == "available" for r in records) else "partial", "records": records}
    if discovery_performed is not None:
        body["discovery_performed"] = discovery_performed
    body["etag"] = sha({"operation": "resolve", "body": body})
    return bounded(body, budget)


def execute_query(store: Store, request: dict) -> dict:
    fields(request, {"operation"}, {"refs", "budget_bytes", "if_none_match"})
    op = request["operation"]
    if not isinstance(op, str) or op not in {"status", "resolve", "context"}:
        raise RuntimeFault("INVALID_INPUT", "Supported operations: status, resolve, context.")
    budget = number(request.get("budget_bytes", 8192), 128, 65536)
    match = request.get("if_none_match")
    if match is not None and (not isinstance(match, str) or not HASH_RE.fullmatch(match)):
        raise RuntimeFault("INVALID_INPUT", "if_none_match must be a retained response etag.")
    key, snapshot = store.current()
    if op == "status":
        if "refs" in request:
            raise RuntimeFault("INVALID_INPUT", "status does not accept refs.")
        body = {"schema": "runtime-result-v1", "status": "ok", "snapshot_id": key,
                "skill_count": len(snapshot["skills"]), "agent_count": len(snapshot["agents"]),
                "tool_count": len(snapshot["tools"]), "resource_count": len(snapshot["resources"]),
                "max_age_seconds": snapshot["max_age_seconds"]}
    else:
        refs = reference_list(request.get("refs"))
        records = [resolve(snapshot, uri) for uri in refs]
        body = {"schema": "runtime-result-v1", "snapshot_id": key,
                "status": "ok" if all(r["status"] == "available" for r in records) else "partial", "records": records}
    etag = sha({"operation": op, "body": body})
    if match == etag:
        return bounded({"schema": "runtime-result-v1", "status": "not_modified", "snapshot_id": key, "etag": etag}, budget)
    body["etag"] = etag
    return bounded(body, budget)
