#!/usr/bin/env python3
"""Validate and package a portable Agent Skills folder with recovery-aware delivery."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile
from pathlib import Path
from typing import Any

EXCLUDED_DIR_NAMES = {
    ".git",
    ".hg",
    ".svn",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".skill-improver",
    ".hardening-work",
}

EXCLUDED_FILE_NAMES = {
    ".DS_Store",
    "test-results.json",
    "skill-benchmark.md",
}

EXCLUDED_SUFFIXES = {
    ".pyc",
    ".pyo",
    ".zip",
}


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def canonical(path: Path) -> Path:
    return path.expanduser().resolve(strict=False)


def is_within(path: Path, root: Path) -> bool:
    try:
        canonical(path).relative_to(canonical(root))
        return True
    except ValueError:
        return False


def aliases(a: Path, b: Path) -> bool:
    ca, cb = canonical(a), canonical(b)
    if ca == cb:
        return True
    if a.exists() and b.exists():
        try:
            return os.path.samefile(a, b)
        except OSError:
            return False
    return False


def ensure_no_alias(candidate: Path, protected: list[Path], label: str) -> None:
    for item in protected:
        if aliases(candidate, item):
            raise ValueError(f"{label} aliases protected path: {item}")


def preflight_paths(root: Path, output: Path, receipt: Path | None, protected: list[Path]) -> dict[str, str]:
    if output.exists() and output.is_dir():
        raise ValueError(f"output path is a directory: {output}")
    if output.suffix.lower() != ".zip":
        raise ValueError(f"output must end in .zip: {output}")
    resolved_output = canonical(output)
    if resolved_output.suffix.lower() != ".zip":
        raise ValueError(f"canonical output must end in .zip: {resolved_output}")
    if is_within(resolved_output, root):
        raise ValueError("output must not be written inside the target skill folder")
    ensure_no_alias(resolved_output, [root, *protected], "output")

    result = {
        "output_authored": str(output),
        "output_canonical": str(resolved_output),
    }
    if receipt is not None:
        if receipt.exists() and receipt.is_dir():
            raise ValueError(f"receipt path is a directory: {receipt}")
        resolved_receipt = canonical(receipt)
        if is_within(resolved_receipt, root):
            raise ValueError("receipt must not be written inside the target skill folder")
        if aliases(resolved_receipt, resolved_output):
            raise ValueError("receipt aliases package output")
        ensure_no_alias(resolved_receipt, [root, *protected], "receipt")
        result.update(
            {
                "receipt_authored": str(receipt),
                "receipt_canonical": str(resolved_receipt),
            }
        )
    return result


def is_excluded(path: Path, root: Path, output_path: Path) -> bool:
    resolved = canonical(path)
    if resolved == canonical(output_path):
        return True
    rel = path.relative_to(root)
    if any(part in EXCLUDED_DIR_NAMES for part in rel.parts):
        return True
    if path.name in EXCLUDED_FILE_NAMES:
        return True
    if path.suffix.lower() in EXCLUDED_SUFFIXES:
        return True
    if any(part.startswith("hardening-") for part in rel.parts):
        return True
    return False


def iter_package_files(root: Path, output_path: Path) -> list[Path]:
    files: list[Path] = []
    for candidate in sorted(root.rglob("*")):
        if candidate.is_symlink():
            raise ValueError(f"symlinks are not packaged: {candidate.relative_to(root)}")
        if not candidate.is_file():
            continue
        if is_excluded(candidate, root, output_path):
            continue
        files.append(candidate)
    return files


def run_validator(root: Path, validator: Path) -> dict[str, Any]:
    if not validator.exists():
        raise FileNotFoundError(f"validator not found: {validator}")

    # Some third-party or legacy validators create caches/generated files while checking.
    # Run them against an exact private copy so validation cannot mutate the frozen candidate.
    with tempfile.TemporaryDirectory(prefix="skill-validator-") as raw_tmp:
        staged_root = Path(raw_tmp) / "target"
        shutil.copytree(root, staged_root, symlinks=False)
        try:
            validator_rel = validator.resolve().relative_to(root.resolve())
            staged_validator = staged_root / validator_rel
        except ValueError:
            staged_validator = validator

        completed = subprocess.run(
            [sys.executable, "-S", str(staged_validator), "--target", str(staged_root)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
    if completed.returncode != 0:
        raise RuntimeError("validator failed:\n" + completed.stdout)
    try:
        data = json.loads(completed.stdout)
    except json.JSONDecodeError:
        data = {"status": "pass", "raw_output": completed.stdout}
    if str(data.get("status", "pass")).lower() not in {"pass", "ok", "success"}:
        raise RuntimeError(f"validator did not pass: {data}")
    if isinstance(data, dict):
        data = dict(data)
        data["validated_candidate"] = str(root)
        data["validation_isolation"] = "private-copy"
    return data


def validate_root(root: Path) -> None:
    if not root.exists() or not root.is_dir():
        raise NotADirectoryError(f"target is not a directory: {root}")
    skill_files = list(root.rglob("SKILL.md"))
    if len(skill_files) != 1:
        raise ValueError(f"expected exactly one SKILL.md, found {len(skill_files)}")
    if canonical(skill_files[0].parent) != canonical(root):
        raise ValueError("SKILL.md must be at the package root")


def build_stage_zip(root: Path, output_dir: Path, files: list[Path]) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    fd, raw_path = tempfile.mkstemp(prefix=".skill-package-stage-", suffix=".zip", dir=output_dir)
    os.close(fd)
    stage = Path(raw_path)
    try:
        with zipfile.ZipFile(stage, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for file_path in files:
                zf.write(file_path, file_path.relative_to(root).as_posix())
        with zipfile.ZipFile(stage, "r") as zf:
            bad = zf.testzip()
            if bad is not None:
                raise RuntimeError(f"staged zip failed CRC validation at {bad}")
            if len(zf.infolist()) != len(files):
                raise RuntimeError("staged zip entry count differs from package file count")
        return stage
    except Exception:
        stage.unlink(missing_ok=True)
        raise


def write_json_atomic(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, raw_path = tempfile.mkstemp(prefix=f".{path.name}.stage-", suffix=".json", dir=path.parent)
    os.close(fd)
    stage = Path(raw_path)
    try:
        with stage.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(stage, path)
    finally:
        stage.unlink(missing_ok=True)


def backup_copy(path: Path, token: str) -> Path | None:
    if not path.exists():
        return None
    backup = path.with_name(f".{path.name}.last-good-{token}")
    shutil.copy2(path, backup)
    return backup


def restore_or_remove(destination: Path, backup: Path | None) -> None:
    if backup and backup.exists():
        os.replace(backup, destination)
    else:
        destination.unlink(missing_ok=True)


def deliver(stage_zip: Path, output: Path, receipt_path: Path | None, receipt: dict[str, Any]) -> list[str]:
    token = f"{os.getpid()}-{time.time_ns()}"
    output.parent.mkdir(parents=True, exist_ok=True)
    if receipt_path is not None:
        receipt_path.parent.mkdir(parents=True, exist_ok=True)

    output_backup: Path | None = None
    receipt_backup: Path | None = None
    recovery: list[str] = []
    output_committed = False

    try:
        output_backup = backup_copy(output, token)
        receipt_backup = backup_copy(receipt_path, token) if receipt_path is not None else None
        os.replace(stage_zip, output)
        output_committed = True
        if receipt_path is not None:
            write_json_atomic(receipt_path, receipt)
        expected_hash = str(receipt.get("artifact", {}).get("sha256", ""))
        if expected_hash and sha256_file(output) != expected_hash:
            raise RuntimeError("committed package hash differs from staged package hash")
        if receipt_path is not None:
            written = json.loads(receipt_path.read_text(encoding="utf-8"))
            if expected_hash and written.get("artifact", {}).get("sha256") != expected_hash:
                raise RuntimeError("committed receipt hash does not match package hash")
    except Exception as exc:
        if output_committed and output.exists():
            failed_candidate = output.with_name(f".{output.name}.failed-{token}")
            try:
                os.replace(output, failed_candidate)
                recovery.append(str(failed_candidate))
            except OSError:
                pass
        try:
            restore_or_remove(output, output_backup)
        except OSError:
            if output_backup and output_backup.exists():
                recovery.append(str(output_backup))
        if receipt_path is not None:
            try:
                restore_or_remove(receipt_path, receipt_backup)
            except OSError:
                if receipt_backup and receipt_backup.exists():
                    recovery.append(str(receipt_backup))
        raise RuntimeError(
            "package commit failed; last-good restoration attempted"
            + (f"; recovery paths: {', '.join(recovery)}" if recovery else "")
        ) from exc
    else:
        for backup in (output_backup, receipt_backup):
            if backup is not None:
                backup.unlink(missing_ok=True)
        return recovery
    finally:
        stage_zip.unlink(missing_ok=True)


def build_receipt(
    root: Path,
    output: Path,
    files: list[Path],
    validator_result: dict[str, Any] | None,
    path_info: dict[str, str],
    artifact_sha256: str,
    artifact_size: int,
) -> dict[str, Any]:
    return {
        "receipt_version": 1,
        "status": "pass",
        "stage": "package",
        "target": str(root),
        "paths": path_info,
        "artifact": {
            "path": str(canonical(output)),
            "sha256": artifact_sha256,
            "size": artifact_size,
            "files_packaged": len(files),
        },
        "checks": [
            {"code": "package/path-preflight", "status": "pass", "subject": str(output)},
            {"code": "package/zip-integrity", "status": "pass", "subject": str(output)},
            {"code": "package/validator", "status": "pass" if validator_result is not None else "not-run", "subject": str(root)},
        ],
        "validator": validator_result,
        "recovery": [],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and package an Agent Skills folder.")
    parser.add_argument("--target", required=True, type=Path, help="Path to the skill folder.")
    parser.add_argument("--output", required=True, type=Path, help="Output .zip path.")
    parser.add_argument("--receipt", type=Path, help="Optional JSON receipt sidecar written atomically.")
    parser.add_argument(
        "--validator",
        type=Path,
        help="Validator script. Defaults to scripts/validate_skill_improver_package.py under the target.",
    )
    parser.add_argument("--protected-path", action="append", type=Path, default=[], help="Additional path that output/receipt must not alias. Can be repeated.")
    parser.add_argument("--no-validate", action="store_true", help="Skip validator execution.")
    args = parser.parse_args()

    stage_zip: Path | None = None
    try:
        root = canonical(args.target)
        output = canonical(args.output)
        receipt_path = canonical(args.receipt) if args.receipt else None
        protected = [canonical(p) for p in args.protected_path]
        validate_root(root)
        path_info = preflight_paths(root, output, receipt_path, protected)

        validator_result: dict[str, Any] | None = None
        if not args.no_validate:
            validator = canonical(args.validator) if args.validator else root / "scripts" / "validate_skill_improver_package.py"
            validator_result = run_validator(root, validator)

        files = iter_package_files(root, output)
        stage_zip = build_stage_zip(root, output.parent, files)
        artifact_sha256 = sha256_file(stage_zip)
        artifact_size = stage_zip.stat().st_size
        receipt = build_receipt(root, output, files, validator_result, path_info, artifact_sha256, artifact_size)
        recovery = deliver(stage_zip, output, receipt_path, receipt)
        stage_zip = None

        committed_hash = sha256_file(output)
        if committed_hash != artifact_sha256:
            raise RuntimeError("committed package hash differs from staged package hash")
        receipt["artifact"]["sha256"] = committed_hash
        receipt["recovery"] = recovery
        if receipt_path is not None:
            written = json.loads(receipt_path.read_text(encoding="utf-8"))
            if written.get("artifact", {}).get("sha256") != committed_hash:
                raise RuntimeError("receipt hash does not match committed package")

        print(json.dumps(receipt, indent=2, sort_keys=True), flush=True)
        return 0
    except Exception as exc:
        if stage_zip is not None:
            stage_zip.unlink(missing_ok=True)
        failure = {
            "receipt_version": 1,
            "status": "fail",
            "stage": "package",
            "error": str(exc),
        }
        print(json.dumps(failure, indent=2, sort_keys=True), flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
