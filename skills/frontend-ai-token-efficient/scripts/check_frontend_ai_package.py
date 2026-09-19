#!/usr/bin/env python3
"""Deterministic lightweight scanner for frontend AI-maintainability and leak-prevention signals."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

SCHEMA_VERSION = "2.0"
SCANNER_VERSION = "2.1.0"

SKIP_DIRS = {
    ".git",
    "node_modules",
    "dist",
    "build",
    "coverage",
    ".next",
    ".turbo",
    ".cache",
    "storybook-static",
}
TEXT_SUFFIXES = {".ts", ".tsx", ".js", ".jsx", ".md", ".html", ".css", ".scss", ".json", ".env", ".local", ".sample"}
MAX_FILE_BYTES = 1_000_000
SEVERITY_RANK = {"critical": 0, "high": 1, "medium": 2, "low": 3}

SECRET_ENV_RE = re.compile(r"\b(?:vite|next_public)_[a-z0-9_]*(?:secret|client_secret|token|password|private|credential|key)[a-z0-9_]*\b", re.I)
STORAGE_TOKEN_RE = re.compile(r"\b(?:localStorage|sessionStorage)\.(?:setItem|getItem)\([^)]*(?:token|auth|session|jwt|refresh)", re.I)
DIRECT_HTTP_RE = re.compile(r"\b(?:fetch\s*\(|axios\.)")
CONSOLE_RE = re.compile(r"\bconsole\.(?:log|debug|info|warn|error)\s*\(")
SHARED_IMPORTS_FEATURE_RE = re.compile(r"from\s+['\"][^'\"]*features/|from\s+['\"]@/features/")
FEATURE_IMPORTS_FEATURE_RE = re.compile(r"from\s+['\"][^'\"]*(?:\.\./)+[^'\"]*features/|from\s+['\"]@/features/")
BARREL_EXPORT_RE = re.compile(r"export\s+\*\s+from")


def iter_files(root: Path) -> Iterable[Path]:
    """Yield eligible files in stable repository-relative order."""
    paths: list[Path] = []
    for path in root.rglob("*"):
        try:
            rel_parts = path.relative_to(root).parts
        except ValueError:
            continue
        if any(part in SKIP_DIRS for part in rel_parts):
            continue
        if not path.is_file() or path.is_symlink():
            continue
        if path.stat().st_size > MAX_FILE_BYTES:
            continue
        if path.name.startswith(".env") or path.suffix.lower() in TEXT_SUFFIXES:
            paths.append(path)
    yield from sorted(paths, key=lambda p: p.relative_to(root).as_posix())


def read_bytes(path: Path) -> bytes:
    return path.read_bytes()


def decode_text(data: bytes) -> str:
    return data.decode("utf-8", errors="ignore")


def subject_for(root: Path, path: Path | None) -> str:
    if path is None:
        return "project"
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def add(
    findings: list[dict[str, Any]],
    *,
    root: Path,
    severity: str,
    code: str,
    path: Path | None,
    message: str,
    evidence: str = "",
    supported_fixes: Iterable[str] = (),
) -> None:
    findings.append(
        {
            "severity": severity,
            "code": code,
            "subject": subject_for(root, path),
            "path": str(path) if path else None,
            "message": message,
            "evidence": evidence[:240],
            "supported_fixes": list(supported_fixes),
        }
    )


def has_path(root: Path, relative: str) -> bool:
    return (root / relative).exists()


def finalize_report(root: Path, findings: list[dict[str, Any]], status: str | None = None, *, input_identity: dict[str, Any] | None = None) -> dict[str, Any]:
    findings.sort(
        key=lambda item: (
            SEVERITY_RANK.get(item.get("severity", "low"), 99),
            item.get("subject") or "",
            item.get("code") or "",
            item.get("message") or "",
            item.get("evidence") or "",
        )
    )
    counts = Counter(item.get("severity", "unknown") for item in findings)
    severities = [item.get("severity") for item in findings]
    resolved_status = status or ("pass" if not any(s in {"critical", "high"} for s in severities) else "review_required")
    return {
        "receipt_version": 1,
        "stage": "scan",
        "schema_version": SCHEMA_VERSION,
        "scanner_version": SCANNER_VERSION,
        "status": resolved_status,
        "target": str(root),
        "input_identity": input_identity or {"algorithm": "sha256", "sha256": None, "file_count": 0},
        "finding_count": len(findings),
        "severity_counts": {key: counts.get(key, 0) for key in ("critical", "high", "medium", "low")},
        "findings": findings,
        "limitations": [
            "heuristic scanner; confirm findings by reading the relevant files",
            "static scan does not prove runtime behavior, security assurance, accessibility, or repository-wide correctness",
        ],
    }


def scan(root: Path, *, exclude_paths: Iterable[Path] = ()) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    excluded = {p.resolve(strict=False) for p in exclude_paths}

    if not root.exists() or not root.is_dir():
        add(
            findings,
            root=root,
            severity="critical",
            code="target_missing",
            path=None,
            message="target directory not found",
            supported_fixes=("provide an existing frontend root directory",),
        )
        return finalize_report(root, findings, status="fail")

    scan_files = [path for path in iter_files(root) if path.resolve(strict=False) not in excluded]
    identity_hasher = hashlib.sha256()

    if has_path(root, "src"):
        for required in ["src/features", "src/shared"]:
            if not has_path(root, required):
                add(
                    findings,
                    root=root,
                    severity="medium",
                    code="missing_structure",
                    path=None,
                    message=f"recommended directory missing: {required}",
                    supported_fixes=("confirm the project uses another explicit ownership structure before creating directories",),
                )
    else:
        add(
            findings,
            root=root,
            severity="low",
            code="missing_src",
            path=None,
            message="src directory not found; scanner may not match this project layout",
            supported_fixes=("confirm the actual source root and treat this finding as layout-specific",),
        )

    for doc in ["AI_CONTEXT.md", "ARCHITECTURE.md", "CONVENTIONS.md", "DEPENDENCY_RULES.md", "SECURITY_FRONTEND.md"]:
        if not has_path(root, doc):
            add(
                findings,
                root=root,
                severity="low",
                code="missing_ai_doc",
                path=None,
                message=f"recommended ai guidance document missing: {doc}",
                evidence=doc,
                supported_fixes=("create only if it will encode real repository decisions and constraints",),
            )

    for path in scan_files:
        data = read_bytes(path)
        rel = path.relative_to(root).as_posix()
        encoded_rel = rel.encode("utf-8")
        identity_hasher.update(len(encoded_rel).to_bytes(8, "big"))
        identity_hasher.update(encoded_rel)
        identity_hasher.update(len(data).to_bytes(8, "big"))
        identity_hasher.update(data)
        text = decode_text(data)
        rel_parts = path.relative_to(root).parts
        lower_rel = rel.lower()

        for match in SECRET_ENV_RE.finditer(text):
            add(
                findings,
                root=root,
                severity="high",
                code="public_env_secret_like_name",
                path=path,
                message="public frontend environment variable looks secret-like",
                evidence=match.group(0),
                supported_fixes=("move real secrets behind a backend/BFF", "rename only when the value is confirmed public configuration"),
            )

        if STORAGE_TOKEN_RE.search(text):
            add(
                findings,
                root=root,
                severity="high",
                code="web_storage_token",
                path=path,
                message="token/session-like value appears to use localStorage or sessionStorage",
                supported_fixes=("prefer secure httpOnly sameSite cookies when architecture supports them", "document and constrain any unavoidable browser-memory token"),
            )

        if "dangerouslySetInnerHTML" in text:
            add(
                findings,
                root=root,
                severity="high",
                code="dangerous_html_rendering",
                path=path,
                message="dangerouslySetInnerHTML requires sanitizer and explicit approval",
                supported_fixes=("sanitize untrusted HTML with reviewed configuration", "avoid HTML injection when structured rendering is possible"),
            )

        if CONSOLE_RE.search(text) and ("src/" in lower_rel or lower_rel.startswith("src")):
            add(
                findings,
                root=root,
                severity="medium",
                code="console_logging",
                path=path,
                message="console logging in source can leak payloads or sensitive context",
                supported_fixes=("route logs through an allowlisted/redacting logger", "remove debug logging after confirming it is not required"),
            )

        is_component_area = "components" in rel_parts or path.suffix.lower() in {".tsx", ".jsx"}
        is_api_area = "api" in rel_parts or lower_rel.endswith(".api.ts") or lower_rel.endswith(".api.tsx")
        if is_component_area and not is_api_area and DIRECT_HTTP_RE.search(text):
            add(
                findings,
                root=root,
                severity="medium",
                code="direct_http_in_component",
                path=path,
                message="component-like file appears to call fetch or axios directly",
                supported_fixes=("move transport access to the feature API boundary and keep orchestration outside rendering",),
            )

        if rel.startswith("src/shared/") and SHARED_IMPORTS_FEATURE_RE.search(text):
            add(
                findings,
                root=root,
                severity="high",
                code="shared_imports_feature",
                path=path,
                message="shared layer must not import features",
                supported_fixes=("move domain behavior back to its feature/entity owner", "extract only a truly domain-neutral contract into shared"),
            )

        if rel.startswith("src/features/") and FEATURE_IMPORTS_FEATURE_RE.search(text):
            add(
                findings,
                root=root,
                severity="medium",
                code="feature_imports_feature",
                path=path,
                message="feature-to-feature imports increase coupling; prefer entities/shared or explicit composition",
                supported_fixes=("compose features at a route/app boundary", "extract a stable shared/entity contract only when ownership is clear"),
            )

        if path.name == "index.ts" and rel.startswith("src/features/") and BARREL_EXPORT_RE.search(text):
            add(
                findings,
                root=root,
                severity="low",
                code="broad_feature_barrel",
                path=path,
                message="broad export star in feature index can hide dependencies",
                supported_fixes=("export an explicit stable feature surface instead of export *",),
            )

    input_identity = {
        "algorithm": "sha256",
        "sha256": identity_hasher.hexdigest(),
        "file_count": len(scan_files),
        "excluded_paths": sorted(subject_for(root, p) for p in excluded if p == root or root in p.parents),
    }
    return finalize_report(root, findings, input_identity=input_identity)


def to_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Frontend AI Maintainability Scan",
        "",
        f"status: `{report['status']}`",
        f"target: `{report['target']}`",
        f"scanner: `{report.get('scanner_version', 'unknown')}`",
        "",
    ]
    findings = report.get("findings", [])
    if not findings:
        lines.append("no findings detected by the lightweight scanner.")
    else:
        lines.append("## findings")
        lines.append("")
        for item in findings:
            subject = item.get("subject") or item.get("path") or "project"
            lines.append(f"- **{item['severity']}** `{item['code']}` in `{subject}`: {item['message']}")
            if item.get("evidence"):
                lines.append(f"  - evidence: `{item['evidence']}`")
            for fix in item.get("supported_fixes", []):
                lines.append(f"  - supported fix: {fix}")
    lines.append("")
    lines.append("## limitations")
    lines.append("")
    for limitation in report.get("limitations", []):
        lines.append(f"- {limitation}")
    return "\n".join(lines) + "\n"


def preflight_output(root: Path, authored: Path) -> Path:
    if authored.exists() and authored.is_symlink():
        raise ValueError("output path must not be a symbolic link")
    resolved = authored.resolve(strict=False)
    if resolved == root.resolve(strict=False):
        raise ValueError("output path must not alias the scan root")
    if resolved.exists() and resolved.is_dir():
        raise ValueError("output path must be a file, not a directory")
    return resolved


def write_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    try:
        with tmp.open("w", encoding="utf-8", newline="") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        try:
            if tmp.exists():
                tmp.unlink()
        except OSError:
            pass


def main() -> int:
    parser = argparse.ArgumentParser(description="scan a frontend repo for ai-maintainability and leak-prevention signals")
    parser.add_argument("--target", required=True)
    parser.add_argument("--format", choices=["json", "markdown"], default="json")
    parser.add_argument("--output")
    args = parser.parse_args()

    root = Path(args.target).resolve()
    output = None
    exclude_paths: list[Path] = []
    if args.output:
        try:
            output = preflight_output(root, Path(args.output))
        except ValueError as exc:
            print(json.dumps({"status": "fail", "stage": "preflight", "code": "output_path_invalid", "message": str(exc)}, sort_keys=True), file=sys.stderr)
            return 2
        if output == root or root in output.parents:
            exclude_paths.append(output)

    report = scan(root, exclude_paths=exclude_paths)
    content = json.dumps(report, indent=2, sort_keys=True) + "\n" if args.format == "json" else to_markdown(report)
    if output is not None:
        write_atomic(output, content)
    else:
        print(content, end="")
    return 0 if report["status"] in {"pass", "review_required"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
