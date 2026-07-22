# Canonical Board Contract

MAGIA carries this contract locally so it can execute planning packages without loading, importing, or running another skill.

```text
docs/boards/<board_id>/<year>/cycles/<cycle_id>/
  cycle.yaml
  registry/<spec_id>.yaml
  specs/<spec_id>/
    manifest.yaml
    prd.md
    technical-design.md        # optional
    tasks.md
    notes.md
    validation.md
    implementation-notes.md    # MAGIA-owned when execution exists
    validation-evidence.md     # MAGIA-owned when execution exists
```

Identifiers are immutable:

```text
cycle_id = cycle-<yyyy-mm-dd>-<cycle-key>
spec_id  = spec-<yyyy-mm-dd>-<feature-key>
```

The encoded date must be a real ISO calendar date, including leap-year rules; regex-shaped but impossible dates are invalid identities.

The year directory must match the year encoded in `cycle_id`. The registry filename must equal `<spec_id>.yaml`; the package directory and manifest `spec_id` must match it. ULID-bearing identifiers are rejected for active execution; ADAPT may read legacy content that mentions them without resolving them as active identities.

## Source of Truth

- `cycle.yaml`: cycle identity and lifecycle.
- `registry/<spec_id>.yaml`: spec identity, dependencies, handoff and planning status.
- `manifest.yaml`: package identity mirror, planning phase, source map and traceability.
- planning documents: intended behavior and validation plan.
- MAGIA execution artifacts: implementation and validation evidence.

`spec-catalog.yaml` and `define-queue.yaml` are generated projections, not active board files and never MAGIA write targets.

## Registry Contract

A registry entry uses `kind: mago-spec` and includes `spec_id`, `cycle_id`, `feature_key`, `feature_version`, title, type, classification, created timestamp, status, dependencies, supersession, handoff data, and the three explicitly separated scheduling concepts:

- `business_priority`: Nomia-owned read-only evidence (`unknown`, `low`, `medium`, `high`, `urgent`) with source and observation time when known;
- `technical_criticality`: Mago-owned technical impact/risk (`low`, `normal`, `high`, `critical`) with rationale for non-default values;
- `execution_sequence`: Mago-owned dependency-safe rank/lane/rationale.

Generic `priority` and `order_hint` fields are invalid. MAGIA consumes these values and validates their provenance; it never changes business priority, technical criticality, or planning sequence.

Spec statuses: `planned`, `in_progress`, `blocked`, `done`, `cancelled`, `superseded`.

Dependencies in `depends_on_specs` must reference existing registry entries and form an acyclic graph. A dependency is execution-ready only when its registry status is `done`.

## Task and Validation Linkage

Before RALPH mutation, `scripts/validate_execution_readiness.py` must prove that the selected task resolves to both current planning intent and a planned validation check. Prefer shared canonical anchors in planning text:

```text
OBJ-001 / GOAL-001 / REQ-001
AC-001
VAL-001
```

For legacy packages without anchors, the validator may use deterministic domain-term overlap, but it must reject an unrelated task even when valid objective, acceptance, and validation sections exist elsewhere in the package. Tasks execute in listed order unless planning explicitly marks a task `[parallel]` or `[independent]`; MAGIA does not add those markers.

For done-state closure, each Traceability source in `validation-evidence.md` must resolve to the selected `taskNNN`, a canonical anchor present in the selected task/PRD, or the exact current text of the selected task, PRD objective, or acceptance criterion. The Traceability check must name the same passed check recorded in the evidence table. Free text that does not resolve to planning truth cannot authorize mutation.

## Execution Sync

MAGIA may update only:

- an existing checkbox in `tasks.md` after truthful completion;
- `manifest.yaml.status`, `manifest.yaml.phase` and evidence-backed `last_execution`;
- the matching registry entry `status`;
- MAGIA-owned execution artifacts.

MAGIA must not rewrite planning identity, task prose, task order, dependencies, acceptance criteria, PRD, validation plan, technical design, handoff fields or governance records.

When the selected task is done but other required tasks remain open, spec status remains `in_progress`. Set spec and manifest to `done` only when every required task is checked and execution evidence is aligned.
