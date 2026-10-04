#!/usr/bin/env python3
"""Deterministic, read-only cleanup inventory with conservative multi-root reachability."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import posixpath
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

sys.dont_write_bytecode = True

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
    "evals",
    "tests",
    "contracts",
}

STRONG_GENERATED_PARTS = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".tox",
    ".nox",
}
WEAK_GENERATED_PARTS = {"dist", "build", "node_modules", "coverage", "htmlcov", "out", "target"}
GENERATED_FILE_SUFFIXES = {".pyc", ".pyo"}
GENERATED_FILE_NAMES = {".DS_Store"}

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
    ".cjs",
    ".mjs",
    ".jsx",
    ".ts",
    ".tsx",
    ".html",
    ".css",
}
SUPPORT_PREFIXES = ("references/", "assets/", "scripts/", "examples/", "evals/", "agents/", "contracts/", "tests/")
INLINE_LINK_PATTERN = re.compile(r"(!?)\[[^\]]*\]\(([^)]+)\)")
REFERENCE_DEF_PATTERN = re.compile(r"(?m)^\s*\[[^\]]+\]:\s*(?:<([^>]+)>|(\S+))")
PATH_TOKEN_PATTERN = re.compile(r"(?<![A-Za-z0-9_.-])((?:\.?\.?/)?[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)+)(?![A-Za-z0-9_.-])")
JS_IMPORT_PATTERN = re.compile(
    r"(?:\b(?:import|export)\b(?:[^\"']*?\bfrom\s*)?[\"']([^\"']+)[\"']|"
    r"\brequire\s*\(\s*[\"']([^\"']+)[\"']\s*\))"
)
ROOT_KIND_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


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
            path = current_path / name
            if path.is_symlink():
                resources.append(path)
            else:
                kept_dirs.append(name)
        dirnames[:] = kept_dirs
        for name in sorted(filenames):
            resources.append(current_path / name)
    return sorted(resources, key=lambda path: canonical_rel(path, root))


def lexical_join(source_rel: str, raw: str) -> str | None:
    raw = raw.strip().strip("<>").split("#", 1)[0]
    if not raw or raw.startswith(("http://", "https://", "mailto:", "#", "/")):
        return None
    raw = raw.replace("\\", "/")
    joined = posixpath.normpath(posixpath.join(posixpath.dirname(source_rel), raw))
    if joined.startswith("../") or joined == "..":
        return None
    return joined


def resolve_code_reference(source_rel: str, raw: str, relset: set[str]) -> set[str]:
    if not raw.startswith("."):
        return set()
    base = posixpath.normpath(posixpath.join(posixpath.dirname(source_rel), raw))
    candidates = {base}
    for ext in (".py", ".js", ".cjs", ".mjs", ".jsx", ".ts", ".tsx", ".json"):
        candidates.add(base + ext)
        candidates.add(posixpath.join(base, "index" + ext))
    return {candidate for candidate in candidates if candidate in relset}


def python_import_candidates(source_rel: str, text: str, relset: set[str]) -> set[str]:
    if not source_rel.endswith(".py"):
        return set()
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return set()
    out: set[str] = set()
    source_parent = PurePosixPath(source_rel).parent
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                module = alias.name.replace(".", "/")
                for candidate in (module + ".py", str(source_parent / (module + ".py"))):
                    candidate = posixpath.normpath(candidate)
                    if candidate in relset:
                        out.add(candidate)
        elif isinstance(node, ast.ImportFrom):
            parent_parts = list(source_parent.parts)
            if node.level:
                keep = max(0, len(parent_parts) - (node.level - 1))
                parent_parts = parent_parts[:keep]
            module_parts = node.module.split(".") if node.module else []
            base = PurePosixPath(*parent_parts, *module_parts)
            if node.module:
                candidate = posixpath.normpath(str(base) + ".py")
                if candidate in relset:
                    out.add(candidate)
            for alias in node.names:
                candidate = posixpath.normpath(str(base / alias.name) + ".py")
                if candidate in relset:
                    out.add(candidate)
    return out


def generated_signals(rel: str, path: Path) -> list[dict[str, str]]:
    parts = set(PurePosixPath(rel).parts)
    signals: list[dict[str, str]] = []
    strong_parts = sorted(parts & STRONG_GENERATED_PARTS)
    weak_parts = sorted(parts & WEAK_GENERATED_PARTS)
    if strong_parts:
        signals.append({"strength": "strong", "kind": "tool-cache-namespace", "value": ",".join(strong_parts)})
    if path.suffix.lower() in GENERATED_FILE_SUFFIXES:
        signals.append({"strength": "strong", "kind": "generated-file-suffix", "value": path.suffix.lower()})
    if path.name in GENERATED_FILE_NAMES:
        signals.append({"strength": "strong", "kind": "generated-file-name", "value": path.name})
    if weak_parts:
        signals.append({"strength": "weak", "kind": "generated-like-namespace", "value": ",".join(weak_parts)})
    return signals


def build_root_registry(rels: Iterable[str], extra_roots: list[dict[str, str]] | None = None) -> list[dict[str, str]]:
    relset = set(rels)
    roots: dict[tuple[str, str], dict[str, str]] = {}

    def add(kind: str, path: str, source: str) -> None:
        if path in relset:
            roots[(kind, path)] = {"kind": kind, "path": path, "source": source}

    add("skill-entrypoint", "SKILL.md", "default")
    for rel in sorted(relset):
        if rel.startswith("agents/"):
            add("host-adapter-root", rel, "default")
        if rel.startswith("evals/"):
            add("evaluator-root", rel, "default")
        if rel.startswith("tests/"):
            add("test-root", rel, "default")
    for item in extra_roots or []:
        kind = str(item.get("kind", "declared-root"))
        path = str(item.get("path", ""))
        if not ROOT_KIND_PATTERN.fullmatch(kind):
            raise ValueError(f"invalid root kind: {kind}")
        if path not in relset:
            raise ValueError(f"declared root does not exist in target: {path}")
        roots[(kind, path)] = {"kind": kind, "path": path, "source": "declared"}
    return sorted(roots.values(), key=lambda item: (item["path"], item["kind"], item["source"]))


def add_edge(edges: set[tuple[str, str, str, str]], source: str, target: str, kind: str, evidence: str = "") -> None:
    if source != target:
        edges.add((source, target, kind, evidence))


def build_reference_graph(
    root: Path,
    resources: list[Path],
    extra_roots: list[dict[str, str]] | None = None,
) -> tuple[dict[str, list[str]], list[dict[str, str]], list[dict[str, str]], set[str]]:
    rels = [canonical_rel(path, root) for path in resources]
    relset = set(rels)
    edges: set[tuple[str, str, str, str]] = set()

    for path in resources:
        rel = canonical_rel(path, root)
        if path.is_symlink() or not is_text_candidate(path):
            continue
        text = read_text(path)
        if not text:
            continue

        for image_marker, link in INLINE_LINK_PATTERN.findall(text):
            candidate = lexical_join(rel, link)
            if candidate in relset:
                add_edge(edges, rel, candidate, "markdown-image" if image_marker else "markdown-link", link)

        for left, right in REFERENCE_DEF_PATTERN.findall(text):
            raw = left or right
            candidate = lexical_join(rel, raw)
            if candidate in relset:
                add_edge(edges, rel, candidate, "markdown-reference", raw)

        for candidate in python_import_candidates(rel, text, relset):
            add_edge(edges, rel, candidate, "python-import")

        for raw in PATH_TOKEN_PATTERN.findall(text):
            candidate = lexical_join(rel, raw)
            if candidate in relset:
                add_edge(edges, rel, candidate, "path-literal", raw)

        if path.suffix.lower() in {".js", ".cjs", ".mjs", ".jsx", ".ts", ".tsx"}:
            for match in JS_IMPORT_PATTERN.finditer(text):
                raw = match.group(1) or match.group(2) or ""
                for candidate in resolve_code_reference(rel, raw, relset):
                    add_edge(edges, rel, candidate, "javascript-import", raw)

        for other in rels:
            if other != rel and other in text:
                add_edge(edges, rel, other, "path-literal", other)

    graph_sets: dict[str, set[str]] = {rel: set() for rel in rels}
    for source, target, _, _ in edges:
        graph_sets[source].add(target)
    graph = {key: sorted(value) for key, value in sorted(graph_sets.items())}

    root_registry = build_root_registry(rels, extra_roots)
    root_paths = {item["path"] for item in root_registry}
    reachable = set(root_paths)
    queue = sorted(root_paths)
    while queue:
        current = queue.pop(0)
        for nxt in graph.get(current, []):
            if nxt not in reachable:
                reachable.add(nxt)
                queue.append(nxt)

    typed_edges = [
        {"source": source, "target": target, "kind": kind, "evidence": evidence}
        for source, target, kind, evidence in sorted(edges)
    ]
    return graph, typed_edges, root_registry, reachable


def reverse_graph(graph: dict[str, list[str]]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {key: [] for key in graph}
    for source, targets in graph.items():
        for target in targets:
            out.setdefault(target, []).append(source)
    return {key: sorted(value) for key, value in sorted(out.items())}


def normalized_lines(path: Path) -> set[str]:
    text = read_text(path)
    return {line.strip() for line in text.splitlines() if line.strip()}


def build_similarity(resources: list[Path], root: Path) -> dict[str, list[dict[str, Any]]]:
    candidates = [
        path
        for path in resources
        if not path.is_symlink() and is_text_candidate(path) and path.is_file() and path.stat().st_size <= 200_000
    ]
    texts = {canonical_rel(path, root): normalized_lines(path) for path in candidates}
    out: dict[str, list[dict[str, Any]]] = {rel: [] for rel in texts}
    rels = sorted(texts)
    for index, left in enumerate(rels):
        if not texts[left]:
            continue
        for right in rels[index + 1 :]:
            if not texts[right]:
                continue
            union = texts[left] | texts[right]
            ratio = (len(texts[left] & texts[right]) / len(union)) if union else 0.0
            if 0.60 <= ratio < 1.0:
                out[left].append({"path": right, "similarity": round(ratio, 4), "tier": "normalized-lines", "note": "review candidate only"})
                out[right].append({"path": left, "similarity": round(ratio, 4), "tier": "normalized-lines", "note": "review candidate only"})
    return {key: sorted(value, key=lambda item: (-item["similarity"], item["path"])) for key, value in out.items() if value}


def is_protected(path: Path, root: Path) -> tuple[bool, list[str]]:
    rel_path = path.relative_to(root)
    parts = set(rel_path.parts)
    lower_name = path.name.lower()
    reasons: list[str] = []
    if any(part in PROTECTED_PARTS for part in parts):
        reasons.append("protected evidence, contract, test, fixture, or repository namespace")
    if any(pattern.search(lower_name) for pattern in SECRET_PATTERNS):
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


def build_inventory(root: Path, extra_roots: list[dict[str, str]] | None = None) -> dict[str, Any]:
    resources = collect_resources(root)
    graph, typed_edges, root_registry, reachable = build_reference_graph(root, resources, extra_roots)
    referenced_by = reverse_graph(graph)
    similarities = build_similarity(resources, root)

    digests: dict[str, list[str]] = {}
    path_by_rel = {canonical_rel(path, root): path for path in resources}
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

    roots_by_path: dict[str, list[str]] = {}
    for root_item in root_registry:
        roots_by_path.setdefault(root_item["path"], []).append(root_item["kind"])

    entries: list[dict[str, Any]] = []
    for rel in sorted(path_by_rel):
        path = path_by_rel[rel]
        digest = file_hash(path)
        blocked, blocked_reasons = is_protected(path, root)
        signals = generated_signals(rel, path)
        strong_generated = any(signal["strength"] == "strong" for signal in signals)
        weak_generated = any(signal["strength"] == "weak" for signal in signals)
        reasons: list[str] = []
        status = "unknown"
        if blocked:
            status = "blocked"
            reasons.extend(blocked_reasons)
        elif rel in reachable:
            status = "used"
            reasons.append("reachable from the recorded root registry through the local reference graph")
        elif strong_generated:
            status = "generated"
            reasons.append("strong tool-generated/cache evidence and not reachable from recorded roots")
        elif rel in exact_duplicates:
            status = "duplicate"
            reasons.append(f"exact sha256 duplicate of {exact_duplicates[rel]}")
        elif rel.startswith(SUPPORT_PREFIXES):
            status = "integrable"
            reasons.append("support resource is unreferenced but may be intentionally dormant; integrate or review before deletion")
        else:
            status = "unknown"
            reasons.append("insufficient evidence for safe removal")
        if weak_generated and status in {"unknown", "integrable"}:
            reasons.append("generated-like namespace is a weak signal only and does not authorize removal")

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
                "root_kinds": sorted(roots_by_path.get(rel, [])),
                "referenced_by": referenced_by.get(rel, []),
                "references": graph.get(rel, []),
                "duplicate_of": exact_duplicates.get(rel),
                "generated_signals": signals,
                "placeholder_hits": hits,
                "similarity_candidates": similarities.get(rel, []),
                "reasons": reasons,
            }
        )

    counts = {state: 0 for state in CANONICAL_STATES}
    for item in entries:
        counts[item["status"]] += 1

    return {
        "inventory_version": 3,
        "target": str(root),
        "canonical_target": str(root.resolve(strict=True)),
        "states": list(CANONICAL_STATES),
        "root_registry": root_registry,
        "entrypoints": sorted({item["path"] for item in root_registry}),
        "file_count": len(entries),
        "status_counts": counts,
        "reference_graph": graph,
        "reference_edges": typed_edges,
        "entries": entries,
        "analysis_limits": [
            "Reachability is bounded to default roots plus caller-declared roots; unknown external consumers are not inferred.",
            "dist/build/node_modules and similar namespaces are weak signals only and never sufficient for generated classification.",
            "Partial similarity is advisory; only exact duplicates can receive the duplicate state mechanically.",
        ],
        "notes": [
            "Inventory is read-only and deterministically ordered by canonical relative path.",
            "unknown is fail-closed and is never eligible for automatic deletion.",
            "Evaluator, test, contract, fixture, expected-output, archive, secret-like, and unsafe symlink resources are protected by default.",
        ],
    }


def parse_root_spec(raw: str, target: Path) -> dict[str, str]:
    if ":" not in raw:
        raise ValueError("--root must use kind:path")
    kind, rel = raw.split(":", 1)
    if not ROOT_KIND_PATTERN.fullmatch(kind):
        raise ValueError(f"invalid root kind: {kind}")
    if not rel or "\\" in rel:
        raise ValueError(f"invalid root path: {rel}")
    pure = PurePosixPath(rel)
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts) or pure.as_posix() != rel:
        raise ValueError(f"root path must be canonical and relative: {rel}")
    candidate = target.joinpath(*pure.parts)
    if not candidate.exists() or candidate.is_symlink() or not candidate.is_file():
        raise ValueError(f"declared root must be an existing regular file: {rel}")
    return {"kind": kind, "path": rel}


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
    parser.add_argument(
        "--root",
        action="append",
        default=[],
        help="Additional trusted reachability root in kind:relative/path form. Repeat as needed.",
    )
    args = parser.parse_args()

    root = Path(args.target).resolve(strict=True)
    if not root.is_dir():
        raise SystemExit(f"target is not a directory: {root}")
    try:
        extra_roots = [parse_root_spec(raw, root) for raw in args.root]
        inventory = build_inventory(root, extra_roots=extra_roots)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    if args.output:
        output = Path(args.output).resolve(strict=False)
        if output == root or root in output.parents:
            raise SystemExit("output must be outside the target package")
        write_json_atomic(output, inventory)
        print(f"wrote inventory: {output}")
    else:
        print(json.dumps(inventory, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
