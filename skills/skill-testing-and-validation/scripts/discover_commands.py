#!/usr/bin/env python3
"""Discover likely build, test, and lint commands for small polyglot projects.

The script is intentionally conservative: it reports command candidates and their
source instead of executing them.
"""
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def add(candidates: list[dict[str, str]], kind: str, command: str, source: str, confidence: str, notes: str = "") -> None:
    if not any(item["kind"] == kind and item["command"] == command for item in candidates):
        candidates.append({
            "kind": kind,
            "command": command,
            "source": source,
            "confidence": confidence,
            "notes": notes,
        })


def makefile_targets(path: Path) -> set[str]:
    makefile = path / "Makefile"
    if not makefile.exists():
        return set()
    text = makefile.read_text(encoding="utf-8", errors="replace")
    return set(re.findall(r"^([A-Za-z0-9_.-]+):(?:\s|$)", text, flags=re.MULTILINE))


def discover(root: Path) -> dict[str, Any]:
    root = root.resolve()
    candidates: list[dict[str, str]] = []
    markers: list[str] = []

    def marker(name: str) -> bool:
        exists = (root / name).exists()
        if exists:
            markers.append(name)
        return exists

    package_json = root / "package.json"
    if package_json.exists():
        markers.append("package.json")
        data = read_json(package_json)
        scripts = data.get("scripts") if isinstance(data, dict) else {}
        if isinstance(scripts, dict):
            for name in ["build", "compile"]:
                if name in scripts:
                    add(candidates, "build", f"npm run {name}", "package.json scripts", "high")
                    break
            for name in ["test", "test:unit", "test:ci", "vitest", "jest"]:
                if name in scripts:
                    command = "npm test" if name == "test" else f"npm run {name}"
                    add(candidates, "test", command, "package.json scripts", "high")
                    break
            for name in ["lint", "format:check", "check"]:
                if name in scripts:
                    add(candidates, "lint", f"npm run {name}", "package.json scripts", "high")
                    break
            for name in ["lint:fix", "format"]:
                if name in scripts:
                    add(candidates, "lint_fix", f"npm run {name}", "package.json scripts", "medium", "mutates files")
                    break
        if not any(c["kind"] == "build" for c in candidates):
            add(candidates, "build", "npx tsc --noEmit", "typescript fallback", "low", "only if TypeScript dependencies are available")

    if marker("pyproject.toml") or marker("pytest.ini") or marker("tox.ini") or any(root.glob("tests/**/*.py")) or any(root.glob("test_*.py")):
        if (root / "pytest.ini").exists() or any(root.glob("tests/test_*.py")) or any(root.glob("**/*_test.py")):
            add(candidates, "test", "python -m pytest", "python test markers", "medium")
        elif any(root.glob("tests/**/*.py")):
            add(candidates, "test", "python -m unittest discover", "python tests directory", "medium")
        py_files = [p for p in root.glob("scripts/*.py") if p.is_file()]
        if py_files:
            add(candidates, "build", "python -m py_compile " + " ".join(str(p.relative_to(root)) for p in py_files), "python scripts", "medium")

    if any(root.glob("*.sln")) or any(root.glob("*.csproj")):
        markers.append("dotnet")
        add(candidates, "build", "dotnet build", "dotnet project markers", "high")
        add(candidates, "test", "dotnet test", "dotnet project markers", "medium")
        add(candidates, "lint", "dotnet format --verify-no-changes", "dotnet project markers", "medium")

    if marker("go.mod"):
        add(candidates, "build", "go build ./...", "go.mod", "high")
        add(candidates, "test", "go test ./...", "go.mod", "high")
        add(candidates, "lint_fix", "gofmt -w .", "go.mod", "low", "mutates files; prefer scoped paths")

    if marker("Cargo.toml"):
        add(candidates, "build", "cargo build", "Cargo.toml", "high")
        add(candidates, "test", "cargo test", "Cargo.toml", "high")
        add(candidates, "lint", "cargo fmt --check", "Cargo.toml", "medium")
        add(candidates, "lint_fix", "cargo fmt", "Cargo.toml", "medium", "mutates files")

    if marker("pom.xml"):
        add(candidates, "build", "mvn compile", "pom.xml", "medium")
        add(candidates, "test", "mvn test", "pom.xml", "medium")

    if marker("build.gradle") or marker("settings.gradle"):
        wrapper = "./gradlew" if (root / "gradlew").exists() else "gradle"
        add(candidates, "build", f"{wrapper} build", "gradle markers", "medium")
        add(candidates, "test", f"{wrapper} test", "gradle markers", "medium")

    targets = makefile_targets(root)
    if targets:
        markers.append("Makefile")
        if "build" in targets:
            add(candidates, "build", "make build", "Makefile", "high")
        elif "all" in targets:
            add(candidates, "build", "make all", "Makefile", "medium")
        if "test" in targets:
            add(candidates, "test", "make test", "Makefile", "high")
        if "lint" in targets:
            add(candidates, "lint", "make lint", "Makefile", "high")

    if (root / "SKILL.md").exists():
        markers.append("SKILL.md")
        add(candidates, "validate", "python scripts/validate_artifact_integrity.py .", "skill package marker", "medium", "if this helper is present in the skill package")
        py_files = [p for p in root.glob("scripts/*.py") if p.is_file()]
        if py_files and not any(c["kind"] == "build" and "py_compile" in c["command"] for c in candidates):
            add(candidates, "build", "python -m py_compile " + " ".join(str(p.relative_to(root)) for p in py_files), "skill package python scripts", "medium")

    return {
        "root": str(root),
        "markers": sorted(set(markers)),
        "candidates": candidates,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Discover likely build, test, lint, and validation commands.")
    parser.add_argument("path", nargs="?", default=".", help="Target project or skill package root")
    parser.add_argument("--format", choices=["json", "markdown"], default="json")
    args = parser.parse_args()

    result = discover(Path(args.path))
    if args.format == "json":
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"# Command discovery\n\nTarget: `{result['root']}`\n")
        print("## Markers\n")
        for item in result["markers"]:
            print(f"- `{item}`")
        print("\n## Candidates\n")
        print("| Kind | Command | Source | Confidence | Notes |")
        print("|---|---|---|---|---|")
        for item in result["candidates"]:
            print(f"| {item['kind']} | `{item['command']}` | {item['source']} | {item['confidence']} | {item['notes']} |")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
