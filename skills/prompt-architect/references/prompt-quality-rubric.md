# Prompt Quality Rubric

Rubric identity: `prompt-quality-rubric/v3`.

Use for `review-only`, complex `improve`, or comparative review. The rubric makes judgments more comparable; it does not turn prompt quality into a fully objective metric.

## Critical gates

Evaluate these before dimension scores:

| Gate | Fail when |
|---|---|
| `G0 right lever` | prompt engineering is treated as the solution although the required property is controlled elsewhere and the limitation is hidden |
| `G1 objective` | the required task cannot be identified |
| `G2 design authority/conflict` | material design requirements contradict and no precedence/clarification exists |
| `G3 safety/privacy` | the prompt requires unsafe, secret-leaking, or prohibited behavior |
| `G4 output contract` | a structured downstream task has no testable output contract |
| `G5 tool/source feasibility` | required tools/sources are unavailable with no fallback/stop rule |
| `G6 validation honesty` | the prompt requires or claims evidence that cannot actually be produced |
| `G7 authority/trust` | untrusted data can become runtime instruction authority without an explicit trusted contract |
| `G8 enforcement` | authorization/security/side-effect/runtime guarantees rely only on prompt prose when stronger enforcement is required |
| `G9 execution compatibility` | the rendered prompt depends on material executor/host/model capabilities that are unavailable or unknown with no fallback |
| `G10 evaluator integrity` | a strong comparison depends on changed/contaminated evaluator evidence or material judge bias is ignored |
| `G11 execution drift` | behavioral/runtime evidence is reused after material execution-profile drift without revalidation or claim downgrade |

Any unresolved critical gate means the review verdict cannot be `pass`/`approve` regardless of average dimension scores.

## Dimensions

Score each dimension only when requested or useful. Use integers 1-5 and cite prompt evidence.

| Dimension | 1 | 3 | 5 |
|---|---|---|---|
| objective/right lever | wrong problem/control layer | usable but lever assumptions remain | criterion and controlling layer are explicit |
| context | essential facts/context policy missing | usable with assumptions | stable/dynamic/untrusted context and fallbacks explicit |
| specificity | critical behavior implied | mixed concrete/vague | critical behavior actionable and bounded |
| structure | execution order confusing | usable but uneven | order supports execution with low ambiguity |
| authority/trust | authority and data trust conflated | partially separated | design authority, runtime authority, and trust are distinct |
| tool/source behavior | missing/unsafe triggers | partial rules | triggers, limits, fallback, evidence rules explicit |
| enforcement | prompt text claims guarantees it cannot enforce | mixed/implicit enforcement | each material requirement uses the lowest reliable control layer |
| output contract | absent | partly testable | syntax/sections/error behavior testable |
| examples/strategies | misleading or universalized | useful but incomplete | representative and profile-appropriate |
| safety/privacy | unsafe or secret-leaking | basic safeguards | prompt/runtime boundaries and trust controls explicit |
| validation readiness | success cannot be observed | some observable criteria | frozen criteria/profile make pass/fail reviewable |
| efficiency | large redundancy obscures rules | moderate redundancy | concise without semantic loss |
| portability | host-private behavior leaks into core | some adapter separation | semantic core and host/model profile are cleanly separated |

## Tie-breakers

When two scores are plausible:

1. prefer the lower score if a required behavior depends on unstated inference;
2. prefer the lower score if evidence is missing for the higher anchor;
3. do not penalize omitted sections that are genuinely irrelevant;
4. do not award points for verbosity by itself;
5. do not award portability for claiming support without a verified capability path.

## Severity taxonomy

- `critical`: unsafe behavior, wrong task/control layer, irreconcilable contradiction, impossible required output, prompt-only security guarantee, or dishonest validation claim;
- `major`: likely repeated misexecution, tool misuse, scope drift, execution-profile mismatch, context/trust failure, or output incompatibility;
- `moderate`: meaningful ambiguity/inconsistency with bounded impact;
- `minor`: localized clarity or efficiency issue without material behavior risk.

## Verdicts

- `pass`: no critical/major blocking defect and declared critical gates pass;
- `pass-with-reservations`: no critical defect, but one or more material issues remain bounded and disclosed;
- `fail`: at least one unresolved critical gate or material behavior contradiction;
- `blocked`: target/evidence/authority/execution profile is insufficient to complete a trustworthy review.

Do not calculate or report an overall numeric score unless the user explicitly requests it. If requested, report dimension scores separately and describe any aggregation rule rather than inventing hidden weights.

## Finding schema

Use:

`id -> severity -> subject/location -> observation -> evidence -> impact -> remediation -> validation`

Distinguish observation from inference. A recommendation is not evidence.
