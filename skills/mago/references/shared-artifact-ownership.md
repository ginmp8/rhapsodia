# Shared Artifact Ownership

Use this reference whenever MAGO touches artifacts that MAGIA also reads or updates during execution.

## Ownership Matrix

| Artifact | MAGO ownership | MAGIA boundary | Notes |
|---|---|---|---|
| `cycle.yaml` | immutable cycle identity and planning lifecycle metadata | read-only | Governance acceptance/status remains nomia-owned where applicable. |
| `registry/<spec_id>.yaml` | immutable spec identity, feature metadata, dependencies, handoff, planning status | may synchronize technical execution status only from current evidence | MAGIA must not create IDs, dependencies, handoff shape, or supersession decisions. |
| `prd.md` | product/technical planning interpretation | read-only | Product intent and acceptance criteria are not execution records. |
| `technical-design.md` | intended architecture, contracts, risks, constraints | read-only input unless execution proves a gap | Material changes return to MAGO. |
| `tasks.md` | definitions, IDs, order, dependencies, metadata, validation expectations | may toggle only an existing checkbox after truthful completion | MAGIA must not create, split, rename, reorder, resequence, or rewrite task definitions. |
| `validation.md` | validation plan and proof expectations | read-only plan | Runtime results belong in `validation-evidence.md`. |
| `validation-evidence.md` | read-only execution evidence | MAGIA-owned | MAGO may consume it but must not fabricate or rewrite it. |
| `notes.md` | planning assumptions, findings, decisions, risks, trade-offs, questions, specialist rationale | read-only planning context | Execution history belongs in `implementation-notes.md`. |
| `implementation-notes.md` | read-only execution evidence | MAGIA-owned | Contains implementation facts, deviations, blockers, and handoffs. |
| `manifest.yaml` | package identity, shape, traceability, planning status/phase defaults | may update execution status, phase, and `last_execution` from evidence | MAGO preserves truthful execution fields during later refinement. |
| generated catalog/queue views | renderer-owned disposable projections | read-only inspection only | Neither MAGO nor MAGIA hand-edits or synchronizes them. |

`business_priority` in the registry is read-only Nomia evidence. Mago owns `technical_criticality` and `execution_sequence`; Magia consumes them without rewriting their source authority.

## Template Boundary

MAGO owns templates and structural normalization for planning-origin files. MAGIA may update generated package files only for narrow, evidence-backed execution state and checkbox synchronization. Missing or invalid planning structure is a MAGO refinement input, not a MAGIA scaffold task.

## MAGO Rules

- Preserve truthful MAGIA evidence and execution fields.
- Do not write runtime results into planning artifacts.
- Do not infer task completion from planning status.
- Do not reset `in_progress`, `done`, or `last_execution` without stronger current evidence.
- Keep notes planning-only; route old execution sections through MAGIA ADAPT before using them as evidence.
- Keep registry/package identity consistent without treating generated views as state.

## Drift Handling

Use the following precedence for drift resolution.

### Drift Resolution Precedence

Resolve conflicts in this order:

1. current repository/runtime evidence;
2. MAGIA validation and implementation evidence;
3. immutable cycle/registry/package identity;
4. current MAGO planning artifacts;
5. discovery and imported source material;
6. generated views and caches.

If evidence cannot reconcile a conflict safely, record the contradiction and stop instead of overwriting history.
