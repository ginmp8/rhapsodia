#!/usr/bin/env python3
"""Deterministically discover and select build/test/lint/validator commands."""
from __future__ import annotations

import argparse
import json
import re
import shlex
import shutil
import sys
from pathlib import Path
from typing import Any

GATES = ("build", "test", "lint", "validator", "packaging")
CONFIDENCE_ORDER = {"high": 0, "medium": 1, "low": 2}


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except Exception:
        return {}


def command_argv(command: str) -> list[str]:
    try:
        return shlex.split(command, posix=True)
    except ValueError:
        return []


def add(
    candidates: list[dict[str, Any]],
    kind: str,
    command: str,
    source: str,
    confidence: str,
    rank: int,
    notes: str = "",
    argv: list[str] | None = None,
) -> None:
    if kind not in GATES:
        raise ValueError(f"unsupported gate: {kind}")
    if any(item["kind"] == kind and item["command"] == command for item in candidates):
        return
    actual_argv = list(argv) if argv is not None else command_argv(command)
    executable = actual_argv[0] if actual_argv else None
    available = bool(executable and (Path(executable).is_file() or shutil.which(executable)))
    tie_break = f"{rank:04d}|{CONFIDENCE_ORDER.get(confidence, 9):02d}|{source.lower()}|{command.lower()}"
    candidates.append(
        {
            "kind": kind,
            "command": command,
            "argv": actual_argv,
            "source": source,
            "confidence": confidence,
            "rank": rank,
            "tie_break": tie_break,
            "runtime": {"executable": executable, "available": available},
            "notes": notes,
        }
    )


def makefile_targets(path: Path) -> set[str]:
    makefile = path / "Makefile"
    if not makefile.exists():
        return set()
    text = makefile.read_text(encoding="utf-8", errors="replace")
    return set(re.findall(r"^([A-Za-z0-9_.-]+):(?:\s|$)", text, flags=re.MULTILINE))


