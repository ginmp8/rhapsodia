# Scanner Contract

## Purpose

`scripts/scan_secrets.py` is a deterministic supporting detector. It increases coverage for text-like files; it does not prove credential validity or replace semantic review.

## Input rules

- Accept exactly one existing file or directory target.
- Resolve the target root once.
- Do not follow symbolic-link files during directory traversal.
- Traverse directory names and file names in canonical lexical order.
- Scan supported text-like file names/extensions only.
- Skip files larger than the configured maximum and report them.
- Read UTF-8 with replacement/ignore behavior only as a best-effort text scan; unsupported/binary surfaces remain outside proof of completeness.

## JSON contract v1

Top-level fields:

- `schema_version`: `1`
- `status`: `complete | partial`
- `target`: resolved invocation target
- `summary`: severity counts
- `scan_stats`: considered/scanned/skipped/finding counts
- `skipped`: canonical list of skipped files with stable reason codes
- `findings`: canonical list of findings

Finding fields:

- `id`: stable hash derived from relative path, line, and rule
- `path`: path relative to the scan root; never an arbitrary temporary absolute path
- `line`: 1-based line number
- `severity`: `critical | high | medium | low`
- `confidence`: `confirmed | likely | possible`
- `rule`: stable detector rule ID
- `evidence`: redacted minimum evidence

## Stable skip reasons

- `symlink`
- `unsupported-type`
- `too-large`
- `read-error`

The default scanner may omit unsupported-type entries for files that were never candidates by extension; material unsupported files should be called out manually when known.

## Redaction invariant

Scanner output must not reproduce the full matched credential material. Provider tokens, bearer values, passwords in URIs, and secret assignments are masked before output. Private-key **markers** may be shown, but private-key payload material must not be copied.

## Ordering

Findings are sorted by:

`severity desc -> path -> line -> rule -> id`

Skipped entries are sorted by path then reason. Summary keys use severity order.

## Coverage

`complete` means no candidate text file was skipped after discovery. `partial` means one or more candidate files were skipped for symlink, size, or read-error reasons.

A `complete` scanner result is still only complete for the scanner's supported filesystem/text scope. It does not include unavailable Git history, remote CI logs, screenshots, external secret stores, or unsupported binary content.

## Durable output

When `--output` is used, write a temporary sibling file and atomically replace the destination only after JSON serialization succeeds. Reject a symbolic-link output path and an output that aliases the single-file input.
