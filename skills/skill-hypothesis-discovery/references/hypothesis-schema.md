# Hypothesis Backlog Contract

## Contract version

The canonical machine-readable backlog is `schema_version: "2.0"`. Unversioned legacy backlogs may be read by the validator for compatibility, but new outputs must use v2. Legacy compatibility is read-only and does not prove the v2 reproducibility gates.

## Item taxonomy

Every backlog item has exactly one `kind`:

- `testable-hypothesis` — a bounded causal claim that can be evaluated.
- `recommendation` — advice or sequencing guidance that is not itself an experiment.
- `evidence-gap` — missing evidence that must be collected before a mutation can be justified.
- `unsupported-speculation` — a plausible-sounding idea without the minimum evidence or measurable path. It must be rejected, not promoted into the test queue.

Only `testable-hypothesis` items may be selected for testing.

## Minimum evidence for a testable hypothesis

A `testable-hypothesis` must have all of the following:

1. at least one `evidence_ref` that resolves to an evidence snapshot source with status `measured`, `observed`, `derived`, or `supplied`;
2. a causal `mechanism` explaining why the proposed change/check could cause the expected effect;
3. an `expected_effect.observable` that can be inspected or measured;
4. at least one metric id in `expected_effect.metric_ids`;
5. an evaluator record with `status: available` before it can be `test-now`;
6. at least one explicit acceptance criterion;
7. no unresolved dependency if it is selected for the next experiment.

`planned`, `gap`, or `unknown` evidence can justify an `evidence-gap`; by itself it cannot justify `test-now`.

## Evidence snapshot

A v2 backlog records the exact evidence set used for discovery:

```json
{
  "evidence_snapshot": {
    "snapshot_id": "sha256:<digest>",
    "sources": [
      {
        "id": "E001",
        "status": "observed",
        "identity": "sha256:<source-bytes-or-report-hash>",
        "summary": "Validator accepts selected hypotheses without an evaluator."
      }
    ]
  }
}
```

The validator recomputes `snapshot_id` from `sources`, sorted by source id and serialized canonically. This binds the backlog to the same evidence identity. Do not invent source identities: when exact bytes/revision are unavailable, use a truthful stable external identifier or an explicit `unverified:<label>` identity and downgrade evidence claims accordingly.

## Metrics and saturation

Top-level `metrics` records the measurement surface:

```json
{
  "metrics": [
    {"id": "M001", "role": "primary", "status": "saturated", "name": "static benchmark score"},
    {"id": "M002", "role": "auxiliary", "status": "active", "name": "holdout regression failures"}
  ]
}
```

Statuses are `active`, `saturated`, or `unknown`.

A saturated metric remains a gate. A `test-now` item must reference at least one `active` metric. Do not optimize further against a saturated metric alone; add an auxiliary metric or return `evidence-gap` / `no-mutation-recommended`.

## Stable hypothesis identity and deduplication

Each testable hypothesis uses bounded semantic keys:

- `subject_key` — stable slug for the affected subject;
- `mechanism_key` — stable slug for the causal mechanism;
- `effect_key` — stable slug for the observable effect.

`dedupe_key` must equal:

```text
<target_area>:<subject_key>:<mechanism_key>:<effect_key>
```

All components use lowercase ASCII letters, digits, `_`, `-`, or `.`. The validator rejects duplicate `dedupe_key` values. Semantic near-duplicates that use different keys still require analyst judgment; when detected, merge them before ranking rather than keeping both.

## Conflict and dependency edges

- `conflicts_with` contains ids of mutually exclusive hypotheses. Conflict edges must be symmetric.
- `depends_on` contains ids of prerequisite backlog items. An item with unresolved dependencies cannot be selected for the next experiment.
- Conflicting items cannot appear together in `selected_for_testing`.

## Priority and deterministic ordering

For ready `testable-hypothesis` items:

```text
priority = impact + confidence + testability - risk - ceil(cost / 2)
```

Ranking precedence is:

1. `gate_effect: blocking` before `non-blocking` before `informational`;
2. higher `priority`;
3. higher `testability`;
4. higher `confidence`;
5. lower `risk`;
6. lower `cost`;
7. lexical `id`.

Do not manually reshuffle equal candidates without recording a new material constraint/evidence item that changes the ordering inputs.

## Experiment limits

Final backlog limits are intentionally small:

| Mode | Maximum final items | Maximum selected | Next experiment |
|---|---:|---:|---|
| `backlog-discovery` | 8 | 3 | exactly one `next_hypothesis_id` when testing is recommended |
| `deep-discovery` | 8 final items | 3 | exactly one next hypothesis; raw ideation is discarded after critique/dedupe |
| `closure-discovery` | 5 | 2 | optional |
| `evidence-gap-review` | 5 | 0 | evidence collection only |

`selected_for_testing` is a shortlist, not a simultaneous mutation batch. `skill-improver` should test one bounded hypothesis at a time, starting with `next_hypothesis_id`.

## Canonical v2 shape

```json
{
  "schema_version": "2.0",
  "target": {"name": "skill-name", "identity": "sha256:<target-snapshot>"},
  "mode": "backlog-discovery",
  "evidence_status": "mixed",
  "recommendation": "test-hypotheses",
  "evidence_snapshot": {
    "snapshot_id": "sha256:<digest-of-sources>",
    "sources": []
  },
  "metrics": [],
  "items": [
    {
      "id": "H001",
      "kind": "testable-hypothesis",
      "title": "Evaluator availability gate",
      "statement": "If test-now requires an available evaluator, unsupported mutation experiments should be filtered before execution.",
      "target_area": "validation",
      "subject_key": "test-now-eligibility",
      "mechanism_key": "require-available-evaluator",
      "effect_key": "unsupported-experiments",
      "dedupe_key": "validation:test-now-eligibility:require-available-evaluator:unsupported-experiments",
      "evidence_refs": ["E001"],
      "mechanism": "The current backlog permits selection before a measurable evaluator exists.",
      "expected_effect": {
        "observable": "Selected hypotheses all have an available evaluator.",
        "direction": "reduce",
        "metric_ids": ["M001"]
      },
      "evaluator": {"id": "EV001", "status": "available", "method": "validator regression"},
      "acceptance_criteria": ["No selected test-now item has evaluator.status != available."],
      "impact": 4,
      "confidence": 4,
      "testability": 5,
      "risk": 1,
      "cost": 2,
      "gate_effect": "blocking",
      "recommendation": "test-now",
      "conflicts_with": [],
      "depends_on": []
    }
  ],
  "selected_for_testing": ["H001"],
  "next_hypothesis_id": "H001"
}
```

## Recommendation constraints

- `testable-hypothesis`: `test-now`, `defer`, `gather-evidence`, or `reject`.
- `evidence-gap`: `gather-evidence` or `defer`; never select.
- `recommendation`: `defer`, `gather-evidence`, or `reject`; never select.
- `unsupported-speculation`: `reject`; never select.

A hypothesis may be plausible and still be ineligible. Plausibility is not evidence.
