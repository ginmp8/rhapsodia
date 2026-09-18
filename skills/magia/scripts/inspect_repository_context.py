#!/usr/bin/env python3
"""Produce a deterministic, read-only orientation view for a repository."""
from __future__ import annotations

import argparse
import json
import os
from collections import Counter
from pathlib import Path
from typing import Any

SKIP_DIRS = {
    ".git", ".hg", ".svn", ".idea", ".vscode", ".pytest_cache", "__pycache__",
    "node_modules", ".venv", "venv", "vendor", "dist", "build", "bin", "obj",
    "coverage", ".next", ".nuxt", "target", "artifacts", "TestResults", "test-results",
}

LANGUAGE_EXTENSIONS = {
    ".py": "python", ".cs": "csharp", ".fs": "fsharp", ".vb": "visual-basic",
    ".ts": "typescript", ".tsx": "typescript", ".js": "javascript", ".jsx": "javascript",
    ".java": "java", ".kt": "kotlin", ".kts": "kotlin", ".go": "go", ".rs": "rust",
    ".rb": "ruby", ".php": "php", ".ex": "elixir", ".exs": "elixir", ".swift": "swift",
    ".cpp": "cpp", ".cc": "cpp", ".c": "c", ".h": "c-cpp-header", ".hpp": "c-cpp-header",
    ".sql": "sql", ".sh": "shell", ".ps1": "powershell",
}

BUILD_MARKERS = {
    "pyproject.toml": "python/pyproject", "setup.py": "python/setuptools",
    "requirements.txt": "python/requirements", "package.json": "node/package-json",
    "pnpm-lock.yaml": "node/pnpm", "yarn.lock": "node/yarn", "package-lock.json": "node/npm",
    "cargo.toml": "rust/cargo", "go.mod": "go/modules", "pom.xml": "java/maven",
    "build.gradle": "java/gradle", "build.gradle.kts": "kotlin/gradle",
    "makefile": "make", "dockerfile": "docker", "compose.yaml": "docker/compose",
    "docker-compose.yml": "docker/compose", "global.json": "dotnet/global-json",
}

PLANNING_NAMES = {
    "prd.md", "tasks.md", "technical-design.md", "validation.md", "manifest.yaml",
    "execution-handoff-plan.md", "spec-catalog.yaml", "cycle.yaml",
}
GOVERNANCE_NAMES: set[str] = set()
CONTRACT_NAMES = {"openapi.yaml", "openapi.yml", "asyncapi.yaml", "asyncapi.yml", "schema.graphql"}
CONTRACT_SUFFIXES = {".proto", ".avsc"}
TEST_DIR_NAMES = {"test", "tests", "spec", "specs"}
ENTRYPOINT_NAMES = {
    "main.py", "app.py", "manage.py", "program.cs", "startup.cs", "main.go", "main.rs",
    "index.ts", "index.js", "server.ts", "server.js", "application.java",
}


def relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def inspect_package_json(path: Path) -> list[str]:
    try:
        if path.stat().st_size > 1_000_000:
            return []
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return []
    scripts = data.get("scripts", {})
    if not isinstance(scripts, dict):
        return []
    return sorted(str(key) for key in scripts if isinstance(key, str))


