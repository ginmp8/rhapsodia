---
name: adaptive-workflow-orchestration
description: Design and operate bounded task-specific execution workflows when runtime topology should adapt to an already-authorized objective. Use for choosing and validating single, sequential, classify-route, fan-out/synthesize, pipeline, adversarial verification, generate/filter, tournament, bounded-loop, or gated-convergence strategies; decomposing dependency-aware work; controlling parallelism, isolation, budgets, retries, state, verification, and termination; or compiling a portable workflow plan to native host capabilities. Do not use for reusable agent-role/topology design, domain ownership decisions, ordinary bounded choices, or simple tasks that do not benefit from orchestration.
---

# Adaptive Workflow Orchestration

## Purpose

Turn an already-authorized objective into a bounded execution topology without changing domain ownership. Keep orchestration mechanics explicit in a validated plan and execution trace instead of relying on free-form model memory.

This skill owns **runtime orchestration for one task/run**. Use `agent-design` when the primary artifact is a reusable agent, supervisor/worker topology, authority model, or `.agent.md` definition.

## Ownership boundary

Own:

- task-specific strategy selection inside an existing authority envelope;
- work-unit decomposition, dependencies, barriers, and safe concurrency;
- read/write-set, isolation, retry, budget, and termination policy;
- `workflow-plan/v1` and backward-compatible `workflow-plan/v2` generation and validation;
- host-capability mapping and explicit degradation;
- plan/run evidence identity and orchestration-state discipline.

Do not own:

- choosing or redefining the domain owner;
- changing another skill/agent's authority or semantic contract;
- reusable custom-agent design or host-specific agent profiles;
- skill optimization, benchmarking, or evaluation ownership;
- bypassing host approvals, safety, permissions, or external-action authority.

## Core invariants

1. Use the simplest valid strategy. A single bounded worker is the default.
2. Resolve authority before topology. Parallelism never broadens authority.
3. Keep exactly one orchestration-state owner. Workers return results/evidence to that owner.
4. Validate dependencies and read/write conflicts before concurrent execution. Unknown overlap serializes.
5. Parallel mutation requires proven non-conflicting resources or explicit ordering. "Last answer wins" is forbidden.
6. Independent verification must be genuinely isolated when independence is part of the claim.
7. Every loop, retry, re-entry, worker count, and parallel branch is finite and budgeted.
8. Separate proposed plan generation from accepted plan execution.
9. Freeze the accepted plan before measured same-plan execution comparisons.
10. Preserve planner, input, accepted-plan, execution-trace, and evaluator identities separately when material.
11. Use native host capabilities when available; serial execution is the default safe degradation.
12. Missing required capability, authority, or evidence causes `blocked`/`escalated`, never invented support.

## Required inputs

Resolve or conservatively declare:

1. objective and terminal outcome;
2. current domain/phase owner and authority boundary;
3. work source or evidence from which units may be derived;
4. dependencies and shared resources;
5. available runtime capabilities;
6. success criteria and evaluator/verification source;
7. worker, parallelism, retry, re-entry, and loop budgets;
8. side-effect/write scope and reconciliation behavior;
9. evidence identities and trace requirements;
10. portability targets and allowed degradation.

Stop before executable planning when authority or a high-impact side effect is unresolved. Conservative assumptions are allowed only for topology details that do not expand authority.

## Strategy selection

Choose one primary strategy. Compose stages only when each added stage solves a distinct dependency or validation need.

| Strategy | Prefer when | Avoid when |
|---|---|---|
| `single` | cohesive task and shared context are useful | decomposition adds evidence or scale value |
| `sequential` | strict dependency/order or shared mutation | units are independent and read-mostly |
| `classify-route` | one bounded classification selects a known route | classification is open-ended exploration |
| `fan-out-synthesize` | independent read-mostly units feed one synthesis | work units contend on shared writes |
| `pipeline` | many units pass through the same ordered stages | each stage needs a global barrier |
| `adversarial-verify` | an independent challenger materially reduces false confidence | verifier cannot be isolated |
| `generate-filter` | several candidates are useful and filtering is reliable | diversity provides no value |
| `tournament` | alternatives can be compared by one frozen evaluator | evaluator is weak or changes between arms |
| `bounded-loop` | an objective predicate requires iteration | termination is subjective or unbounded |
| `gated-convergence` | small increments must prove required behavior/review gates before downstream work may consume them | a single bounded worker can finish and validate the task directly |

