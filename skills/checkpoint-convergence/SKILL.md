---
name: checkpoint-convergence
description: Control reference-grounded incremental implementation through small checkpoints, frozen oracle identity, ordered non-overridable gates, bounded repair/re-review, live-state revalidation, accepted-feedback provenance, checkpoint materialization, and closure verification. Use when progress must not advance until an increment converges against a high-fidelity reference. Do not use for runtime-discovered topology/fan-out/pipelines (use adaptive-workflow-orchestration), simple direct work, or domain-owner selection.
---

# Checkpoint Convergence

## Purpose and routing

Own the **progression control plane** for reference-grounded work. This skill compiles and governs a `convergence-plan/v1`; it does not implement production changes. Magia remains the canonical producer/repair owner.

Activate when all are true:

- a high-fidelity reference exists and can be bounded by checkpoint;
- an already-authorized Magia phase must advance incrementally rather than as one unbounded change;
- oracle and required-gate criteria can be frozen before the producer changes the candidate; and
- checkpoint/gate progression adds material assurance beyond simple direct execution.

Do not use this skill to implement or repair production code, invent or weaken oracle criteria, choose domain ownership, or coordinate broad runtime-discovered fan-out/pipelines. For the last case use `adaptive-workflow-orchestration`. If reference/oracle/authority cannot be resolved, stop instead of fabricating them.

## Non-negotiable invariants

1. Exactly one progression owner controls checkpoint advancement.
2. Reference scope is bounded per checkpoint; do not replace a stronger primary reference with a speculative mega-spec.
3. Freeze `oracle_identity` before the producer sees/changes the candidate.
4. Checkpoints stay small enough for independent review and bounded repair within declared budgets.
5. `gate_ids` order is binding. A later pass cannot override an earlier required failure.
6. Repair creates a new candidate identity and invalidates affected prior gate evidence.
7. Fresh-context reviewers receive current candidate/reference state, frozen oracle, accepted feedback, and remaining budgets—not the producer's hidden rationale.
8. Persisted memory/ledgers are evidence claims, not operational truth. Revalidate mutable live state according to `freshness_policy`.
9. Autonomy policy controls human approval frequency; it never weakens executable, perceptual, adversarial, freshness, or closure requirements.
10. Promoted checkpoint identity/evidence is materialized before dependent checkpoints consume it when `promotion.materialize_promoted_checkpoint` requires it.
11. Closure revalidation reconciles the authoritative end state before final completion.
12. Deterministic code owns mechanically enforceable guarantees; agents own bounded judgment.

## Contract and resource loading

Use `assets/templates/convergence-plan.json.template` with `schemas/convergence-plan.schema.json`, then validate the plan with:

```text
<PYTHON> scripts/validate_convergence_plan.py <PLAN.json>
```

This `SKILL.md` is sufficient to select the skill and start the ordinary workflow. Load supporting Markdown only for the active branch:

- `references/control-plane-composition.md` — only when a dynamic workflow is nested inside a checkpoint;
- `references/research-basis.md` — only when research provenance or the adaptation boundary must be justified; it adds no operational gate or promotion rule.

## Workflow

1. Resolve the already-authorized Magia phase, producer authority, reference identity, and terminal outcome.
2. Split work into the smallest useful checkpoint DAG; make early architecture/behavioral-seam checkpoints especially small.
3. Bind every checkpoint to `reference_scope` and freeze `oracle_identity` before production.
4. Declare required gates in exact execution order, evaluator identity/isolation, capability, and rerun-after-repair semantics.
5. Validate and freeze the plan and finite budgets before production starts.
6. Dispatch Magia as canonical producer for the checkpoint.
7. Run gates in declared order; stop at the first failed, blocked, invalid, or stale required gate.
8. Repair through Magia only; assign a new candidate identity and rerun every affected required gate.
9. Promote only when all required current evidence passes and all dependencies are already promoted.
10. Materialize promoted identity/evidence when required; carry forward only accepted/proven feedback with provenance.
11. Revalidate mutable reference/live state at the points required by `freshness_policy` before mutation, promotion, or closure.
12. At closure, reconcile authoritative final state and report pass, blocked, escalated, or exhausted budget truthfully.

## Composition boundary

A bounded `dynamic-workflow-plan/v1` may run **inside one checkpoint** to gather independent evidence or process a wide read-only surface. It returns structured evidence to this controller; it cannot promote the checkpoint, alter the frozen oracle, broaden producer authority, or create a second progression graph.

If the primary problem is runtime discovery/decomposition rather than proving incremental convergence against a reference, route to `adaptive-workflow-orchestration` instead.

## Stop conditions

Stop when reference/oracle identity is missing or stale; owner/authority is unresolved; a required gate/capability cannot run; repair/checkpoint budget is exhausted; a dependent checkpoint would start before promotion; candidate/reference state changed without required revalidation; a reviewer cannot satisfy declared isolation; or continuation would require weakening frozen criteria.

## Output contract

Return the validated convergence plan, plan identity, checkpoint/candidate/reference identities, gate results in declared order, repair history, promoted checkpoint evidence, accepted-feedback provenance, closure revalidation status, and terminal reason. Structural validation is not runtime proof.