def inspect_root(root: Path, max_files: int) -> dict[str, Any]:
    root = root.expanduser()
    if root.is_symlink():
        raise ValueError("repository root must not be a symlink")
    root = root.resolve()
    if not root.is_dir():
        raise ValueError(f"repository root is not a directory: {root}")

    languages: Counter[str] = Counter()
    build_systems: set[str] = set()
    build_files: list[str] = []
    test_signals: list[str] = []
    entrypoints: list[str] = []
    contracts: list[str] = []
    migrations: list[str] = []
    planning: list[str] = []
    governance: list[str] = []
    package_scripts: dict[str, list[str]] = {}
    top_level_dirs: set[str] = set()
    scanned = 0
    truncated = False

    for current, dirs, files in os.walk(root, followlinks=False):
        current_path = Path(current)
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS and not (current_path / d).is_symlink())
        if current_path == root:
            top_level_dirs.update(dirs)
        for name in sorted(files):
            path = current_path / name
            if path.is_symlink():
                continue
            scanned += 1
            if scanned > max_files:
                truncated = True
                break
            rel = relative(path, root)
            lower = name.lower()
            suffix = path.suffix.lower()
            language = LANGUAGE_EXTENSIONS.get(suffix)
            if language:
                languages[language] += 1
            if lower in BUILD_MARKERS:
                build_systems.add(BUILD_MARKERS[lower])
                build_files.append(rel)
            if suffix in {".sln", ".csproj", ".fsproj", ".vbproj"}:
                build_systems.add("dotnet")
                build_files.append(rel)
            parts_lower = {part.lower() for part in path.parts}
            if parts_lower & TEST_DIR_NAMES or lower.startswith("test_") or lower.endswith(("_test.py", ".test.ts", ".spec.ts", ".test.js", ".spec.js")):
                test_signals.append(rel)
            if lower in ENTRYPOINT_NAMES:
                entrypoints.append(rel)
            if lower in CONTRACT_NAMES or suffix in CONTRACT_SUFFIXES or "schemas" in parts_lower or "contracts" in parts_lower:
                contracts.append(rel)
            if "migrations" in parts_lower or "migration" in parts_lower:
                migrations.append(rel)
            if lower in PLANNING_NAMES or ("docs" in parts_lower and "boards" in parts_lower):
                planning.append(rel)
            if lower in GOVERNANCE_NAMES or "governance" in parts_lower:
                governance.append(rel)
            if lower == "package.json":
                scripts = inspect_package_json(path)
                if scripts:
                    package_scripts[rel] = scripts
        if truncated:
            break

    suggested: list[dict[str, str]] = []
    if any(x.startswith("python/") for x in build_systems) or languages.get("python"):
        if test_signals:
            suggested.append({"family": "python-tests", "suggestion": "inspect pytest configuration, then run the narrowest pytest target"})
    if "dotnet" in build_systems:
        suggested.append({"family": "dotnet", "suggestion": "inspect solution/project targets, then run the narrowest dotnet test or build command"})
    if any(x.startswith("node/") for x in build_systems):
        suggested.append({"family": "node", "suggestion": "inspect package.json scripts before selecting a test, lint, typecheck, or build command"})
    if "rust/cargo" in build_systems:
        suggested.append({"family": "rust", "suggestion": "inspect Cargo workspace packages, then run the narrowest cargo test or check target"})
    if "go/modules" in build_systems:
        suggested.append({"family": "go", "suggestion": "inspect module/package scope, then run the narrowest go test target"})
    if contracts:
        suggested.append({"family": "contracts", "suggestion": "identify consumers and run the repository's existing contract or compatibility validator"})
    if migrations:
        suggested.append({"family": "migration", "suggestion": "require forward, compatibility, data-integrity, and rollback or recovery checks"})

    return {
        "kind": "magia-repository-orientation",
        "version": 1,
        "root": str(root),
        "read_only": True,
        "commands_executed": [],
        "scan": {"file_count": min(scanned, max_files), "max_files": max_files, "truncated": truncated},
        "top_level_directories": sorted(top_level_dirs),
        "languages": [{"name": name, "file_count": count} for name, count in sorted(languages.items(), key=lambda x: (-x[1], x[0]))],
        "build_systems": sorted(build_systems),
        "build_files": sorted(set(build_files)),
        "entrypoint_signals": sorted(set(entrypoints)),
        "test_signals": sorted(set(test_signals))[:200],
        "contract_signals": sorted(set(contracts))[:200],
        "migration_signals": sorted(set(migrations))[:200],
        "planning_markers": sorted(set(planning))[:200],
        "governance_markers": sorted(set(governance))[:200],
        "package_scripts": {key: package_scripts[key] for key in sorted(package_scripts)},
        "suggested_validation_families": suggested,
        "limitations": [
            "path and limited metadata inspection only",
            "suggestions are not executed commands or validation evidence",
            "verify repository-specific semantics before mutation",
        ],
    }


def to_markdown(data: dict[str, Any]) -> str:
    def bullets(values: list[Any]) -> str:
        return "\n".join(f"- `{value}`" for value in values) if values else "- `none observed`"

    languages = [f"{item['name']}: {item['file_count']} files" for item in data["languages"]]
    validation = [f"{item['family']}: {item['suggestion']}" for item in data["suggested_validation_families"]]
    return "\n".join([
        "# MAGIA Repository Orientation",
        "",
        f"- Root: `{data['root']}`",
        f"- Read-only: `{str(data['read_only']).lower()}`",
        f"- Files scanned: `{data['scan']['file_count']}`",
        f"- Truncated: `{str(data['scan']['truncated']).lower()}`",
        "",
        "## Languages",
        bullets(languages),
        "",
        "## Build systems",
        bullets(data["build_systems"]),
        "",
        "## Entry-point signals",
        bullets(data["entrypoint_signals"]),
        "",
        "## Test signals",
        bullets(data["test_signals"]),
        "",
        "## Contract and migration signals",
        bullets(data["contract_signals"] + data["migration_signals"]),
        "",
        "## Planning and governance markers",
        bullets(data["planning_markers"] + data["governance_markers"]),
        "",
        "## Suggested validation families",
        bullets(validation),
        "",
        "## Limitations",
        bullets(data["limitations"]),
        "",
    ])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Produce a deterministic read-only repository orientation view.")
    parser.add_argument("--root", required=True, help="Repository root to inspect.")
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    parser.add_argument("--output", help="Optional output path. Defaults to stdout.")
    parser.add_argument("--max-files", type=int, default=20_000)
    args = parser.parse_args(argv)
    if args.max_files < 1:
        parser.error("--max-files must be positive")
    try:
        data = inspect_root(Path(args.root), args.max_files)
    except ValueError as exc:
        parser.error(str(exc))
    text = json.dumps(data, indent=2, sort_keys=True) + "\n" if args.format == "json" else to_markdown(data)
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
