#!/usr/bin/env python3
"""Validate the thinking-token-efficient skill package with stable diagnostics."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REQUIRED_FILES = [
    "SKILL.md",
    "agents/openai.yaml",
    "assets/templates/private-ledger.md.template",
    "contracts/semantic-contract.json",
    "evals/activation-scenarios.json",
    "examples/activation-scenarios.md",
    "references/compression-protocol.md",
    "references/measurement-and-preservation.md",
    "references/semantic-safety.md",
    "references/technical-discipline.md",
    "references/validation-gates.md",
    "scripts/compare_candidate.py",
    "scripts/token_audit.py",
    "scripts/validate_skill.py",
]

REQUIRED_SKILL_TERMS = [
    "quality first",
    "do not reveal hidden chain of thought",
    "compression ladder",
    "evidence/citation/source/path/line",
    "executed and not-executed validation",
    "host telemetry",
    "stop conditions",
    "scripts/validate_skill.py",
]

REQUIRED_CATEGORIES = {
    "activation",
    "non_activation",
    "ambiguous",
    "edge_case",
    "regression",
    "scope",
    "output_contract",
    "adversarial",
}

REQUIRED_PROTECTED_CATEGORIES = {
    "urls",
    "paths",
    "commands",
    "env_vars",
    "schemas",
    "flags",
    "proper_nouns",
    "versions",
    "numbers",
    "safety_rules",
    "validation_rules",
    "evidence_rules",
}

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)
MD_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
CODE_REF_RE = re.compile(r"`([^`]+\.(?:md|py|json|yaml|yml|template|txt))`")
BLOCKED_PARTS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
BLOCKED_SUFFIXES = {".zip", ".tar", ".gz", ".pyc"}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="strict")


def diag(code: str, severity: str, subject: str, evidence: object) -> dict[str, object]:
    return {"code": code, "severity": severity, "subject": subject, "evidence": evidence}


def parse_frontmatter(text: str) -> dict[str, str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}
    data: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def local_refs(text: str) -> set[str]:
    refs: set[str] = set()
    for raw in MD_LINK_RE.findall(text):
        ref = raw.split("#", 1)[0].strip()
        if ref and "://" not in ref and not ref.startswith(("#", "/", "mailto:")):
            refs.add(ref)
    for raw in CODE_REF_RE.findall(text):
        if "://" not in raw and not raw.startswith("/"):
            refs.add(raw)
    return refs


def validate(root: Path) -> dict[str, object]:
    diagnostics: list[dict[str, object]] = []
    if not root.exists() or not root.is_dir():
        diagnostics.append(diag("TARGET_NOT_DIRECTORY", "error", str(root), "target must be an existing directory"))
        return build_result(diagnostics)

    for rel in REQUIRED_FILES:
        if not (root / rel).is_file():
            diagnostics.append(diag("REQUIRED_FILE_MISSING", "error", rel, "required package file"))

    skill_path = root / "SKILL.md"
    if skill_path.exists():
        text = read(skill_path)
        front = parse_frontmatter(text)
        if set(front) != {"name", "description"}:
            diagnostics.append(diag("FRONTMATTER_KEYS", "error", "SKILL.md", sorted(front)))
        if front.get("name") != "thinking-token-efficient":
            diagnostics.append(diag("FRONTMATTER_NAME", "error", "SKILL.md", front.get("name")))
        description = front.get("description", "")
        if len(description.split()) < 25:
            diagnostics.append(diag("DESCRIPTION_TOO_SHORT", "error", "SKILL.md", len(description.split())))
        if description != description.lower():
            diagnostics.append(diag("DESCRIPTION_NOT_LOWERCASE", "error", "SKILL.md", description))
        body = FRONTMATTER_RE.sub("", text, count=1)
        if len(body.splitlines()) > 500:
            diagnostics.append(diag("ENTRYPOINT_TOO_LONG", "error", "SKILL.md", len(body.splitlines())))
        if len(body.split()) > 900:
            diagnostics.append(diag("ENTRYPOINT_WORD_BUDGET", "warning", "SKILL.md", len(body.split())))
        lower = text.lower()
        for term in REQUIRED_SKILL_TERMS:
            if term not in lower:
                diagnostics.append(diag("REQUIRED_RULE_MISSING", "error", "SKILL.md", term))
        for ref in sorted(local_refs(text)):
            parts = Path(ref).parts
            if ".." in parts:
                diagnostics.append(diag("REFERENCE_ESCAPE", "error", ref, "local reference escapes package"))
            elif not (root / ref).exists():
                diagnostics.append(diag("REFERENCE_MISSING", "error", ref, "referenced from SKILL.md"))

    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if any(part in BLOCKED_PARTS for part in path.parts):
            diagnostics.append(diag("BLOCKED_GENERATED_PATH", "error", rel, "generated/cache path"))
        if path.suffix.lower() in BLOCKED_SUFFIXES:
            diagnostics.append(diag("BLOCKED_ARCHIVE_OR_CACHE", "error", rel, path.suffix.lower()))
        if path.suffix.lower() == ".py":
            try:
                compile(read(path), rel, "exec")
            except SyntaxError as exc:
                diagnostics.append(diag("PYTHON_SYNTAX", "error", rel, f"{exc.msg} at line {exc.lineno}"))

    eval_path = root / "evals/activation-scenarios.json"
    if eval_path.exists():
        try:
            payload = json.loads(read(eval_path))
            scenarios = payload.get("scenarios", [])
            if payload.get("status") != "planned":
                diagnostics.append(diag("EVAL_STATUS", "error", eval_path.name, payload.get("status")))
            ids = [item.get("id") for item in scenarios]
            if len(ids) != len(set(ids)):
                diagnostics.append(diag("EVAL_DUPLICATE_ID", "error", eval_path.name, ids))
            categories = {item.get("category") for item in scenarios}
            missing = REQUIRED_CATEGORIES - categories
            if missing:
                diagnostics.append(diag("EVAL_CATEGORY_MISSING", "error", eval_path.name, sorted(missing)))
            if len(scenarios) < 16:
                diagnostics.append(diag("EVAL_COUNT_LOW", "error", eval_path.name, len(scenarios)))
            for item in scenarios:
                for key in ("id", "type", "category", "prompt", "expected_behavior"):
                    if not item.get(key):
                        diagnostics.append(diag("EVAL_FIELD_MISSING", "error", str(item.get("id", "<no id>")), key))
        except Exception as exc:
            diagnostics.append(diag("EVAL_JSON_INVALID", "error", eval_path.name, str(exc)))

    contract_path = root / "contracts/semantic-contract.json"
    if contract_path.exists():
        try:
            contract = json.loads(read(contract_path))
            if contract.get("skill") != "thinking-token-efficient":
                diagnostics.append(diag("CONTRACT_SKILL", "error", contract_path.name, contract.get("skill")))
            categories = set(contract.get("protected_literal_categories", []))
            missing = REQUIRED_PROTECTED_CATEGORIES - categories
            if missing:
                diagnostics.append(diag("CONTRACT_CATEGORY_MISSING", "error", contract_path.name, sorted(missing)))
            if not contract.get("required_invariants"):
                diagnostics.append(diag("CONTRACT_INVARIANTS_EMPTY", "error", contract_path.name, "required_invariants"))
            progressive = contract.get("progressive_loading", {})
            if progressive.get("entrypoint") != "SKILL.md" or progressive.get("max_reference_depth") != 1:
                diagnostics.append(diag("PROGRESSIVE_LOADING_CONTRACT", "error", contract_path.name, progressive))
        except Exception as exc:
            diagnostics.append(diag("CONTRACT_JSON_INVALID", "error", contract_path.name, str(exc)))

    return build_result(diagnostics)


def build_result(diagnostics: list[dict[str, object]]) -> dict[str, object]:
    errors = [f"{d['code']}: {d['subject']}: {d['evidence']}" for d in diagnostics if d["severity"] == "error"]
    warnings = [f"{d['code']}: {d['subject']}: {d['evidence']}" for d in diagnostics if d["severity"] == "warning"]
    return {
        "validator_version": "2.0",
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "warnings": warnings,
        "diagnostics": diagnostics,
        "summary": {
            "errors": len(errors),
            "warnings": len(warnings),
            "diagnostics": len(diagnostics),
        },
    }


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("usage: validate_skill.py <skill-folder>", file=sys.stderr)
        return 2
    result = validate(Path(argv[0]).resolve())
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
