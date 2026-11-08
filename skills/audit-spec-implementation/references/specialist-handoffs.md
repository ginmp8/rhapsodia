# Stage handoff and evidence reconciliation

## At a Glance

**Purpose:** Preserve frozen requirement, source, candidate, specialist and proof identities through external delegation or local fallback.
**Load when:** Coordinating two or more audit stages, validating their receipts, or reconciling contradictory observations.
**Decision impact:** An unavailable specialist, stale SHA, changed spec or unexecuted test must remain a gap rather than becoming `PASS` or an independent review claim.

## Shared contract

Every stage takes and returns `repository`, `base_sha`, `head_sha`, `source_snapshot`, requested scope and unchanged `REQ-###` IDs. `source_snapshot` identifies issue/document version or retrieval provenance; distinguish later edits from original normative requirements. A changed target or source invalidates affected stage evidence and any dependent verdict.

## Stage ownership and handoffs

| Stage | Owner | Receipt content |
|---|---|---|
| `criteria` (`spec-criteria-extractor`) | Normative source authority | Sources, atomic `REQ-###`, conflicts, exclusions, inaccessible history |
| `implementation` (`implementation-reachability-auditor`) | Code reachability | Entrypoint, guards, effects, writers, config and SHA-linked evidence |
| `causal` (`causal-behavior-auditor`) | Counterpaths | Guards, state transitions, bypasses, races and bounded alternatives |
| `verification` (`verification-oracle-auditor`) | Proof strength | Observable fault signal, test sensitivity, executed-vs-defined status |
| `parity` (`regression-parity-auditor`) | Differential behavior | Frozen original/candidate, intended deviations and scoped differences |

The coordinator owns compliance verdicts and findings. Specialists own evidence candidates only; neither self-declared verdicts nor tool-generated claims are authoritative without reconciliation.

## Optional machine-readable stage receipt: `audit-stage/v1`

Minimal example (do not report an unexecuted stage as completed):

```json
{
  "schema_version": "audit-stage/v1",
  "stage": "criteria",
  "status": "completed",
  "identity": {"base_sha":"1111111", "head_sha":"2222222", "source_snapshot":"issue#2@2026-10-27"},
  "delegate": {"mode":"local-adapter", "skill":"spec-criteria-extractor", "invoked":true, "invocation_evidence":"read and applied the local adapter at 2222222"},
  "requirement_ids": ["REQ-001"],
  "evidence": [{"requirement_id":"REQ-001", "kind":"source", "locator":"issue#2 AC1", "candidate_sha":"2222222", "result":"not_run"}],
  "limitations": []
}
```

The receipt validator checks types, immutable SHA consistency, requirement IDs, and provenance of claimed execution; it cannot prove a human/model really invoked a skill or that cited code is correct. Run:

```text
python scripts/validate_stage_receipt.py stage.json --expected-head HEAD_SHA --expected-source SOURCE_REV
```

For `executed_test` or `runtime_observation` with `passed`/`failed`, include `command`, `environment`, and `observed_at`; `test_defined` cannot mean `passed`. `not-run`/`skipped` cannot claim actual invocation. If host-supplied invocation evidence is unavailable, state `not-run`, or distinguish an ordinary single-agent stage from an independently verified specialist run.

## Reconciliation rules

1. Original normative source decides what must happen, within a declared version and authority hierarchy.
2. Frozen reachable source establishes what code is wired; code existence does not establish runtime outcomes.
3. Observed test/trace at an exact SHA establishes a bounded behavior under the recorded environment and inputs.
4. Unknown paths, mock-only proofs, inferred bugs, stale CI, source drift and missing history remain separate from confirmed violations.
5. Any disagreement affecting `PASS` triggers a discriminating source/test check or a lower-confidence result. An independent reviewer has a separate context only when the host actually provides one.

Final machine-readable output remains **unchanged**: `spec-audit/v1`. `audit-stage/v1` is optional and must not break clients that only consume the previous final report.
