#!/usr/bin/env python3
"""Lightweight scanner for frontend projects optimized for AI maintainability and leak prevention."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

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

SECRET_ENV_RE = re.compile(r"\b(?:vite|next_public)_[a-z0-9_]*(?:secret|client_secret|token|password|private|credential|key)[a-z0-9_]*\b", re.I)
STORAGE_TOKEN_RE = re.compile(r"\b(?:localStorage|sessionStorage)\.(?:setItem|getItem)\([^)]*(?:token|auth|session|jwt|refresh)", re.I)
DIRECT_HTTP_RE = re.compile(r"\b(?:fetch\s*\(|axios\.)")
CONSOLE_RE = re.compile(r"\bconsole\.(?:log|debug|info|warn|error)\s*\(")
SHARED_IMPORTS_FEATURE_RE = re.compile(r"from\s+['\"][^'\"]*features/|from\s+['\"]@/features/")
FEATURE_IMPORTS_FEATURE_RE = re.compile(r"from\s+['\"][^'\"]*(?:\.\./)+[^'\"]*features/|from\s+['\"]@/features/")
BARREL_EXPORT_RE = re.compile(r"export\s+\*\s+from")


def iter_files(root: Path):
    for path in root.rglob("*"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if not path.is_file() or path.is_symlink():
            continue
        if path.stat().st_size > MAX_FILE_BYTES:
            continue
        if path.name.startswith(".env") or path.suffix.lower() in TEXT_SUFFIXES:
            yield path


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def add(findings: list[dict[str, Any]], severity: str, code: str, path: Path | None, message: str, evidence: str = ""):
    findings.append(
        {
            "severity": severity,
            "code": code,
            "path": str(path) if path else None,
            "message": message,
            "evidence": evidence[:240],
        }
    )


def has_path(root: Path, relative: str) -> bool:
    return (root / relative).exists()


def scan(root: Path) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []

    if not root.exists() or not root.is_dir():
        return {"status": "fail", "target": str(root), "findings": [{"severity": "critical", "code": "target_missing", "path": None, "message": "target directory not found", "evidence": ""}]}

    if has_path(root, "src"):
        for required in ["src/features", "src/shared"]:
            if not has_path(root, required):
                add(findings, "medium", "missing_structure", None, f"recommended directory missing: {required}")
    else:
        add(findings, "low", "missing_src", None, "src directory not found; scanner may not match this project layout")

    for doc in ["AI_CONTEXT.md", "ARCHITECTURE.md", "CONVENTIONS.md", "DEPENDENCY_RULES.md", "SECURITY_FRONTEND.md"]:
        if not has_path(root, doc):
            add(findings, "low", "missing_ai_doc", None, f"recommended ai guidance document missing: {doc}")

    for path in iter_files(root):
        text = read_text(path)
        rel_parts = path.relative_to(root).parts
        rel = path.relative_to(root).as_posix()
        lower_rel = rel.lower()

        for match in SECRET_ENV_RE.finditer(text):
            add(findings, "high", "public_env_secret_like_name", path, "public frontend environment variable looks secret-like", match.group(0))

        if STORAGE_TOKEN_RE.search(text):
            add(findings, "high", "web_storage_token", path, "token/session-like value appears to use localStorage or sessionStorage")

        if "dangerouslySetInnerHTML" in text:
            add(findings, "high", "dangerous_html_rendering", path, "dangerouslySetInnerHTML requires sanitizer and explicit approval")

        if CONSOLE_RE.search(text) and ("src/" in lower_rel or lower_rel.startswith("src")):
            add(findings, "medium", "console_logging", path, "console logging in source can leak payloads or sensitive context")

        is_component_area = "components" in rel_parts or path.suffix.lower() in {".tsx", ".jsx"}
        is_api_area = "api" in rel_parts or lower_rel.endswith(".api.ts") or lower_rel.endswith(".api.tsx")
        if is_component_area and not is_api_area and DIRECT_HTTP_RE.search(text):
            add(findings, "medium", "direct_http_in_component", path, "component-like file appears to call fetch or axios directly")

        if rel.startswith("src/shared/") and SHARED_IMPORTS_FEATURE_RE.search(text):
            add(findings, "high", "shared_imports_feature", path, "shared layer must not import features")

        if rel.startswith("src/features/") and FEATURE_IMPORTS_FEATURE_RE.search(text):
            add(findings, "medium", "feature_imports_feature", path, "feature-to-feature imports increase coupling; prefer entities/shared or explicit composition")

        if path.name == "index.ts" and rel.startswith("src/features/") and BARREL_EXPORT_RE.search(text):
            add(findings, "low", "broad_feature_barrel", path, "broad export star in feature index can hide dependencies")

    severities = [f["severity"] for f in findings]
    status = "pass" if not any(s in {"critical", "high"} for s in severities) else "review_required"
    return {"status": status, "target": str(root), "finding_count": len(findings), "findings": findings}


def to_markdown(report: dict[str, Any]) -> str:
    lines = ["# Frontend AI Maintainability Scan", "", f"status: `{report['status']}`", f"target: `{report['target']}`", ""]
    findings = report.get("findings", [])
    if not findings:
        lines.append("no findings detected by the lightweight scanner.")
        return "\n".join(lines) + "\n"
    lines.append("## findings")
    lines.append("")
    for item in findings:
        path = item.get("path") or "project"
        lines.append(f"- **{item['severity']}** `{item['code']}` in `{path}`: {item['message']}")
        if item.get("evidence"):
            lines.append(f"  - evidence: `{item['evidence']}`")
    lines.append("")
    lines.append("## limitations")
    lines.append("")
    lines.append("this scanner is heuristic. confirm findings by reading the relevant files before changing code.")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="scan a frontend repo for ai-maintainability and leak-prevention signals")
    parser.add_argument("--target", required=True)
    parser.add_argument("--format", choices=["json", "markdown"], default="json")
    parser.add_argument("--output")
    args = parser.parse_args()

    report = scan(Path(args.target).resolve())
    content = json.dumps(report, indent=2, sort_keys=True) + "\n" if args.format == "json" else to_markdown(report)
    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(content, encoding="utf-8")
    else:
        print(content, end="")
    return 0 if report["status"] in {"pass", "review_required"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
