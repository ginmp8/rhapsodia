# Rhapsodia Agent Architecture

## Artifact-native default (agent-system-contract/v3)

Domain agents decide which files their own skill needs. The Supervisor selects the current owner, not filenames. All three workers return uniform `artifact_actions` and a separate action-validation result. Their canonical roots are independently owned (`docs/product`, `docs/specs`, `docs/implementation`, or explicit non-overlapping alternatives). Board/cycle/registry setup is not a native requirement.

`Rhapsodia Workspace` is a seventh, derived-only profile. Invoke it only for an explicit catalog/UI request after canonical writers stop. It can index, validate, project and render under `.rhapsodia`, but cannot create source sidecars, write domain files, advance lifecycle, mint planning identity or emit ecosystem v3 handoffs. Its absence does not prevent a domain phase from running. Requested UI output must still complete before claiming the user's whole request is complete.

The original Nomia/Mago/Magia ownership and typed v3 handoff directions remain intact. Read-only Analyst fan-out and independent Verifier checkpoints are unchanged. Workspace counts toward the same 24-hop budget and has at most one retry after a source change. No framework, external orchestration service, watcher or Board runtime is introduced.

See [artifact orchestration](ARTIFACT-ORCHESTRATION.md) for data contracts, migration, validation and operation. Existing Board examples elsewhere are explicit legacy compatibility, not default storage prerequisites.


## Purpose

This package adds a portable semantic agent layer with a validated VS Code adapter around the Nomia, Mago, Magia, and test-oracle-engineering Agent Skills. It preserves one centralized orchestration owner and one canonical production writer per lifecycle phase while allowing bounded isolated analysis, adversarial review, and executable verification when they materially reduce false confidence.

The architecture is native-first:

```text
user/request
    |
    v
Rhapsodia Supervisor
    |
    +--> Rhapsodia Analyst (read-only analysis / adversarial review)
    |       +--> uses Nomia/Mago/Magia skill context as read-only guidance
    |
    +--> Rhapsodia Verifier (independent executable proof)
    |       +--> test-oracle-engineering Skill
    |
    +--> Nomia worker --> Nomia Skill
    |
    +--> Mago worker  --> Mago Skill
    |
    +--> Magia worker --> Magia Skill (producer / production repair)
```

The VS Code adapter uses native custom agents and native subagent delegation. No external orchestration runtime is required.

## Responsibility split

### Supervisor

Owns:

- current-owner resolution;
- lifecycle routing;
- task-specific atomic-vs-decomposable decision;
- compact delegation/work-unit packets;
- route/work-unit trace and finite budgets;
- transition validation;
- cycle detection;
- final integration/synthesis;
- escalation.

Does not own:

- governance artifacts;
- requirements/design/tasks;
- product code/tests;
- ecosystem handoff v3 construction;
- business-risk acceptance;
- deployment/release authority.

### Rhapsodia Analyst

Owns one isolated **read-only** work unit. It may inspect evidence, answer a bounded question, or independently challenge a result while using the named Nomia/Mago/Magia skill as read-only domain guidance.

It never owns a canonical lifecycle phase and cannot:

- edit files;
- execute commands;
- emit ecosystem handoff v3;
- complete a canonical phase;
- change governance/planning/implementation authority;
- invoke another agent.

This separate profile exists because current host custom-agent tool lists can mechanically enforce `read`/`search` only, instead of relying on a write-capable worker to obey a prompt-only read-only convention.

### Rhapsodia Verifier

Owns one independent executable proof unit for a Magia candidate/checkpoint. It uses `test-oracle-engineering`, may write only explicitly declared verification/test artifacts, and may run bounded proof commands. It cannot repair production code, change acceptance criteria, emit ecosystem handoff v3, or promote a checkpoint.

This separation prevents the producer from being the sole judge of its own implementation while keeping verification authority narrower than Magia's production authority.

### Nomia worker

Owns one product/delivery-governance phase through the Nomia Skill.

### Mago worker

Owns one technical-planning or reconciliation phase through the Mago Skill.

### Magia worker

Owns one bounded repository execution phase through the Magia Skill. Direct ADHOC entry is allowed only outside governed board/package work and only with explicit scope and proof.

## Why the analyst is separate

Adaptive decomposition is justified only for distinct context isolation, independent verification, or independent read-only work. Nomia, Mago, and Magia all have edit/execute capabilities because their canonical phases may mutate owned artifacts or run validators. Running several of those profiles concurrently would violate least privilege and single-writer ownership even if the prompt told them to remain read-only.

`Rhapsodia Analyst` solves that with an explicit host-enforced read-only toolset. One analyst profile can apply the already-resolved domain skill context without creating three duplicate read-only domain agents.

## Delegation versus evidence transfer

The supervisor retains orchestration ownership and workers return results. This is delegation, not ownership transfer.

Four distinct surfaces coexist:

