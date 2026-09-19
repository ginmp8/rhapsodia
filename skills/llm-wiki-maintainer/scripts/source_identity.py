#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _wiki_common import (  # noqa: E402
    STATE_VERSION,
    atomic_write_json,
    ensure_within,
    load_json,
    sha256_file,
    stable_id,
)

MANIFEST_VERSION = 1


def _state_paths(workspace: Path) -> tuple[Path, Path, Path]:
    state = workspace / ".llm-wiki"
    return state, state / "source-manifest.json", state / "source-snapshots"


def _empty_manifest() -> dict:
    return {"manifest_version": MANIFEST_VERSION, "state_schema_version": STATE_VERSION, "paths": {}, "sources": {}}


def _receipt_path(workspace: Path, explicit: str | None, operation_id: str) -> Path:
    return Path(explicit).resolve() if explicit else workspace / ".llm-wiki" / "receipts" / "ingest" / f"{operation_id.replace(':', '-')}.json"


def identify(path: Path) -> dict:
    digest = sha256_file(path)
    return {"source_id": f"sha256:{digest}", "sha256": digest, "size": path.stat().st_size}


def capture(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve(strict=True)
    source_root_input = Path(args.source_root) if args.source_root else (workspace / "raw")
    if not source_root_input.is_absolute():
        source_root_input = workspace / source_root_input
    source_root = ensure_within(workspace, source_root_input)
    if not source_root.is_dir():
        raise SystemExit(f"source root is not a directory: {source_root}")
    source_input = Path(args.source)
    if not source_input.is_absolute():
        source_input = workspace / source_input
    source = ensure_within(source_root, source_input)
    if not source.is_file():
        raise SystemExit(f"source is not a file: {source}")

    state, manifest_path, snapshots = _state_paths(workspace)
    manifest = load_json(manifest_path, _empty_manifest())
    info = identify(source)
    source_id = info["source_id"]
    rel = source.relative_to(workspace).as_posix()
    old = manifest.get("paths", {}).get(rel)
    operation_id = stable_id("ingest", {"schema": args.schema_version, "source_id": source_id, "source_path": rel})
    receipt_path = _receipt_path(workspace, args.json, operation_id).resolve(strict=False)
    raw_boundary = (workspace / "raw").resolve(strict=False)
    wiki_boundary = (workspace / "wiki").resolve(strict=False)
    schema_path = (workspace / "WIKI_SCHEMA.md").resolve(strict=False)
    if receipt_path == raw_boundary or raw_boundary in receipt_path.parents:
        raise SystemExit("receipt output must not be inside raw/")
    if receipt_path == wiki_boundary or wiki_boundary in receipt_path.parents or receipt_path == schema_path:
        raise SystemExit("receipt output must not alias maintained wiki content")
    if receipt_path == source.resolve(strict=False) or receipt_path == manifest_path.resolve(strict=False):
        raise SystemExit("receipt output aliases a protected input/state path")

    if old and old.get("source_id") != source_id and not args.accept_external_replacement:
        receipt = {
            "receipt_version": 1,
            "stage": "ingest",
            "status": "blocked",
            "operation_id": operation_id,
            "classification": "source-modified",
            "schema_version": args.schema_version,
            "source_path": rel,
            "previous_source_id": old.get("source_id"),
            **info,
            "checks": [{"code": "source/path-modified", "status": "fail", "subject": rel, "evidence": {"previous_source_id": old.get("source_id"), "observed_source_id": source_id}}],
        }
        atomic_write_json(receipt_path, receipt)
        print(json.dumps(receipt, indent=2))
        return 2

    snapshot_dir = snapshots / info["sha256"]
    snapshot = snapshot_dir / "content"
    if receipt_path == snapshot.resolve(strict=False):
        raise SystemExit("receipt output aliases the immutable source snapshot")
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    if snapshot.exists():
        snap_hash = sha256_file(snapshot)
        if snap_hash != info["sha256"]:
            raise SystemExit(f"snapshot hash mismatch for {source_id}")
    else:
        fd, tmp_name = tempfile.mkstemp(prefix=".content.", suffix=".tmp", dir=str(snapshot_dir))
        try:
            with os.fdopen(fd, "wb") as out, source.open("rb") as inp:
                shutil.copyfileobj(inp, out, length=1024 * 1024)
                out.flush()
                os.fsync(out.fileno())
            if sha256_file(Path(tmp_name)) != info["sha256"]:
                raise RuntimeError("snapshot copy hash mismatch")
            os.replace(tmp_name, snapshot)
            try:
                snapshot.chmod(0o444)
            except OSError:
                pass
        except Exception:
            try:
                os.unlink(tmp_name)
            except FileNotFoundError:
                pass
            raise

    sources = manifest.setdefault("sources", {})
    paths = manifest.setdefault("paths", {})
    entry = sources.get(source_id, {
        "sha256": info["sha256"],
        "size": info["size"],
        "snapshot": snapshot.relative_to(workspace).as_posix(),
        "aliases": [],
    })
    aliases = sorted(set(entry.get("aliases", [])) | {rel})
    entry["aliases"] = aliases
    sources[source_id] = entry
    replacement = old.get("source_id") if old and old.get("source_id") != source_id else None
    paths[rel] = {"source_id": source_id}
    if replacement:
        paths[rel]["replaces_source_id"] = replacement
    manifest["manifest_version"] = MANIFEST_VERSION
    manifest["state_schema_version"] = STATE_VERSION
    atomic_write_json(manifest_path, manifest)

    existing_same_path = old and old.get("source_id") == source_id
    duplicate_alias = not existing_same_path and len(aliases) > 1
    classification = "already-ingested" if existing_same_path else ("duplicate-content-alias" if duplicate_alias else ("external-replacement-accepted" if replacement else "first-ingest"))
    receipt = {
        "receipt_version": 1,
        "stage": "ingest",
        "status": "pass",
        "operation_id": operation_id,
        "classification": classification,
        "schema_version": args.schema_version,
        "source_path": rel,
        "source_aliases": aliases,
        "snapshot_path": snapshot.relative_to(workspace).as_posix(),
        "snapshot_sha256": sha256_file(snapshot),
        "manifest_sha256": sha256_file(manifest_path),
        **info,
        "checks": [
            {"code": "source/inside-boundary", "status": "pass", "subject": rel, "evidence": {"source_root": source_root.as_posix()}},
            {"code": "source/snapshot-hash", "status": "pass", "subject": source_id, "evidence": {"sha256": info["sha256"]}},
        ],
    }
    if replacement:
        receipt["previous_source_id"] = replacement
    atomic_write_json(receipt_path, receipt)
    print(json.dumps(receipt, indent=2))
    return 0


def verify(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve(strict=True)
    state, manifest_path, _ = _state_paths(workspace)
    manifest = load_json(manifest_path)
    if not manifest:
        report = {"receipt_version": 1, "stage": "source-verify", "status": "blocked", "checks": [{"code": "manifest/missing", "status": "fail", "subject": str(manifest_path), "evidence": {}}]}
        if args.json:
            atomic_write_json(Path(args.json), report)
        print(json.dumps(report, indent=2))
        return 2

    checks = []
    hard_fail = False
    warnings = False
    for source_id, entry in sorted(manifest.get("sources", {}).items()):
        snapshot = workspace / entry["snapshot"]
        if not snapshot.exists():
            checks.append({"code": "snapshot/missing", "status": "fail", "subject": source_id, "evidence": {"snapshot": entry["snapshot"]}})
            hard_fail = True
        else:
            observed = sha256_file(snapshot)
            expected = entry["sha256"]
            ok = observed == expected
            checks.append({"code": "snapshot/hash", "status": "pass" if ok else "fail", "subject": source_id, "evidence": {"expected": expected, "observed": observed}})
            hard_fail |= not ok
    for rel, pentry in sorted(manifest.get("paths", {}).items()):
        path = workspace / rel
        expected = pentry["source_id"]
        if not path.exists():
            checks.append({"code": "source/path-missing", "status": "warn", "subject": rel, "evidence": {"source_id": expected}})
            warnings = True
        elif not path.is_file():
            checks.append({"code": "source/path-not-file", "status": "fail", "subject": rel, "evidence": {"source_id": expected}})
            hard_fail = True
        else:
            observed = f"sha256:{sha256_file(path)}"
            ok = observed == expected
            checks.append({"code": "source/path-hash", "status": "pass" if ok else "fail", "subject": rel, "evidence": {"expected": expected, "observed": observed}})
            hard_fail |= not ok
    status = "fail" if hard_fail else ("warn" if warnings else "pass")
    report = {"receipt_version": 1, "stage": "source-verify", "status": status, "manifest": manifest_path.relative_to(workspace).as_posix(), "checks": checks}
    if args.json:
        out = Path(args.json).resolve(strict=False)
        raw_boundary = (workspace / "raw").resolve(strict=False)
        wiki_boundary = (workspace / "wiki").resolve(strict=False)
        schema_path = (workspace / "WIKI_SCHEMA.md").resolve(strict=False)
        if out == raw_boundary or raw_boundary in out.parents or out == wiki_boundary or wiki_boundary in out.parents or out == schema_path or out == manifest_path.resolve(strict=False):
            raise SystemExit("source verification receipt aliases protected source/wiki/state content")
        atomic_write_json(out, report)
    print(json.dumps(report, indent=2))
    return 1 if hard_fail else 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Deterministic source identity, immutable snapshot, duplicate detection, and source-integrity verification.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("identify")
    p.add_argument("source")
    p.add_argument("--json")
    p = sub.add_parser("capture")
    p.add_argument("--workspace", required=True)
    p.add_argument("--source", required=True)
    p.add_argument("--source-root")
    p.add_argument("--schema-version", default="llm-wiki/2")
    p.add_argument("--accept-external-replacement", action="store_true")
    p.add_argument("--json")
    p = sub.add_parser("verify")
    p.add_argument("--workspace", required=True)
    p.add_argument("--json")
    args = ap.parse_args()
    if args.cmd == "identify":
        info = identify(Path(args.source).resolve(strict=True))
        if args.json:
            atomic_write_json(Path(args.json), info)
        print(json.dumps(info, indent=2))
        return 0
    if args.cmd == "capture":
        return capture(args)
    return verify(args)


if __name__ == "__main__":
    raise SystemExit(main())
