# Sample Optimization Run

User: “Optimize `./skills/customer-briefing` completely and return a validated `skill.zip`.”

Response shape:
1. Preflight target root and inventory.
2. Freeze evaluator/scenarios/fixtures before mutation.
3. Run benchmark and harness evidence collection.
4. Run `skill-hypothesis-discovery` to generate and rank 5-10 candidate hypotheses.
5. Apply selected bounded hypotheses.
6. Run `skill-change-gate` or its checklist before accepting material candidate changes.
7. Validate after material changes.
8. Compress tokens only after behavior, validation, and change-gate checks are stable.
9. Revalidate after compression.
10. Harden and package.
11. Run final `skill-change-gate`, final benchmark, improver closure, and token-efficiency closure.
12. Return report and package path only when archive validation passed.

## Ledger excerpt

| Pass | Status | Evidence | Notes |
|---|---|---|---|
| skill-creator-juiced | applied-by-checklist | redesign check | no split needed |
| skill-improver | pass | hypothesis ledger | candidate patch proposed and bounded |
| skill-change-gate | pass | gate report | no blocking regression before accepting candidate |
| skill-benchmark | pass | static report | behavioral metrics planned |
| skill-harness | pass | scenario validator | suite valid; not executed |
| skill-hypothesis-discovery | pass | backlog report | generated 7 candidates; selected H1-H3 |
| skill-testing-and-validation | pass | validator command | structure validates |
| skill-token-efficient | pass | token audit | validation rerun after compression |
| skill-hardening | pass | readiness checks | package prepared |
| final skill-change-gate | pass | final gate report | no blocking regression after hardening/compression |
| final skill-benchmark | pass | final report | delta recorded |
| final skill-improver closure | pass | decision record | package accepted |
| final skill-token-efficient closure | pass | audit-only check | no mutation required |

## Discovery backlog excerpt

```yaml
generated_count: 7
selected_for_current_cycle: [H1, H2, H3]
deferred: [H4, H5, H6, H7]
no_mutation_rationale: null
```

## Hypothesis shape

```yaml
id: H1
statement: If SKILL.md remains a compact control plane and branch detail stays in references, context cost should drop while behavior remains stable.
files: [SKILL.md, references/workflow.md]
expected_effect: lower token estimate with validation passing
validation: structure validator plus activation scenario review
status: accepted
evidence: token estimate decreased and gates passed
```
