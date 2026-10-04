# Evidence and Confidence

## Evidence discipline

Treat evidence as caller/workflow-owned facts, observations, rules, or retrieved sources with stable ids when downstream automation needs traceability. Do not invent an evidence id for an unsupported claim.

Useful evidence classes include:

- direct authoritative source;
- direct observed/tool/file result;
- explicit caller/user constraint;
- deterministic rule result;
- supporting inference;
- conflicting evidence;
- missing required evidence.

The output `evidence_refs` should point to evidence ids known by the caller/workflow. If no ids exist, use an empty list and make the limitation visible in rationale/status rather than fabricating identifiers. Rich provenance may live in a caller-owned evidence registry; keep only stable refs in the decision envelope.

## Evidence acquisition stop rule

Before acquiring more evidence, ask:

1. Can the missing evidence plausibly change the decision, status, or decided-result confidence?
2. Is acquiring it proportionate to materiality, latency, cost, and authorization?

Acquire more evidence only when both answers are yes. If either answer is no, stop. This is a bounded operational rule, not a formal value-of-information calculation.

## Qualitative confidence

Confidence exists only for `status=decided`:

- `high`: criteria are well-defined and direct evidence materially converges; no unresolved conflict is outcome-changing.
- `medium`: evidence is adequate to decide but some uncertainty, indirect evidence, or plausible alternative remains.
- `low`: evidence is sparse or materially indirect, but still adequate for the declared low/medium consequence contract.

A high-materiality decided result cannot use low confidence. If high materiality lacks adequate direct evidence or has outcome-changing authoritative conflict, prefer `undetermined` or `escalate`.

For `undetermined`, `blocked`, or `escalate`, emit `confidence: null`. Do not assign a confidence level to a decision that was intentionally not made.

Confidence describes support for this decision under the declared contract. It is not a calibrated probability of real-world correctness.

## Numeric probability

Default:

```json
{"kind":"none"}
```

Permit:

```json
{
  "kind": "calibrated_probability",
  "value": 0.87,
  "source": "named calibrated model or evaluator",
  "calibration_ref": "versioned calibration/evaluation reference"
}
```

Only when all are true:

1. the numeric value comes from a calibrated external source rather than free-form self-estimation;
2. the source is identified;
3. a calibration/evaluation reference is identified;
4. the probability applies to the declared event/decision meaning;
5. the result status is `decided`.

If the caller asks for a numeric probability without these conditions, keep `kind=none` and state that calibrated probability is unavailable. Never manufacture a probability merely because a model can emit a number.

## Selective outcomes and escalation

A non-decided result can be correct behavior. Use:

- `undetermined` when evidence/criteria/options are insufficient or outcome-changing conflict remains;
- `blocked` when a required capability, authorization, source, or policy prevents the decision;
- `escalate` when a stronger evaluator/process is required or available and the current process is not sufficient.

Use `escalate` particularly when:

- high consequence plus insufficient evidence where a stronger decision process is available;
- conflicting authoritative evidence requires adjudication;
- policy requires human/specialist/independent review;
- the current model/tool is not authorized or capable enough;
- the caller explicitly requires independent review for subjective or contested judgment.

Do not escalate merely because materiality is high if the declared policy and evidence support a trustworthy bounded decision.
