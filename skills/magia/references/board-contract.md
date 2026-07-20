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
cycle_id = <yyyy-mm-dd>-<cycle-key>--<lowercase-ulid>
spec_id  = spec-<yyyy-mm-dd>-<feature-key>--<lowercase-ulid>
```

The year directory must match the year encoded in `cycle_id`. The registry filename must equal `<spec_id>.yaml`; the package directory and manifest `spec_id` must match it.

## Source of Truth

- `cycle.yaml`: cycle identity and lifecycle.
- `registry/<spec_id>.yaml`: spec identity, dependencies, handoff and planning status.
- `manifest.yaml`: package identity mirror, planning phase, source map and traceability.
- planning documents: intended behavior and validation plan.
- MAGIA execution artifacts: implementation and validation evidence.

`registry/<spec_id>.yaml` and `define-queue.yaml` are generated projections, not active board files and never MAGIA write targets.

## Registry Contract

A registry entry uses `kind: mago-spec` and includes `spec_id`, `spec_uid`, `cycle_id`, `feature_key`, `feature_version`, title, type, classification, created timestamp, status, priority, optional order hint, dependencies, supersession and handoff data.

Spec statuses: `planned`, `in_progress`, `blocked`, `done`, `cancelled`, `superseded`.

Dependencies in `depends_on_specs` must reference existing registry entries and form an acyclic graph. A dependency is execution-ready only when its registry status is `done`.

## Execution Sync

MAGIA may update only:

- an existing checkbox in `tasks.md` after truthful completion;
- `manifest.yaml.status`, `manifest.yaml.phase` and evidence-backed `last_execution`;
- the matching registry entry `status`;
- MAGIA-owned execution artifacts.

MAGIA must not rewrite planning identity, task prose, task order, dependencies, acceptance criteria, PRD, validation plan, technical design, handoff fields or governance records.

When the selected task is done but other required tasks remain open, spec status remains `in_progress`. Set spec and manifest to `done` only when every required task is checked and execution evidence is aligned.
