# Planning to Execution Handoff

Use this reference whenever MAGO creates, adapts, refines, or reshapes artifacts that downstream MAGIA execution may consume.

## Boundary Principle

MAGO owns planning authorship. MAGIA or another execution workflow owns implementation and runtime evidence. A MAGO planning boundary is not an implementation prohibition for downstream execution.

Do not write statements such as:

- implementation is forbidden merely due to MAGO authorship
- repository is planning-only
- implementation is deferred because the task requires code
- requires product implementation, therefore blocked

Use those ideas only when they are factual repository constraints supplied by evidence, not as consequences of MAGO ownership.

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

## Execution-Ready Task Rules

- Implementation-required tasks are valid MAGO planning outputs.
- Do not convert implementation work into a documentation-only confirmation unless the PRD and repository evidence prove no code is needed.
- Do not label a task `blocked` merely because it requires code.
- If the executor must decide among architecture alternatives, add or update technical-design.md first, then define bounded tasks.
- If a task relies on unknown repository files or dependencies, record the unknown as an explicit planning blocker or refinement task.
- Use `confirmation` tasks only for truthful no-op checks, not as a way to avoid implementation.

## Handoff Language

When handing off to MAGIA, use language like:

```text
MAGO has prepared the planning package and execution-ready task contract. Downstream MAGIA execution may implement code, configuration, tests, or documentation required by these tasks. MAGO has not executed the work or produced runtime evidence.
```

Avoid language like:

```text
This is planning-only, so product implementation is blocked.
```

## Validation

Before closing a MAGO run that changes tasks.md, technical-design.md, validation.md, or package handoff wording, verify:

- implementation tasks have concrete `Objective`, `Affected boundary`, `Validation`, and `Expected result` fields;
- no package text treats MAGO ownership as a prohibition against MAGIA implementation;
- blockers describe missing scope, files, dependencies, credentials, evidence, or validation paths, not the mere need for implementation;
- product-only modes did not create tasks; task-only modes did not rewrite product intent;
- `scripts/validate_planning_execution_handoff.py <skill-root>` passes for skill package changes.
