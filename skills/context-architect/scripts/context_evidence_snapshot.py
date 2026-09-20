#!/usr/bin/env python3
"""Capture or verify exact file identities used by a reusable context map."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any

MANIFEST_VERSION = 1


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def normalize_selected_file(root: Path, raw: str) -> tuple[str, Path, str | None]:
    authored = Path(raw)
    candidate = authored if authored.is_absolute() else root / authored
    if not candidate.exists() and not candidate.is_symlink():
        raise ValueError(f"missing evidence path: {raw}")
    if candidate.is_dir():
        raise ValueError(f"evidence path must be a file, not a directory: {raw}")
    resolved = candidate.resolve(strict=True)
    if not is_within(resolved, root):
        raise ValueError(f"evidence path resolves outside repository root: {raw}")
    rel = candidate.absolute().relative_to(root).as_posix()
    link_target = os.readlink(candidate) if candidate.is_symlink() else None
    return rel, resolved, link_target


def git_identity(root: Path, rel_paths: list[str]) -> dict[str, Any]:
    env = dict(os.environ)
    env["LC_ALL"] = "C"
    try:
        head = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
            env=env,
        ).stdout.strip()
    except (FileNotFoundError, subprocess.SubprocessError):
        return {"available": False, "head": None, "selected_dirty": None, "status": []}

    try:
        proc = subprocess.run(
            ["git", "-C", str(root), "status", "--porcelain=v1", "--untracked-files=all", "--", *rel_paths],
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
            env=env,
        )
        status = [line for line in proc.stdout.splitlines() if line.strip()]
    except subprocess.SubprocessError:
        status = []
    return {"available": True, "head": head, "selected_dirty": bool(status), "status": status}


def atomic_json_write(path: Path, payload: dict[str, Any]) -> None:
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


def preflight_manifest_output(root: Path, output: Path) -> Path:
    parent = output.parent.resolve(strict=True) if output.parent.exists() else output.parent.resolve()
    resolved = parent / output.name
    if is_within(resolved, root):
        raise ValueError("evidence manifest must be written outside the repository root")
    return resolved


def capture(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve(strict=True)
    output = preflight_manifest_output(root, Path(args.out).expanduser())
    selected: list[tuple[str, Path, str | None]] = []
    seen: set[str] = set()
    for raw in args.path:
        rel, resolved, link_target = normalize_selected_file(root, raw)
        if rel not in seen:
            selected.append((rel, resolved, link_target))
            seen.add(rel)
    selected.sort(key=lambda item: item[0])
    files = []
    for rel, resolved, link_target in selected:
        files.append(
            {
                "path": rel,
                "size": resolved.stat().st_size,
                "sha256": sha256_file(resolved),
                "symlink_target": link_target,
            }
        )
    git = git_identity(root, [f[0] for f in selected])
    payload = {
        "manifest_version": MANIFEST_VERSION,
        "status": "captured",
        "root_name": root.name,
        "git": git,
        "files": files,
    }
    atomic_json_write(output, payload)
    print(json.dumps({"status": "pass", "manifest": str(output), "file_count": len(files)}, sort_keys=True))
    return 0


def verify(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve(strict=True)
    manifest_path = Path(args.manifest).resolve(strict=True)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    diagnostics: list[dict[str, Any]] = []
    rel_paths = [item["path"] for item in manifest.get("files", [])]

    current_git = git_identity(root, rel_paths)
    expected_git = manifest.get("git", {})
    if expected_git.get("available") and current_git.get("available") and expected_git.get("head") != current_git.get("head"):
        diagnostics.append(
            {
                "code": "repository_revision_changed",
                "subject": "git.head",
                "expected": expected_git.get("head"),
                "actual": current_git.get("head"),
            }
        )

    for item in manifest.get("files", []):
        rel = item.get("path")
        if not isinstance(rel, str) or not rel:
            diagnostics.append({"code": "invalid_manifest_path", "subject": str(rel)})
            continue
        authored = root / rel
        if not authored.exists() and not authored.is_symlink():
            diagnostics.append({"code": "evidence_file_missing", "subject": rel})
            continue
        try:
            resolved = authored.resolve(strict=True)
        except OSError as exc:
            diagnostics.append({"code": "evidence_path_unresolvable", "subject": rel, "evidence": str(exc)})
            continue
        if not is_within(resolved, root):
            diagnostics.append({"code": "evidence_path_escaped_root", "subject": rel})
            continue
        actual_link_target = os.readlink(authored) if authored.is_symlink() else None
        if actual_link_target != item.get("symlink_target"):
            diagnostics.append(
                {
                    "code": "symlink_target_changed",
                    "subject": rel,
                    "expected": item.get("symlink_target"),
                    "actual": actual_link_target,
                }
            )
        actual_hash = sha256_file(resolved)
        if actual_hash != item.get("sha256"):
            diagnostics.append(
                {
                    "code": "evidence_hash_changed",
                    "subject": rel,
                    "expected": item.get("sha256"),
                    "actual": actual_hash,
                }
            )
        actual_size = resolved.stat().st_size
        if actual_size != item.get("size"):
            diagnostics.append(
                {
                    "code": "evidence_size_changed",
                    "subject": rel,
                    "expected": item.get("size"),
                    "actual": actual_size,
                }
            )

    report = {
        "status": "pass" if not diagnostics else "stale",
        "root_name": root.name,
        "manifest": str(manifest_path),
        "diagnostics": diagnostics,
    }
    if args.json_output:
        atomic_json_write(Path(args.json_output), report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if not diagnostics else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    capture_parser = sub.add_parser("capture", help="Capture selected evidence file hashes.")
    capture_parser.add_argument("--root", required=True, help="Repository root.")
    capture_parser.add_argument("--path", action="append", required=True, help="Evidence file path; repeat as needed.")
    capture_parser.add_argument("--out", required=True, help="Manifest path outside the repository root.")
    capture_parser.set_defaults(func=capture)

    verify_parser = sub.add_parser("verify", help="Verify repository evidence against a prior manifest.")
    verify_parser.add_argument("--root", required=True, help="Repository root to verify.")
    verify_parser.add_argument("--manifest", required=True, help="Previously captured manifest.")
    verify_parser.add_argument("--json", dest="json_output", help="Optional machine-readable verification report path.")
    verify_parser.set_defaults(func=verify)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
