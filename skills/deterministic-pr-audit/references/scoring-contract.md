# Frozen Scoring Contract (v1.1.0)

## Scope and identity

Input identity consists of SHA-256 of canonical UTF-8 JSON for the source, extracted requirements, check plan, and evidence. Captured PR metadata includes full head/base SHAs. Requirements and plan hashes must match across evaluated PRs before a comparison is valid. Canonical JSON uses sorted keys, two-space indentation and a terminal newline; no evaluation timestamps or stochastic inputs are introduced by `score`.

The extractor deliberately reads only explicit `REQ-NN` / `AC-NN` lines or Markdown checkboxes beneath an acceptance-criteria heading. Checkboxes checked in GitHub **do not imply PASS**. Informal paragraphs may contain additional obligations; adding explicit acceptance criteria to the original issue or a supplemental authoritative spec is the supported remediation. Content of the issue and all captured comments is frozen even when it does not yield criteria. An offline `--from-json` capture is tagged as *not completeness-verified* because it may be a curated excerpt; only a live `gh api` capture verifies pagination/completeness at capture time.

## Mandatory input-readiness gate

`preflight` requires (a) a nonempty evidence plan, (b) checks for all applicable criteria, and (c) at least one evidence source: the exact-SHA Git repository and/or pinned test execution receipts. An incomplete plan may be explicitly inspected with `--allow-partial`, but that diagnostic cannot be presented as full issue closure. Even when `score` is called without preflight, a partially mapped plan has a `null` evidence floor. `preflight` does not attest to the quality of chosen assertions: independently review check-to-criterion correspondence. If a Git checkout cannot be obtained, use the GitHub connector to inspect code/tests/CI for a qualitative source-backed report, never to manufacture test receipts or a numerical functional-progress estimate.

## Status reducer

For one atomic criterion with ordered, declared checks:

| Observations | Status |
|---|---|
| Explicit excluded + justified | NOT_APPLICABLE |
| Zero checks, or all NOT_RUN | UNVERIFIED |
| FAIL present and any PASS present | PARTIAL |
| FAIL present and zero PASS | FAIL |
| NOT_RUN present and some PASS | PARTIAL |
| All PASS and proof_policy=static | PASS |
| All PASS and proof_policy=runtime with at least one passing test check | PASS |
| All PASS but runtime policy without passing test | PARTIAL |

A text presence check means a literal exists at the pinned commit, not that behavior works. A test receipt means the declared command finished with exit code 0 in the checkout with that HEAD; a superficial or poorly constructed test cannot establish functional correctness. The quality/independence of each test must be reviewed outside of this numerical reducer. The reducer does not read or trust the PR's checkboxes.

## Metrics

- `completion_verified_pct` = 100 × PASS weight / applicable weight **only when the check plan covers all applicable criteria and at least one criterion has a decisive `PASS` or `FAIL` outcome**; otherwise `null` / N/A. This is a verified-evidence floor, **not a functional-implementation percentage**.
- `completion_possible_upper_pct` = 100 × (PASS + PARTIAL + UNVERIFIED) weight / applicable weight if checks were evaluated; otherwise `null`. This is a mathematical upper bound, not a forecast.
- `probes_pass_pct` = 100 × passing checks / declared applicable checks; N/A if no check was evaluated.
- `requirements_mapped_pct` = 100 × criteria with checks / applicable criteria.
- `assessment_state` = `NOT_ASSESSED` (zero evaluated checks), `INCOMPLETE_PLAN` (checks not mapped to all applicable criteria), `PARTIALLY_ASSESSED` (mapped evidence but at least one `PARTIAL` or `UNVERIFIED` criterion), or `EVALUATED_KNOWN_SCOPE` (only `PASS`/`FAIL`/excluded outcomes in explicit scope). Some `PARTIALLY_ASSESSED` reports still have an N/A floor if no criterion was conclusively accepted or rejected.
- `observed_checks`, `declared_checks`, `checks_not_run`, and `requirements_with_observations` expose evidence coverage independently of numerical floor.
- `acceptance_criteria` and `parent_requirements` repeat the reducer for disjoint `AC-` and `REQ-` subsets. An issue with 40 ACs and 14 higher-level REQs has **40 acceptance outcomes**, not a meaningful 54-item functional completion rate. The overall all-explicit group is retained for audit compatibility but its ratio must not be presented as implementation progress.
- All percentages are decimal strings with 2 fractional digits, rounded half-up. N/A is represented as JSON null.

The plan allows integer weights 1..100; an unchanged weight contract is mandatory for side-by-side PR comparison. The output is based on *criteria known to the extractor* only, never a claim that all implicit issue prose was satisfied.

`score-v1.1.0` is not numerically comparable with `score-v1.0.0`: the new no-evidence N/A gate, separate AC/REQ groups and readiness metadata change the output contract. `compare` refuses legacy reports and any candidate with a `null` evidence floor, even if both have matching missing evidence. Partially assessed comparisons are labeled *evidence-floor only*.

## Reproducibility classes

1. **Pure replay** (`score` and `verify`): byte-for-byte deterministic for frozen inputs and algorithm.
2. **Static reinspection** (`inspect`, `verify-evidence`): deterministic when the pinned Git objects, plan and receipts remain identical.
3. **Fresh runtime proof** (`run-tests --execute`): externally variable; each run creates a distinct receipt. A command that now fails is not a scoring anomaly; it is a new observation.
4. **Semantic plan authoring:** judgment-dependent. Freeze checks after review and make changes explicit instead of silently revising earlier scores.

The SHA-256 values detect accidental drift; they do not authenticate evidence against malicious tampering. Local report validation is a consistency check, not an independent acceptance test or cryptographic signature.

Historical code ledgers, issue checkboxes, or green workflows are **pointers** to potential evidence; the status reducer may only consume declared check observations at the frozen HEAD. A CI job proving a matrix dispatches reviewers does not prove it also completed all parent/child rounds, aggregated receipts and issued exactly one final callback. Missing such test coverage remains unresolved rather than being converted into `PASS`.
