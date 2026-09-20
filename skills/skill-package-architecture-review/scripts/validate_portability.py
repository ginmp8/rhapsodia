#!/usr/bin/env python3
"""Validate mechanically checkable portability properties for this skill package."""

from __future__ import annotations

import argparse
import ast
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "1.0.0"
MIN_PYTHON = (3, 10)
TEXT_SUFFIXES = {".md", ".py", ".json", ".yaml", ".yml", ".template", ".txt"}
EXCLUDED_PARTS = {".git", "__pycache__"}
SANDBOX_PATH_PATTERNS = (
    re.compile(r"(?<![A-Za-z0-9_])/home/[A-Za-z0-9_.-]+/"),
    re.compile(r"(?<![A-Za-z0-9_])/mnt/data/"),
)
WINDOWS_ABSOLUTE_RE = re.compile(r"(?i)(?<![A-Za-z0-9_])[A-Z]:\\\\")
SHELL_COUPLING_PATTERNS = (
    re.compile(r"subprocess\.(?:run|Popen|call|check_call|check_output)\([^\n]*shell\s*=\s*True"),
    re.compile(r"\bos\.system\s*\("),
)
SHELL_COMMAND_RE = re.compile(
    r"(?i)^(?:bash|sh|zsh|fish|powershell|pwsh|cmd(?:\.exe)?)\b"
)


def _iter_files(root: Path) -> list[Path]:
    return sorted(
        [
            p
            for p in root.rglob("*")
            if p.is_file() and not any(part in EXCLUDED_PARTS for part in p.relative_to(root).parts)
        ],
        key=lambda p: p.relative_to(root).as_posix(),
    )


def _read_text(path: Path) -> str | None:
    if path.suffix.lower() not in TEXT_SUFFIXES and path.name != "SKILL.md":
        return None
    try:
        return path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return None


