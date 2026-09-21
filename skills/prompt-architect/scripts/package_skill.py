#!/usr/bin/env python3
"""Deterministically package a skill with atomic delivery and a SHA-256 receipt."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

MAX_BYTES = 25 * 1024 * 1024
EXCLUDED_PARTS = {".git", "__pycache__", ".pytest_cache"}
EXCLUDED_SUFFIXES = {".pyc", ".zip"}
FIXED_ZIP_TIME = (1980, 1, 1, 0, 0, 0)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_frontmatter(skill_md: Path) -> dict[str, str]:
    text = skill_md.read_text(encoding="utf-8")
    match = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.DOTALL)
    if not match:
        raise ValueError("SKILL.md must start with YAML frontmatter")
    data: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"\'')
    return data


def validate_skill(skill_dir: Path) -> dict[str, str]:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        raise ValueError("SKILL.md not found")
    meta = read_frontmatter(skill_md)
    name = meta.get("name", "")
    description = meta.get("description", "")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        raise ValueError("frontmatter name must be lowercase hyphen-case")
    if len(description.split()) < 12:
        raise ValueError("frontmatter description is too short")
    if any(part in description for part in "<>"):
        raise ValueError("frontmatter description cannot contain angle brackets")
    return {"name": name, "description": description}


def iter_package_files(skill_dir: Path):
    for path in sorted(skill_dir.rglob("*"), key=lambda p: p.as_posix()):
        if path.is_symlink():
            raise ValueError(f"symlinks are not allowed in deterministic package: {path}")
        if not path.is_file():
            continue
        rel = path.relative_to(skill_dir)
        if any(part in EXCLUDED_PARTS for part in rel.parts):
            continue
        if path.suffix.lower() in EXCLUDED_SUFFIXES:
            continue
        yield path


def canonical_child(parent: Path, child: Path) -> Path:
    parent = parent.resolve()
    child = child.resolve(strict=False)
    try:
        child.relative_to(parent)
    except ValueError as exc:
        raise ValueError(f"output escapes output directory: {child}") from exc
    return child


def write_deterministic_zip(skill_dir: Path, out: Path) -> list[dict[str, object]]:
    manifest: list[dict[str, object]] = []
    root_name = skill_dir.name
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in iter_package_files(skill_dir):
            rel = path.relative_to(skill_dir).as_posix()
            arcname = f"{root_name}/{rel}"
            data = path.read_bytes()
            info = zipfile.ZipInfo(arcname, FIXED_ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            info.create_system = 3
            zf.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
            manifest.append({"path": rel, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    return manifest


def atomic_json(path: Path, payload: dict) -> None:
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False, sort_keys=True)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_name, path)
    except Exception:
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass
        raise



def validate_package_contract(skill_dir: Path) -> None:
    validator = skill_dir / "scripts" / "validate_skill.py"
    if not validator.is_file():
        raise ValueError("scripts/validate_skill.py not found")
    result = subprocess.run([sys.executable, str(validator), "--target", str(skill_dir)], text=True, capture_output=True)
    if result.returncode != 0:
        detail = (result.stdout + result.stderr).strip()
        raise ValueError(f"package validation failed: {detail}")


def package(skill_dir: Path, output_dir: Path) -> tuple[Path, Path]:
    skill_dir = skill_dir.resolve()
    if not skill_dir.is_dir():
        raise ValueError("skill_dir must be a directory")
    meta = validate_skill(skill_dir)
    validate_package_contract(skill_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
    output_dir = output_dir.resolve()
    out = canonical_child(output_dir, output_dir / "skill.zip")
    receipt = canonical_child(output_dir, output_dir / "skill.receipt.json")
    last_good = canonical_child(output_dir, output_dir / "skill.last-good.zip")

    # Never allow an output to alias the input tree.
    try:
        out.relative_to(skill_dir)
        raise ValueError("skill.zip cannot be written inside the target skill tree")
    except ValueError as exc:
        if str(exc) == "skill.zip cannot be written inside the target skill tree":
            raise

    fd, tmp_name = tempfile.mkstemp(prefix=".skill.", suffix=".zip.tmp", dir=output_dir)
    os.close(fd)
    tmp = Path(tmp_name)
    previous_backup_created = False
    try:
        manifest = write_deterministic_zip(skill_dir, tmp)
        size = tmp.stat().st_size
        if size > MAX_BYTES:
            raise ValueError(f"skill.zip exceeds 25 MB limit: {size} bytes")
        # Verify archive readability before touching last-good/current outputs.
        with zipfile.ZipFile(tmp, "r") as zf:
            bad = zf.testzip()
            if bad is not None:
                raise ValueError(f"zip CRC validation failed at {bad}")

        package_sha = sha256_file(tmp)
        payload = {
            "receipt_version": 1,
            "skill": meta["name"],
            "file_count": len(manifest),
            "package_bytes": size,
            "package_sha256": package_sha,
            "files": manifest,
            "delivery": {
                "atomic_replace": True,
                "last_good_preserved": out.exists(),
            },
        }

        if out.exists():
            shutil.copy2(out, last_good)
            previous_backup_created = True
        os.replace(tmp, out)
        try:
            atomic_json(receipt, payload)
        except Exception:
            if previous_backup_created and last_good.exists():
                os.replace(last_good, out)
            raise
        return out, receipt
    finally:
        if tmp.exists():
            tmp.unlink()


def main() -> int:
    parser = argparse.ArgumentParser(description="Package a skill folder as deterministic skill.zip")
    parser.add_argument("skill_dir")
    parser.add_argument("output_dir")
    args = parser.parse_args()
    try:
        out, receipt = package(Path(args.skill_dir), Path(args.output_dir))
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(out)
    print(receipt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
