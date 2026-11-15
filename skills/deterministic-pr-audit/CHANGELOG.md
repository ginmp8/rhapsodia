# Changelog

## [0.4.0] - 2026-11-15

### Code-delivery grading independent of CI

- Add an explicit frozen per-criterion semantic source-review ledger and Git-blob/line validation.
- Compute reproducible functional completion, development progress, assessment coverage and issue-wide bounds without using CI status or test outcomes.
- Keep the prior verified-check evidence floor separate for optional targeted tests; include both channels in the deterministic audit ZIP.
- Provide CLI generation, scoring and verification for code-based reviews, GitHub-connector source snapshot support, and 13 offline regressions.
- Model-authored semantic classification is not automatically deterministic: only the frozen adjudication plus source and algorithm has reproducible grades.

## [0.3.1] - 2026-11-15

### Packaging compatibility

- Remove optional SVG icon and icon references to avoid image processing during ChatGPT skill import.
- Preserve audit behavior, scripts, requirements and tests from v0.3.0.
- Validate the single-root ZIP with no SVG/images, unsupported entry types or unresolved references.

## [0.3.0] - 2026-11-15

### Added

- The default one-shot `scripts/audit_bundle.py` writes a deterministic, SHA-pinned report and ZIP even without Git or test receipts.
- Archive includes frozen JSON inputs, criterion-level Markdown, evidence, file SHA-256 manifest, and honest capture limitations.
- Offline and no-checkout regressions validate output existence, N/A semantics, ZIP integrity, byte-identical replay and malformed input rejection.

### Changed

- A missing checkout must never silently prevent artifact production when PR/issue identity was captured.
- Numerical claims still require complete reviewed checks and observed evidence; empty plans yield `NOT_ASSESSED`, not 0% implementation.
- Keeps RhapsodIA release version 0.18.0 independent from the skill's minor-version increment.

## [0.2.0] - 2026-11-14

- Distinguish `NOT_ASSESSED` from zero verified evidence; require meaningful frozen checks and report parent REQ/AC groups separately.
- Add preflight and refuse unassessed comparisons; support qualitative connector-based source inspection.

## [0.1.0] - 2026-11-14

- Initial SHA-pinned PR/issue capture, deterministic score report and CLI.
