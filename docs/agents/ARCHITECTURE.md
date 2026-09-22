# Rhapsodia Agent Architecture

## Purpose

This package adds a VS Code-first agent layer around the existing Nomia, Mago, and Magia Agent Skills. It does not merge the three skills and does not create a fourth domain-writing capability.

The architecture is native-first:

```text
user/request
    |
    v
Rhapsodia Supervisor
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
- compact delegation packets;
- route trace and finite budgets;
- transition validation;
- cycle detection;
- final integration summary;
- escalation.

Does not own:

- governance artifacts;
- requirements/design/tasks;
- product code/tests;
- ecosystem handoff v3 construction;
- business-risk acceptance;
- deployment/release authority.

### Nomia worker

Owns one product/delivery-governance phase through the Nomia Skill.

### Mago worker

Owns one technical-planning or reconciliation phase through the Mago Skill.

### Magia worker

Owns one bounded repository execution phase through the Magia Skill. Direct ADHOC entry is allowed only outside governed board/package work and only with explicit scope and proof.

## Why delegation instead of worker-to-worker handoff

The supervisor retains orchestration ownership and workers return results. This is delegation, not ownership transfer.

Two distinct contracts coexist:

1. `handoff/v1` is the agent-layer delegation packet. It carries only the context a worker needs.
2. ecosystem handoff v3 is the skill-layer evidence-transfer contract between Nomia, Mago, and Magia.

The supervisor may inspect ecosystem handoff v3 but must never synthesize, repair, or rewrite it. The owning skill generates and validates that envelope.

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

## Routing budgets

The default routing contract is intentionally finite:

- maximum specialist delegations: 12;
- maximum re-entries to the same owner: 2;
- materially identical handoff repeats: 0.

A re-entry requires new evidence, changed state/artifact, completed repair, or new authorization. Budget exhaustion is escalation, not permission to continue guessing.

## Authority model

Capability is not authorization.

The worker tool lists expose the minimum host capabilities required by the role, while the Agent Skill determines the semantic scope of those capabilities.

- Supervisor: read/search/delegate only.
- Nomia: read/search/edit/execute only inside governance authority.
- Mago: read/search/edit/execute only for planning artifacts and planning validators; application tests/builds/deployments remain forbidden.
- Magia: read/search/edit/execute for bounded implementation and proof; production/release/external actions remain approval-gated and outside the normal lifecycle.

The host's own approval and workspace-trust controls remain authoritative.

## Context policy

Do not load all three skills into every worker context.

Each worker loads only:

- its own Agent Skill;
- the compact parent delegation packet;
- valid incoming ecosystem handoff evidence when applicable;
- the minimum repository files required for the current phase.

This prevents context flooding and reduces cross-owner instruction drift.

## Recovery and resume

The supervisor itself does not create a new durable orchestration database. It relies on canonical repository artifacts, stable workflow/handoff identities, the current session route trace, and skill-owned ledgers/evidence when present.

On resume:

1. inspect canonical current state;
2. inspect the latest valid typed evidence;
3. resolve current owner;
4. do not replay a completed side effect simply because conversation context is missing.

## Installation boundary

The RhapsodIA source package keeps canonical profiles in `agents/`. VS Code discovers workspace custom agents from `.github/agents/`, so installation copies only the four `.agent.md` profiles to that destination. Documentation, tests, validators, and the portable contract remain source-package artifacts and do not need to be copied into the consuming repository.

The three Agent Skills are prerequisites and are intentionally not bundled here. They must already be discoverable from one supported project skill root (`.github/skills/`, `.claude/skills/`, or `.agents/skills/`).

## Host boundary

The portable design/build contract is `docs/agents/contracts/rhapsodia-agent-system.json`. It validates the source package and future adapters, but it is not a runtime dependency in target repositories. Runtime authority comes from the installed custom-agent profiles plus the installed Nomia, Mago, and Magia Agent Skills.

The repository stores the source profiles in `agents/*.agent.md`. For VS Code/Copilot use, copy those profiles into the target repository's `.github/agents/` discovery directory. Future adapters must translate capabilities and file conventions without changing ownership, authority, termination, or evidence semantics.

No MCP server, LangGraph, CrewAI, AutoGen, Orca, or provider SDK is required by the core design.
