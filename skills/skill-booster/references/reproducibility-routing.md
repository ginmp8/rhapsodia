# Reproducibility Routing

Use this gate after baseline benchmark/harness evidence and before `skill-hypothesis-discovery`. Its purpose is to decide whether `reproducibility-engineer` adds material value for the current target. The gate is always evaluated; the specialist is conditional.

## Decision states

Choose exactly one:

- `invoke-audit`: material reproducibility risk exists, but the current cycle still needs a ranked backlog. Invoke `reproducibility-engineer` in `audit-only`; feed its variability map, ceiling, and recommended controls into `skill-hypothesis-discovery`.
- `invoke-apply`: reproducibility is the explicit objective, or a bounded selected hypothesis already requires a reproducibility transformation. Invoke `reproducibility-engineer` in `apply`; treat that specialist as owner of that bounded patch batch, then run `skill-change-gate` before acceptance.
- `not-applicable`: evidence shows no material controllable reproducibility gap. Record why; do not invoke merely because scripts, evals, validators, or a complex workflow exist.
- `blocked`: the specialist is applicable but required baseline/evaluator/source truth cannot be frozen or accessed safely.
- `unavailable`: the specialist would be applicable but cannot be invoked in the active environment. Apply only the routing checklist; do not claim specialist execution.

## Material signals

Treat a signal as material only when it affects the semantic contract, quality gates, delivery guarantees, or repeated execution quality. One material signal is enough to consider invocation; multiple weak cosmetic signals are not.

1. Equivalent supported inputs can produce materially inconsistent semantic outcomes or workflow decisions.
2. Critical behavior exists only in free-form instructions when it could reliably move to a script, schema, type, validator, or deterministic transform.
3. Semantic/output contracts are absent, ambiguous, or too weak to validate acceptance.
4. Objective validation depends unnecessarily on model self-judgment, or generator and evaluator are not sufficiently independent.
5. Evaluator assets can drift with the candidate, or baseline/freeze discipline is missing.
6. Repair loops are open-ended, taste-driven, or lack stable diagnostics/stop conditions.
7. Final passing state can still be edited without invalidating evidence.
8. Package/delivery identity cannot be tied to the validated candidate with atomic delivery or a receipt when that matters; package/report aliases, last-known-good preservation, or rollback recovery are not controlled.
9. External nondeterminism such as versions, data snapshots, clocks, repository revisions, or tool state is material but neither pinned nor recorded; live-source bytes can drift between baseline and acceptance.
10. Structured outputs repeatedly fail due to invented fields, inconsistent enums, malformed syntax, or missing typed/schema constraints.

## Skip rules

Use `not-applicable` when all material risks are already controlled, remaining variance is intentionally subjective/model-judgment, or extra machinery would not remove an observed source of variance. Do not invoke the specialist just to imitate another skill's architecture.

## Mode and ownership rules

- Default applicable route: `invoke-audit`.
- Use `invoke-apply` only when reproducibility is explicitly requested or a selected bounded hypothesis is clearly owned by reproducibility transformation.
- After `invoke-audit`, `skill-hypothesis-discovery` owns backlog ranking and `skill-improver` normally owns selected patches.
- After `invoke-apply`, `reproducibility-engineer` owns only that bounded transformation batch. Run `skill-change-gate`; then return remaining hypotheses to the normal Booster sequence.
- Never let `reproducibility-engineer` replace `skill-harness`, `skill-benchmark`, `skill-change-gate`, or general hardening. Their evidence roles are distinct.

## Decision record

Create a JSON record and validate it with `scripts/validate_reproducibility_decision.py` before hypothesis discovery.

```json
{
  "decision_version": 1,
  "target": "<target skill identity>",
  "state": "invoke-audit",
  "selected_mode": "audit-only",
  "specialist_status": "invoked",
  "downstream_owner": "skill-improver",
  "material_signals": [
    {
      "id": "R4",
      "evidence": "final passing candidate can still be edited without invalidating evidence"
    }
  ],
  "rationale": "A reproducibility audit can turn the observed finalization variance into bounded hypotheses."
}
```

`specialist_status: invoked` means the skill was actually invoked. Use `blocked`, `unavailable`, or `not-applicable` otherwise. Checklist-only review never counts as invocation.
