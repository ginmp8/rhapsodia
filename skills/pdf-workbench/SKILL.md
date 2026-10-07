---
name: pdf-workbench
description: Work with PDF files reliably across reading/review, text or table extraction, merge/split/rotate/crop/watermark, creation/conversion, forms, OCR, redaction, encryption, images, repair, and PDF/A or PDF/UA validation. Use when PDF is the primary input or output, including scanned, fillable, signed, encrypted, tagged, or damaged PDFs. Do not use for ordinary DOCX/PPTX/XLSX work unless PDF conversion or PDF-specific validation is the actual goal.
---

# PDF Processing

## Purpose and scope

Treat PDF work as a document-integrity workflow, not a collection of library snippets. Preserve the user's content and semantics, detect risky document features before mutation, choose tools by capability rather than host name, and verify the exact output before delivery.

## Router

Choose the smallest branch that satisfies the request:

| Need | Primary branch | Load |
|---|---|---|
| Read/review, text, tables, images, metadata | extract/review | `references/operations.md` |
| Merge, split, rotate, crop, watermark, encrypt, repair | edit | `references/operations.md` |
| Create or convert to PDF | create/convert | `references/operations.md` |
| Fill an existing form or stamp a non-fillable form | forms | `references/forms.md` |
| OCR scanned or mixed PDFs | OCR | `references/safety-ocr-conformance.md` |
| Remove sensitive content | redaction | `references/safety-ocr-conformance.md` |
| Signed, XFA, encrypted, damaged, untrusted, tagged, PDF/A/UA | safety/conformance | `references/safety-ocr-conformance.md` |
| Need canonical executable command | executable toolkit | `references/executable-toolkit.md` |
| Need exact library/CLI examples or custom fallback | tooling | `references/tooling.md` |

## Core workflow

1. **Resolve inputs and intent.** Identify exact files, requested pages/ranges, preservation requirements, output format, and whether mutation is allowed.
2. **Detect capabilities.** Prefer `python scripts/inspect_capabilities.py`; choose among available equivalent tools. Do not require a host-specific tool name or absolute skill path.
3. **Preflight risky inputs.** Before editing, OCR, form filling, redaction, repair, or conversion, run `python scripts/pdf_preflight.py <input.pdf>` when `pypdf` is available. Treat signatures, XFA, encryption, attachments/active content, unusual structure, and parser warnings as routing signals.
4. **Render before mutation when appearance matters.** Use `python scripts/render_pdf.py <input.pdf> <dir>` or another available renderer. Inspect the rendered pages instead of assuming extracted text represents layout.
5. **Operate with the canonical helper first.** Use the bundled helper from `references/executable-toolkit.md` when it covers the request; write ad-hoc implementation only when the helper cannot express the required variant. Preserve unrelated content and document features. Prefer structure/semantics over OCR when they already exist.
6. **Validate the result.** Re-run structural checks and task-specific checks. For visual changes, re-render the output and inspect it; use `scripts/compare_renders.py` when a before/after pixel comparison is meaningful.
7. **Deliver only the final artifact.** Keep intermediate renders, debug JSON, passwords, and temporary files out of the deliverable set unless requested.

## Critical invariants

- **Signed PDF:** do not silently modify a digitally signed PDF. Stop or require explicit intent to create a modified copy whose signature may become invalid.
- **XFA:** do not route XFA forms through a tool that cannot preserve XFA. Detect first; never let a convenience API silently delete XFA data.
- **Redaction:** drawing a box or adding a redaction annotation is not sufficient. Require true underlying-content removal plus post-redaction extraction/inspection.
- **OCR:** do not rasterize a born-digital or tagged PDF by default. Select OCR mode based on whether existing text, forms, links, annotations, signatures, or structure must survive.
- **Tagged PDF:** when a structure tree exists, prefer explicit reading order/semantics before coordinate heuristics or OCR.
- **Untrusted/damaged PDF:** keep parser/resource safety limits enabled. Do not disable conservative limits merely to force success on a malformed file.
- **External tools:** resolve only the documented local executable by capability, pass structured argument arrays, use finite subprocess timeouts, and never install or download a dependency automatically.
- **Passwords:** do not place secret values in command arguments, logs, source files, or reusable examples. Bundled helpers use password-file inputs; keep password files ephemeral, permission-restricted where possible, and out of deliverables.
- **Coordinates:** explicitly track whether coordinates are PDF points (origin usually bottom-left) or rendered-image pixels (origin top-left). Never mix them without conversion.
- **Creation quality:** no clipped text, overlaps, broken glyphs, missing pages, or accidental font substitution in the final render.
- **Claims:** structural validation, visual inspection, OCR accuracy, accessibility, archival conformance, and signature validity are distinct claims; do not substitute one for another.

