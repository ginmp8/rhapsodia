# sequential work packaging convention

This file contains the full source convention used by the skill.

# Final Established Convention for Sequential Work Packaging

## Purpose

This convention defines how to organize planning-first work packages for sequential execution, with exactly one feature or one fix per release item.

It standardizes:

* macro versioning and release-item sequencing
* work package identity
* stable feature identity
* semantic versioning rules
* dependency modeling
* catalog structure
* filesystem structure
* artifact responsibilities
* status rules
* final review and handoff
* reproducibility rules for both humans and AI

This convention is intended to be used by both humans and AI during planning and development.

---

## 1. Core Model

The model separates five different concerns:

* `cycle_version` -> macro grouping container
* `spec_id` -> sequential work package identifier
* `feature_key` -> stable functional identity
* `feature_version` -> semantic evolution of the feature or fix
* planning artifacts -> execution-ready documentation package

This separation is mandatory.

---

## 2. Macro Versioning and Release Semantics

### 2.1 `cycle_version`

`cycle_version` is the macro grouping container.

Example:

* `01.00.00`

It is used to:

* group a set of related specs
* represent a larger initiative, cycle, milestone, or release line
* create a stable top-level container for ordered work packages

### 2.2 Semantic meaning of the macro version

Semantic Versioning already conveys whether an item is primarily a feature or a fix through major, minor, and patch evolution.

Therefore, `cycle_version` is not replacing semantic versioning. Instead:

* the macro version organizes the top-level grouping
* the feature or fix version expresses semantic evolution
* the ordered `spec_id` expresses execution sequence

### 2.3 Practical interpretation

Use this interpretation consistently:

* `cycle_version` = macro planning and grouping container
* `feature_version` = semantic technical evolution of a feature or fix
* `spec_id` = ordered execution unit

This means:

* semantic versioning explains the nature of change
* `spec_id` explains the order of execution
* `cycle_version` explains the container where that sequence lives

---

## 3. Sequential Work Package Identity

### 3.1 `spec_id`

`spec_id` is the unique sequential identifier of the work package.

Format:

* `spec001`
* `spec002`
* `spec003`

Rules:

* `spec_id` is the primary execution identifier
* it must remain stable once created
* cancelled specs keep their id
* gaps in numbering are allowed
* existing specs must not be renumbered except under exceptional circumstances

### 3.2 `order`

Each spec must also carry an `order` field.

Format:

* integer
* increments of 10

Examples:

* `10`
* `20`
* `30`

Purpose:

* preserve sortable execution order
* allow insertion later without renumbering all remaining items

Example of later insertion:

* `15`
* `25`

Rule:

* `spec_id` is the stable identity
* `order` is the sortable sequence
* both must exist

---

## 4. Stable Functional Identity

### 4.1 `feature_key`

`feature_key` is the stable identity of the capability.

Format:

* lowercase
* kebab-case

Examples:

* `document-classification`
* `pending-extraction`
* `case-summary`

Rules:

* `feature_key` identifies the functional domain
* the same `feature_key` may appear across multiple specs over time
* `feature_key` must never replace `spec_id` as the execution identifier

### 4.2 Reopening and evolving an existing feature

Use these rules:

* new capability -> new `feature_key`
* compatible improvement -> same `feature_key`, new `feature_version`
* correction -> same `feature_key`, patch version increment
* materially different capability or conceptual redesign -> new `feature_key`

---

## 5. Semantic Versioning Rules

### 5.1 `feature_version`

`feature_version` tracks the semantic evolution of the feature or fix.

Format:

* `v0.1.0`
* `v0.2.1`
* `v1.0.0`
* `v2.0.0`

### 5.2 Lifecycle rules

#### First functional implementation

* `v0.1.0`

#### Compatible improvement before stable production

* increment minor
* example: `v0.2.0`

#### Fix before stable production

* increment patch
* example: `v0.2.1`

#### First stable production release

* `v1.0.0`

#### Compatible improvement after stable release

* example: `v1.1.0`

#### Fix after stable release

* example: `v1.1.1`

#### Breaking change

* example: `v2.0.0`

### 5.3 Rule summary

* use Semantic Versioning for the technical evolution of the feature or fix
* do not use semantic version numbers to define roadmap execution order
* execution order is defined by `order` and `spec_id`

---

## 6. Planning Artifact Model

Each spec folder must contain the full planning package:

* `manifest.yaml`
* `prd.md`
* `tasks.md`
* `notes.md`
* `validation.md`

All five are mandatory.

### 6.1 Responsibility split

#### `manifest.yaml`

The top-level descriptor of the spec.

Purpose:

* identify the initiative
* classify the work
* define planning state
* point to source-of-truth files
* preserve traceability when needed

#### `prd.md`

Defines:

