---
name: adaptive-workflow-orchestration
description: Design and operate bounded task-specific execution workflows when runtime topology may adapt inside an already-authorized objective and domain owner. Use for runtime-discovered decomposition, classify-route, fan-out/synthesize, pipelines, adversarial verification, generate/filter, tournaments, bounded loops, dependency-aware parallelism, finite budgets, externalized runtime state, and compile-to-workflow execution. Do not use for checkpoint promotion/reference-grounded convergence (use checkpoint-convergence), reusable agent-role design (use agent-design), choosing domain ownership, skill optimization, or simple direct work that does not benefit from orchestration.
---

# Adaptive Workflow Orchestration

## Activation and Routing

Use only after the task objective **and** domain/phase owner are already authorized. This skill owns runtime orchestration for one task/run: choose or compile the smallest safe topology, bound concurrency/retries/loops, coordinate execution state, and keep plan/run evidence explicit.

Use it when runtime evidence may determine work units/topology or when classify-route, fan-out/synthesize, pipeline, adversarial verification, generate/filter, tournament, bounded-loop, or dependency-aware execution materially improves scale, isolation, or verification.

Do not use it to choose/redefine the domain owner, design reusable agents, optimize skills, bypass host approvals, or own checkpoint/oracle/gate promotion. New reference-grounded checkpoint progression routes to `checkpoint-convergence`; reusable supervisor/worker or `.agent.md` design routes to `agent-design`; otherwise prefer direct single/serial execution.

## Ownership Boundary

Own: task-specific strategy selection inside the existing authority envelope; work-unit/dependency/barrier design; read/write sets and isolation; finite worker/parallel/retry/re-entry/loop budgets; semantic capability requirements and safe degradation; plan validation/freeze; centralized runtime state; plan/run/evaluator identity separation.

Never broaden another owner/skill's semantic contract, production/destructive privilege, identity/access scope, financial authority, external-communication authority, or write scope.

## Quick-Start Workflow

1. **Normalize authority and outcome.** Record owner, terminal outcome, success criteria, allowed/forbidden effects, write scope, and high-impact side effects. Unresolved authority blocks executable planning.
2. **Map work and capabilities.** Identify work source, units, dependencies, shared resources, barriers, read/write sets, isolation needs, required/optional semantic capabilities, and actual host primitives.
3. **Choose the least-complex strategy.** Default to one bounded worker; add stages or parallelism only for a concrete dependency, scale, isolation, or verification need.
4. **Choose the contract.** New runtime-adaptive work -> `dynamic-workflow-plan/v1`; existing material `workflow-plan/v1` integrations may stay v1; historical `workflow-plan/v2` is validation/compatibility only; new checkpoint promotion -> `checkpoint-convergence` / `convergence-plan/v1`.
5. **Build the smallest bounded plan.** Include objective, authority, strategy, stages, dependencies, effects, read/write sets, isolation, finite budgets, termination, capabilities/degradation, and input/planner/evaluator identities.
6. **Validate before dispatch.** Reject cycles, authority/write-scope violations, missing finite budgets, unresolved unordered read/write conflicts, invalid verifier isolation, or missing required evidence/capability.
7. **Freeze the accepted plan.** Bind measured/repeatability claims to the validated plan hash; a changed plan is a different comparison subject.
8. **Compile to native capabilities.** Prefer the strongest safe host-native mechanism; optional capability loss may degrade only when semantics stay intact. Missing required capability is `blocked`.
9. **Execute centrally.** One parent/controller owns orchestration state, intermediate-result integration, budgets, retries, cancellation, and termination; workers receive only bounded context/authority.
10. **Verify and terminate by evidence.** Preserve verifier isolation when claimed, revalidate mutable state when required, stop on success/blocker/budget exhaustion, and separate planned topology from actual trace/result.

## Non-Negotiable Invariants

1. Authority is resolved before topology; parallelism never expands authority.
2. The simplest valid strategy wins; single bounded execution is the default.
3. Exactly one orchestration-state owner coordinates workers and evidence.
4. Unknown resource overlap serializes; unordered read/write or write/write conflicts are invalid.
5. Parallel mutation requires proven non-conflicting resources or explicit ordering; "last answer wins" is forbidden.
6. Every worker count, branch, loop, retry, and re-entry is finite and budgeted.
7. Proposed-plan generation and accepted-plan execution are distinct states.
8. Independent verification requires real isolation; isolated contexts are not automatically independent truth sources.
9. Keep input/source, planner, accepted-plan, execution-trace, evaluator, and result identities distinct when material.
10. Runtime limits/state belong to deterministic/runtime mechanisms when available; prompts do not prove enforcement.
11. Capability ids are semantic and late-bound; vendor/package/model names do not belong in portable plan requirements.
12. Missing authority, capability, evidence, safe ordering, or required finite budget yields `blocked`/`escalated`, never invented support.

## Strategy Router

