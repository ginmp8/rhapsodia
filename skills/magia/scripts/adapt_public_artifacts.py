#!/usr/bin/env python3
"""Normalize supported public SDD artifact folders into a read-only execution view."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

TASK_RE = re.compile(r"^\s*[-*]\s+\[(?P<mark>[ xX])\]\s+", re.MULTILINE)
KINDS = {"spec-kit", "kiro", "openspec"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*") if path.is_file() and path.suffix.lower() in {".md", ".yaml", ".yml", ".json"})


def detect_kind(root: Path, files: list[Path]) -> str:
    names = {path.name.lower() for path in files}
    parts = {part.lower() for path in files for part in path.relative_to(root).parts}
    if ".kiro" in parts or "requirements.md" in names:
        return "kiro"
    if "proposal.md" in names or "openspec" in parts:
        return "openspec"
    if ".specify" in parts or "spec.md" in names:
        return "spec-kit"
    raise ValueError("unable to detect adapter kind; pass --kind explicitly")


def classify(kind: str, relative: str) -> str:
    name = Path(relative).name.lower()
    if kind == "spec-kit":
        return {"spec.md": "requirements", "plan.md": "design", "tasks.md": "tasks"}.get(name, "constraints")
    if kind == "kiro":
        return {"requirements.md": "requirements", "design.md": "design", "tasks.md": "tasks"}.get(name, "constraints")
    if name == "proposal.md":
        return "requirements"
    if name == "design.md":
        return "design"
    if name == "tasks.md":
        return "tasks"
    if "spec" in Path(relative).parts or "specs" in Path(relative).parts:
        return "deltas"
    return "constraints"


def adapt(root: Path, kind: str) -> dict[str, Any]:
    files = source_files(root)
    selected = detect_kind(root, files) if kind == "auto" else kind
    if selected not in KINDS:
        raise ValueError(f"unsupported kind: {selected}")
    records: list[dict[str, Any]] = []
    categories: dict[str, list[str]] = {"requirements": [], "design": [], "tasks": [], "deltas": [], "constraints": []}
    task_total = 0
    task_complete = 0
    for path in files:
        relative = path.relative_to(root).as_posix()
        category = classify(selected, relative)
        text = path.read_text(encoding="utf-8-sig")
        matches = list(TASK_RE.finditer(text)) if category == "tasks" else []
        completed = sum(1 for match in matches if match.group("mark").lower() == "x")
        task_total += len(matches)
        task_complete += completed
        categories[category].append(relative)
        records.append({
            "path": relative,
            "category": category,
            "size": path.stat().st_size,
            "sha256": sha256(path),
            "task_count": len(matches),
            "completed_task_count": completed,
        })
    expected = {
        "spec-kit": ["requirements", "design", "tasks"],
        "kiro": ["requirements", "design", "tasks"],
        "openspec": ["requirements", "tasks", "deltas"],
    }[selected]
    missing = [name for name in expected if not categories[name]]
    lossy: list[str] = []
    if categories["requirements"] and not categories["tasks"]:
        lossy.append("requirements have no mapped task artifact")
    if task_total and not categories["requirements"]:
        lossy.append("task checkboxes exist without a mapped requirement artifact")
    if selected == "openspec" and not categories["design"]:
        lossy.append("OpenSpec design artifact is absent or intentionally omitted")
    return {
        "schema_version": 1,
        "adapter": selected,
        "source_root": str(root),
        "read_only": True,
        "source_files": records,
        "execution_view": categories,
        "task_summary": {"total": task_total, "completed": task_complete},
        "missing_fields": missing,
        "lossy_mappings": lossy,
        "assumptions": ["checkbox state is not current implementation evidence", "original source paths remain authoritative"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True)
    parser.add_argument("--kind", choices=["auto", *sorted(KINDS)], default="auto")
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    try:
        root = Path(args.source).resolve()
        output = Path(args.output).resolve()
        if not root.is_dir():
            raise ValueError(f"source directory does not exist: {root}")
        try:
            output.relative_to(root)
        except ValueError:
            pass
        else:
            raise ValueError("output must be outside the read-only source directory")
        result = adapt(root, args.kind)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}, indent=2))
        return 1
    print(json.dumps({"status": "pass", "output": str(output), "adapter": result["adapter"], "missing_fields": result["missing_fields"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