def _stdlib_imports(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            modules.add(node.module.split(".", 1)[0])
    return sorted(modules)


def _package_identity(root: Path) -> str:
    script = root / "scripts" / "inventory_skill_package.py"
    if not script.exists():
        return "not-available"
    namespace: dict[str, Any] = {"__name__": "inventory_portability_probe"}
    exec(compile(script.read_text(encoding="utf-8"), str(script), "exec"), namespace)
    data = namespace["inventory"](root)
    return str(data["package_identity_sha256"])


def validate(root: Path) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    checks: dict[str, Any] = {}

    skill_md = root / "SKILL.md"
    checks["root_skill_md"] = skill_md.exists()
    if not skill_md.exists():
        errors.append("missing root SKILL.md")

    py_files = [p for p in _iter_files(root) if p.suffix == ".py"]
    syntax_errors: list[str] = []
    third_party_imports: dict[str, list[str]] = {}
    stdlib = set(getattr(sys, "stdlib_module_names", ()))
    for path in py_files:
        rel = path.relative_to(root).as_posix()
        try:
            compile(path.read_text(encoding="utf-8"), rel, "exec")
            imports = _stdlib_imports(path)
        except (SyntaxError, UnicodeDecodeError, OSError) as exc:
            syntax_errors.append(f"{rel}: {exc}")
            continue
        external = [name for name in imports if stdlib and name not in stdlib]
        if external:
            third_party_imports[rel] = external
    checks["python_syntax_errors"] = syntax_errors
    checks["third_party_imports"] = third_party_imports
    if syntax_errors:
        errors.extend(f"python syntax error: {item}" for item in syntax_errors)
    if third_party_imports:
        errors.append("bundled Python helpers import non-stdlib modules")

    absolute_path_hits: list[str] = []
    shell_coupling_hits: list[str] = []
    python3_command_hits: list[str] = []
    shell_command_hits: list[str] = []
    for path in _iter_files(root):
        text = _read_text(path)
        if text is None:
            continue
        rel = path.relative_to(root).as_posix()
        scan_text = text
        if rel == "scripts/validate_portability.py":
            scan_text = ""  # detector patterns are data, not package path assumptions
        elif path.suffix in {".md", ".template"}:
            fenced: list[str] = []
            in_fence = False
            for line in text.splitlines():
                if line.strip().startswith("```"):
                    in_fence = not in_fence
                    continue
                if in_fence:
                    fenced.append(line)
            scan_text = "\n".join(fenced)
        for pattern in SANDBOX_PATH_PATTERNS:
            if pattern.search(scan_text):
                absolute_path_hits.append(rel)
                break
        if WINDOWS_ABSOLUTE_RE.search(scan_text):
            absolute_path_hits.append(rel)
        if path.suffix == ".py" and any(pattern.search(text) for pattern in SHELL_COUPLING_PATTERNS):
            if rel != "scripts/validate_portability.py":
                shell_coupling_hits.append(rel)
        if path.suffix in {".md", ".template"}:
            for line in scan_text.splitlines():
                stripped = line.strip()
                if stripped.startswith("python3 ") or stripped.startswith("python ") or stripped.startswith("py -3 "):
                    python3_command_hits.append(f"{rel}: {stripped}")
                if SHELL_COMMAND_RE.search(stripped):
                    shell_command_hits.append(f"{rel}: {stripped}")
    checks["sandbox_absolute_path_hits"] = sorted(set(absolute_path_hits))
    checks["shell_coupling_hits"] = sorted(set(shell_coupling_hits))
    checks["hardcoded_python_launcher_hits"] = sorted(set(python3_command_hits))
    checks["host_shell_command_hits"] = sorted(set(shell_command_hits))
    if absolute_path_hits:
        errors.append("package content contains environment-specific absolute paths")
    if shell_coupling_hits:
        errors.append("bundled Python helpers contain shell-coupled execution")
    if python3_command_hits:
        errors.append("documentation hardcodes a Python launcher instead of <PYTHON>")
    if shell_command_hits:
        errors.append("documentation requires a host-specific shell command")

    adapter = root / "agents" / "openai.yaml"
    adapter_is_optional = adapter.exists() and "agents/openai.yaml" in (skill_md.read_text(encoding="utf-8") if skill_md.exists() else "")
    checks["openai_adapter_present"] = adapter.exists()
    checks["openai_adapter_declared_optional"] = adapter_is_optional
    if adapter.exists() and not adapter_is_optional:
        warnings.append("agents/openai.yaml exists but SKILL.md does not explicitly keep it optional")

    identity_original = "not-available"
    identity_copy = "not-available"
    try:
        identity_original = _package_identity(root)
        with tempfile.TemporaryDirectory(prefix="skill-portability-") as tmp:
            copy_root = Path(tmp) / "copied-skill"
            shutil.copytree(root, copy_root)
            identity_copy = _package_identity(copy_root)
    except Exception as exc:  # deterministic evidence collection should report, not crash
        warnings.append(f"package identity path-independence check unavailable: {exc}")
    checks["package_identity_original"] = identity_original
    checks["package_identity_copy"] = identity_copy
    checks["package_identity_path_independent"] = (
        identity_original != "not-available" and identity_original == identity_copy
    )
    if identity_original != "not-available" and identity_original != identity_copy:
        errors.append("package identity changes when the package is copied to another absolute path")

    checks["runtime_python"] = ".".join(map(str, sys.version_info[:3]))
    checks["minimum_python_contract"] = ".".join(map(str, MIN_PYTHON))

    return {
        "schema_version": SCHEMA_VERSION,
        "status": "pass" if not errors else "fail",
        "target": str(root),
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="validate portable-core properties for skill-package-architecture-review")
    parser.add_argument("--target", required=True, help="skill package root")
    parser.add_argument("--json-output", help="optional JSON report path")
    args = parser.parse_args()

    root = Path(args.target)
    if not root.exists() or not root.is_dir():
        result = {
            "schema_version": SCHEMA_VERSION,
            "status": "fail",
            "target": str(root),
            "checks": {},
            "errors": [f"target is not a directory: {root}"],
            "warnings": [],
        }
    else:
        result = validate(root)

    text = json.dumps(result, indent=2, sort_keys=True)
    print(text)
    if args.json_output:
        out = Path(args.json_output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text + "\n", encoding="utf-8")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