| Strategy | Use when | Do not use when |
|---|---|---|
| `single` | cohesive bounded work; shared context helps | decomposition adds real evidence/scale value |
| `sequential` | strict order or shared mutation | units are independent/read-mostly |
| `classify-route` | one bounded classification selects a known route | routing is open-ended exploration |
| `fan-out-synthesize` | independent read-mostly units feed one synthesis | branches contend on shared writes |
| `pipeline` | many units traverse the same ordered stages | each stage needs a global barrier |
| `adversarial-verify` | isolated challenge materially reduces false confidence | verifier cannot be isolated |
| `generate-filter` | candidate diversity plus reliable filtering has value | diversity adds no decision value |
| `tournament` | alternatives share one frozen evaluator | evaluator is weak or drifts |
| `bounded-loop` | an objective predicate justifies finite iteration | termination is subjective/unbounded |

## Stop-Before-Dispatch Gate

Do not dispatch if owner/authority or a high-impact side effect is unresolved; the work source is missing; resources conflict without safe ordering; mutation exceeds write scope; required isolation/capability/evidence is unavailable; any worker/branch/retry/re-entry/loop budget is unbounded/undefined; or success would require fabricating execution, durability, independence, validation, or host support.

## Direct Resource Map

- New adaptive-plan semantics and hard ceilings -> [dynamic plan contract](references/dynamic-workflow-plan-contract.md); compile/resume/durability/verification runtime semantics -> [dynamic workflow runtime](references/dynamic-workflow-runtime.md).
- Strategy choice or anti-pattern uncertainty -> [orchestration patterns](references/orchestration-patterns.md).
- **Mandatory when more than one stage may run concurrently** -> [parallelization and state](references/parallelization-and-state.md) for conflict, state, retry, cancellation, and merge rules.
- Existing `workflow-plan/v1` only -> [workflow-plan/v1](references/workflow-plan-contract.md); historical v2 validation only -> [workflow-plan/v2](references/workflow-plan-v2-contract.md).
- Repeatability, evaluator freeze, verification independence, or comparison claims -> [evidence and reproducibility](references/evidence-and-reproducibility.md).
- Cross-host execution or degradation decisions -> [host portability](references/host-portability.md).
- Historical checkpoint-convergence compatibility pointer only -> [reference-grounded convergence](references/reference-grounded-convergence.md).

## Minimum Output Evidence

For substantive orchestration, report objective/owner, least-complex selected strategy, plan contract/version, validation status and plan hash when validated, host capability/degradation mapping, actual execution trace only when execution occurred, and terminal reason/blockers. Structural validity is never runtime-execution evidence.

## Required Inputs

Resolve or conservatively declare:

1. objective and terminal outcome;
2. current domain/phase owner and authority boundary;
3. work source/evidence from which units may be derived;
4. dependencies and shared resources;
5. available runtime capabilities;
6. success criteria and evaluator/verification source;
7. worker, parallelism, retry, re-entry, loop, and total-agent budgets where applicable;
8. side-effect/write scope and reconciliation behavior;
9. evidence identities and trace requirements;
10. portability targets and allowed degradation.

Stop before executable planning when authority or a high-impact side effect is unresolved. Conservative assumptions are allowed only for topology details that do not expand authority.

## Plan Contracts

### `dynamic-workflow-plan/v1` — default for new adaptive work

Use when work units/topology are discovered at runtime, isolated fan-out materially helps, or a bounded loop/pipeline is compiled from current evidence. The model may choose topology, but deterministic/runtime mechanisms own hard ceilings, dependency execution, intermediate state, retries, and trace identity.

The contract distinguishes:

- `max_parallel`: simultaneous execution ceiling;
- `max_workers`: worker-pool ceiling;
- `max_total_agents`: total agent invocation ceiling;
- `resumption_semantics: session-replay`: resumable session/cache semantics, not durable workflow execution;
- `resumption_semantics: durable-external`: valid only when a real durable-state capability exists;
- deterministic-first verification from model criticism;
- context isolation from epistemic independence.

Validate with:

```text
<PYTHON> scripts/validate_dynamic_workflow.py <PLAN.json>
```

Use [assets/templates/dynamic-workflow-plan.json.template](assets/templates/dynamic-workflow-plan.json.template) with [schemas/dynamic-workflow-plan.schema.json](schemas/dynamic-workflow-plan.schema.json).

### `workflow-plan/v1` — supported compatibility contract

Retain for existing material workflows already using it; do not silently upgrade. A valid plan contains objective/success criteria/authority, one primary strategy, explicit stages and dependencies, effects/read-write sets/isolation, finite budgets, failure/termination behavior, semantic capabilities/degradation, and input/planner/evaluator identities.

Use [assets/templates/workflow-plan.json.template](assets/templates/workflow-plan.json.template) with [schemas/workflow-plan.schema.json](schemas/workflow-plan.schema.json), then validate with:

```text
<PYTHON> scripts/validate_workflow_plan.py <PLAN.json> --json <REPORT.json>
```

### `workflow-plan/v2` — historical gated-convergence compatibility only

