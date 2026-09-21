#!/usr/bin/env python3
"""Deterministic, read-only cleanup inventory with conservative reference tracing."""

from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
import ast
import hashlib
import json
import os
import posixpath
import re
from pathlib import Path, PurePosixPath
from typing import Any

CANONICAL_STATES = (
    "used",
    "integrable",
    "duplicate",
    "obsolete",
    "generated",
    "blocked",
    "unknown",
)

PROTECTED_PARTS = {
    ".git",
    ".hg",
    ".svn",
    "fixtures",
    "fixture",
    "expected",
    "expected-output",
    "expected-outputs",
    "golden",
    "snapshots",
    "snapshot",
    "evidence",
    "benchmark-reports",
    "reports",
}

GENERATED_PARTS = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".tox",
    ".nox",
    ".cache",
    "node_modules",
    "dist",
    "build",
}

ARCHIVE_SUFFIXES = {".zip", ".tar", ".tgz", ".gz", ".7z", ".rar"}
SECRET_PATTERNS = [
    re.compile(r"(^|[._-])(secret|credential|credentials|token|private|key|cert)([._-]|$)", re.I),
    re.compile(r"^\.env($|[.])", re.I),
]
PLACEHOLDER_PATTERNS = [
    re.compile(r"(?m)^\s*TO" + r"DO(?:\b|:)", re.I),
    re.compile(r"(?m)^\s*REPLACE ME\b", re.I),
    re.compile(r"\bexample script\b", re.I),
    re.compile(r"\bexample\s+asset\b", re.I),
    re.compile(r"\bapi reference\b", re.I),
]
TEXT_SUFFIXES = {
    ".md",
    ".txt",
    ".py",
    ".sh",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".cfg",
    ".csv",
    ".js",
    ".ts",
    ".html",
    ".css",
}
SUPPORT_PREFIXES = ("references/", "assets/", "scripts/", "examples/", "evals/", "agents/")
LINK_PATTERN = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


def is_text_candidate(path: Path) -> bool:
    return path.suffix.lower() in TEXT_SUFFIXES or path.name in {"SKILL.md", "README", "README.md"}


def canonical_rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def file_hash(path: Path) -> str | None:
    try:
        if path.is_symlink():
            return hashlib.sha256(("symlink:" + os.readlink(path)).encode("utf-8", errors="surrogateescape")).hexdigest()
        if not path.is_file():
            return None
        h = hashlib.sha256()
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError:
        return None


def read_text(path: Path, max_bytes: int = 2_000_000) -> str:
    try:
        if path.is_symlink() or not path.is_file() or path.stat().st_size > max_bytes:
            return ""
        return path.read_bytes().decode("utf-8", errors="ignore")
    except OSError:
        return ""


def collect_resources(root: Path) -> list[Path]:
    resources: list[Path] = []
    for current, dirnames, filenames in os.walk(root, followlinks=False):
        current_path = Path(current)
        kept_dirs: list[str] = []
        for name in sorted(dirnames):
            p = current_path / name
            if p.is_symlink():
                resources.append(p)
            else:
                kept_dirs.append(name)
        dirnames[:] = kept_dirs
        for name in sorted(filenames):
            resources.append(current_path / name)
    return sorted(resources, key=lambda p: canonical_rel(p, root))


def lexical_join(source_rel: str, raw: str) -> str | None:
    raw = raw.strip().split("#", 1)[0]
    if not raw or raw.startswith(("http://", "https://", "mailto:", "#", "/")):
        return None
    raw = raw.replace("\\", "/")
    joined = posixpath.normpath(posixpath.join(posixpath.dirname(source_rel), raw))
    if joined.startswith("../") or joined == "..":
        return None
    return joined


def python_import_candidates(source_rel: str, text: str) -> set[str]:
    if not source_rel.endswith(".py"):
        return set()
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return set()
    base = PurePosixPath(source_rel).parent
    out: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                mod = alias.name.replace(".", "/") + ".py"
                out.add(str(base / mod))
                out.add(mod)
        elif isinstance(node, ast.ImportFrom) and node.module:
            mod = node.module.replace(".", "/") + ".py"
            out.add(str(base / mod))
            out.add(mod)
    return {posixpath.normpath(x) for x in out}


