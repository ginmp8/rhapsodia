# Executable PDF Toolkit

## At a glance

- **Purpose:** Give the agent a canonical executable path for recurring PDF operations instead of regenerating implementation code on every run.
- **Load when:** A requested operation maps to a bundled helper, or when choosing between a helper and the lower-level examples in `tooling.md`.
- **Decision impact:** Prefer the helper first; use the library/CLI example only when the helper is unavailable, insufficient for the requested variant, or diagnosis requires lower-level control.

## Core commands

```text
python scripts/pdf_inspect.py input.pdf --json
python scripts/pdf_preflight.py input.pdf

python scripts/pdf_extract.py text input.pdf --method pdfplumber --out text.txt
python scripts/pdf_extract.py words input.pdf --out words.csv
python scripts/pdf_extract.py chars input.pdf --out chars.csv
python scripts/pdf_extract.py tables input.pdf --out_dir tables --format json
python scripts/pdf_extract.py images input.pdf --out_dir images
python scripts/pdf_extract.py attachments input.pdf --out_dir attachments
python scripts/pdf_extract.py annotations input.pdf --out annotations.json
python scripts/pdf_extract.py forms input.pdf --out forms.json

python scripts/pdf_edit.py merge a.pdf b.pdf -o merged.pdf
python scripts/pdf_edit.py split input.pdf --out_dir split
python scripts/pdf_edit.py select input.pdf --pages 1-3,7 -o selected.pdf
python scripts/pdf_edit.py extract input.pdf --ranges 1-3,7,10-12 --out_dir ranges
python scripts/pdf_edit.py rotate input.pdf --angle 90 --pages 2,4 -o rotated.pdf
python scripts/pdf_edit.py crop input.pdf --inset 10pt --pages all -o cropped.pdf
python scripts/pdf_edit.py watermark input.pdf --watermark watermark.pdf -o watermarked.pdf
python scripts/pdf_edit.py paginate input.pdf -o numbered.pdf --format "{page}/{total}"
python scripts/pdf_edit.py encrypt input.pdf -o encrypted.pdf --user_password '<secret>'
python scripts/pdf_edit.py decrypt input.pdf -o decrypted.pdf --password '<secret>'
python scripts/pdf_edit.py repair input.pdf -o repaired.pdf
python scripts/pdf_edit.py optimize input.pdf -o optimized.pdf

python scripts/fill_fillable_fields.py input.pdf field_values.json output.pdf
python scripts/ocr_pdf.py scan.pdf -o searchable.pdf --lang eng
python scripts/ocr_pdf.py scan.pdf -o searchable.pdf --lang eng --fallback
python scripts/pdf_redact.py text input.pdf redacted.pdf --text "TOP SECRET"
python scripts/pdf_redact.py boxes input.pdf redacted.pdf --boxes_json boxes.json

python scripts/render_pdf.py input.pdf renders
python scripts/compare_renders.py before.pdf after.pdf --out_dir diff
```

## Selection rules

- Run preflight before mutation, OCR, redaction, repair, or form filling.
- Prefer `pdf_edit.py` for ordinary structural edits and `pdf_extract.py` for extraction; do not regenerate equivalent Python unless the helper cannot express the requested operation.
- Prefer `ocr_pdf.py` over hand-written raster/OCR loops. It uses OCRmyPDF when available and an explicit `pdftoppm + tesseract` fallback when requested.
- Prefer `pdf_redact.py` for true redaction. A visual overlay is not a substitute.
- For passwords, avoid reusable literal secrets; use ephemeral values and prefer external password-file/stdin mechanisms when the selected backend supports them.
- After geometry/content edits, render and inspect. For edits expected to be visually identical, use `compare_renders.py`.

## Lower-level fallback

Load `references/tooling.md` when a helper is unavailable, when a specialized variant is not represented by its CLI, or when debugging requires direct library/CLI control. Keep the same preflight and validation invariants.
