# Hypothesis Schema

Use this schema for markdown tables and JSON backlogs.

## Required fields

| Field | Meaning |
|---|---|
| `id` | Stable identifier such as `H001`. |
| `title` | Short hypothesis name. |
| `statement` | If we change/check X, Y should improve because Z. |
| `target_area` | activation, output, architecture, validation, security, package, token, documentation, consistency, evidence, or other. |
| `evidence` | Observed signal or missing evidence that justifies the hypothesis. |
| `expected_effect` | Expected measurable or gate-level improvement. |
| `validation_method` | Command, evaluator, scenario, review gate, or evidence needed. |
| `impact` | 1-5 expected value if successful. |
| `confidence` | 1-5 confidence that the mechanism is real. |
| `testability` | 1-5 quality of available validation. |
| `risk` | 1-5 regression or scope risk. |
| `cost` | 1-5 estimated implementation/validation cost. |
| `recommendation` | `test-now`, `defer`, `reject`, or `gather-evidence`. |

## Ranking

Use this qualitative scoring formula when a deterministic order is helpful:

```text
priority = impact + confidence + testability - risk - ceil(cost / 2)
```

Then adjust manually for:

- blocking validation/security/package issues;
- user-stated priorities;
- evaluator availability;
- dependency order, such as adding a harness before testing behavioral improvements;
- saturated primary scores that need auxiliary metrics first.

## JSON backlog shape

```json
{
  "target": "skill-name-or-path",
  "mode": "backlog-discovery",
  "evidence_status": "mixed",
  "recommendation": "test-hypotheses",
  "hypotheses": [
    {
      "id": "H001",
      "title": "Add non-activation cases",
      "statement": "If we add adjacent non-activation prompts, activation precision can be tested before changing the description.",
      "target_area": "activation",
      "evidence": "No non-activation scenarios were present in evals.",
      "expected_effect": "Better activation precision evidence without mutating runtime behavior.",
      "validation_method": "validate scenario JSON and run activation review when available",
      "impact": 4,
      "confidence": 4,
      "testability": 5,
      "risk": 1,
      "cost": 2,
      "recommendation": "test-now"
    }
  ],
  "selected_for_testing": ["H001"]
}
```

## Selection rules

- `backlog-discovery`: generate 5-10 candidates, select top 3-5, recommend next 1-3 tests.
- `deep-discovery`: generate up to 20 raw ideas across two passes, dedupe to top 5-8, recommend next 3-5 tests.
- `closure-discovery`: list remaining safe hypotheses or state `no-mutation-recommended`.
- Never select a hypothesis whose validation method is missing unless the recommendation is `gather-evidence`.
