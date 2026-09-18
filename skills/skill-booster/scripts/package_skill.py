#!/usr/bin/env python3
"""Validate and package a skill as a deterministic, recovery-aware skill.zip."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import secrets
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

BLOCKED_PARTS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "build",
    "dist",
    "reports",
    "generated_evidence",
    "generated-evidence",
    "benchmark-results",
    "validation-reports",
}
BLOCKED_SUFFIXES = {".pyc", ".pyo"}
BLOCKED_FILENAMES = {"skill.zip"}


def should_exclude(path: Path) -> bool:
    return bool(set(path.parts) & BLOCKED_PARTS or path.name in BLOCKED_FILENAMES or path.suffix in BLOCKED_SUFFIXES)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_future_path(path: Path) -> Path:
    try:
        return path.expanduser().resolve(strict=False)
    except RuntimeError as exc:
        raise ValueError(f"path contains a symbolic-link cycle: {path}") from exc


def paths_alias(left: Path, right: Path) -> bool:
    left_resolved = canonical_future_path(left)
    right_resolved = canonical_future_path(right)
    if os.path.normcase(str(left_resolved)) == os.path.normcase(str(right_resolved)):
        return True
    try:
        return os.path.samefile(left_resolved, right_resolved)
    except (FileNotFoundError, OSError):
        return False


def path_is_inside(root: Path, candidate: Path) -> bool:
    root_resolved = canonical_future_path(root)
    candidate_resolved = canonical_future_path(candidate)
    try:
        candidate_resolved.relative_to(root_resolved)
        return True
    except ValueError:
        return False


def fsync_dir(path: Path) -> None:
    if os.name == "nt":
        return
    try:
        fd = os.open(path, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(fd)
    except OSError:
        pass
    finally:
        os.close(fd)


def stage_bytes(parent: Path, name: str, data: bytes) -> Path:
    parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{name}.", suffix=".tmp", dir=parent)
    temp = Path(tmp_name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        return temp
    except Exception:
        if temp.exists():
            temp.unlink()
        raise


def target_exists(path: Path) -> bool:
    return path.exists() or path.is_symlink()


def transactional_commit(staged_targets: list[tuple[Path, Path]]) -> list[dict]:
    token = secrets.token_hex(8)
    backups: dict[Path, Path] = {}
    committed: list[Path] = []
    recovery: list[dict] = []
    try:
        for _, target in staged_targets:
            target.parent.mkdir(parents=True, exist_ok=True)
            if target_exists(target):
                backup = target.with_name(f".{target.name}.skill-booster-backup-{token}")
                if target_exists(backup):
                    raise RuntimeError(f"backup path already exists: {backup}")
                os.replace(target, backup)
                backups[target] = backup

        for staged, target in staged_targets:
            os.replace(staged, target)
            committed.append(target)
            fsync_dir(target.parent)

        for backup in backups.values():
            if target_exists(backup):
                backup.unlink()
        for _, target in staged_targets:
            fsync_dir(target.parent)
        return []
    except Exception as exc:
        rollback_errors: list[dict] = []
        for target in reversed(committed):
            if not target_exists(target):
                continue
            failed = target.with_name(f".{target.name}.skill-booster-failed-{token}")
            try:
                os.replace(target, failed)
                recovery.append({"kind": "failed-candidate", "target": str(target), "preserved_at": str(failed)})
            except Exception as rollback_exc:
                rollback_errors.append({"target": str(target), "error": str(rollback_exc)})

        for target, backup in backups.items():
            if not target_exists(backup):
                continue
            try:
                os.replace(backup, target)
                fsync_dir(target.parent)
            except Exception as rollback_exc:
                recovery.append({"kind": "last-good-backup", "target": str(target), "preserved_at": str(backup)})
                rollback_errors.append({"target": str(target), "error": str(rollback_exc)})

        for staged, target in staged_targets:
            if staged.exists():
                recovery.append({"kind": "staged-candidate", "target": str(target), "preserved_at": str(staged)})

        raise RuntimeError(json.dumps({
            "commit_error": str(exc),
            "rollback_errors": rollback_errors,
            "recovery": recovery,
        })) from exc


def package_files(target: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(target.rglob("*")):
        rel = path.relative_to(target)
        if should_exclude(rel) or path.is_symlink() or not path.is_file():
            continue
        files.append(path)
    return files


def candidate_identity(target: Path, files: list[Path]) -> tuple[str, dict[str, str]]:
    mapping: dict[str, str] = {}
    combined = hashlib.sha256()
    for path in files:
        rel = path.relative_to(target).as_posix()
        digest = sha256_file(path)
        mapping[rel] = digest
        combined.update(rel.encode("utf-8"))
        combined.update(b"\0")
        combined.update(digest.encode("ascii"))
        combined.update(b"\n")
    return combined.hexdigest(), mapping


def validate(target: Path) -> tuple[int, dict]:
    validator = Path(__file__).resolve().with_name("validate_skill_booster.py")
    if not validator.exists():
        return 1, {"status": "fail", "errors": [f"missing validator: {validator}"]}
    proc = subprocess.run(
        [sys.executable, str(validator), "--target", str(target)],
        text=True,
        capture_output=True,
        check=False,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    try:
        report = json.loads(proc.stdout)
    except json.JSONDecodeError:
        report = {
            "status": "fail",
            "errors": ["validator did not return JSON"],
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        }
    return proc.returncode, report


def validate_reconciliation(ledger: Path) -> tuple[int, dict]:
    validator = Path(__file__).resolve().with_name("validate_specialist_reconciliation.py")
    if not validator.exists():
        return 1, {"status": "fail", "errors": [f"missing reconciliation validator: {validator}"]}
    proc = subprocess.run(
        [sys.executable, str(validator), "--ledger", str(ledger)],
        text=True,
        capture_output=True,
        check=False,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    try:
        report = json.loads(proc.stdout)
    except json.JSONDecodeError:
        report = {
            "status": "fail",
            "errors": ["reconciliation validator did not return JSON"],
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        }
    return proc.returncode, report


def validate_portability(target: Path, hosts: str) -> tuple[int, dict]:
    validator = Path(__file__).resolve().with_name("validate_portability.py")
    if not validator.exists():
        return 1, {"status": "fail", "errors": [{"code": "PORTABILITY_VALIDATOR_MISSING", "evidence": str(validator)}]}
    proc = subprocess.run(
        [sys.executable, str(validator), "--target", str(target), "--hosts", hosts],
        text=True,
        capture_output=True,
        check=False,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    try:
        report = json.loads(proc.stdout)
    except json.JSONDecodeError:
        report = {
            "status": "fail",
            "errors": [{"code": "PORTABILITY_VALIDATOR_OUTPUT", "evidence": "validator did not return JSON"}],
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        }
    return proc.returncode, report


def write_deterministic_zip(target: Path, archive: Path, files: list[Path]) -> list[str]:
    root_name = target.name
    names: list[str] = []
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in files:
            rel = path.relative_to(target)
            archive_name = f"{root_name}/{rel.as_posix()}"
            data = path.read_bytes()
            info = zipfile.ZipInfo(archive_name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            mode = 0o755 if path.suffix.lower() in {".py", ".sh"} else 0o644
            info.external_attr = mode << 16
            zf.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
            names.append(archive_name)
    with archive.open("rb") as handle:
        os.fsync(handle.fileno())
    return names


def verify_archive(archive: Path, root_name: str) -> list[str]:
    errors: list[str] = []
    with zipfile.ZipFile(archive, "r") as zf:
        bad = zf.testzip()
        names = zf.namelist()
    top_levels = sorted({name.split("/", 1)[0] for name in names if name})
    if bad:
        errors.append(f"corrupt zip member: {bad}")
    if top_levels != [root_name]:
        errors.append(f"expected one top-level directory {root_name!r}, found {top_levels}")
    if f"{root_name}/SKILL.md" not in names:
        errors.append(f"archive missing {root_name}/SKILL.md")
    return errors


def failure(stage: str, *, code: str | None = None, **extra) -> dict:
    result = {
        "receipt_version": 2,
        "status": "fail",
        "stage": stage,
        "last_good_preserved_on_failure": True,
        "recovery": [],
        **extra,
    }
    if code:
        result["code"] = code
    return result


def preflight(target: Path, output: Path, report: Path | None) -> tuple[Path, Path, Path | None] | dict:
    target = target.expanduser().resolve()
    authored_output = output.expanduser()
    resolved_output = canonical_future_path(authored_output)

    if authored_output.name != "skill.zip" or resolved_output.name != "skill.zip":
        return failure(
            "preflight",
            code="OUTPUT_NAME_INVALID",
            errors=["output filename must be skill.zip before and after path resolution"],
            output=str(authored_output),
            resolved_output=str(resolved_output),
        )
    if path_is_inside(target, resolved_output):
        return failure("preflight", code="OUTPUT_INSIDE_TARGET", errors=["output must be outside the target skill folder"])
    if resolved_output.exists() and not resolved_output.is_file():
        return failure("preflight", code="OUTPUT_NOT_FILE", errors=["output target must be a file path"])

    resolved_report = None
    if report is not None:
        authored_report = report.expanduser()
        resolved_report = canonical_future_path(authored_report)
        if paths_alias(resolved_output, resolved_report):
            return failure(
                "preflight",
                code="OUTPUT_REPORT_ALIAS",
                errors=["package output and report output must not alias the same file"],
                output=str(resolved_output),
                report=str(resolved_report),
            )
        if authored_report.suffix.lower() != ".json" or resolved_report.suffix.lower() != ".json":
            return failure("preflight", code="REPORT_EXTENSION_INVALID", errors=["report must use and resolve to a .json extension"])
        if path_is_inside(target, resolved_report):
            return failure("preflight", code="REPORT_INSIDE_TARGET", errors=["report must be outside the target skill folder"])
        if resolved_report.exists() and not resolved_report.is_file():
            return failure("preflight", code="REPORT_NOT_FILE", errors=["report target must be a file path"])

    return target, resolved_output, resolved_report


def package(
    target: Path,
    output: Path,
    report: Path | None = None,
    reconciliation_ledger: Path | None = None,
    portability_hosts: str | None = None,
) -> dict:
    checked = preflight(target, output, report)
    if isinstance(checked, dict):
        return checked
    target, output, report = checked
    output.parent.mkdir(parents=True, exist_ok=True)
    if report is not None:
        report.parent.mkdir(parents=True, exist_ok=True)

    code, validation = validate(target)
    if code != 0 or validation.get("status") != "pass":
        return failure("validate", validation=validation, atomic_replace=False)

    portability = None
    if portability_hosts:
        portability_code, portability = validate_portability(target, portability_hosts)
        if portability_code != 0 or portability.get("status") != "pass":
            return failure(
                "portability",
                validation=validation,
                portability=portability,
                atomic_replace=False,
            )

    reconciliation = None
    if reconciliation_ledger is not None:
        rec_code, reconciliation = validate_reconciliation(reconciliation_ledger)
        if rec_code != 0 or reconciliation.get("finalization_allowed") is not True:
            return failure(
                "specialist_reconciliation",
                validation=validation,
                specialist_reconciliation=reconciliation,
                atomic_replace=False,
            )

    files = package_files(target)
    candidate_before, file_hashes = candidate_identity(target, files)
    package_stage: Path | None = None
    report_stage: Path | None = None
    recovery_paths_to_preserve: set[Path] = set()
    names: list[str] = []

    try:
        fd, tmp_name = tempfile.mkstemp(prefix=f".{output.name}.", suffix=".tmp", dir=output.parent)
        os.close(fd)
        package_stage = Path(tmp_name)
        names = write_deterministic_zip(target, package_stage, files)
        package_errors = verify_archive(package_stage, target.name)

        files_after = package_files(target)
        candidate_after, _ = candidate_identity(target, files_after)
        if candidate_after != candidate_before:
            package_errors.append("target changed while packaging; candidate identity is not stable")

        if package_errors:
            return failure(
                "package_verify",
                validation=validation,
                specialist_reconciliation=reconciliation,
                portability=portability,
                candidate_sha256=candidate_before,
                package_errors=package_errors,
                atomic_replace=False,
            )

        archive_sha256 = sha256_file(package_stage)
        size_bytes = package_stage.stat().st_size
        receipt = {
            "receipt_version": 2,
            "status": "pass",
            "stage": "committed",
            "archive": str(output),
            "file_count": len(names),
            "size_bytes": size_bytes,
            "candidate_sha256": candidate_before,
            "archive_sha256": archive_sha256,
            "atomic_replace": True,
            "last_good_preserved_on_failure": True,
            "validation": validation,
            "specialist_reconciliation": reconciliation,
            "portability": portability,
            "package_errors": [],
            "recovery": [],
            "files": names,
            "file_hashes": file_hashes,
        }

        staged_targets: list[tuple[Path, Path]] = [(package_stage, output)]
        if report is not None:
            report_stage = stage_bytes(
                report.parent,
                report.name,
                (json.dumps(receipt, indent=2, ensure_ascii=False) + "\n").encode("utf-8"),
            )
            staged_targets.append((report_stage, report))

        transactional_commit(staged_targets)
        package_stage = None
        report_stage = None
        return receipt
    except Exception as exc:
        recovery: list[dict] = []
        try:
            parsed = json.loads(str(exc))
            if isinstance(parsed, dict):
                recovery = parsed.get("recovery", [])
        except Exception:
            pass
        recovery_paths_to_preserve = {
            Path(item["preserved_at"])
            for item in recovery
            if isinstance(item, dict) and item.get("preserved_at")
        }
        return failure(
            "commit",
            code="ATOMIC_COMMIT_FAILED",
            errors=[str(exc)],
            candidate_sha256=candidate_before,
            atomic_replace=False,
            recovery=recovery,
        )
    finally:
        for temp in (package_stage, report_stage):
            if temp is not None and temp.exists() and temp not in recovery_paths_to_preserve:
                try:
                    temp.unlink()
                except OSError:
                    pass


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and package a skill as deterministic skill.zip.")
    parser.add_argument("--target", required=True, help="Skill folder to package")
    parser.add_argument("--output", required=True, help="Output path; basename must be skill.zip")
    parser.add_argument("--report", help="Optional JSON package receipt path; committed transactionally with the archive")
    parser.add_argument("--reconciliation-ledger", help="Optional specialist reconciliation JSON; packaging fails unless finalization_allowed is true")
    parser.add_argument("--portability-hosts", help="Optional comma-separated host profiles; packaging fails unless portability validation passes")
    args = parser.parse_args()

    try:
        ledger = Path(args.reconciliation_ledger) if args.reconciliation_ledger else None
        report_path = Path(args.report) if args.report else None
        result = package(Path(args.target), Path(args.output), report_path, ledger, args.portability_hosts)
    except Exception as exc:
        result = failure("exception", errors=[str(exc)], atomic_replace=False)

    text = json.dumps(result, indent=2, ensure_ascii=False)
    print(text)
    # Successful receipts are already committed transactionally. Failure output stays on
    # stdout so an existing last-good receipt is never overwritten by a failed attempt.
    return 0 if result.get("status") == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