Load [references/orchestration-patterns.md](references/orchestration-patterns.md) for composition rules and anti-patterns.

## Portable plan contracts

Use `workflow-plan/v1` for existing material workflows. Use `workflow-plan/v2` only when checkpoint promotion and non-overridable quality gates are required. Load [references/workflow-plan-contract.md](references/workflow-plan-contract.md) for v1 and [references/workflow-plan-v2-contract.md](references/workflow-plan-v2-contract.md) for gated convergence. v1 remains supported and is not silently upgraded.

A valid plan includes:

- objective, success criteria, and authority;
- primary strategy;
- explicit stages with work source, dependencies, effects, read/write sets, and isolation;
- global/stage parallelism and finite budgets;
- failure/retry behavior and terminal states;
- required/optional capabilities plus degradation;
- source/planner/evaluator identities.

Use [assets/templates/workflow-plan.json.template](assets/templates/workflow-plan.json.template) with [schemas/workflow-plan.schema.json](schemas/workflow-plan.schema.json) for v1. For gated convergence use [assets/templates/workflow-plan-v2.json.template](assets/templates/workflow-plan-v2.json.template) with [schemas/workflow-plan-v2.schema.json](schemas/workflow-plan-v2.schema.json).

When Python 3 is available, validate every material plan before execution with [scripts/validate_workflow_plan.py](scripts/validate_workflow_plan.py):

```text
<PYTHON> scripts/validate_workflow_plan.py <PLAN.json> --json <REPORT.json>
```

The validator auto-detects v1/v2 and checks semantic invariants that JSON Schema alone cannot express, including dependency cycles, budget bounds, authority/write scope, independent verification isolation, unordered read/write conflicts, checkpoint DAGs, gate independence/capability requirements, bounded repairs, and promotion invariants.

## Supporting capability binding

Workflow capability ids describe **what the run needs**, not which external skill package must provide it. Keep `capabilities.required`, `capabilities.optional`, and gate `capability` values semantic and host-neutral. Do not encode vendor names, installation paths, model ids, or a fixed Rhapsodia skill catalog into the plan.

At execution time, the active worker resolves a semantic capability through the host's native Agent Skills discovery:

1. interpret the capability against the bounded work unit and active owner;
2. select the minimum matching installed skill(s) using their activation/scope contracts;
3. intersect supporting guidance with the active agent's existing authority, tools, write scope, criteria, and stop conditions;
4. required unresolved capability -> `blocked`; optional unresolved capability -> declared degradation/`not-run` only when semantics remain valid;
5. record the semantic capability and actual binding identity when the host exposes it, but do not rewrite the frozen workflow plan to pin that implementation.

A supporting skill never becomes the lifecycle owner and never grants authority. If its instructions conflict with the active agent/phase contract, the narrower active-agent authority wins.

## Workflow

