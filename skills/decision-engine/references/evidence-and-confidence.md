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

The output `evidence_refs` should point to evidence ids known by the caller/workflow. If no ids exist, use an empty list and make the limitation visible in rationale/status rather than fabricating identifiers.

## Qualitative confidence

Default confidence is qualitative:

- `high`: criteria are well-defined and direct evidence materially converges; no unresolved conflict is outcome-changing.
- `medium`: evidence is adequate to decide but some uncertainty, indirect evidence, or plausible alternative remains.
- `low`: evidence is sparse, materially indirect, or conflicting. Low confidence is incompatible with a high-materiality `decided` result.

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
4. the probability applies to the declared event/decision meaning.

If the caller asks for a numeric probability without these conditions, keep `kind=none` and state that calibrated probability is unavailable. Never manufacture `0.93` merely because a model can emit a number.

## Escalation

Use `escalate` when one of these is true:

- high consequence plus insufficient/medium confidence where a stronger decision process is available;
- conflicting authoritative evidence;
- policy requires human/specialist review;
- current model/tool is not authorized or capable enough;
- the caller explicitly requires independent review for subjective or contested judgment.
