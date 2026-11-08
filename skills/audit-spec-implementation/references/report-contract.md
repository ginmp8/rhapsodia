# Spec audit report contract

## Human-readable Markdown report

Use this sequence, omitting only sections that are genuinely inapplicable:

1. **Verdict**: `COMPLIANT`, `PARTIALLY_COMPLIANT`, `NON_COMPLIANT`, or `INCONCLUSIVE`, with the word **scoped** if only part of the source/feature was inspected. Give one concise reason.
2. **Frozen target**: repository and exact base/head SHAs; PR URL and audit time; environment; reviewed vs excluded areas; inaccessible documents, links and revised specs.
3. **Specification inventory**: each source URL/path/version/authority, expected linked issues, missing links and contradictions. Document incomplete GitHub Development metadata separately if not accessible.
4. **Traceability matrix**:

   | ID | Criterion and source | Code/behavior evidence at SHA | Verification evidence | Status | Finding |
   |---|---|---|---|---|---|
   | REQ-001 | Issue #12, AC-1 | `api/Handler.cs:45-70` | `auth_tests` run at SHA... | PASS | - |
   | REQ-002 | Issue #12, AC-2 | `worker/Consumer.cs:10-50` | No retry-specific proof | UNVERIFIED | F-002 |

5. **Coverage**: number of confirmed applicable requirements and counts for PASS/PARTIAL/FAIL/UNVERIFIED. Include excluded NOT_APPLICABLE with reasons. Compute completeness as `PASS/applicable`; compute proof coverage separately as cases with adequate proof; if there are unidentified or inaccessible specs, say known-scope only rather than implying full coverage.
6. **Findings ordered by severity**: finding ID, severity, requirement, expected/actual, source and code locations, reproducible failure mechanism, remediation and independent acceptance check.
7. **Missing proofs and regression risk**: cases needing tests, observed vs only authored tests, unexecuted commands, environment blockers.
8. **Decision conditions**: minimal evidence or fixes needed to make a new verdict possible, without silently starting implementation.

A report with `scope.partial=true` cannot claim the global `COMPLIANT` verdict; use a scoped lower-confidence verdict, even when all inspected requirements passed.

Never synthesize line anchors, fake run results or claim that passing CI validates the whole feature. For missing evidence prefer `UNVERIFIED` with next proof.

## Optional machine-readable JSON (`spec-audit/v1`)

Use this small contract for reusable audit receipts. Create it only when asked for JSON or when persistent, diffable evidence will materially help. The included validator checks structure and simple consistency rules, not whether source claims are true.

```json
{
  "schema_version": "spec-audit/v1",
  "scope": {
    "repository": "owner/repo",
    "target": "PR #42",
    "base_sha": "abc123",
    "head_sha": "def456",
    "snapshot_time_utc": "2026-10-27T08:00:00Z",
    "partial": false
  },
  "sources": [
    {"locator": "https://github.com/owner/repo/issues/20", "available": true, "revision": "retrieved 2026-10-27"}
  ],
  "requirements": [
    {
      "id": "REQ-001",
      "criterion": "Unauthorized sessions cannot change state through the API.",
      "source_locator": "issue #20, acceptance criterion 1",
      "status": "PASS",
      "implementation_evidence": [
        {"locator": "owner/repo@def456:api/Route.cs#L10-L50", "claim": "Route checks session permission before mutation."}
      ],
      "proof": [
        {"kind": "executed_test", "locator": "test command, result and commit SHA", "result": "passed"}
      ],
      "explanation": "Observed unauthorized request rejected without side effects.",
      "finding_ids": []
    }
  ],
  "findings": [],
  "verdict": "COMPLIANT",
  "limitations": []
}
```

`requirements[].status`: `PASS`, `PARTIAL`, `FAIL`, `UNVERIFIED`, `NOT_APPLICABLE`.
`proof[].kind`: `executed_test`, `runtime_observation`, `static_proof`, `test_defined`.
`proof[].result`: `passed`, `failed`, `not_run`, `inconclusive`. A `PASS` requires cited implementation evidence and at least one proof item of kind `executed_test`, `runtime_observation`, or `static_proof` with `passed`. `test_defined` alone is insufficient. `NOT_APPLICABLE` requires `explanation` explicitly justifying exclusion. `PARTIAL`, `FAIL`, and `UNVERIFIED` require a nonempty explanation. `PARTIAL` and `FAIL` should have finding IDs. `sources[].available=false` prevents a global `COMPLIANT` verdict. A high/critical unresolved finding also blocks `COMPLIANT`.

Use `python scripts/validate_report.py report.json` when script execution is available; it reports derived counts for confirmed requirements. Requirements inferred during risk review should be kept outside `requirements[]`, in findings/notes labeled as inferences, until normatively confirmed. Avoid publishing reports containing private code paths or secrets to unauthorized destinations.
