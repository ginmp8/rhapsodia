# Prompt Quality Rubric

Rubric identity: `prompt-quality-rubric/v2`.

Use for `review-only`, complex `improve`, or comparative review. The rubric makes judgments more comparable; it does not turn prompt quality into a fully objective metric.

## Critical gates

Evaluate these before dimension scores:

| Gate | Fail when |
|---|---|
| `G1 objective` | the required task cannot be identified |
| `G2 authority/conflict` | material requirements contradict and no precedence/clarification exists |
| `G3 safety/privacy` | the prompt requires unsafe, secret-leaking, or prohibited behavior |
| `G4 output contract` | a structured downstream task has no testable output contract |
| `G5 tool/source feasibility` | required tools/sources are unavailable with no fallback/stop rule |
| `G6 validation honesty` | the prompt requires or claims evidence that cannot actually be produced |

Any unresolved critical gate means the review verdict cannot be `pass`/`approve` regardless of average dimension scores.

## Dimensions

Score each dimension only when requested or useful. Use integers 1-5 and cite prompt evidence.

| Dimension | 1 | 3 | 5 |
|---|---|---|---|
| objective | vague/decorative | understandable but broad | concrete, scoped, testable task |
| context | essential facts missing | usable with assumptions | required facts/assumptions explicit |
| specificity | critical behavior implied | mixed concrete/vague | critical behavior actionable and bounded |
| structure | execution order confusing | usable but uneven | order supports execution with low ambiguity |
| authority/conflicts | conflicts hidden | some precedence implied | authority, exceptions, and tie-breakers explicit |
| tool/source behavior | missing/unsafe triggers | partial rules | triggers, limits, fallback, evidence rules explicit |
| output contract | absent | partly testable | syntax/sections/error behavior testable |
| examples | misleading or harmful | useful but incomplete | representative, consistent, safe for user-supplied variables |
| safety/privacy | unsafe or secret-leaking | basic safeguards | relevant safety/privacy boundaries explicit |
| validation readiness | success cannot be observed | some observable criteria | frozen/defined criteria make pass/fail reviewable |
| efficiency | large redundancy obscures rules | moderate redundancy | concise without semantic loss |

## Tie-breakers

When two scores are plausible:

1. prefer the lower score if a required behavior depends on unstated inference;
2. prefer the lower score if evidence is missing for the higher anchor;
3. do not penalize omitted sections that are genuinely irrelevant;
4. do not award points for verbosity by itself.

## Severity taxonomy

Each finding uses one severity:

- `critical`: unsafe behavior, wrong task, irreconcilable contradiction, impossible required output, or dishonest validation claim;
- `major`: likely repeated misexecution, tool misuse, scope drift, or output incompatibility;
- `moderate`: meaningful ambiguity/inconsistency with bounded impact;
- `minor`: localized clarity or efficiency issue without material behavior risk.

## Verdicts

Use these verdicts in reviews:

- `pass`: no critical/major blocking defect and declared critical gates pass;
- `pass-with-reservations`: no critical defect, but one or more material moderate/major issues remain bounded and disclosed;
- `fail`: at least one unresolved critical gate or material behavior contradiction;
- `blocked`: target/evidence/authority is insufficient to complete a trustworthy review.

Do not calculate or report an overall numeric score unless the user explicitly requests it. If requested, report dimension scores separately and describe any aggregation rule rather than inventing hidden weights.

## Finding schema

Use:

`id -> severity -> subject/location -> observation -> evidence -> impact -> remediation -> validation`

Distinguish observation from inference. A recommendation is not evidence.
