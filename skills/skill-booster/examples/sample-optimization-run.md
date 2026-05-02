# Sample Optimization Run

User: “Optimize `./skills/customer-briefing` completely and return a validated `skill.zip`.”

Response shape:
1. Preflight target root and inventory.
2. Freeze evaluator/scenarios/fixtures before mutation.
3. Run the specialist ledger in order.
4. Apply bounded hypotheses.
5. Validate after material changes.
6. Compress tokens only after behavior and gates are stable.
7. Revalidate after compression.
8. Harden and package.
9. Run final benchmark, improver closure, and token-efficiency closure.
10. Return report and package path only when archive validation passed.

## Ledger excerpt

| Pass | Status | Evidence | Notes |
|---|---|---|---|
| skill-creator-juiced | applied-by-checklist | redesign check | no split needed |
| skill-benchmark | pass | static report | behavioral metrics planned |
| skill-harness | pass | scenario validator | suite valid; not executed |
| skill-testing-and-validation | pass | validator command | structure validates |
| skill-token-efficient | pass | token audit | validation rerun after compression |
| skill-hardening | pass | readiness checks | package prepared |
| final skill-benchmark | pass | final report | delta recorded |
| final skill-improver closure | pass | decision record | package accepted |
| final skill-token-efficient closure | pass | audit-only check | no mutation required |

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
