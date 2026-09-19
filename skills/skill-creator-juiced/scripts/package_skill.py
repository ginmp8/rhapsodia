#!/usr/bin/env python3
"""Validate and recovery-safely package a portable Agent Skills skill directory."""
from __future__ import annotations

import argparse
import sys
sys.dont_write_bytecode = True

import hashlib
import json
import os
import re
import secrets
import tempfile
import zipfile
from pathlib import Path
from typing import Any

from skill_spec import read_text, validate_agent_skill
from validate_portability import normalize_hosts, validate_portability

TEXT_SUFFIXES = {".md", ".txt", ".yaml", ".yml", ".json", ".py", ".sh", ".template"}
EXCLUDED_DIRS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "reports", "benchmark-reports", "test-results", "tmp"}
EXCLUDED_FILES = {".DS_Store"}
SENSITIVE_RE = re.compile(r"(^|[-_.])(secret|secrets|credential|credentials|token|tokens)([-_.]|$)|private[-_.]?key|^\.env($|\.)", re.I)
MARKER_RE = re.compile(r"\[" + "TO" + "DO|" + r"\b" + "TO" + "DO" + r"\s*:|replace" + " with actual|this is a " + "placeholder", re.I)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_future_path(path: str | Path) -> Path:
    try:
        return Path(path).expanduser().resolve(strict=False)
    except RuntimeError as exc:
        raise ValueError(f"path contains a symbolic-link cycle: {path}") from exc


def paths_alias(left: str | Path, right: str | Path) -> bool:
    a = canonical_future_path(left)
    b = canonical_future_path(right)
    if os.path.normcase(str(a)) == os.path.normcase(str(b)):
        return True
    try:
        return os.path.samefile(a, b)
    except (FileNotFoundError, OSError):
        return False


def path_is_inside(root: str | Path, candidate: str | Path) -> bool:
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


def fsync_file(path: Path) -> None:
    with path.open("rb") as fh:
        os.fsync(fh.fileno())


def stage_bytes(parent: Path, logical_name: str, data: bytes) -> Path:
    parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{logical_name}.", suffix=".tmp", dir=parent)
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        return tmp
    except Exception:
        tmp.unlink(missing_ok=True)
        raise


def atomic_write_bytes(path: Path, data: bytes) -> None:
    staged = stage_bytes(path.parent, path.name, data)
    try:
        os.replace(staged, path)
        fsync_dir(path.parent)
    finally:
        staged.unlink(missing_ok=True)


def target_exists(path: Path) -> bool:
    return path.exists() or path.is_symlink()


def skip_reason(rel: str) -> str | None:
    parts = Path(rel).parts
    if any(part in EXCLUDED_DIRS for part in parts[:-1]):
        return "excluded directory"
    name = parts[-1]
    if name in EXCLUDED_FILES or name.endswith(("~", ".swp", ".swo", ".pyc", ".pyo", ".zip")):
        return "excluded file"
    if SENSITIVE_RE.search(name):
        return "sensitive-looking file name"
    return None


def package_files(target: Path) -> tuple[list[Path], list[dict[str, str]], list[str]]:
    files: list[Path] = []
    excluded: list[dict[str, str]] = []
    errors: list[str] = []
    for path in sorted(target.rglob("*")):
        rel = path.relative_to(target).as_posix()
        if path.is_symlink():
            errors.append(f"symlink path blocked: {rel}")
            continue
        if not path.is_file():
            continue
        reason = skip_reason(rel)
        if reason:
            excluded.append({"path": rel, "reason": reason})
        else:
            files.append(path)
    return files, excluded, errors


