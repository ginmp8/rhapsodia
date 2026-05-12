# Sample Optimization Run

User: “Optimize `.github/skills/customer-briefing` completely and return a validated `skill.zip`.”

Response shape:

1. Preflight target root and inventory.
2. Freeze evaluator/scenarios/fixtures before mutation.
3. Collect benchmark and harness evidence.
4. Run `skill-hypothesis-discovery` and rank 5-10 hypotheses.
5. Apply selected bounded hypotheses.
6. Run candidate `skill-change-gate` before accepting material changes.
7. Validate after material changes.
8. Run `skill-token-efficient` only after behavior, validation, and gates are stable.
9. Revalidate after compression.
10. Harden and package only after gates pass.
11. Run final gate, benchmark, improver closure, and token-efficiency closure.
12. Return report and package path only when archive validation passes.

## Ledger excerpt

Use one row per required pass. For explicit required sequences, available specialists need `execution_type: invoked-skill`; checklist-only is insufficient.

|   # | Pass                                          | Status | Execution type | Evidence                                  |
| --: | --------------------------------------------- | ------ | -------------- | ----------------------------------------- |
|   1 | skill-creator-juiced                          | pass   | invoked-skill  | redesign/package-governance check         |
|   2 | skill-benchmark                               | pass   | invoked-skill  | static report; behavioral metrics planned |
|   3 | skill-harness                                 | pass   | invoked-skill  | scenario schema/coverage valid            |
|   4 | skill-hypothesis-discovery                    | pass   | invoked-skill  | 7 candidates; H1-H3 selected              |
|   5 | skill-improver                                | pass   | invoked-skill  | bounded patch decision record             |
|   6 | skill-change-gate                             | pass   | invoked-skill  | no blocking candidate regression          |
|   7 | skill-package-architecture-review             | pass   | invoked-skill  | unified package retained                  |
|   8 | context-architect                             | pass   | invoked-skill  | affected files and sequence mapped        |
|   9 | skill-prompt-and-activation-review            | pass   | invoked-skill  | activation and boundary review            |
|  10 | prompt-architect                              | pass   | invoked-skill  | instruction clarity review                |
|  11 | skill-consistency-repair                      | pass   | invoked-skill  | refs/scripts/templates aligned            |
|  12 | documentation-quality                         | pass   | invoked-skill  | docs verified against files               |
|  13 | karpathy-guidelines                           | pass   | invoked-skill  | scripts kept small and checked            |
|  14 | security-and-governance-review                | pass   | invoked-skill  | no blocking security finding              |
|  15 | skill-testing-and-validation                  | pass   | invoked-skill  | validators pass                           |
|  16 | skill-cleanup-and-simplification              | pass   | invoked-skill  | generated noise absent                    |
|  17 | skill-token-efficient                         | pass   | invoked-skill  | total/file/section token audit            |
|  18 | post-compression skill-testing-and-validation | pass   | invoked-skill  | validators rerun                          |
|  19 | skill-hardening                               | pass   | invoked-skill  | readiness gates pass                      |
|  20 | final skill-change-gate                       | pass   | invoked-skill  | no blocking final regression              |
|  21 | final skill-benchmark                         | pass   | invoked-skill  | final score/delta recorded                |
|  22 | final skill-improver                          | pass   | invoked-skill  | accept/reject ledger closed               |
|  23 | final skill-token-efficient                   | pass   | invoked-skill  | no unjustified local token growth         |

## Discovery backlog excerpt

```yaml
generated_count: 7
selected_for_current_cycle: [H1, H2, H3]
deferred: [H4, H5, H6, H7]
no_mutation_rationale: null
reconciliation_gate: pass
finalization_allowed: true
```

## Hypothesis shape

```yaml
id: H1
statement: If branch detail moves to references, context cost drops while behavior remains stable.
files: [SKILL.md, references/workflow.md]
expected_effect: lower token estimate with validation passing
validation: structure validator plus activation scenario review
status: accepted
evidence: token estimate decreased and gates passed
```
