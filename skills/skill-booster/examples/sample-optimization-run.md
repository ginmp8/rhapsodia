# Sample Optimization Run

User: “Optimize `<target-skill-root>` completely and return a validated `skill.zip`.”

Response shape:

1. Resolve requested hosts/capabilities/Python launcher, preflight target root, and run portability validation when claimed.
2. Freeze evaluator/scenarios/fixtures before mutation; when external evidence matters, snapshot/pin the exact source bytes before analysis.
3. Collect benchmark and harness evidence.
4. Evaluate the reproducibility decision gate and validate its JSON record. Invoke `reproducibility-engineer` only when material signals justify it.
5. Run `skill-hypothesis-discovery` with reproducibility findings when applicable and rank 5-10 hypotheses.
6. Apply selected bounded hypotheses; avoid duplicate ownership when a reproducibility `apply` batch is delegated.
7. Run candidate `skill-change-gate` before accepting material changes.
8. Validate after material changes.
9. Run `skill-token-efficient` only after behavior, validation, and gates are stable.
10. Revalidate after compression.
11. Harden, run final gate/benchmark/improver/token closure, reverify material source snapshots, then freeze the exact final candidate.
12. Verify the freeze and requested-host portability, preflight package/report aliases, and commit package+success receipt transactionally; return them only when validation, hashes, and last-known-good/recovery guarantees pass.

## Ledger excerpt

Use one row per required pass. For explicit required sequences, available specialists need `execution_type: invoked-skill`; checklist-only is insufficient.

|   # | Pass | Status | Execution type | Evidence |
| --: | --- | --- | --- | --- |
| 1 | skill-creator-juiced | pass | invoked-skill | redesign/package-governance check |
| 2 | skill-benchmark | pass | invoked-skill | static report; behavioral metrics planned |
| 3 | skill-harness | pass | invoked-skill | scenario schema/coverage valid |
| 4 | reproducibility decision + optional reproducibility-engineer | pass | invoked-skill | invoke-audit; variability findings recorded |
| 5 | skill-hypothesis-discovery | pass | invoked-skill | 7 candidates; H1-H3 selected |
| 6 | skill-improver | pass | invoked-skill | bounded patch decision record |
| 7 | skill-change-gate | pass | invoked-skill | no blocking candidate regression |
| 8 | skill-quality-reviewer | pass | invoked-skill | capability delta preserved; no breaking removal |
| 9 | skill-package-architecture-review | pass | invoked-skill | unified package retained |
| 10 | context-architect | pass | invoked-skill | affected files and sequence mapped |
| 11 | skill-prompt-and-activation-review | pass | invoked-skill | activation and boundary review |
| 12 | prompt-architect | pass | invoked-skill | instruction clarity review |
| 13 | skill-consistency-repair | pass | invoked-skill | refs/scripts/templates aligned |
| 14 | documentation-quality | pass | invoked-skill | docs verified against files |
| 15 | karpathy-guidelines | pass | invoked-skill | scripts kept small and checked |
| 16 | security-and-governance-review | pass | invoked-skill | no blocking security finding |
| 17 | skill-testing-and-validation | pass | invoked-skill | validators pass |
| 18 | skill-cleanup-and-simplification | pass | invoked-skill | generated noise absent |
| 19 | skill-token-efficient | pass | invoked-skill | total/file/section token audit |
| 20 | post-compression skill-testing-and-validation | pass | invoked-skill | validators rerun |
| 21 | skill-hardening | pass | invoked-skill | readiness gates pass |
| 22 | final skill-change-gate | pass | invoked-skill | no blocking final regression |
| 23 | final skill-benchmark | pass | invoked-skill | final score/delta recorded |
| 24 | final skill-improver | pass | invoked-skill | accept/reject ledger closed |
| 25 | final skill-token-efficient | pass | invoked-skill | no unjustified local token growth |

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
