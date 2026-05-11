# Shared Artifact Ownership

Use this reference whenever MAGO touches artifacts that MAGIA also reads or updates during execution.

## Ownership Matrix

| Artifact | MAGO ownership | MAGIA boundary | Notes |
|---|---|---|---|
| `prd.md` | product/technical planning interpretation for the selected spec | read-only | Product intent and acceptance criteria are not execution records. |
| `technical-design.md` | intended architecture, contracts, risks, and design constraints | read-only input unless execution proves a gap | Material design changes return to MAGO. |
| `tasks.md` | task definitions, ids, order, dependencies, metadata, and validation expectations | may toggle only an existing checkbox when the task is truthfully done | MAGIA must not create, split, rename, reorder, resequence, or rewrite task definitions. |
| `validation.md` | validation plan and proof expectations | read-only plan | Runtime commands/results belong in `validation-evidence.md`. |
| `validation-evidence.md` | read-only evidence produced by execution | MAGIA-owned | MAGO may consume it during later planning reconciliation but must not fabricate it. |
| `notes.md` | assumptions, repository findings, planning decisions, risks, trade-offs, open questions, and specialist rationale | read-only planning context | Execution history belongs in `implementation-notes.md`. Legacy execution sections are not preserved as MAGO-compatible content; route them through MAGIA ADAPT or remove them during MAGO adapt once current artifacts exist. |
| `implementation-notes.md` | read-only execution evidence | MAGIA-owned | Contains execution log, implementation facts, deviations, blockers, and handoffs. |
| `manifest.yaml` | planning identity, package shape, source-of-truth links, traceability, initial `status: planned`, and initial `phase: define` | may update execution status, phase, and `last_execution` from truthful execution evidence | MAGO must preserve truthful MAGIA execution fields during refine/adapt unless current evidence proves drift. |
| `spec-catalog.yaml` | catalog order, dependencies, planning status defaults, feature metadata, and package selection | may sync execution status from truthful execution evidence | nomia owns delivery/governance status, not MAGO or MAGIA. |

Delivery reporting note: nomia may consume `validation-evidence.md`, `implementation-notes.md`, `technical-gap-note.md`, and implementation ADRs as read-only input for feature reports, release notes, or governance blockers. MAGO should keep those files source-attributed and must not rewrite them to make delivery status look accepted.

## Template Boundary

MAGO is the source of truth for templates and structural normalization of shared planning artifacts (`spec-catalog.yaml`, `manifest.yaml`, `tasks.md`, `notes.md`, and `validation.md`). MAGIA may update existing generated files only for execution evidence and technical execution-state fields; it should not carry or use duplicate planning templates for these files. If a downstream executor needs a missing or structurally invalid planning artifact, route back to MAGO instead of scaffolding it from MAGIA.

## MAGO Rules

- Create new planning packages with unchecked tasks, `status: planned`, and `phase: define` unless source truth already proves another state.
- Treat execution-state fields as evidence inputs. Do not simulate execution start, completion, validation, deployment, or acceptance.
- If MAGIA evidence shows a completed task, preserve it and align planning around it; if evidence is missing or contradictory, record a planning blocker instead of changing execution state.
- Do not write new command results, runtime logs, test outcomes, or execution summaries into `validation.md` or `notes.md`.
- When planning changes require MAGIA action, express the expectation in task metadata, `validation.md`, `technical-design.md`, or `execution-handoff-plan` wording, not in execution evidence files.
- If execution evidence has delivery/governance implications, preserve the evidence and hand off the delivery interpretation to nomia instead of changing release notes, stakeholder status, roadmap priority, owner, due date, or accepted business risk.

## Drift Handling

If shared artifacts disagree:

1. Preserve repository truth and MAGIA execution evidence first.
2. Preserve MAGO planning intent where it does not contradict execution evidence.
3. Stop and hand off when repair would require changing task definitions, acceptance criteria, architecture, or product intent.
4. Never make `manifest.yaml`, `spec-catalog.yaml`, or task checkboxes look done without matching execution evidence.
