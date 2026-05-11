# Define mode

Use define mode when the request is about creating or revising one execution-ready spec package under the active cycle.

## Scope
- planning-only
- select exactly one `spec_id`
- operate under `<cycle_version>/specs/<spec_id>/`
- create or refine:
  - `manifest.yaml`
  - `prd.md`
  - `tasks.md`
  - `validation.md`
  - `notes.md`
- keep the package aligned with the active `spec-catalog.yaml`

## Artifact responsibilities

### `manifest.yaml`
Authoritative for:
- local spec identity
- classification
- status
- phase
- source-of-truth mapping
- traceability metadata

Rules:
- keep `phase: define` during planning-only definition work
- preserve discovery traceability when relevant
- keep source-of-truth paths lowercase

### `prd.md`
Must contain:
- context
- problem statement
- goals
- non-goals
- current state
- proposed outcome
- functional requirements
- non-functional requirements
- constraints
- risks and trade-offs
- acceptance criteria
- open questions

Rules:
- include the YAML metadata block
- be concrete and repository-aware
- keep acceptance criteria testable
- do not turn the PRD into a task list

### `tasks.md`
Every actionable task must include:
- markdown checkbox
- stable numeric identifier such as `Task 1`
- `Objective`
- `Affected boundary`
- `Task type`
- `Reasoning`
- `Why this reasoning is sufficient`
- `Specialist Support`
- `Validation`
- `Expected result`
- `Dependencies` when applicable

Rules:
- default to `low` or `medium`
- keep tasks small, concrete, and reviewable
- split vague umbrella tasks
- preserve execution readiness

### `validation.md`
Keep proof expectations concrete and proportional.

### `notes.md`
Keep assumptions, findings, design decisions, risks, trade-offs, open questions, and execution context factual and distinct from requirements.

## Final review
Review in this order:
1. `manifest.yaml`
2. `prd.md`
3. `validation.md`
4. `notes.md`
5. architecture impact when relevant
