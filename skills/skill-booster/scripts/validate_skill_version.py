#!/usr/bin/env python3
"""Validate portable skill release identity and optional immutable baseline."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

SEMVER_RE = re.compile(
    r"(?P<major>0|[1-9][0-9]*)\."
    r"(?P<minor>0|[1-9][0-9]*)\."
    r"(?P<patch>0|[1-9][0-9]*)"
    r"(?:-(?P<pre>[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
    r"(?:\+(?P<build>[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
)
EXCLUDED_DIRS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "dist", "build"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo", ".zip"}


def parse_semver(value: str) -> tuple[tuple[int, int, int], tuple[str, ...] | None] | None:
    matched = SEMVER_RE.fullmatch(value)
    if not matched:
        return None
    pre = matched.group("pre")
    if pre is not None:
        parts = pre.split(".")
        if any(part.isascii() and part.isdigit() and len(part) > 1 and part.startswith("0") for part in parts):
            return None
    return (
        tuple(int(matched.group(key)) for key in ("major", "minor", "patch")),
        tuple(pre.split(".")) if pre is not None else None,
    )


def compare_semver(left: str, right: str) -> int:
    """SemVer 2.0.0 precedence; build metadata intentionally does not decide order."""
    lp = parse_semver(left)
    rp = parse_semver(right)
    if lp is None or rp is None:
        raise ValueError("compare_semver requires valid SemVer values")
    lc, lpre = lp
    rc, rpre = rp
    if lc != rc:
        return 1 if lc > rc else -1
    if lpre is None or rpre is None:
        return (0 if lpre is rpre else (1 if lpre is None else -1))
    for lpart, rpart in zip(lpre, rpre):
        if lpart == rpart:
            continue
        lnum = lpart.isascii() and lpart.isdigit()
        rnum = rpart.isascii() and rpart.isdigit()
        if lnum and rnum:
            return 1 if int(lpart) > int(rpart) else -1
        if lnum != rnum:
            return -1 if lnum else 1
        return 1 if lpart > rpart else -1
    return (len(lpre) > len(rpre)) - (len(lpre) < len(rpre))


def read_version(root: Path, errors: list[str], *, label: str) -> str | None:
    path = root / "VERSION"
    if path.is_symlink() or not path.is_file():
        errors.append(f"{label}: missing regular root VERSION file")
        return None
    try:
        raw = path.read_bytes()
        value = raw.decode("ascii").removesuffix("\n").removesuffix("\r")
    except (UnicodeDecodeError, OSError) as exc:
        errors.append(f"{label}: VERSION must be readable ASCII SemVer: {exc}")
        return None
    if raw not in {value.encode("ascii"), (value + "\n").encode("ascii"), (value + "\r\n").encode("ascii")}:
        errors.append(f"{label}: VERSION must contain exactly one SemVer value and optional final newline")
        return None
    if parse_semver(value) is None:
        errors.append(f"{label}: VERSION is not SemVer 2.0.0: {value!r}")
        return None
    return value


def tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root)
        if any(part in EXCLUDED_DIRS for part in rel.parts) or rel.suffix in EXCLUDED_SUFFIXES:
            continue
        if path.is_file() and not path.is_symlink():
            digest.update(rel.as_posix().encode("utf-8") + b"\0")
            digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def validate(root: Path, baseline: Path | None = None) -> dict:
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    if not root.is_dir():
        return {"status": "fail", "version": None, "baseline_version": None, "errors": [f"not a directory: {root}"], "warnings": []}
    version = read_version(root, errors, label="candidate")
    changelog = root / "CHANGELOG.md"
    if changelog.is_symlink() or not changelog.is_file():
        errors.append("missing regular root CHANGELOG.md file")
    elif version:
        content = changelog.read_text(encoding="utf-8")
        heading = re.compile(r"^## \[" + re.escape(version) + r"\](?:\s+-\s+\d{4}-\d{2}-\d{2})?\s*$", re.MULTILINE)
        if len(heading.findall(content)) != 1:
            errors.append(f"CHANGELOG.md must have exactly one release heading '## [{version}]' (optional ISO date)")
    notes = root / "RELEASE_NOTES.md"
    if notes.exists() and version:
        if notes.is_symlink() or not notes.is_file():
            errors.append("RELEASE_NOTES.md must be a regular file when present")
        elif not re.search(r"(?<![0-9A-Za-z.+-])" + re.escape(version) + r"(?![0-9A-Za-z.+-])", "\n".join(notes.read_text(encoding="utf-8").splitlines()[:25])):
            errors.append(f"RELEASE_NOTES.md must identify current version {version} within its first 25 lines")
    manifest = root / "release.json"
    if manifest.exists():
        try:
            if manifest.is_symlink() or not manifest.is_file():
                raise ValueError("not a regular file")
            declared = json.loads(manifest.read_text(encoding="utf-8"))
            if not isinstance(declared, dict) or not isinstance(declared.get("version"), str):
                errors.append("release.json must declare a string version")
            elif version and declared["version"] != version:
                errors.append(f"release.json version {declared['version']!r} differs from VERSION {version!r}")
        except (OSError, ValueError) as exc:
            errors.append(f"invalid release.json: {exc}")

    previous = None
    baseline_changed = None
    if baseline is not None:
        baseline = baseline.resolve()
        if not baseline.is_dir() or baseline == root:
            errors.append("baseline must be an existing, separate, immutable skill directory")
        else:
            old_path = baseline / "VERSION"
            if old_path.is_file() and not old_path.is_symlink():
                previous = read_version(baseline, errors, label="baseline")
            else:
                warnings.append("baseline has no VERSION; this is first tracked version, not proof of prior release history")
            baseline_changed = tree_digest(root) != tree_digest(baseline)
            if previous and version:
                cmp = compare_semver(version, previous)
                if cmp < 0:
                    errors.append(f"VERSION decreased from {previous} to {version}")
                elif baseline_changed and cmp == 0:
                    errors.append(f"published package contents changed but VERSION did not advance beyond {previous}")
    return {
        "status": "pass" if not errors else "fail", "version": version,
        "baseline_version": previous, "baseline_changed": baseline_changed,
        "errors": sorted(set(errors)), "warnings": sorted(set(warnings)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate skill VERSION, release documentation and optional baseline bump.")
    parser.add_argument("--target", required=True)
    parser.add_argument("--baseline", help="Immutable extracted prior skill directory for monotonic bump checks")
    args = parser.parse_args()
    report = validate(Path(args.target), Path(args.baseline) if args.baseline else None)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