def source_tree_sha256(target: Path, files: list[Path]) -> str:
    manifest = []
    for path in files:
        manifest.append({
            "path": path.relative_to(target).as_posix(),
            "size": path.stat().st_size,
            "sha256": sha256_file(path),
        })
    payload = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def validate_folder(target: Path, profile: str, portability_hosts: str | None = None) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    portability = validate_agent_skill(target, profile)
    errors.extend(portability["errors"])
    warnings.extend(portability["warnings"])
    host_portability = None
    if portability_hosts:
        host_portability = validate_portability(target, normalize_hosts(portability_hosts))
        errors.extend(item["evidence"] for item in host_portability["errors"])
        warnings.extend(item["evidence"] for item in host_portability["warnings"])

    skill_files = [p for p in target.rglob("SKILL.md") if p.is_file() and not skip_reason(p.relative_to(target).as_posix())]
    if skill_files != [target / "SKILL.md"]:
        errors.append(f"target must contain exactly one root SKILL.md, found {len(skill_files)}")

    files, _, file_errors = package_files(target)
    errors.extend(file_errors)
    if not files:
        errors.append("no packageable files found")
    for path in files:
        rel = path.relative_to(target).as_posix()
        if path.suffix.lower() in TEXT_SUFFIXES and not rel.startswith("assets/templates/"):
            for no, line in enumerate(read_text(path).splitlines(), 1):
                if "MARKER_RE" not in line and MARKER_RE.search(line):
                    errors.append(f"residual scaffold marker: {rel}:{no}")
    return {"status": "pass" if not errors else "fail", "errors": sorted(set(errors)), "warnings": sorted(set(warnings)), "portability": portability, "host_portability": host_portability}


def stage_zip(target: Path, output: Path) -> tuple[Path, dict[str, Any]]:
    files, excluded, file_errors = package_files(target)
    if file_errors:
        raise ValueError("; ".join(file_errors))
    output.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{output.name}.", suffix=".tmp", dir=output.parent)
    os.close(fd)
    tmp = Path(tmp_name)
    try:
        with zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for path in files:
                rel = path.relative_to(target).as_posix()
                zf.write(path, f"{target.name}/{rel}")
        fsync_file(tmp)
        return tmp, {
            "output": str(output),
            "file_count": len(files),
            "excluded": excluded,
            "size_bytes": tmp.stat().st_size,
            "sha256": sha256_file(tmp),
            "source_tree_sha256": source_tree_sha256(target, files),
        }
    except Exception:
        tmp.unlink(missing_ok=True)
        raise


def validate_archive(zip_path: Path) -> dict[str, Any]:
    errors: list[str] = []
    entries: list[str] = []
    try:
        with zipfile.ZipFile(zip_path) as zf:
            bad = zf.testzip()
            if bad:
                errors.append(f"corrupt archive member: {bad}")
            entries = sorted(n for n in zf.namelist() if not n.endswith("/"))
            roots = {n.split("/", 1)[0] for n in entries}
            root = next(iter(roots)) if len(roots) == 1 else ""
            if len(roots) != 1:
                errors.append(f"archive must contain one top-level directory, found {sorted(roots)}")
            if not root or f"{root}/SKILL.md" not in entries:
                errors.append("archive missing root SKILL.md")
            for entry in entries:
                rel = entry.split("/", 1)[1] if "/" in entry else entry
                if entry.startswith("/") or ".." in Path(entry).parts:
                    errors.append(f"unsafe archive path: {entry}")
                reason = skip_reason(rel)
                if reason:
                    errors.append(f"blocked path included: {entry} ({reason})")
    except (zipfile.BadZipFile, FileNotFoundError) as exc:
        errors.append(str(exc))
    return {
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "warnings": [],
        "file_count": len(entries),
        "size_bytes": zip_path.stat().st_size if zip_path.exists() else 0,
        "sha256": sha256_file(zip_path) if zip_path.exists() else None,
    }


