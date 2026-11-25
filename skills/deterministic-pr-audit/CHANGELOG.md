# Changelog

## [0.7.0] - 2026-11-25

### Frozen scope and same-HEAD reconciliation

- Freeze specification-only obligation descriptors and stable IDs in a separate canonical plan before code adjudication. Bind the review to that plan and retain every obligation even when UNKNOWN.
- Freeze the inventory of available prior JSON/Markdown grades; require source-anchored reconciliation of same-HEAD verdict disagreements and shared counterexample leads. Do not infer semantic contradictions from source overlap alone.
- Distinguish complete adjudication from incomplete, unreconciled and provisional evidence floors, including unknown obligations inside PARTIAL rows. Preserve diagnostic bundles and reject misleading new-policy progress comparisons.
- Preserve v1/v2 replay, original AC weights, CI independence, and all numeric formulas. This is a structural reproducibility improvement, not a guarantee of identical independent model judgments.

## [0.6.0] - 2026-11-25

### Symmetric source-backed obligation adjudication

- Add canonical explicit checkbox and heading-suffix IDs for new audits, preserving historical extraction for replay.
- Add coverage review v2 and `--require-coverage`: affirmative completion and proven gaps require typed obligation verdicts and pinned witnesses. Require both polarities for each explicitly enumerated test subject; trace actual input, reached predicate and asserted effect to avoid false credit from short circuits.
- Reject inconsistent criterion/obligation verdicts, coverage scope drift and divergent same-HEAD comparisons; preserve v1 replay, equal-weight scores and CI independence.
- Add structural/causal regression cases and CLI/bundle verification. Semantic claims remain analyst-reviewed, not automatically proven by the validator.

## [0.5.1] - 2026-11-25

### Semantic adjudication and penalty evidence

- Require new audits to reconcile the full PR discussion, normative exceptions and actual composed/parameterized test assertions against pinned code, and challenge proposed penalties before scoring.
- Add `--require-adjudication` to grade, verify and bundle commands: every PARTIAL/MISSING gap must identify its type, exact normative quote, pinned negative source anchor, observed result and contrary-evidence reconciliation. Unknowns and optional improvements cannot be treated as proven gaps.
- Separate runtime behavior deficits from mandatory test/documentation/delivery-configuration gaps. Describe the existing AC score as a conformance proxy, not measured code or effort.
- Preserve legacy v1 ledger and score replay; gated reports explicitly identify their policy and refuse cross-policy comparisons. CI remains excluded from scoring.

## [0.5.0] - 2026-11-15

### Evidence-bounded numeric grading and GitHub capture fallback

- Expose an always-numeric conservative delivery grade independently of CI, while preserving assessed-only percentages and issue-wide confidence bounds; make zero-coverage diagnostics unmistakable.
- Add an explicit `--require-review` gate so all-`UNVERIFIED` scaffolds cannot masquerade as substantive completed audits.
- Add `capture-code-snapshots` to fetch complete referenced source files directly through authenticated GitHub Contents at the pinned SHA, validating blob integrity without a local checkout.
- Permit `--allow-provisional` only for a substantive source-traced review when Git/blob verification is unavailable, with explicit unverified provenance and reproducible output.
- Cover no-code diagnostics, provisional fallback, exact-SHA fetch/mismatch/invalid data and bundle review gates in offline regression tests.

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
