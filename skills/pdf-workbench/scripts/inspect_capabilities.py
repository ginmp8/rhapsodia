#!/usr/bin/env python3
import importlib.util
import json
import platform
import shutil
import sys

PY_MODULES = ["pypdf", "pdfplumber", "pypdfium2", "PIL", "fitz", "reportlab", "openpyxl"]
EXECUTABLES = ["qpdf", "pdftotext", "pdftoppm", "pdfimages", "ocrmypdf", "tesseract", "verapdf", "gs"]


def main() -> int:
    modules = {name: bool(importlib.util.find_spec(name)) for name in PY_MODULES}
    executables = {name: shutil.which(name) for name in EXECUTABLES}
    result = {
        "schema_version": 1,
        "python": {
            "executable": sys.executable,
            "version": platform.python_version(),
            "platform": platform.system().lower(),
        },
        "python_modules": modules,
        "executables": executables,
        "capabilities": {
            "pdf_structure": modules["pypdf"] or bool(executables["qpdf"]),
            "layout_extraction": modules["pdfplumber"] or bool(executables["pdftotext"]),
            "rendering": modules["pypdfium2"] or bool(executables["pdftoppm"]),
            "ocr_searchable_pdf": bool(executables["ocrmypdf"]) or (bool(executables["tesseract"]) and bool(executables["pdftoppm"])),
            "pdf_conformance_validation": bool(executables["verapdf"]),
            "true_redaction_python": modules["fitz"],
        },
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
