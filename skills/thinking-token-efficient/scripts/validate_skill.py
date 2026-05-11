#!/usr/bin/env python3
"""Validate the thinking-token-efficient skill package."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REQUIRED_FILES = [
    "SKILL.md",
    "references/compression-protocol.md",
    "references/semantic-safety.md",
    "references/technical-discipline.md",
    "references/validation-gates.md",
    "examples/activation-scenarios.md",
    "evals/activation-scenarios.json",
    "assets/templates/private-ledger.md.template",
    "agents/openai.yaml",
]

REQUIRED_SKILL_TERMS = [
    "quality first",
    "do not reveal hidden chain of thought",
    "compression ladder",
    "evidence/citation/source/path/line",
    "executed and not-executed validation",
    "stop conditions",
    "scripts/validate_skill.py",
]

REQUIRED_CATEGORIES = {
    "activation",
    "non_activation",
    "ambiguous",
    "edge_case",
    "regression",
}

CJK_RE = re.compile("[\u3400-\u9fff\uf900-\ufaff]")
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)
MD_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
CODE_REF_RE = re.compile(r"`([^`]+\.(?:md|py|json|yaml|yml|template|txt))`")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_frontmatter(text: str) -> dict[str, str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}
    data = {}
    for line in match.group(1).splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def local_refs(text: str) -> set[str]:
    refs = set()
    for raw in MD_LINK_RE.findall(text):
        ref = raw.split("#", 1)[0].strip()
        if ref and "://" not in ref and not ref.startswith(("#", "/", "mailto:")):
            refs.add(ref)
    for raw in CODE_REF_RE.findall(text):
        if "://" not in raw and not raw.startswith("/"):
            refs.add(raw)
    return refs


def validate(root: Path) -> dict[str, object]:
    errors: list[str] = []
    warnings: list[str] = []
    if not root.exists() or not root.is_dir():
        return {"status": "fail", "errors": [f"target is not a directory: {root}"], "warnings": []}

    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            errors.append(f"required file missing: {rel}")

    skill_path = root / "SKILL.md"
    if skill_path.exists():
        text = read(skill_path)
        front = parse_frontmatter(text)
        if front.get("name") != "thinking-token-efficient":
            errors.append("frontmatter name mismatch")
        description = front.get("description", "")
        if len(description.split()) < 25:
            errors.append("frontmatter description too short")
        if description != description.lower():
            errors.append("frontmatter description must be lowercase")
        lower = text.lower()
        for term in REQUIRED_SKILL_TERMS:
            if term not in lower:
                errors.append(f"missing required skill term: {term}")
        for ref in sorted(local_refs(text)):
            if ".." in Path(ref).parts:
                errors.append(f"local reference escapes package: {ref}")
            elif not (root / ref).exists():
                errors.append(f"local reference missing: {ref}")

    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if any(part in {".git", "__pycache__", ".pytest_cache"} for part in path.parts):
            errors.append(f"blocked generated path present: {rel}")
        if path.suffix.lower() in {".md", ".txt", ".yaml", ".yml", ".json", ".py", ".template"}:
            text = read(path)
            if CJK_RE.search(text):
                errors.append(f"cjk characters found in text file: {rel}")
            if "raw hidden reasoning" in text.lower() and "do not reveal" not in text.lower() and "without exposing" not in text.lower():
                warnings.append(f"raw reasoning phrase lacks nearby boundary language: {rel}")

    eval_path = root / "evals/activation-scenarios.json"
    if eval_path.exists():
        try:
            payload = json.loads(read(eval_path))
            scenarios = payload.get("scenarios", [])
            categories = {item.get("category") for item in scenarios}
            missing = REQUIRED_CATEGORIES - categories
            if missing:
                errors.append(f"eval categories missing: {sorted(missing)}")
            if len(scenarios) < 10:
                errors.append("too few eval scenarios")
            for item in scenarios:
                for key in ("id", "type", "prompt", "expected_behavior"):
                    if not item.get(key):
                        errors.append(f"scenario {item.get('id', '<no id>')} missing {key}")
        except Exception as exc:
            errors.append(f"eval json invalid: {exc}")

    status = "pass" if not errors else "fail"
    return {"status": status, "errors": errors, "warnings": warnings}


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("usage: validate_skill.py <skill-folder>", file=sys.stderr)
        return 2
    result = validate(Path(argv[0]).resolve())
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
