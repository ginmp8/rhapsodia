#!/usr/bin/env python3
import argparse
import json
import sys

from pypdf import PdfReader, PdfWriter

from extract_form_field_info import get_field_info


def deref(obj):
    try:
        return obj.get_object()
    except Exception:
        return obj


def assert_mutation_allowed(reader: PdfReader, allow_signature_invalidation: bool) -> None:
    if reader.is_encrypted:
        raise RuntimeError("encrypted PDF: decrypt with authorized credentials before filling")
    root = deref(reader.trailer["/Root"])
    acroform = deref(root.get("/AcroForm")) if root.get("/AcroForm") else None
    if acroform and hasattr(acroform, "get") and acroform.get("/XFA") is not None:
        raise RuntimeError("XFA detected: bundled AcroForm filling is blocked to avoid silent XFA loss")
    fields = reader.get_fields() or {}
    signature_fields = [name for name, field in fields.items() if str(deref(field).get("/FT")) == "/Sig"]
    if signature_fields and not allow_signature_invalidation:
        raise RuntimeError("digital signature field(s) detected: filling is blocked unless --allow-signature-invalidation is explicitly supplied")


def validation_error_for_field_value(field_info, field_value):
    field_type = field_info["type"]
    field_id = field_info["field_id"]
    if field_type == "checkbox":
        checked_val = field_info.get("checked_value")
        unchecked_val = field_info.get("unchecked_value")
        if checked_val is None or unchecked_val is None:
            return f'ERROR: checkbox field "{field_id}" has unresolved export values; inspect it before filling'
        if field_value != checked_val and field_value != unchecked_val:
            return f'ERROR: Invalid value "{field_value}" for checkbox field "{field_id}". Valid values are "{checked_val}" and "{unchecked_val}"'
    elif field_type == "radio_group":
        option_values = [opt["value"] for opt in field_info["radio_options"]]
        if field_value not in option_values:
            return f'ERROR: Invalid value "{field_value}" for radio group field "{field_id}". Valid values are: {option_values}'
    elif field_type == "choice":
        choice_values = [opt["value"] for opt in field_info["choice_options"]]
        if field_value not in choice_values:
            return f'ERROR: Invalid value "{field_value}" for choice field "{field_id}". Valid values are: {choice_values}'
    return None


def monkeypatch_pypdf_method():
    from pypdf.generic import DictionaryObject
    from pypdf.constants import FieldDictionaryAttributes

    original_get_inherited = DictionaryObject.get_inherited

    def patched_get_inherited(self, key: str, default=None):
        result = original_get_inherited(self, key, default)
        if key == FieldDictionaryAttributes.Opt:
            if isinstance(result, list) and all(isinstance(v, list) and len(v) == 2 for v in result):
                result = [r[0] for r in result]
        return result

    DictionaryObject.get_inherited = patched_get_inherited


def fill_pdf_fields(input_pdf_path: str, fields_json_path: str, output_pdf_path: str, allow_signature_invalidation: bool):
    with open(fields_json_path, encoding="utf-8") as f:
        fields = json.load(f)

    reader = PdfReader(input_pdf_path, strict=False)
    assert_mutation_allowed(reader, allow_signature_invalidation)

    fields_by_page = {}
    for field in fields:
        if "value" in field:
            fields_by_page.setdefault(field["page"], {})[field["field_id"]] = field["value"]

    has_error = False
    field_info = get_field_info(reader)
    fields_by_ids = {f["field_id"]: f for f in field_info}
    for field in fields:
        existing_field = fields_by_ids.get(field["field_id"])
        if not existing_field:
            has_error = True
            print(f"ERROR: `{field['field_id']}` is not a valid supported field ID")
        elif field["page"] != existing_field["page"]:
            has_error = True
            print(f"ERROR: Incorrect page number for `{field['field_id']}` (got {field['page']}, expected {existing_field['page']})")
        elif "value" in field:
            err = validation_error_for_field_value(existing_field, field["value"])
            if err:
                print(err)
                has_error = True
    if has_error:
        raise RuntimeError("field validation failed")

    writer = PdfWriter(clone_from=reader)
    for page, field_values in fields_by_page.items():
        writer.update_page_form_field_values(writer.pages[page - 1], field_values, auto_regenerate=False)
    writer.set_need_appearances_writer(True)
    with open(output_pdf_path, "wb") as f:
        writer.write(f)


def main() -> int:
    parser = argparse.ArgumentParser(description="Fill supported AcroForm fields after validating IDs and export values.")
    parser.add_argument("input_pdf")
    parser.add_argument("field_values_json")
    parser.add_argument("output_pdf")
    parser.add_argument("--allow-signature-invalidation", action="store_true")
    args = parser.parse_args()
    monkeypatch_pypdf_method()
    try:
        fill_pdf_fields(args.input_pdf, args.field_values_json, args.output_pdf, args.allow_signature_invalidation)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Wrote filled PDF to {args.output_pdf}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
