#!/usr/bin/env python3
"""Validate declared Mago runtime dependencies and provide actionable diagnostics."""
from __future__ import annotations

import argparse
import importlib
import importlib.metadata
import json
import re
from pathlib import Path
from typing import Any

REQ_RE = re.compile(r"^(?P<name>[A-Za-z0-9_.-]+)(?P<specifier>(?:[<>=!~]=?[^;\s,]+(?:,[<>=!~]=?[^;\s,]+)*)?)$")
VERSION_PART_RE = re.compile(r"\d+")


def version_tuple(value: str) -> tuple[int, ...]:
    parts = VERSION_PART_RE.findall(value)
    return tuple(int(part) for part in parts[:4]) if parts else (0,)


def compare(actual: str, operator: str, expected: str) -> bool:
    left = version_tuple(actual)
    right = version_tuple(expected)
    width = max(len(left), len(right))
    left += (0,) * (width - len(left))
    right += (0,) * (width - len(right))
    return {
        ">=": left >= right,
        ">": left > right,
        "<=": left <= right,
        "<": left < right,
        "==": left == right,
        "!=": left != right,
    }[operator]


def satisfies(actual: str, specifier: str) -> bool:
    if not specifier:
        return True
    for clause in specifier.split(","):
        match = re.fullmatch(r"(>=|<=|==|!=|>|<)\s*([0-9][A-Za-z0-9_.+-]*)", clause.strip())
        if not match or not compare(actual, match.group(1), match.group(2)):
            return False
    return True


def load_release(root: Path) -> dict[str, Any]:
    payload = json.loads((root / "release.json").read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("release.json root must be an object")
    return payload


def parse_requirements(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        match = REQ_RE.fullmatch(line)
        if not match:
            raise ValueError(f"{path}:{line_number}: unsupported requirement syntax: {line!r}")
        result[match.group("name").lower()] = match.group("specifier") or ""
    return result


def validate(root: Path, *, check_installed: bool = True) -> dict[str, Any]:
    errors: list[str] = []
    dependencies: list[dict[str, Any]] = []
    requirements_path = root / "requirements.txt"
    if not requirements_path.is_file() or requirements_path.is_symlink():
        return {"status": "fail", "errors": [f"{requirements_path}: missing regular dependency manifest"], "dependencies": []}
    try:
        requirements = parse_requirements(requirements_path)
        release = load_release(root)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return {"status": "fail", "errors": [str(exc)], "dependencies": []}

    declared = release.get("runtime_dependencies")
    if not isinstance(declared, list) or not declared:
        errors.append("release.json runtime_dependencies must be a non-empty list")
        declared = []

    seen: set[str] = set()
    for index, item in enumerate(declared):
        if not isinstance(item, dict):
            errors.append(f"runtime_dependencies[{index}] must be an object")
            continue
        distribution = str(item.get("distribution", "")).strip()
        module = str(item.get("import", "")).strip()
        specifier = str(item.get("specifier", "")).replace(" ", "")
        if not distribution or not module or not specifier:
            errors.append(f"runtime_dependencies[{index}] needs distribution, import, and specifier")
            continue
        key = distribution.lower()
        if key in seen:
            errors.append(f"duplicate runtime dependency declaration: {distribution}")
            continue
        seen.add(key)
        if requirements.get(key) != specifier:
            errors.append(
                f"requirements.txt declaration for {distribution} must equal {specifier!r}; "
                f"found {requirements.get(key)!r}"
            )
        record: dict[str, Any] = {
            "distribution": distribution,
            "import": module,
            "specifier": specifier,
            "installed_version": None,
            "import_status": "not-checked" if not check_installed else "pending",
        }
        if check_installed:
            try:
                imported = importlib.import_module(module)
                del imported
                actual = importlib.metadata.version(distribution)
                record["installed_version"] = actual
                record["import_status"] = "pass"
                if not satisfies(actual, specifier):
                    errors.append(f"installed {distribution} {actual} does not satisfy {specifier}")
            except Exception as exc:  # noqa: BLE001 - diagnostic gate
                record["import_status"] = "fail"
                errors.append(
                    f"cannot load runtime dependency {distribution} ({module}): {exc}. "
                    "Install with `python -m pip install -r requirements.txt`."
                )
        dependencies.append(record)

    undeclared = sorted(set(requirements) - seen)
    if undeclared:
        errors.append(f"requirements.txt contains undeclared runtime dependencies: {undeclared}")
    return {"status": "pass" if not errors else "fail", "errors": errors, "dependencies": dependencies}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Mago runtime dependency declarations and imports.")
    parser.add_argument("target", nargs="?", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--metadata-only", action="store_true", help="Validate declarations without importing installed packages.")
    parser.add_argument("--json-output")
    args = parser.parse_args(argv)
    result = validate(Path(args.target).resolve(), check_installed=not args.metadata_only)
    if args.json_output:
        output = Path(args.json_output).resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"wrote {output}")
    for error in result["errors"]:
        print(f"ERROR: {error}")
    if result["status"] == "pass":
        print(f"OK: {len(result['dependencies'])} runtime dependency declaration(s) validated")
        return 0
    print(f"FAILED: {len(result['errors'])} runtime dependency error(s)")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