1. `handoff/v1` - agent-layer delegation packet for canonical workers, analyst units, or verifier units.
2. ecosystem handoff v3 - skill-layer evidence transfer between Nomia, Mago, and Magia domains.
3. optional `workflow-plan/v1` or `workflow-plan/v2` - task-specific orchestration plans owned by `adaptive-workflow-orchestration`; v2 is reserved for gated convergence.
4. `test-oracle-spec/v1` / `test-oracle-proof/v1` - executable proof contracts owned by `test-oracle-engineering`.

The supervisor may inspect ecosystem handoff v3 but must never synthesize, repair, or rewrite it. The owning canonical skill generates and validates that envelope.

A workflow plan cannot change lifecycle ownership, tool authority, budgets, or the single-writer rules in this contract.

## Supporting semantic capabilities

Rhapsodia distinguishes **canonical domain skills** from **supporting Agent Skills**. Nomia, Mago, Magia, and `test-oracle-engineering` remain the canonical skill owners for their phases. Any other installed Agent Skill is optional supporting guidance unless another explicit package contract says otherwise.

Supporting skills are resolved **at runtime by semantic capability**, not by a fixed repository catalog:

1. the Supervisor or accepted `workflow-plan` declares required/optional semantic capability ids;
2. the active worker uses the host's native Agent Skills discovery to find the minimum matching skill(s);
3. the worker intersects that guidance with its existing authority, tools, owner, write scope, acceptance criteria, handoff directions, and stop conditions;
4. a required unresolved capability blocks the affected unit; an optional unresolved capability may be `not-run`/degraded only when semantics remain intact;
5. the result records semantic capability status and, when the host exposes it, the actual skill identity used as execution evidence.

There is intentionally **no external-skill allowlist, package-name mapping, vendor mapping, or installation-path dependency** in the portable contract. Supporting skills are not subagents and must not be added to the VS Code `agents:` allowlist. Their instructions cannot change lifecycle ownership or grant authority the active agent does not already have.

## Canonical governed lifecycle

```text
Nomia intake/governance
        |
        v
Mago technical planning
        |
        v
Magia implementation/validation
        |
        v
Mago reconciliation
        |
        +--> Magia repair/re-execution (bounded)
        |
        v
Nomia closure
```

A workflow may start in the middle when canonical repository evidence already proves the active phase. Completed phases are not replayed merely to satisfy the diagram.

Adaptive work units are **inside one box** in this lifecycle. They never create a second lifecycle or move ownership sideways.

Inside the Magia box, a gated-convergence plan may use:

```text
Magia candidate
    -> Rhapsodia Verifier executable proof
    -> Rhapsodia Analyst adversarial review(s)
    -> optional perceptual/human gate
    -> promote checkpoint OR return failed evidence to Magia for bounded repair
```

A required gate is non-overridable. A repaired candidate invalidates every affected gate result and those gates rerun before promotion. A dependent checkpoint cannot start until its dependencies are promoted.

## Adaptive execution model

The default is still one canonical worker.

A phase may be decomposed only when:

- the domain owner is already resolved;
- work units are independent read-only analysis/verification;
- every unit can run under `Rhapsodia Analyst` with `read`/`search` only;
- dependencies and source identities are explicit enough to integrate safely;
- the supervisor remains the only orchestration-state owner;
- any canonical write/validator/phase completion/handoff v3 still goes through one Nomia/Mago/Magia worker;
- total and per-phase work-unit budgets remain finite;
- serial fallback preserves semantics when parallel scheduling is unavailable.

`adaptive-workflow-orchestration` is optional. When installed it can provide the portable v1 strategy/dependency/budget plan or the v2 gated-convergence checkpoint plan. When absent the supervisor applies the conservative single/serial rules directly and must not improvise an unbounded checkpoint graph.

### Safe example

```text
Mago phase
  -> Analyst unit A: inspect API consumers (read-only)
  -> Analyst unit B: inspect migration risks (read-only)
  -> Analyst unit C: challenge validation gaps (read-only)
  -> Supervisor synthesizes evidence
  -> ONE Mago worker updates canonical planning artifacts
```

### Rejected example

```text
Mago writer A ----\
Mago writer B -----+--> concurrent edits / last-writer-wins
Mago writer C ----/
```

Write-capable canonical worker fan-out is not allowed.

## Routing budgets

The routing contract is finite:

- maximum total subagent delegations: 24;
- maximum analyst work units per lifecycle phase: 4;
- maximum parallel analyst units when host-supported: 4;
- maximum gated checkpoints per Magia phase: 4;
- maximum checkpoint repairs after an initial candidate: 2;
- maximum adversarial Analyst reviews per checkpoint: 2;
- maximum Verifier proof units per candidate attempt: 1;
- maximum ordinary re-entries to the same canonical owner: 2;
- materially identical canonical handoff/analyst/verifier repeats: 0.

Analyst units count toward the total delegation budget. A re-entry requires new evidence, changed state/artifact, completed repair, or new authorization. Budget exhaustion is escalation, not permission to continue guessing.

## Authority model

Capability is not authorization.

