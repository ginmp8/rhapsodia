# Frozen Scoring Contract (v1.0.0)

## Scope and identity

Input identity consists of SHA-256 of canonical UTF-8 JSON for the source, extracted requirements, check plan, and evidence. Captured PR metadata includes full head/base SHAs. Requirements and plan hashes must match across evaluated PRs before a comparison is valid. Canonical JSON uses sorted keys, two-space indentation and a terminal newline; no evaluation timestamps or stochastic inputs are introduced by `score`.

The extractor deliberately reads only explicit `REQ-NN` / `AC-NN` lines or Markdown checkboxes beneath an acceptance-criteria heading. Checkboxes checked in GitHub **do not imply PASS**. Informal paragraphs may contain additional obligations; adding explicit acceptance criteria to the original issue or a supplemental authoritative spec is the supported remediation. Content of the issue and all captured comments is frozen even when it does not yield criteria.

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

- `completion_verified_pct` = 100 × PASS weight / applicable weight.
- `completion_possible_upper_pct` = 100 × (PASS + PARTIAL + UNVERIFIED) weight / applicable weight. This is a mathematical upper bound, not a forecast.
- `probes_pass_pct` = 100 × passing checks / declared applicable checks; N/A if no checks are configured.
- `requirements_mapped_pct` = 100 × criteria with checks / applicable criteria.
- All percentages are decimal strings with 2 fractional digits, rounded half-up. N/A is represented as JSON null.

The plan allows integer weights 1..100; an unchanged weight contract is mandatory for side-by-side PR comparison. The output is based on *criteria known to the extractor* only, never a claim that all implicit issue prose was satisfied.

## Reproducibility classes

1. **Pure replay** (`score` and `verify`): byte-for-byte deterministic for frozen inputs and algorithm.
2. **Static reinspection** (`inspect`, `verify-evidence`): deterministic when the pinned Git objects, plan and receipts remain identical.
3. **Fresh runtime proof** (`run-tests --execute`): externally variable; each run creates a distinct receipt. A command that now fails is not a scoring anomaly; it is a new observation.
4. **Semantic plan authoring:** judgment-dependent. Freeze checks after review and make changes explicit instead of silently revising earlier scores.

The SHA-256 values detect accidental drift; they do not authenticate evidence against malicious tampering. Local report validation is a consistency check, not an independent acceptance test or cryptographic signature.
