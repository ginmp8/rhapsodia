#!/usr/bin/env python3
"""Small baseline evaluator for a ChatGPT skill folder.

This is intentionally simple. It is not a replacement for a full behavioral
benchmark, but it gives the improvement loop a deterministic starter metric.
It prints JSON with a numeric score from 0 to 100.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def parse_frontmatter(text: str) -> dict[str, str]:
    match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return {}
    data: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def score_skill(path: Path) -> dict:
    skill_md = path / "SKILL.md"
    notes: list[str] = []
    score = 0.0

    if skill_md.exists():
        score += 10
        text = skill_md.read_text(encoding="utf-8", errors="replace")
    else:
        return {"score": 0, "status": "fail", "notes": ["missing SKILL.md"]}

    fm = parse_frontmatter(text)
    name = fm.get("name", "")
    description = fm.get("description", "")

    if name and re.match(r"^[a-z0-9-]+$", name):
        score += 10
    else:
        notes.append("missing or invalid hyphen-case name")

    if description:
        score += 10
        if 120 <= len(description) <= 1024:
            score += 5
        else:
            notes.append("description length is weak")
        if any(w in description.lower() for w in ["use when", "when asked", "use for", "trigger"]):
            score += 5
        else:
            notes.append("description lacks explicit trigger language")
        if any(w in description.lower() for w in ["do not", "never", "unless", "out of scope"]):
            score += 5
        else:
            notes.append("description lacks exclusion boundaries")
    else:
        notes.append("missing description")

    body = re.sub(r"^---\n.*?\n---", "", text, flags=re.DOTALL)
    if len(body.strip()) >= 500:
        score += 5
    else:
        notes.append("body is very short")

    headings = re.findall(r"^##+\s+", body, flags=re.MULTILINE)
    if len(headings) >= 3:
        score += 5
    else:
        notes.append("few markdown sections")

    if re.search(r"\b(workflow|steps?|process|procedure)\b", body, re.I):
        score += 7
    else:
        notes.append("no clear workflow language")

    if re.search(r"\b(required inputs?|inputs?|prerequisites?)\b", body, re.I):
        score += 6
    else:
        notes.append("no explicit input contract")

    if re.search(r"\b(output|deliverable|report|format|contract)\b", body, re.I):
        score += 6
    else:
        notes.append("no explicit output contract")

    if re.search(r"\b(validate|validation|checklist|acceptance|criteria|gate)\b", body, re.I):
        score += 7
    else:
        notes.append("no validation or acceptance criteria")

    placeholder_token = "TO" + "DO"
    bracket_placeholder_token = "[" + placeholder_token
    if placeholder_token not in text and bracket_placeholder_token not in text:
        score += 5
    else:
        notes.append("unresolved placeholder markers remain")

    if (path / "agents" / "openai.yaml").exists():
        score += 5
    else:
        notes.append("missing agents/openai.yaml")

    references = list((path / "references").glob("**/*")) if (path / "references").exists() else []
    scripts = list((path / "scripts").glob("**/*")) if (path / "scripts").exists() else []
    examples = list((path / "examples").glob("**/*")) if (path / "examples").exists() else []

    if any(p.is_file() for p in references):
        score += 5
    else:
        notes.append("no references")
    if any(p.is_file() for p in scripts):
        score += 3
    if any(p.is_file() for p in examples):
        score += 2

    score = max(0.0, min(100.0, score))
    return {"score": round(score, 2), "max_score": 100, "direction": "higher-is-better", "status": "pass", "notes": notes}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(score_skill(args.target.resolve()), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
