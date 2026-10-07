# PDF Operations

## At a glance

- **Purpose:** Route ordinary PDF reading, extraction, editing, creation and conversion to the narrowest suitable operation while preserving unrelated document behavior.
- **Load when:** The request is not primarily forms, OCR, redaction, signatures, XFA, or standards conformance.
- **Decision impact:** Chooses structure-first extraction, mutation safeguards, rendering requirements and authoring route.

## Contents

- Executable-first rule
- Read and review
- Extract text and tables
- Extract images and attachments
- Edit existing PDFs
- Create PDFs
- Convert to PDF
- Validation matrix

## Executable-first rule

For recurring operations, use `references/executable-toolkit.md` and the bundled helpers before generating equivalent code from scratch. Load `references/tooling.md` only for a specialized variant, missing dependency fallback, or debugging. The machine-readable coverage contract is `references/capability-registry.json`.

## Read and review

1. Inspect page count, encryption and document features before assuming text extraction is enough.
2. For layout-sensitive questions, render the relevant pages and treat page images as authoritative for appearance.
3. Preserve page provenance in summaries/extractions when the user may need to trace findings back to the source.
4. If the document is scanned or text extraction is empty/garbled, route to the OCR branch instead of repeatedly trying text parsers.

## Extract text and tables

Preferred order:

1. Tagged/structured semantics when available and the tooling exposes them.
2. Native text extraction with layout/coordinates for born-digital PDFs.
3. Table-specific extraction when ruled/column geometry is material.
4. Rendered-page analysis for visual relationships not represented in extracted text.
5. OCR only when native text/structure is absent or demonstrably unusable.

Do not concatenate multi-page tables blindly. Preserve page boundaries and repeated headers until the table structure is verified.

## Extract images and attachments

- Use embedded-image extraction when the original asset is needed; rendering the whole page is not equivalent.
- Treat embedded attachments as untrusted files. Extract only when requested or necessary, and never execute them automatically.
- Record page/object provenance when several similar images exist.

## Edit existing PDFs

For merge/split/select/rotate/crop/watermark/paginate/encrypt/repair:

1. Preflight first for signatures, encryption, forms/XFA and annotations.
2. Prefer transformations that copy existing PDF objects/pages rather than rasterizing them.
3. Write a new output by default.
4. Re-open the output and verify page count/order and the requested mutation.
5. Re-render when geometry or appearance can change.

Cropping changes visibility, not necessarily underlying content. Never treat crop as redaction.

## Create PDFs

Choose the authoring representation before coding:

- **ReportLab/direct drawing:** fixed-position programmatic PDF, stamping, simple generated reports.
- **DOCX -> PDF:** text-heavy business documents with headings, long tables, TOC or flowing prose.
- **PPTX -> PDF:** slide-like layouts, fixed compositions, charts/callouts.
- **HTML/LaTeX -> PDF:** when the available runtime already has a reliable renderer and the source format fits the content.

For ReportLab `Paragraph`, use markup such as `<sub>`/`<super>` rather than assuming built-in fonts support Unicode subscript/superscript glyphs. Embed appropriate fonts when broad Unicode coverage is required.

## Convert to PDF

Conversion success means more than “a PDF file exists.” Verify:

- page count and order;
- font/glyph rendering;
- images/charts;
- hyperlinks/bookmarks/forms when preservation is required;
- page size/orientation;
- no clipping/overflow.

If the source is already PDF, avoid a format round-trip unless it solves a specific problem; round-tripping can flatten or discard PDF-native features.

## Validation matrix

| Operation | Minimum checks |
|---|---|
| read/extract | page provenance; native-vs-OCR state understood |
| merge/split | page count/order; forms/annotations not unexpectedly lost |
| rotate/crop | target pages; final render |
| watermark/stamp | placement; opacity/readability; final render |
| encrypt/decrypt | open with intended credentials; permissions/metadata expectations |
| repair | re-open; parser warnings; page count; render representative pages |
| create/convert | open/render all pages; no clipping/broken glyphs |
