#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from pypdf import PdfReader


def deref(obj):
    try:
        return obj.get_object()
    except Exception:
        return obj


def inspect(path: str) -> dict:
    reader = PdfReader(path, strict=False)
    if reader.is_encrypted:
        return {"status":"blocked","encrypted":True,"reason":"encrypted PDF; decrypt with authorized credentials before form inspection"}
    root = deref(reader.trailer["/Root"])
    acroform = deref(root.get("/AcroForm")) if root.get("/AcroForm") else None
    has_xfa = bool(acroform and hasattr(acroform, "get") and acroform.get("/XFA") is not None)
    fields = reader.get_fields() or {}
    signature_fields = [name for name, field in fields.items() if str(deref(field).get("/FT")) == "/Sig"]
    fillable = [name for name, field in fields.items() if str(deref(field).get("/FT")) in {"/Tx","/Btn","/Ch"}]
    mode = "xfa" if has_xfa else "acroform" if fillable else "non-fillable"
    return {
        "status":"ok",
        "encrypted":False,
        "mode":mode,
        "has_xfa":has_xfa,
        "fillable_field_count":len(fillable),
        "signature_field_count":len(signature_fields),
        "signature_fields":signature_fields,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify PDF form type before filling.")
    parser.add_argument("pdf")
    parser.add_argument("--json", action="store_true", help="Emit JSON only.")
    args = parser.parse_args()
    result = inspect(args.pdf)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif result.get("status") != "ok":
        print(f"BLOCKED: {result.get('reason')}")
    elif result["mode"] == "xfa":
        print("This PDF contains XFA. Do not use the bundled AcroForm fill script because XFA preservation is not supported.")
    elif result["mode"] == "acroform":
        suffix = " Digital signature fields are present; filling may invalidate signatures." if result["signature_field_count"] else ""
        print(f"This PDF has {result['fillable_field_count']} fillable AcroForm field(s).{suffix}")
    else:
        print("This PDF does not have supported fillable AcroForm fields; use the non-fillable/coordinate workflow.")
    return 0 if result.get("status") == "ok" else 2


if __name__ == "__main__":
    raise SystemExit(main())
