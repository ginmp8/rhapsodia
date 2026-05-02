# Sample Optimization Run

## User Request

"Optimize `./skills/customer-briefing` completely and return a validated package."

## Skill Booster Response Shape

1. Preflight target root and inventory.
2. Freeze baseline evaluator.
3. Run specialist ledger in sequence.
4. Apply bounded patches.
5. Validate after material changes.
6. Compress tokens near the end.
7. Revalidate after compression.
8. Harden and package.
9. Benchmark final state.
10. Return report and `skill.zip` only if validation passed.

## Example Specialist Ledger

| Pass | Status | Evidence | Notes |
|---|---|---|---|
| skill-creator-juiced | applied-by-checklist | major redesign escalation check | no split needed |
| skill-improver | pass | baseline/final comparison | H1 accepted, H2 rejected |
| skill-benchmark | pass | benchmark report | score 72 to 84 |
| skill-harness | planned | scenario suite created | not executed in environment |
| skill-package-architecture-review | pass | architecture decision | unified skill with modes |
| context-architect | not-applicable | no code dependencies | package is instruction-only |
| skill-prompt-and-activation-review | pass | description and boundaries refined | non-triggers added |
| prompt-architect | pass | prompt body simplified | output contract preserved |
| skill-consistency-repair | pass | references aligned | broken local link fixed |
| documentation-quality | pass | references rewritten | duplicate guide merged |
| karpathy-guidelines | not-applicable | no scripts | no technical code to review |
| security-and-governance-review | pass | package safety review | package exclusions added |
| skill-testing-and-validation | pass | validator command | structure validates |
| skill-cleanup-and-simplification | pass | file inventory | generated reports excluded |
| skill-token-efficient | pass | token audit | reduction after behavior stable |
| skill-hardening | pass | final readiness checks | package prepared |
| final skill-benchmark | pass | final report | delta recorded |
| final skill-improver closure | pass | decision record | package accepted |

## Example Hypothesis

```yaml
id: H1
statement: If SKILL.md is reduced to control-plane rules and branch details move to references, context cost should drop while behavior remains stable.
files:
  - SKILL.md
  - references/workflow.md
expected_effect: lower token count with validation passing
validation: structure validator plus activation scenario review
status: accepted
evidence: token estimate decreased and gates passed
```
