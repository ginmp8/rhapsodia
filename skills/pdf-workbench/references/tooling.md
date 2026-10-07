# PDF Tooling Reference

## At a glance

- **Purpose:** Provide lower-level implementation examples for common PDF libraries/CLIs when the bundled executable toolkit is unavailable or insufficient.
- **Load when:** `references/executable-toolkit.md` cannot express the needed variant, a dependency/helper is unavailable, or lower-level diagnosis/customization is required.
- **Decision impact:** Selects an available implementation and avoids stale commands/APIs known to fail.

## Contents

- pypdf
- pdfplumber
- pypdfium2
- qpdf and Poppler
- ReportLab
- JavaScript

## pypdf

Use for object-preserving page operations and basic metadata/forms when available.

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("input.pdf")
writer = PdfWriter()
for page in reader.pages:
    writer.add_page(page)
with open("copy.pdf", "wb") as f:
    writer.write(f)
```

For encrypted/signed/XFA documents, preflight before writing. A successful `PdfWriter.write()` does not prove preservation of all interactive or signature behavior.

## pdfplumber

Use when text coordinates or table geometry are needed:

```python
import pdfplumber

with pdfplumber.open("input.pdf") as pdf:
    for page in pdf.pages:
        print(page.extract_text())
        for table in page.extract_tables():
            print(table)
```

Table extraction is heuristic. Validate multi-line cells, repeated headers and page-spanning tables against the rendered page.

## pypdfium2

Use PDFium rendering for portable visual verification when the module is available:

```python
import pypdfium2 as pdfium

pdf = pdfium.PdfDocument("input.pdf")
page = pdf[0]
image = page.render(scale=2).to_pil()
image.save("page-1.png")

textpage = page.get_textpage()
text = textpage.get_text_range()
print(text)
```

`PdfPage` text extraction goes through a text-page object; do not assume a generic page-level `get_text()` method exists.

## qpdf and Poppler

Use qpdf for structural inspection/page manipulation and Poppler utilities for text/render/image extraction when installed.

```text
qpdf --check input.pdf
qpdf --empty --pages a.pdf b.pdf -- merged.pdf
qpdf input.pdf --pages . 1-5 -- selected.pdf
qpdf --linearize input.pdf output.pdf
qpdf --optimize-images input.pdf optimized.pdf
pdftotext -layout input.pdf output.txt
pdftoppm -png -r 200 input.pdf page
pdfimages -all input.pdf images/img
```

For QDF editing, `fix-qdf` is a separate program:

```text
qpdf --qdf input.pdf editable.pdf
fix-qdf editable.pdf repaired-qdf.pdf
qpdf repaired-qdf.pdf output.pdf
```

For decryption passwords, prefer a password file rather than embedding the secret in history/logs:

```text
qpdf --password-file=password.txt --decrypt input.pdf output.pdf
```

Do not disable qpdf's conservative parser/resource limits merely to force a damaged or suspicious document through processing.

## ReportLab

Use for direct programmatic creation or stamping. For flowing rich business documents, consider authoring in DOCX/PPTX/HTML/LaTeX first and validating the exported PDF.

With `Paragraph`, prefer markup for sub/superscripts when built-in fonts may lack Unicode glyphs:

```python
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph

style = getSampleStyleSheet()["BodyText"]
water = Paragraph("H<sub>2</sub>O", style)
area = Paragraph("x<super>2</super>", style)
```

Embed a font with the required glyph coverage for multilingual output.

## JavaScript

`pdf-lib` is useful for many creation/edit/AcroForm tasks but does not support XFA fields. Detect XFA before using a form-mutation path. PDF.js is appropriate for browser rendering/text/annotation inspection; preserve worker configuration and do not confuse rendered canvas output with object-preserving PDF editing.
