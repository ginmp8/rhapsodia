#!/usr/bin/env python3
"""Build an exact, reproducible portable skill ZIP and provenance receipt.

Uses standard-library Python 3.10+, emits no host-specific wrappers, and does
not install the skill. Never writes inside the canonical skill root.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import tempfile
import zipfile
from pathlib import Path

from validate_package import validate_package
from validate_report import validate_report
from validate_traceability import validate_traceability

FIXED_TIME = (1980, 1, 1, 0, 0, 0)


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _validate_inputs(root: Path, out: Path, receipt: Path) -> None:
    if not root.is_dir():
        raise ValueError("skill root must be a directory")
    if root.name != "premortem-analysis":
        raise ValueError("skill directory name must match its canonical identity")
    for path in (out, receipt):
        if path.resolve().is_relative_to(root.resolve()):
            raise ValueError("output must not be inside the skill root")
        if path.is_symlink() or path.is_dir():
            raise ValueError("output must be a regular file or absent")
    if out.resolve() == receipt.resolve():
        raise ValueError("package and receipt must be different files")
    if out.suffix.lower() != ".zip" or receipt.suffix.lower() != ".json":
        raise ValueError("expected .zip package and .json receipt")


def _payload(root: Path) -> list[tuple[str, bytes]]:
    out: list[tuple[str, bytes]] = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"symbolic link rejected: {path}")
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if any(chunk in ("__pycache__", ".git") for chunk in path.relative_to(root).parts):
            raise ValueError(f"generated or forbidden bytes in package: {rel}")
        out.append((f"{root.name}/{rel}", path.read_bytes()))
    return out


def build(root: Path, output: Path, receipt_path: Path, overwrite: bool = False) -> dict:
    root = root.resolve()
    output = output.absolute()
    receipt_path = receipt_path.absolute()
    _validate_inputs(root, output, receipt_path)
    if (output.exists() or receipt_path.exists()) and not overwrite:
        raise ValueError("output already exists; use --overwrite explicitly")

    checks = {
        "package": validate_package(root),
        "trace": validate_traceability(json.loads((root / "evidence/traceability.json").read_text(encoding="utf-8")), root),
        "example": validate_report(json.loads((root / "examples/messaging-migration.json").read_text(encoding="utf-8")))
    }
    failures = {name: errs for name, errs in checks.items() if errs}
    if failures:
        raise ValueError(f"failed prepackaging checks: {failures}")
    entries = _payload(root)
    if not entries:
        raise ValueError("empty skill archive")
    output.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    stage_dir = Path(tempfile.mkdtemp(prefix="premortem-package-", dir=str(output.parent)))
    stage_zip = stage_dir / "stage.zip"
    stage_json = stage_dir / "stage.json"
    backups: list[tuple[Path, Path | None]] = []
    preserve_recovery = False
    try:
        with zipfile.ZipFile(stage_zip, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
            for name, data in entries:
                info = zipfile.ZipInfo(name, date_time=FIXED_TIME)
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = (0o100644 << 16)
                info.create_system = 3
                z.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
        with zipfile.ZipFile(stage_zip, "r") as z:
            if z.testzip() is not None:
                raise ValueError("archive CRC failed")
            names = z.namelist()
            if names != [name for name, _ in entries]:
                raise ValueError("archive member order mismatch")
            for name, data in entries:
                if z.read(name) != data:
                    raise ValueError(f"archive content mismatch: {name}")
        zip_hash = _digest(stage_zip.read_bytes())
        receipt = {
            "receipt_version": "1.0.0",
            "status": "pass",
            "skill": root.name,
            "version": (root / "VERSION").read_text(encoding="utf-8").strip(),
            "profile": "portable-core",
            "archive_sha256": zip_hash,
            "archive_bytes": stage_zip.stat().st_size,
            "file_count": len(entries),
            "files": [{"path": name, "sha256": _digest(data), "bytes": len(data)} for name, data in entries],
            "gates": {"structural": "pass", "trace": "pass", "example_json": "pass", "host_runtime": "not-run", "llm_activation": "not-run"},
            "claim_limit": "Structural/serialization verification; no runtime/behavioral claim"
        }
        stage_json.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        for path in (output, receipt_path):
            if path.exists():
                backup = stage_dir / ("backup-zip" if path == output else "backup-receipt")
                shutil.copy2(path, backup)
                backups.append((path, backup))
            else:
                backups.append((path, None))
        try:
            os.replace(stage_zip, output)
            os.replace(stage_json, receipt_path)
            if _digest(output.read_bytes()) != zip_hash:
                raise ValueError("committed archive differs from frozen validated bytes")
            committed_receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            if committed_receipt.get("archive_sha256") != zip_hash:
                raise ValueError("receipt does not match committed archive")
        except (OSError, ValueError) as failure:
            rollback_errors = []
            for path, backup in reversed(backups):
                try:
                    if backup is None:
                        path.unlink(missing_ok=True)
                    else:
                        os.replace(backup, path)
                except OSError as rollback_failure:
                    rollback_errors.append(f"{path}: {rollback_failure}")
            if rollback_errors:
                preserve_recovery = True
                raise RuntimeError(f"Rollback incomplete; recovery files at {stage_dir}: {rollback_errors}") from failure
            raise
        return receipt
    finally:
        if not preserve_recovery:
            shutil.rmtree(stage_dir, ignore_errors=True)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--receipt", type=Path)
    p.add_argument("--overwrite", action="store_true")
    args = p.parse_args()
    receipt_path = args.receipt if args.receipt else args.out.with_name(args.out.stem + ".receipt.json")
    try:
        receipt = build(args.root, args.out, receipt_path, args.overwrite)
    except (OSError, ValueError) as e:
        print(f"FAIL: {e}")
        return 1
    print(f"PASS: {receipt['skill']} v{receipt['version']} {receipt['file_count']} files SHA256 {receipt['archive_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
