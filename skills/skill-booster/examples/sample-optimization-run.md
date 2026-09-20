# Sample Optimization Run

User: “Optimize `<target-skill-root>` completely and return a validated `skill.zip`.”

Response shape:

1. Resolve requested hosts/capabilities/Python launcher, preflight target root, and run portability validation when claimed.
2. Freeze evaluator/scenarios/fixtures before mutation; when external evidence matters, snapshot/pin the exact source bytes before analysis.
3. Collect benchmark/harness evidence, classify reproducibility, then run the remaining diagnostic providers in passbook order: quality, package architecture, context, prompt/activation, prompt architecture, consistency, documentation, code, security, testing, cleanup, and token/context analysis.
4. Reconcile all diagnostic evidence, then run `skill-hypothesis-discovery` and rank 5-10 bounded hypotheses.
5. Apply one selected bounded transformation with one declared mutation owner; avoid duplicate ownership when a reproducibility `apply` batch is delegated.
6. Run candidate `skill-change-gate`, then `skill-testing-and-validation`, before accepting material changes.
7. Harden, run final change gate, final benchmark, final improver lifecycle closure, and final token-efficiency closure.
8. For complete/full optimization, resolve every material actionable finding to `fixed`, `rejected`, `accepted-trade-off`, `blocked`, or `not-applicable`; if final token closure finds material avoidable waste, open another bounded batch and rerun affected gates instead of deferring it.
9. Reverify material source snapshots, freeze the exact final candidate, verify requested-host portability, preflight package/report aliases, and commit package+success receipt transactionally; return them only when validation, hashes, and last-known-good/recovery guarantees pass.

## Ledger excerpt

Use one row per required pass. For explicit required sequences, available specialists need `execution_type: invoked-skill`; checklist-only is insufficient.

|   # | Pass | Status | Execution type | Evidence |
| --: | --- | --- | --- | --- |
| 1 | skill-creator-juiced | pass | invoked-skill | redesign/package-governance check |
| 2 | skill-benchmark | pass | invoked-skill | static report; behavioral metrics planned |
| 3 | skill-harness | pass | invoked-skill | scenario schema/coverage valid |
| 4 | reproducibility decision + optional reproducibility-engineer | pass | invoked-skill | invoke-audit; variability findings recorded |
| 5 | skill-quality-reviewer | pass | invoked-skill | capability delta preserved; no breaking removal |
| 6 | skill-package-architecture-review | pass | invoked-skill | unified package retained |
| 7 | context-architect | pass | invoked-skill | affected files and sequence mapped |
| 8 | skill-prompt-and-activation-review | pass | invoked-skill | activation and boundary review |
| 9 | prompt-architect | pass | invoked-skill | instruction clarity review |
| 10 | skill-consistency-repair | pass | invoked-skill | refs/scripts/templates aligned |
| 11 | documentation-quality | pass | invoked-skill | docs verified against files |
| 12 | karpathy-guidelines | pass | invoked-skill | scripts kept small and checked |
| 13 | security-and-governance-review | pass | invoked-skill | no blocking security finding |
| 14 | skill-testing-and-validation | pass | invoked-skill | baseline validators/tests classified |
| 15 | skill-cleanup-and-simplification | pass | invoked-skill | generated noise absent |
| 16 | skill-token-efficient | pass | invoked-skill | diagnostic token/context findings recorded |
| 17 | skill-hypothesis-discovery | pass | invoked-skill | 7 candidates; H1-H3 selected |
| 18 | skill-improver | pass | invoked-skill | one selected bounded transformation applied |
| 19 | skill-change-gate | pass | invoked-skill | no blocking candidate regression |
| 20 | skill-testing-and-validation | pass | invoked-skill | affected validators/tests rerun |
| 21 | skill-hardening | pass | invoked-skill | readiness gates pass |
| 22 | final skill-change-gate | pass | invoked-skill | no blocking final regression |
| 23 | final skill-benchmark | pass | invoked-skill | final score/delta recorded |
| 24 | final skill-improver | pass | invoked-skill | accept/reject/revert ledger closed |
| 25 | final skill-token-efficient | pass | invoked-skill | no unresolved material avoidable context waste |

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
