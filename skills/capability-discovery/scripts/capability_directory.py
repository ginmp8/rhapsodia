#!/usr/bin/env python3
"""Bounded, read-only source-pinned candidates for Skills and native agents.

This is NOT a host installation inventory, authority oracle, semantic router,
workflow engine, agent allowlist or a substitute for native Skill discovery.
Requires Python 3.10+ and the standard library only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path

SCHEMA = "rhapsodia-capability-directory/v1"
SKILL_ROOTS = ("skills", ".github/skills", ".claude/skills", ".cursor/skills", ".agents/skills")
AGENT_ROOTS = ("agents", ".github/agents", ".claude/agents", ".cursor/agents")
STOP = frozenset(
    "a an and as by com como da de do dos das e em for from in is no na nos nas o of "
    "on or ou para por que se skill skills the um uma use using when with".split()
)


def tokens(text: str) -> set[str]:
    normalized = unicodedata.normalize("NFKD", text.casefold())
    ascii_text = "".join(c for c in normalized if not unicodedata.combining(c))
    return {t for t in re.findall(r"[a-z0-9]+", ascii_text) if len(t) >= 3 and t not in STOP}


def metadata(path: Path) -> dict[str, str]:
    """Parse bounded YAML scalar/folded frontmatter without executing YAML tags."""
    with path.open("r", encoding="utf-8") as source:
        if source.readline().strip() != "---":
            raise ValueError("missing frontmatter")
        header: list[str] = []
        for line in source:
            if line.strip() == "---":
                break
            header.append(line.rstrip("\r\n"))
            if len(header) > 120:
                raise ValueError("frontmatter is too long")
        else:
            raise ValueError("unterminated frontmatter")
    found: dict[str, str] = {}
    for i, line in enumerate(header):
        if line.startswith((" ", "\t")) or ":" not in line:
            continue
        key, value = (s.strip() for s in line.split(":", 1))
        if key not in ("name", "description"):
            continue
        if key in found:
            raise ValueError("duplicate field " + key)
        if value in {">", ">-", "|", "|-"}:
            block: list[str] = []
            for next_line in header[i + 1:]:
                if next_line.strip() and not next_line.startswith((" ", "\t")):
                    break
                if next_line.strip():
                    block.append(next_line.strip())
            value = " ".join(block)
        elif value.startswith('"'):
            value = json.loads(value)
        elif len(value) >= 2 and value[0] == value[-1] == "'":
            value = value[1:-1].replace("''", "'")
        if not isinstance(value, str) or not value.strip():
            raise ValueError("invalid " + key)
        found[key] = value.strip()
    if not found.get("name") or not found.get("description"):
        raise ValueError("name or description missing")
    return found


def checked_root(root: Path) -> bool:
    # Ancestors may include platform aliases such as macOS /var -> /private/var.
    return root.is_dir() and not root.is_symlink()


def relative_or_absolute(path: Path, workspace: Path) -> str:
    try:
        return path.relative_to(workspace).as_posix()
    except ValueError:
        return path.as_posix()


def inventory(
    workspace: Path,
    kind: str = "all",
    skill_roots: list[Path] | None = None,
    agent_roots: list[Path] | None = None,
) -> tuple[list[dict], list[str], list[str]]:
    workspace = workspace.absolute()
    errors: list[str] = []
    inspected: list[str] = []
    entries: list[dict] = []
    seen: set[tuple[str, str]] = set()
    spec = (("skill", SKILL_ROOTS, skill_roots or []), ("agent", AGENT_ROOTS, agent_roots or []))
    for label, conventional, explicit in spec:
        if kind not in ("all", label):
            continue
        roots = [workspace / rel for rel in conventional if (workspace / rel).exists()]
        roots.extend(p if p.is_absolute() else workspace / p for p in explicit)
        unique: set[str] = set()
        for raw in roots:
            text = str(raw.absolute())
            if text in unique:
                continue
            unique.add(text)
            shown = relative_or_absolute(raw.absolute(), workspace)
            if not checked_root(raw):
                errors.append(f"unavailable or symlinked {label} root: {shown}")
                continue
            inspected.append(shown)
            entrypoints = sorted(
                [raw / "SKILL.md"] if label == "skill" and (raw / "SKILL.md").is_file()
                else list(raw.glob("*/SKILL.md")) if label == "skill"
                else list(raw.glob("*.agent.md")),
                key=lambda p: p.as_posix().casefold(),
            )
            if label == "skill" and not (raw / "SKILL.md").is_file():
                try:
                    children = list(raw.iterdir())
                except OSError as exc:
                    errors.append(f"cannot enumerate {shown}: {type(exc).__name__}")
                    continue
                for child in children:
                    if child.is_symlink():
                        errors.append(f"linked entry within skill root: {shown}/{child.name}")
                    elif child.is_dir() and not (child / "SKILL.md").is_file():
                        errors.append(f"missing entrypoint in {shown}/{child.name}")
            for path in entrypoints:
                shown_path = relative_or_absolute(path.absolute(), workspace)
                if path.is_symlink() or path.parent.is_symlink():
                    errors.append(f"symlinked entrypoint: {shown_path}")
                    continue
                try:
                    info = metadata(path)
                    identity = path.parent.name if label == "skill" else path.name.removesuffix(".agent.md")
                    marker = (label, identity.casefold())
                    if marker in seen:
                        raise ValueError("duplicate local identity; inspect host precedence")
                    seen.add(marker)
                    version_file = path.parent / "VERSION" if label == "skill" else None
                    version = (
                        version_file.read_text(encoding="utf-8").strip()
                        if version_file and version_file.is_file() and not version_file.is_symlink()
                        else None
                    )
                    entries.append({
                        "kind": label, "id": identity, "name": info["name"],
                        "description": info["description"], "path": shown_path,
                        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                        "version": version,
                    })
                except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
                    errors.append(f"unreadable entrypoint {shown_path}: {type(exc).__name__}: {exc}")
    if not inspected:
        errors.append("no accessible inspected roots; specify an approved --skill-root or --agent-root")
    entries.sort(key=lambda v: (v["kind"], v["id"].casefold(), v["path"]))
    return entries, errors, inspected


def score(query: str, entry: dict) -> int:
    wanted = tokens(query)
    if not wanted:
        return 0
    return 5 * len(wanted & tokens(entry["id"] + " " + entry["name"])) + len(wanted & tokens(entry["description"]))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("find", "list"))
    parser.add_argument("query", nargs="?", help="bounded query for 'find'; matches are advisory only")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="approved workspace (not Skill root)")
    parser.add_argument("--skill-root", type=Path, action="append", default=[], help="additional approved Skill root, repeatable")
    parser.add_argument("--agent-root", type=Path, action="append", default=[], help="additional approved agent root, repeatable")
    parser.add_argument("--kind", choices=("all", "skill", "agent"), default="all")
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args(argv)
    if args.command == "find" and not (args.query and args.query.strip()):
        parser.error("find requires a non-empty query")
    if args.command == "list" and args.query:
        parser.error("list does not take a query")
    if not 1 <= args.limit <= 150:
        parser.error("--limit must be between 1 and 150")
    records, errors, inspected = inventory(args.root, args.kind, args.skill_root, args.agent_root)
    if args.command == "find":
        records = [{**item, "match_score": score(args.query, item)} for item in records]
        records = [item for item in records if item["match_score"] > 0]
        records.sort(key=lambda v: (-v["match_score"], v["kind"], v["id"].casefold(), v["path"]))
    matches = records[:args.limit]
    result = {
        "schema": SCHEMA,
        "status": "partial" if errors else ("candidates" if matches else "unresolved"),
        "scope": "bounded-local-roots-not-host-inventory",
        "source_completeness": "partial" if errors else "inspected-roots-only",
        "inspected_roots": inspected,
        "query": args.query if args.command == "find" else None,
        "matches": matches, "returned": len(matches), "total_candidates": len(records),
        "truncated": len(records) > len(matches), "errors": errors,
        "decision": "native-availability-and-semantic-review-required",
        "unmatched_meaning": "unknown-outside-inspected-roots",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 2 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
