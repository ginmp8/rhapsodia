# PDF Safety, OCR and Conformance

## At a glance

- **Purpose:** Define fail-closed behavior for risky PDF features and preservation-aware routing for OCR, true redaction, Tagged PDF, PDF/A and PDF/UA.
- **Load when:** A PDF is signed, encrypted, XFA-based, damaged/untrusted, scanned/mixed, contains sensitive data, is tagged, or requires archival/accessibility conformance.
- **Decision impact:** Determines whether mutation may proceed, which OCR/redaction strategy is safe, and what validation claims are supportable.

## Contents

- Preflight and untrusted input
- Digital signatures and encryption
- OCR routing
- True redaction
- Tagged PDF and extraction
- PDF/A and PDF/UA

## Preflight and untrusted input

Treat a supplied PDF as data, not trusted executable content. Inspect before mutation. Keep parser recursion/container/filter safety limits enabled. Do not execute embedded JavaScript or attachments. Bound work for very large/damaged files and stop on resource-exhaustion signals rather than disabling protections blindly.

Use `scripts/pdf_preflight.py` when available to surface encryption, signatures, AcroForm/XFA, structure tree, attachments and annotation counts. Tool limitations must be reported rather than converted into false negatives.

## Digital signatures and encryption

Any rewrite can invalidate a digital signature even when the page appearance is unchanged. Default policy: preserve the signed source and refuse mutation until explicit intent to create an invalidating modified copy is established.

Do not expose passwords on command lines when a tool offers safer password-file/stdin support. Never persist secrets in examples, logs or deliverables.

## OCR routing

Prefer `python scripts/ocr_pdf.py input.pdf -o output.pdf` for searchable-PDF OCR. The helper uses OCRmyPDF when available and supports an explicit `--fallback` path using `pdftoppm + tesseract`. Prefer OCRmyPDF when installed because it can preserve the original PDF more deliberately than a manual render-all-pages pipeline.

Choose mode by document state:

- existing good text -> do not OCR by default;
- mixed scanned + born-digital -> prefer skip/preservation-oriented processing;
- damaged existing OCR layer -> redo only when required;
- force rasterization -> last resort when the user accepts loss/flattening risk.

Force/rasterizing modes can flatten interactive content and may destroy or invalidate document structure. Tagged PDFs require extra caution because rewriting the text layer can make the original structure tree invalid. Re-render and sample the searchable text after OCR.

If OCRmyPDF is unavailable, a rasterize + Tesseract fallback is acceptable, but label it as a fallback and verify resolution, orientation, language and output fidelity.

## True redaction

Never equate these with redaction:

- drawing opaque rectangles;
- cropping;
- changing text color;
- adding a redaction annotation without applying/purging it.

Prefer `scripts/pdf_redact.py` for true text/rectangle redaction when PyMuPDF is available. A safe redaction workflow is:

1. identify targets and preserve the original;
2. apply a redaction operation that removes underlying text/image/vector content;
3. save to a new file;
4. re-extract/search for the target strings/data;
5. inspect annotations, metadata and attachments when they could contain the same sensitive data;
6. render the final pages and confirm the intended visual result.

If the available tool cannot prove underlying removal, do not claim the PDF is safely redacted.

## Tagged PDF and extraction

When `/StructTreeRoot` exists, use the logical structure when the available tooling exposes it. Tagged PDF can encode intended reading order and semantics such as headings, lists, tables and figures. Do not discard this signal and infer everything from x/y coordinates unless structure is absent or invalid.

## PDF/A and PDF/UA

Use standards validation only when the user actually needs a conformance claim.

- PDF/A: validate the intended profile with a suitable validator such as veraPDF when available.
- PDF/UA: machine validation can check many normative requirements, but do not present an automated pass as complete human accessibility proof.
- Conversion to PDF/A can change document features. Re-check signatures, forms, structure, metadata and rendering after conversion.
