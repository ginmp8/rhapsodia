#!/usr/bin/env python3
"""Validate and build a ChatGPT skill.zip archive."""
from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path
from typing import Any

TEXT_SUFFIXES = {".md", ".txt", ".yaml", ".yml", ".json", ".py", ".sh", ".template"}
EXCLUDED_DIRS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "reports", "benchmark-reports", "test-results", "tmp"}
EXCLUDED_FILES = {".DS_Store"}
SENSITIVE_RE = re.compile(r"(^|[-_.])(secret|secrets|credential|credentials|token|tokens)([-_.]|$)|private[-_.]?key|^\.env($|\.)", re.I)
REF_RE = re.compile(r"`([^`]+\.(?:md|py|json|yaml|yml|template|txt|sh))`|\[[^\]]+\]\(([^)]+)\)")
MARKER_RE = re.compile(r"\[" + "TO" + "DO|\b" + "TO" + "DO" + r"\s*:|replace" + " with actual|this is a " + "placeholder", re.I)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1")


def frontmatter_errors(skill_md: Path) -> list[str]:
    text = read_text(skill_md) if skill_md.exists() else ""
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        return ["SKILL.md frontmatter block missing"]
    raw = text.split("\n---\n", 1)[0][4:]
    data: dict[str, str] = {}
    current: str | None = None
    for line in raw.splitlines():
        if not line.strip():
            continue
        if re.match(r"^[A-Za-z_][A-Za-z0-9_-]*:\s*", line):
            current, value = line.split(":", 1)
            data[current.strip()] = value.strip().strip('"').strip("'")
        elif current:
            data[current] += " " + line.strip().strip('"').strip("'")
    errors: list[str] = []
    if set(data) != {"name", "description"}:
        errors.append(f"frontmatter keys must be name and description, found {sorted(data)}")
    for key in ("name", "description"):
        value = data.get(key, "")
        if not value:
            errors.append(f"frontmatter {key} is empty")
        elif value != value.lower():
            errors.append(f"frontmatter {key} must be lowercase")
    if data.get("description") and len(data["description"].split()) < 25:
        errors.append("frontmatter description is too short for reliable activation")
    return errors


def normalize_ref(raw: str) -> str | None:
    ref = raw.split("#", 1)[0].strip()
    if not ref or "://" in ref or ref.startswith(("/", "mailto:")) or ".." in Path(ref).parts:
        return None
    return None if any(ch.isspace() for ch in ref) else ref


def skill_refs(skill_text: str) -> set[str]:
    refs: set[str] = set()
    for match in REF_RE.finditer(skill_text):
        ref = normalize_ref(match.group(1) or match.group(2) or "")
        if ref:
            refs.add(ref)
    return refs


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


def validate_folder(target: Path) -> list[str]:
    errors: list[str] = []
    if not target.is_dir():
        return [f"target is not a directory: {target}"]
    skill_files = [p for p in target.rglob("SKILL.md") if p.is_file() and not skip_reason(p.relative_to(target).as_posix())]
    if skill_files != [target / "SKILL.md"]:
        errors.append(f"target must contain exactly one root SKILL.md, found {len(skill_files)}")
    skill_md = target / "SKILL.md"
    errors.extend(frontmatter_errors(skill_md))
    skill_text = read_text(skill_md) if skill_md.exists() else ""
    for ref in sorted(skill_refs(skill_text)):
        if not (target / ref).exists():
            errors.append(f"referenced path missing: {ref}")
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
    return errors


def build_zip(target: Path, output: Path) -> dict[str, Any]:
    files, excluded, _ = package_files(target)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.unlink(missing_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in files:
            rel = path.relative_to(target).as_posix()
            zf.write(path, f"{target.name}/{rel}")
    return {"output": str(output), "file_count": len(files), "excluded": excluded, "size_bytes": output.stat().st_size}


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
            if len(roots) != 1:
                errors.append(f"archive must contain one top-level directory, found {sorted(roots)}")
                root = sorted(roots)[0] if roots else ""
            else:
                root = next(iter(roots))
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
    return {"status": "pass" if not errors else "fail", "errors": errors, "warnings": [], "file_count": len(entries), "size_bytes": zip_path.stat().st_size if zip_path.exists() else 0}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate and build skill.zip for a ChatGPT skill folder.")
    parser.add_argument("--target")
    parser.add_argument("--output")
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--validate-only")
    parser.add_argument("--json-output")
    args = parser.parse_args(argv)
    if args.validate_only:
        archive = validate_archive(Path(args.validate_only).resolve())
        result = {"mode": "validate-only", "zip_path": str(Path(args.validate_only).resolve()), "archive": archive}
        status = archive["status"]
    else:
        if not args.target or not args.output:
            print("ERROR: --target and --output are required unless --validate-only is used", file=sys.stderr)
            return 2
        target, output = Path(args.target).resolve(), Path(args.output).resolve()
        folder_errors = validate_folder(target) if args.validate else []
        if folder_errors:
            result = {"mode": "package", "status": "fail", "target": str(target), "output": str(output), "folder_errors": folder_errors}
            status = "fail"
        else:
            package = build_zip(target, output)
            archive = validate_archive(output) if args.validate else {"status": "not_run"}
            status = "pass" if archive["status"] in {"pass", "not_run"} else "fail"
            result = {"mode": "package", "status": status, "target": str(target), "package": package, "archive": archive}
    if args.json_output:
        out = Path(args.json_output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"wrote {out}")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
