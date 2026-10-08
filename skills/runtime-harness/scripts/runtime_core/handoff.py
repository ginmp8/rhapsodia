"""Content-bound transport hints; not ownership, authorization, or test verdicts."""
from __future__ import annotations
from pathlib import Path
from .common import HASH_RE, RuntimeFault, atomic_write, canonical, confined, fields, read_bytes, safe_text, sha, strict_json
from .query import reference_list, resolve
from .store import Store


def create(store: Store, request: dict) -> dict:
    fields(request, {"task_id", "next_action", "refs"}, {"summary"})
    task = safe_text(request["task_id"], 128)
    action = safe_text(request["next_action"], 256)
    summary = safe_text(request["summary"], 1024) if "summary" in request else None
    refs = reference_list(request["refs"])
    snapshot_id, snapshot = store.current()
    records = [resolve(snapshot, uri) for uri in refs]
    if any(record["status"] != "available" for record in records):
        raise RuntimeFault("UNAVAILABLE_RESOURCE", "A required resource is missing or stale; no handoff was published.", 3)
    pins = []
    for record in records:
        pin = {"uri": record["uri"], "kind": record["kind"]}
        if "sha256" in record:
            pin["sha256"] = record["sha256"]
        else:
            pin["identity"] = record["identity"]
        pins.append(pin)
    body = {"schema": "runtime-handoff-v1", "task_id": task, "next_action": action,
            "scope": snapshot["scope"], "snapshot_id": snapshot_id, "pins": pins}
    if summary is not None:
        body["summary"] = summary
    key = sha(body)
    envelope = {**body, "handoff_id": key}
    with store.writer():
        atomic_write(store.root, "handoffs/" + key + ".json", canonical(envelope), immutable=True)
    return {"status": "stored", "handoff_id": key, "relative_path": "handoffs/" + key + ".json"}


def validate_receipt(value: object) -> dict:
    fields(value, {"schema", "task_id", "next_action", "scope", "snapshot_id", "pins", "handoff_id"}, {"summary"})
    body = {k: v for k, v in value.items() if k != "handoff_id"}
    if value["schema"] != "runtime-handoff-v1" or sha(body) != value["handoff_id"]:
        raise RuntimeFault("INVALID_RECEIPT", "Receipt schema or content identity does not match.", 3)
    for field in ("scope", "snapshot_id", "handoff_id"):
        if not isinstance(value[field], str) or not HASH_RE.fullmatch(value[field]):
            raise RuntimeFault("INVALID_RECEIPT", "Invalid receipt identity.", 3)
    safe_text(value["task_id"], 128)
    safe_text(value["next_action"], 256)
    if "summary" in value:
        safe_text(value["summary"], 1024)
    if not isinstance(value["pins"], list):
        raise RuntimeFault("INVALID_RECEIPT", "Receipt pins must be a bounded array.", 3)
    for pin in value["pins"]:
        fields(pin, {"uri", "kind"}, {"sha256", "identity"})
        key = "sha256" if "sha256" in pin else "identity"
        if ("sha256" in pin) == ("identity" in pin) or not isinstance(pin.get(key), str) or not HASH_RE.fullmatch(pin[key]):
            raise RuntimeFault("INVALID_RECEIPT", "Each pin must bind exactly one content or tool identity.", 3)
    reference_list([p["uri"] for p in value["pins"]])
    return value


def resume(store: Store, *, key: str | None = None, external: Path | None = None, rebind: bool = False) -> dict:
    if (key is None) == (external is None):
        raise RuntimeFault("INVALID_INPUT", "Provide exactly one handoff ID or explicit input file.")
    if key is not None:
        if not HASH_RE.fullmatch(key):
            raise RuntimeFault("INVALID_INPUT", "Invalid handoff ID.")
        path = confined(store.root, "handoffs/" + key + ".json")
    else:
        path = external
        if path.is_symlink():
            raise RuntimeFault("UNSAFE_PATH", "Receipt input may not be a symbolic link.")
    receipt = validate_receipt(strict_json(read_bytes(path, 65536)))
    if key is not None and receipt["handoff_id"] != key:
        raise RuntimeFault("INVALID_RECEIPT", "Requested ID and stored receipt differ.", 3)
    snapshot_id, snapshot = store.current()
    foreign = receipt["scope"] != snapshot["scope"]
    if foreign and not rebind:
        raise RuntimeFault("REBIND_REQUIRED", "This receipt belongs to another environment. Explicit rebind resolves local tools and verifies portable content.", 3)
    records = []
    for pin in receipt["pins"]:
        record = resolve(snapshot, pin["uri"])
        if record["status"] != "available" or record["kind"] != pin["kind"]:
            raise RuntimeFault("STALE_HANDOFF", "A pinned resource is unavailable or changed kind.", 3)
        if "sha256" in pin and record.get("sha256") != pin["sha256"]:
            raise RuntimeFault("STALE_HANDOFF", "Pinned file content changed; prior evidence cannot be reused.", 3)
        if "identity" in pin and not foreign and record.get("identity") != pin["identity"]:
            raise RuntimeFault("STALE_HANDOFF", "A pinned local capability changed.", 3)
        records.append(record)
    return {"schema": "runtime-resume-v1", "status": "ready", "handoff_id": receipt["handoff_id"],
            "snapshot_id": snapshot_id, "rebound": foreign, "task_id": receipt["task_id"],
            "next_action": receipt["next_action"], "records": records,
            "notice": "Resource identity verified only. Domain authority, minimum tool versions and validation gates remain unchanged."}
