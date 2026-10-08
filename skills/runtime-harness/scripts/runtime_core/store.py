"""Immutable environment snapshots with atomic current-pointer publication."""
from __future__ import annotations
from contextlib import contextmanager
import os
from pathlib import Path
import time
import uuid
from . import VERSION
from .common import HASH_RE, ID_RE, MAX_STATE, RuntimeFault, atomic_write, canonical, confined, number, read_bytes, relative_parts, sha, strict_json
from .environment import agent_stamps, discover, interpreter, root_stamps, scope_id, selected_roots


def _validate_observation_fields(record: dict) -> None:
    if not isinstance(record.get("source"), str) or not record["source"]:
        raise ValueError("invalid source")
    if not isinstance(record.get("observed_at"), (int, float)) or isinstance(record.get("observed_at"), bool):
        raise ValueError("invalid observation time")
    number(record.get("ttl_seconds"), 1, 86400)
    fingerprint = record.get("search_fingerprint")
    if fingerprint is not None and (not isinstance(fingerprint, str) or not HASH_RE.fullmatch(fingerprint)):
        raise ValueError("invalid search fingerprint")


def validate_snapshot(data: dict) -> None:
    """Reject malformed local state before any lookup, even with a matching hash."""
    if not isinstance(data, dict) or not isinstance(data.get("workspace"), str):
        raise ValueError("invalid state")
    if not isinstance(data.get("scope"), str) or not HASH_RE.fullmatch(data["scope"]):
        raise ValueError("invalid scope")
    for key in ("created_at", "updated_at"):
        if not isinstance(data.get(key), (int, float)) or isinstance(data.get(key), bool):
            raise ValueError("invalid timestamp")
    roots = data.get("skill_roots")
    if not isinstance(roots, list) or len(roots) > 16 or any(not isinstance(p, str) or not Path(p).is_absolute() for p in roots):
        raise ValueError("invalid roots")
    for key in ("root_stamps", "agent_stamps"):
        if not isinstance(data.get(key), list) or any(not isinstance(v, dict) for v in data[key]):
            raise ValueError("invalid stamps")
    for key in ("skills", "agents", "tools", "resources"):
        if not isinstance(data.get(key), dict) or len(data[key]) > 4096:
            raise ValueError("invalid index")
        for name, record in data[key].items():
            if not isinstance(name, str) or not isinstance(record, dict):
                raise ValueError("invalid record")
            if key == "skills":
                root = record.get("root")
                if not isinstance(root, str) or str(Path(root).parent) not in roots or Path(root).name != name:
                    raise ValueError("invalid skill root")
                digest = record.get("entrypoint_sha256")
                if not isinstance(digest, str) or not HASH_RE.fullmatch(digest):
                    raise ValueError("invalid skill identity")
            elif key == "agents":
                if record.get("relative_path") not in {"agents/" + name + ".agent.md", ".github/agents/" + name + ".agent.md"}:
                    raise ValueError("invalid agent path")
                digest = record.get("sha256")
                if not isinstance(digest, str) or not HASH_RE.fullmatch(digest):
                    raise ValueError("invalid agent identity")
            elif key == "tools":
                if record.get("uri") != "tool://" + name or record.get("kind") != "tool" or record.get("status") not in {"missing", "available"} or not isinstance(record.get("verified"), bool):
                    raise ValueError("invalid tool")
                _validate_observation_fields(record)
                if record["status"] == "missing":
                    if "argv" in record or "identity" in record:
                        raise ValueError("invalid missing tool")
                    continue
                argv = record.get("argv")
                if not isinstance(argv, list) or len(argv) != 1 or not isinstance(argv[0], str) or not Path(argv[0]).is_absolute():
                    raise ValueError("invalid executable")
                digest = record.get("identity")
                if not isinstance(digest, str) or not HASH_RE.fullmatch(digest):
                    raise ValueError("invalid tool identity")
            else:
                # Keys are the tail after resource:// and are canonical slash-separated IDs.
                if record.get("uri") != "resource://" + name or record.get("kind") != "resource":
                    raise ValueError("invalid resource")
                parts = relative_parts(name)
                if any(not ID_RE.fullmatch(part) for part in parts):
                    raise ValueError("invalid resource id")
                if record.get("base") not in {"workspace", "skill"}:
                    raise ValueError("invalid resource base")
                rel = record.get("relative_path")
                if not isinstance(rel, str):
                    raise ValueError("invalid resource path")
                relative_parts(rel)
                owner = record.get("owner")
                if record["base"] == "skill":
                    if not isinstance(owner, str) or owner not in data["skills"]:
                        raise ValueError("invalid resource owner")
                elif owner is not None:
                    raise ValueError("workspace resource must not declare owner")
                digest = record.get("observed_sha256")
                if not isinstance(digest, str) or not HASH_RE.fullmatch(digest):
                    raise ValueError("invalid resource identity")
                _validate_observation_fields(record)