def selected_by_gate(candidates: list[dict[str, Any]]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    selected: dict[str, Any] = {}
    ambiguities: list[dict[str, Any]] = []
    for gate in GATES:
        gate_items = [item for item in candidates if item["kind"] == gate]
        if not gate_items:
            continue
        ordered = sorted(gate_items, key=lambda item: (item["rank"], CONFIDENCE_ORDER.get(item["confidence"], 9), item["source"].lower(), item["command"].lower()))
        selected[gate] = ordered[0]
        top = [item for item in ordered if item["rank"] == ordered[0]["rank"] and item["confidence"] == ordered[0]["confidence"]]
        if len(top) > 1:
            ambiguities.append(
                {
                    "gate": gate,
                    "resolution": "fixed lexical tie-break on source then command",
                    "candidates": [item["command"] for item in top],
                    "selected": ordered[0]["command"],
                }
            )
    return selected, ambiguities


def discover(root: Path) -> dict[str, Any]:
    root = root.resolve()
    candidates: list[dict[str, Any]] = []
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
            package_rules = [
                ("build", "build", "npm run build", 20),
                ("build", "compile", "npm run compile", 25),
                ("test", "test", "npm test", 20),
                ("test", "test:ci", "npm run test:ci", 25),
                ("test", "test:unit", "npm run test:unit", 26),
                ("test", "vitest", "npm run vitest", 27),
                ("test", "jest", "npm run jest", 28),
                ("lint", "lint", "npm run lint", 20),
                ("lint", "format:check", "npm run format:check", 25),
                ("lint", "check", "npm run check", 28),
            ]
            for gate, script_name, command, rank in package_rules:
                if script_name in scripts:
                    add(candidates, gate, command, f"package.json script:{script_name}", "high", rank)
        if not any(c["kind"] == "build" and c["source"].startswith("package.json") for c in candidates):
            add(candidates, "build", "npx tsc --noEmit", "TypeScript fallback", "low", 60, "only when project dependencies already provide TypeScript")

    targets = makefile_targets(root)
    if targets:
        markers.append("Makefile")
        if "build" in targets:
            add(candidates, "build", "make build", "Makefile target:build", "high", 10)
        elif "all" in targets:
            add(candidates, "build", "make all", "Makefile target:all", "medium", 15)
        if "test" in targets:
            add(candidates, "test", "make test", "Makefile target:test", "high", 10)
        if "lint" in targets:
            add(candidates, "lint", "make lint", "Makefile target:lint", "high", 10)
        if "validate" in targets:
            add(candidates, "validator", "make validate", "Makefile target:validate", "high", 10)

    python_markers = marker("pyproject.toml") or marker("pytest.ini") or marker("tox.ini") or any(root.glob("tests/**/*.py")) or any(root.glob("test_*.py"))
    if python_markers:
        pyproject_text = (root / "pyproject.toml").read_text(encoding="utf-8", errors="replace") if (root / "pyproject.toml").exists() else ""
        pytest_marked = (root / "pytest.ini").exists() or "pytest" in pyproject_text.lower()
        if pytest_marked:
            add(candidates, "test", "<PYTHON> -m pytest", "Python pytest markers", "medium", 35, argv=[sys.executable, "-m", "pytest"])
        elif any(root.glob("tests/**/*.py")):
            add(candidates, "test", "<PYTHON> -m unittest discover -s tests -p test_*.py", "Python tests directory", "medium", 35, argv=[sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"])
        py_files = sorted(p for p in root.glob("scripts/*.py") if p.is_file())
        if py_files:
            rels = [str(p.relative_to(root)).replace("\\", "/") for p in py_files]
            add(candidates, "build", "<PYTHON> -m py_compile " + " ".join(rels), "Python scripts", "medium", 50, argv=[sys.executable, "-m", "py_compile", *rels])

    if any(root.glob("*.sln")) or any(root.glob("*.csproj")):
        markers.append("dotnet")
        add(candidates, "build", "dotnet build", ".NET project marker", "high", 30)
        add(candidates, "test", "dotnet test", ".NET project marker", "medium", 35)
        add(candidates, "lint", "dotnet format --verify-no-changes", ".NET project marker", "medium", 40)

    if marker("go.mod"):
        add(candidates, "build", "go build ./...", "go.mod", "high", 30)
        add(candidates, "test", "go test ./...", "go.mod", "high", 30)

    if marker("Cargo.toml"):
        add(candidates, "build", "cargo build", "Cargo.toml", "high", 30)
        add(candidates, "test", "cargo test", "Cargo.toml", "high", 30)
        add(candidates, "lint", "cargo fmt --check", "Cargo.toml", "medium", 40)

    if marker("pom.xml"):
        add(candidates, "build", "mvn compile", "pom.xml", "medium", 30)
        add(candidates, "test", "mvn test", "pom.xml", "medium", 30)

    if marker("build.gradle") or marker("settings.gradle"):
        wrapper = "./gradlew" if (root / "gradlew").exists() else "gradle"
        add(candidates, "build", f"{wrapper} build", "Gradle marker", "medium", 30)
        add(candidates, "test", f"{wrapper} test", "Gradle marker", "medium", 30)

    if (root / "SKILL.md").exists():
        markers.append("SKILL.md")
        validator = root / "scripts" / "validate_artifact_integrity.py"
        if validator.exists():
            add(candidates, "validator", "<PYTHON> scripts/validate_artifact_integrity.py . --format json", "skill integrity validator", "high", 20, argv=[sys.executable, "scripts/validate_artifact_integrity.py", ".", "--format", "json"])
        py_files = sorted(p for p in root.glob("scripts/*.py") if p.is_file())
        if py_files and not any(c["kind"] == "build" and "py_compile" in c["command"] for c in candidates):
            rels = [str(p.relative_to(root)).replace("\\", "/") for p in py_files]
            add(candidates, "build", "<PYTHON> -m py_compile " + " ".join(rels), "skill package Python scripts", "medium", 50, argv=[sys.executable, "-m", "py_compile", *rels])
        packager = root / "scripts" / "package_skill.py"
        if packager.exists():
            add(candidates, "packaging", "<PYTHON> scripts/package_skill.py . <OUTPUT.zip>", "skill package builder", "medium", 50, "requires an explicit output path", argv=[])

    candidates = sorted(candidates, key=lambda item: (GATES.index(item["kind"]), item["rank"], CONFIDENCE_ORDER.get(item["confidence"], 9), item["source"].lower(), item["command"].lower()))
    selected, ambiguities = selected_by_gate(candidates)
    return {
        "schema_version": 1,
        "root": str(root),
        "working_directory": str(root),
        "markers": sorted(set(markers)),
        "candidates": candidates,
        "selected": selected,
        "ambiguities": ambiguities,
        "precedence": ["user-provided", "repository orchestrator", "declared package script", "runtime-standard command", "static fallback", "lexical tie-break"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Deterministically discover and select build/test/lint/validator commands.")
    parser.add_argument("path", nargs="?", default=".", help="Target project or skill package root")
    parser.add_argument("--format", choices=["json", "markdown"], default="json")
    args = parser.parse_args()
    result = discover(Path(args.path))
    if args.format == "json":
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"# Command discovery\n\nTarget: `{result['root']}`\n")
        print("| Gate | Selected command | Rank | Source |")
        print("|---|---|---:|---|")
        for gate in GATES:
            item = result["selected"].get(gate)
            if item:
                print(f"| {gate} | `{item['command']}` | {item['rank']} | {item['source']} |")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