## Reproducibility controls

- Route by document state and requested operation, not by whichever library example is easiest.
- Use deterministic scripts for recurring edit/extract/OCR/redaction work, capability detection, preflight, coordinate validation, rendering, and regression checks when available.
- **Advertised-capability rule:** every operation exposed by this skill must have either a bundled executable helper or a complete canonical example recorded in `references/capability-registry.json`; frequent, destructive, security-sensitive, or multi-step operations should prefer a helper.
- Keep source files unchanged; write to a new output unless the user explicitly requests in-place replacement and rollback is safe.
- Freeze the final passing output: any later edit requires affected validation to run again.
- Prefer stable diagnostics and machine-readable JSON for preflight/comparison results.

## Direct resources

- [operations](references/operations.md) - reading, extraction, edit, creation, conversion, tool-selection rules.
- [executable toolkit](references/executable-toolkit.md) - canonical helper commands for recurring operations.
- `references/capability-registry.json` - machine-readable advertised-capability coverage map.
- [forms](references/forms.md) - AcroForm/XFA/non-fillable routing and existing form helper scripts.
- [safety, OCR and conformance](references/safety-ocr-conformance.md) - signatures, untrusted inputs, OCR, redaction, tagged PDF, PDF/A and PDF/UA.
- [tooling](references/tooling.md) - corrected pypdf/pypdfium2/pdfplumber/qpdf/ReportLab examples and compatibility notes.
- `scripts/pdf_inspect.py` - metadata/structure inspection.
- `scripts/pdf_extract.py` - text/words/chars/tables/images/attachments/annotations/forms extraction.
- `scripts/pdf_edit.py` - merge/split/select/rotate/crop/watermark/paginate/encrypt/decrypt/repair/optimize.
- `scripts/ocr_pdf.py` - preservation-aware OCR with OCRmyPDF primary path and explicit Tesseract fallback.
- `scripts/pdf_redact.py` - true text/box redaction via PyMuPDF.
- `scripts/inspect_capabilities.py` - deterministic runtime capability inventory.
- `scripts/pdf_preflight.py` - PDF structure/risk preflight when `pypdf` is available.
- `scripts/render_pdf.py` - renderer abstraction using pypdfium2 or pdftoppm.
- `scripts/compare_renders.py` - render-and-pixel-compare helper.
- `scripts/validate_docs.py` - package documentation/link regression checks.
- `scripts/validate_capability_coverage.py` - rejects advertised operations without a helper or canonical example.

## Output contract

Report what was produced, the exact output file(s), and the validation actually executed. State material preservation trade-offs or unverified properties. For extraction, keep page provenance when useful. For edits, preserve page count/order and unrelated features unless the request changes them. For forms/redaction/OCR/conformance, state the specific branch and verification performed.

## Stop conditions

Stop or return a bounded partial result rather than guessing when: the source file is missing/corrupt beyond available repair; a required password or permission is unavailable; a signature/XFA preservation requirement conflicts with the available mutation tools; true redaction cannot be verified; required rendering/validation cannot run for a high-risk change; or the user asks for a conformance/accessibility claim that available evidence cannot establish.

## Authoring choice

When the requested deliverable is a new text-heavy business document, a DOCX-first workflow converted to PDF may be more maintainable. For slide-like fixed layouts, a PPTX-first workflow may be better. Use direct PDF generation when fixed-position drawing, forms, stamping, or programmatic PDF output is the actual requirement. Regardless of authoring route, validate the final PDF itself.
