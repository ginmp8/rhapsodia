# Mature Skill Patterns

Use this reference when translating mature workflow-skill patterns into a target skill without depending on any external named skill, framework, or prior implementation.

## High-value patterns to preserve

### 1. Explicit scope boundary

A hardened skill says exactly what it owns and what it does not own. Apply this pattern to the target skill:

- state the owned artifact family or task family;
- state explicit non-goals;
- define when to hand off instead of stretching the skill;
- preserve unknowns instead of inventing missing evidence.

### 2. Mode selection before work

Mature skills avoid one giant workflow. They choose one primary mode from user intent, required inputs, outputs, and final validators. Add a mode matrix when the target skill supports different types of work, such as audit, generate, refine, validate, package, or execute.

A useful mode matrix includes:

- user intent;
- mode name;
- required inputs;
- primary outputs;
- final validator or closure check.

### 3. Canonical path and ownership rules

For any target skill that writes files, add rules for:

- where generated artifacts belong;
- which files are read-only evidence;
- which files are controlled records;
- which paths must never be created as ad hoc duplicates.

### 4. Progressive loading

Keep `SKILL.md` as the control plane. Move detailed mode rules, schemas, template usage rules, examples, and quality rubrics into `references/`. Keep reusable fillable artifact skeletons in `assets/templates/`. Link each reference from `SKILL.md` with a condition for loading it.

Good conditional references answer: "load this only when the run needs X."

### 5. Template-backed artifacts

Treat `assets/templates/` as operational artifact skeletons, not explanatory prose. A template may be consumed by a script or filled/copied by the agent when the workflow declares that use. Apply this pattern when the target skill creates repeatable artifacts:

- keep reusable fillable templates in `assets/templates/`;
- reference each template from `SKILL.md`, a relevant reference, or a writer/validator script;
- add writer, updater, or validator scripts when mechanical correctness or schema stability matters;
- instruct the model when it may fill the template directly versus when it must use a script;
- do not migrate or delete a useful template merely because no script reads it; integrate it first when the workflow needs it;
- validate after writing or editing when the output has required structure.

### 6. Deterministic validators and helpers

Use scripts for operations that are fragile, repetitive, or easy to hallucinate. Examples:

- choose the correct validator based on a path;
- scaffold a file from a template;
- update a list field without breaking schema;
- sync state across files;
- validate cross-file consistency.

### 7. Truthful evidence and closure

Mature skills do not claim completion from intent alone. Add closure rules requiring:

- exact commands executed;
- pass/fail outcomes;
- files changed;
- remaining gaps;
- validation evidence before final claims.

### 8. Stop conditions

Hardened skills name explicit blockers. Stop conditions are useful when continuing would cause invented facts, duplicate structures, unsafe writes, or invalid state.

## Anti-patterns to remove

- A long `SKILL.md` that tries to contain every rule and example.
- Resources that exist but are never referenced by the workflow.
- Scripts without a CLI, deterministic output, or a representative test run.
- Templates that are copied or filled without workflow references, placeholder rules, validation expectations, or an explicit rationale.
- Output formats described vaguely instead of as an output contract.
- Benchmark scores reported without frozen fixtures or real execution evidence.
- Activation guidance hidden only in the body instead of frontmatter description.