def build_reference_graph(root: Path, resources: list[Path]) -> tuple[dict[str, list[str]], set[str]]:
    rels = [canonical_rel(p, root) for p in resources]
    relset = set(rels)
    graph: dict[str, set[str]] = {rel: set() for rel in rels}

    for path in resources:
        rel = canonical_rel(path, root)
        if path.is_symlink() or not is_text_candidate(path):
            continue
        text = read_text(path)
        if not text:
            continue
        for link in LINK_PATTERN.findall(text):
            candidate = lexical_join(rel, link)
            if candidate in relset:
                graph[rel].add(candidate)
        for other in rels:
            if other != rel and other in text:
                graph[rel].add(other)
        for candidate in python_import_candidates(rel, text):
            if candidate in relset:
                graph[rel].add(candidate)

    entrypoints = {"SKILL.md"} if "SKILL.md" in relset else set()
    entrypoints.update(rel for rel in rels if rel.startswith("agents/"))
    reachable = set(entrypoints)
    queue = sorted(entrypoints)
    while queue:
        current = queue.pop(0)
        for nxt in sorted(graph.get(current, ())):
            if nxt not in reachable:
                reachable.add(nxt)
                queue.append(nxt)
    return {k: sorted(v) for k, v in sorted(graph.items())}, reachable


