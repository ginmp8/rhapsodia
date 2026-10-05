#!/usr/bin/env python3
"""Structural and portability quality gate for Skill Creator Juiced packages."""
from __future__ import annotations

import argparse
import sys
sys.dont_write_bytecode = True
import json
import re
from pathlib import Path

from skill_spec import read_text, validate_agent_skill
from validate_portability import normalize_hosts, normalize_surfaces, validate_portability

PLACEHOLDER_PATTERNS = [
    "TO" + "DO",
    "[" + "TO" + "DO",
    "replace" + " with actual",
    "placeholder" + " script",
    "example" + " asset",
    "api_" + "reference.md",
]
REQUIRED_BODY_TERMS = ["workflow", "output contract", "stop condition"]
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
TEXT_SUFFIXES = {".md", ".txt", ".py", ".yaml", ".yml", ".json", ".template", ".sh"}
ACTIVATION_GROUPS = {"activation", "non-activation", "ambiguous", "boundary", "adversarial", "holdout"}
ACTIVATION_ROUTES = {
    "activate", "do-not-activate", "conditional", "activate-constrained", "split-handoff",
    "reject-scope-weakening", "reject-fabricated-evidence", "reject-ownership-expansion",
}
ACTIVATION_CONTRACT_ID = re.compile(r"^[A-Z]{2,5}-\d{3}$")
TOP100_LIMIT = 100
TOP100_BOUNDARY_TERMS = ("activation", "routing", "scope", "use when", "do not use", "modes", "mode selection")
TOP100_EXECUTION_TERMS = ("workflow", "quick start", "procedure", "process", "steps", "execution")
TOP100_RULE_TERMS = ("core rules", "rules", "constraints", "guardrails", "invariants", "requirements")
PREVIEW_SUMMARY_HEADINGS = {"at a glance", "summary", "quick reference", "overview"}
PREVIEW_CONTENTS_HEADINGS = {"contents", "table of contents", "section map"}
PREVIEW_EXCEPTION_RE = re.compile(
    r"<!--\s*context-preview-exception:\s*(generated|vendor|unsafe-to-rewrite)\s*-->",
    re.IGNORECASE,
)
MARKDOWN_HEADING_RE = re.compile(r"^\s{0,3}(#{1,6})\s+(.+?)\s*#*\s*$")
CONTENTS_ITEM_RE = re.compile(r"^\s*[-*+]\s+(?:\[([^\]]+)\]\([^)]+\)|(.+?))\s*$")


def normalize_heading_label(value: str) -> str:
    value = re.sub(r"`([^`]*)`", r"\1", value)
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
    value = re.sub(r"<[^>]+>", "", value)
    value = re.sub(r"[*_~]", "", value)
    return re.sub(r"\s+", " ", value).strip()


def visible_markdown_lines(lines: list[str]):
    in_fence = False
    fence_char: str | None = None
    for index, line in enumerate(lines):
        stripped = line.lstrip()
        fence = re.match(r"(`{3,}|~{3,})", stripped)
        if fence:
            marker_char = fence.group(1)[0]
            if not in_fence:
                in_fence = True
                fence_char = marker_char
            elif marker_char == fence_char:
                in_fence = False
                fence_char = None
            continue
        if not in_fence:
            yield index, line


def h2_headings(lines: list[str]) -> list[tuple[int, str]]:
    headings: list[tuple[int, str]] = []
    for index, line in visible_markdown_lines(lines):
        match = MARKDOWN_HEADING_RE.match(line)
        if match and len(match.group(1)) == 2:
            headings.append((index, normalize_heading_label(match.group(2))))
    return headings


def contents_entries(lines: list[str], contents_index: int) -> list[str]:
    entries: list[str] = []
    for _index, line in visible_markdown_lines(lines[contents_index + 1 :]):
        if MARKDOWN_HEADING_RE.match(line):
            break
        if not line.strip():
            continue
        match = CONTENTS_ITEM_RE.match(line)
        if match:
            entries.append(normalize_heading_label(match.group(1) or match.group(2)))
            continue
        if entries:
            break
        return []
    return entries


def validate_long_markdown_preview(md: Path, display_path: str) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    lines = read_text(md).splitlines()
    if len(lines) <= TOP100_LIMIT:
        return errors, warnings

    first40 = "\n".join(lines[:40])
    exception = PREVIEW_EXCEPTION_RE.search(first40)
    if exception:
        warnings.append(f"long markdown preview exception declared ({exception.group(1).lower()}): {display_path}")
        return errors, warnings

    headings = h2_headings(lines)
    summary_locations = [
        index for index, label in headings
        if index < 40 and label.casefold() in PREVIEW_SUMMARY_HEADINGS
    ]
    contents_locations = [
        index for index, label in headings
        if index < 40 and label.casefold() in PREVIEW_CONTENTS_HEADINGS
    ]
    if not summary_locations or not contents_locations or min(summary_locations) >= min(contents_locations):
        errors.append(
            f"long markdown requires an early summary followed by heading-derived contents within first 40 lines: {display_path}"
        )
        return errors, warnings

    contents_index = min(contents_locations)
    expected = [
        label for _index, label in headings
        if label.casefold() not in PREVIEW_SUMMARY_HEADINGS | PREVIEW_CONTENTS_HEADINGS
    ]
    actual = contents_entries(lines, contents_index)
    expected_norm = [label.casefold() for label in expected]
    actual_norm = [label.casefold() for label in actual]
    if actual_norm != expected_norm:
        errors.append(
            "long markdown contents do not match material H2 headings in document order: "
            f"{display_path}; expected={expected!r}; found={actual!r}"
        )
    return errors, warnings


