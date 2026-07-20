# Planning to Execution Handoff

Use this reference whenever MAGO creates, adapts, refines, or reshapes artifacts that downstream MAGIA execution may consume.

## Boundary Principle

MAGO owns planning authorship. MAGIA owns implementation and runtime evidence. A MAGO planning boundary is not an implementation prohibition for downstream execution.

The three-way boundary is:

- nomia provides governance inputs and consumes delivery-facing evidence;
- MAGO converts supplied intent and repository evidence into execution-ready technical plans;
- MAGIA executes those plans and returns implementation/validation evidence.

MAGO writes planning defaults and task contracts. MAGIA writes execution reality: `implementation-notes.md`, `validation-evidence.md`, task checkbox completion, `manifest.yaml.last_execution`, and evidence-backed execution-state synchronization. Load `references/shared-artifact-ownership.md` whenever shared files are touched.

Do not write statements that imply implementation is forbidden merely because MAGO authored the package, or that a task is blocked merely because it requires code. Those are valid only when supported by an actual repository constraint.

## Identity and Template Handoff

MAGO creates or normalizes `cycle.yaml`, `registry/<spec_id>.yaml`, `manifest.yaml`, `tasks.md`, `validation.md`, `notes.md`, and other planning artifacts. MAGIA consumes those files but must not invent missing cycle/spec identities, registry records, package scaffolds, task definitions, or validation plans.

Generated `spec-catalog.yaml` and `define-queue.yaml` are external projections only. They are never shared writable state and must not be used for execution-state synchronization.

## Handoff Contract

For implementation, integration, validation, hardening, migration, or rollout tasks, use the canonical fields in `tasks.md`:

- `Objective`: concrete behavior or artifact to produce;
- `Affected boundary`: repository-relative module, package, config, document, or system boundary;
- `Task type`: phase-aligned executable type;
- `Dependencies`: existing prior task IDs;
- `Validation`: observable command, validator, test, static check, or documented fallback;
- `Expected result`: verifiable completion evidence;
- `Required LOAD` and `Optional LOAD`: specialist/reference inputs or `none`.

If a task cannot name an affected boundary or validation path, split, refine, or block it as under-specified. Do not mark implementation itself as the blocker.

## Execution-Ready Task Rules

- Execution-required tasks are valid MAGO planning outputs when implementation is explicitly handed off to MAGIA.
- Do not convert real implementation work into a documentation-only confirmation unless product and repository evidence prove no change is required.
- Do not label a task `blocked` merely because it requires code.
- If the executor must choose among material architecture alternatives, update the planned technical design or ADR before defining bounded tasks.
- Record unknown files, dependencies, credentials, evidence, or validation paths as explicit blockers.
- Use `confirmation` tasks only for truthful no-op checks.

## Reverse Handoff

When MAGIA reports `technical-gap-note.md`, implementation ADRs, validation gaps, or contradictions with code/runtime truth, MAGO may refine product interpretation, technical design, task definitions, dependencies, validation plans, and handoff wording. Delivery commitments, owner, due date, release posture, accepted business risk, and stakeholder communication route to nomia.

## Recommended Handoff Language

```text
MAGO prepared the planning package and execution-ready task contract for <spec_id>. Downstream MAGIA execution may implement the required code, configuration, tests, migrations, and technical documentation. MAGO has not executed the work or produced runtime evidence.
```

Avoid language such as: `This is planning-only, so product implementation is blocked.`

## Validation

Before closing a run that changes `tasks.md`, technical design, validation, notes, or handoff wording, verify:

- cycle, registry, package, and manifest identities agree;
- dependencies resolve and are acyclic;
- implementation tasks have concrete objective, boundary, validation, and expected result;
- blockers identify missing evidence or prerequisites rather than the need for implementation;
- product-only modes did not create tasks and task-only modes did not rewrite product intent;
- generated views are not treated as authoritative;
- `scripts/validate_planning_execution_handoff.py <skill-root>` passes for skill-package changes.
