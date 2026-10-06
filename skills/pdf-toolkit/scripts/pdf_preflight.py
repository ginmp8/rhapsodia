#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path


def _deref(obj):
    try:
        return obj.get_object()
    except Exception:
        return obj


def _has_js_action(obj) -> bool:
    obj = _deref(obj)
    if not hasattr(obj, "get"):
        return False
    try:
        return str(obj.get("/S")) == "/JavaScript" or "/JS" in obj
    except Exception:
        return False


def inspect_pdf(path: Path, password: str | None, sample_pages: int) -> dict:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        return {
            "schema_version": 1,
            "status": "blocked",
            "file": str(path),
            "error": "pypdf is required for this preflight script",
            "detail": str(exc),
        }

    result = {
        "schema_version": 1,
        "status": "ok",
        "file": str(path),
        "exists": path.is_file(),
        "encrypted": None,
        "decrypted": None,
        "page_count": None,
        "has_acroform": False,
        "has_xfa": False,
        "has_signature_fields": False,
        "has_structure_tree": False,
        "has_embedded_files": False,
        "has_javascript": False,
        "annotation_count": 0,
        "redaction_annotation_count": 0,
        "sampled_text_pages": 0,
        "sampled_nonempty_text_pages": 0,
        "warnings": [],
    }
    if not path.is_file():
        result["status"] = "error"
        result["warnings"].append("input file does not exist")
        return result

    try:
        reader = PdfReader(str(path), strict=False)
    except Exception as exc:
        result["status"] = "error"
        result["warnings"].append(f"reader failed: {type(exc).__name__}: {exc}")
        return result

    result["encrypted"] = bool(reader.is_encrypted)
    if reader.is_encrypted:
        if password is None:
            result["status"] = "blocked"
            result["decrypted"] = False
            result["warnings"].append("encrypted PDF requires a password for deeper inspection")
            return result
        try:
            decrypt_result = reader.decrypt(password)
            result["decrypted"] = bool(decrypt_result)
            if not decrypt_result:
                result["status"] = "blocked"
                result["warnings"].append("password did not decrypt the PDF")
                return result
        except Exception as exc:
            result["status"] = "blocked"
            result["decrypted"] = False
            result["warnings"].append(f"decryption failed: {type(exc).__name__}: {exc}")
            return result
    else:
        result["decrypted"] = True

    try:
        root = _deref(reader.trailer["/Root"])
        acroform = _deref(root.get("/AcroForm")) if root.get("/AcroForm") else None
        result["has_acroform"] = bool(acroform)
        result["has_xfa"] = bool(acroform and hasattr(acroform, "get") and acroform.get("/XFA") is not None)
        result["has_structure_tree"] = root.get("/StructTreeRoot") is not None
        names = _deref(root.get("/Names")) if root.get("/Names") else None
        if names and hasattr(names, "get"):
            result["has_embedded_files"] = names.get("/EmbeddedFiles") is not None
            result["has_javascript"] = names.get("/JavaScript") is not None
        if _has_js_action(root.get("/OpenAction")):
            result["has_javascript"] = True
        if root.get("/AA") is not None:
            result["has_javascript"] = True
    except Exception as exc:
        result["warnings"].append(f"catalog inspection incomplete: {type(exc).__name__}: {exc}")

    try:
        fields = reader.get_fields() or {}
        for field in fields.values():
            if str(_deref(field).get("/FT")) == "/Sig":
                result["has_signature_fields"] = True
                break
    except Exception as exc:
        result["warnings"].append(f"form field inspection incomplete: {type(exc).__name__}: {exc}")

    try:
        result["page_count"] = len(reader.pages)
        for index, page in enumerate(reader.pages):
            for ann_ref in page.get("/Annots", []) or []:
                ann = _deref(ann_ref)
                result["annotation_count"] += 1
                if hasattr(ann, "get") and str(ann.get("/Subtype")) == "/Redact":
                    result["redaction_annotation_count"] += 1
            if index < sample_pages:
                result["sampled_text_pages"] += 1
                try:
                    text = page.extract_text() or ""
                    if text.strip():
                        result["sampled_nonempty_text_pages"] += 1
                except Exception as exc:
                    result["warnings"].append(f"text extraction failed on page {index + 1}: {type(exc).__name__}")
    except Exception as exc:
        result["status"] = "error"
        result["warnings"].append(f"page inspection failed: {type(exc).__name__}: {exc}")

    if result["has_signature_fields"]:
        result["warnings"].append("digital signature field detected; mutation may invalidate signatures")
    if result["has_xfa"]:
        result["warnings"].append("XFA detected; do not use a form tool that cannot preserve XFA")
    if result["redaction_annotation_count"]:
        result["warnings"].append("redaction annotations detected; annotations alone do not prove underlying content was purged")
    if result["has_javascript"] or result["has_embedded_files"]:
        result["warnings"].append("active/embedded content detected; treat as untrusted and do not execute attachments or JavaScript")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Preflight a PDF before mutation.")
    parser.add_argument("pdf")
    parser.add_argument("--password-file", help="Read the first line as the PDF password; never printed.")
    parser.add_argument("--sample-pages", type=int, default=3)
    parser.add_argument("--json-output")
    args = parser.parse_args()
    password = None
    if args.password_file:
        password = Path(args.password_file).read_text(encoding="utf-8").splitlines()[0]
    result = inspect_pdf(Path(args.pdf), password, max(0, args.sample_pages))
    text = json.dumps(result, indent=2, sort_keys=True)
    print(text)
    if args.json_output:
        Path(args.json_output).write_text(text + "\n", encoding="utf-8")
    return 0 if result["status"] == "ok" else 2


if __name__ == "__main__":
    raise SystemExit(main())