def check_top100_contract(target: Path, skill_md: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    lines = read_text(skill_md).splitlines()
    if len(lines) > TOP100_LIMIT:
        first = "\n".join(lines[:TOP100_LIMIT]).lower()
        if not any(term in first for term in TOP100_BOUNDARY_TERMS):
            errors.append("Top-100 control plane lacks scope/activation/routing guidance")
        if not any(term in first for term in TOP100_EXECUTION_TERMS):
            errors.append("Top-100 control plane lacks workflow/quick-start execution guidance")
        if not any(term in first for term in TOP100_RULE_TERMS):
            errors.append("Top-100 control plane lacks material rules/constraints/invariants")

    direct_markdown: set[Path] = set()
    for raw in MARKDOWN_LINK_RE.findall(read_text(skill_md)):
        ref = raw.split("#", 1)[0].strip()
        if not ref or "://" in ref or ref.startswith(("#", "/", "mailto:")):
            continue
        resolved = (skill_md.parent / ref).resolve()
        if resolved.is_file() and resolved.suffix.lower() == ".md":
            direct_markdown.add(resolved)

    for md in sorted(target.rglob("*.md")):
        if md == skill_md or ".git" in md.parts:
            continue
        preview_errors, preview_warnings = validate_long_markdown_preview(md, md.relative_to(target).as_posix())
        errors.extend(preview_errors)
        warnings.extend(preview_warnings)

        for _source, _link, resolved in local_markdown_links(target, md):
            if resolved.suffix.lower() == ".md" and resolved != skill_md.resolve() and resolved not in direct_markdown:
                warnings.append(
                    f"reference chain is deeper than one level from SKILL.md: {md.relative_to(target)} -> {resolved.relative_to(target)}"
                )
    return errors, warnings


def validate_activation_suite_file(path: Path) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        return ["activation suite missing: evals/activation-scenarios.json"]
    try:
        data = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        return [f"activation suite invalid JSON: {exc}"]
    if not isinstance(data.get("suite_version"), str) or not data["suite_version"].strip():
        errors.append("activation suite requires non-empty suite_version")
    scenarios = data.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        return errors + ["activation suite requires non-empty scenarios"]
    seen: set[str] = set()
    groups: set[str] = set()
    for index, row in enumerate(scenarios):
        if not isinstance(row, dict):
            errors.append(f"activation scenario {index} must be an object")
            continue
        sid = row.get("id")
        if not isinstance(sid, str) or not sid.strip():
            errors.append(f"activation scenario {index} requires id")
        elif sid in seen:
            errors.append(f"activation scenario id duplicated: {sid}")
        else:
            seen.add(sid)
        group = row.get("group")
        if group not in ACTIVATION_GROUPS:
            errors.append(f"activation scenario {sid or index} has invalid group: {group}")
        else:
            groups.add(group)
        if not isinstance(row.get("prompt"), str) or not row["prompt"].strip():
            errors.append(f"activation scenario {sid or index} requires prompt")
        if row.get("expected_route") not in ACTIVATION_ROUTES:
            errors.append(f"activation scenario {sid or index} has invalid expected_route: {row.get('expected_route')}")
        contract_ids = row.get("contract_ids")
        if not isinstance(contract_ids, list) or not contract_ids:
            errors.append(f"activation scenario {sid or index} requires contract_ids")
        elif any(not isinstance(value, str) or not ACTIVATION_CONTRACT_ID.fullmatch(value) for value in contract_ids):
            errors.append(f"activation scenario {sid or index} has invalid contract_ids")
    missing = sorted(ACTIVATION_GROUPS - groups)
    if missing:
        errors.append("activation suite missing groups: " + ", ".join(missing))
    return errors


def local_markdown_links(target: Path, markdown_file: Path):
    text = read_text(markdown_file)
    for raw in MARKDOWN_LINK_RE.findall(text):
        ref = raw.split("#", 1)[0].strip()
        if not ref or "://" in ref or ref.startswith(("#", "/", "mailto:")):
            continue
        yield markdown_file, ref, (markdown_file.parent / ref).resolve()


def run_gate(target: Path, profile: str, hosts: str | None = None, surfaces: str | None = None) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    inspected: list[str] = []

    if not target.is_dir():
        return {"status": "fail", "profile": profile, "errors": [f"target is not a directory: {target}"], "warnings": [], "inspected": []}

    skill_files = [p for p in target.rglob("SKILL.md") if ".git" not in p.parts]
    if skill_files != [target / "SKILL.md"]:
        errors.append(f"expected exactly one root SKILL.md, found {len(skill_files)}")
        return {"status": "fail", "profile": profile, "errors": errors, "warnings": warnings, "inspected": [str(p) for p in skill_files]}

    portability = validate_agent_skill(target, profile)
    errors.extend(portability["errors"])
    warnings.extend(portability["warnings"])
    host_portability = None
    if hosts:
        host_portability = validate_portability(target, normalize_hosts(hosts), normalize_surfaces(surfaces))
        errors.extend(item["evidence"] for item in host_portability["errors"])
        warnings.extend(item["evidence"] for item in host_portability["warnings"])

    errors.extend(validate_activation_suite_file(target / "evals" / "activation-scenarios.json"))

    skill_md = target / "SKILL.md"
    inspected.append(str(skill_md))
    text = read_text(skill_md)
    lower_text = text.lower()
    for term in REQUIRED_BODY_TERMS:
        if term not in lower_text:
            warnings.append(f"SKILL.md does not visibly include '{term}'")

    line_count = len(text.splitlines())
    estimated_tokens = (len(text) + 3) // 4
    if line_count > 500:
        warnings.append(f"SKILL.md exceeds progressive-disclosure review threshold: {line_count} lines > 500")
    if estimated_tokens > 5000:
        warnings.append(f"SKILL.md exceeds approximate context review threshold: ~{estimated_tokens} tokens > 5000")

    top100_errors, top100_warnings = check_top100_contract(target, skill_md)
    errors.extend(top100_errors)
    warnings.extend(top100_warnings)

    directly_discoverable: set[str] = set()
    for raw in MARKDOWN_LINK_RE.findall(text):
        ref = raw.split("#", 1)[0].strip()
        if ref and not ref.startswith(("#", "/", "mailto:")) and "://" not in ref:
            resolved = (skill_md.parent / ref).resolve()
            if str(resolved).startswith(str(target.resolve())) and resolved.exists() and resolved.is_file():
                directly_discoverable.add(resolved.relative_to(target).as_posix())
    for file_path in target.rglob("*"):
        if file_path.is_file():
            rel = file_path.relative_to(target).as_posix()
            if rel in text:
                directly_discoverable.add(rel)

    refs_dir = target / "references"
    if refs_dir.exists():
        for file_path in sorted(refs_dir.rglob("*.md")):
            rel = file_path.relative_to(target).as_posix()
            if rel not in directly_discoverable:
                warnings.append(f"reference is not directly discoverable from SKILL.md: {rel}")

    for path in target.rglob("*"):
        if ".git" in path.parts:
            continue
        rel = path.relative_to(target)
        if "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"}:
            errors.append(f"cache/generated bytecode must not be packaged: {rel}")
            continue
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        content = read_text(path)
        if str(rel).startswith("assets/templates/"):
            continue
        for pattern in PLACEHOLDER_PATTERNS:
            if pattern.lower() in content.lower() or pattern.lower() in str(rel).lower():
                errors.append(f"placeholder/scaffold marker '{pattern}' found in {rel}")
                break

    for md in target.rglob("*.md"):
        inspected.append(str(md))
        for source, link, resolved in local_markdown_links(target, md):
            if not str(resolved).startswith(str(target.resolve())):
                errors.append(f"local link leaves package: {source.relative_to(target)} -> {link}")
            elif not resolved.exists():
                errors.append(f"broken local link: {source.relative_to(target)} -> {link}")

    referenced: set[str] = set()
    markdown_text = "\n".join(read_text(md) for md in target.rglob("*.md"))
    for file_path in target.rglob("*"):
        if file_path.is_file():
            rel = file_path.relative_to(target).as_posix()
            if rel in markdown_text:
                referenced.add(rel)

    for folder in ("references", "scripts"):
        dir_path = target / folder
        if not dir_path.exists():
            continue
        for file_path in dir_path.rglob("*"):
            if not file_path.is_file():
                continue
            rel = file_path.relative_to(target).as_posix()
            if rel not in referenced and file_path.name != "skill_spec.py":
                warnings.append(f"support file may be unreferenced: {rel}")

    return {
        "status": "pass" if not errors else "fail",
        "profile": profile,
        "errors": sorted(set(errors)),
        "warnings": sorted(set(warnings)),
        "inspected": sorted(set(inspected)),
        "portability": portability,
        "host_portability": host_portability,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run structural and portability gates for a skill package.")
    parser.add_argument("target", help="Path to a skill folder")
    parser.add_argument("--profile", choices=["portable", "openai"], default="portable")
    parser.add_argument("--hosts", help="Optional semantic profile matrix: portable-core,openai,codex,claude,copilot,cursor,all")
    parser.add_argument("--surfaces", help="Optional distribution/client surfaces or all")
    parser.add_argument("--json", dest="json_path", help="Optional JSON output path")
    args = parser.parse_args()

    report = run_gate(Path(args.target).resolve(), args.profile, args.hosts, args.surfaces)
    if args.json_path:
        out = Path(args.json_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