def reverse_graph(graph: dict[str, list[str]]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {k: [] for k in graph}
    for source, targets in graph.items():
        for target in targets:
            out.setdefault(target, []).append(source)
    return {k: sorted(v) for k, v in sorted(out.items())}


def normalized_lines(path: Path) -> set[str]:
    text = read_text(path)
    return {line.strip() for line in text.splitlines() if line.strip()}


def build_similarity(resources: list[Path], root: Path) -> dict[str, list[dict[str, Any]]]:
    candidates = [p for p in resources if not p.is_symlink() and is_text_candidate(p) and p.is_file() and p.stat().st_size <= 200_000]
    texts = {canonical_rel(p, root): normalized_lines(p) for p in candidates}
    out: dict[str, list[dict[str, Any]]] = {rel: [] for rel in texts}
    rels = sorted(texts)
    for i, left in enumerate(rels):
        if not texts[left]:
            continue
        for right in rels[i + 1 :]:
            if not texts[right]:
                continue
            union = texts[left] | texts[right]
            ratio = (len(texts[left] & texts[right]) / len(union)) if union else 0.0
            if 0.60 <= ratio < 1.0:
                item_l = {"path": right, "similarity": round(ratio, 4), "note": "manual partial-duplicate review only"}
                item_r = {"path": left, "similarity": round(ratio, 4), "note": "manual partial-duplicate review only"}
                out[left].append(item_l)
                out[right].append(item_r)
    return {k: sorted(v, key=lambda x: (-x["similarity"], x["path"])) for k, v in out.items() if v}


def is_protected(path: Path, root: Path) -> tuple[bool, list[str]]:
    rel_path = path.relative_to(root)
    parts = set(rel_path.parts)
    lower_name = path.name.lower()
    reasons: list[str] = []
    if any(part in PROTECTED_PARTS for part in parts):
        reasons.append("protected path/evidence/fixture namespace")
    if any(p.search(lower_name) for p in SECRET_PATTERNS):
        reasons.append("secret-like or credential-like filename")
    if path.suffix.lower() in ARCHIVE_SUFFIXES:
        reasons.append("existing archive/package is protected from automatic cleanup")
    if path.is_symlink():
        reasons.append("symbolic link requires explicit manual review; automatic mutation is blocked")
        try:
            resolved = path.resolve(strict=False)
            root_resolved = root.resolve(strict=True)
            if not resolved.is_relative_to(root_resolved):
                reasons.append("symbolic link resolves outside target root")
        except (OSError, RuntimeError):
            reasons.append("symbolic link could not be resolved safely")
    return bool(reasons), reasons


def placeholder_hits(path: Path) -> list[str]:
    if not is_text_candidate(path) or path.is_symlink():
        return []
    text = read_text(path)
    return [pattern.pattern for pattern in PLACEHOLDER_PATTERNS if pattern.search(text)]


def build_inventory(root: Path) -> dict[str, Any]:
    resources = collect_resources(root)
    graph, reachable = build_reference_graph(root, resources)
    referenced_by = reverse_graph(graph)
    similarities = build_similarity(resources, root)

    digests: dict[str, list[str]] = {}
    path_by_rel = {canonical_rel(p, root): p for p in resources}
    for rel, path in path_by_rel.items():
        digest = file_hash(path)
        if digest and not path.is_symlink():
            digests.setdefault(digest, []).append(rel)

    exact_duplicates: dict[str, str] = {}
    for group in digests.values():
        if len(group) < 2:
            continue
        ordered = sorted(group, key=lambda rel: (rel not in reachable, rel))
        canonical = ordered[0]
        for rel in ordered[1:]:
            exact_duplicates[rel] = canonical

    entries: list[dict[str, Any]] = []
    for rel in sorted(path_by_rel):
        path = path_by_rel[rel]
        digest = file_hash(path)
        blocked, blocked_reasons = is_protected(path, root)
        reasons: list[str] = []
        status = "unknown"
        if blocked:
            status = "blocked"
            reasons.extend(blocked_reasons)
        elif rel in reachable:
            status = "used"
            reasons.append("reachable from SKILL.md or host adapter through the local reference graph")
        elif any(part in GENERATED_PARTS for part in Path(rel).parts):
            status = "generated"
            reasons.append("generated/cache/build namespace and not reachable from package entrypoints")
        elif rel in exact_duplicates:
            status = "duplicate"
            reasons.append(f"exact sha256 duplicate of {exact_duplicates[rel]}")
        elif rel.startswith(SUPPORT_PREFIXES):
            status = "integrable"
            reasons.append("support resource is unreferenced but may be intentionally dormant; integrate or review before deletion")
        elif rel == "SKILL.md":
            status = "used"
            reasons.append("root skill entrypoint")
        else:
            status = "unknown"
            reasons.append("insufficient evidence for safe removal")

        hits = placeholder_hits(path)
        if hits:
            reasons.append("scaffold/placeholder markers are informational only and do not make a resource removable")

        entries.append(
            {
                "path": rel,
                "status": status,
                "size_bytes": path.lstat().st_size,
                "sha256": digest,
                "is_symlink": path.is_symlink(),
                "referenced_by": referenced_by.get(rel, []),
                "references": graph.get(rel, []),
                "duplicate_of": exact_duplicates.get(rel),
                "placeholder_hits": hits,
                "similarity_candidates": similarities.get(rel, []),
                "reasons": reasons,
            }
        )

    counts = {state: 0 for state in CANONICAL_STATES}
    for item in entries:
        counts[item["status"]] += 1

    entrypoints = sorted({"SKILL.md"} & set(path_by_rel) | {rel for rel in path_by_rel if rel.startswith("agents/")})
    return {
        "inventory_version": 2,
        "target": str(root),
        "canonical_target": str(root.resolve(strict=True)),
        "states": list(CANONICAL_STATES),
        "entrypoints": entrypoints,
        "file_count": len(entries),
        "status_counts": counts,
        "reference_graph": graph,
        "entries": entries,
        "notes": [
            "Inventory is read-only and deterministically ordered by canonical relative path.",
            "unknown is fail-closed and is never eligible for automatic deletion.",
            "Partial similarity is advisory; only exact duplicates can receive the duplicate state mechanically.",
        ],
    }


def write_json_atomic(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    payload = json.dumps(data, indent=2, sort_keys=True) + "\n"
    with tmp.open("w", encoding="utf-8") as fh:
        fh.write(payload)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a deterministic read-only cleanup inventory.")
    parser.add_argument("--target", required=True, help="Target folder to inspect.")
    parser.add_argument("--output", help="Optional JSON output path; keep it outside the target package.")
    args = parser.parse_args()

    root = Path(args.target).resolve(strict=True)
    if not root.is_dir():
        raise SystemExit(f"target is not a directory: {root}")

    inventory = build_inventory(root)
    if args.output:
        output = Path(args.output)
        output = output.resolve(strict=False)
        if output == root or root in output.parents:
            raise SystemExit("output must be outside the target package")
        write_json_atomic(output, inventory)
        print(f"wrote inventory: {output}")
    else:
        print(json.dumps(inventory, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
