#!/usr/bin/env python3
"""Build and validate an installable ChatGPT skill zip package."""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path
from typing import Any

TEXT_SUFFIXES = {".md", ".txt", ".yaml", ".yml", ".json", ".py", ".sh", ".toml"}
ARCHIVE_TEXT_SUFFIXES = TEXT_SUFFIXES | {".template"}
LOCAL_REF_RE = re.compile(r"`([^`]+\.(?:md|py|sh|yaml|yml|json|template|txt))`")
MD_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
MARKER_PATTERNS = [
    re.compile(r"\[" + "TO" + "DO", re.IGNORECASE),
    re.compile(r"\b" + "TO" + "DO" + r"\s*:", re.IGNORECASE),
    re.compile("replace with " + "actual", re.IGNORECASE),
    re.compile("this is a " + "placeholder", re.IGNORECASE),
]
EXCLUDED_DIR_NAMES = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "tmp",
    ".tmp",
    "reports",
    "test-results",
    "benchmark-reports",
}
EXCLUDED_FILE_NAMES = {
    ".DS_Store",
    "test-results.json",
    "hardening-audit.json",
}
SENSITIVE_NAME_PATTERNS = [
    re.compile(r"(^|[-_.])secret(s)?($|[-_.])", re.IGNORECASE),
    re.compile(r"(^|[-_.])credential(s)?($|[-_.])", re.IGNORECASE),
    re.compile(r"(^|[-_.])token(s)?($|[-_.])", re.IGNORECASE),
    re.compile(r"private[-_.]?key", re.IGNORECASE),
    re.compile(r"^\.env($|\.)", re.IGNORECASE),
]


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1")


def parse_frontmatter(text: str) -> tuple[dict[str, str], list[str]]:
    errors: list[str] = []
    if not text.startswith("---\n"):
        return {}, ["SKILL.md missing opening frontmatter fence"]
    end = text.find("\n---", 4)
    if end == -1:
        return {}, ["SKILL.md missing closing frontmatter fence"]
    raw_lines = text[4:end].strip().splitlines()
    data: dict[str, str] = {}
    current_key: str | None = None
    for line in raw_lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if re.match(r"^[A-Za-z_][A-Za-z0-9_-]*:\s*", line):
            key, value = line.split(":", 1)
            current_key = key.strip()
            data[current_key] = value.strip().strip('"').strip("'")
        elif current_key:
            data[current_key] += " " + stripped.strip('"').strip("'")
        else:
            errors.append(f"unparseable frontmatter line: {stripped}")
    return data, errors


def validate_frontmatter(text: str) -> list[str]:
    data, errors = parse_frontmatter(text)
    keys = set(data)
    expected = {"name", "description"}
    if keys != expected:
        errors.append(f"frontmatter keys must be exactly {sorted(expected)}, found {sorted(keys)}")
    for key in expected:
        value = data.get(key, "")
        if not value:
            errors.append(f"frontmatter {key} is empty")
        elif value != value.lower():
            errors.append(f"frontmatter {key} must be lowercase")
    if data.get("description") and len(data["description"].split()) < 25:
        errors.append("frontmatter description is too short for reliable activation")
    return errors


def normalize_ref(raw: str) -> str | None:
    ref = raw.strip().split("#", 1)[0].strip()
    if not ref or "://" in ref or ref.startswith("mailto:"):
        return None
    if ref.startswith("/") or ".." in Path(ref).parts:
        return None
    if any(ch.isspace() for ch in ref):
        return None
    return ref


def extract_refs(text: str) -> set[str]:
    refs: set[str] = set()
    for match in MD_LINK_RE.finditer(text):
        ref = normalize_ref(match.group(1))
        if ref:
            refs.add(ref)
    for match in LOCAL_REF_RE.finditer(text):
        ref = normalize_ref(match.group(1))
        if ref:
            refs.add(ref)
    return refs


def is_sensitive_name(name: str) -> bool:
    return any(pattern.search(name) for pattern in SENSITIVE_NAME_PATTERNS)


def should_exclude(rel_path: str) -> tuple[bool, str | None]:
    parts = Path(rel_path).parts
    if any(part in EXCLUDED_DIR_NAMES for part in parts[:-1]):
        return True, "excluded directory"
    name = parts[-1]
    if name in EXCLUDED_FILE_NAMES or name.endswith(("~", ".swp", ".swo")):
        return True, "excluded file"
    if is_sensitive_name(name):
        return True, "sensitive-looking file name"
    return False, None


