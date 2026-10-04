# Review Rubric

Score each category from 0 to 2. The score is a static design aid, not measured reliability.

| Category | 0 | 1 | 2 |
|---|---|---|---|
| Objective | missing | partly clear | explicit and testable |
| Layer/authority separation | confused | workable | transport, instructions, data, canonical schema, projection, tool/runtime authority separated |
| Field design | ambiguous | mostly clear | typed, descriptive, minimal |
| Canonical contract | absent/informal | partial | dialect/version and semantics explicit |
| Provider portability | assumed | provider mentioned | current capability evidence plus loss/application-validation accounting |
| Failure behavior | absent | partial | refusal, incomplete, schema failure, tool/runtime failure distinguished |
| Security/authority | unsafe | warnings only | provenance, validation, authorization, scope, and side effects handled |
| Maintainability | duplicated | moderate | versioned single sources of truth with low redundancy |
| Validation evidence | none | planned | executed mechanics separated from semantic/runtime not-run checks |

## Verdict

- `approve`: no critical/high defect and at least 16/18.
- `approve_with_reservations`: no critical defect and at least 11/18.
- `reject`: any critical defect, unsafe authority design, or score below 11.

## Severity

- `critical`: exposed credential, unauthorized/destructive operation enabled, or model-generated data directly controls privileged execution without independent authorization.
- `high`: contract cannot be consumed reliably, provider projection silently drops required semantics, schema/tool layers are materially confused, or failure states make unsafe success interpretation possible.
- `medium`: ambiguous fields, stale/unverified provider capability, incomplete failure handling, weak portability accounting, or avoidable duplication.
- `low`: naming, documentation, minor nesting, or token-efficiency issue without material behavior impact.

## Evidence rule

A clean lint result does not prove JSON Schema conformance, semantic correctness, provider runtime support, security, or behavioral quality. Report those axes independently.
