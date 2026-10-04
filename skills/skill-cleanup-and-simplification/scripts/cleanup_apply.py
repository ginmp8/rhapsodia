#!/usr/bin/env python3
"""Apply an evidence-backed cleanup plan with dry-run, validation, rollback, and durable receipts."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path, PurePosixPath
from typing import Any

sys.dont_write_bytecode = True

REMOVABLE = {"generated", "duplicate", "obsolete"}
FAIL_CLOSED = {"used", "integrable", "blocked", "unknown"}
OBSOLETE_EVIDENCE = {"user-explicit", "target-doc", "replacement-verified", "validator-proven", "migration-complete"}
GENERATED_EVIDENCE = {"user-explicit-generated", "target-doc", "generator-command", "manifest-generated", "reproducible-generated"}
CHECKPOINT_PATTERN = __import__("re").compile(r"^[A-Za-z0-9._-]{1,64}$")
MAX_VALIDATION_OUTPUT = 6000


def _load_inventory_builder():
    module_path = Path(__file__).with_name("cleanup_inventory.py")
    spec = importlib.util.spec_from_file_location("cleanup_inventory_local", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load sibling cleanup_inventory.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build_inventory


build_inventory = _load_inventory_builder()


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
    return path.parent.resolve(strict=False) / path.name


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
    path = PurePosixPath(raw)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise Rejected("preflight/noncanonical-path", raw, {"reason": "absolute, dot, and parent segments are forbidden"})
    if path.as_posix() != raw:
        raise Rejected("preflight/noncanonical-path", raw, {"canonical": path.as_posix()})
    return path


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
    out: set[str] = set()
    for item in action.get("evidence", []):
        if isinstance(item, dict) and item.get("kind") and item.get("value"):
            out.add(str(item["kind"]))
    return out


def normalize_roots(data: dict[str, Any]) -> list[dict[str, str]]:
    roots = data.get("roots", [])
    if roots is None:
        return []
    if not isinstance(roots, list):
        raise Rejected("plan/roots-schema", "roots", {"reason": "roots must be a list"})
    result: list[dict[str, str]] = []
    for index, item in enumerate(roots):
        if not isinstance(item, dict) or not item.get("kind") or not item.get("path"):
            raise Rejected("plan/roots-schema", f"roots[{index}]", {"reason": "each root requires kind and path"})
        rel = parse_relative(str(item["path"]))
        result.append({"kind": str(item["kind"]), "path": rel.as_posix()})
    return result


def normalize_validation_commands(data: dict[str, Any]) -> list[dict[str, Any]]:
    commands = data.get("validation_commands", [])
    if commands is None:
        return []
    if not isinstance(commands, list):
        raise Rejected("plan/validation-schema", "validation_commands", {"reason": "must be a list"})
    result: list[dict[str, Any]] = []
    for index, item in enumerate(commands):
        if not isinstance(item, dict):
            raise Rejected("plan/validation-schema", f"validation_commands[{index}]", {"reason": "must be an object"})
        if item.get("approved") is not True:
            raise Rejected("plan/validation-not-approved", f"validation_commands[{index}]", {})
        argv = item.get("argv")
        if not isinstance(argv, list) or not argv or not all(isinstance(part, str) and part for part in argv):
            raise Rejected("plan/validation-schema", f"validation_commands[{index}].argv", {"reason": "argv must be a non-empty string array"})
        timeout = item.get("timeout_seconds", 120)
        if not isinstance(timeout, int) or not 1 <= timeout <= 600:
            raise Rejected("plan/validation-schema", f"validation_commands[{index}].timeout_seconds", {"reason": "must be an integer from 1 to 600"})
        result.append({"name": str(item.get("name") or f"validation-{index + 1}"), "argv": argv, "timeout_seconds": timeout})
    return result


def inventory_map(target: Path, roots: list[dict[str, str]]) -> dict[str, dict[str, Any]]:
    try:
        inventory = build_inventory(target, extra_roots=roots)
    except ValueError as exc:
        raise Rejected("plan/root-invalid", "roots", {"error": str(exc)}) from exc
    return {item["path"]: item for item in inventory["entries"]}


def preflight_action(target: Path, action: dict[str, Any], current: dict[str, dict[str, Any]]) -> dict[str, Any]:
    if action.get("action") != "delete":
        raise Rejected("plan/unsupported-action", str(action.get("path", "<unknown>")), {"action": action.get("action")})
    rel = parse_relative(str(action.get("path", "")))
    path = candidate_path(target, rel)
    classification = action.get("classification")
    if classification not in REMOVABLE:
        raise Rejected("plan/nonremovable-classification", rel.as_posix(), {"classification": classification})
    checkpoint = str(action.get("checkpoint", "default"))
    if not CHECKPOINT_PATTERN.fullmatch(checkpoint):
        raise Rejected("plan/checkpoint-invalid", rel.as_posix(), {"checkpoint": checkpoint})
    kinds = evidence_kinds(action)
    if not kinds:
        raise Rejected("plan/missing-evidence", rel.as_posix(), {})

    item = current.get(rel.as_posix())
    if item is None:
        return {
            "path": rel.as_posix(),
            "classification": classification,
            "checkpoint": checkpoint,
            "path_obj": path,
            "exists": False,
            "result": "already_absent",
            "evidence": action.get("evidence", []),
            "expected_sha256": action.get("expected_sha256"),
        }

    actual = item["status"]
    override_allowed = False
    if classification == "obsolete" and action.get("approval") == "explicit" and kinds & OBSOLETE_EVIDENCE and actual in {"integrable", "unknown"}:
        override_allowed = True
    if classification == "generated" and action.get("approval") == "explicit" and kinds & GENERATED_EVIDENCE and actual in {"integrable", "unknown"}:
        override_allowed = True

    if actual in FAIL_CLOSED:
        if not override_allowed:
            raise Rejected("plan/fail-closed-state", rel.as_posix(), {"inventory_status": actual, "requested": classification})
    elif classification != actual:
        raise Rejected("plan/classification-mismatch", rel.as_posix(), {"inventory_status": actual, "requested": classification})

    if classification == "obsolete" and not (action.get("approval") == "explicit" and kinds & OBSOLETE_EVIDENCE):
        raise Rejected("plan/obsolete-needs-explicit-evidence", rel.as_posix(), {"evidence_kinds": sorted(kinds)})
    if classification == "generated" and actual != "generated" and not (action.get("approval") == "explicit" and kinds & GENERATED_EVIDENCE):
        raise Rejected("plan/generated-needs-corroboration", rel.as_posix(), {"inventory_status": actual, "evidence_kinds": sorted(kinds)})

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
        "checkpoint": checkpoint,
        "path_obj": path,
        "exists": True,
        "result": "planned",
        "evidence": action.get("evidence", []),
        "expected_sha256": expected,
    }


def restore_actions(target: Path, lkg: Path, changed: list[dict[str, Any]]) -> tuple[bool, list[dict[str, str]]]:
    recovery: list[dict[str, str]] = []
    ok = True
    for item in reversed(changed):
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


def clip(text: str) -> str:
    if len(text) <= MAX_VALIDATION_OUTPUT:
        return text
    return text[:MAX_VALIDATION_OUTPUT] + "\n...[truncated]"


def run_external_validations(target: Path, commands: list[dict[str, Any]]) -> tuple[bool, list[dict[str, Any]]]:
    results: list[dict[str, Any]] = []
    all_ok = True
    for command in commands:
        try:
            cp = subprocess.run(
                command["argv"],
                cwd=target,
                text=True,
                capture_output=True,
                timeout=command["timeout_seconds"],
                shell=False,
            )
            status = "pass" if cp.returncode == 0 else "fail"
            all_ok = all_ok and cp.returncode == 0
            results.append(
                {
                    "name": command["name"],
                    "argv": command["argv"],
                    "status": status,
                    "exit_code": cp.returncode,
                    "stdout": clip(cp.stdout),
                    "stderr": clip(cp.stderr),
                }
            )
        except subprocess.TimeoutExpired as exc:
            all_ok = False
            results.append(
                {
                    "name": command["name"],
                    "argv": command["argv"],
                    "status": "fail",
                    "exit_code": None,
                    "stdout": clip(exc.stdout or ""),
                    "stderr": clip(exc.stderr or ""),
                    "error": "timeout",
                }
            )
        except OSError as exc:
            all_ok = False
            results.append(
                {
                    "name": command["name"],
                    "argv": command["argv"],
                    "status": "fail",
                    "exit_code": None,
                    "stdout": "",
                    "stderr": "",
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )
    return all_ok, results


def grouped_actions(actions: list[dict[str, Any]]) -> list[tuple[str, list[dict[str, Any]]]]:
    order: list[str] = []
    groups: dict[str, list[dict[str, Any]]] = {}
    for action in actions:
        checkpoint = action["checkpoint"]
        if checkpoint not in groups:
            groups[checkpoint] = []
            order.append(checkpoint)
        groups[checkpoint].append(action)
    return [(name, groups[name]) for name in order]


def sanitized_actions(actions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{key: value for key, value in action.items() if key != "path_obj"} for action in actions]


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
        "receipt_version": 2,
        "status": "rejected",
        "stage": "preflight",
        "target": str(target),
        "plan": str(plan_path),
        "mode": "apply" if args.apply else "dry-run",
        "started_unix": started,
        "actions": [],
        "checks": [],
        "checkpoints": [],
        "validations": [],
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
        if data.get("plan_version") not in {1, 2} or not isinstance(data.get("actions"), list):
            raise Rejected("plan/schema", str(plan_path), {"plan_version": data.get("plan_version")})
        roots = normalize_roots(data)
        validation_commands = normalize_validation_commands(data)
        current = inventory_map(target, roots)
        actions = [preflight_action(target, action, current) for action in data["actions"]]
        paths = [action["path"] for action in actions]
        if len(paths) != len(set(paths)):
            raise Rejected("plan/duplicate-path", "actions", {"paths": paths})

        base_receipt["hashes"]["before_tree_sha256"] = tree_hash(target)
        base_receipt["actions"] = sanitized_actions(actions)
        base_receipt["checks"].append(
            {
                "code": "preflight/pass",
                "status": "pass",
                "subject": str(target),
                "evidence": {"action_count": len(actions), "root_count": len(roots), "validation_command_count": len(validation_commands)},
            }
        )

        if not args.apply:
            base_receipt["status"] = "dry-run"
            atomic_write_json(receipt, base_receipt)
            return 0

        actionable = [action for action in actions if action["exists"]]
        work_dir.mkdir(parents=True, exist_ok=True)
        if not actionable:
            validation_out = work_dir / "idempotent-validation.json"
            rc, validation, output = run_validator(target, validation_out)
            external_ok, external_results = run_external_validations(target, validation_commands)
            base_receipt["validations"] = external_results
            if rc != 0 or not external_ok:
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
            for checkpoint, group in grouped_actions(actionable):
                group_changed: list[str] = []
                for item in group:
                    remove_path(item["path_obj"])
                    item["result"] = "removed"
                    changed.append(item)
                    group_changed.append(item["path"])
                checkpoint_validation = tx / f"checkpoint-{checkpoint}-validation.json"
                rc, validation, output = run_validator(target, checkpoint_validation)
                base_receipt["checkpoints"].append(
                    {
                        "name": checkpoint,
                        "changed": group_changed,
                        "status": "pass" if rc == 0 else "fail",
                        "validator_report": validation,
                        "validator_output": output,
                    }
                )
                if rc != 0:
                    raise RuntimeError(f"checkpoint validation failed: {checkpoint}")
        except Exception as exc:
            ok, recovery_items = restore_actions(target, lkg, changed)
            base_receipt["actions"] = sanitized_actions(actions)
            base_receipt["recovery"]["items"] = recovery_items
            base_receipt["status"] = "rolled-back" if ok else "recovery-required"
            base_receipt["stage"] = "rollback"
            base_receipt["checks"].append({"code": "commit/failure", "status": "fail", "subject": str(target), "evidence": {"error": f"{type(exc).__name__}: {exc}"}})
            base_receipt["hashes"]["after_rollback_tree_sha256"] = tree_hash(target)
            atomic_write_json(receipt, base_receipt)
            return 1

        validation_out = tx / "post-cleanup-validation.json"
        rc, validation, output = run_validator(target, validation_out)
        external_ok, external_results = run_external_validations(target, validation_commands)
        base_receipt["validations"] = external_results
        if rc != 0 or not external_ok:
            ok, recovery_items = restore_actions(target, lkg, changed)
            base_receipt["actions"] = sanitized_actions(actions)
            base_receipt["recovery"]["items"] = recovery_items
            base_receipt["status"] = "rolled-back" if ok else "recovery-required"
            base_receipt["stage"] = "rollback"
            base_receipt["checks"].append(
                {
                    "code": "validation/fail",
                    "status": "fail",
                    "subject": str(target),
                    "evidence": {"output": output, "report": validation, "external": external_results},
                }
            )
            base_receipt["hashes"]["after_rollback_tree_sha256"] = tree_hash(target)
            atomic_write_json(receipt, base_receipt)
            return 1

        base_receipt["actions"] = sanitized_actions(actions)
        base_receipt["status"] = "pass"
        base_receipt["stage"] = "commit"
        base_receipt["checks"].append({"code": "validation/pass", "status": "pass", "subject": str(target), "evidence": {"report": validation, "external": external_results}})
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
