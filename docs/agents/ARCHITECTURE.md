# Rhapsodia Agent Architecture

## Purpose

This package adds a VS Code-first agent layer around the existing Nomia, Mago, and Magia Agent Skills. It preserves one centralized orchestration owner and one canonical writer per lifecycle phase while allowing bounded, isolated read-only work units when decomposition materially helps.

The architecture is native-first:

```text
user/request
    |
    v
Rhapsodia Supervisor
    |
    +--> Rhapsodia Analyst (optional read-only work units)
    |       +--> uses Nomia/Mago/Magia skill context as read-only guidance
    |
    +--> Nomia worker --> Nomia Skill
    |
    +--> Mago worker  --> Mago Skill
    |
    +--> Magia worker --> Magia Skill
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

Three distinct surfaces coexist:

1. `handoff/v1` - agent-layer delegation packet for canonical workers or analyst work units.
2. ecosystem handoff v3 - skill-layer evidence transfer between Nomia, Mago, and Magia domains.
3. optional `workflow-plan/v1` - task-specific orchestration plan owned by `adaptive-workflow-orchestration` when that skill is installed and useful.

The supervisor may inspect ecosystem handoff v3 but must never synthesize, repair, or rewrite it. The owning canonical skill generates and validates that envelope.

A workflow plan cannot change lifecycle ownership, tool authority, budgets, or the single-writer rules in this contract.

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

`adaptive-workflow-orchestration` is optional. When installed it can provide the portable strategy/dependency/budget plan. When absent the supervisor applies the same conservative gate directly and defaults to serial execution.

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

- maximum total subagent delegations: 12;
- maximum analyst work units per lifecycle phase: 4;
- maximum parallel analyst units when host-supported: 4;
- maximum re-entries to the same canonical owner: 2;
- materially identical canonical handoff repeats: 0;
- materially identical analyst work-unit repeats: 0.

Analyst units count toward the total delegation budget. A re-entry requires new evidence, changed state/artifact, completed repair, or new authorization. Budget exhaustion is escalation, not permission to continue guessing.

## Authority model

Capability is not authorization.

- Supervisor: `read`, `search`, `agent`; no edit/execute.
- Rhapsodia Analyst: `read`, `search`; no edit/execute/agent.
- Nomia: read/search/edit/execute only inside governance authority.
- Mago: read/search/edit/execute only for planning artifacts and planning validators; application tests/builds/deployments remain forbidden.
- Magia: read/search/edit/execute for bounded implementation and proof; production/release/external actions remain approval-gated and outside the normal lifecycle.

The host's approval and workspace-trust controls remain authoritative.

## Context policy

Do not load all skills into every worker context.

Canonical workers load only:

- their own Agent Skill;
- the compact parent delegation packet;
- valid incoming ecosystem handoff evidence when applicable;
- the minimum repository files required for the phase.

Rhapsodia Analyst loads only:

- one named domain skill as read-only guidance;
- one work-unit packet;
- the minimum evidence required for that unit.

This preserves context isolation and prevents a read-only work unit from inheriting unrelated write intent.

## Failure, cancellation, and partial results

When a hard blocker, invalidated source identity, revoked authority, or exhausted budget occurs:

1. stop dispatching new work units;
2. cancel pending analyst work when the host safely supports cancellation;
3. preserve already-completed evidence with its original work-unit/source identity;
4. do not treat a missing required unit as success;
5. reconcile uncertain canonical side effects before retrying a write-capable worker.

Parallelism is an optimization. Serial fallback is preferable to adding a third-party orchestration dependency.

## Recovery and resume

The supervisor does not create a separate durable orchestration database. It relies on canonical repository artifacts, stable workflow/handoff identities, the current session route trace, optional workflow-plan identity, analyst work-unit ids, and skill-owned ledgers/evidence when present.

On resume:

1. inspect canonical current state;
2. inspect the latest valid typed evidence;
3. resolve current owner;
4. discard stale/incomplete work units whose source identity no longer matches;
5. do not replay a completed side effect simply because conversation context is missing.

## Installation boundary

The RhapsodIA source package keeps canonical profiles in `agents/`. VS Code discovers workspace custom agents from `.github/agents/`, so installation copies the five `.agent.md` profiles to that destination. Documentation, tests, validators, and the portable contract remain source-package artifacts and do not need to be copied into the consuming repository.

Nomia, Mago, and Magia Agent Skills remain prerequisites. `adaptive-workflow-orchestration` is optional: installing it enables the reusable portable workflow-plan capability but is not required for the canonical serial lifecycle.

## Host boundary

The portable design/build contract is `docs/agents/contracts/rhapsodia-agent-system.json`. It validates the source package and future adapters, but it is not a runtime dependency in target repositories. Runtime authority comes from the installed custom-agent profiles plus the installed Nomia, Mago, and Magia Agent Skills.

The repository stores source profiles in `agents/*.agent.md`. For VS Code/Copilot use, copy those profiles into the target repository's `.github/agents/` discovery directory. Future adapters must translate capabilities and file conventions without changing ownership, authority, termination, single-writer, or evidence semantics.

No MCP server, LangGraph, CrewAI, AutoGen, Orca, or provider SDK is required by the core design.
