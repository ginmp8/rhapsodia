# Files, Uploads, Downloads, and Media

## Upload workflow

1. Accept the file with `st.file_uploader`.
2. Validate extension, MIME hint, size, and parser compatibility.
3. Parse in memory or into a safe temporary location.
4. Display a preview and schema summary.
5. Ask for confirmation before persistence.
6. Store only what is needed.

## Parser safety

User files are untrusted. Avoid executing file contents. Treat CSV formulas, embedded HTML, huge rows, malformed encodings, and compressed archives as potential risks. For enterprise apps, scan or validate files before passing them to downstream systems.

## CSV and Excel

Handle encodings, delimiters, date parsing, decimal separators, and large files. Show inferred schema and row count before using the data for writes or model input.

## Images, audio, and video

Use native media commands for display. Keep uploaded media size limits explicit. Strip or avoid exposing metadata when privacy matters. For camera/audio input, state why capture is needed.

## Downloads

Use `st.download_button` for generated outputs. Generate deterministic filenames that include report type and date/time when useful. Do not embed secrets or raw access tokens in downloadable files.

## Temporary files

Prefer in-memory processing when possible. If temporary files are necessary, use safe temporary directories, random names, and cleanup. Never write uploaded filenames directly into filesystem paths without sanitization.

## Media UX

- Show previews before processing.
- Display parsing errors in user language.
- Provide downloadable error reports for batch validation.
- Avoid rendering extremely large files in full.
- Summarize large files before exposing detail views.
