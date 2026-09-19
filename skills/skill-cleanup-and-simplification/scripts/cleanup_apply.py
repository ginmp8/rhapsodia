#!/usr/bin/env python3
"""Apply an evidence-backed cleanup plan with dry-run, identity checks, rollback, and durable receipts."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
sys.dont_write_bytecode = True
import time
from pathlib import Path, PurePosixPath
from typing import Any

from cleanup_inventory import build_inventory

REMOVABLE = {"generated", "duplicate", "obsolete"}
FAIL_CLOSED = {"used", "integrable", "blocked", "unknown"}
OBSOLETE_EVIDENCE = {"user-explicit", "target-doc", "replacement-verified", "validator-proven", "migration-complete"}


class Rejected(Exception):
    def __init__(self, code: str, subject: str, evidence: dict[str, Any]):
        super().__init__(code)
        self.code = code
        self.subject = subject
        self.evidence = evidence


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def tree_hash(root: Path) -> str:
    h = hashlib.sha256()
    for path in sorted(root.rglob("*"), key=lambda p: p.relative_to(root).as_posix()):
        if path.is_symlink():
            data = ("symlink:" + os.readlink(path)).encode("utf-8", errors="surrogateescape")
        elif path.is_file():
            data = path.read_bytes()
        else:
            continue
        h.update(path.relative_to(root).as_posix().encode("utf-8") + b"\0" + data + b"\0")
    return h.hexdigest()


def canonical_output(path: Path) -> Path:
    parent = path.parent.resolve(strict=False)
    return parent / path.name


def within(path: Path, root: Path) -> bool:
    return path == root or root in path.parents


def assert_external_output(path: Path, target: Path, label: str) -> Path:
    canonical = canonical_output(path)
    if within(canonical, target):
        raise Rejected("preflight/output-inside-target", label, {"path": str(canonical)})
    return canonical


def parse_relative(raw: str) -> PurePosixPath:
    if not raw or "\\" in raw:
        raise Rejected("preflight/noncanonical-path", raw or "<empty>", {"reason": "use non-empty forward-slash relative path"})
    p = PurePosixPath(raw)
    if p.is_absolute() or any(part in {"", ".", ".."} for part in p.parts):
        raise Rejected("preflight/noncanonical-path", raw, {"reason": "absolute, dot, and parent segments are forbidden"})
    canonical = p.as_posix()
    if canonical != raw:
        raise Rejected("preflight/noncanonical-path", raw, {"canonical": canonical})
    return p


def candidate_path(target: Path, rel: PurePosixPath) -> Path:
    current = target
    for part in rel.parts:
        current = current / part
        if current.is_symlink():
            raise Rejected("preflight/symlink", rel.as_posix(), {"component": str(current)})
    resolved = current.resolve(strict=False)
    if not within(resolved, target):
        raise Rejected("preflight/path-escape", rel.as_posix(), {"resolved": str(resolved)})
    return current


def atomic_write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        fh.write(json.dumps(data, indent=2, sort_keys=True) + "\n")
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)


def copy_path(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.is_symlink():
        raise Rejected("recovery/symlink", str(src), {})
    if src.is_dir():
        shutil.copytree(src, dst, symlinks=True)
    else:
        shutil.copy2(src, dst)


def remove_path(path: Path) -> None:
    if path.is_symlink():
        raise Rejected("commit/symlink", str(path), {})
    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()


def evidence_kinds(action: dict[str, Any]) -> set[str]:
    out = set()
    for item in action.get("evidence", []):
        if isinstance(item, dict) and item.get("kind") and item.get("value"):
            out.add(str(item["kind"]))
    return out


def inventory_map(target: Path) -> dict[str, dict[str, Any]]:
    return {item["path"]: item for item in build_inventory(target)["entries"]}


def preflight_action(target: Path, action: dict[str, Any], current: dict[str, dict[str, Any]]) -> dict[str, Any]:
    if action.get("action") != "delete":
        raise Rejected("plan/unsupported-action", str(action.get("path", "<unknown>")), {"action": action.get("action")})
    rel = parse_relative(str(action.get("path", "")))
    path = candidate_path(target, rel)
    classification = action.get("classification")
    if classification not in REMOVABLE:
        raise Rejected("plan/nonremovable-classification", rel.as_posix(), {"classification": classification})
    kinds = evidence_kinds(action)
    if not kinds:
        raise Rejected("plan/missing-evidence", rel.as_posix(), {})

    item = current.get(rel.as_posix())
    if item is None:
        return {
            "path": rel.as_posix(),
            "classification": classification,
            "path_obj": path,
            "exists": False,
            "result": "already_absent",
            "evidence": action.get("evidence", []),
            "expected_sha256": action.get("expected_sha256"),
        }

    actual = item["status"]
    if actual in FAIL_CLOSED:
        if not (classification == "obsolete" and action.get("approval") == "explicit" and kinds & OBSOLETE_EVIDENCE and actual in {"integrable", "unknown"}):
            raise Rejected("plan/fail-closed-state", rel.as_posix(), {"inventory_status": actual, "requested": classification})
    elif classification != actual:
        raise Rejected("plan/classification-mismatch", rel.as_posix(), {"inventory_status": actual, "requested": classification})

    if classification == "obsolete" and not (action.get("approval") == "explicit" and kinds & OBSOLETE_EVIDENCE):
        raise Rejected("plan/obsolete-needs-explicit-evidence", rel.as_posix(), {"evidence_kinds": sorted(kinds)})

    expected = action.get("expected_sha256")
    if path.is_file():
        if not expected:
            raise Rejected("plan/missing-expected-hash", rel.as_posix(), {})
        actual_hash = sha256_file(path)
        if expected != actual_hash:
            raise Rejected("plan/hash-mismatch", rel.as_posix(), {"expected": expected, "actual": actual_hash})
    elif path.is_dir():
        if classification != "generated":
            raise Rejected("plan/directory-delete-restricted", rel.as_posix(), {"classification": classification})
    else:
        raise Rejected("plan/unsupported-path-type", rel.as_posix(), {})

    return {
        "path": rel.as_posix(),
        "classification": classification,
        "path_obj": path,
        "exists": True,
        "result": "planned",
        "evidence": action.get("evidence", []),
        "expected_sha256": expected,
    }


def restore_actions(target: Path, lkg: Path, changed: list[dict[str, Any]]) -> tuple[bool, list[dict[str, str]]]:
    recovery: list[dict[str, str]] = []
    ok = True
    for item in changed:
        rel = Path(item["path"])
        src = lkg / rel
        dst = target / rel
        try:
            if dst.exists() or dst.is_symlink():
                recovery.append({"path": item["path"], "status": "blocked", "reason": "destination recreated before rollback"})
                ok = False
                continue
            copy_path(src, dst)
            recovery.append({"path": item["path"], "status": "restored"})
        except Exception as exc:
            recovery.append({"path": item["path"], "status": "failed", "reason": f"{type(exc).__name__}: {exc}"})
            ok = False
    return ok, recovery


def run_validator(target: Path, output: Path) -> tuple[int, dict[str, Any] | None, str]:
    validator = Path(__file__).with_name("validate_cleanup_package.py")
    cp = subprocess.run([sys.executable, "-S", str(validator), "--target", str(target), "--output", str(output)], text=True, capture_output=True)
    data = None
    if output.exists():
        try:
            data = json.loads(output.read_text(encoding="utf-8"))
        except Exception:
            data = None
    return cp.returncode, data, (cp.stdout + cp.stderr).strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply a conservative cleanup plan. Default is dry-run.")
    parser.add_argument("--target", required=True)
    parser.add_argument("--plan", required=True)
    parser.add_argument("--work-dir", required=True, help="External recovery/work directory.")
    parser.add_argument("--receipt", required=True, help="External machine-readable receipt path.")
    parser.add_argument("--apply", action="store_true", help="Perform mutation after preflight. Without this flag the command is dry-run only.")
    args = parser.parse_args()

    target = Path(args.target).resolve(strict=True)
    plan_path = Path(args.plan).resolve(strict=True)
    work_dir = Path(args.work_dir).resolve(strict=False)
    receipt = Path(args.receipt).resolve(strict=False)
    started = int(time.time())

    base_receipt: dict[str, Any] = {
        "receipt_version": 1,
        "status": "rejected",
        "stage": "preflight",
        "target": str(target),
        "plan": str(plan_path),
        "mode": "apply" if args.apply else "dry-run",
        "started_unix": started,
        "actions": [],
        "checks": [],
        "hashes": {},
        "recovery": {},
    }

    try:
        if not target.is_dir():
            raise Rejected("preflight/target-not-directory", str(target), {})
        receipt = assert_external_output(receipt, target, "receipt")
        work_dir = assert_external_output(work_dir, target, "work-dir")
        if canonical_output(receipt) == canonical_output(plan_path):
            raise Rejected("preflight/receipt-plan-alias", str(receipt), {})
        if within(plan_path, target) and plan_path.is_symlink():
            raise Rejected("preflight/plan-symlink", str(plan_path), {})
        data = json.loads(plan_path.read_text(encoding="utf-8"))
        if data.get("plan_version") != 1 or not isinstance(data.get("actions"), list):
            raise Rejected("plan/schema", str(plan_path), {"plan_version": data.get("plan_version")})
        current = inventory_map(target)
        actions = [preflight_action(target, action, current) for action in data["actions"]]
        paths = [a["path"] for a in actions]
        if len(paths) != len(set(paths)):
            raise Rejected("plan/duplicate-path", "actions", {"paths": paths})
        base_receipt["hashes"]["before_tree_sha256"] = tree_hash(target)
        base_receipt["actions"] = [{k: v for k, v in a.items() if k != "path_obj"} for a in actions]
        base_receipt["checks"].append({"code": "preflight/pass", "status": "pass", "subject": str(target), "evidence": {"action_count": len(actions)}})

        if not args.apply:
            base_receipt["status"] = "dry-run"
            base_receipt["stage"] = "preflight"
            atomic_write_json(receipt, base_receipt)
            return 0

        actionable = [a for a in actions if a["exists"]]
        if not actionable:
            validation_out = work_dir / "idempotent-validation.json"
            work_dir.mkdir(parents=True, exist_ok=True)
            rc, validation, output = run_validator(target, validation_out)
            if rc != 0:
                base_receipt["status"] = "fail"
                base_receipt["stage"] = "validation"
                base_receipt["checks"].append({"code": "validation/fail", "status": "fail", "subject": str(target), "evidence": {"output": output, "report": validation}})
                atomic_write_json(receipt, base_receipt)
                return 1
            base_receipt["status"] = "pass"
            base_receipt["stage"] = "commit"
            base_receipt["hashes"]["after_tree_sha256"] = tree_hash(target)
            atomic_write_json(receipt, base_receipt)
            return 0

        tx = work_dir / ("cleanup-" + base_receipt["hashes"]["before_tree_sha256"][:16])
        lkg = tx / "last-known-good"
        tx.mkdir(parents=True, exist_ok=True)
        if lkg.exists():
            shutil.rmtree(lkg)
        lkg.mkdir(parents=True)
        for item in actionable:
            copy_path(item["path_obj"], lkg / item["path"])
        base_receipt["recovery"]["last_known_good"] = str(lkg)

        changed: list[dict[str, Any]] = []
        try:
            for item in actionable:
                remove_path(item["path_obj"])
                item["result"] = "removed"
                changed.append(item)
        except Exception as exc:
            ok, recovery_items = restore_actions(target, lkg, changed)
            base_receipt["actions"] = [{k: v for k, v in a.items() if k != "path_obj"} for a in actions]
            base_receipt["recovery"]["items"] = recovery_items
            base_receipt["status"] = "rolled-back" if ok else "recovery-required"
            base_receipt["stage"] = "rollback"
            base_receipt["checks"].append({"code": "commit/failure", "status": "fail", "subject": str(target), "evidence": {"error": f"{type(exc).__name__}: {exc}"}})
            atomic_write_json(receipt, base_receipt)
            return 1

        validation_out = tx / "post-cleanup-validation.json"
        rc, validation, output = run_validator(target, validation_out)
        if rc != 0:
            ok, recovery_items = restore_actions(target, lkg, changed)
            base_receipt["actions"] = [{k: v for k, v in a.items() if k != "path_obj"} for a in actions]
            base_receipt["recovery"]["items"] = recovery_items
            base_receipt["status"] = "rolled-back" if ok else "recovery-required"
            base_receipt["stage"] = "rollback"
            base_receipt["checks"].append({"code": "validation/fail", "status": "fail", "subject": str(target), "evidence": {"output": output, "report": validation}})
            base_receipt["hashes"]["after_rollback_tree_sha256"] = tree_hash(target)
            atomic_write_json(receipt, base_receipt)
            return 1

        base_receipt["actions"] = [{k: v for k, v in a.items() if k != "path_obj"} for a in actions]
        base_receipt["status"] = "pass"
        base_receipt["stage"] = "commit"
        base_receipt["checks"].append({"code": "validation/pass", "status": "pass", "subject": str(target), "evidence": {"report": validation}})
        base_receipt["hashes"]["after_tree_sha256"] = tree_hash(target)
        atomic_write_json(receipt, base_receipt)
        return 0

    except Rejected as exc:
        base_receipt["checks"].append({"code": exc.code, "status": "fail", "subject": exc.subject, "evidence": exc.evidence})
        try:
            receipt = assert_external_output(Path(args.receipt).resolve(strict=False), target, "receipt")
            atomic_write_json(receipt, base_receipt)
        except Exception:
            pass
        return 2
    except Exception as exc:
        base_receipt["status"] = "fail"
        base_receipt["stage"] = "error"
        base_receipt["checks"].append({"code": "runtime/unexpected", "status": "fail", "subject": str(target), "evidence": {"error": f"{type(exc).__name__}: {exc}"}})
        try:
            atomic_write_json(receipt, base_receipt)
        except Exception:
            pass
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
