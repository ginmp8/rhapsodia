#!/usr/bin/env python3
"""Generate or check a deterministic scoped RhapsodIA source manifest.

The scope is exactly the release archive's package_policy.files selection,
excluding separate agent and release/research report identities.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import unicodedata

import package_policy

ROOT = Path(__file__).resolve().parents[1]
VERSION_RE = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+")
SCHEMA = "release-source-manifest/v1"
ALGORITHM = "sha256(canonical sorted-key compact UTF-8 JSON files array)"
SCOPE = ("Release-eligible source files from scripts/package_policy.py, excluding "
         "MANIFEST.json, docs/releases/ and docs/research/; .zip and caches are excluded by release policy.")


def render(root: Path) -> dict:
    items = []
    portable_names: set[str] = set()
    for file in package_policy.files(root):
        rel = file.relative_to(root).as_posix()
        if rel == "MANIFEST.json" or rel.startswith(("docs/releases/", "docs/research/")):
            continue
        norm = unicodedata.normalize("NFC", rel).casefold()
        if norm in portable_names:
            raise ValueError("portable path collision in release source: " + rel)
        portable_names.add(norm)
        items.append({"path": rel, "sha256": hashlib.sha256(file.read_bytes()).hexdigest()})
    items.sort(key=lambda item: item["path"])
    canonical = json.dumps(items, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return {"schema": SCHEMA, "algorithm": ALGORITHM, "scope": SCOPE,
            "sha256": hashlib.sha256(canonical).hexdigest(), "files": items}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", required=True)
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--check", action="store_true", help="compare exact expected JSON bytes; default")
    action.add_argument("--write", action="store_true", help="write a missing versioned source manifest")
    parser.add_argument("--replace", action="store_true", help="explicitly replace an existing manifest with --write")
    args = parser.parse_args()
    if not VERSION_RE.fullmatch(args.version):
        parser.error("version must be exactly MAJOR.MINOR.PATCH")
    if args.replace and not args.write:
        parser.error("--replace requires --write")
    target = ROOT / "docs" / "releases" / f"source-manifest-{args.version}.json"
    expected = render(ROOT)
    output = (json.dumps(expected, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    if target.is_symlink():
        raise ValueError("refusing symlink manifest")
    if args.write:
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and target.read_bytes() != output and not args.replace:
            raise ValueError("manifest exists with different bytes; --replace must be explicit")
        descriptor, temporary = tempfile.mkstemp(prefix=".source-manifest-", dir=target.parent)
        try:
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(output)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, target)
        finally:
            Path(temporary).unlink(missing_ok=True)
    elif not target.is_file() or target.read_bytes() != output:
        print(json.dumps({"status": "fail", "reason": "source_manifest_out_of_sync",
                          "file": str(target.relative_to(ROOT)),
                          "expected_identity": expected["sha256"]}))
        return 1
    print(json.dumps({"status": "pass", "version": args.version, "file_count": len(expected["files"]),
                      "source_manifest_sha256": expected["sha256"], "action": "write" if args.write else "check"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
