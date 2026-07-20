#!/usr/bin/env python3
"""Validate MAGIA run-state files and optionally verify source drift."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

PROFILES = {"quick", "standard", "governed"}
MODES = {"adhoc", "ralph", "adapt", "bug_fix", "refactor", "documentation"}
STATUSES = {"pending", "in_progress", "paused", "cancelled", "blocked", "failed", "completed", "rolled_back", "handoff"}
CHECKPOINTS = {"inspect", "execute", "validate", "converge", "close"}
RESULTS = {"pass", "fail", "not_run"}
VALIDATION = {"pass", "fail", "not_run", "partial"}
CONVERGENCE = {"satisfied", "partially_satisfied", "unsatisfied", "obsolete", "unverified", "out_of_scope", "planning_change_required"}
HANDOFFS = {"none", "mago", "nomia", "both"}
ATOMICITY = {"single_repository", "not_guaranteed"}
REPO_STATUSES = STATUSES | {"compatible", "deployed"}
ROLLBACK_STATUSES = {"not_required", "planned", "succeeded", "failed", "partial"}
REQUIRED = {
    "schema_version", "run_id", "profile", "mode", "status", "checkpoint", "pending_step", "scope",
    "inspected_files", "planned_writes", "completed_writes", "commands", "validation_status",
    "convergence_status", "retry", "cancellation", "rollback_evidence", "handoff", "atomicity", "repositories",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_repo_path(root: Path, raw: str) -> Path | None:
    candidate = Path(raw)
    if candidate.is_absolute() or ".." in candidate.parts:
        return None
    resolved = (root / candidate).resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError:
        return None
    return resolved


def require_mapping(value: Any, name: str, errors: list[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(f"{name} must be an object")
        return {}
    return value


def require_list(value: Any, name: str, errors: list[str]) -> list[Any]:
    if not isinstance(value, list):
        errors.append(f"{name} must be an array")
        return []
    return value


def validate_state(data: Any, repo_root: Path | None = None, verify_drift: bool = False) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["run-state root must be an object"]
    missing = REQUIRED - set(data)
    if missing:
        errors.append(f"missing required fields: {sorted(missing)}")
    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if not isinstance(data.get("run_id"), str) or not data.get("run_id", "").strip():
        errors.append("run_id must be a non-empty string")
    if data.get("profile") not in PROFILES:
        errors.append(f"profile must be one of {sorted(PROFILES)}")
    if data.get("mode") not in MODES:
        errors.append(f"mode must be one of {sorted(MODES)}")
    if data.get("status") not in STATUSES:
        errors.append(f"status must be one of {sorted(STATUSES)}")
    if data.get("checkpoint") not in CHECKPOINTS:
        errors.append(f"checkpoint must be one of {sorted(CHECKPOINTS)}")
    if data.get("validation_status") not in VALIDATION:
        errors.append(f"validation_status must be one of {sorted(VALIDATION)}")
    if data.get("convergence_status") not in CONVERGENCE:
        errors.append(f"convergence_status must be one of {sorted(CONVERGENCE)}")
    if data.get("atomicity") not in ATOMICITY:
        errors.append(f"atomicity must be one of {sorted(ATOMICITY)}")

    require_mapping(data.get("scope"), "scope", errors)
    inspected = require_list(data.get("inspected_files"), "inspected_files", errors)
    planned = require_list(data.get("planned_writes"), "planned_writes", errors)
    completed = require_list(data.get("completed_writes"), "completed_writes", errors)
    commands = require_list(data.get("commands"), "commands", errors)
    require_list(data.get("rollback_evidence"), "rollback_evidence", errors)
    repositories = require_list(data.get("repositories"), "repositories", errors)

    for name, values in (("planned_writes", planned), ("completed_writes", completed)):
        for index, value in enumerate(values):
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{name}[{index}] must be a non-empty repository-relative path")
            elif Path(value).is_absolute() or ".." in Path(value).parts:
                errors.append(f"{name}[{index}] must stay inside the selected repository")

    for index, command in enumerate(commands):
        if not isinstance(command, dict):
            errors.append(f"commands[{index}] must be an object")
            continue
        if not isinstance(command.get("command"), str) or not command.get("command", "").strip():
            errors.append(f"commands[{index}].command must be non-empty")
        if command.get("status") not in RESULTS:
            errors.append(f"commands[{index}].status must be one of {sorted(RESULTS)}")

    retry = require_mapping(data.get("retry"), "retry", errors)
    count, maximum = retry.get("count"), retry.get("max")
    if not isinstance(count, int) or count < 0:
        errors.append("retry.count must be a non-negative integer")
    if not isinstance(maximum, int) or maximum < 0:
        errors.append("retry.max must be a non-negative integer")
    if isinstance(count, int) and isinstance(maximum, int) and count > maximum:
        errors.append("retry.count must not exceed retry.max")

    cancellation = require_mapping(data.get("cancellation"), "cancellation", errors)
    if not isinstance(cancellation.get("requested"), bool):
        errors.append("cancellation.requested must be boolean")

    handoff = require_mapping(data.get("handoff"), "handoff", errors)
    if handoff.get("target") not in HANDOFFS:
        errors.append(f"handoff.target must be one of {sorted(HANDOFFS)}")

    seen_repo_ids: set[str] = set()
    for index, repo in enumerate(repositories):
        if not isinstance(repo, dict):
            errors.append(f"repositories[{index}] must be an object")
            continue
        rid = repo.get("id")
        if not isinstance(rid, str) or not rid.strip():
            errors.append(f"repositories[{index}].id must be non-empty")
        elif rid in seen_repo_ids:
            errors.append(f"duplicate repository id: {rid}")
        else:
            seen_repo_ids.add(rid)
        if not isinstance(repo.get("dependency_order"), int) or repo.get("dependency_order", -1) < 0:
            errors.append(f"repositories[{index}].dependency_order must be a non-negative integer")
        if repo.get("status") not in REPO_STATUSES:
            errors.append(f"repositories[{index}].status is invalid")
        if repo.get("checkpoint") not in CHECKPOINTS:
            errors.append(f"repositories[{index}].checkpoint is invalid")
        if repo.get("rollback_status") not in ROLLBACK_STATUSES:
            errors.append(f"repositories[{index}].rollback_status is invalid")
    if len(repositories) > 1 and data.get("atomicity") != "not_guaranteed":
        errors.append("multi-repository runs must set atomicity to not_guaranteed")

    if data.get("status") == "completed":
        if data.get("checkpoint") != "close":
            errors.append("completed run must be at close checkpoint")
        if data.get("pending_step") is not None:
            errors.append("completed run must have pending_step null")
        if data.get("validation_status") != "pass":
            errors.append("completed run requires validation_status pass")
        if data.get("convergence_status") != "satisfied":
            errors.append("completed run requires convergence_status satisfied")
        if cancellation.get("requested") is True:
            errors.append("cancelled request cannot be marked completed")
        if any(isinstance(repo, dict) and repo.get("status") in {"failed", "blocked", "cancelled"} for repo in repositories):
            errors.append("completed run cannot contain failed, blocked, or cancelled repositories")

    if verify_drift:
        if repo_root is None:
            errors.append("--verify-drift requires --repo-root")
        else:
            for index, item in enumerate(inspected):
                if not isinstance(item, dict):
                    errors.append(f"inspected_files[{index}] must be an object")
                    continue
                raw_path, expected = item.get("path"), item.get("sha256")
                if not isinstance(raw_path, str) or not isinstance(expected, str):
                    errors.append(f"inspected_files[{index}] requires path and sha256 strings")
                    continue
                resolved = safe_repo_path(repo_root, raw_path)
                if resolved is None:
                    errors.append(f"inspected_files[{index}] path escapes repository: {raw_path}")
                elif not resolved.is_file():
                    errors.append(f"repository_drift: inspected file missing: {raw_path}")
                elif sha256_file(resolved) != expected:
                    errors.append(f"repository_drift: fingerprint changed: {raw_path}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a MAGIA machine-readable run-state file.")
    parser.add_argument("--state", required=True, help="Run-state JSON path.")
    parser.add_argument("--repo-root", help="Repository root used for drift verification.")
    parser.add_argument("--verify-drift", action="store_true", help="Re-hash inspected files and stop on drift.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable result.")
    args = parser.parse_args(argv)
    try:
        data = json.loads(Path(args.state).read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        result = {"status": "fail", "errors": [f"cannot read run-state: {exc}"]}
    else:
        errors = validate_state(data, Path(args.repo_root) if args.repo_root else None, args.verify_drift)
        result = {"status": "pass" if not errors else "fail", "errors": errors}
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"status: {result['status']}")
        for error in result["errors"]:
            print(f"error: {error}")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
