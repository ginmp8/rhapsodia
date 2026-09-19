#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _wiki_common import atomic_write_json, ensure_within, load_json, parse_frontmatter, sha256_file, stable_id  # noqa: E402


def _allowed_target(rel: str) -> bool:
    if rel == "WIKI_SCHEMA.md":
        return True
    return rel.startswith("wiki/") and rel != "wiki/"


def _canonical_rel(workspace: Path, rel: str) -> tuple[str, Path]:
    p = Path(rel)
    if p.is_absolute() or ".." in p.parts:
        raise ValueError(f"target must be a normalized relative path: {rel}")
    normalized = p.as_posix()
    if not _allowed_target(normalized):
        raise ValueError(f"target is outside writable wiki boundary: {rel}")
    target = ensure_within(workspace, workspace / p)
    if target.exists() and target.is_symlink():
        raise ValueError(f"target symlink is not allowed: {rel}")
    return normalized, target


def _hash_or_none(path: Path) -> str | None:
    return sha256_file(path) if path.exists() and path.is_file() else None


def _write_target_atomic(target: Path, staged: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{target.name}.", suffix=".tmp", dir=str(target.parent))
    try:
        with os.fdopen(fd, "wb") as out, staged.open("rb") as inp:
            shutil.copyfileobj(inp, out, length=1024 * 1024)
            out.flush()
            os.fsync(out.fileno())
        os.replace(tmp_name, target)
    except Exception:
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass
        raise


def _build_changes(workspace: Path, staging: Path, plan: dict[str, Any], allow_delete: bool) -> list[dict[str, Any]]:
    changes: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in plan.get("writes", []):
        rel, target = _canonical_rel(workspace, item["path"])
        if rel in seen:
            raise ValueError(f"duplicate target in plan: {rel}")
        seen.add(rel)
        staged = ensure_within(staging, staging / rel)
        if not staged.is_file():
            raise ValueError(f"staged file missing: {rel}")
        changes.append({
            "action": "write",
            "path": rel,
            "target": target,
            "staged": staged,
            "expected_before_sha256": item.get("expected_before_sha256"),
            "before_sha256": _hash_or_none(target),
            "after_sha256": sha256_file(staged),
        })
    deletes = plan.get("deletes", [])
    if deletes and not allow_delete:
        raise ValueError("plan contains deletes but --allow-delete was not supplied")
    for item in deletes:
        rel, target = _canonical_rel(workspace, item["path"])
        if rel in seen:
            raise ValueError(f"duplicate target in plan: {rel}")
        seen.add(rel)
        changes.append({
            "action": "delete",
            "path": rel,
            "target": target,
            "staged": None,
            "expected_before_sha256": item.get("expected_before_sha256"),
            "before_sha256": _hash_or_none(target),
            "after_sha256": None,
        })
    return changes


def _txn_identity(plan: dict[str, Any], changes: list[dict[str, Any]]) -> str:
    payload = {
        "operation": plan.get("operation"),
        "schema_version": plan.get("schema_version"),
        "source_ids": sorted(set(plan.get("source_ids", []))),
        "changes": [
            {
                "action": c["action"],
                "path": c["path"],
                "expected_before_sha256": c["expected_before_sha256"],
                "after_sha256": c["after_sha256"],
            }
            for c in sorted(changes, key=lambda x: x["path"])
        ],
    }
    return stable_id("txn", payload)


def _already_applied(changes: list[dict[str, Any]]) -> bool:
    for c in changes:
        current = _hash_or_none(c["target"])
        if c["action"] == "write" and current != c["after_sha256"]:
            return False
        if c["action"] == "delete" and current is not None:
            return False
    return True


def _check_preconditions(changes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    failures = []
    for c in changes:
        observed = _hash_or_none(c["target"])
        expected = c["expected_before_sha256"]
        if c["action"] == "write" and observed is not None and expected is None:
            failures.append({"code": "mutation/existing-target-without-precondition", "path": c["path"], "observed": observed})
        elif observed != expected:
            failures.append({"code": "mutation/precondition-mismatch", "path": c["path"], "expected": expected, "observed": observed})
    return failures


def _backup(workspace: Path, txn_id: str, changes: list[dict[str, Any]]) -> Path:
    recovery = workspace / ".llm-wiki" / "recovery" / txn_id.replace(":", "-") / "before"
    for c in changes:
        if c["before_sha256"] is None:
            continue
        dst = recovery / c["path"]
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(c["target"], dst)
        if sha256_file(dst) != c["before_sha256"]:
            raise RuntimeError(f"backup verification failed: {c['path']}")
    return recovery


def _rollback_changes(changes: list[dict[str, Any]], recovery: Path) -> list[dict[str, Any]]:
    results = []
    for c in reversed(changes):
        target = c["target"]
        before = c["before_sha256"]
        if before is None:
            if target.exists():
                target.unlink()
            results.append({"path": c["path"], "status": "restored-missing"})
            continue
        backup = recovery / c["path"]
        if not backup.is_file() or sha256_file(backup) != before:
            results.append({"path": c["path"], "status": "failed", "reason": "missing-or-corrupt-backup"})
            continue
        _write_target_atomic(target, backup)
        ok = _hash_or_none(target) == before
        results.append({"path": c["path"], "status": "restored" if ok else "failed"})
    return results


def commit_transaction(workspace: Path, staging: Path, plan: dict[str, Any], receipt_path: Path, allow_delete: bool = False, fail_after: int | None = None) -> tuple[int, dict[str, Any]]:
    workspace = workspace.resolve(strict=True)
    staging = staging.resolve(strict=True)
    if plan.get("transaction_version") != 1:
        raise ValueError("transaction_version must be 1")
    receipt_path = receipt_path.resolve(strict=False)
    raw_root = (workspace / "raw").resolve(strict=False)
    wiki_root = (workspace / "wiki").resolve(strict=False)
    schema_path = (workspace / "WIKI_SCHEMA.md").resolve(strict=False)
    if receipt_path == raw_root or raw_root in receipt_path.parents:
        raise ValueError("receipt output must not be inside raw/")
    if receipt_path == wiki_root or wiki_root in receipt_path.parents or receipt_path == schema_path:
        raise ValueError("receipt output must not alias maintained wiki content")
    if receipt_path == staging or staging in receipt_path.parents:
        raise ValueError("receipt output must not alias or live inside staging")
    changes = _build_changes(workspace, staging, plan, allow_delete)
    for c in changes:
        if receipt_path in {c["target"].resolve(strict=False), c["staged"].resolve(strict=False) if c["staged"] else None}:
            raise ValueError("receipt output aliases a transaction input/output")
    txn_id = _txn_identity(plan, changes)
    page_provenance = []
    for c in sorted(changes, key=lambda x: x["path"]):
        if c["action"] != "write" or not c["path"].startswith(("wiki/sources/", "wiki/entities/", "wiki/concepts/", "wiki/syntheses/")) or not c["path"].endswith(".md"):
            continue
        try:
            meta, _ = parse_frontmatter(c["staged"].read_text(encoding="utf-8"))
        except Exception:
            meta = {}
        if meta.get("page_id"):
            page_provenance.append({
                "page_id": meta.get("page_id"),
                "path": c["path"],
                "source_ids": sorted(set(meta.get("source_ids", []))),
            })
    source_to_pages: dict[str, list[str]] = {}
    for page in page_provenance:
        for sid in page["source_ids"]:
            source_to_pages.setdefault(sid, []).append(page["page_id"])
    source_to_pages = {sid: sorted(set(ids)) for sid, ids in sorted(source_to_pages.items())}
    base_receipt = {
        "receipt_version": 1,
        "stage": "mutation",
        "transaction_id": txn_id,
        "operation": plan.get("operation"),
        "schema_version": plan.get("schema_version"),
        "source_ids": sorted(set(plan.get("source_ids", []))),
        "page_provenance": page_provenance,
        "source_to_pages": source_to_pages,
    }
    if _already_applied(changes):
        receipt = {**base_receipt, "status": "pass", "classification": "already-applied", "changes": [{k: c[k] for k in ("action", "path", "before_sha256", "after_sha256")} for c in changes], "recovery": []}
        atomic_write_json(receipt_path, receipt)
        return 0, receipt

    failures = _check_preconditions(changes)
    if failures:
        receipt = {**base_receipt, "status": "blocked", "classification": "precondition-failed", "checks": failures, "changes": [{k: c[k] for k in ("action", "path", "before_sha256", "after_sha256", "expected_before_sha256")} for c in changes], "recovery": []}
        atomic_write_json(receipt_path, receipt)
        return 2, receipt

    recovery = _backup(workspace, txn_id, changes)
    touched: list[dict[str, Any]] = []
    try:
        for idx, c in enumerate(changes, 1):
            if c["action"] == "write":
                _write_target_atomic(c["target"], c["staged"])
            else:
                if c["target"].exists():
                    c["target"].unlink()
            touched.append(c)
            if fail_after is not None and idx >= fail_after:
                raise RuntimeError("injected test failure")
        for c in changes:
            if _hash_or_none(c["target"]) != c["after_sha256"]:
                raise RuntimeError(f"postcondition failed: {c['path']}")
    except Exception as exc:
        rollback = _rollback_changes(touched, recovery)
        rollback_ok = all(r["status"] != "failed" for r in rollback)
        receipt = {
            **base_receipt,
            "status": "failed",
            "classification": "commit-failed-rolled-back" if rollback_ok else "commit-failed-recovery-needed",
            "error": str(exc),
            "changes": [{k: c[k] for k in ("action", "path", "before_sha256", "after_sha256", "expected_before_sha256")} for c in changes],
            "recovery": rollback,
            "recovery_root": recovery.parent.relative_to(workspace).as_posix(),
        }
        atomic_write_json(receipt_path, receipt)
        return 1, receipt

    receipt = {
        **base_receipt,
        "status": "pass",
        "classification": "committed",
        "changes": [
            {
                "action": c["action"],
                "path": c["path"],
                "before_sha256": c["before_sha256"],
                "after_sha256": c["after_sha256"],
                "backup": (recovery / c["path"]).relative_to(workspace).as_posix() if c["before_sha256"] else None,
            }
            for c in changes
        ],
        "recovery": [],
        "recovery_root": recovery.parent.relative_to(workspace).as_posix(),
    }
    atomic_write_json(receipt_path, receipt)
    return 0, receipt


def rollback_receipt(workspace: Path, original_receipt: dict[str, Any], out_path: Path) -> tuple[int, dict[str, Any]]:
    workspace = workspace.resolve(strict=True)
    out_path = out_path.resolve(strict=False)
    raw_root = (workspace / "raw").resolve(strict=False)
    wiki_root = (workspace / "wiki").resolve(strict=False)
    schema_path = (workspace / "WIKI_SCHEMA.md").resolve(strict=False)
    if out_path == raw_root or raw_root in out_path.parents:
        raise ValueError("rollback receipt output must not be inside raw/")
    if out_path == wiki_root or wiki_root in out_path.parents or out_path == schema_path:
        raise ValueError("rollback receipt output must not alias maintained wiki content")
    if original_receipt.get("status") != "pass" or original_receipt.get("classification") not in {"committed", "already-applied"}:
        report = {"receipt_version": 1, "stage": "rollback", "status": "blocked", "reason": "receipt-does-not-describe-a-committed-transaction"}
        atomic_write_json(out_path, report)
        return 2, report
    if original_receipt.get("classification") == "already-applied" or not original_receipt.get("recovery_root"):
        report = {"receipt_version": 1, "stage": "rollback", "status": "blocked", "reason": "no-owned-recovery-snapshot-for-this-receipt"}
        atomic_write_json(out_path, report)
        return 2, report
    recovery = workspace / original_receipt["recovery_root"] / "before"
    changes = []
    drift = []
    for item in original_receipt.get("changes", []):
        rel, target = _canonical_rel(workspace, item["path"])
        observed = _hash_or_none(target)
        if observed != item.get("after_sha256"):
            drift.append({"path": rel, "expected_current": item.get("after_sha256"), "observed": observed})
        changes.append({"path": rel, "target": target, "before_sha256": item.get("before_sha256")})
    if drift:
        report = {"receipt_version": 1, "stage": "rollback", "status": "blocked", "reason": "post-commit-drift", "drift": drift}
        atomic_write_json(out_path, report)
        return 2, report
    results = _rollback_changes(changes, recovery)
    ok = all(r["status"] != "failed" for r in results)
    report = {"receipt_version": 1, "stage": "rollback", "status": "pass" if ok else "fail", "transaction_id": original_receipt.get("transaction_id"), "results": results}
    atomic_write_json(out_path, report)
    return (0 if ok else 1), report


def main() -> int:
    ap = argparse.ArgumentParser(description="Recovery-aware multi-page wiki commit with precondition hashes and rollback.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("commit")
    p.add_argument("--workspace", required=True)
    p.add_argument("--staging", required=True)
    p.add_argument("--plan", required=True)
    p.add_argument("--json", required=True)
    p.add_argument("--allow-delete", action="store_true")
    p = sub.add_parser("rollback")
    p.add_argument("--workspace", required=True)
    p.add_argument("--receipt", required=True)
    p.add_argument("--json", required=True)
    args = ap.parse_args()

    if args.cmd == "commit":
        code, report = commit_transaction(Path(args.workspace), Path(args.staging), load_json(Path(args.plan)), Path(args.json), args.allow_delete)
    else:
        code, report = rollback_receipt(Path(args.workspace), load_json(Path(args.receipt)), Path(args.json))
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
