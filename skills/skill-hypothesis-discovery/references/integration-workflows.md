# Integration Workflows

The portable core uses Agent Skills conventions and relative package resources. Host-specific invocation or metadata is optional adapter behavior; do not make discovery semantics depend on ChatGPT, Codex, Claude, Copilot, Cursor, or another host.

## Handoff contract

Downstream mutation/testing receives, at minimum:

- target baseline identity;
- evidence snapshot id;
- selected hypothesis id and canonical dedupe key;
- exact evidence refs;
- mechanism and expected effect;
- evaluator id/status/method;
- acceptance criteria;
- conflicts/dependencies;
- priority inputs and deterministic rank;
- risk/rollback notes;
- whether additional evidence is required first.

If any of these are absent, downgrade the handoff rather than silently filling the gap downstream.

## With skill-booster

Recommended full-optimization order:

```text
inventory/baseline -> benchmark/harness evidence -> skill-hypothesis-discovery -> skill-improver -> skill-change-gate -> validation/package
```

Use discovery after baseline evidence exists. `deep-discovery` may internally consider a broader set, but the final backlog remains capped and deduplicated. Saturated primary metrics require an auxiliary metric before another mutation experiment is selected.

## With skill-improver

Use when no bounded hypothesis is already supplied or when the current evaluator is saturated/blocked. Test one hypothesis at a time, beginning with `next_hypothesis_id`.

Do not combine multiple selected hypotheses into one patch merely because they were shortlisted. A combined experiment is valid only when the hypotheses are inseparable by design and the backlog records that dependency explicitly.

Rejected hypotheses are not retried unless new evidence changes the mechanism, evaluator, or acceptance criteria.

## With skill-creator-juiced

Use in redesign or quality-upgrade modes when an existing package has several plausible improvement directions. Do not use this skill as a substitute for net-new skill creation.

## With skill-harness and skill-benchmark

These workflows provide evidence and evaluators. This skill consumes exact identified results and turns them into bounded hypotheses. It does not rewrite benchmark/harness assets, thresholds, fixtures, or expected outputs.

When a metric is saturated, request a non-saturated auxiliary measurement rather than treating the saturated score as room for further optimization.

## With skill-change-gate

`skill-change-gate` evaluates a concrete candidate after mutation. Pass it the baseline identity, evidence snapshot, hypothesis id, evaluator identity, acceptance criteria, and expected risk areas. Candidate acceptance is outside this skill.

## With specialist reviewers

Specialist findings become evidence only when their target/version is identified:

- `skill-package-architecture-review` -> architecture signals;
- `skill-prompt-and-activation-review` -> activation/boundary signals;
- `documentation-quality` -> documentation signals;
- `security-and-governance-review` -> safety/governance signals;
- `skill-token-efficient` -> token signals;
- `skill-cleanup-and-simplification` -> hygiene signals;
- `skill-consistency-repair` -> consistency signals;
- `skill-hardening` -> maturity/package signals.

Do not require those skills to know this skill. Discovery remains a planner/orchestrator concern.