* what is being solved
* why it matters
* goals, scope, constraints, and expected outcome

#### `tasks.md`

Defines:

* how the work will be executed
* in what sequence
* with what reasoning level
* with what validation expectations

#### `notes.md`

Defines:

* assumptions
* findings
* risks
* trade-offs
* open questions
* additional execution context

#### `validation.md`

Defines:

* how correctness will be proven
* what evidence is required
* what remains untested or blocked if relevant

---

## 7. Source of Truth and Precedence Rules

To avoid ambiguity, use the following precedence model.

### 7.1 `spec-catalog.yaml`

Authoritative for:

* sequence
* order
* spec ids
* feature mapping
* dependency summary
* high-level status
* semantic version reference

### 7.2 `manifest.yaml`

Authoritative for:

* local spec identity
* classification
* phase
* source-of-truth file mapping
* traceability metadata

### 7.3 `prd.md`, `tasks.md`, `notes.md`, `validation.md`

Authoritative for:

* detailed planning content
* execution details
* assumptions and trade-offs
* task decomposition
* proof and validation expectations

### 7.4 Conflict resolution rule

If there is conflict:

1. sequence and summary metadata come from `spec-catalog.yaml`
2. local identity and traceability come from `manifest.yaml`
3. detailed planning meaning comes from the `.md` files

This precedence must be followed consistently.

---

## 8. Request Classification and Type

### 8.1 `type`

Use a narrow operational enum:

* `feature`
* `fix`

### 8.2 `classification`

Use a richer planning classification when useful.

Allowed values:

* `feature`
* `bugfix`
* `refactor`
* `performance`
* `validation`
* `architecture`
* `investigation`
* `docs-only`

### 8.3 Scope rule

`classification` is useful at the spec level.

It is not required to treat classification as a permanent property of the feature itself. A feature remains primarily identified by `feature_key`, while the spec may describe the nature of the current work through `classification`.

### 8.4 Mapping rule

* `bugfix` maps operationally to `type: fix`
* all other classes default to `type: feature` unless explicitly overridden

---

## 9. Status Model

### 9.1 Spec status

Allowed values:

* `planned`
* `in_progress`
* `done`
* `cancelled`

Definitions:

* `planned` = defined but not started
* `in_progress` = currently being executed
* `done` = completed and validated
* `cancelled` = intentionally abandoned or removed

### 9.2 Cycle status

A cycle may also have its own status.

Allowed values:

* `planned`
* `active`
* `closed`
* `cancelled`

Definitions:

* `planned` = created but not started
* `active` = at least one spec is in execution or pending execution in the active cycle
* `closed` = all intended specs are completed or intentionally excluded
* `cancelled` = the cycle was abandoned

---

## 10. Dependency Model

Dependencies exist at three levels and must be modeled separately when needed.

### 10.1 Feature or fix dependencies

Use when one capability logically depends on another.

Field:

* `depends_on_features`

Value:

* list of `feature_key`

### 10.2 Spec dependencies

Use when one work package depends on another work package being completed first.

Field:

* `depends_on_specs`

Value:

* list of `spec_id`

### 10.3 Task dependencies

Use inside `tasks.md` when one task depends on another task.

Field inside task body:

* `Dependencies`

Value:

* list of task identifiers

### 10.4 Summary rule

* capability dependency -> `depends_on_features`
* execution dependency between work packages -> `depends_on_specs`
* execution dependency inside one spec -> task-level dependencies

This separation must be preserved.

---

## 10.5 Discovery Model

Discovery remains a separate upstream activity.

Discovery artifacts may live outside the cycle container under:

* `docs/discovery/`

Discovery is authoritative only for:

* frontier analysis
* candidate evidence
* provisional capability boundaries
* repository findings that inform ordering

Discovery is not authoritative for:

* `spec_id`
* `order`
* `cycle_version`
* `feature_version`
* final dependency declarations in `spec-catalog.yaml`

### Discovery output expectations

Discovery should identify candidates using a provisional capability key that already follows the future `feature_key` format:

* lowercase
* kebab-case

This means discovery should prefer a provisional `feature_key` over ad hoc ids whenever possible.

### Discovery to ordering handoff

The ordering phase is responsible for converting discovery evidence into formal sequential work packages by:

1. selecting or creating the active `cycle_version`
2. assigning `spec_id`
3. assigning `order`
4. assigning `feature_version`
5. writing `spec-catalog.yaml`
6. preserving discovery traceability in `manifest.yaml`

### Discovery traceability rule

If a spec originates from discovery, the resulting `manifest.yaml` should preserve at least:

* primary discovery file
* supporting discovery files when relevant
* discovery frontier when known

This keeps the discovery model compatible with the planning and execution model without mixing their responsibilities.

---

## 11. Global Naming and Casing Rules

Use lowercase everywhere for:

