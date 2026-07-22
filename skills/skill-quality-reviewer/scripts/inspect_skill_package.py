#!/usr/bin/env python3
"""Deterministic structural preflight for a skill package.

This script reports objective package signals. It intentionally does not assign
semantic quality scores or perform security analysis.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
import tempfile
import zipfile
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

IGNORED_DIRS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "venv",
    "node_modules",
}
PLACEHOLDER_RE = re.compile(r"(?i)(\bTO" r"DO\b|\bTBD\b|\bFIXME\b|\bXXX\b|\[TO" r"DO[:\]])")
MD_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


@dataclass
class Finding:
    code: str
    severity: str
    evidence_status: str
    path: str
    message: str
    suggestion: str


class InspectionError(RuntimeError):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect a skill package for structural quality signals.")
    parser.add_argument("target", help="Skill folder, SKILL.md path, or ZIP archive")
    parser.add_argument("--json-out", help="Write the complete report to this JSON file")
    parser.add_argument("--strict", action="store_true", help="Return non-zero when MAJOR or BLOCKER findings exist")
    return parser.parse_args()


def is_ignored(path: Path) -> bool:
    return any(part in IGNORED_DIRS for part in path.parts)


def safe_extract_zip(archive: Path, destination: Path) -> None:
    with zipfile.ZipFile(archive) as zf:
        for member in zf.infolist():
            member_path = Path(member.filename)
            if member_path.is_absolute() or ".." in member_path.parts:
                raise InspectionError(f"Archive contains an invalid member path: {member.filename}")
        zf.extractall(destination)


def resolve_root(target: Path, temporary_root: Path | None = None) -> tuple[Path, str]:
    source_kind = "directory"
    candidate = target
    if target.is_file() and target.suffix.lower() == ".zip":
        if temporary_root is None:
            raise InspectionError("Temporary extraction root was not provided")
        safe_extract_zip(target, temporary_root)
        candidate = temporary_root
        source_kind = "zip"
    elif target.is_file() and target.name == "SKILL.md":
        return target.parent.resolve(), "skill-file"
    elif not target.exists():
        raise InspectionError(f"Target does not exist: {target}")
    elif not target.is_dir():
        raise InspectionError("Target must be a skill directory, SKILL.md, or ZIP archive")

    roots = [
        path.parent.resolve()
        for path in candidate.rglob("SKILL.md")
        if not is_ignored(path.relative_to(candidate))
    ]
    unique_roots = sorted(set(roots))
    if len(unique_roots) != 1:
        raise InspectionError(
            f"Expected exactly one SKILL.md root, found {len(unique_roots)}: "
            + ", ".join(str(root) for root in unique_roots[:10])
        )
    return unique_roots[0], source_kind


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def strip_fenced_code(text: str) -> str:
    """Remove fenced code content while preserving line count."""
    output: list[str] = []
    in_fence = False
    fence_marker = ""
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith(("```", "~~~")):
            marker = stripped[:3]
            if not in_fence:
                in_fence = True
                fence_marker = marker
            elif marker == fence_marker:
                in_fence = False
                fence_marker = ""
            output.append("")
            continue
        output.append("" if in_fence else line)
    return "\n".join(output)


def iter_files(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*")):
        if path.is_file() and not is_ignored(path.relative_to(root)):
            yield path


def parse_frontmatter(text: str) -> tuple[dict[str, str], list[str]]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, []
    try:
        end = next(index for index in range(1, len(lines)) if lines[index].strip() == "---")
    except StopIteration:
        return {}, []

    raw = lines[1:end]
    data: dict[str, str] = {}
    current_key: str | None = None
    for line in raw:
        match = re.match(r"^([A-Za-z0-9_-]+)\s*:\s*(.*)$", line)
        if match:
            current_key = match.group(1)
            data[current_key] = match.group(2).strip().strip('"\'')
        elif current_key and (line.startswith(" ") or line.startswith("\t")):
            data[current_key] = (data[current_key] + " " + line.strip()).strip()
    return data, raw


def local_link_target(raw_target: str) -> str | None:
    value = raw_target.strip().split("#", 1)[0].strip()
    if not value or value.startswith(("#", "http://", "https://", "mailto:", "data:")):
        return None
    if " " in value and not value.startswith("<"):
        value = value.split(" ", 1)[0]
    return value.strip("<>")


def add(findings: list[Finding], code: str, severity: str, path: str, message: str, suggestion: str,
        evidence_status: str = "confirmed") -> None:
    findings.append(Finding(code, severity, evidence_status, path, message, suggestion))


def inspect(root: Path, source_kind: str) -> dict[str, object]:
    findings: list[Finding] = []
    files = list(iter_files(root))
    relative_files = [path.relative_to(root).as_posix() for path in files]
    skill_path = root / "SKILL.md"
    skill_text = read_text(skill_path)

    frontmatter, raw_frontmatter = parse_frontmatter(skill_text)
    if not raw_frontmatter:
        add(findings, "FM001", "BLOCKER", "SKILL.md", "Missing or unterminated YAML frontmatter.",
            "Add a frontmatter block containing only name and description.")
    else:
        name = frontmatter.get("name", "").strip()
        description = frontmatter.get("description", "").strip()
        if not name:
            add(findings, "FM002", "BLOCKER", "SKILL.md", "Frontmatter is missing name.",
                "Add a lowercase hyphen-case name matching the skill folder intent.")
        elif not NAME_RE.fullmatch(name):
            add(findings, "FM003", "MAJOR", "SKILL.md", f"Invalid skill name format: {name!r}.",
                "Use lowercase letters, digits, and single hyphens only.")
        elif root.name != name:
            add(findings, "FM004", "MINOR", "SKILL.md", f"Frontmatter name {name!r} differs from folder {root.name!r}.",
                "Align the folder and frontmatter name unless the platform explicitly permits a difference.")
        if not description:
            add(findings, "FM005", "BLOCKER", "SKILL.md", "Frontmatter is missing description.",
                "Add a description that states capability, triggers, and non-activation boundaries.")
        else:
            lower = description.lower()
            trigger_signals = ("use when", "use for", "when asked", "use this skill", "use quando", "usar quando")
            boundary_signals = ("do not use", "not for", "não use", "nao use", "não utilizar", "nao utilizar")
            if not any(signal in lower for signal in trigger_signals):
                add(findings, "FM006", "MINOR", "SKILL.md", "Description has no explicit usage trigger phrase.",
                    "State concrete requests, artifacts, or contexts that should activate the skill.", "likely")
            if not any(signal in lower for signal in boundary_signals):
                add(findings, "FM007", "MINOR", "SKILL.md", "Description has no explicit non-activation boundary.",
                    "Name adjacent work the skill should not own.", "likely")
            if len(description) < 80:
                add(findings, "FM008", "MINOR", "SKILL.md", "Description is unusually short for a reliable activation surface.",
                    "Add concrete triggers and boundaries without turning the description into a workflow.", "likely")
        extra_keys = sorted(set(frontmatter) - {"name", "description"})
        if extra_keys:
            add(findings, "FM009", "MINOR", "SKILL.md", f"Unexpected frontmatter keys: {', '.join(extra_keys)}.",
                "Retain only name and description unless the active platform contract requires more.")

    metadata_path = root / "agents" / "openai.yaml"
    if not metadata_path.exists():
        add(findings, "META001", "MINOR", "agents/openai.yaml", "ChatGPT UI metadata file is absent.",
            "Add agents/openai.yaml when the package targets ChatGPT.", "likely")
    else:
        metadata = read_text(metadata_path)
        if "display_name:" not in metadata:
            add(findings, "META002", "MINOR", "agents/openai.yaml", "display_name is missing.",
                "Add a human-readable display name.")
        if "short_description:" not in metadata:
            add(findings, "META003", "MINOR", "agents/openai.yaml", "short_description is missing.",
                "Add a concise user-facing capability summary.")

    all_markdown_links: dict[str, set[str]] = {}
    for path in files:
        relative = path.relative_to(root).as_posix()
        if path.suffix.lower() not in {".md", ".markdown"}:
            continue
        text = read_text(path)
        semantic_text = strip_fenced_code(text)
        targets: set[str] = set()
        for match in MD_LINK_RE.finditer(semantic_text):
            raw = local_link_target(match.group(1))
            if raw is None:
                continue
            resolved = (path.parent / raw).resolve()
            targets.add(raw)
            try:
                resolved.relative_to(root.resolve())
            except ValueError:
                add(findings, "LINK001", "MAJOR", relative, f"Local link escapes the skill root: {raw}",
                    "Reference a file packaged under the skill root.")
                continue
            if not resolved.exists():
                add(findings, "LINK002", "MAJOR", relative, f"Broken local link: {raw}",
                    "Create the referenced file or update/remove the link.")
        all_markdown_links[relative] = targets

        headings: dict[str, int] = {}
        for line in semantic_text.splitlines():
            heading = HEADING_RE.match(line)
            if heading:
                normalized = re.sub(r"\s+", " ", heading.group(2).strip().lower())
                headings[normalized] = headings.get(normalized, 0) + 1
        duplicates = sorted(name for name, count in headings.items() if count > 1)
        if duplicates:
            add(findings, "DOC001", "MINOR", relative,
                "Duplicate headings may create ambiguous references: " + ", ".join(duplicates[:5]),
                "Rename or consolidate duplicate sections when they represent different contracts.", "likely")

        if not path.name.endswith(".template"):
            placeholder_matches = sorted(set(match.group(0) for match in PLACEHOLDER_RE.finditer(semantic_text)))
            if placeholder_matches:
                severity = "MAJOR" if relative == "SKILL.md" else "MINOR"
                add(findings, "DOC002", severity, relative,
                    "Operational file contains placeholder markers: " + ", ".join(placeholder_matches[:5]),
                    "Resolve the placeholders or move intentional fillable content into a .template asset.")

    direct_skill_links = all_markdown_links.get("SKILL.md", set())
    directly_resolved: set[str] = set()
    for raw in direct_skill_links:
        resolved = (skill_path.parent / raw).resolve()
        if resolved.exists():
            try:
                directly_resolved.add(resolved.relative_to(root).as_posix())
            except ValueError:
                pass

    for relative in relative_files:
        if relative.startswith("references/") and relative.endswith((".md", ".markdown")) and relative not in directly_resolved:
            add(findings, "REF001", "QUESTION", relative,
                "Reference file is not linked directly from SKILL.md.",
                "Verify that the file is intentionally branch-loaded; otherwise link, integrate, or remove it.",
                "needs verification")

    operational_candidates = [
        relative for relative in relative_files
        if relative != "SKILL.md"
        and not relative.startswith("agents/")
        and not relative.startswith("assets/templates/")
        and not relative.endswith(".svg")
    ]
    referenced_anywhere: set[str] = set()
    for source, raw_targets in all_markdown_links.items():
        source_path = root / source
        for raw in raw_targets:
            resolved = (source_path.parent / raw).resolve()
            if resolved.exists():
                try:
                    referenced_anywhere.add(resolved.relative_to(root).as_posix())
                except ValueError:
                    pass
    for relative in operational_candidates:
        if relative.startswith(("references/", "scripts/", "examples/", "evals/")) and relative not in referenced_anywhere:
            add(findings, "RES001", "QUESTION", relative,
                "File is not referenced by Markdown instructions.",
                "Verify whether a script, platform convention, or maintainer workflow consumes it before treating it as orphaned.",
                "needs verification")

    for path in files:
        relative = path.relative_to(root).as_posix()
        if path.suffix.lower() == ".py":
            try:
                ast.parse(read_text(path), filename=relative)
            except SyntaxError as exc:
                add(findings, "PY001", "MAJOR", relative,
                    f"Python syntax error at line {exc.lineno}: {exc.msg}",
                    "Repair syntax and rerun py_compile or the script's smoke test.")

        if any(part in IGNORED_DIRS for part in Path(relative).parts):
            add(findings, "PKG001", "MINOR", relative, "Cache or dependency directory is included in the package.",
                "Exclude generated caches and vendored dependency folders from the final archive.")
        if path.suffix.lower() in {".zip", ".tar", ".gz", ".tgz"}:
            add(findings, "PKG002", "MINOR", relative, "Nested archive is present inside the skill package.",
                "Remove old packages or justify an intentional runtime asset.", "likely")
        if path.suffix.lower() in {".pyc", ".pyo"} or path.name == ".DS_Store":
            add(findings, "PKG003", "MINOR", relative, "Generated package noise is present.",
                "Remove generated files before packaging.")

    eval_path = root / "evals" / "activation-scenarios.json"
    eval_categories: list[str] = []
    if not eval_path.exists():
        add(findings, "EVAL001", "MINOR", "evals/activation-scenarios.json",
            "Activation scenario suite is absent.",
            "Add planned activation, non-activation, ambiguous, and edge scenarios when activation quality matters.", "likely")
    else:
        try:
            payload = json.loads(read_text(eval_path))
            scenarios = payload.get("scenarios", []) if isinstance(payload, dict) else payload
            if not isinstance(scenarios, list):
                raise ValueError("scenarios must be a list")
            eval_categories = sorted({
                str(item.get("category") or item.get("type") or "")
                for item in scenarios if isinstance(item, dict)
            })
            required_categories = {"should_activate", "should_not_activate", "ambiguous", "edge_case"}
            missing = sorted(required_categories - set(eval_categories))
            if missing:
                add(findings, "EVAL002", "MINOR", "evals/activation-scenarios.json",
                    "Activation scenario categories are missing: " + ", ".join(missing),
                    "Add representative planned cases for each missing category.")
        except (json.JSONDecodeError, ValueError) as exc:
            add(findings, "EVAL003", "MAJOR", "evals/activation-scenarios.json",
                f"Activation scenario file is invalid: {exc}",
                "Repair JSON and scenario schema before using it as coverage evidence.")

    lower_skill = skill_text.lower()
    section_signals = {
        "mission_or_scope": ("## mission", "## scope", "## missão", "## missao", "## escopo"),
        "workflow": ("## workflow", "## fluxo", "## process"),
        "resource_loading": ("## resource loading", "## resources", "## carregamento de recursos", "## recursos"),
        "output_contract": ("## output contract", "## contrato de saída", "## contrato de saida"),
        "stop_conditions": ("## stop conditions", "## condições de parada", "## condicoes de parada"),
    }
    section_coverage = {
        key: any(signal in lower_skill for signal in signals)
        for key, signals in section_signals.items()
    }

    token_estimates = {
        path.relative_to(root).as_posix(): max(1, round(len(read_text(path)) / 4))
        for path in files
        if path.suffix.lower() in {".md", ".markdown", ".json", ".yaml", ".yml", ".py"}
    }

    severity_rank = {"BLOCKER": 0, "MAJOR": 1, "MINOR": 2, "QUESTION": 3, "NIT": 4}
    findings.sort(key=lambda item: (severity_rank.get(item.severity, 9), item.path, item.code))
    counts = {severity: sum(1 for item in findings if item.severity == severity)
              for severity in ("BLOCKER", "MAJOR", "MINOR", "QUESTION", "NIT")}

    return {
        "schema_version": "1.0",
        "target_root": str(root),
        "source_kind": source_kind,
        "inventory": {
            "file_count": len(relative_files),
            "files": relative_files,
            "section_coverage": section_coverage,
            "activation_scenario_categories": eval_categories,
            "token_estimate_by_file": token_estimates,
            "token_estimate_total": sum(token_estimates.values()),
        },
        "finding_counts": counts,
        "findings": [asdict(item) for item in findings],
        "interpretation": "Structural preflight only. Candidate orphan and heuristic findings require semantic verification.",
    }


def print_summary(report: dict[str, object]) -> None:
    counts = report["finding_counts"]
    print(f"Target: {report['target_root']}")
    print(f"Files: {report['inventory']['file_count']}")
    print("Findings: " + ", ".join(f"{key}={value}" for key, value in counts.items()))
    for item in report["findings"]:
        print(f"[{item['severity']}] {item['code']} {item['path']}: {item['message']}")


def main() -> int:
    args = parse_args()
    target = Path(args.target).expanduser().resolve()
    try:
        with tempfile.TemporaryDirectory(prefix="skill-review-") as temporary:
            root, source_kind = resolve_root(target, Path(temporary))
            report = inspect(root, source_kind)
    except (InspectionError, zipfile.BadZipFile, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print_summary(report)
    if args.json_out:
        output = Path(args.json_out).expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"JSON report: {output}")

    if args.strict:
        counts = report["finding_counts"]
        if counts["BLOCKER"] or counts["MAJOR"]:
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
