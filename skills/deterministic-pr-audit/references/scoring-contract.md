# Frozen scoring contract

## Primary: source-code implementation grade (code-delivery-v1)

**Implementation scoring is CI-independent.** Freeze the full issue and every AC/REQ, select HEAD and code evidence, then populate `implementation-review.json` using the source paths and Git blob SHA/line ranges at that HEAD. `code-grade` validates the ledger and source anchors; the score function has no CI-status or test-exit input.

A criterion is `COMPLETE` only when every required behavior is traced as implemented/reachable through its entrypoint, guards and final effects. `PARTIAL` requires implemented code plus a concrete remaining obligation. `MISSING` requires observed counterexample code, not merely absent lexical matches. `UNVERIFIED` remains unknown, never missing. Code evidence validation proves the blob/line reference, **not the analyst's semantic conclusion**; inspect the entire relevant path before adjudicating.

For new substantive audits the [semantic adjudication protocol](adjudication.md) is mandatory; `--require-coverage` uses canonical requirement extraction and a v2 review ledger with symmetric typed obligation coverage, causal positive/negative test witnesses, pinned anchors and counterevidence reconciliation. Criterion statuses must agree with the obligation verdicts. The unchanged v1 formula and report replay remain available for legacy ledgers; `--require-adjudication` alone selects the historical penalty-only gate. Do not compare different adjudication policies or obligation scopes without re-reviewing both candidates. Different verdicts at the same HEAD and same scope are a semantic disagreement to reconcile, not code progress. PR discussion and CI never enter the formula. Distinguish actual runtime deficits from required test/document/config gaps; the composite AC score is a conformance proxy, not a measured fraction of code or effort.

One AC = one equally weighted obligation. A composite AC with several requirements is `COMPLETE` only when all required parts work; `PARTIAL` is a fixed half-credit modeling assumption, not a measured 50% of code. Never split or weight ACs differently after viewing the candidate to manipulate the note; if a spec's AC granularity is inappropriate, version an explicit subcriterion rubric before comparison and state its limitations.

For the main AC group, let `C` = COMPLETE count, `P` = PARTIAL, `M` = MISSING, `U` = UNVERIFIED and `N=C+P+M+U`. Then:

- **Functional completion (assessed scope)** = `100 × C/(C+P+M)`, or N/A if denominator zero.
- **Development progress (assessed scope)** = `100 × (C+0.5×P)/(C+P+M)`, or N/A if denominator zero.
- **Assessment coverage** = `100 × (C+P+M)/N`.
- **Issue-wide completion lower/upper** = `100×C/N` and `100×(C+U)/N`.
- **Issue-wide progress lower/upper** = `100×(C+0.5×P)/N` and `100×(C+0.5×P+U)/N`.
- **Always-numeric delivery grade** = progress lower bound, using `0.00` if no ACs exist. This is a demonstrated-evidence **floor**, NOT an estimate of the unknown work. With `C=P=M=0`, it is a diagnostic 0/100 with 0% coverage and 0–100% bounds; never claim 0% implementation.

Round half-up to two decimal places using the standard-library `Decimal` scorer. Parent `REQ` metrics use a separate denominator and **never** inflate AC progress. The report binds source, requirements, review ledger, algorithm, candidate HEAD, and optional code snapshots by digest. `capture-code-snapshots` fetches full referenced files at HEAD using GitHub Contents API and validates each blob SHA. Explicit `--allow-provisional` bypasses independent Git object verification **only** when a substantive analyst source-trace ledger exists; this must show `provisional_connector_refs_unverified` and must not be described as verified. `--require-review` rejects a diagnostic with no assessed criteria. Source snapshots without a local checkout have checked Git blob bytes but lack an independent SHA-to-tree proof; disclose as weaker provenance. An offline issue capture is not authoritative until independently verified complete.

**Determinism boundary:** the same frozen source+requirements+ledger+code snapshot+algorithm reproduces byte-identical scores; a different semantic judgment can legitimately change the score. Never claim an independently repeated free-form LLM review is deterministic without freezing the adjudications. CI failures may be noted in a separate operational section but cannot move the code-delivery percentage.

## Secondary: executable verification evidence floor (score-v1.1.0)

The original `report.json` uses `source.json`, `requirements.json`, `checks.json`, `evidence.json` and its algorithm. A requirement is `PASS` only when its reviewed checks passed and proof policy is fulfilled, `PARTIAL` when some observed checks passed but others failed/missing, `FAIL` when none passed and at least one failed, `UNVERIFIED` with no observed proof, `NOT_APPLICABLE` with a reason. Its `completion_verified_pct` is an **evidence floor**, NOT a grade of delivered code.

`preflight` requires a complete check map, pinned source and real test/static evidence before numeric verified claims. Empty plans produce `NOT_ASSESSED` / N/A, never 0% implemented. `audit_bundle.py` still always generates a ZIP. Its legacy verification evidence is not allowed into `implementation-grade.json`; a green or red generic CI workflow cannot certify the semantic delivery grade.

Both modes require exact source/evaluator identity. Comparisons should freeze the same issue and rubric; changing requirements, review judgments or scoring version creates a different evidence version. A running test only proves what its actual assertions tested. A source reference only proves what its text shows when the interpretation is valid.
