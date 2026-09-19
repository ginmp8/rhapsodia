# Planning to Execution Handoff

Use this reference whenever MAGO creates, adapts, refines, or reshapes artifacts that downstream MAGIA execution may consume.

## Boundary Principle

MAGO owns planning authorship. MAGIA or another execution workflow owns implementation and runtime evidence. A MAGO planning boundary is not an implementation prohibition for downstream execution.

Three-way boundary: nomia provides governance inputs and consumes delivery-facing evidence; MAGO converts approved or supplied intent into execution-ready technical plans; MAGIA executes and returns evidence. MAGO does not write stakeholder status or release communication, and it does not transform Magia evidence into MAGO-authored runtime proof.

Shared record boundary: MAGO writes cycle/spec identity, registry planning state, the plan (`tasks.md`, `validation.md`, `notes.md`, `manifest.yaml` planning defaults), and package structure. MAGIA writes execution reality (`implementation-notes.md`, `validation-evidence.md`, task checkbox completion, `manifest.yaml.last_execution`, and narrow technical execution-state sync backed by evidence). Generated catalog/queue projections are not shared writable state. Load `references/shared-artifact-ownership.md` when touching these files.

Do not write statements such as:

- implementation is forbidden merely due to MAGO authorship
- repository is planning-only
- downstream execution is required because the task needs code changes
- requires product implementation, therefore blocked

Use those ideas only when they are factual repository constraints supplied by evidence, not as consequences of MAGO ownership.

## Template Handoff

MAGO-authored templates and identity scripts create or normalize `cycle.yaml`, `registry/<spec_id>.yaml`, and planning-origin package files before execution. MAGIA consumes those generated files and writes execution evidence, but it must not create replacement planning scaffolds for missing registry records, `tasks.md`, `validation.md`, `notes.md`, or `manifest.yaml`. Missing or invalid shared planning structure is a MAGO refinement input, not a MAGIA scaffold task.

The catalog and define-queue files are renderer-owned external projections. Neither skill hand-edits them or uses them for execution-state synchronization.

## Handoff Contract

For implementation, integration, validation, hardening, migration, or rollout tasks, make the task executable by specifying the following through the existing task fields instead of adding noncanonical fields:

- `Objective`: concrete behavior or artifact to produce, not a broad product slogan.
- `Affected boundary`: repository-relative module, package, config, document, or system boundary expected to change; use `unknown` only when evidence truly cannot establish a boundary.
- `Task type`: phase-aligned executable type from the canonical enum.
- `Dependencies`: prior task ids that must be done first.
- `Validation`: observable command, validator, test, static check, or documented fallback that can prove the selected task.
- `Expected result`: concrete completion evidence the executor can verify.
- `Required LOAD` and `Optional LOAD`: specialist or reference files needed by the executor, or `none`.

If a task cannot name an affected boundary or validation path, split, refine, or block the planning output as under-specified. Do not mark implementation itself as the blocker.

## Reverse Handoff

When MAGIA reports `technical-gap-note.md`, implementation ADRs, validation gaps, or contradictions with code/runtime truth, MAGO may refine PRD interpretation, technical design, task definitions, dependencies, validation plans, registry handoff wording, or execution handoff wording. When MAGIA reports release posture, stakeholder risk, ownership, due date, accepted business risk, or go/no-go impact, route that evidence to nomia instead of updating delivery governance from MAGO.

## Execution-Ready Task Rules

- Execution-required tasks are valid MAGO planning outputs when implementation is explicitly handed off to Magia.
- Do not convert implementation work into a documentation-only confirmation unless the PRD and repository evidence prove no code is needed.
- Do not label a task `blocked` merely because it requires code.
- If the executor must decide among architecture alternatives, add or update technical-design.md first, then define bounded tasks.
- If a task relies on unknown repository files or dependencies, record the unknown as an explicit planning blocker or refinement task.
- Use `confirmation` tasks only for truthful no-op checks, not as a way to avoid implementation.

## Handoff Language

When handing off to MAGIA, use language like:

```text
MAGO has prepared the registry-backed planning package and execution-ready task contract for <spec_id>. Downstream MAGIA execution may implement code, configuration, tests, migrations, or documentation required by these tasks. MAGO has not executed the work or produced runtime evidence.
```

Avoid language like:

```text
This is planning-only, so product implementation is blocked.
```

## Validation

Before closing a MAGO run that changes tasks.md, technical-design.md, validation.md, notes.md, registry handoff, or package handoff wording, verify:

- cycle, registry, package directory, and manifest identities agree;
- spec dependencies resolve and remain acyclic;
- implementation tasks have concrete `Objective`, `Affected boundary`, `Validation`, and `Expected result` fields;
- no package text treats MAGO ownership as a prohibition against MAGIA implementation;
- blockers describe missing scope, files, dependencies, credentials, evidence, or validation paths, not the mere need for implementation;
- product-only modes did not create tasks; task-only modes did not rewrite product intent;
- generated views are not treated as authoritative or writable state;
- `scripts/validate_planning_execution_handoff.py <skill-root>` passes for skill package changes.
