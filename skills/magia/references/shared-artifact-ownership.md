# Shared Artifact Ownership

Use this reference whenever MAGIA executes from a MAGO package or updates controlled execution records that MAGO also reads.

## Ownership Matrix

| Artifact | MAGO/nomia ownership | MAGIA authority | Rules |
|---|---|---|---|
| `prd.md` | MAGO planning / product intent | read-only | Do not rewrite product intent, goals, non-goals, or acceptance criteria. |
| `technical-design.md` | MAGO intended architecture/design | read-only input | If implementation proves design drift, write `technical-gap-note.md` or an implementation ADR and hand off to MAGO. |
| `execution-handoff-plan.md` | MAGO planned execution strategy/handoff | read-only input | Use it to guide execution; if it is unsafe, incomplete, or contradicted by code/runtime evidence, write `technical-gap-note.md` or an implementation ADR and hand off to MAGO. |
| `tasks.md` | MAGO task definitions, ids, order, dependencies, and metadata | partial | Toggle only an existing checkbox when the task is truthfully done; never create, split, rename, reorder, resequence, or rewrite task definitions. |
| `validation.md` | MAGO validation plan | read-only plan | Use it to choose checks. Write real outcomes to `validation-evidence.md`. |
| `validation-evidence.md` | downstream evidence consumer input | MAGIA-owned | Record executed, failed, skipped, static checks, residual gaps, and blockers. |
| `notes.md` | MAGO planning notes | read-only planning context | Do not append new execution logs here. Use `implementation-notes.md`. |
| `implementation-notes.md` | downstream execution evidence | MAGIA-owned | Record execution log, actual implementation facts, deviations, blockers, decisions, and handoffs. |
| `manifest.yaml` | MAGO package identity and planning defaults | execution-state sync only | Update execution status, phase, and `last_execution` only from current truthful execution evidence. |
| `registry/<spec_id>.yaml` | planning identity, dependencies, handoff, and planning status; nomia delivery status is separate | execution-state sync only | Update only evidence-backed technical execution `status`. Preserve identity, versions, dependencies, supersession, handoff, `business_priority`, `technical_criticality`, `execution_sequence`, and provenance. Reject the unsupported generic aliases `priority` and `order_hint` rather than preserving or translating them. |

Downstream evidence boundary: nomia may read MAGIA-owned evidence for feature reports, release notes, governance blockers, or delivery risk. MAGIA must keep the evidence factual and source-level; nomia owns the stakeholder-facing interpretation.

## MAGIA Rules

- Treat planning artifacts as constraints and source evidence, not as writable execution journals.
- Keep task definitions stable; completion is represented by toggling an existing checkbox only after validation proves done.
- Write validation outcomes to `validation-evidence.md`, not `validation.md`.
- Write execution history to `implementation-notes.md`, not `notes.md`.
- Update `manifest.yaml` and the matching `registry/<spec_id>.yaml` only for technical execution state backed by current evidence.
- Stop and hand off to MAGO when safe execution requires changing PRD, acceptance criteria, architecture intent, task definitions, ordering, dependencies, or metadata.
- Hand off to nomia for delivery commitments, release posture, stakeholder communications, roadmap status, owner, or accepted business risk.
- Do not create governance RFCs, release notes, portfolio reports, stakeholder briefs, roadmap updates, or delivery status records; write execution evidence that nomia can consume instead.

## Template Boundary

MAGIA intentionally does not carry planning templates for `cycle.yaml`, `registry/<spec_id>.yaml`, `manifest.yaml`, `tasks.md`, `notes.md`, or `validation.md`. Those templates belong to MAGO. MAGIA may read those generated files and may update only the narrow execution-state fields allowed above. Use `scripts/write_artifact_scaffold.py` only for MAGIA-owned artifacts such as `implementation-notes.md`, `validation-evidence.md`, `technical-gap-note.md`, and implementation/runtime notes.

## Legacy Adapt Policy

Legacy execution content in `notes.md` or command-result content in `validation.md` is not operational MAGIA evidence. Normal RALPH execution, closure, validators, and heal scripts ignore legacy files. Use ADAPT mode only to convert legacy content best effort into current MAGIA-owned `implementation-notes.md` and `validation-evidence.md`; after adaptation, downstream work reads the current artifacts only. If adaptation cannot produce a trustworthy current artifact, report the gap instead of preserving legacy content as fallback.
