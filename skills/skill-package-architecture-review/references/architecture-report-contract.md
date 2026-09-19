# Architecture Review Report Contract

**Schema version:** 1.0.0  
**Rubric version:** 2.0.0

Use this contract for durable `review-report` output and whenever reports from repeated reviews must be comparable.

## Canonical logical fields

A report contains:

1. `schema_version`
2. `rubric_version`
3. `target`
   - `name`
   - `package_identity_sha256`
4. `mode`
5. `evidence_snapshot`
   - `identity`
   - `source`
6. `observations[]`
   - `id`
   - `kind`: `mechanical | declared-contract | behavioral | supplied | derived`
   - `claim`
   - `evidence[]`
7. `judgments[]`
   - `id`
   - `claim`
   - `evidence_ids[]` referencing observations
   - `confidence`: `low | medium | high`
8. `decision`
   - `choice`: `keep_unified | split | extract_mode | create_router | merge_resources | no_change`
   - `evidence_ids[]`
   - `alternatives_considered[]`
   - `tie_breaker_used`
9. `recommendations[]`
10. `measured`
    - `commands[]`
    - `behavioral_scenarios_executed`
11. `residual_risks[]`

The Markdown template renders the same logical fields for humans. The JSON form is the canonical mechanically validated companion when machine-readable output is requested.

## Identity rules

- `target.package_identity_sha256` identifies the exact reviewed package bytes from inventory schema 2.0.0.
- `evidence_snapshot.identity` identifies the evidence bundle/report input used for the review.
- Do not compare two reports as "same package" when target identities differ.
- If exact identity could not be measured, do not emit a fabricated hash; use prose output and mark identity `not-measured` instead of claiming schema-valid JSON.

## Observation and judgment rules

- Observations state facts/evidence without architectural conclusion.
- Judgments reference observation IDs.
- Decisions reference the observations/judgments that justify them.
- Recommendations reference evidence and specify validation gates.

## Measured claims

`behavioral_scenarios_executed: true` is allowed only when scenarios were actually run in the current evidence set. Presence of `evals/architecture-review-scenarios.json` alone means planned coverage, not measured behavior.

## Validation

Validate JSON reports with:

```text
<PYTHON> scripts/validate_architecture_report.py <REPORT.json>
```

A passing schema does not prove the architectural judgment is correct; it proves the report is structurally traceable and identity-bound.
