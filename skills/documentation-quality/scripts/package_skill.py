#!/usr/bin/env python3
"""Validate and package a skill folder as a deterministic skill.zip.

This maintenance-only helper stages and validates the archive, binds it to a
candidate tree hash in a durable receipt, rejects output aliases inside the
source skill, and preserves last-good outputs if commit fails.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import uuid
import zipfile
from pathlib import Path

MAX_ZIP_BYTES = 25 * 1024 * 1024
EXCLUDED_PARTS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}
RECEIPT_NAME = "skill.zip.receipt.json"


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    _, yaml_part, _ = text.split("---", 2)
    data: dict[str, str] = {}
    for line in yaml_part.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"\'')
    return data


def validate_skill_folder(skill_path: Path) -> list[str]:
    errors: list[str] = []
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return ["SKILL.md is missing"]
    frontmatter = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
    if set(frontmatter) != {"name", "description"}:
        errors.append("frontmatter must contain only name and description")
    if not frontmatter.get("name"):
        errors.append("frontmatter name is empty")
    if not frontmatter.get("description"):
        errors.append("frontmatter description is empty")
    if frontmatter.get("name", "") != frontmatter.get("name", "").lower():
        errors.append("frontmatter name must be lowercase")
    if frontmatter.get("description", "") != frontmatter.get("description", "").lower():
        errors.append("frontmatter description must be lowercase")
    return errors


def should_include(path: Path) -> bool:
    if any(part in EXCLUDED_PARTS for part in path.parts):
        return False
    if path.suffix in EXCLUDED_SUFFIXES:
        return False
    if path.name in {"skill.zip", RECEIPT_NAME}:
        return False
    return True


def package_files(skill_path: Path) -> list[Path]:
    return [
        path
        for path in sorted(skill_path.rglob("*"))
        if path.is_file() and should_include(path.relative_to(skill_path))
    ]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def candidate_sha256(skill_path: Path) -> str:
    digest = hashlib.sha256()
    for file_path in package_files(skill_path):
        relative = file_path.relative_to(skill_path).as_posix().encode("utf-8")
        content = file_path.read_bytes()
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    return digest.hexdigest()


NOISE_DIRS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}


def source_tree_sha256(skill_path: Path) -> str:
    rows: list[dict[str, object]] = []
    for path in sorted(skill_path.rglob("*")):
        relative = path.relative_to(skill_path)
        if any(part in NOISE_DIRS for part in relative.parts):
            continue
        if not path.is_file():
            continue
        rows.append(
            {
                "path": relative.as_posix(),
                "type": "file",
                "size": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    payload = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def is_inside(parent: Path, child: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def validate_output_paths(skill_path: Path, output_dir: Path) -> None:
    skill_path = skill_path.resolve()
    output_dir = output_dir.resolve()
    if is_inside(skill_path, output_dir):
        raise ValueError("output directory must be outside the skill folder")


def write_deterministic_zip(skill_path: Path, zip_path: Path) -> None:
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for file_path in package_files(skill_path):
            archive_name = file_path.relative_to(skill_path.parent).as_posix()
            info = zipfile.ZipInfo(archive_name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, file_path.read_bytes())


def validate_staged_archive(zip_path: Path) -> None:
    size = zip_path.stat().st_size
    if size > MAX_ZIP_BYTES:
        raise ValueError(f"skill.zip exceeds 25 MiB upload limit: {size} bytes")
    with zipfile.ZipFile(zip_path, "r") as archive:
        bad_member = archive.testzip()
        if bad_member is not None:
            raise ValueError(f"staged archive failed integrity check at: {bad_member}")


def atomic_commit_pair(
    staged_zip: Path,
    staged_receipt: Path,
    zip_path: Path,
    receipt_path: Path,
) -> None:
    token = uuid.uuid4().hex
    zip_backup = zip_path.with_name(f".{zip_path.name}.{token}.last-good")
    receipt_backup = receipt_path.with_name(f".{receipt_path.name}.{token}.last-good")
    zip_had_previous = zip_path.exists()
    receipt_had_previous = receipt_path.exists()

    try:
        if zip_had_previous:
            os.replace(zip_path, zip_backup)
        if receipt_had_previous:
            os.replace(receipt_path, receipt_backup)
        os.replace(staged_zip, zip_path)
        os.replace(staged_receipt, receipt_path)
    except Exception as exc:
        recovery_paths: list[str] = []
        try:
            if zip_path.exists():
                zip_path.unlink()
            if zip_had_previous and zip_backup.exists():
                os.replace(zip_backup, zip_path)
        except Exception:
            if zip_backup.exists():
                recovery_paths.append(str(zip_backup))
        try:
            if receipt_path.exists():
                receipt_path.unlink()
            if receipt_had_previous and receipt_backup.exists():
                os.replace(receipt_backup, receipt_path)
        except Exception:
            if receipt_backup.exists():
                recovery_paths.append(str(receipt_backup))
        suffix = f"; recovery paths: {recovery_paths}" if recovery_paths else ""
        raise RuntimeError(f"atomic package commit failed{suffix}") from exc
    else:
        for backup in (zip_backup, receipt_backup):
            if backup.exists():
                backup.unlink()


def package_skill(skill_path: Path, output_dir: Path) -> Path:
    skill_path = skill_path.resolve()
    output_dir = output_dir.resolve()
    if not skill_path.is_dir():
        raise ValueError(f"target is not a directory: {skill_path}")
    validate_output_paths(skill_path, output_dir)
    errors = validate_skill_folder(skill_path)
    if errors:
        raise ValueError("; ".join(errors))

    output_dir.mkdir(parents=True, exist_ok=True)
    zip_path = output_dir / "skill.zip"
    receipt_path = output_dir / RECEIPT_NAME
    token = uuid.uuid4().hex
    staged_zip = output_dir / f".skill.zip.{token}.staged"
    staged_receipt = output_dir / f".{RECEIPT_NAME}.{token}.staged"

    try:
        write_deterministic_zip(skill_path, staged_zip)
        validate_staged_archive(staged_zip)
        receipt = {
            "receipt_version": 1,
            "status": "pass",
            "stage": "committed",
            "candidate_sha256": candidate_sha256(skill_path),
            "source_tree_sha256": source_tree_sha256(skill_path),
            "archive_sha256": sha256_file(staged_zip),
            "archive_size_bytes": staged_zip.stat().st_size,
            "archive_name": zip_path.name,
            "recovery_paths": [],
        }
        staged_receipt.write_text(
            json.dumps(receipt, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        atomic_commit_pair(staged_zip, staged_receipt, zip_path, receipt_path)
    finally:
        for staged in (staged_zip, staged_receipt):
            if staged.exists():
                staged.unlink()

    return zip_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and package a skill folder as skill.zip")
    parser.add_argument("skill_path", help="Path to the skill folder")
    parser.add_argument("output_dir", nargs="?", default=".", help="Directory where skill.zip will be written")
    args = parser.parse_args()
    skill_path = Path(args.skill_path).resolve()
    if not skill_path.is_dir():
        print(f"target is not a directory: {skill_path}", file=sys.stderr)
        return 2
    try:
        zip_path = package_skill(skill_path, Path(args.output_dir).resolve())
    except Exception as exc:
        print(f"package failed: {exc}", file=sys.stderr)
        return 1
    print(str(zip_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