class Store:
    def __init__(self, workspace: Path):
        if not workspace.is_dir():
            raise RuntimeFault("INVALID_ROOT", "Workspace must be an existing directory.")
        self.workspace = workspace.resolve()
        self.root = confined(self.workspace, ".rhapsodia/runtime", write=True)

    @contextmanager
    def writer(self, *, wait_seconds: float = 0.2):
        """Serialize short publications without stealing another writer's lock."""
        confined(self.workspace, ".rhapsodia/runtime", write=True)
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        lock = confined(self.root, ".writer.lock", write=True)
        nonce = uuid.uuid4().hex
        data = canonical({"pid": os.getpid(), "nonce": nonce})
        deadline = time.monotonic() + max(0.0, wait_seconds)
        while True:
            try:
                fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
                break
            except FileExistsError as exc:
                if time.monotonic() >= deadline:
                    raise RuntimeFault("BUSY", "A writer lock exists. Do not steal it; retry after the active publication completes or recover manually if its owner stopped.", 5) from exc
                time.sleep(0.01)
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
        try:
            yield
        finally:
            if lock.is_file() and not lock.is_symlink() and lock.read_bytes() == data:
                lock.unlink()

    def _pointer(self, key: str, data: dict) -> dict:
        runtime = Path(__file__).resolve().parents[1] / "runtime.py"
        python_argv = [interpreter()]
        return {"schema": "runtime-bootstrap-v1", "snapshot_id": key, "snapshot_file": "snapshots/" + key + ".json",
                "python_argv": python_argv,
                "runtime_argv": python_argv + ["-I", "-S", "-B", str(runtime), "--workspace", str(self.workspace)],
                "created_at": data["created_at"], "updated_at": data["updated_at"],
                "max_age_seconds": data["max_age_seconds"],
                "notice": "Local observations only; not permission or validation evidence. Never reuse on another host."}

    def _publish(self, data: dict) -> tuple[str, dict]:
        validate_snapshot(data)
        key = sha(data)
        rel = "snapshots/" + key + ".json"
        atomic_write(self.root, rel, canonical(data), immutable=True)
        atomic_write(self.root, "current.json", canonical(self._pointer(key, data)))
        return key, data

    def current(self, *, validate_scope: bool = True) -> tuple[str, dict]:
        path = confined(self.root, "current.json")
        if not path.exists():
            raise RuntimeFault("NOT_INITIALIZED", "Run init once with this workspace and its approved skill roots.", 3)
        try:
            pointer = strict_json(read_bytes(path), MAX_STATE)
            key = pointer["snapshot_id"]
            if not isinstance(key, str) or not HASH_RE.fullmatch(key):
                raise ValueError("invalid identity")
            rel = "snapshots/" + key + ".json"
            if pointer["snapshot_file"] != rel:
                raise ValueError("invalid pointer")
            snapshot = strict_json(read_bytes(confined(self.root, rel)), MAX_STATE)
            if sha(snapshot) != key or snapshot["schema"] != "runtime-snapshot-v1" or snapshot["runtime_version"] != VERSION:
                raise ValueError("invalid snapshot")
            validate_snapshot(snapshot)
            runtime = Path(__file__).resolve().parents[1] / "runtime.py"
            recorded_python = snapshot["tools"]["python"]["argv"]
            expected = recorded_python + ["-I", "-S", "-B", str(runtime), "--workspace", str(self.workspace)]
            if pointer.get("schema") != "runtime-bootstrap-v1" or pointer.get("runtime_argv") != expected or pointer.get("python_argv") != recorded_python:
                raise ValueError("invalid bootstrap argv")
            if pointer.get("updated_at") != snapshot["updated_at"]:
                raise ValueError("invalid bootstrap timestamp")

            if snapshot["workspace"] != str(self.workspace):
                raise RuntimeFault("STALE_ENVIRONMENT", "Workspace changed; run init in the current workspace.", 3)
            number(snapshot["max_age_seconds"], 1, 86400)
            if validate_scope:
                if recorded_python != [interpreter()]:
                    raise RuntimeFault("STALE_ENVIRONMENT", "Recorded Python differs from the running interpreter; reinitialize.", 3)
                if snapshot["scope"] != scope_id(self.workspace):
                    raise RuntimeFault("STALE_ENVIRONMENT", "Host, workspace or interpreter identity changed; run init.", 3)
                age = time.time() - snapshot["created_at"]
                if age < -5 or age > snapshot["max_age_seconds"]:
                    raise RuntimeFault("EXPIRED", "Snapshot age is outside its validity interval; run init.", 3)
                if snapshot["agent_stamps"] != agent_stamps(self.workspace):
                    raise RuntimeFault("STALE_CATALOG", "An agent root changed; run init.", 3)
                if snapshot["root_stamps"] != root_stamps([Path(p) for p in snapshot["skill_roots"]]):
                    raise RuntimeFault("STALE_CATALOG", "A skill root changed; run init to refresh its index.", 3)
            return key, snapshot
        except RuntimeFault as exc:
            if exc.code in {"STALE_ENVIRONMENT", "STALE_CATALOG", "EXPIRED"}:
                raise
            raise RuntimeFault("CORRUPT_STATE", "Snapshot integrity check failed; inspect the local state and explicitly refresh.", 3) from exc
        except (KeyError, TypeError, ValueError) as exc:
            raise RuntimeFault("CORRUPT_STATE", "Snapshot schema or identity is invalid; explicitly refresh after inspection.", 3) from exc

    def initialize(self, supplied: list[Path] | None = None, *, refresh: bool = False, max_age: int | None = None) -> dict:
        if max_age is not None:
            number(max_age, 1, 86400)
        previous = None
        unchecked = None
        try:
            old_id, previous = self.current()
        except RuntimeFault as exc:
            if exc.code not in {"NOT_INITIALIZED", "STALE_ENVIRONMENT", "STALE_CATALOG", "EXPIRED", "CORRUPT_STATE"} and not refresh:
                raise
            if exc.code == "CORRUPT_STATE" and not refresh:
                raise
        if supplied is None and previous is not None:
            supplied = [Path(p) for p in previous["skill_roots"]]
        elif supplied is None and (self.root / "current.json").exists():
            try:
                _, unchecked = self.current(validate_scope=False)
                supplied = [Path(p) for p in unchecked["skill_roots"]]
            except RuntimeFault:
                if not refresh:
                    raise
        if max_age is None:
            max_age = previous["max_age_seconds"] if previous is not None else 86400
            if previous is None and unchecked is not None:
                max_age = unchecked["max_age_seconds"]
        roots = selected_roots(self.workspace, supplied)
        if previous is not None and not refresh and previous["skill_roots"] == [str(p) for p in roots] and previous["max_age_seconds"] == max_age:
            return self.summary(old_id, cache_hit=True)
        with self.writer():
            data = discover(self.workspace, roots, max_age)
            key, _ = self._publish(data)
        return self.summary(key, cache_hit=False)

    def publish_observations(self, *, tools: dict | None = None, resources: dict | None = None) -> tuple[str, dict, bool]:
        """Merge validated observations into the latest snapshot under one writer lock."""
        tools = tools or {}
        resources = resources or {}
        if len(tools) > 32 or len(resources) > 32:
            raise RuntimeFault("INVALID_INPUT", "At most 32 observations may be published per operation.")
        with self.writer():
            current_id, snapshot = self.current()
            merged_tools = dict(snapshot["tools"])
            merged_resources = dict(snapshot["resources"])
            changed = False
            for name, record in tools.items():
                if merged_tools.get(name) != record:
                    merged_tools[name] = record
                    changed = True
            for name, record in resources.items():
                if merged_resources.get(name) != record:
                    merged_resources[name] = record
                    changed = True
            if not changed:
                return current_id, snapshot, False
            data = dict(snapshot)
            data["tools"] = merged_tools
            data["resources"] = merged_resources
            data["updated_at"] = time.time()
            key, data = self._publish(data)
            return key, data, True

    def summary(self, key: str, *, cache_hit: bool) -> dict:
        return {"status": "ready", "snapshot_id": key, "cache_hit": cache_hit,
                "discovery_performed": not cache_hit, "bootstrap": str(self.root / "current.json")}
