#!/usr/bin/env python3
"""Validate MAGO technical-design.md structure and architecture-doc boundaries."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

from mago_utils import strip_quotes

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None


REQUIRED_FRONTMATTER = (
    "spec_id",
    "order",
    "feature_key",
    "title",
    "type",
    "classification",
    "status",
    "phase",
    "cycle_version",
    "feature_version",
    "project_size",
    "project_types",
    "depends_on_features",
    "depends_on_specs",
)
VALID_PROJECT_SIZES = {"small", "medium", "large", "unknown"}
SECURITY_RISK_PROJECT_TYPES = {"identity_access", "sensitive_data", "regulated_data", "secret_handling", "trust_boundary"}
OPERABILITY_RISK_PROJECT_TYPES = {
    "production_change",
    "infrastructure_change",
    "external_integration",
    "migration",
    "data_change",
    "public_contract",
}
DEPRECATED_PRODUCT_TYPES = {"auth", "payment", "pii"}
REQUIRED_HEADINGS = (
    "## Context",
    "## Problem Statement",
    "## Scope",
    "## Technical Solution",
    "## Architecture Decisions",
    "## Security Considerations",
    "## Testing Strategy",
    "## Monitoring and Observability",
    "## Rollback Plan",
    "## Risks",
    "## Implementation Plan",
    "## Open Questions",
)
IMPLEMENTATION_CODE_FENCES = {
    "bash",
    "sh",
    "shell",
    "powershell",
    "ps1",
    "python",
    "py",
    "javascript",
    "js",
    "typescript",
    "ts",
    "tsx",
    "jsx",
    "csharp",
    "cs",
    "java",
    "go",
    "rust",
    "ruby",
}
TEMPLATE_TOKEN_RE = re.compile(r"<[A-Za-z0-9_|.-]+>")
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
FENCE_RE = re.compile(r"^```(?P<lang>[A-Za-z0-9_-]+)?\s*$")
SECTION_HEADING_RE = re.compile(r"^##\s+.+$")


def split_frontmatter(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    start = next((index for index, line in enumerate(lines) if line.strip() == "---"), None)
    if start is None:
        raise ValueError("missing YAML front matter")
    end = next((index for index, line in enumerate(lines[start + 1 :], start=start + 1) if line.strip() == "---"), None)
    if end is None:
        raise ValueError("YAML front matter is not closed")
    if yaml is None:
        raise ValueError("PyYAML is required to validate technical-design.md")
    data = yaml.safe_load("\n".join(lines[start + 1 : end])) or {}
    if not isinstance(data, dict):
        raise ValueError("front matter must be a mapping")
    return data, "\n".join(lines[end + 1 :])


def find_unresolved_tokens(text: str) -> list[str]:
    text = HTML_COMMENT_RE.sub("", text)
    return sorted(set(TEMPLATE_TOKEN_RE.findall(text)))


def normalize_string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    normalized: list[str] = []
    for item in value:
        text = strip_quotes(str(item)).lower() if item is not None else ""
        if text:
            normalized.append(text)
    return normalized


def section_content(body: str, heading: str) -> str:
    lines = body.splitlines()
    try:
        start = next(index for index, line in enumerate(lines) if line.strip() == heading)
    except StopIteration:
        return ""

    collected: list[str] = []
    for line in lines[start + 1 :]:
        if SECTION_HEADING_RE.match(line.strip()):
            break
        if line.strip().startswith("### "):
            continue
        collected.append(line)

    return HTML_COMMENT_RE.sub("", "\n".join(collected)).strip()


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return [f"{path}: missing file"]
    if path.name != "technical-design.md":
        return [f"{path}: expected technical-design.md"]

    try:
        frontmatter, body = split_frontmatter(path)
    except Exception as exc:
        return [f"{path}: {exc}"]

    for key in REQUIRED_FRONTMATTER:
        if key not in frontmatter:
            errors.append(f"{path}: missing front matter key `{key}`")

    project_size = strip_quotes(str(frontmatter.get("project_size"))) if frontmatter.get("project_size") is not None else None
    if project_size and project_size not in VALID_PROJECT_SIZES:
        errors.append(f"{path}: `project_size` must be one of {sorted(VALID_PROJECT_SIZES)}")

    if "project_types" in frontmatter and not isinstance(frontmatter.get("project_types"), list):
        errors.append(f"{path}: `project_types` must be a list")
    project_types = set(normalize_string_list(frontmatter.get("project_types")))
    deprecated_types = sorted(project_types & DEPRECATED_PRODUCT_TYPES)
    if deprecated_types:
        errors.append(
            f"{path}: `project_types` must use product-agnostic risk tags, not {', '.join(deprecated_types)}"
        )
    for list_key in ("depends_on_features", "depends_on_specs"):
        if list_key in frontmatter and not isinstance(frontmatter.get(list_key), list):
            errors.append(f"{path}: `{list_key}` must be a list")

    h1_lines = [line.strip() for line in body.splitlines() if line.startswith("# ")]
    if len(h1_lines) != 1:
        errors.append(f"{path}: expected exactly one H1")
    elif not h1_lines[0].startswith("# Technical Design - "):
        errors.append(f"{path}: H1 must start with `# Technical Design - `")

    body_lines = {line.strip() for line in body.splitlines()}
    for heading in REQUIRED_HEADINGS:
        if heading not in body_lines:
            errors.append(f"{path}: missing heading `{heading}`")

    critical_headings: set[str] = set()
    if project_types & SECURITY_RISK_PROJECT_TYPES:
        critical_headings.add("## Security Considerations")
    if project_types & OPERABILITY_RISK_PROJECT_TYPES:
        critical_headings.update(
            {
                "## Testing Strategy",
                "## Monitoring and Observability",
                "## Rollback Plan",
                "## Risks",
            }
        )
    if project_size in {"medium", "large"}:
        critical_headings.update({"## Technical Solution", "## Architecture Decisions", "## Risks"})

    for heading in sorted(critical_headings):
        if heading in body_lines and not section_content(body, heading):
            errors.append(f"{path}: `{heading}` needs explicit content for project_size/project_types risk gates")

    tokens = find_unresolved_tokens(path.read_text(encoding="utf-8"))
    if tokens:
        errors.append(f"{path}: contains unresolved template token(s): {', '.join(tokens)}")

    for line_number, line in enumerate(body.splitlines(), start=1):
        match = FENCE_RE.match(line.strip())
        if not match:
            continue
        language = (match.group("lang") or "").lower()
        if language in IMPLEMENTATION_CODE_FENCES:
            errors.append(
                f"{path}:{line_number}: implementation code fence `{language}` is not allowed in technical-design.md"
            )

    return errors


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Validate MAGO technical-design.md.")
    parser.add_argument("paths", nargs="+", help="technical-design.md path(s) to validate.")
    args = parser.parse_args(argv)

    errors: list[str] = []
    for raw_path in args.paths:
        errors.extend(validate(Path(raw_path).resolve()))

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"FAILED: {len(errors)} errors, 0 warnings")
        return 1

    print(f"OK: validated {len(args.paths)} technical design artifact(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