* directory names
* file names
* ids
* enum values
* YAML keys

### Allowed formats

#### `cycle_version`

* quoted string in YAML
* example: `"01.00.00"`

#### `spec_id`

* format `specNNN`

#### `feature_key`

* lowercase kebab-case

#### File names

* `spec-catalog.yaml`
* `manifest.yaml`
* `prd.md`
* `tasks.md`
* `notes.md`
* `validation.md`

---

## 12. Official Directory Structure

```text
01.00.00/
  spec-catalog.yaml
  specs/
    spec001/
      manifest.yaml
      prd.md
      tasks.md
      notes.md
      validation.md
    spec002/
      manifest.yaml
      prd.md
      tasks.md
      notes.md
      validation.md
```

Meaning:

* `01.00.00/` = cycle container
* `spec-catalog.yaml` = sequence source of truth
* `specs/spec001/` = one execution-ready work package
* inner files = mandatory planning artifacts

---

## 13. Official Workflow

The standard workflow is:

1. define or update the `cycle_version`
2. define or update `cycle_status`
3. define execution order in `spec-catalog.yaml`
4. assign `spec_id`
5. create the spec folder
6. create `manifest.yaml`
7. write `prd.md`
8. write `tasks.md`
9. write `notes.md`
10. write `validation.md`
11. review dependencies
12. perform final review
13. hand off for execution

Mandatory rule:

* the catalog must exist before the spec is created

In short:

* catalog first
* spec after

---

## 14. Reasoning Guidance

Every actionable task in `tasks.md` must declare a reasoning level.

Allowed values:

* `low`
* `medium`
* `high`
* `xhigh`

### Definitions

* `low` = local, concrete, obvious target, little judgment
* `medium` = spans a few files or layers, requires adaptation or bounded judgment
* `high` = unresolved architecture, durable trade-off, broader contract impact, expensive-to-reverse mistake
* `xhigh` = truth-critical or recovery-critical planning where weaker reasoning would likely preserve false posture or misleading delivery claims

### Rules

* default to `low` or `medium`
* use `high` only with a clear reason
* use `xhigh` only in exceptional planning boundaries
* routine docs updates, consistency review, and simple revalidation are usually not `high`

---

## 15. Specialist Support

Specialist support is optional metadata attached to a task when it materially helps execution.

Allowed structure when present:

* `required_load`
* `optional_load`
* `discovery_source`
* `selection_hint`

Rules:

* specialist metadata is sparse, not default
* a task may have none, one, or multiple specialists
* multiple specialists are allowed only when complementary
* specialist support must not compensate for poor decomposition

This documentation is intended for both human and AI execution, so specialist guidance must remain explicit but proportionate.

---

## 16. Proportionality Rule

The planning package should be complete by default.

However, proportionality still applies to the depth of content:

* small items may have shorter content
* complex items require fuller analysis
* completeness is mandatory, verbosity is not

Rule:

* always prioritize a complete package
* do not omit required sections
* adapt detail level to the complexity of the feature or fix

---

## 17. Bounded Refinement Rule

A bounded refinement task may be added only when all of the following are true:

1. the same initiative continues under the same PRD
2. remaining work is too broad, under-specified, or not safely batchable
3. a later docs-only pass will improve execution quality
4. refinement remains bounded to the same feature and documentation root
5. the work cannot already be decomposed clearly into executable tasks now

Rules:

* do not use refinement to postpone already-clear planning work
* preserve completed history
* refine future work only
* keep refinement bounded to the same initiative

Because the documentation is used by both humans and AI, refinement must be controlled and explicit.

---

## 18. Required Structures

### 18.1 `spec-catalog.yaml`

```yaml
schema_version: 1
cycle_version: "01.00.00"
cycle_status: active
specs:
  - order: 10
    spec_id: spec001
    feature_key: document-classification
    title: Document Classification
    type: feature
    classification: feature
    depends_on_features: []
    depends_on_specs: []
    status: planned
    feature_version: v0.1.0

  - order: 20
    spec_id: spec002
    feature_key: pending-extraction
    title: Pending Extraction
    type: feature
    classification: feature
    depends_on_features:
      - document-classification
    depends_on_specs:
      - spec001
    status: planned
    feature_version: v0.1.0
```

### 18.2 `manifest.yaml`

```yaml
schema_version: 1
spec_id: spec001
feature_key: document-classification
title: Document Classification
type: feature
classification: feature
status: planned
phase: define
cycle_version: "01.00.00"
feature_version: v0.1.0
source_of_truth:
  prd: prd.md
  tasks: tasks.md
  validation: validation.md
  notes: notes.md
traceability: {}
```

### 18.2.1 `phase` guidance

Use a narrow, lowercase phase model in `manifest.yaml`:

