#!/usr/bin/env python3
"""Build a deterministic evidence identity manifest for a skill review.

The helper never executes target code. It hashes bytes and declared identities only.
It emits no timestamp and no absolute filesystem path so the same inputs/arguments
produce the same JSON across equivalent environments.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Iterable

HOST_PROFILES = ("portable", "openai", "codex", "claude", "copilot", "cursor")


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _tree_sha256(root: Path) -> str:
    digest = hashlib.sha256()
    entries: list[Path] = []
    for path in root.rglob("*"):
        rel = path.relative_to(root)
        if ".git" in rel.parts:
            continue
        if path.is_file() or path.is_symlink():
            entries.append(path)
    for path in sorted(entries, key=lambda p: p.relative_to(root).as_posix()):
        rel = path.relative_to(root).as_posix().encode("utf-8")
        if path.is_symlink():
            payload = os.readlink(path).encode("utf-8", errors="surrogateescape")
            digest.update(b"L\0" + rel + b"\0" + payload + b"\0")
        else:
            file_hash = bytes.fromhex(_file_sha256(path))
            digest.update(b"F\0" + rel + b"\0" + file_hash + b"\0")
    return digest.hexdigest()


def hash_path(path: Path) -> tuple[str, str]:
    path = path.expanduser().resolve()
    if path.is_dir():
        return "directory-tree-sha256", _tree_sha256(path)
    if path.is_file():
        kind = "zip-sha256" if path.suffix.lower() == ".zip" else "file-sha256"
        return kind, _file_sha256(path)
    raise FileNotFoundError(str(path))


def _parse_evaluator(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise ValueError("evaluator must use LABEL=PATH")
    label, raw_path = value.split("=", 1)
    if not label.strip() or not raw_path.strip():
        raise ValueError("evaluator must use non-empty LABEL=PATH")
    return label.strip(), Path(raw_path.strip())


def _parse_source(value: str) -> tuple[str, str, str]:
    parts = value.split("|", 2)
    if len(parts) != 3 or not all(part.strip() for part in parts):
        raise ValueError("source must use LABEL|LOCATOR|IDENTITY")
    return tuple(part.strip() for part in parts)  # type: ignore[return-value]


def build_manifest(
    target: Path,
    reviewer_root: Path,
    host_profiles: Iterable[str],
    spec_baseline: str,
    evaluators: Iterable[tuple[str, Path]],
    sources: Iterable[tuple[str, str, str]],
) -> dict[str, object]:
    target_kind, target_hash = hash_path(target)
    reviewer_kind, reviewer_hash = hash_path(reviewer_root)

    evaluator_rows = []
    for label, path in evaluators:
        kind, digest = hash_path(path)
        evaluator_rows.append({"label": label, "kind": kind, "sha256": digest})
    evaluator_rows.sort(key=lambda row: (row["label"], row["sha256"]))

    source_rows = [
        {"label": label, "locator": locator, "identity": identity}
        for label, locator, identity in sources
    ]
    source_rows.sort(key=lambda row: (row["label"], row["locator"], row["identity"]))

    return {
        "schema_version": "1.0",
        "target": {"kind": target_kind, "sha256": target_hash},
        "reviewer": {"kind": reviewer_kind, "sha256": reviewer_hash},
        "spec_baseline": spec_baseline or "not-supplied",
        "host_profiles": sorted(set(host_profiles)),
        "evaluators": evaluator_rows,
        "sources": source_rows,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build deterministic skill-review evidence identity manifest.")
    parser.add_argument("--target", required=True, help="Skill directory, SKILL.md/file, or ZIP under review")
    parser.add_argument(
        "--reviewer-root",
        default=str(Path(__file__).resolve().parents[1]),
        help="Reviewer package root; default is this skill package",
    )
    parser.add_argument("--host-profile", action="append", choices=HOST_PROFILES, default=[])
    parser.add_argument("--spec-baseline", default="not-supplied")
    parser.add_argument("--evaluator", action="append", default=[], help="Repeatable LABEL=PATH")
    parser.add_argument("--source", action="append", default=[], help="Repeatable LABEL|LOCATOR|IDENTITY")
    parser.add_argument("--json-out", required=True, help="Output path outside the reviewed target")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        evaluators = [_parse_evaluator(value) for value in args.evaluator]
        sources = [_parse_source(value) for value in args.source]
        manifest = build_manifest(
            target=Path(args.target),
            reviewer_root=Path(args.reviewer_root),
            host_profiles=args.host_profile or ["portable"],
            spec_baseline=args.spec_baseline,
            evaluators=evaluators,
            sources=sources,
        )
    except (FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    output = Path(args.json_out).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    output.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
