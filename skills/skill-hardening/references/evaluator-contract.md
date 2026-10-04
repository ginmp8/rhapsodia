# Evaluator Contract

## Evidence layers

Keep these independent: structural/spec/package evidence; semantic-review evidence; behavioral/scenario evidence; runtime/host evidence; perceptual/editorial evidence. A pass in one layer never upgrades another.

## Freeze before mutation

Freeze prompts, fixtures, expected outputs, grader rules, thresholds, independent validators, and package gates that will decide candidate acceptance. Keep candidate implementation/generators outside the frozen set. If a frozen evaluator is defective, invalidate the comparison, repair/refreeze separately, and restart rather than tailoring the oracle after failure.

## Required structural failures

Fail when applicable: missing/invalid root `SKILL.md`; portable-core frontmatter invalid; broken package-local references; residual scaffold markers; protected/frozen evidence changed; target-owned mandatory validation fails; requested portability profile fails; package/archive/receipt correspondence fails.

Do **not** fail merely because optional scripts, references, templates, examples, evals, host adapters, or a target-owned package builder are absent.

## Claim-sensitive evaluation

- Structural repair/readiness: deterministic spec/package/resource gates may be sufficient.
- Behavioral activation/output claim: require a frozen scenario suite with predeclared categories/thresholds.
- Ecosystem routing claim: include coexistence and semantic-collision cases.
- Strong stochastic reliability/improvement claim: repeated trials, fixed evaluator, declared budget/stop rule, uncertainty/reliability reporting, and comparable material environment identity.
- Subjective quality: independent editorial/perceptual review appropriate to the reproducibility ceiling.

## Static score

A structural maturity score is a gate/diagnostic, never behavioral proof. When it is saturated, use a non-saturated signal such as unresolved risk count, missing-reference count, unreferenced-resource count, target test pass rate, scenario failures, repair rounds, token cost, or runtime failures. Do not add machinery merely to move a score.

## Report minimums

Record target/baseline/candidate identity, evaluator identity, gate states, evidence labels (`measured`, `observed`, `derived`, `supplied`, `planned`, `blocked`), acceptance/rejection rationale, and remaining unmeasured behavior.
