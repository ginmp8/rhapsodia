# Mature Skill Patterns

Use when translating mature workflow-skill patterns into a target skill without relying on an external named skill or prior implementation.

## Preserve

### 1. Scope boundary

State owned artifact/task family, explicit non-goals, handoff points, and unknowns instead of inventing evidence.

### 2. Mode before work

Select one primary mode from user intent, inputs, outputs, and final validators. Add a matrix when the target supports audit, generate, refine, validate, package, or execute. Include intent, mode, inputs, outputs, and closure check.

### 3. Path and ownership rules

For writing skills, define generated-artifact locations, read-only evidence, controlled records, and paths that must never be duplicated ad hoc.

### 4. Progressive loading

Keep `SKILL.md` as control plane. Move detailed mode rules, schemas, template rules, examples, and rubrics to `references/`. Keep fillable skeletons in `assets/templates/`. Link each reference from `SKILL.md` with a clear load condition.

### 5. Template-backed artifacts

Treat `assets/templates/` as operational skeletons. Keep reusable templates there; reference each from `SKILL.md`, a reference, or writer/validator script; state when the model may fill/copy directly versus use a script; add writer/updater/validator scripts when structure matters. Do not delete a useful template only because no script reads it; integrate first. Validate strict outputs.

### 6. Deterministic helpers

Use scripts for fragile or repetitive tasks: validator selection, template scaffolding, schema-safe updates, file syncing, cross-file consistency.

### 7. Truthful closure

Require exact commands, pass/fail outcomes, files changed, gaps, and validation evidence before completion claims.

### 8. Stop conditions

Name blockers that prevent invented facts, duplicate structures, unsafe writes, or invalid state.

## Remove anti-patterns

- Long `SKILL.md` carrying every rule/example.
- Resources not referenced by workflow.
- Scripts without CLI, deterministic output, or representative run.
- Templates copied/filled without workflow reference, placeholder rules, validation expectation, or rationale.
- Vague output formats instead of contracts.
- Benchmark scores without frozen fixtures or execution evidence.
- Activation guidance hidden only in the body instead of frontmatter.
