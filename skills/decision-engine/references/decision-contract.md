# Decision Contract

## Canonical types

### Noul

Use for one binary proposition.

Required input: a proposition that can be evaluated as true/false under declared criteria.

When `status=decided`, `decision.value` is `true` or `false`. Otherwise it is `null`.

### Choice

Use for one selection among explicit alternatives.

Required input: at least two distinct options. Never invent an option merely to avoid `undetermined`.

When `status=decided`, `decision.selected` must exactly equal one supplied option. Otherwise it is `null`.

### Score

Use for a bounded ordinal or numeric judgment.

Required input: numeric `min`, numeric `max` with `min < max`, and a scale meaning. Prefer integer scales when the rubric is ordinal.

When `status=decided`, `decision.score` must lie within the declared inclusive bounds. Otherwise it is `null`.

## Status

- `decided`: the contract is sufficiently defined and evidence/criteria support a result.
- `undetermined`: the question is valid but evidence or criteria are insufficient/conflicting.
- `blocked`: a required capability, source, authorization, or policy prevents a trustworthy decision.
- `escalate`: the decision should move to a stronger evaluator, specialist, human, or external process.

For non-decided statuses, return the decision value as `null`.

## Materiality

Use `low`, `medium`, or `high` to express consequence, not confidence.

- `low`: reversible or low-consequence routing/preference decision.
- `medium`: meaningful operational effect but bounded recovery is available.
- `high`: safety, security, legal, financial, medical, production, irreversible, or broad-impact decision.

High materiality requires explicit evidence references when `status=decided`. Prefer `undetermined` or `escalate` when high materiality would otherwise be decided with low confidence.

## Canonical result fields

- `contract_version`: exactly `decision-engine/1`.
- `decision_id`: optional caller-supplied identifier; do not invent stable external identity.
- `materiality`: `low|medium|high`.
- `decision`: type-specific decision object.
- `confidence`: qualitative level plus concise basis.
- `evidence_refs`: ids pointing to evidence supplied/retrieved by the caller/workflow.
- `rationale`: concise visible criteria/evidence summary, not hidden chain-of-thought.
- `calibration`: `none` by default; calibrated numeric probability only under the rules below.
- `next_action`: optional continuation when status is not `decided` or when caller requests a follow-on action.

## Tie-breakers

1. Higher-priority policy/authorization constraints override convenience.
2. Direct authoritative evidence overrides weaker inferred evidence for the same fact.
3. Explicit user/caller criteria override unstated generic preferences when policy permits.
4. If valid alternatives remain materially tied, prefer `undetermined` over a fabricated winner unless a caller-supplied deterministic tie-breaker exists.
5. Do not use confidence as a substitute for missing evidence.