def iter_package_files(target: Path) -> tuple[list[Path], list[dict[str, str]]]:
    files: list[Path] = []
    excluded: list[dict[str, str]] = []
    for path in sorted(target.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(target).as_posix()
        skip, reason = should_exclude(rel)
        if skip:
            excluded.append({"path": rel, "reason": reason or "excluded"})
            continue
        files.append(path)
    return files, excluded


def scan_folder_markers(target: Path, files: list[Path]) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    for path in files:
        rel = path.relative_to(target).as_posix()
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if rel.startswith("assets/templates/"):
            continue
        text = read_text(path)
        for line_no, line in enumerate(text.splitlines(), start=1):
            if "re.compile" in line:
                continue
            if any(pattern.search(line) for pattern in MARKER_PATTERNS):
                hits.append({"path": rel, "line": line_no, "text": line.strip()[:160]})
    return hits


def validate_folder(target: Path) -> list[str]:
    errors: list[str] = []
    if not target.exists() or not target.is_dir():
        return [f"target is not a directory: {target}"]
    skill_files = [p for p in target.rglob("SKILL.md") if p.is_file()]
    if len(skill_files) != 1 or skill_files[0].parent != target:
        errors.append(f"target must contain exactly one root SKILL.md, found {len(skill_files)}")
    skill_md = target / "SKILL.md"
    if skill_md.exists():
        skill_text = read_text(skill_md)
        errors.extend(validate_frontmatter(skill_text))
        refs = extract_refs(skill_text)
        for ref in sorted(refs):
            candidate = target / ref
            if not candidate.exists():
                errors.append(f"referenced path missing: {ref}")
    files, _ = iter_package_files(target)
    if not files:
        errors.append("no packageable files found")
    errors.extend([f"residual scaffold marker: {hit['path']}:{hit['line']}" for hit in scan_folder_markers(target, files)])
    return errors


def build_package(target: Path, output: Path) -> dict[str, Any]:
    files, excluded = iter_package_files(target)
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()
    root_name = target.name
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file_path in files:
            rel = file_path.relative_to(target).as_posix()
            zf.write(file_path, f"{root_name}/{rel}")
    return {
        "output": str(output),
        "file_count": len(files),
        "excluded": excluded,
        "size_bytes": output.stat().st_size,
    }


def read_archive_text(zf: zipfile.ZipFile, name: str) -> str:
    data = zf.read(name)
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("latin-1")


def validate_archive(zip_path: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    entries: list[str] = []
    if not zip_path.exists() or not zip_path.is_file():
        return {"status": "fail", "errors": [f"zip does not exist: {zip_path}"], "warnings": [], "file_count": 0}
    try:
        with zipfile.ZipFile(zip_path) as zf:
            bad_member = zf.testzip()
            if bad_member:
                errors.append(f"corrupt archive member: {bad_member}")
            entries = sorted(name for name in zf.namelist() if not name.endswith("/"))
            if not entries:
                errors.append("archive has no files")
                return {"status": "fail", "errors": errors, "warnings": warnings, "file_count": 0}
            top_levels = {name.split("/", 1)[0] for name in entries}
            if len(top_levels) != 1:
                errors.append(f"archive must contain exactly one top-level skill directory, found {sorted(top_levels)}")
            root = sorted(top_levels)[0]
            skill_name = f"{root}/SKILL.md"
            if skill_name not in entries:
                errors.append("archive missing root SKILL.md")
            for entry in entries:
                rel = entry.split("/", 1)[1] if "/" in entry else entry
                if entry.startswith("/") or ".." in Path(entry).parts:
                    errors.append(f"unsafe archive path: {entry}")
                skip, reason = should_exclude(rel)
                if skip:
                    errors.append(f"blocked path included: {entry} ({reason})")
            if skill_name in entries:
                skill_text = read_archive_text(zf, skill_name)
                errors.extend(validate_frontmatter(skill_text))
                entry_set = set(entries)
                for ref in sorted(extract_refs(skill_text)):
                    archived_ref = f"{root}/{ref}"
                    if archived_ref not in entry_set and not any(item.startswith(archived_ref.rstrip("/") + "/") for item in entry_set):
                        errors.append(f"referenced path missing from archive: {ref}")
            for entry in entries:
                rel = entry.split("/", 1)[1] if "/" in entry else entry
                suffix = Path(entry).suffix.lower()
                if suffix not in ARCHIVE_TEXT_SUFFIXES or rel.startswith("assets/templates/"):
                    continue
                text = read_archive_text(zf, entry)
                for line_no, line in enumerate(text.splitlines(), start=1):
                    if "re.compile" in line:
                        continue
                    if any(pattern.search(line) for pattern in MARKER_PATTERNS):
                        errors.append(f"residual scaffold marker in archive: {rel}:{line_no}")
    except zipfile.BadZipFile:
        errors.append("archive is not a readable zip file")
    return {
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "warnings": warnings,
        "file_count": len(entries),
        "size_bytes": zip_path.stat().st_size if zip_path.exists() else 0,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build and validate a ChatGPT skill package zip.")
    parser.add_argument("--target", help="Path to the target skill folder.")
    parser.add_argument("--output", help="Path to write skill.zip.")
    parser.add_argument("--validate", action="store_true", help="Validate the folder before packaging and the zip after packaging.")
    parser.add_argument("--validate-only", help="Validate an existing package zip without creating a new one.")
    parser.add_argument("--json-output", help="Optional JSON evidence output path.")
    args = parser.parse_args(argv)

    result: dict[str, Any]
    if args.validate_only:
        zip_path = Path(args.validate_only).resolve()
        archive_result = validate_archive(zip_path)
        result = {"mode": "validate-only", "archive": archive_result, "zip_path": str(zip_path)}
        status = archive_result["status"]
    else:
        if not args.target or not args.output:
            print("ERROR: --target and --output are required unless --validate-only is used", file=sys.stderr)
            return 2
        target = Path(args.target).resolve()
        output = Path(args.output).resolve()
        folder_errors = validate_folder(target) if args.validate else []
        if folder_errors:
            result = {"mode": "package", "status": "fail", "folder_errors": folder_errors, "target": str(target), "output": str(output)}
            status = "fail"
        else:
            package_info = build_package(target, output)
            archive_result = validate_archive(output) if args.validate else {"status": "not_run"}
            status = "pass" if archive_result.get("status") in {"pass", "not_run"} else "fail"
            result = {
                "mode": "package",
                "status": status,
                "target": str(target),
                "package": package_info,
                "archive": archive_result,
            }
    if args.json_output:
        out = Path(args.json_output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"wrote {out}")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
