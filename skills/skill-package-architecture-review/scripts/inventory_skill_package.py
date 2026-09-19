#!/usr/bin/env python3
"""Create deterministic structural evidence for an Agent Skills package.

The output is mechanical evidence only. It records files, identity, declared
resource relationships, consumer evidence, ownership-role taxonomy, and
progressive-loading declarations. It never labels a resource orphaned or makes
an architectural recommendation.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "2.0.0"
TOP_LEVEL_AREAS = ["agents", "references", "scripts", "assets", "examples", "evals"]
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
EXCLUDED_PARTS = {".git", "__pycache__"}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def is_text_file(path: Path) -> bool:
    try:
        data = path.read_bytes()[:4096]
        return b"\x00" not in data and _is_utf8(data)
    except OSError:
        return False


def _is_utf8(data: bytes) -> bool:
    try:
        data.decode("utf-8")
        return True
    except UnicodeDecodeError:
        return False


def count_lines(path: Path) -> int | None:
    if not is_text_file(path):
        return None
    try:
        return len(path.read_text(encoding="utf-8").splitlines())
    except OSError:
        return None


def extract_frontmatter(skill_md: Path) -> dict[str, Any]:
    if not skill_md.exists() or not is_text_file(skill_md):
        return {}
    text = skill_md.read_text(encoding="utf-8", errors="replace")
    if not text.startswith("---\n"):
        return {"present": False}
    end = text.find("\n---", 4)
    if end == -1:
        return {"present": False, "error": "unterminated frontmatter"}
    raw = text[4:end].strip()
    result: dict[str, Any] = {"present": True, "raw_line_count": len(raw.splitlines())}
    for line in raw.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip().strip('"').strip("'")
    return result


def _included_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if any(part in EXCLUDED_PARTS for part in path.parts):
            continue
        if path.is_file():
            files.append(path)
    return sorted(files, key=lambda p: p.relative_to(root).as_posix())


def _resource_taxonomy(rel: str) -> tuple[str, str]:
    p = Path(rel)
    parts = p.parts
    if rel == "SKILL.md":
        return "control-plane", "control-plane"
    if parts and parts[0] == "agents":
        return "host-adapter", "host-adapter"
    if parts and parts[0] == "references":
        return "reference", "review-guidance"
    if parts and parts[0] == "scripts":
        return "script", "deterministic-mechanics"
    if len(parts) >= 2 and parts[0] == "assets" and parts[1] == "templates":
        return "template-asset", "output-contract"
    if parts and parts[0] == "assets":
        return "runtime-asset", "runtime-asset"
    if parts and parts[0] == "examples":
        return "example", "example-evidence"
    if parts and parts[0] == "evals":
        return "eval", "evaluation-evidence"
    return "package-resource", "unknown"


def markdown_links(path: Path, root: Path) -> list[dict[str, str]]:
    if path.suffix.lower() != ".md" or not is_text_file(path):
        return []
    text = path.read_text(encoding="utf-8", errors="replace")
    links: list[dict[str, str]] = []
    for match in LINK_RE.finditer(text):
        target = match.group(1).strip()
        if "://" in target or target.startswith("mailto:") or target.startswith("#"):
            links.append({"source": path.relative_to(root).as_posix(), "target": target, "kind": "external-or-anchor", "exists": "not-checked"})
            continue
        clean = target.split("#", 1)[0]
        target_path = (path.parent / clean).resolve()
        try:
            rel = target_path.relative_to(root.resolve()).as_posix()
            kind = "local"
            exists = str(target_path.exists())
            normalized_target = rel
        except ValueError:
            kind = "outside-root"
            exists = str(target_path.exists())
            normalized_target = target
        links.append({"source": path.relative_to(root).as_posix(), "target": target, "normalized_target": normalized_target, "kind": kind, "exists": exists})
    return links


def _text_by_rel(files: list[Path], root: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for path in files:
        if is_text_file(path):
            out[path.relative_to(root).as_posix()] = path.read_text(encoding="utf-8", errors="replace")
    return out


def _consumer_evidence(rel: str, texts: dict[str, str], links: list[dict[str, str]]) -> list[str]:
    consumers: set[str] = set()
    for link in links:
        if link.get("kind") == "local" and link.get("normalized_target") == rel:
            consumers.add(link["source"])
    for source, text in texts.items():
        if source == rel:
            continue
        if rel in text:
            consumers.add(source)
    return sorted(consumers)


def _python_import_edges(files: list[Path], root: Path) -> list[dict[str, str]]:
    available = {p.relative_to(root).as_posix(): p for p in files}
    module_to_path: dict[str, str] = {}
    for rel in available:
        if not rel.endswith(".py"):
            continue
        module = rel[:-3].replace("/", ".")
        if module.endswith(".__init__"):
            module = module[:-9]
        module_to_path[module] = rel
    edges: list[dict[str, str]] = []
    for rel, path in available.items():
        if not rel.endswith(".py") or not is_text_file(path):
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=rel)
        except SyntaxError:
            continue
        modules: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                modules.add(node.module)
        for module in sorted(modules):
            target = module_to_path.get(module)
            if target:
                edges.append({"source": rel, "target": target, "kind": "python-import"})
    return edges


def _package_identity(files: list[dict[str, Any]]) -> str:
    h = hashlib.sha256()
    for item in files:
        h.update(item["path"].encode("utf-8"))
        h.update(b"\0")
        h.update(item["sha256"].encode("ascii"))
        h.update(b"\n")
    return h.hexdigest()


def inventory(root: Path) -> dict[str, Any]:
    root = root.resolve()
    paths = _included_files(root)
    files: list[dict[str, Any]] = []
    area_counts = {area: 0 for area in TOP_LEVEL_AREAS}
    links: list[dict[str, str]] = []
    skill_md_files: list[str] = []

    for path in paths:
        rel = path.relative_to(root).as_posix()
        if path.name == "SKILL.md":
            skill_md_files.append(rel)
        area = Path(rel).parts[0] if Path(rel).parts else "root"
        if area in area_counts:
            area_counts[area] += 1
        taxonomy, owner_role = _resource_taxonomy(rel)
        info = {
            "path": rel,
            "area": area,
            "suffix": path.suffix,
            "size_bytes": path.stat().st_size,
            "line_count": count_lines(path),
            "sha256": sha256_file(path),
            "is_text": is_text_file(path),
            "taxonomy": taxonomy,
            "owner_role": owner_role,
        }
        files.append(info)
        links.extend(markdown_links(path, root))

    texts = _text_by_rel(paths, root)
    resource_map: list[dict[str, Any]] = []
    ownership_map: list[dict[str, str]] = []
    dependency_edges: list[dict[str, str]] = []

    for item in files:
        rel = item["path"]
        consumers = _consumer_evidence(rel, texts, links)
        resource_map.append({
            "path": rel,
            "taxonomy": item["taxonomy"],
            "owner_role": item["owner_role"],
            "consumer_evidence": consumers,
            "consumer_status": "observed-consumer-evidence" if consumers else "unresolved-no-evidence",
        })
        ownership_map.append({
            "path": rel,
            "owner_role": item["owner_role"],
            "basis": "deterministic-path-role-taxonomy" if item["owner_role"] != "unknown" else "unresolved",
        })
        for source in consumers:
            dependency_edges.append({"source": source, "target": rel, "kind": "path-or-link-evidence"})

    dependency_edges.extend(_python_import_edges(paths, root))
    dependency_edges = sorted(
        {json.dumps(edge, sort_keys=True): edge for edge in dependency_edges}.values(),
        key=lambda e: (e["source"], e["target"], e["kind"]),
    )

    skill_text = texts.get("SKILL.md", "")
    declared_resources: list[dict[str, str]] = []
    for item in resource_map:
        rel = item["path"]
        if rel == "SKILL.md":
            continue
        if rel in skill_text or any(
            link.get("source") == "SKILL.md" and link.get("kind") == "local" and link.get("normalized_target") == rel
            for link in links
        ):
            declared_resources.append({"target": rel, "evidence": "direct-SKILL.md-reference"})

    local_links = [link for link in links if link["kind"] == "local"]
    broken_local_links = [link for link in local_links if link["exists"] == "False"]
    skill_md = root / "SKILL.md"

    return {
        "schema_version": SCHEMA_VERSION,
        "target": str(root),
        "package_identity_sha256": _package_identity(files),
        "skill_md_files": sorted(skill_md_files),
        "root_skill_md_present": skill_md.exists(),
        "frontmatter": extract_frontmatter(skill_md),
        "file_count": len(files),
        "total_size_bytes": sum(item["size_bytes"] for item in files),
        "area_counts": area_counts,
        "files": files,
        "resource_map": sorted(resource_map, key=lambda x: x["path"]),
        "ownership_map": sorted(ownership_map, key=lambda x: x["path"]),
        "dependency_map": {"edges": dependency_edges},
        "progressive_loading_map": {"skill_md_declared_resources": sorted(declared_resources, key=lambda x: x["target"])},
        "markdown_links": sorted(links, key=lambda x: (x["source"], x["target"], x["kind"])),
        "broken_local_links": broken_local_links,
        "notes": [
            "inventory is mechanical evidence only",
            "consumer_status unresolved-no-evidence is not an orphan classification",
            "architectural judgment requires the versioned rubric and package context",
        ],
    }


def render_markdown(data: dict[str, Any]) -> str:
    lines = [
        f"# Skill Package Inventory: {data['target']}",
        "",
        "## Identity",
        "",
        f"- schema: `{data['schema_version']}`",
        f"- package SHA-256: `{data['package_identity_sha256']}`",
        "",
        "## Summary",
        "",
        f"- root `SKILL.md` present: {data['root_skill_md_present']}",
        f"- `SKILL.md` files found: {len(data['skill_md_files'])}",
        f"- file count: {data['file_count']}",
        f"- total size bytes: {data['total_size_bytes']}",
        f"- broken local markdown links: {len(data['broken_local_links'])}",
        "",
        "## Resource map",
        "",
    ]
    for item in data["resource_map"]:
        consumers = ", ".join(item["consumer_evidence"]) or "none observed"
        lines.append(f"- `{item['path']}` — {item['taxonomy']} / {item['owner_role']}; consumers: {consumers}; status: {item['consumer_status']}")
    lines.extend(["", "> Mechanical evidence only. Absence of consumer evidence is not deletion evidence."])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="inventory a skill package deterministically")
    parser.add_argument("--target", required=True, help="path to skill package root")
    parser.add_argument("--json-output", help="optional json output path")
    parser.add_argument("--markdown-output", help="optional markdown output path")
    args = parser.parse_args()

    target = Path(args.target)
    if not target.exists() or not target.is_dir():
        raise SystemExit(f"target is not a directory: {target}")

    data = inventory(target)
    text = json.dumps(data, indent=2, sort_keys=True)
    print(text)

    if args.json_output:
        out = Path(args.json_output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text + "\n", encoding="utf-8")
    if args.markdown_output:
        out = Path(args.markdown_output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render_markdown(data), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
