#!/usr/bin/env python3
"""Deterministic identity, contract, and evaluator controls for hardening runs."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

EXCLUDED_DIRS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "tmp",
    ".tmp",
    "reports",
    "test-results",
    "benchmark-reports",
}
EXCLUDED_FILES = {".DS_Store", "test-results.json", "hardening-audit.json"}
CEILINGS = {"objective-artifact", "tool-action", "research-analytic", "constrained-subjective"}
VARIABILITY_CLASSES = {
    "mechanical",
    "schema-type",
    "constrained-heuristic",
    "model-judgment",
    "external-nondeterminism",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def package_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"symlink is not allowed: {path.relative_to(root).as_posix()}")
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if any(part in EXCLUDED_DIRS for part in rel.parts[:-1]):
            continue
        if rel.name in EXCLUDED_FILES or rel.name.endswith(("~", ".swp", ".swo")):
            continue
        files.append(path)
    return files


def file_records(root: Path, files: list[Path]) -> list[dict[str, Any]]:
    return [
        {
            "path": path.relative_to(root).as_posix(),
            "size_bytes": path.stat().st_size,
            "sha256": sha256_bytes(path.read_bytes()),
        }
        for path in files
    ]


def tree_identity(root: Path, files: list[Path] | None = None) -> dict[str, Any]:
    selected = files if files is not None else package_files(root)
    records = file_records(root, selected)
    digest = hashlib.sha256()
    for item in records:
        digest.update(item["path"].encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(item["size_bytes"]).encode("ascii"))
        digest.update(b"\0")
        digest.update(item["sha256"].encode("ascii"))
        digest.update(b"\n")
    return {"tree_sha256": digest.hexdigest(), "file_count": len(records), "files": records}


def resolve_selected(root: Path, selected: list[str]) -> list[Path]:
    files: set[Path] = set()
    for raw in selected:
        candidate = (root / raw).resolve()
        try:
            candidate.relative_to(root)
        except ValueError as exc:
            raise ValueError(f"selected path escapes root: {raw}") from exc
        if not candidate.exists():
            raise ValueError(f"selected path does not exist: {raw}")
        candidates = [candidate] if candidate.is_file() else sorted(candidate.rglob("*"))
        for path in candidates:
            if path.is_symlink():
                raise ValueError(f"selected symlink is not allowed: {path.relative_to(root).as_posix()}")
            if path.is_file():
                files.add(path)
    return sorted(files)


def diagnostic(code: str, subject: str, evidence: str, severity: str = "error") -> dict[str, str]:
    return {"code": code, "severity": severity, "subject": subject, "evidence": evidence}


def validate_contract(data: Any) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    if not isinstance(data, dict):
        return [diagnostic("HC001", "contract", "root must be a JSON object")]
    required = ["schema_version", "target", "ceiling", "protected_paths", "variability", "evaluators", "hard_gates", "acceptance", "delivery"]
    for key in required:
        if key not in data:
            findings.append(diagnostic("HC002", key, "required key is missing"))
    if data.get("schema_version") != 1:
        findings.append(diagnostic("HC003", "schema_version", "must equal 1"))
    target = data.get("target")
    if not isinstance(target, dict) or not all(target.get(key) for key in ("name", "path", "baseline_tree_sha256")):
        findings.append(diagnostic("HC004", "target", "name, path, and baseline_tree_sha256 are required"))
    if data.get("ceiling") not in CEILINGS:
        findings.append(diagnostic("HC005", "ceiling", f"unsupported value: {data.get('ceiling')!r}"))
    variability = data.get("variability")
    if not isinstance(variability, list) or not variability:
        findings.append(diagnostic("HC006", "variability", "must be a non-empty list"))
    else:
        ids: set[str] = set()
        for index, item in enumerate(variability):
            subject = f"variability[{index}]"
            if not isinstance(item, dict):
                findings.append(diagnostic("HC007", subject, "must be an object"))
                continue
            missing = [key for key in ("id", "surface", "class", "evidence", "control", "validation") if not item.get(key)]
            if missing:
                findings.append(diagnostic("HC008", subject, f"missing fields: {missing}"))
            if item.get("class") not in VARIABILITY_CLASSES:
                findings.append(diagnostic("HC009", subject, f"unsupported class: {item.get('class')!r}"))
            if item.get("id") in ids:
                findings.append(diagnostic("HC010", subject, f"duplicate id: {item.get('id')!r}"))
            ids.add(str(item.get("id")))
    evaluators = data.get("evaluators")
    if not isinstance(evaluators, list) or not evaluators:
        findings.append(diagnostic("HC011", "evaluators", "must be a non-empty list"))
    gates = data.get("hard_gates")
    if not isinstance(gates, list) or not gates:
        findings.append(diagnostic("HC012", "hard_gates", "must be a non-empty list"))
    acceptance = data.get("acceptance")
    if not isinstance(acceptance, dict):
        findings.append(diagnostic("HC013", "acceptance", "must be an object"))
    else:
        if acceptance.get("freeze_after_pass") is not True:
            findings.append(diagnostic("HC014", "acceptance.freeze_after_pass", "must be true"))
        if acceptance.get("weaken_hard_gates_to_pass") is not False:
            findings.append(diagnostic("HC015", "acceptance.weaken_hard_gates_to_pass", "must be false"))
        limit = acceptance.get("stagnation_limit")
        if not isinstance(limit, int) or limit < 1:
            findings.append(diagnostic("HC016", "acceptance.stagnation_limit", "must be an integer >= 1"))
    return findings


def write_result(result: dict[str, Any], output: str | None) -> None:
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if output:
        path = Path(output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(payload, encoding="utf-8")
    print(payload, end="")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Identity, contract, and evaluator controls for skill hardening.")
    sub = parser.add_subparsers(dest="command", required=True)

    tree = sub.add_parser("tree-hash", help="Compute a deterministic package tree identity.")
    tree.add_argument("--target", required=True)
    tree.add_argument("--json-output")

    freeze = sub.add_parser("freeze", help="Freeze selected evaluator files by SHA-256.")
    freeze.add_argument("--root", required=True)
    freeze.add_argument("--path", action="append", required=True)
    freeze.add_argument("--output", required=True)

    verify = sub.add_parser("verify", help="Verify a frozen evaluator manifest.")
    verify.add_argument("--root", required=True)
    verify.add_argument("--manifest", required=True)
    verify.add_argument("--json-output")

    contract = sub.add_parser("validate-contract", help="Validate a filled hardening contract.")
    contract.add_argument("--contract", required=True)
    contract.add_argument("--json-output")

    args = parser.parse_args(argv)
    try:
        if args.command == "tree-hash":
            root = Path(args.target).resolve()
            result = {"status": "pass", "target": str(root), **tree_identity(root)}
            write_result(result, args.json_output)
            return 0
        if args.command == "freeze":
            root = Path(args.root).resolve()
            selected = resolve_selected(root, args.path)
            result = {
                "schema_version": 1,
                "root_name": root.name,
                "selected_paths": sorted(args.path),
                **tree_identity(root, selected),
            }
            write_result(result, args.output)
            return 0
        if args.command == "verify":
            root = Path(args.root).resolve()
            manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
            current = tree_identity(root, resolve_selected(root, manifest.get("selected_paths", [])))
            passed = current["tree_sha256"] == manifest.get("tree_sha256") and current["files"] == manifest.get("files")
            findings = [] if passed else [diagnostic("EV001", "evaluator", "frozen evaluator files changed")]
            result = {"status": "pass" if passed else "fail", "tree_sha256": current["tree_sha256"], "findings": findings}
            write_result(result, args.json_output)
            return 0 if passed else 1
        data = json.loads(Path(args.contract).read_text(encoding="utf-8"))
        findings = validate_contract(data)
        result = {"status": "pass" if not findings else "fail", "findings": findings}
        write_result(result, args.json_output)
        return 0 if not findings else 1
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        output = getattr(args, "json_output", None) or (args.output if args.command == "freeze" else None)
        write_result({"status": "fail", "findings": [diagnostic("RC001", args.command, str(exc))]}, output)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
