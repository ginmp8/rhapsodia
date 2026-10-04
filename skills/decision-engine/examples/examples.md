# Examples

These examples calibrate shape and boundaries. They are not evidence that a host/model will produce the same answer.

## Binary

```json
{
  "contract_version": "decision-engine/2",
  "decision_id": "gate-17",
  "materiality": "medium",
  "decision": {
    "type": "binary",
    "question": "Does the candidate preserve the declared public contract?",
    "status": "decided",
    "value": true
  },
  "confidence": {
    "level": "high",
    "basis": "the frozen contract tests and direct diff evidence converge"
  },
  "evidence_refs": ["E-contract-tests", "E-diff"],
  "rationale": "No public contract regression is present in the inspected change.",
  "calibration": {"kind": "none"},
  "next_action": null
}
```

## Choice with a non-exhaustive option set

If supplied options may not cover reality and none fits, do not invent a winner:

```json
{
  "contract_version": "decision-engine/2",
  "decision_id": null,
  "materiality": "low",
  "decision": {
    "type": "choice",
    "question": "Which supplied route fits this request?",
    "status": "undetermined",
    "options": ["answer", "search"],
    "options_exhaustive": false,
    "selected": null
  },
  "confidence": null,
  "evidence_refs": [],
  "rationale": "The request fits neither supplied route and the option set is not exhaustive.",
  "calibration": {"kind": "none"},
  "next_action": null
}
```

## Ordinal score

```json
{
  "contract_version": "decision-engine/2",
  "decision_id": "risk-8",
  "materiality": "medium",
  "decision": {
    "type": "score",
    "question": "How severe is the bounded issue?",
    "status": "decided",
    "scale": {
      "kind": "ordinal",
      "levels": [
        "Cosmetic only",
        "Degraded with workaround",
        "Blocking without workaround"
      ]
    },
    "score": 1
  },
  "confidence": {
    "level": "medium",
    "basis": "observed impact is direct but one dependency remains uncertain"
  },
  "evidence_refs": ["E-observation"],
  "rationale": "The issue degrades the workflow but a verified workaround exists.",
  "calibration": {"kind": "none"},
  "next_action": null
}
```

The ordinal indices express rank only; do not treat the distance from level 0 to 1 as equal to the distance from 1 to 2.

## Numeric score

```json
{
  "contract_version": "decision-engine/2",
  "decision_id": "capacity-3",
  "materiality": "low",
  "decision": {
    "type": "score",
    "question": "What percentage of the declared capacity budget is used?",
    "status": "decided",
    "scale": {
      "kind": "numeric",
      "min": 0,
      "max": 100,
      "meaning": "Percentage of the declared capacity budget",
      "unit": "percent"
    },
    "score": 73.5
  },
  "confidence": {
    "level": "high",
    "basis": "the value comes from a direct deterministic measurement"
  },
  "evidence_refs": ["E-measurement"],
  "rationale": "The observed measurement is within the declared numeric scale.",
  "calibration": {"kind": "none"},
  "next_action": null
}
```

## Escalation

```json
{
  "contract_version": "decision-engine/2",
  "decision_id": "high-risk-2",
  "materiality": "high",
  "decision": {
    "type": "binary",
    "question": "Should the high-impact action be approved?",
    "status": "escalate",
    "value": null
  },
  "confidence": null,
  "evidence_refs": ["E-policy"],
  "rationale": "Policy requires an independent authorized reviewer for this decision.",
  "calibration": {"kind": "none"},
  "next_action": "Route the decision and evidence to the authorized reviewer."
}
```
