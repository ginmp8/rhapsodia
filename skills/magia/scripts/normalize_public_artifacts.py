#!/usr/bin/env python3
"""Normalize Spec Kit, Kiro, or OpenSpec Markdown into a read-only MAGIA execution view."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

TASK_RE = re.compile(r"^\s*[-*]\s+\[([ xX])\]\s+(.+?)\s*$")
HEADING_RE = re.compile(r"^(#{2,4})\s+(.+?)\s*$")
REQ_RE = re.compile(r"^(?:[-*]\s+)?(?:FR-\d+[:.]?\s*)?(.+\b(?:shall|must)\b.+)$", re.IGNORECASE)
EARS_RE = re.compile(r"^(?:WHEN|IF|WHILE|WHERE|THE SYSTEM SHALL)\b", re.IGNORECASE)
DELTA_RE = re.compile(r"^##\s+(ADDED|MODIFIED|REMOVED|RENAMED)\s+Requirements", re.IGNORECASE)
OPEN_REQ_RE = re.compile(r"^###\s+Requirement:\s*(.+)$", re.IGNORECASE)
SCENARIO_RE = re.compile(r"^####\s+Scenario:\s*(.+)$", re.IGNORECASE)


def ensure_safe_source(root: Path, path: Path) -> Path:
    if path.is_symlink():
        raise ValueError(f"symbolic links are not allowed in public artifact sources: {path}")
    resolved = path.resolve(strict=True)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"source path escapes artifact root: {path}") from exc
    if not resolved.is_file():
        raise ValueError(f"source path is not a file: {path}")
    return resolved


def sha256_file(path: Path, root: Path) -> str:
    return hashlib.sha256(ensure_safe_source(root, path).read_bytes()).hexdigest()


def rel(path: Path, root: Path) -> str:
    return ensure_safe_source(root, path).relative_to(root).as_posix()


def read_lines(path: Path, root: Path) -> list[str]:
    return ensure_safe_source(root, path).read_text(encoding="utf-8-sig").splitlines()


def extract_tasks(path: Path, root: Path) -> list[dict[str, Any]]:
    tasks: list[dict[str, Any]] = []
    if not path.is_file():
        return tasks
    for index, line in enumerate(read_lines(path, root), start=1):
        match = TASK_RE.match(line)
        if match:
            tasks.append({"id": f"task-{len(tasks)+1:03d}", "text": match.group(2), "completed": match.group(1).lower() == "x", "source": f"{rel(path, root)}:{index}"})
    return tasks


def extract_generic_requirements(path: Path, root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    requirements: list[dict[str, Any]] = []
    criteria: list[dict[str, Any]] = []
    if not path.is_file():
        return requirements, criteria
    for index, raw in enumerate(read_lines(path, root), start=1):
        line = raw.strip()
        heading = HEADING_RE.match(line)
        if heading and any(token in heading.group(2).lower() for token in ("requirement", "user story", "current behavior", "expected behavior", "unchanged behavior")):
            requirements.append({"id": f"req-{len(requirements)+1:03d}", "text": heading.group(2), "source": f"{rel(path, root)}:{index}"})
        if EARS_RE.match(line) or REQ_RE.match(line):
            criteria.append({"id": f"ac-{len(criteria)+1:03d}", "text": line, "source": f"{rel(path, root)}:{index}"})
    return requirements, criteria


def detect_format(root: Path) -> str:
    if any(path.is_file() for path in (root / "requirements.md", root / "bugfix.md")):
        for path in (root / "requirements.md", root / "bugfix.md"):
            if path.exists():
                ensure_safe_source(root, path)
        return "kiro"
    if (root / "proposal.md").is_file() and (root / "specs").is_dir():
        ensure_safe_source(root, root / "proposal.md")
        if (root / "specs").is_symlink():
            raise ValueError("symbolic links are not allowed for specs directories")
        return "openspec"
    if (root / "spec.md").is_file() and (root / "tasks.md").is_file():
        ensure_safe_source(root, root / "spec.md")
        ensure_safe_source(root, root / "tasks.md")
        return "spec-kit"
    raise ValueError("cannot auto-detect supported artifact format")


def normalize_spec_kit(root: Path) -> dict[str, Any]:
    reqs, criteria = extract_generic_requirements(root / "spec.md", root)
    files = [path for path in (root / "spec.md", root / "plan.md", root / "tasks.md") if path.is_file()]
    missing = [name for name in ("spec.md", "plan.md", "tasks.md") if not (root / name).is_file()]
    return {
        "requirements": reqs,
        "acceptance_criteria": criteria,
        "tasks": extract_tasks(root / "tasks.md", root),
        "design_sources": ["plan.md"] if (root / "plan.md").is_file() else [],
        "delta_operations": [],
        "source_paths": files,
        "missing_fields": missing,
        "lossy_mappings": ["cross-artifact requirement-to-task links are not explicit and must be converged against repository evidence"],
    }


def normalize_kiro(root: Path) -> dict[str, Any]:
    requirements_file = root / "requirements.md" if (root / "requirements.md").is_file() else root / "bugfix.md"
    reqs, criteria = extract_generic_requirements(requirements_file, root)
    files = [path for path in (requirements_file, root / "design.md", root / "tasks.md") if path.is_file()]
    missing = [name for name, path in (("requirements.md or bugfix.md", requirements_file), ("design.md", root / "design.md"), ("tasks.md", root / "tasks.md")) if not path.is_file()]
    return {
        "requirements": reqs,
        "acceptance_criteria": criteria,
        "tasks": extract_tasks(root / "tasks.md", root),
        "design_sources": ["design.md"] if (root / "design.md").is_file() else [],
        "delta_operations": [],
        "source_paths": files,
        "missing_fields": missing,
        "lossy_mappings": ["design diagrams and property-test relationships remain source references rather than normalized structures"],
    }


def normalize_openspec(root: Path) -> dict[str, Any]:
    requirements: list[dict[str, Any]] = []
    criteria: list[dict[str, Any]] = []
    operations: list[dict[str, Any]] = []
    files = [path for path in (root / "proposal.md", root / "design.md", root / "tasks.md") if path.is_file()]
    spec_files = sorted((root / "specs").rglob("*.md")) if (root / "specs").is_dir() else []
    files.extend(spec_files)
    for path in spec_files:
        operation = "unspecified"
        current_req: str | None = None
        for index, raw in enumerate(read_lines(path, root), start=1):
            line = raw.strip()
            delta = DELTA_RE.match(line)
            if delta:
                operation = delta.group(1).lower()
                continue
            req = OPEN_REQ_RE.match(line)
            if req:
                current_req = f"req-{len(requirements)+1:03d}"
                requirements.append({"id": current_req, "text": req.group(1), "operation": operation, "source": f"{rel(path, root)}:{index}"})
                operations.append({"requirement_id": current_req, "operation": operation})
                continue
            scenario = SCENARIO_RE.match(line)
            if scenario:
                criteria.append({"id": f"ac-{len(criteria)+1:03d}", "text": scenario.group(1), "requirement_id": current_req, "source": f"{rel(path, root)}:{index}"})
    missing = [name for name in ("proposal.md", "tasks.md", "specs/") if not ((root / name).is_file() or (root / name).is_dir())]
    return {
        "requirements": requirements,
        "acceptance_criteria": criteria,
        "tasks": extract_tasks(root / "tasks.md", root),
        "design_sources": ["design.md"] if (root / "design.md").is_file() else [],
        "delta_operations": operations,
        "source_paths": files,
        "missing_fields": missing,
        "lossy_mappings": ["proposal rationale and free-form design details remain source references; delta operations are preserved"],
    }


def normalize(root: Path, source_format: str) -> dict[str, Any]:
    root = root.resolve()
    if not root.is_dir():
        raise ValueError(f"source root is not a directory: {root}")
    fmt = detect_format(root) if source_format == "auto" else source_format
    if fmt == "spec-kit":
        body = normalize_spec_kit(root)
    elif fmt == "kiro":
        body = normalize_kiro(root)
    elif fmt == "openspec":
        body = normalize_openspec(root)
    else:
        raise ValueError("format must be auto, spec-kit, kiro, or openspec")
    source_files = [{"path": rel(path, root), "sha256": sha256_file(path, root)} for path in sorted(set(body.pop("source_paths")))]
    return {"schema_version": 1, "read_only": True, "source_format": fmt, "source_root": str(root), "source_files": source_files, **body}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Normalize public SDD artifacts into a MAGIA execution view.")
    parser.add_argument("--source", required=True, help="Artifact root directory.")
    parser.add_argument("--format", default="auto", choices=["auto", "spec-kit", "kiro", "openspec"])
    parser.add_argument("--output", required=True, help="Output JSON path; source files are never modified.")
    args = parser.parse_args(argv)
    try:
        result = normalize(Path(args.source), args.format)
        source_root = Path(args.source).resolve()
        output = Path(args.output).resolve()
        if output.is_symlink():
            raise ValueError("output path must not be a symbolic link")
        try:
            output.relative_to(source_root)
        except ValueError:
            pass
        else:
            raise ValueError("output must be outside the read-only source root")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"status: pass\nformat: {result['source_format']}\noutput: {output}")
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"status: fail\nerror: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