def transactional_commit(staged_targets: list[tuple[Path, Path]]) -> dict[str, Any]:
    token = secrets.token_hex(8)
    backups: dict[Path, Path] = {}
    committed: list[Path] = []
    recovery: list[dict[str, str]] = []
    cleanup_warnings: list[str] = []
    try:
        for _, target in staged_targets:
            target.parent.mkdir(parents=True, exist_ok=True)
            if target_exists(target):
                backup = target.with_name(f".{target.name}.juiced-backup-{token}")
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
                try:
                    backup.unlink()
                except OSError as exc:
                    recovery.append({"kind": "obsolete-backup", "preserved_at": str(backup)})
                    cleanup_warnings.append(str(exc))
        return {"status": "pass", "recovery": recovery, "cleanup_warnings": cleanup_warnings}
    except Exception as exc:
        rollback_errors: list[dict[str, str]] = []
        for target in reversed(committed):
            if not target_exists(target):
                continue
            failed = target.with_name(f".{target.name}.juiced-failed-{token}")
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
                recovery.append({"kind": "previous-output-backup", "target": str(target), "preserved_at": str(backup)})
                rollback_errors.append({"target": str(target), "error": str(rollback_exc)})

        for staged, target in staged_targets:
            if staged.exists():
                recovery.append({"kind": "staged-candidate", "target": str(target), "preserved_at": str(staged)})

        raise RuntimeError(json.dumps({"commit_error": str(exc), "rollback_errors": rollback_errors, "recovery": recovery})) from exc


def emit_result(result: dict[str, Any], json_output: str | None, *, preserve_existing_on_failure: bool = False) -> None:
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if json_output:
        out = canonical_future_path(json_output)
        if not (preserve_existing_on_failure and target_exists(out)):
            atomic_write_bytes(out, payload.encode("utf-8"))
            print(f"wrote {out}")
    sys.stdout.write(payload)
    sys.stdout.flush()


