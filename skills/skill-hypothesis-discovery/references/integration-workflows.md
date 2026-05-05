# Integration Workflows

## With skill-booster

Use after baseline inventory and after initial benchmark/harness evidence exists.

Recommended full-optimization order:

```text
inventory/baseline -> benchmark/harness evidence -> skill-hypothesis-discovery -> skill-improver -> skill-change-gate -> validation/package
```

Run once by default. Use `deep-discovery` only for full optimization when no clear hypothesis exists, the benchmark is saturated, or the user asks for broad exploration. The output should feed the `accepted/rejected hypotheses` ledger, but this skill itself does not accept patches.

## With skill-improver

Use only when no bounded hypothesis is supplied or the primary evaluator is saturated. Handoff format:

- selected hypothesis id and statement;
- files likely to change;
- validation method;
- accept/reject rule;
- risk and rollback notes;
- whether evidence must be gathered before mutation.

`skill-improver` tests one bounded hypothesis at a time. Rejected hypotheses are not retried unless new evidence changes the mechanism.

## With skill-creator-juiced

Use in `redesign` and `quality-upgrade` modes when there are several possible improvement directions. Do not use for routine net-new creation unless the user asks for a post-creation improvement backlog.

## With skill-harness and skill-benchmark

`skill-harness` and `skill-benchmark` provide evidence. This skill consumes their findings and turns them into hypotheses. Do not make those skills depend on this one.

## With skill-change-gate

`skill-change-gate` evaluates a concrete candidate after mutation. This skill runs before mutation and proposes candidates. Handoff should state what gate areas must be checked after the patch: activation, scope, references, safety, validation, packaging, output contract, or evidence discipline.

## With specialist skills

Specialist outputs can become evidence signals:

- `skill-package-architecture-review`: architecture hypotheses.
- `skill-prompt-and-activation-review`: activation hypotheses.
- `documentation-quality`: documentation hypotheses.
- `security-and-governance-review`: safety/governance hypotheses.
- `skill-token-efficient`: token hypotheses.
- `skill-cleanup-and-simplification`: hygiene hypotheses.
- `skill-consistency-repair`: consistency hypotheses.
- `skill-hardening`: maturity/package hypotheses.

Do not require each specialist to know this skill. Keep discovery in orchestrators and planners.
