#!/usr/bin/env python3
"""Deterministic structural validator for agent-design output artifacts.

This validator checks contract shape and objective invariants only. It does not
claim that an agent prompt is semantically correct, safe, or high quality.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

RECEIPT_VERSION = 1
AGENT_REQUIRED_HEADINGS = {
    "role",
    "responsibilities",
    "boundaries",
    "workflow",
    "output contract",
    "stop conditions",
}
SPEC_REQUIRED_HEADINGS = {
    "operating surface",
    "contract identity",
    "mission",
    "inputs and context",
    "outputs",
    "authority boundary",
    "tool contract",
    "workflow",
    "handoffs",
    "state and termination",
    "stop conditions",
    "validation scenarios",
    "risks and trade-offs",
}
READ_ONLY_PROFILES = {"router", "review", "governance"}
WRITE_TOOL_MARKERS = {
    "write",
    "edit",
    "terminal",
    "shell",
    "bash",
    "powershell",
    "execute",
    "run_command",
    "create_file",
    "delete",
    "deploy",
    "apply_patch",
}


def normalize_heading(value: str) -> str:
    value = re.sub(r"\s+#+\s*$", "", value.strip())
    value = re.sub(r"^\d+(?:\.\d+)*[.)]?\s*", "", value)
    return re.sub(r"\s+", " ", value).strip().lower()


def headings(text: str) -> set[str]:
    found: set[str] = set()
    for line in text.splitlines():
        match = re.match(r"^#{1,6}\s+(.+?)\s*$", line)
        if match:
            found.add(normalize_heading(match.group(1)))
    return found


def frontmatter(text: str) -> tuple[dict[str, Any], list[str]]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, []
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return {}, []
    raw = lines[1:end]
    data: dict[str, Any] = {}
    current_list_key: str | None = None
    for line in raw:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        list_match = re.match(r"^\s*-\s+(.+?)\s*$", line)
        if list_match and current_list_key:
            data.setdefault(current_list_key, []).append(list_match.group(1).strip(" '\""))
            continue
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*?)\s*$", line)
        if not match:
            continue
        key, value = match.group(1), match.group(2)
        current_list_key = None
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            data[key] = [part.strip().strip("'\"") for part in inner.split(",") if part.strip()]
        elif value == "":
            data[key] = []
            current_list_key = key
        else:
            data[key] = value.strip(" '\"")
    return data, raw


def write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


def add_check(checks: list[dict[str, Any]], code: str, ok: bool, subject: str, evidence: dict[str, Any] | None = None) -> None:
    checks.append({
        "code": code,
        "status": "pass" if ok else "fail",
        "subject": subject,
        "evidence": evidence or {},
    })


def tool_names(data: dict[str, Any]) -> list[str]:
    value = data.get("tools", [])
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        return [part.strip() for part in value.split(",") if part.strip()]
    return []


def is_write_tool(name: str) -> bool:
    lowered = name.lower().replace("-", "_")
    tokens = set(re.split(r"[^a-z0-9_]+", lowered))
    return any(marker in lowered or marker in tokens for marker in WRITE_TOOL_MARKERS)


def validate_agent_md(text: str, profile: str, allow_write_tools: bool, checks: list[dict[str, Any]]) -> None:
    fm, _ = frontmatter(text)
    add_check(checks, "frontmatter/present", bool(fm), "frontmatter")
    add_check(checks, "frontmatter/name", bool(str(fm.get("name", "")).strip()), "name")
    add_check(checks, "frontmatter/description", bool(str(fm.get("description", "")).strip()), "description")

    found = headings(text)
    missing = sorted(AGENT_REQUIRED_HEADINGS - found)
    add_check(checks, "contract/required-headings", not missing, "agent-md", {"missing": missing})

    tools = tool_names(fm)
    if profile in READ_ONLY_PROFILES and not allow_write_tools:
        write_tools = sorted(tool for tool in tools if is_write_tool(tool))
        add_check(
            checks,
            "tools/least-authority-profile",
            not write_tools,
            profile,
            {"write_capable_tools": write_tools, "tools": tools},
        )
    if profile == "router":
        has_handoff = bool(re.search(r"\bhandoff\b|\broute\b|\bdispatch\b", text, re.IGNORECASE))
        add_check(checks, "router/handoff-contract", has_handoff, "router")


def validate_spec(text: str, checks: list[dict[str, Any]]) -> None:
    found = headings(text)
    missing = sorted(SPEC_REQUIRED_HEADINGS - found)
    add_check(checks, "contract/required-headings", not missing, "agent-spec", {"missing": missing})
    add_check(
        checks,
        "contract/identity",
        "agent-design-contract/v1" in text,
        "agent-design-contract/v1",
    )
    authority_terms = ["may decide", "may recommend", "may execute", "must not execute", "must escalate"]
    missing_authority = [term for term in authority_terms if term not in text.lower()]
    add_check(
        checks,
        "authority/complete-shape",
        not missing_authority,
        "authority boundary",
        {"missing": missing_authority},
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact")
    parser.add_argument("--kind", choices=["auto", "agent-md", "spec"], default="auto")
    parser.add_argument("--profile", choices=["generic", "router", "review", "governance", "controlled-executor"], default="generic")
    parser.add_argument("--allow-write-tools", action="store_true")
    parser.add_argument("--require-complete", action="store_true")
    parser.add_argument("--json", dest="json_path")
    args = parser.parse_args()

    artifact = Path(args.artifact)
    checks: list[dict[str, Any]] = []
    try:
        text = artifact.read_text(encoding="utf-8")
        add_check(checks, "input/readable-utf8", True, str(artifact))
    except Exception as exc:
        add_check(checks, "input/readable-utf8", False, str(artifact), {"error": str(exc)})
        text = ""

    kind = args.kind
    if kind == "auto":
        kind = "agent-md" if artifact.name.endswith(".agent.md") else "spec"

    if text:
        if kind == "agent-md":
            validate_agent_md(text, args.profile, args.allow_write_tools, checks)
        else:
            validate_spec(text, checks)
        if args.require_complete:
            placeholders = sorted(set(re.findall(r"\{\{[^{}]+\}\}", text)))
            add_check(checks, "content/no-template-placeholders", not placeholders, str(artifact), {"placeholders": placeholders})

    errors = sum(1 for check in checks if check["status"] == "fail")
    payload = {
        "receipt_version": RECEIPT_VERSION,
        "status": "pass" if errors == 0 else "fail",
        "stage": "validation",
        "kind": kind,
        "profile": args.profile,
        "artifact": str(artifact),
        "checks": checks,
        "errors": errors,
        "warnings": 0,
        "metrics": {"check_count": len(checks)},
        "limitations": [
            "Structural validation does not prove semantic quality, safety, or runtime behavior."
        ],
    }
    if args.json_path:
        write_json_atomic(Path(args.json_path), payload)
    else:
        json.dump(payload, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
        sys.stdout.flush()
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