1. **Normalize the objective.** State the authorized owner, terminal outcome, and success criteria.
2. **Resolve capabilities.** Record actual runtime primitives; do not infer support from another host.
3. **Map work.** Identify units, work source, dependencies, shared reads, writes, barriers, and isolation needs. Consume an existing Context Architect parallelization map when available.
4. **Select the least-complex strategy.** Use a bounded decision helper only when alternatives are explicit and genuinely tied; it does not own orchestration.
5. **Build the smallest contract.** Use `workflow-plan/v1` unless the task needs checkpoint promotion; use `workflow-plan/v2` with `gated-convergence` only for that case. Keep the authority envelope unchanged.
6. **Validate mechanically.** Reject invalid authority, conflicts, cycles, missing identities, or budget violations before dispatch.
7. **Freeze the accepted plan.** Record the validator-provided plan hash before measured/repeatability runs.
8. **Compile to native capabilities.** Use the strongest safe native host mechanism. Apply only declared degradation.
9. **Execute centrally.** Keep orchestration state in the parent/controller; workers receive only bounded context and authority.
10. **Verify independently when required.** Do not leak producer reasoning/history or evaluator-only answers into an independence claim. For gated convergence, bind every gate result to the current candidate identity.
11. **Promote only proven checkpoints.** A failed, blocked, invalid, stale, or not-run required gate cannot be overridden. Repair within budget and rerun affected gates; downstream checkpoints wait for promoted dependencies. Carry forward only explicitly accepted feedback/evidence with source identity.
12. **Terminate by evidence.** Stop on success predicate, explicit blocker/escalation, or exhausted budget.
13. **Report plan vs run.** Keep planned topology, actual trace, and final result identity separate.

## Parallelism and mutation

Load [references/parallelization-and-state.md](references/parallelization-and-state.md) whenever more than one stage may be runnable at once.

Minimum rules:

- parallel immutable reads are normally safe when source identity is frozen;
- any unordered pair with overlapping write/write or read/write resources is invalid;
- mutation outside the declared authority write scope is invalid;
- read-only stages must have an empty write set;
- mutating stages require a non-empty write set;
- global `max_parallel` and `max_workers` are hard ceilings;
- stage `max_parallel` cannot exceed either global ceiling;
- retries reconcile current state before repeating non-idempotent work;
- synthesis/merge begins only after its declared dependencies complete.

## Evidence and reproducibility

Load [references/evidence-and-reproducibility.md](references/evidence-and-reproducibility.md) when repeatability, benchmarking, verification independence, or cross-host comparison matters.

Treat these as distinct identities:

`input/source -> planner -> accepted plan -> execution trace -> evaluator -> result/artifact`

A changed plan invalidates a same-plan execution comparison. A changed evaluator invalidates an improvement comparison unless explicitly re-baselined.

## Portability

Load [references/host-portability.md](references/host-portability.md) when mapping a plan to OpenAI/ChatGPT, Codex, Claude, GitHub Copilot, VS Code, Cursor, Visual Studio, or another host.

The core requires semantic capabilities, not vendor APIs. Examples:

- `read-context`
- `invoke-specialist-agent`
- `parallelize-independent-work`
- `isolated-context`
- `run-bounded-process`
- `persist-workflow-state`

Optional capability loss may degrade to serial execution when semantics remain intact. Missing required capability is `blocked`.

## Stop conditions

Stop with `blocked` or `escalated` when:

- owner or authority cannot be resolved;
- work source/evidence needed for decomposition is missing;
- a required work pair has unresolved resource conflict with no safe ordering;
- a proposed stage mutates outside the allowed write scope;
- a required verifier/reviewer cannot satisfy declared independence;
- a gated-convergence checkpoint lacks current passing evidence for every required gate;
- a required gate capability is unavailable or a repair budget is exhausted;
- a loop/retry/re-entry branch is unbounded;
- required capability is unavailable and declared degradation changes semantics;
- required budget is undefined or exhausted;
- continuation requires ungranted destructive, privileged, production, identity/access, financial, or external-communication authority;
- completion, validation, trace, or host support would need to be fabricated.

## Output contract

For a substantive orchestration request return, as applicable:

1. objective and current authority owner;
2. selected strategy and why it is the least-complex valid option;
3. validated `workflow-plan/v1`, validated `workflow-plan/v2` for gated convergence, or a concise equivalent for trivial single-stage work;
4. plan validation status and plan SHA-256 when executed;
5. host capability/degradation mapping;
6. execution status/trace evidence when execution actually occurred;
7. terminal reason, remaining blockers, and residual unmeasured behavior.

Do not claim runtime execution from a structurally valid plan. Planned activation and boundary coverage lives in [evals/activation-scenarios.json](evals/activation-scenarios.json); treat it as planned evidence until a harness executes it.
