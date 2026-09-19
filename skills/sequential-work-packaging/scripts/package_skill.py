#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _swp_common import atomic_write_json, sha256_file, tree_hash  # noqa: E402

EXCLUDED_DIRS = {"__pycache__", ".git", ".pytest_cache"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}


def skill_name(root: Path) -> str:
    text = (root / "SKILL.md").read_text(encoding="utf-8")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not m:
        raise ValueError("SKILL.md portable frontmatter missing")
    for line in m.group(1).splitlines():
        if line.startswith("name:"):
            name = line.split(":", 1)[1].strip()
            if re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
                return name
    raise ValueError("portable frontmatter name missing or invalid")


def package(root: Path, output: Path, receipt: Path | None = None) -> dict:
    root = root.resolve()
    output = output.resolve(strict=False)
    if not (root / "SKILL.md").is_file():
        return {"status": "blocked", "code": "SKILL_MD_MISSING"}
    if output == root or root in output.parents:
        return {"status": "blocked", "code": "OUTPUT_INSIDE_INPUT", "output": str(output)}

    if receipt:
        receipt = receipt.resolve(strict=False)
        if receipt == output or _samefile_if_exists(receipt, output):
            return {"status": "blocked", "code": "OUTPUT_RECEIPT_ALIAS"}
        if receipt == root or root in receipt.parents:
            return {"status": "blocked", "code": "RECEIPT_INSIDE_INPUT"}

    name = skill_name(root)
    files: list[tuple[Path, Path]] = []
    for path in sorted(x for x in root.rglob("*") if x.is_file() or x.is_symlink()):
        rel = path.relative_to(root)
        if any(part in EXCLUDED_DIRS for part in rel.parts) or path.suffix in EXCLUDED_SUFFIXES:
            continue
        if path.is_symlink():
            return {"status": "blocked", "code": "SYMLINK_UNSUPPORTED", "path": rel.as_posix()}
        files.append((path, rel))

    output.parent.mkdir(parents=True, exist_ok=True)
    if receipt:
        receipt.parent.mkdir(parents=True, exist_ok=True)

    zip_tmp = _temp_path(output.parent, f".{output.name}.", ".zip.tmp")
    receipt_tmp: Path | None = None
    output_backup: Path | None = None
    receipt_backup: Path | None = None
    output_existed = output.is_file()
    receipt_existed = bool(receipt and receipt.is_file())
    committed_output = False
    committed_receipt = False

    try:
        _build_zip(zip_tmp, name, files)
        package_sha256 = sha256_file(zip_tmp)
        result = {
            "receipt_version": 1,
            "status": "pass",
            "package_name": name,
            "input_root": str(root),
            "input_tree_sha256": tree_hash(root),
            "file_count": len(files),
            "output": str(output),
            "package_sha256": package_sha256,
            "deterministic_zip_metadata": {
                "timestamp": "1980-01-01T00:00:00",
                "sorted_paths": True,
                "compression": "deflate-9",
            },
        }

        if receipt:
            receipt_tmp = _temp_path(receipt.parent, f".{receipt.name}.", ".json.tmp")
            atomic_write_json(receipt_tmp, result)

        if output_existed:
            output_backup = _temp_path(output.parent, f".{output.name}.", ".backup")
            shutil.copyfile(output, output_backup)
            _fsync_file(output_backup)
        if receipt and receipt_existed:
            receipt_backup = _temp_path(receipt.parent, f".{receipt.name}.", ".backup")
            shutil.copyfile(receipt, receipt_backup)
            _fsync_file(receipt_backup)

        os.replace(zip_tmp, output)
        committed_output = True
        _fsync_file(output)
        if sha256_file(output) != package_sha256:
            raise RuntimeError("committed package hash differs from staged package hash")

        if receipt and receipt_tmp:
            os.replace(receipt_tmp, receipt)
            committed_receipt = True
            _fsync_file(receipt)
            written = json.loads(receipt.read_text(encoding="utf-8"))
            if written.get("package_sha256") != package_sha256 or written.get("output") != str(output):
                raise RuntimeError("committed package receipt does not describe the committed package")

        _safe_unlink(output_backup)
        _safe_unlink(receipt_backup)
        return result
    except Exception as exc:
        rollback_errors: list[dict[str, str]] = []
        if committed_receipt and receipt:
            try:
                if receipt_backup and receipt_backup.is_file():
                    shutil.copyfile(receipt_backup, receipt)
                    _fsync_file(receipt)
                elif receipt.exists():
                    receipt.unlink()
            except Exception as rb_exc:
                rollback_errors.append({"path": str(receipt), "error": str(rb_exc)})
        if committed_output:
            try:
                if output_backup and output_backup.is_file():
                    shutil.copyfile(output_backup, output)
                    _fsync_file(output)
                elif output.exists():
                    output.unlink()
            except Exception as rb_exc:
                rollback_errors.append({"path": str(output), "error": str(rb_exc)})

        recovery_paths = [str(p) for p in (output_backup, receipt_backup, zip_tmp, receipt_tmp) if p and p.exists()]
        if not rollback_errors:
            for path in (output_backup, receipt_backup, zip_tmp, receipt_tmp):
                _safe_unlink(path)
            recovery_paths = []
        return {
            "receipt_version": 1,
            "status": "failed_recovery_required" if rollback_errors else "failed_recovered",
            "code": "PACKAGE_COMMIT_FAILED",
            "failure": str(exc),
            "output": str(output),
            "receipt": str(receipt) if receipt else None,
            "rollback_errors": rollback_errors,
            "recovery_paths": recovery_paths,
        }
    finally:
        _safe_unlink(zip_tmp)
        _safe_unlink(receipt_tmp)


def _build_zip(tmp: Path, name: str, files: list[tuple[Path, Path]]) -> None:
    with zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path, rel in files:
            arc = f"{name}/{rel.as_posix()}"
            info = zipfile.ZipInfo(arc, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            executable = rel.parts and rel.parts[0] == "scripts" and path.read_bytes().startswith(b"#!")
            mode = 0o100755 if executable else 0o100644
            info.external_attr = mode << 16
            info.flag_bits |= 0x800
            zf.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    _fsync_file(tmp)


def _temp_path(parent: Path, prefix: str, suffix: str) -> Path:
    fd, name = tempfile.mkstemp(prefix=prefix, suffix=suffix, dir=str(parent))
    os.close(fd)
    return Path(name)


def _samefile_if_exists(a: Path, b: Path) -> bool:
    try:
        return a.exists() and b.exists() and os.path.samefile(a, b)
    except OSError:
        return False


def _fsync_file(path: Path) -> None:
    with path.open("rb") as f:
        os.fsync(f.fileno())


def _safe_unlink(path: Path | None) -> None:
    if not path:
        return
    try:
        path.unlink(missing_ok=True)
    except OSError:
        pass


def main() -> int:
    ap = argparse.ArgumentParser(description="Build a deterministic portable ZIP for this Agent Skill.")
    ap.add_argument("--target", default=str(Path(__file__).resolve().parents[1]))
    ap.add_argument("--output", required=True)
    ap.add_argument("--receipt")
    args = ap.parse_args()
    result = package(Path(args.target), Path(args.output), Path(args.receipt) if args.receipt else None)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