Continue to validate existing `workflow-plan/v2` integrations with [references/workflow-plan-v2-contract.md](references/workflow-plan-v2-contract.md), [assets/templates/workflow-plan-v2.json.template](assets/templates/workflow-plan-v2.json.template), and [schemas/workflow-plan-v2.schema.json](schemas/workflow-plan-v2.schema.json). Do not create new checkpoint-promotion work under this skill; use `checkpoint-convergence`.

The workflow-plan validator auto-detects v1/v2 and checks semantic invariants beyond JSON Schema, including dependency cycles, budget bounds, authority/write scope, verification isolation, unordered conflicts, checkpoint/gate consistency, bounded repairs, and promotion invariants for legacy v2 inputs.

## Supporting Capability Binding

Workflow capability ids describe **what the run needs**, not which external package must provide it. Keep `capabilities.required`, `capabilities.optional`, and gate capability values semantic and host-neutral; do not encode vendor names, installation paths, model ids, or a fixed RhapsodIA catalog.

At execution time:

1. interpret the capability against the bounded work unit and active owner;
2. select the minimum matching installed/native capability through host discovery;
3. intersect supporting guidance with the active authority, tools, write scope, criteria, and stop conditions;
4. required unresolved capability -> `blocked`; optional unresolved capability -> declared degradation/`not-run` only when semantics remain valid;
5. record actual binding identity when exposed, without rewriting the frozen plan to pin that implementation.

A supporting skill never becomes lifecycle owner and never grants authority. If guidance conflicts, the narrower active owner/phase authority wins.

## Detailed Execution Rules

### Parallelism and mutation

Load [references/parallelization-and-state.md](references/parallelization-and-state.md) whenever more than one stage may be runnable at once.

- Parallel immutable reads are normally safe when source identity is frozen.
- Any unordered pair with overlapping write/write or read/write resources is invalid.
- Mutation outside declared authority write scope is invalid.
- Read-only stages have an empty write set; mutating stages require a non-empty write set.
- Global `max_parallel`/`max_workers` are hard ceilings; stage parallelism cannot exceed them.
- Retries reconcile current state before repeating non-idempotent work.
- Synthesis/merge begins only after declared dependencies complete.

### Verification and reproducibility

Load [references/evidence-and-reproducibility.md](references/evidence-and-reproducibility.md) when repeatability, benchmarking, verification independence, or cross-host comparison matters.

Treat these identities separately:

`input/source -> planner -> accepted plan -> execution trace -> evaluator -> result/artifact`

A changed plan invalidates a same-plan comparison. A changed evaluator invalidates an improvement comparison unless explicitly re-baselined. Persisted ledgers, summaries, and feedback are evidence claims, not live operational truth; revalidate mutable state according to the accepted freshness policy.

### Portability

Load [references/host-portability.md](references/host-portability.md) when mapping to OpenAI/ChatGPT, Codex, Claude, GitHub Copilot, VS Code, Cursor, Visual Studio, or another host.

The core requires semantic capabilities such as `read-context`, `invoke-specialist-agent`, `parallelize-independent-work`, `isolated-context`, `run-bounded-process`, and `persist-workflow-state`. Optional capability loss may degrade to serial execution only when semantics remain intact. Missing required capability is `blocked`.

## Composition with Checkpoint Convergence

Exactly one **progression owner** decides whether checkpointed work advances.

- Adaptive orchestration may gather read-only evidence or execute a bounded subflow for one convergence checkpoint, then return evidence.
- `checkpoint-convergence` retains oracle/gate/promotion ownership when it requests such a subflow.
- An adaptive subflow cannot promote a checkpoint, relax its oracle, or create a second promotion graph.
- `checkpoint-convergence` cannot silently take over unrelated runtime topology outside its declared checkpoint scope.
- If neither dynamic topology nor checkpoint promotion is needed, use direct single/serial execution.

## Stop Conditions

Stop with `blocked` or `escalated` when:

- owner/authority cannot be resolved;
- decomposition evidence/work source is missing;
- required work has unresolved resource conflict with no safe ordering;
- a stage mutates outside allowed write scope;
- required verifier/reviewer cannot satisfy declared isolation;
- a loop/retry/re-entry/worker branch is unbounded;
- required capability is unavailable and degradation would change semantics;
- a finite required budget is undefined or exhausted;
- continuation needs ungranted destructive, privileged, production, identity/access, financial, or external-communication authority;
- completion, validation, execution trace, durability, independence, or host support would need to be fabricated.

## Output Contract

For a substantive orchestration request return, as applicable:

1. objective and current authority owner;
2. selected strategy and why it is the least-complex valid option;
3. validated `dynamic-workflow-plan/v1` for new adaptive work, compatible `workflow-plan/v1`/historical v2 only when actually required, or a concise equivalent for trivial single-stage work;
4. plan validation status and plan SHA-256 when executed;
5. host capability/degradation mapping;
6. execution status/trace evidence only when execution actually occurred;
7. terminal reason, blockers, and residual unmeasured behavior.

Do not claim runtime execution from a structurally valid plan. Planned activation/boundary coverage in [evals/activation-scenarios.json](evals/activation-scenarios.json) remains planned evidence until a harness executes it.
