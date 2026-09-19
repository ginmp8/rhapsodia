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

from _swp_common import (  # noqa: E402
    MODES, atomic_write_json, is_protected_relative, resolve_inside, sha256_bytes,
    sha256_file, tree_hash,
)
from validate_sequential import validate_cycle  # noqa: E402
from validate_transition import validate_transition  # noqa: E402


def _transaction_identity(
    *,
    cycle_root: Path,
    mode: str,
    allow_order_change: bool,
    protected_paths: list[str],
    post_validate: dict[str, Any],
    prepared: list[dict[str, Any]],
) -> str:
    stable = {
        "plan_version": 1,
        "mode": mode,
        "cycle_root": str(cycle_root),
        "allow_order_change": allow_order_change,
        "protected_paths": sorted(set(protected_paths)),
        "post_validate": {
            "mode": post_validate.get("mode", mode),
            "spec_id": post_validate.get("spec_id"),
        },
        "writes": sorted(
            [
                {
                    "path": item["rel"],
                    "expected_before_sha256": item["expected"],
                    "candidate_sha256": item["candidate_hash"],
                }
                for item in prepared
            ],
            key=lambda item: item["path"],
        ),
    }
    encoded = json.dumps(stable, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256_bytes(encoded)[:24]


def apply(plan_path: Path, receipt_path: Path, fail_after: int | None = None) -> dict:
    try:
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return _failure("PLAN_PARSE_ERROR", str(plan_path), str(exc))

    if not isinstance(plan, dict):
        return _failure("PLAN_INVALID", "plan", "operation plan must be a JSON object")
    if plan.get("plan_version") != 1:
        return _failure("PLAN_VERSION_INVALID", "plan_version", plan.get("plan_version"))
    allowed_plan_fields = {
        "plan_version", "mode", "cycle_root", "protected_paths", "allow_order_change",
        "post_validate", "writes",
    }
    unknown_plan_fields = sorted(set(plan) - allowed_plan_fields)
    if unknown_plan_fields:
        return _failure("PLAN_FIELDS_UNKNOWN", "plan", unknown_plan_fields)

    mode = plan.get("mode")
    if mode not in MODES or mode == "audit":
        return _failure("PLAN_MODE_INVALID", "mode", mode)

    cycle_root_raw = plan.get("cycle_root")
    if not isinstance(cycle_root_raw, str) or not cycle_root_raw.strip():
        return _failure("CYCLE_ROOT_INVALID", "cycle_root", cycle_root_raw)
    cycle_root = Path(cycle_root_raw).resolve()
    if not cycle_root.exists() or not cycle_root.is_dir():
        return _failure("CYCLE_ROOT_MISSING", str(cycle_root), "cycle root does not exist")

    receipt_resolved = receipt_path.resolve(strict=False)
    if _is_within(receipt_resolved, cycle_root):
        return _failure(
            "RECEIPT_INSIDE_CYCLE",
            str(receipt_resolved),
            "transaction receipts must live outside the canonical cycle tree",
        )

    writes = plan.get("writes")
    if not isinstance(writes, list) or not writes:
        return _persist_failure(receipt_path, "WRITES_MISSING", "writes", "writes must be a non-empty list")

    protected_raw = plan.get("protected_paths") or []
    if not isinstance(protected_raw, list) or not all(isinstance(x, str) for x in protected_raw):
        return _persist_failure(receipt_path, "PROTECTED_PATHS_INVALID", "protected_paths", protected_raw)
    extra_protected = list(protected_raw)

    allow_order_change = plan.get("allow_order_change", False)
    if not isinstance(allow_order_change, bool):
        return _persist_failure(receipt_path, "ALLOW_ORDER_CHANGE_INVALID", "allow_order_change", allow_order_change)
    if allow_order_change and mode != "order":
        return _persist_failure(
            receipt_path,
            "ALLOW_ORDER_CHANGE_SCOPE_INVALID",
            "allow_order_change",
            "explicit order changes are supported only in order mode",
        )

    post_validate = plan.get("post_validate") or {"mode": mode}
    if not isinstance(post_validate, dict):
        return _persist_failure(receipt_path, "POST_VALIDATE_INVALID", "post_validate", post_validate)
    unknown_post_fields = sorted(set(post_validate) - {"mode", "spec_id"})
    if unknown_post_fields:
        return _persist_failure(receipt_path, "POST_VALIDATE_FIELDS_UNKNOWN", "post_validate", unknown_post_fields)
    post_mode = post_validate.get("mode", mode)
    post_spec_id = post_validate.get("spec_id")
    if post_mode not in MODES:
        return _persist_failure(receipt_path, "POST_VALIDATE_MODE_INVALID", "post_validate.mode", post_mode)
    if post_mode != mode:
        return _persist_failure(
            receipt_path,
            "POST_VALIDATE_MODE_MISMATCH",
            "post_validate.mode",
            {"operation_mode": mode, "post_validate_mode": post_mode},
        )
    if post_spec_id is not None and not isinstance(post_spec_id, str):
        return _persist_failure(receipt_path, "POST_VALIDATE_SPEC_INVALID", "post_validate.spec_id", post_spec_id)

    plan_resolved = plan_path.resolve(strict=False)
    symlink_issues = _symlink_issues(cycle_root)
    if symlink_issues:
        return _persist_failure(receipt_path, "SYMLINK_ESCAPE", str(cycle_root), symlink_issues)

    root_token = sha256_bytes(str(cycle_root).encode("utf-8"))[:12]
    lock_path = cycle_root.parent / f".swp-lock-{root_token}"
    try:
        lock_acquired = _acquire_lock(lock_path, cycle_root)
    except Exception as exc:
        return _persist_failure(
            receipt_path,
            "LOCK_ACQUIRE_FAILED",
            str(cycle_root),
            {"lock_path": str(lock_path), "error": str(exc)},
        )
    if not lock_acquired:
        return _persist_failure(receipt_path, "TRANSACTION_LOCKED", str(cycle_root), {"lock_path": str(lock_path)})

    txn_dir: Path | None = None
    prepared: list[dict[str, Any]] = []
    transaction_id: str | None = None
    before_tree_sha256: str | None = None
    candidate_tree_sha256: str | None = None
    candidate_validation: dict | None = None
    candidate_transition: dict | None = None
    post_validation: dict | None = None
    post_transition: dict | None = None
    committed: list[dict[str, Any]] = []
    created_dirs: list[Path] = []

    try:
        recovery_paths = _recovery_paths(cycle_root, root_token)
        if recovery_paths:
            return _persist_failure(
                receipt_path,
                "RECOVERY_STATE_PRESENT",
                str(cycle_root),
                {"paths": [str(p) for p in recovery_paths]},
            )

        seen_targets: set[Path] = set()
        for idx, write in enumerate(writes):
            if not isinstance(write, dict):
                return _persist_failure(receipt_path, "WRITE_INVALID", f"writes[{idx}]", "write must be an object")
            unknown_write_fields = sorted(set(write) - {"path", "source", "expected_before_sha256"})
            if unknown_write_fields:
                return _persist_failure(receipt_path, "WRITE_FIELDS_UNKNOWN", f"writes[{idx}]", unknown_write_fields)
            rel = write.get("path")
            src_raw = write.get("source")
            expected = write.get("expected_before_sha256")
            if not isinstance(rel, str) or not isinstance(src_raw, str) or not isinstance(expected, str):
                return _persist_failure(
                    receipt_path,
                    "WRITE_FIELDS_MISSING",
                    f"writes[{idx}]",
                    "path, source, and expected_before_sha256 are required strings",
                )
            if expected != "ABSENT" and not _is_sha256(expected):
                return _persist_failure(receipt_path, "EXPECTED_HASH_INVALID", rel, expected)
            if is_protected_relative(rel, extra_protected):
                return _persist_failure(receipt_path, "PROTECTED_PATH", rel, None)
            try:
                target = resolve_inside(cycle_root, rel)
            except Exception as exc:
                return _persist_failure(receipt_path, "TARGET_PATH_INVALID", rel, str(exc))

            lexical_target = Path(os.path.abspath(cycle_root / rel))
            if target != lexical_target:
                return _persist_failure(
                    receipt_path,
                    "TARGET_SYMLINK_ALIAS",
                    rel,
                    {"authored": str(lexical_target), "resolved": str(target)},
                )

            source = Path(src_raw).resolve()
            if not source.is_file():
                return _persist_failure(receipt_path, "SOURCE_MISSING", str(source), None)
            if target in seen_targets:
                return _persist_failure(receipt_path, "TARGET_DUPLICATE", rel, None)
            seen_targets.add(target)
            if source == target or _samefile_if_exists(source, target):
                return _persist_failure(receipt_path, "SOURCE_TARGET_ALIAS", rel, None)
            if target == plan_resolved or _samefile_if_exists(target, plan_resolved):
                return _persist_failure(receipt_path, "PLAN_TARGET_ALIAS", rel, str(plan_resolved))
            if source == receipt_resolved or target == receipt_resolved or _samefile_if_exists(source, receipt_resolved) or _samefile_if_exists(target, receipt_resolved):
                return _persist_failure(receipt_path, "RECEIPT_ALIAS", rel, None)

            candidate_hash = sha256_file(source)
            current_hash = sha256_file(target) if target.is_file() else None
            noop = current_hash == candidate_hash
            if not noop:
                if expected == "ABSENT":
                    if target.exists():
                        return _persist_failure(receipt_path, "EXPECTED_ABSENT_MISMATCH", rel, {"actual": current_hash})
                else:
                    if not target.is_file():
                        return _persist_failure(receipt_path, "EXPECTED_HASH_TARGET_MISSING", rel, None)
                    if current_hash != expected:
                        return _persist_failure(
                            receipt_path,
                            "EXPECTED_HASH_MISMATCH",
                            rel,
                            {"expected": expected, "actual": current_hash},
                        )
            prepared.append(
                {
                    "rel": rel,
                    "source": source,
                    "target": target,
                    "candidate_hash": candidate_hash,
                    "current_hash": current_hash,
                    "noop": noop,
                    "expected": expected,
                }
            )

        transaction_id = _transaction_identity(
            cycle_root=cycle_root,
            mode=mode,
            allow_order_change=allow_order_change,
            protected_paths=extra_protected,
            post_validate=post_validate,
            prepared=prepared,
        )

        if all(item["noop"] for item in prepared):
            post_validation = validate_cycle(cycle_root, post_mode, post_spec_id)
            if post_validation["status"] != "pass":
                return _persist_failure(
                    receipt_path,
                    "POSTCONDITION_FAILED",
                    str(cycle_root),
                    post_validation,
                    transaction_id=transaction_id,
                )
            final_hash = tree_hash(cycle_root)
            receipt = _receipt(
                "no_change",
                "postcondition",
                transaction_id,
                cycle_root,
                prepared,
                [{"path": x["rel"], "sha256": x["current_hash"], "noop": True} for x in prepared],
                post_validation,
                None,
                before_tree_sha256=final_hash,
                candidate_tree_sha256=final_hash,
                after_tree_sha256=final_hash,
                candidate_validation=post_validation,
            )
            atomic_write_json(receipt_path, receipt)
            return receipt

        txn_dir = Path(
            tempfile.mkdtemp(
                prefix=f".swp-txn-{root_token}-{transaction_id}-",
                dir=str(cycle_root.parent),
            )
        )
        before_root = txn_dir / "before" / cycle_root.name
        candidate_root = txn_dir / "candidate" / cycle_root.name
        stage_dir = txn_dir / "stage"
        backup_dir = txn_dir / "backups"
        stage_dir.mkdir()
        backup_dir.mkdir()

        shutil.copytree(cycle_root, before_root, symlinks=True)
        before_tree_sha256 = tree_hash(before_root)
        live_after_snapshot = tree_hash(cycle_root)
        if live_after_snapshot != before_tree_sha256:
            return _block_and_cleanup(
                receipt_path,
                txn_dir,
                "SOURCE_CHANGED_DURING_SNAPSHOT",
                str(cycle_root),
                {"snapshot": before_tree_sha256, "live": live_after_snapshot},
                transaction_id,
            )

        shutil.copytree(before_root, candidate_root, symlinks=True)
        for idx, item in enumerate(prepared):
            if item["noop"]:
                continue
            staged = stage_dir / f"{idx:04d}.candidate"
            shutil.copyfile(item["source"], staged)
            _fsync_file(staged)
            staged_hash = sha256_file(staged)
            if staged_hash != item["candidate_hash"]:
                return _block_and_cleanup(
                    receipt_path,
                    txn_dir,
                    "SOURCE_CHANGED_DURING_STAGING",
                    item["rel"],
                    {"expected": item["candidate_hash"], "staged": staged_hash},
                    transaction_id,
                )
            item["staged"] = staged
            candidate_target = resolve_inside(candidate_root, item["rel"])
            candidate_target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(staged, candidate_target)
            _fsync_file(candidate_target)

        candidate_validation = validate_cycle(candidate_root, post_mode, post_spec_id)
        if candidate_validation["status"] != "pass":
            return _block_and_cleanup(
                receipt_path,
                txn_dir,
                "CANDIDATE_VALIDATION_FAILED",
                str(candidate_root),
                candidate_validation,
                transaction_id,
            )

        candidate_transition = validate_transition(
            before_root,
            candidate_root,
            mode,
            allow_order_change=allow_order_change,
        )
        if candidate_transition["status"] != "pass":
            return _block_and_cleanup(
                receipt_path,
                txn_dir,
                "TRANSITION_VALIDATION_FAILED",
                str(candidate_root),
                candidate_transition,
                transaction_id,
            )

        candidate_tree_sha256 = tree_hash(candidate_root)
        live_before_commit = tree_hash(cycle_root)
        if live_before_commit != before_tree_sha256:
            return _block_and_cleanup(
                receipt_path,
                txn_dir,
                "SOURCE_CHANGED_BEFORE_COMMIT",
                str(cycle_root),
                {"snapshot": before_tree_sha256, "live": live_before_commit},
                transaction_id,
            )

        for idx, item in enumerate(prepared):
            if item["noop"]:
                continue
            current_hash = sha256_file(item["target"]) if item["target"].is_file() else None
            if current_hash != item["current_hash"]:
                return _block_and_cleanup(
                    receipt_path,
                    txn_dir,
                    "TARGET_CHANGED_BEFORE_COMMIT",
                    item["rel"],
                    {"snapshot": item["current_hash"], "live": current_hash},
                    transaction_id,
                )
            if item["target"].is_file():
                backup = backup_dir / f"{idx:04d}.backup"
                shutil.copyfile(item["target"], backup)
                _fsync_file(backup)
                if sha256_file(backup) != item["current_hash"]:
                    return _block_and_cleanup(
                        receipt_path,
                        txn_dir,
                        "BACKUP_HASH_MISMATCH",
                        item["rel"],
                        None,
                        transaction_id,
                    )
                item["backup"] = backup
            else:
                item["backup"] = None

        count = 0
        for item in prepared:
            if item["noop"]:
                continue
            parent = item["target"].parent
            missing_chain: list[Path] = []
            cur = parent
            while not cur.exists() and cur != cycle_root:
                missing_chain.append(cur)
                cur = cur.parent
            for directory in reversed(missing_chain):
                directory.mkdir()
                created_dirs.append(directory)
            os.replace(item["staged"], item["target"])
            _fsync_file(item["target"])
            committed.append(item)
            count += 1
            if fail_after is not None and count >= fail_after:
                raise RuntimeError("injected partial write failure")

        post_validation = validate_cycle(cycle_root, post_mode, post_spec_id)
        if post_validation["status"] != "pass":
            raise RuntimeError("postcondition validation failed: " + json.dumps(post_validation["diagnostics"], sort_keys=True))

        post_transition = validate_transition(
            before_root,
            cycle_root,
            mode,
            allow_order_change=allow_order_change,
        )
        if post_transition["status"] != "pass":
            raise RuntimeError("postcondition transition validation failed: " + json.dumps(post_transition["diagnostics"], sort_keys=True))

        final_tree_sha256 = tree_hash(cycle_root)
        if final_tree_sha256 != candidate_tree_sha256:
            raise RuntimeError(
                "committed tree does not match validated candidate: "
                f"candidate={candidate_tree_sha256} committed={final_tree_sha256}"
            )

        after = [{"path": x["rel"], "sha256": sha256_file(x["target"]), "noop": x["noop"]} for x in prepared]
        receipt = _receipt(
            "applied",
            "committed",
            transaction_id,
            cycle_root,
            prepared,
            after,
            post_validation,
            post_transition,
            before_tree_sha256=before_tree_sha256,
            candidate_tree_sha256=candidate_tree_sha256,
            after_tree_sha256=final_tree_sha256,
            candidate_validation=candidate_validation,
            candidate_transition_validation=candidate_transition,
        )
        atomic_write_json(receipt_path, receipt)
        shutil.rmtree(txn_dir)
        txn_dir = None
        return receipt

    except Exception as exc:
        if not committed:
            receipt = _failure(
                "PRECOMMIT_FAILURE",
                str(cycle_root),
                str(exc),
                transaction_id=transaction_id,
            )
            receipt["candidate_validation"] = candidate_validation
            receipt["candidate_transition_validation"] = candidate_transition
            receipt["before_tree_sha256"] = before_tree_sha256
            receipt["candidate_tree_sha256"] = candidate_tree_sha256
            if txn_dir:
                shutil.rmtree(txn_dir, ignore_errors=True)
                txn_dir = None
            atomic_write_json(receipt_path, receipt)
            return receipt

        rollback_errors: list[dict[str, str]] = []
        for item in reversed(committed):
            try:
                backup = item.get("backup")
                if backup and Path(backup).is_file():
                    shutil.copyfile(backup, item["target"])
                    _fsync_file(item["target"])
                elif item["target"].exists():
                    item["target"].unlink()
            except Exception as rb_exc:
                rollback_errors.append({"path": item["rel"], "error": str(rb_exc)})

        for item in committed:
            try:
                actual = sha256_file(item["target"]) if item["target"].is_file() else None
                if actual != item["current_hash"]:
                    rollback_errors.append(
                        {
                            "path": item["rel"],
                            "error": f"rollback verification mismatch expected={item['current_hash']} actual={actual}",
                        }
                    )
            except Exception as rb_exc:
                rollback_errors.append({"path": item["rel"], "error": f"rollback verification failed: {rb_exc}"})

        for directory in reversed(created_dirs):
            try:
                directory.rmdir()
            except OSError:
                pass

        recovery = str(txn_dir) if rollback_errors and txn_dir else None
        status = "failed_recovery_required" if rollback_errors else "failed_recovered"
        txid = transaction_id or "unassigned"
        receipt = _receipt(
            status,
            "rollback",
            txid,
            cycle_root,
            prepared,
            [],
            post_validation,
            post_transition,
            before_tree_sha256=before_tree_sha256,
            candidate_tree_sha256=candidate_tree_sha256,
            after_tree_sha256=tree_hash(cycle_root) if cycle_root.exists() else None,
            candidate_validation=candidate_validation,
            candidate_transition_validation=candidate_transition,
        )
        receipt["failure"] = str(exc)
        receipt["rollback_errors"] = rollback_errors
        receipt["recovery_path"] = recovery
        if txn_dir and not rollback_errors:
            shutil.rmtree(txn_dir, ignore_errors=True)
            txn_dir = None
        atomic_write_json(receipt_path, receipt)
        return receipt
    finally:
        _release_lock(lock_path)


def _receipt(
    status: str,
    stage: str,
    txid: str,
    root: Path,
    prepared: list[dict[str, Any]],
    after: list[dict[str, Any]],
    validation: dict | None,
    transition_validation: dict | None,
    *,
    before_tree_sha256: str | None,
    candidate_tree_sha256: str | None,
    after_tree_sha256: str | None,
    candidate_validation: dict | None,
    candidate_transition_validation: dict | None = None,
) -> dict:
    return {
        "receipt_version": 1,
        "status": status,
        "stage": stage,
        "transaction_id": txid,
        "cycle_root": str(root),
        "before_tree_sha256": before_tree_sha256,
        "candidate_tree_sha256": candidate_tree_sha256,
        "after_tree_sha256": after_tree_sha256,
        "writes": [
            {
                "path": x["rel"],
                "expected_before_sha256": x["expected"],
                "candidate_sha256": x["candidate_hash"],
                "before_sha256": x["current_hash"],
                "noop": x["noop"],
            }
            for x in prepared
        ],
        "after": after,
        "candidate_validation": candidate_validation,
        "candidate_transition_validation": candidate_transition_validation,
        "validation": validation,
        "transition_validation": transition_validation,
    }


def _failure(code: str, subject: str, evidence=None, *, transaction_id: str | None = None) -> dict:
    result = {
        "receipt_version": 1,
        "status": "blocked",
        "stage": "preflight",
        "code": code,
        "subject": subject,
        "evidence": evidence,
    }
    if transaction_id:
        result["transaction_id"] = transaction_id
    return result


def _persist_failure(
    receipt_path: Path,
    code: str,
    subject: str,
    evidence=None,
    *,
    transaction_id: str | None = None,
) -> dict:
    receipt = _failure(code, subject, evidence, transaction_id=transaction_id)
    atomic_write_json(receipt_path, receipt)
    return receipt


def _block_and_cleanup(
    receipt_path: Path,
    txn_dir: Path,
    code: str,
    subject: str,
    evidence,
    transaction_id: str,
) -> dict:
    receipt = _persist_failure(receipt_path, code, subject, evidence, transaction_id=transaction_id)
    shutil.rmtree(txn_dir, ignore_errors=True)
    return receipt


def _is_sha256(value: str) -> bool:
    return len(value) == 64 and all(ch in "0123456789abcdef" for ch in value)


def _samefile_if_exists(a: Path, b: Path) -> bool:
    try:
        return a.exists() and b.exists() and os.path.samefile(a, b)
    except OSError:
        return False


def _is_within(path: Path, root: Path) -> bool:
    try:
        return path == root or root in path.parents
    except RuntimeError:
        return False


def _symlink_issues(root: Path) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    for path in sorted(root.rglob("*")):
        if not path.is_symlink():
            continue
        rel = path.relative_to(root).as_posix()
        try:
            resolved = path.resolve(strict=False)
        except (OSError, RuntimeError) as exc:
            issues.append({"path": rel, "error": str(exc)})
            continue
        if not _is_within(resolved, root):
            issues.append({"path": rel, "resolved": str(resolved)})
    return issues


def _recovery_paths(cycle_root: Path, root_token: str) -> list[Path]:
    result: list[Path] = []
    for path in cycle_root.iterdir():
        if path.is_dir() and path.name.startswith(".swp-"):
            result.append(path)
    prefix = f".swp-txn-{root_token}-"
    for path in cycle_root.parent.iterdir():
        if path.is_dir() and path.name.startswith(prefix):
            result.append(path)
    return sorted(set(result), key=lambda p: str(p))


def _acquire_lock(lock_path: Path, cycle_root: Path) -> bool:
    try:
        lock_path.mkdir()
    except FileExistsError:
        return False
    try:
        atomic_write_json(
            lock_path / "owner.json",
            {
                "lock_version": 1,
                "cycle_root": str(cycle_root),
                "pid": os.getpid(),
            },
        )
    except Exception:
        shutil.rmtree(lock_path, ignore_errors=True)
        raise
    return True


def _release_lock(lock_path: Path) -> None:
    shutil.rmtree(lock_path, ignore_errors=True)


def _fsync_file(path: Path) -> None:
    with path.open("rb") as f:
        os.fsync(f.fileno())


def main() -> int:
    ap = argparse.ArgumentParser(description="Apply a hash-guarded recovery-aware sequential work transaction.")
    ap.add_argument("--plan", required=True)
    ap.add_argument("--receipt", required=True)
    ap.add_argument("--fail-after", type=int, help=argparse.SUPPRESS)
    args = ap.parse_args()
    receipt = apply(Path(args.plan), Path(args.receipt), args.fail_after)
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if receipt.get("status") in {"applied", "no_change"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
