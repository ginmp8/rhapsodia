---
name: checkpoint-convergence
description: Control reference-grounded incremental implementation through small checkpoints, frozen oracle identity, ordered non-overridable gates, bounded repair/re-review, live-state revalidation, accepted-feedback provenance, checkpoint materialization, and closure verification. Use when progress must not advance until an increment converges against a high-fidelity reference. Do not use for runtime-discovered topology/fan-out/pipelines (use adaptive-workflow-orchestration), simple direct work, or domain-owner selection.
---

# Checkpoint Convergence

## Purpose

Own the **progression control plane** for reference-grounded work. This skill does not implement production changes. It compiles a `convergence-plan/v1` that keeps reference, oracle, candidate, gate evidence, repair, and promotion identities explicit while Magia remains the canonical producer/repair owner.

## Core invariants

1. Exactly one progression owner controls checkpoint advancement.
2. Reference scope is bounded per checkpoint; do not replace a stronger primary reference with a speculative mega-spec.
3. Freeze `oracle_identity` before the producer sees/changes the candidate.
4. Checkpoints are small enough for fast review and bounded repair.
5. `gate_ids` order is binding. A later pass cannot override an earlier required failure.
6. Repair creates a new candidate identity and invalidates affected prior gate evidence.
7. Fresh-context reviewers receive current candidate/reference state, frozen oracle, accepted feedback, and remaining budgets—not the producer's hidden rationale.
8. Persisted memory/ledgers are evidence claims, not operational truth. Revalidate mutable live state according to `freshness_policy`.
9. Autonomy policy controls human approval frequency; it never weakens executable, perceptual, adversarial, freshness, or closure requirements.
10. Promoted checkpoint identity/evidence is materialized before dependent checkpoints consume it when the plan requires materialization.
11. Closure revalidation reconciles the authoritative end state before final completion.
12. Deterministic code owns mechanically enforceable guarantees; agents own bounded judgment.

## Contract

Use `convergence-plan/v1` from `assets/templates/convergence-plan.json.template` and validate with:

```text
<PYTHON> scripts/validate_convergence_plan.py <PLAN.json>
```

Load `references/control-plane-composition.md` whenever dynamic orchestration is nested in a checkpoint. Load `references/research-basis.md` for the evidence/adaptation boundary.

## Workflow

1. Resolve the already-authorized Magia phase, producer authority, reference identity, and terminal outcome.
2. Split into the smallest useful checkpoint DAG. Early checkpoints should be especially small when they establish architecture/behavioral seams.
3. Bind each checkpoint to `reference_scope` and freeze `oracle_identity` before production.
4. Declare required gates in exact execution order, evaluator identity/isolation, capability, and rerun-after-repair semantics.
5. Validate/freeze the plan and budgets.
6. Dispatch Magia as canonical producer for the checkpoint.
7. Run gates in order. Stop at the first failed/blocked/invalid/stale required gate.
8. Repair through Magia only; rerun every affected required gate for the new candidate identity.
9. Promote only when all required current evidence passes and dependencies are already promoted.
10. Materialize promoted identity/evidence when required; carry forward only accepted/proven feedback with provenance.
11. Revalidate mutable reference/live state according to policy before mutation/promotion/closure.
12. At closure, reconcile authoritative final state; report pass, blocked, escalated, or exhausted budget truthfully.

## Composition

A bounded `dynamic-workflow-plan/v1` may be used **inside** one checkpoint to gather independent evidence or process a wide read-only surface. It returns structured evidence to this controller. It cannot promote the checkpoint, alter the frozen oracle, or create a second progression graph.

Conversely, this skill does not own broad runtime topology. If the primary problem is discovering/decomposing runtime work rather than proving incremental convergence, use `adaptive-workflow-orchestration`.

## Stop conditions

Stop when reference/oracle identity is missing or stale; owner/authority is unresolved; a required gate/capability cannot run; repair/checkpoint budget is exhausted; a dependent checkpoint would start before promotion; candidate/reference state changed without required revalidation; a reviewer cannot satisfy declared isolation; or continuation would require weakening frozen criteria.

## Output

Return the validated convergence plan, plan identity, checkpoint/candidate/reference identities, gate results in order, repair history, promoted checkpoint evidence, accepted-feedback provenance, closure revalidation status, and terminal reason. Structural validation is not runtime proof.