def preflight_package_paths(target: Path, output_raw: str, receipt_raw: str | None) -> tuple[Path, Path | None, dict[str, Any] | None]:
    authored_output = Path(output_raw).expanduser()
    try:
        output = canonical_future_path(authored_output)
    except ValueError as exc:
        return Path(output_raw), None, {"code": "output/path-cycle", "error": str(exc)}
    if authored_output.suffix.lower() != ".zip":
        return output, None, {"code": "output/extension", "error": "output must use a .zip extension", "output": str(authored_output)}
    if output.suffix.lower() != ".zip":
        return output, None, {"code": "output/resolved-extension", "error": "output must resolve to a .zip destination", "output": str(authored_output), "resolved_output": str(output)}
    if output.exists() and not output.is_file():
        return output, None, {"code": "output/not-file", "error": "output target must be a file path", "output": str(output)}
    if path_is_inside(target, output):
        return output, None, {"code": "output/inside-target", "error": "output must be outside the frozen target skill folder", "output": str(output)}

    receipt: Path | None = None
    if receipt_raw:
        authored_receipt = Path(receipt_raw).expanduser()
        try:
            receipt = canonical_future_path(authored_receipt)
        except ValueError as exc:
            return output, None, {"code": "receipt/path-cycle", "error": str(exc)}
        if authored_receipt.suffix.lower() != ".json" or receipt.suffix.lower() != ".json":
            return output, receipt, {"code": "receipt/extension", "error": "receipt must use and resolve to a .json destination", "receipt": str(authored_receipt), "resolved_receipt": str(receipt)}
        if receipt.exists() and not receipt.is_file():
            return output, receipt, {"code": "receipt/not-file", "error": "receipt target must be a file path", "receipt": str(receipt)}
        if path_is_inside(target, receipt):
            return output, receipt, {"code": "receipt/inside-target", "error": "receipt must be outside the frozen target skill folder", "receipt": str(receipt)}
        if paths_alias(output, receipt):
            return output, receipt, {"code": "output/target-alias", "error": "package output and receipt must not alias the same destination", "output": str(output), "receipt": str(receipt)}
    return output, receipt, None


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and recovery-safely build skill.zip for an Agent Skills package.")
    parser.add_argument("--target")
    parser.add_argument("--output")
    parser.add_argument("--profile", choices=["portable", "openai"], default="portable")
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--portability-hosts", help="Optional multi-host matrix required for package acceptance")
    parser.add_argument("--validate-only")
    parser.add_argument("--json-output")
    args = parser.parse_args()

    if args.validate_only:
        archive_path = canonical_future_path(args.validate_only)
        archive = validate_archive(archive_path)
        result = {"receipt_version": 2, "mode": "validate-only", "stage": "archive-validation", "status": archive["status"], "profile": args.profile, "zip_path": str(archive_path), "archive": archive}
        emit_result(result, args.json_output, preserve_existing_on_failure=result["status"] != "pass")
        return 0 if result["status"] == "pass" else 1

    if not args.target or not args.output:
        print("ERROR: --target and --output are required unless --validate-only is used")
        return 2

    target = Path(args.target).expanduser().resolve()
    output, receipt, preflight_error = preflight_package_paths(target, args.output, args.json_output)
    if preflight_error:
        result = {"receipt_version": 2, "mode": "package", "stage": "preflight", "status": "fail", "profile": args.profile, "target": str(target), **preflight_error}
        emit_result(result, None)
        return 1

    folder = validate_folder(target, args.profile, args.portability_hosts) if args.validate else {"status": "not-run", "errors": [], "warnings": [], "host_portability": None}
    if folder["status"] == "fail":
        result = {"receipt_version": 2, "mode": "package", "stage": "validation", "profile": args.profile, "status": "fail", "target": str(target), "output": str(output), "folder": folder, "output_preserved": target_exists(output), "receipt_preserved": bool(receipt and target_exists(receipt))}
        emit_result(result, str(receipt) if receipt else None, preserve_existing_on_failure=True)
        return 1

    staged_zip: Path | None = None
    staged_receipt: Path | None = None
    try:
        staged_zip, package = stage_zip(target, output)
        archive = validate_archive(staged_zip) if args.validate else {"status": "not-run", "errors": [], "warnings": []}
        if archive["status"] == "fail":
            result = {"receipt_version": 2, "mode": "package", "stage": "archive-validation", "profile": args.profile, "status": "fail", "target": str(target), "output": str(output), "folder": folder, "package": package, "archive": archive, "output_preserved": target_exists(output), "receipt_preserved": bool(receipt and target_exists(receipt))}
            staged_zip.unlink(missing_ok=True)
            emit_result(result, str(receipt) if receipt else None, preserve_existing_on_failure=True)
            return 1

        result: dict[str, Any] = {
            "receipt_version": 2,
            "mode": "package",
            "stage": "committed",
            "profile": args.profile,
            "status": "pass",
            "target": str(target),
            "folder": folder,
            "package": package,
            "archive": archive,
            "delivery": {
                "status": "pass",
                "last_good_preserved_on_failure": True,
                "package_receipt_atomic_when_requested": receipt is not None,
                "recovery": [],
                "cleanup_warnings": [],
            },
        }

        staged_targets: list[tuple[Path, Path]] = [(staged_zip, output)]
        if receipt is not None:
            staged_receipt = stage_bytes(receipt.parent, receipt.name, (json.dumps(result, indent=2, sort_keys=True) + "\n").encode("utf-8"))
            staged_targets.append((staged_receipt, receipt))

        delivery = transactional_commit(staged_targets)
        result["delivery"].update(delivery)
        staged_zip = None
        staged_receipt = None

        if receipt is not None and (delivery.get("recovery") or delivery.get("cleanup_warnings")):
            try:
                atomic_write_bytes(receipt, (json.dumps(result, indent=2, sort_keys=True) + "\n").encode("utf-8"))
            except Exception as receipt_update_exc:
                result["delivery"]["receipt_update_warning"] = str(receipt_update_exc)

        emit_result(result, None)
        return 0
    except Exception as exc:
        recovery: list[dict[str, str]] = []
        try:
            parsed = json.loads(str(exc))
            if isinstance(parsed, dict):
                recovery = parsed.get("recovery", [])
        except Exception:
            pass
        if staged_zip is not None and staged_zip.exists():
            recovery.append({"kind": "staged-package", "preserved_at": str(staged_zip)})
        if staged_receipt is not None and staged_receipt.exists():
            recovery.append({"kind": "staged-receipt", "preserved_at": str(staged_receipt)})
        result = {
            "receipt_version": 2,
            "mode": "package",
            "stage": "commit",
            "profile": args.profile,
            "status": "fail",
            "target": str(target),
            "output": str(output),
            "error": str(exc),
            "output_preserved": target_exists(output),
            "receipt_preserved": bool(receipt and target_exists(receipt)),
            "recovery": recovery,
        }
        emit_result(result, None)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
