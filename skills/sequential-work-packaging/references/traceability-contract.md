# Requirement traceability and readiness contract

Requirement traceability is an execution-readiness signal, not a replacement for lifecycle status. Existing schema-v1 packages without trace IDs remain structurally readable and valid; they are not automatically considered `execution_ready`.

## Stable trace identities

For newly defined or materially refined requirements use:

- requirement identity: `reqNNN` in `prd.md`;
- task identity: `taskNNN` in `tasks.md`;
- validation identity: `valNNN` in `validation.md`.

IDs are stable after publication. Do not renumber an existing explicit ID merely to close a gap or modernize formatting.

### PRD

Declare requirements as:

```md
- Requirement ID: req001
  - Statement: <testable requirement>
```

### Tasks

Each task implementing a requirement declares:

```md
  - Satisfies: req001
```

Multiple requirement IDs may be supplied as a comma-separated list or bracketed list.

### Validation

Each proof obligation declares:

```md
- Validation ID: val001
  - Covers: req001
  - Evidence: <expected proof>
```

## Validator behavior

The validator checks referential integrity in both execution directions:

`requirement <- task.Satisfies`

`requirement <- validation.Covers`

Unknown requirement references are errors. A declared requirement with no task or no validation is a readiness gap and is reported as a warning so legacy/partially defined packages remain inspectable without pretending they are execution-ready.

## Derived readiness

`readiness` is computed evidence; it is not persisted lifecycle state.

- `catalog_only` — the catalog identity exists but the complete canonical spec package is not present;
- `defined` — the five canonical spec artifacts exist, but requirement/task/validation traceability is absent or incomplete;
- `execution_ready` — canonical artifacts exist, at least one stable requirement is declared, every declared requirement has task coverage and validation coverage, and no readiness gap remains;
- `blocked` — structural validation contains an error that prevents safe handoff.

`planned | in_progress | done | cancelled` remains the spec lifecycle status. Do not infer readiness from status, and do not change lifecycle status merely to make readiness pass.

## Compatibility

Do not retroactively invent trace IDs for old packages during unrelated refinement. Add traceability when a requirement is newly defined, materially changed, explicitly normalized, or when the caller asks to make the package execution-ready. Record ambiguous mappings as gaps instead of guessing.