* `define`
* `execute`
* `review`
* `done`

Rules:

* use `define` while the planning package is being created or refined
* use `execute` once implementation starts
* use `review` only when the remaining work is final review or release-readiness review
* use `done` only when the spec is completed and validated

### 18.3 PRD metadata block

```yaml
spec_id: spec001
order: 10
feature_key: document-classification
title: Document Classification
type: feature
classification: feature
status: planned
phase: define
cycle_version: "01.00.00"
feature_version: v0.1.0
depends_on_features: []
depends_on_specs: []
```

---

## 19. Minimum Content Required in Each File

### `prd.md`

Must contain:

* context
* problem statement
* goals
* non-goals
* current state
* proposed outcome
* functional requirements
* non-functional requirements
* constraints
* risks and trade-offs
* acceptance criteria
* open questions

Rules:

* be concrete
* be repository-aware when repository context matters
* keep acceptance criteria testable
* do not turn the PRD into a task list

### `tasks.md`

Every actionable task must:

* have a markdown checkbox
* have a stable numeric identifier such as `Task 1`
* declare objective
* declare affected boundary
* declare task type
* declare reasoning level
* explain why that reasoning level is sufficient
* declare validation approach
* declare expected result
* declare dependencies when applicable

Recommended shape:

```md
- [ ] Task 1: <short title>
  - Objective: ...
  - Affected boundary: ...
  - Task type: ...
  - Reasoning: low|medium|high|xhigh
  - Why this reasoning is sufficient: ...
  - Specialist Support: none
  - Dependencies: ...
  - Validation: ...
  - Expected result: ...
```

Rules:

* keep tasks small, concrete, and reviewable
* split vague umbrella tasks
* preserve execution-readiness
* include tests, docs, validation, or hardening explicitly when relevant

### `notes.md`

Must contain:

* assumptions
* repository findings
* design decisions
* risks
* trade-offs
* open questions
* specialist rationale when used
* complementary execution context

Rules:

* keep notes factual and useful
* do not duplicate the PRD
* distinguish assumptions from requirements

### `validation.md`

Must contain concrete proof expectations relevant to the work, such as:

* backward compatibility
* parsing or serialization
* compile-time behavior
* runtime behavior
* integration behavior
* edge cases
* regression behavior
* performance validation
* observability validation
* docs-consistency validation

Rules:

* avoid vague statements
* validation depth must match task reasoning
* record concrete evidence expectations

---

## 20. Mandatory Final Review

Every spec must end with a final review.

Review order:

1. `manifest.yaml`
2. `prd.md`
3. `validation.md`
4. `notes.md`
5. architecture impact, when relevant

Rules:

* close planning gaps that can already be resolved
* align open questions with available evidence
* add only the minimum new in-scope tasks required
* verify architecture impact when relevant
* do not claim completion without evidence
* keep all planning docs internally consistent

---

## 21. Reproducibility Rules

To guarantee future consistency, always:

* use `specNNN`
* use lowercase everywhere
* use kebab-case for `feature_key`
* use `cycle_version` as a grouping container only
* keep `spec-catalog.yaml` as the source of truth for ordering
* keep `manifest.yaml` mandatory inside each spec
* use `order` in increments of 10
* use Semantic Versioning only for feature or fix evolution
* use the three-level dependency model
* keep planning complete by default
* keep tasks execution-ready
* assign reasoning levels explicitly
* perform final review before handoff

Never:

* use semantic version numbers to define roadmap order
* use `feature_key` as the execution identifier
* mix `spec_id` and `feature_key`
* renumber specs casually
* hide tasks inside the PRD
* use vague validation
* overuse `high` reasoning
* use refinement to postpone already-clear planning work

---

## 22. Final Institutionalized Model

The final standardized model is:

* `cycle_version` organizes the macro container
* `spec_id` organizes the sequential execution unit
* `feature_key` identifies the stable functional capability
* `feature_version` tracks semantic technical evolution
* `spec-catalog.yaml` is the source of truth for ordering
* `manifest.yaml` is mandatory inside each spec
* each `spec` folder contains `prd.md`, `tasks.md`, `notes.md`, and `validation.md`
* dependencies exist at feature, spec, and task level
* each task declares reasoning level and validation approach
* each spec ends with a mandatory final review
* the model is intended for both human and AI use

---

## 23. Canonical Summary Statement

Use `cycle_version` as the macro grouping container, `spec_id` as the sequential execution unit, `feature_key` as the stable functional identity, and `feature_version` as the semantic technical evolution of the feature or fix. Use `spec-catalog.yaml` as the source of truth for ordering, make `manifest.yaml` mandatory inside each spec, store every work package under `specs/specNNN/`, model dependencies at feature, spec, and task level, require explicit reasoning guidance in tasks, and finish every spec with a mandatory final review.
