# PDF Forms

## At a glance

- **Purpose:** Route AcroForm, XFA and non-fillable forms safely and define the deterministic helper sequence for field discovery, coordinate placement, filling and visual verification.
- **Load when:** Filling, inspecting, flattening, or stamping an existing PDF form.
- **Decision impact:** Prevents silent XFA/signature damage, chooses field-based versus coordinate-based filling, and fixes the required validation order.

## Contents

- Form routing
- AcroForm workflow
- Non-fillable workflow
- Coordinate rules
- Appearance and Unicode checks
- Final verification

## Form routing

Run preflight first:

```text
python scripts/pdf_preflight.py input.pdf
```

Then classify:

1. **Digitally signed:** do not mutate unless the user explicitly accepts signature invalidation in the produced copy.
2. **XFA present:** do not call a tool path known to remove/ignore XFA. Report the limitation or use an XFA-capable workflow available in the environment.
3. **AcroForm fields present:** use the fillable-field workflow below.
4. **No fillable fields:** use structure-based stamping first, then visual coordinate estimation only as fallback.

`pdf-lib` is suitable for many AcroForm tasks but does not support reading/writing XFA fields. Do not use `getForm()` blindly on an XFA document.

## AcroForm workflow

1. Detect fields:

```text
python scripts/check_fillable_fields.py input.pdf
```

2. Extract field types, page positions and legal checkbox/radio/choice values:

```text
python scripts/extract_form_field_info.py input.pdf field_info.json
```

3. Render the pages and map field IDs to their visible labels:

```text
python scripts/render_pdf.py input.pdf renders
```

4. Create `field_values.json` with only validated field IDs/pages/values.
5. Fill to a new file:

```text
python scripts/fill_fillable_fields.py input.pdf field_values.json output.pdf
```

6. Re-open and render `output.pdf`; verify every changed field visually. Appearance streams differ across viewers, so a correct field value alone is not enough.

Example value record:

```json
{
  "field_id": "customer.name",
  "description": "Customer legal name",
  "page": 1,
  "value": "Example Ltd"
}
```

For checkboxes/radio groups/choices, use the exact export values returned by `extract_form_field_info.py`.

## Non-fillable workflow

Prefer structure-derived coordinates:

```text
python scripts/extract_form_structure.py input.pdf form_structure.json
```

Use extracted labels, lines and checkbox rectangles to define entry boxes. Validate them before stamping:

```text
python scripts/check_bounding_boxes.py fields.json
python scripts/fill_pdf_form_with_annotations.py input.pdf fields.json output.pdf
```

If structure extraction is unusable (for example, a scanned form), render the page, estimate a rough region, inspect a zoomed crop with any available image tool, then convert image coordinates into PDF coordinates before filling.

## Coordinate rules

- PDF points usually use origin at bottom-left; rendered-image pixels use origin at top-left.
- Use one coordinate system in a field manifest. Convert explicitly before combining sources.
- For image -> PDF conversion:

```text
pdf_x = image_x * pdf_width / image_width
pdf_y_top = image_y * pdf_height / image_height
```

Convert vertical orientation as required by the stamping script's documented convention. Never copy a y coordinate between systems without checking its origin.

## Appearance and Unicode checks

- Form values and their visible appearances are separate PDF concerns.
- If a viewer shows blank/missing glyphs, verify font coverage and appearance generation; do not assume the stored field value is wrong.
- For complex scripts or non-Latin characters, test with the actual target viewer/toolchain when appearance fidelity matters.
- Flatten only when the user wants a non-editable visual result and the consequences for forms/signatures/accessibility are acceptable.

## Final verification

Require all applicable checks:

- expected field count and IDs;
- legal option/export values;
- output re-opens without parser errors;
- rendered values are aligned and legible;
- no unintended field changes;
- XFA/signature constraints were respected;
- no sensitive debug JSON is included in the final deliverable unless requested.