- Supervisor: `read`, `search`, `agent`; no edit/execute.
- Rhapsodia Analyst: `read`, `search`; no edit/execute/agent.
- Rhapsodia Verifier: `read`, `search`, `edit`, `execute`; edit is restricted to verification-only scope, execute to bounded oracle proof, and production repair/delegation are forbidden.
- Nomia: read/search/edit/execute only inside governance authority.
- Mago: read/search/edit/execute only for planning artifacts and planning validators; application tests/builds/deployments remain forbidden.
- Magia: read/search/edit/execute for bounded implementation and proof; production/release/external actions remain approval-gated and outside the normal lifecycle.

The host's approval and workspace-trust controls remain authoritative.

## Context policy

Do not load all skills into every worker context.

Canonical workers load only:

- their own canonical Agent Skill;
- the compact parent delegation packet;
- valid incoming ecosystem handoff evidence when applicable;
- the minimum repository files required for the phase;
- only the minimum supporting Agent Skills needed to satisfy declared semantic capabilities, resolved natively at runtime.

Rhapsodia Analyst loads only:

- one named canonical domain skill as read-only guidance;
- one work-unit/review packet;
- the frozen candidate/source/rubric needed for that unit;
- only declared supporting semantic capabilities, still constrained to read/search authority.

Rhapsodia Verifier loads only:

- `test-oracle-engineering`;
- one verifier-unit packet;
- the exact candidate/source/oracle identity;
- the minimum repository/runtime evidence needed to execute the proof;
- only gate-declared supporting semantic capabilities, constrained to verification authority.

Do not preload all installed skills. Do not maintain a Rhapsodia catalog of external skill names. Capability binding belongs to the active host/worker and must preserve the agent-system authority envelope.

This preserves context isolation, avoids self-preferential review, and prevents verification from inheriting production repair authority.

## Failure, cancellation, and partial results

When a hard blocker, invalidated source identity, revoked authority, or exhausted budget occurs:

1. stop dispatching new work units;
2. cancel pending analyst/verifier work when the host safely supports cancellation;
3. preserve already-completed evidence with its original work-unit/source identity;
4. do not treat a missing/failed/blocked required gate or work unit as success;
5. reconcile uncertain canonical side effects before retrying a write-capable worker.

Parallelism is an optimization. Serial fallback is preferable to adding a third-party orchestration dependency.

## Recovery and resume

The supervisor does not create a separate durable orchestration database. It relies on canonical repository artifacts, stable workflow/handoff identities, the current session route trace, optional workflow-plan/checkpoint/candidate identities, analyst/verifier work-unit ids, and skill-owned ledgers/evidence when present.

On resume:

1. inspect canonical current state;
2. inspect the latest valid typed evidence;
3. resolve current owner;
4. discard stale/incomplete work units whose source identity no longer matches;
5. do not replay a completed side effect simply because conversation context is missing.

## Installation boundary

The RhapsodIA source package keeps canonical profiles in `agents/`. VS Code discovers workspace custom agents from `.github/agents/`, so installation copies the six `.agent.md` profiles to that destination. Documentation, tests, validators, and the portable contract remain source-package artifacts and do not need to be copied into the consuming repository.

Nomia, Mago, Magia, and `test-oracle-engineering` Agent Skills are prerequisites for the full six-agent adapter. `adaptive-workflow-orchestration` is optional: installing it enables the reusable portable workflow-plan capability but is not required for the canonical serial lifecycle. Additional Agent Skills may be installed independently and discovered as supporting semantic capabilities; they are not Rhapsodia package prerequisites and are never enumerated in the portable contract.

## Host boundary

The portable design/build contract is `docs/agents/contracts/rhapsodia-agent-system.json`. It validates the source package and future adapters, but it is not a runtime dependency in target repositories. Runtime authority comes from the installed custom-agent profiles plus the installed Nomia, Mago, Magia, and test-oracle-engineering Agent Skills. `perceptual-validation` is an optional capability when a plan includes a perceptual gate.

The repository stores source profiles in `agents/*.agent.md`. For VS Code/Copilot use, copy those profiles into the target repository's `.github/agents/` discovery directory. The JSON contract is the portable semantic core. Future/adapted host profiles for OpenAI/ChatGPT, Codex, Claude, GitHub Copilot, Cursor, Visual Studio, or other hosts must translate capabilities and discovery conventions without changing ownership, authority, termination, producer/verifier separation, gate-promotion, single-writer, or evidence semantics. Structural portability is not a claim of runtime parity.

No MCP server, LangGraph, CrewAI, AutoGen, Orca, or provider SDK is required by the core design.

## Reference-grounded convergence

For high-risk work with a strong existing reference, the Supervisor may compile the current lifecycle phase into small ordered checkpoints. Each checkpoint can bind a narrow reference scope and a candidate-independent oracle identity before Magia produces code. Required gates execute in declared order; repair returns to Magia; affected proof is rerun; dependent checkpoints wait for promotion.

The system intentionally does not implement hidden long-term agent memory. Cross-checkpoint learning is explicit evidence: accepted feedback with provenance, current candidate/reference identities, and checkpoint status. Mutable source state is revalidated when the plan declares it. This prevents stale ledgers or long transcripts from silently becoming operational truth.

Autonomous mode is a policy choice, not a lower quality tier. It may reduce human approval frequency only when explicitly accepted; required proof/review/freshness gates remain invariant.
