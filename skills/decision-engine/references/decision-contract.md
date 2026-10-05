# Decision Contract

## At a Glance

Defines the canonical `decision-engine/2` semantics for `binary`, `choice`, and `score`; the four statuses; materiality; result fields; and deterministic tie-breakers. Preserve caller-supplied decision surfaces, use null type-specific values plus `confidence: null` for non-decided outcomes, and never force a winner when evidence or alternatives are insufficient.

## Contents

- Canonical types: Binary, Choice, Score
- Status
- Materiality
- Canonical result fields
- Decision policy and tie-breakers

## Canonical types

### Binary

Use for one proposition that can be evaluated as true/false under declared criteria.

When `status=decided`, `decision.value` is `true` or `false`. Otherwise it is `null`.

The type is named `binary`, not `noul`. `decision-engine/2` deliberately avoids using `noul` for a boolean result because that name is also used in external decision-model ecosystems for calibrated probability. See [migration-v1-to-v2.md](migration-v1-to-v2.md).

### Choice

Use for one selection among explicit alternatives.

Required inputs:

- at least two distinct options;
- `options_exhaustive: true|false`;
- optional `option_criteria` keyed only by supplied options.

Never invent an option merely to avoid `undetermined`. When the option set is not exhaustive and no supplied option fits, return `undetermined` unless the caller explicitly supplied a fallback such as `other` or `none` as a real option.

When `status=decided`, `decision.selected` must exactly equal one supplied option. Otherwise it is `null`.

### Score

Use for a bounded ordinal or numeric judgment. Declare the scale kind explicitly.

#### Ordinal

```json
{
  "kind": "ordinal",
  "levels": [
    "Cosmetic only",
    "Degraded with workaround",
    "Blocking without workaround"
  ]
}
```

The array order defines rank. A decided ordinal `score` is the zero-based integer index of one level. Do not infer equal distance between adjacent ordinal levels.

#### Numeric

```json
{
  "kind": "numeric",
  "min": 0,
  "max": 100,
  "meaning": "Percentage of the declared capacity budget",
  "unit": "percent"
}
```

`min` and `max` must be finite numbers with `min < max`; `meaning` is required; `unit` is optional. A decided numeric score is finite and inside the inclusive bounds.

For either scale kind, a non-decided result uses `score: null`.

## Status

- `decided`: the contract is sufficiently defined and evidence/criteria support a result.
- `undetermined`: the question is valid but evidence, criteria, or supplied alternatives are insufficient/conflicting.
- `blocked`: a required capability, source, authorization, or policy prevents a trustworthy decision.
- `escalate`: the decision should move to a stronger evaluator, specialist, human, or external process.

For non-decided statuses, return the type-specific decision value as `null` and root `confidence` as `null`.

## Materiality

Use `low`, `medium`, or `high` to express consequence, not confidence.

- `low`: reversible or low-consequence routing/preference decision.
- `medium`: meaningful operational effect but bounded recovery is available.
- `high`: safety, security, legal, financial, medical, production, irreversible, or broad-impact decision.

A high-materiality `decided` result requires explicit evidence references, at least medium confidence, and no unresolved outcome-changing authoritative conflict. Escalate when policy requires independent review or the available process is not strong enough. Do not impose universal human review when caller/policy does not require it.

## Canonical result fields

- `contract_version`: exactly `decision-engine/2`.
- `decision_id`: optional caller-supplied identifier; do not invent stable external identity.
- `materiality`: `low|medium|high`.
- `decision`: type-specific decision object.
- `confidence`: qualitative object only for `decided`; `null` otherwise.
- `evidence_refs`: ids pointing to caller/workflow-owned evidence.
- `rationale`: concise visible criteria/evidence summary, not hidden chain-of-thought.
- `calibration`: `none` by default; calibrated numeric probability only under the calibration rules.
- `next_action`: optional continuation; required for `blocked` and `escalate`.

## Decision policy and tie-breakers

Operational action policy is caller-owned. Do not invent thresholds, weights, utility functions, approval rules, or permissions.

Apply tie-breakers in this order:

1. higher-priority policy/authorization constraints override convenience;
2. direct authoritative evidence overrides weaker inferred evidence for the same fact;
3. explicit user/caller criteria override unstated generic preferences when policy permits;
4. caller-supplied lexicographic order, weights, or deterministic tie-breakers may be applied exactly as supplied;
5. if valid alternatives remain materially tied, prefer `undetermined` over a fabricated winner;
6. do not use confidence as a substitute for missing evidence.
