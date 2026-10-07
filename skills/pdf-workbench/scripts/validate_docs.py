#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

BANNED = {
    "pypdfium2-page-get-text": "page.get_text()",
    "qpdf-fix-qdf-option": "qpdf --fix-qdf",
    "qpdf-nonexistent-optimize-level": "--optimize-level=all",
    "host-private-openai-path": "/home/oai/skills/",
}
REQUIRED = {
    "xfa-guard": "XFA",
    "signed-pdf-guard": "digitally signed",
    "true-redaction": "true redaction",
    "tagged-pdf": "Tagged PDF",
    "pdf-ua": "PDF/UA",
    "ocr-mode": "OCR",
}


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    markdown = sorted([root / "SKILL.md", *root.joinpath("references").glob("*.md")])
    findings = []
    combined = "\n".join(p.read_text(encoding="utf-8") for p in markdown if p.exists())
    for code, token in BANNED.items():
        for p in markdown:
            if not p.exists():
                continue
            text = p.read_text(encoding="utf-8")
            if token in text:
                findings.append({"code":code,"severity":"error","subject":str(p.relative_to(root)),"evidence":token})
    for code, token in REQUIRED.items():
        if token.lower() not in combined.lower():
            findings.append({"code":code,"severity":"error","subject":"documentation","evidence":f"missing required token: {token}"})

    link_re = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    for p in markdown:
        if not p.exists():
            continue
        for target in link_re.findall(p.read_text(encoding="utf-8")):
            if "://" in target or target.startswith("#"):
                continue
            resolved = (p.parent / target.split("#",1)[0]).resolve()
            try:
                resolved.relative_to(root.resolve())
            except ValueError:
                findings.append({"code":"link-outside-root","severity":"error","subject":str(p.relative_to(root)),"evidence":target})
                continue
            if not resolved.exists():
                findings.append({"code":"broken-local-link","severity":"error","subject":str(p.relative_to(root)),"evidence":target})

    status = "pass" if not any(f["severity"] == "error" for f in findings) else "fail"
    result = {"status":status,"checked_markdown":[str(p.relative_to(root)) for p in markdown if p.exists()],"findings":findings}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
