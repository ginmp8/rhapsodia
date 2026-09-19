#!/usr/bin/env python3
"""Build a deterministic context-architect skill.zip with atomic delivery."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Any

EXCLUDE_PARTS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache"}
EXCLUDE_SUFFIXES = {".pyc", ".pyo", ".zip"}
RECEIPT_NOISE_DIRS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "node_modules"}
RECEIPT_NOISE_FILES = {".DS_Store"}
FIXED_ZIP_TIME = (1980, 1, 1, 0, 0, 0)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def should_include(path: Path, root: Path) -> bool:
    rel = path.relative_to(root)
    if any(part in EXCLUDE_PARTS for part in rel.parts):
        return False
    if path.suffix in EXCLUDE_SUFFIXES:
        return False
    if path.name.startswith(".") and path.name not in {".gitkeep"}:
        return False
    return path.is_file()


def included_files(root: Path) -> list[Path]:
    return [path for path in sorted(root.rglob("*"), key=lambda p: p.relative_to(root).as_posix()) if should_include(path, root)]


def tree_sha256(root: Path) -> str:
    rows: list[dict[str, object]] = []
    for path in sorted(root.rglob("*")):
        rel_path = path.relative_to(root)
        if any(part in RECEIPT_NOISE_DIRS for part in rel_path.parts):
            continue
        if path.name in RECEIPT_NOISE_FILES or path.suffix == ".pyc":
            continue
        rel = rel_path.as_posix()
        if path.is_symlink():
            rows.append({"path": rel, "type": "symlink", "target": os.readlink(path)})
        elif path.is_file():
            rows.append({"path": rel, "type": "file", "size": path.stat().st_size, "sha256": sha256_file(path)})
    payload = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def resolve_output(root: Path, raw: Path) -> Path:
    output = raw.expanduser()
    if output.suffix == "":
        output = output / "skill.zip"
    elif output.name != "skill.zip":
        output = output.with_name("skill.zip")
    resolved_parent = output.parent.resolve(strict=False)
    resolved = resolved_parent / output.name
    if is_within(resolved, root):
        raise ValueError("package output must be outside the target skill root")
    resolved_parent.mkdir(parents=True, exist_ok=True)
    return resolved


def validate_folder(root: Path) -> None:
    errors: list[str] = []
    if not (root / "SKILL.md").is_file():
        errors.append("missing SKILL.md")
    if not (root / "agents" / "openai.yaml").is_file():
        errors.append("missing agents/openai.yaml")
    if len(list(root.rglob("SKILL.md"))) != 1:
        errors.append("package must contain exactly one SKILL.md")
    if errors:
        raise ValueError("; ".join(errors))


def write_deterministic_zip(root: Path, files: list[Path], output: Path) -> None:
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in files:
            rel = path.relative_to(root).as_posix()
            info = zipfile.ZipInfo(rel, FIXED_ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            mode = 0o755 if os.access(path, os.X_OK) else 0o644
            info.external_attr = (mode & 0xFFFF) << 16
            info.create_system = 3
            zf.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def validate_archive(path: Path) -> None:
    with zipfile.ZipFile(path, "r") as zf:
        names = zf.namelist()
        if len(names) != len(set(names)):
            raise ValueError("archive contains duplicate paths")
        if names.count("SKILL.md") != 1:
            raise ValueError("archive must contain exactly one root SKILL.md")
        bad = [name for name in names if name.startswith("/") or ".." in Path(name).parts]
        if bad:
            raise ValueError(f"archive contains unsafe paths: {bad}")
        corrupt = zf.testzip()
        if corrupt:
            raise ValueError(f"archive CRC validation failed at {corrupt}")
    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb > 25:
        raise ValueError(f"package exceeds 25 MB: {size_mb:.2f} MB")


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, sort_keys=True)
            fh.write("\n")
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(temp_name, path)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def replace_with_backup(staged: Path, destination: Path) -> Path | None:
    backup: Path | None = None
    if destination.exists():
        fd, backup_name = tempfile.mkstemp(prefix=f".{destination.name}.", suffix=".bak", dir=destination.parent)
        os.close(fd)
        backup = Path(backup_name)
        shutil.copy2(destination, backup)
    os.replace(staged, destination)
    return backup


def restore(destination: Path, backup: Path | None) -> None:
    if backup is None:
        destination.unlink(missing_ok=True)
    elif backup.exists():
        os.replace(backup, destination)


def package(root: Path, output: Path, receipt: Path | None) -> tuple[Path, dict[str, Any]]:
    validate_folder(root)
    files = included_files(root)
    tree_hash = tree_sha256(root)

    fd, staged_name = tempfile.mkstemp(prefix=".skill.", suffix=".zip.tmp", dir=output.parent)
    os.close(fd)
    staged = Path(staged_name)
    try:
        write_deterministic_zip(root, files, staged)
        validate_archive(staged)
        package_hash = sha256_file(staged)
        payload = {
            "receipt_version": 1,
            "status": "pass",
            "artifact": output.name,
            "artifact_sha256": package_hash,
            "candidate_tree_sha256": tree_hash,
            "file_count": len(files),
            "deterministic_zip_metadata": True,
        }

        package_backup: Path | None = None
        receipt_backup: Path | None = None
        staged_receipt: Path | None = None
        if receipt is not None:
            receipt.parent.mkdir(parents=True, exist_ok=True)
            if receipt == output:
                raise ValueError("receipt path must differ from package output")
            if is_within(receipt.resolve(), root):
                raise ValueError("receipt path must be outside the target skill root")
            fd2, receipt_tmp = tempfile.mkstemp(prefix=f".{receipt.name}.", suffix=".tmp", dir=receipt.parent)
            os.close(fd2)
            staged_receipt = Path(receipt_tmp)
            staged_receipt.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        try:
            package_backup = replace_with_backup(staged, output)
            if staged_receipt is not None and receipt is not None:
                receipt_backup = replace_with_backup(staged_receipt, receipt)
        except Exception:
            restore(output, package_backup)
            if receipt is not None:
                restore(receipt, receipt_backup)
            raise
        finally:
            if package_backup is not None:
                package_backup.unlink(missing_ok=True)
            if receipt_backup is not None:
                receipt_backup.unlink(missing_ok=True)
            if staged_receipt is not None:
                staged_receipt.unlink(missing_ok=True)
        return output, payload
    finally:
        staged.unlink(missing_ok=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", help="Skill folder to package.")
    parser.add_argument("output", nargs="?", default="skill.zip", help="Output zip path or directory; final filename is skill.zip.")
    parser.add_argument("--receipt", help="Optional JSON receipt path outside the target skill root.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.target).resolve(strict=True)
    output = resolve_output(root, Path(args.output))
    receipt = Path(args.receipt).expanduser().resolve() if args.receipt else None
    try:
        result, payload = package(root, output, receipt)
    except Exception as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}, sort_keys=True), file=sys.stderr)
        return 1
    print(json.dumps({"status": "pass", "artifact": str(result), **payload}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
