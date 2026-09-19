#!/usr/bin/env python3
"""Create a deterministic, recovery-aware bug-security-hunter skill archive."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

SKILL_NAME = "bug-security-hunter"
EXPECTED_TOP_LEVEL = "bug-security-hunter/"
EXCLUDE_PARTS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache"}
EXCLUDE_SUFFIXES = {".pyc", ".pyo", ".DS_Store", ".zip"}
REQUIRED_ARCHIVE_FILES = {
    f"{SKILL_NAME}/SKILL.md",
    f"{SKILL_NAME}/agents/openai.yaml",
    f"{SKILL_NAME}/evals/activation-scenarios.json",
    f"{SKILL_NAME}/evals/behavioral-scenarios.json",
    f"{SKILL_NAME}/scripts/validate_skill_package.py",
    f"{SKILL_NAME}/scripts/package_skill.py",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def should_include(path: Path, root: Path) -> bool:
    rel = path.relative_to(root)
    if path.is_symlink():
        return False
    if any(part in EXCLUDE_PARTS for part in rel.parts):
        return False
    if path.name in EXCLUDE_SUFFIXES or path.suffix in EXCLUDE_SUFFIXES:
        return False
    return path.is_file()


def package_inputs(target: Path) -> list[Path]:
    return [path for path in sorted(target.rglob("*")) if should_include(path, target)]


def validate_archive(output: Path) -> list[str]:
    with zipfile.ZipFile(output, "r") as zf:
        names = zf.namelist()
        bad_crc = zf.testzip()
    if not names:
        raise SystemExit("FAIL: archive is empty")
    if bad_crc:
        raise SystemExit(f"FAIL: archive CRC validation failed for {bad_crc}")
    top_levels = {PurePosixPath(name).parts[0] for name in names if PurePosixPath(name).parts}
    if top_levels != {SKILL_NAME}:
        raise SystemExit(f"FAIL: archive needs one top-level {EXPECTED_TOP_LEVEL} folder, got {sorted(top_levels)}")
    if len(names) != len(set(names)):
        raise SystemExit("FAIL: archive has duplicate member names")
    for name in names:
        pp = PurePosixPath(name)
        if name.startswith("/") or ".." in pp.parts:
            raise SystemExit(f"FAIL: unsafe archive member path: {name}")
        if any(part in EXCLUDE_PARTS for part in pp.parts) or pp.suffix in EXCLUDE_SUFFIXES:
            raise SystemExit(f"FAIL: excluded file leaked into archive: {name}")
    missing = sorted(REQUIRED_ARCHIVE_FILES - set(names))
    if missing:
        raise SystemExit("FAIL: archive missing required files: " + ", ".join(missing))
    return names


def resolve_output(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.is_symlink():
        raise SystemExit(f"FAIL: output may not be a symlink: {path}")
    return path.resolve(strict=False)


def ensure_outside_target(path: Path, target: Path, label: str) -> None:
    try:
        path.relative_to(target)
    except ValueError:
        return
    raise SystemExit(f"FAIL: {label} must be outside target skill folder: {path}")


def fsync_file(path: Path) -> None:
    with path.open("rb") as fh:
        os.fsync(fh.fileno())


def fsync_dir(path: Path) -> None:
    try:
        fd = os.open(path, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def tree_manifest(target: Path, inputs: list[Path]) -> tuple[list[dict[str, object]], str]:
    entries: list[dict[str, object]] = []
    aggregate = hashlib.sha256()
    for path in inputs:
        rel = path.relative_to(target).as_posix()
        data = path.read_bytes()
        digest = sha256_bytes(data)
        size = len(data)
        entries.append({"path": rel, "sha256": digest, "bytes": size})
        aggregate.update(rel.encode("utf-8"))
        aggregate.update(b"\0")
        aggregate.update(digest.encode("ascii"))
        aggregate.update(b"\0")
        aggregate.update(str(size).encode("ascii"))
        aggregate.update(b"\n")
    return entries, aggregate.hexdigest()


def commit_outputs(staged_archive: Path, output: Path, staged_receipt: Path, receipt: Path) -> None:
    pairs = [(staged_archive, output), (staged_receipt, receipt)]
    backups: dict[Path, Path] = {}
    committed: list[Path] = []
    token = str(os.getpid())
    try:
        for _, target in pairs:
            if target.exists():
                backup = target.with_name(f".{target.name}.last-good-{token}")
                if backup.exists():
                    raise RuntimeError(f"backup path already exists: {backup}")
                os.replace(target, backup)
                backups[target] = backup
        for staged, target in pairs:
            os.replace(staged, target)
            committed.append(target)
        fsync_dir(output.parent)
        if receipt.parent != output.parent:
            fsync_dir(receipt.parent)
    except Exception as exc:
        recovery: list[str] = []
        for target in reversed(committed):
            try:
                if target.exists():
                    failed = target.with_name(f".{target.name}.failed-{token}")
                    os.replace(target, failed)
                    recovery.append(f"failed candidate preserved at {failed}")
            except Exception as rollback_exc:
                recovery.append(f"could not preserve failed candidate {target}: {rollback_exc}")
        for target, backup in backups.items():
            try:
                if backup.exists():
                    os.replace(backup, target)
            except Exception as rollback_exc:
                recovery.append(f"last-good backup remains at {backup}; restore to {target}: {rollback_exc}")
        detail = "; ".join(recovery) if recovery else "no recovery paths required"
        raise SystemExit(f"FAIL: commit failed: {exc}; recovery: {detail}") from exc
    else:
        for backup in backups.values():
            try:
                backup.unlink()
            except FileNotFoundError:
                pass


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True, help="skill folder")
    parser.add_argument("--output", required=True, help="output skill.zip path")
    parser.add_argument("--receipt", help="optional receipt path; defaults to <output>.receipt.json")
    parser.add_argument("--validate", action="store_true", help="run validate_skill_package.py first")
    args = parser.parse_args()

    target = Path(args.target).resolve()
    if not target.is_dir():
        raise SystemExit(f"FAIL: target is not a directory: {target}")

    authored_output = Path(args.output).expanduser()
    if authored_output.suffix.lower() != ".zip":
        raise SystemExit("FAIL: output must use .zip extension")
    output = resolve_output(authored_output)

    authored_receipt = Path(args.receipt).expanduser() if args.receipt else Path(str(authored_output) + ".receipt.json")
    if authored_receipt.suffix.lower() != ".json":
        raise SystemExit("FAIL: receipt must use .json extension")
    receipt = resolve_output(authored_receipt)

    ensure_outside_target(output, target, "output")
    ensure_outside_target(receipt, target, "receipt")
    if output == receipt:
        raise SystemExit("FAIL: output and receipt paths alias each other")

    if args.validate:
        validator = target / "scripts" / "validate_skill_package.py"
        subprocess.run([sys.executable, str(validator), str(target)], check=True)

    inputs = package_inputs(target)
    manifest, tree_sha256 = tree_manifest(target, inputs)

    archive_fd, archive_name = tempfile.mkstemp(prefix=f".{output.name}.candidate-", suffix=".zip", dir=output.parent)
    os.close(archive_fd)
    staged_archive = Path(archive_name)
    receipt_fd, receipt_name = tempfile.mkstemp(prefix=f".{receipt.name}.candidate-", suffix=".json", dir=receipt.parent)
    os.close(receipt_fd)
    staged_receipt = Path(receipt_name)

    try:
        with zipfile.ZipFile(staged_archive, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for path in inputs:
                arcname = f"{SKILL_NAME}/{path.relative_to(target).as_posix()}"
                info = zipfile.ZipInfo(arcname)
                info.date_time = (2026, 1, 1, 0, 0, 0)
                info.external_attr = 0o644 << 16
                zf.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED)
        names = validate_archive(staged_archive)
        fsync_file(staged_archive)
        archive_sha256 = sha256_file(staged_archive)

        receipt_data = {
            "receipt_version": 1,
            "status": "pass",
            "stage": "packaging",
            "skill": SKILL_NAME,
            "target": str(target),
            "authored_output": str(authored_output),
            "canonical_output": str(output),
            "canonical_receipt": str(receipt),
            "candidate_tree_sha256": tree_sha256,
            "archive_sha256": archive_sha256,
            "archive_bytes": staged_archive.stat().st_size,
            "archive_members": len(names),
            "files": manifest,
        }
        staged_receipt.write_text(json.dumps(receipt_data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        fsync_file(staged_receipt)

        commit_outputs(staged_archive, output, staged_receipt, receipt)
    finally:
        for path in (staged_archive, staged_receipt):
            try:
                if path.exists():
                    path.unlink()
            except OSError:
                pass

    print(f"PASS: wrote and validated {output}")
    print(f"PASS: wrote package receipt {receipt}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
