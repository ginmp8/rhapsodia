# Review Rubric

Score each category from 0 to 2.

| Category | 0 | 1 | 2 |
|---|---|---|---|
| Objective | missing | partly clear | explicit and testable |
| Layer choice | confused | workable | transport, prompt, schema, and tool layers separated |
| Field design | ambiguous | mostly clear | typed, descriptive, minimal |
| Output contract | absent | illustrative | enforceable and provider-aware |
| Failure behavior | absent | partial | explicit missing, invalid, refusal, and truncation behavior |
| Security | unsafe | warnings only | trust, validation, authority, and secrets handled |
| Maintainability | duplicated | moderate | versioned, single source of truth, low redundancy |
| Validation | none | planned | representative checks executed |

## Verdict

- `approve`: no high-severity defects and total score at least 14;
- `approve_with_reservations`: no critical defect and total score 9 to 13;
- `reject`: critical defect, unsafe authority design, or total score below 9.

## Severity

- `critical`: credentials exposed, unauthorized operation possible, or destructive execution directly controlled by unvalidated model output;
- `high`: output contract cannot be consumed reliably, workflow can invoke unknown privileged operations, or core instructions conflict;
- `medium`: ambiguous fields, incomplete failure behavior, provider mismatch, or avoidable duplication;
- `low`: naming, minor nesting, documentation, or token-efficiency issue without material behavior impact.

Do not present a score as measured reliability. It is a static design review score.
