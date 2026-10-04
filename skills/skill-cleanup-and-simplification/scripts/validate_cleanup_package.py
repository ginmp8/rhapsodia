#!/usr/bin/env python3
"""Post-cleanup structural validator with Agent Skills and context-efficiency checks."""

from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
import math
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

ARCHIVE_SUFFIXES = {".zip", ".tar", ".tgz", ".gz", ".7z", ".rar"}
TEXT_SUFFIXES = {".md", ".txt", ".py", ".sh", ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg"}
PLACEHOLDER_PATTERNS = [
    re.compile(r"(?m)^\s*TO" + r"DO(?:\b|:)", re.I),
    re.compile(r"(?m)^\s*REPLACE ME\b", re.I),
    re.compile(r"\[TO" + r"DO:", re.I),
]
INLINE_LINK_PATTERN = re.compile(r"!?(?:\[[^\]]*\])\(([^)]+)\)")
REFERENCE_DEF_PATTERN = re.compile(r"(?m)^\s*\[[^\]]+\]:\s*(?:<([^>]+)>|(\S+))")
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def _load_inventory_builder():
    module_path = Path(__file__).with_name("cleanup_inventory.py")
    spec = importlib.util.spec_from_file_location("cleanup_inventory_local_for_validation", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load sibling cleanup_inventory.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build_inventory


build_inventory = _load_inventory_builder()


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def is_text(path: Path) -> bool:
    return path.suffix.lower() in TEXT_SUFFIXES or path.name == "SKILL.md"


def add(
    checks: list[dict[str, Any]],
    code: str,
    status: str,
    subject: str,
    evidence: dict[str, Any],
    severity: str,
    fixes: list[str] | None = None,
) -> None:
    checks.append(
        {
            "code": code,
            "status": status,
            "subject": subject,
            "evidence": evidence,
            "severity": severity,
            "supported_fixes": fixes or [],
        }
    )


def tree_hash(root: Path) -> str:
    h = hashlib.sha256()
    for path in sorted(root.rglob("*"), key=lambda p: p.relative_to(root).as_posix()):
        if path.is_symlink():
            data = ("symlink:" + os.readlink(path)).encode("utf-8", errors="surrogateescape")
        elif path.is_file():
            data = path.read_bytes()
        else:
            continue
        h.update(path.relative_to(root).as_posix().encode("utf-8") + b"\0" + data + b"\0")
    return h.hexdigest()


def scalar_value(raw: str) -> str:
    value = raw.strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value[1:-1]
    if len(value) >= 2 and value[0] == value[-1] == "'":
        return value[1:-1].replace("''", "'")
    return value


def parse_frontmatter(text: str) -> tuple[dict[str, str], list[str]]:
    diagnostics: list[str] = []
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, ["missing opening frontmatter delimiter"]
    try:
        end = next(index for index in range(1, len(lines)) if lines[index].strip() == "---")
    except StopIteration:
        return {}, ["missing closing frontmatter delimiter"]
    front_lines = lines[1:end]
    values: dict[str, str] = {}
    index = 0
    while index < len(front_lines):
        line = front_lines[index]
        if not line.strip() or line.lstrip().startswith("#"):
            index += 1
            continue
        if line.startswith((" ", "\t")):
            index += 1
            continue
        match = re.match(r"^([A-Za-z0-9_-]+):(?:\s*(.*))?$", line)
        if not match:
            diagnostics.append(f"unparsed top-level frontmatter line: {line}")
            index += 1
            continue
        key, raw = match.group(1), match.group(2) or ""
        if raw in {"|", ">", "|-", ">-", "|+", ">+"}:
            folded = raw.startswith(">")
            block: list[str] = []
            index += 1
            while index < len(front_lines):
                next_line = front_lines[index]
                if next_line and not next_line.startswith((" ", "\t")):
                    break
                block.append(next_line.strip())
                index += 1
            values[key] = (" " if folded else "\n").join(block).strip()
            continue
        values[key] = scalar_value(raw)
        index += 1
    return values, diagnostics


def check_skill_root(root: Path, checks: list[dict[str, Any]], metrics: dict[str, Any]) -> None:
    skill_files = [path for path in root.rglob("SKILL.md") if path.is_file() and not path.is_symlink()]
    if len(skill_files) != 1:
        add(checks, "skill/root-count", "fail", "SKILL.md", {"count": len(skill_files)}, "error", ["keep exactly one root SKILL.md"])
        return
    skill_md = skill_files[0]
    if skill_md.parent != root:
        add(checks, "skill/root-location", "fail", rel(skill_md, root), {}, "error", ["move SKILL.md to target root"])
    text = skill_md.read_text(encoding="utf-8", errors="ignore")
    frontmatter, parse_diagnostics = parse_frontmatter(text)
    if parse_diagnostics:
        add(
            checks,
            "skill/frontmatter-parser",
            "warn",
            "SKILL.md",
            {"diagnostics": parse_diagnostics},
            "warning",
            ["prefer simple valid YAML frontmatter or validate with skills-ref"],
        )
    name = frontmatter.get("name", "")
    description = frontmatter.get("description", "")
    if not name:
        add(checks, "skill/name", "fail", "SKILL.md", {"present": False}, "error", ["add non-empty name"])
    else:
        valid_name = bool(NAME_PATTERN.fullmatch(name)) and 1 <= len(name) <= 64
        add(
            checks,
            "skill/name-format",
            "pass" if valid_name else "fail",
            "SKILL.md",
            {"name": name, "length": len(name)},
            "info" if valid_name else "error",
            ["use lowercase letters, digits, and single hyphens; maximum 64 characters"] if not valid_name else [],
        )
        matches_dir = name == root.name
        add(
            checks,
            "skill/name-directory-match",
            "pass" if matches_dir else "fail",
            "SKILL.md",
            {"name": name, "directory": root.name},
            "info" if matches_dir else "error",
            ["make frontmatter.name match the skill directory name"] if not matches_dir else [],
        )
    valid_description = bool(description.strip()) and len(description) <= 1024
    add(
        checks,
        "skill/description",
        "pass" if valid_description else "fail",
        "SKILL.md",
        {"present": bool(description.strip()), "length": len(description)},
        "info" if valid_description else "error",
        ["use a non-empty description of at most 1024 characters"] if not valid_description else [],
    )

    body = text.split("---", 2)[-1] if text.startswith("---") else text
    line_count = len(text.splitlines())
    estimated_tokens = math.ceil(len(text.encode("utf-8")) / 4)
    metrics["skill_md_lines"] = line_count
    metrics["skill_md_estimated_tokens"] = estimated_tokens
    metrics["skill_md_body_chars"] = len(body)
    if line_count > 500:
        add(checks, "context/skill-lines", "warn", "SKILL.md", {"lines": line_count, "recommended_max": 500}, "warning", ["move branch detail to focused references"])
    if estimated_tokens > 5000:
        add(checks, "context/skill-tokens", "warn", "SKILL.md", {"estimated_tokens": estimated_tokens, "recommended_max": 5000}, "warning", ["reduce control-plane context and use progressive references"])


def check_reference_validator(root: Path, checks: list[dict[str, Any]], metrics: dict[str, Any]) -> None:
    executable = shutil.which("skills-ref")
    if not executable:
        metrics["skills_ref"] = "not-run"
        add(checks, "skill/skills-ref", "pass", "skills-ref", {"status": "not-run", "reason": "skills-ref not available"}, "info")
        return
    cp = subprocess.run([executable, "validate", str(root)], text=True, capture_output=True)
    metrics["skills_ref"] = "pass" if cp.returncode == 0 else "fail"
    add(
        checks,
        "skill/skills-ref",
        "pass" if cp.returncode == 0 else "fail",
        "skills-ref",
        {"exit_code": cp.returncode, "stdout": cp.stdout[-4000:], "stderr": cp.stderr[-4000:]},
        "info" if cp.returncode == 0 else "error",
        ["repair Agent Skills specification violations reported by skills-ref"] if cp.returncode else [],
    )


def check_placeholders(root: Path, checks: list[dict[str, Any]]) -> None:
    for path in sorted(root.rglob("*"), key=lambda p: p.relative_to(root).as_posix()):
        if path.is_symlink() or not path.is_file() or not is_text(path):
            continue
        if "assets" in path.parts and path.name.endswith(".template"):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if any(pattern.search(text) for pattern in PLACEHOLDER_PATTERNS):
            add(checks, "hygiene/placeholder", "warn", rel(path, root), {}, "warning", ["confirm marker is intentional or replace it"])


def check_package_hygiene(root: Path, checks: list[dict[str, Any]], metrics: dict[str, Any]) -> None:
    inventory = build_inventory(root)
    metrics["inventory_status_counts"] = inventory["status_counts"]
    weak_candidates = 0
    for item in inventory["entries"]:
        path = root / item["path"]
        if item["status"] == "generated":
            add(checks, "hygiene/generated-artifact", "fail", item["path"], {"signals": item.get("generated_signals", [])}, "error", ["remove reproducible generated/cache residue"])
        elif any(signal.get("strength") == "weak" for signal in item.get("generated_signals", [])):
            weak_candidates += 1
            add(
                checks,
                "hygiene/generated-candidate",
                "warn",
                item["path"],
                {"signals": item.get("generated_signals", []), "status": item["status"]},
                "warning",
                ["collect generator/manifest/target evidence before classifying as generated"],
            )
        if path.is_file() and path.suffix.lower() in ARCHIVE_SUFFIXES:
            add(checks, "hygiene/archive", "fail", item["path"], {}, "error", ["move package/archive outside target"])
        if path.is_symlink():
            try:
                resolved = path.resolve(strict=False)
                outside = not resolved.is_relative_to(root.resolve(strict=True))
            except (OSError, RuntimeError):
                outside = True
                resolved = path
            add(
                checks,
                "path/symlink-escape" if outside else "path/symlink-present",
                "fail" if outside else "warn",
                item["path"],
                {"resolved": str(resolved), "outside_target": outside},
                "error" if outside else "warning",
                ["replace symlink with a real in-package resource or review manually"],
            )
    metrics["weak_generated_candidate_count"] = weak_candidates

    graph = inventory["reference_graph"]
    depths = {"SKILL.md": 0} if "SKILL.md" in graph else {}
    queue = ["SKILL.md"] if "SKILL.md" in graph else []
    while queue:
        source = queue.pop(0)
        for target in graph.get(source, []):
            next_depth = depths[source] + 1
            if target not in depths or next_depth < depths[target]:
                depths[target] = next_depth
                queue.append(target)
    max_depth = max(depths.values(), default=0)
    metrics["max_reference_depth_from_skill_md"] = max_depth
    metrics["reference_edge_count"] = len(inventory.get("reference_edges", []))
    metrics["root_count"] = len(inventory.get("root_registry", []))
    if max_depth > 1:
        add(
            checks,
            "context/reference-depth",
            "warn",
            "SKILL.md",
            {"max_depth": max_depth, "recommended_max": 1},
            "warning",
            ["prefer direct SKILL.md links to focused supporting resources"],
        )


def iter_local_links(text: str) -> list[str]:
    links = list(INLINE_LINK_PATTERN.findall(text))
    for left, right in REFERENCE_DEF_PATTERN.findall(text):
        links.append(left or right)
    return links


def check_markdown_links(root: Path, checks: list[dict[str, Any]]) -> None:
    for path in sorted(root.rglob("*.md"), key=lambda p: p.relative_to(root).as_posix()):
        if path.is_symlink():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for link in iter_local_links(text):
            if link.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target = link.strip().strip("<>").split("#", 1)[0]
            if not target:
                continue
            candidate = (path.parent / target).resolve(strict=False)
            try:
                candidate.relative_to(root.resolve(strict=True))
            except ValueError:
                add(checks, "link/outside-target", "warn", rel(path, root), {"link": link}, "warning", ["use an explicit external URL or in-package path"])
                continue
            if not candidate.exists():
                add(checks, "link/broken-local", "fail", rel(path, root), {"link": link}, "error", ["restore target or update link"])


def check_python_scripts(root: Path, checks: list[dict[str, Any]]) -> None:
    for path in sorted(root.rglob("*.py"), key=lambda p: p.relative_to(root).as_posix()):
        if path.is_symlink():
            continue
        try:
            ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError as exc:
            add(checks, "python/syntax", "fail", rel(path, root), {"error": str(exc)}, "error", ["repair Python syntax"])


def validate(root: Path) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    metrics: dict[str, Any] = {}
    check_skill_root(root, checks, metrics)
    check_reference_validator(root, checks, metrics)
    check_placeholders(root, checks)
    check_package_hygiene(root, checks, metrics)
    check_markdown_links(root, checks)
    check_python_scripts(root, checks)
    errors = [check for check in checks if check["status"] == "fail"]
    warnings = [check for check in checks if check["status"] == "warn"]
    return {
        "receipt_version": 3,
        "target": str(root),
        "status": "pass" if not errors else "fail",
        "stage": "validation",
        "checks": checks,
        "summary": {"error_count": len(errors), "warning_count": len(warnings), "check_count": len(checks)},
        "metrics": metrics,
        "hashes": {"target_tree_sha256": tree_hash(root)},
        "evidence_boundary": "structural-static; target-owned runtime/behavioral validation is separate unless explicitly executed by cleanup_apply validation_commands",
    }


def write_json_atomic(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        fh.write(json.dumps(data, indent=2, sort_keys=True) + "\n")
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate cleanup package structure.")
    parser.add_argument("--target", required=True, help="Target skill folder.")
    parser.add_argument("--output", help="Optional JSON output path; must be outside target.")
    parser.add_argument("--allow-warnings", action="store_true", help="Compatibility flag; warnings are non-blocking by default.")
    args = parser.parse_args()

    root = Path(args.target).resolve(strict=True)
    if not root.is_dir():
        raise SystemExit(f"target is not a directory: {root}")

    report = validate(root)
    if args.output:
        output = Path(args.output).resolve(strict=False)
        if output == root or root in output.parents:
            raise SystemExit("output must be outside the target package")
        write_json_atomic(output, report)
        print(f"wrote validation: {output}")
    else:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if report["status"] == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
