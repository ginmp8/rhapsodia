#!/usr/bin/env python3
"""Validate MAGO package evidence and traceability contracts.

This validator is intentionally conservative. It verifies that package artifacts carry
traceability structure and that local source-of-truth paths resolve when they are
claimed as evidence. It does not prove implementation correctness.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable

from mago_utils import SPEC_ID_RE
PLACEHOLDER_RE = re.compile(r"<[^>]+>")
SOURCE_SECTION_RE = re.compile(r"^source_of_truth:\s*$")
TRACE_SECTION_RE = re.compile(r"^traceability:\s*$")
TOP_LEVEL_RE = re.compile(r"^[a-z_]+:\s*")
NESTED_KV_RE = re.compile(r"^\s+([a-z_]+):\s*(.*?)\s*$")
VALIDATION_CLAIM_RE = re.compile(r"\b(passed|validated|verified|complete|done|success)\b", re.IGNORECASE)
EXECUTION_CLAIM_RE = re.compile(r"\b(executed|deployed|released|runtime|production|implemented)\b", re.IGNORECASE)
EVIDENCE_MARKERS = (
    "repository findings",
    "assumptions",
    "open questions",
    "blockers",
    "source_of_truth",
    "traceability",
    "validation strategy",
)


@dataclass
class EvidenceIssue:
    severity: str
    path: str
    message: str


@dataclass
class EvidenceReport:
    status: str = "pass"
    packages_checked: int = 0
    errors: list[EvidenceIssue] = field(default_factory=list)
    warnings: list[EvidenceIssue] = field(default_factory=list)

    def error(self, path: Path | str, message: str) -> None:
        self.status = "fail"
        self.errors.append(EvidenceIssue("error", str(path), message))

    def warning(self, path: Path | str, message: str) -> None:
        self.warnings.append(EvidenceIssue("warning", str(path), message))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_manifest_blocks(text: str) -> tuple[dict[str, str], dict[str, str], bool]:
    source_of_truth: dict[str, str] = {}
    traceability: dict[str, str] = {}
    has_last_execution = False
    current: str | None = None
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if SOURCE_SECTION_RE.match(line):
            current = "source_of_truth"
            continue
        if TRACE_SECTION_RE.match(line):
            current = "traceability"
            continue
        if line.startswith("last_execution:"):
            has_last_execution = True
            current = "last_execution"
            continue
        if TOP_LEVEL_RE.match(line) and not line.startswith(" "):
            current = None
            continue
        nested = NESTED_KV_RE.match(line)
        if nested and current == "source_of_truth":
            source_of_truth[nested.group(1)] = nested.group(2).strip().strip('"').strip("'")
        elif nested and current == "traceability":
            traceability[nested.group(1)] = nested.group(2).strip().strip('"').strip("'")
    return source_of_truth, traceability, has_last_execution


def normalize_optional_path(value: str) -> str | None:
    cleaned = value.strip().strip('"').strip("'")
    if not cleaned or cleaned.lower() in {"none", "null", "[]", "{}"}:
        return None
    if PLACEHOLDER_RE.search(cleaned):
        return cleaned
    if "://" in cleaned:
        return None
    return cleaned


def resolve_claimed_path(package_path: Path, repo_root: Path | None, raw: str) -> Path:
    candidate = Path(raw)
    if candidate.is_absolute():
        return candidate
    local = package_path / candidate
    if local.exists():
        return local
    if repo_root is not None:
        return repo_root / candidate
    return local


def find_packages(target: Path, spec_ids: Iterable[str]) -> list[Path]:
    target = target.resolve()
    selected = list(spec_ids)
    packages: list[Path] = []
    if (target / "manifest.yaml").exists():
        return [target]
    specs_root = target / "specs"
    if specs_root.is_dir():
        for child in sorted(specs_root.iterdir()):
            if child.is_dir() and SPEC_ID_RE.fullmatch(child.name):
                if not selected or child.name in selected:
                    packages.append(child)
        return packages
    if selected:
        for spec_id in selected:
            packages.append(target / "specs" / spec_id)
    return packages


def has_evidence_marker(path: Path) -> bool:
    if not path.exists():
        return False
    text = read_text(path).lower()
    return any(marker in text for marker in EVIDENCE_MARKERS)


def validate_package(package_path: Path, report: EvidenceReport, repo_root: Path | None, strict_paths: bool) -> None:
    report.packages_checked += 1
    manifest = package_path / "manifest.yaml"
    if not manifest.exists():
        report.error(package_path, "missing manifest needed for evidence traceability")
        return
    manifest_text = read_text(manifest)
    if PLACEHOLDER_RE.search(manifest_text):
        report.error(manifest, "manifest still contains unresolved dynamic tokens")
    source_of_truth, traceability, has_last_execution = parse_manifest_blocks(manifest_text)
    if not source_of_truth:
        report.error(manifest, "missing source_of_truth map")
    if not traceability:
        report.error(manifest, "missing traceability map")

    for label, raw_value in sorted(source_of_truth.items()):
        normalized = normalize_optional_path(raw_value)
        if normalized is None:
            continue
        if PLACEHOLDER_RE.search(normalized):
            report.error(manifest, f"source_of_truth.{label} is unresolved: {normalized}")
            continue
        resolved = resolve_claimed_path(package_path, repo_root, normalized)
        if not resolved.exists():
            message = f"source_of_truth.{label} points to missing local path: {normalized}"
            if strict_paths:
                report.error(manifest, message)
            else:
                report.warning(manifest, message)

    primary_discovery = traceability.get("primary_discovery_file", "")
    normalized_primary = normalize_optional_path(primary_discovery)
    if normalized_primary and PLACEHOLDER_RE.search(normalized_primary):
        report.error(manifest, f"traceability.primary_discovery_file is unresolved: {normalized_primary}")
    elif normalized_primary:
        resolved = resolve_claimed_path(package_path, repo_root, normalized_primary)
        if not resolved.exists():
            message = f"traceability.primary_discovery_file points to missing local path: {normalized_primary}"
            if strict_paths:
                report.error(manifest, message)
            else:
                report.warning(manifest, message)

    notes = package_path / "notes.md"
    validation = package_path / "validation.md"
    if not has_evidence_marker(notes) and not has_evidence_marker(validation):
        report.warning(package_path, "notes or validation should carry assumptions, findings, open questions, or validation strategy")

    if has_last_execution:
        tasks = package_path / "tasks.md"
        if not tasks.exists():
            report.error(manifest, "last_execution is present but tasks artifact is missing")
        if not (package_path / "implementation-notes.md").exists():
            report.error(manifest, "last_execution is present but current implementation-notes.md execution evidence is missing")

    if validation.exists():
        validation_text = read_text(validation)
        if VALIDATION_CLAIM_RE.search(validation_text) and not any(
            marker in validation_text.lower() for marker in ("command", "evidence", "source", "open questions", "not run")
        ):
            report.warning(validation, "validation success language appears without command, evidence, source, or not-run context")
    if notes.exists():
        notes_text = read_text(notes)
        if "## Execution Log" in notes_text:
            report.warning(notes, "legacy Execution Log in notes.md is not current evidence; run MAGIA ADAPT and keep notes.md planning-only")
        elif EXECUTION_CLAIM_RE.search(notes_text):
            report.warning(notes, "execution-like language appears in MAGO planning notes; move execution evidence to implementation-notes.md")


def run(target: Path, repo_root: Path | None, spec_ids: Iterable[str], strict_paths: bool) -> EvidenceReport:
    report = EvidenceReport()
    packages = find_packages(target, spec_ids)
    if not packages:
        report.error(target, "no spec packages found to validate")
        return report
    for package_path in packages:
        if not package_path.exists():
            report.error(package_path, "package path does not exist")
            continue
        validate_package(package_path, report, repo_root.resolve() if repo_root else None, strict_paths)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate MAGO package evidence and traceability contracts.")
    parser.add_argument("target", help="Spec package path or BOARD_ROOT containing specs/")
    parser.add_argument("--repo-root", help="Optional repository root for resolving repository-relative evidence paths")
    parser.add_argument("--spec-id", action="append", default=[], help="Limit validation to one spec id; repeat as needed")
    parser.add_argument("--strict-paths", action="store_true", help="Treat missing claimed local evidence paths as errors instead of warnings")
    parser.add_argument("--json-output", help="Optional path for JSON report")
    args = parser.parse_args(argv)

    report = run(Path(args.target), Path(args.repo_root) if args.repo_root else None, args.spec_id, args.strict_paths)
    payload = asdict(report)
    if args.json_output:
        out = Path(args.json_output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"wrote {out}")
    print(f"status: {report.status}")
    print(f"packages_checked: {report.packages_checked}")
    for issue in report.warnings:
        print(f"warning: {issue.path}: {issue.message}")
    for issue in report.errors:
        print(f"error: {issue.path}: {issue.message}")
    return 0 if report.status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
