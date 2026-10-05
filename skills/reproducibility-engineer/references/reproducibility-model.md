# Reproducibility Model

## At a Glance

- **Purpose:** Classify the target reproducibility ceiling and each variance source so controls are placed at the lowest reliable layer without erasing legitimate judgment.
- **Load when:** Before choosing transformations, when deciding whether variance is mechanical, heuristic, model judgment, or external nondeterminism, or when a determinism claim needs a ceiling.
- **Decision impact:** Sets the maximum defensible reproducibility claim, control-placement choice, maturity interpretation, and variance budget; prevents forcing subjective/stochastic decisions into fake deterministic mechanisms.
- **Do not load when:** The target ceiling and variance classification are already frozen and the task is only executing a known downstream gate.

## Contents

- Purpose
- Reproducibility ceilings
- Variability taxonomy
- Control placement
- Maturity levels
- Variance budget

## Purpose

Use this model to decide what can be made mechanically reproducible, what should be constrained, and what must remain bounded judgment.

## Reproducibility ceilings

### Objective artifact
Examples: file conversion, code generation with a schema, structured extraction, deterministic diagrams, packaging.

Target state:
- normalized input;
- typed intermediate representation when useful;
- deterministic mechanics;
- independent validators;
- machine-readable diagnostics;
- exact artifact identity/hash when environment is pinned;
- regression fixtures/golden cases.

Ceiling: high.

### Tool action
Examples: deployment workflow, account mutation, repository operation, data migration.

Target state:
- explicit preconditions;
- bounded authority;
- idempotency/retry policy;
- deterministic request construction;
- postcondition verification;
- receipts/audit trail;
- dry-run when feasible.

Ceiling: high for process correctness, lower for external-system timing/outcomes.

### Research or analytic
Examples: technical research, code review, incident analysis, business analysis.

Target state:
- source hierarchy;
- evidence/citation requirements;
- explicit assumptions;
- stable report contract;
- deterministic checks for objective claims;
- calibrated rubric for judgment;
- independent review for high-impact conclusions.

Ceiling: medium-high for process and evidence; conclusions may remain stochastic.

### Constrained subjective
Examples: visual design, prose, UX critique, creative artifacts.

Target state:
- structural contract;
- hard mechanical gates for format/accessibility/runtime;
- strong defaults and design constraints;
- perceptual/editorial rubric;
- blinded comparative or human/image-capable review;
- explicit separation between mechanical pass and subjective approval.

Ceiling: medium-high for quality band, not identical output.

## Variability taxonomy

Map each material decision to one class:

| Class | Typical symptoms | Preferred control |
|---|---|---|
| mechanical | repeated parsing, formatting, rendering, hashing | script/runtime |
| schema/type | invented fields, malformed structure, inconsistent enums | schema/typed IR |
| constrained heuristic | inconsistent ordering, defaults, tie choices | ordered rules/defaults/tie-breakers |
| model judgment | interpretation, editorial choices, visual taste | evidence + rubric + independent review |
| external nondeterminism | changing web data, tool/model/runtime state, versions, clocks | pin/snapshot/version/record identity; validated environment profile when comparison depends on runtime identity |

## Control placement

Use the lowest reliable control that preserves the kind of reasoning the task actually needs:

| Variance | Control |
|---|---|
| mechanical | script, schema, or validator; keep repeated mechanics out of free-form generation |
| constrained heuristic | defaults, deterministic ordering/tie-breakers, bounded options, and stop limits |
| model judgment | explicit criteria, evidence, and rubric; keep legitimate judgment visible |
| subjective/perceptual | independent evaluation or review; never compile taste into fake determinism |

Do not promote a variance source to a stronger control layer unless the stronger layer preserves the target semantics and evaluation contract.

## Maturity levels

These are structural maturity levels, not behavioral benchmark scores.

### R0 - Instruction only
Mostly prose. Output correctness depends on model interpretation. No executable gate.

### R1 - Contract bounded
Clear activation, inputs, modes, output contract, defaults, stop rules, and progressive references.

### R2 - Mechanically validated
R1 plus scripts/schemas/validators for objective behavior and machine-readable diagnostics.

### R3 - Regression controlled
R2 plus frozen evaluators, scenario suites, regression/golden cases, repair rules, and before/after comparison.

### R4 - Evidence reproducible
R3 plus final freeze, atomic delivery/package integrity, artifact/source hashes where useful, environment/version identity, and truthful separation of structural, behavioral, runtime, and perceptual evidence. Apply the environment/provenance, stochastic-evaluation, and execution-lineage profiles when those variance surfaces are material; R4 does not require irrelevant machinery.

A subjective skill can reach R4 process maturity without producing byte-identical outputs.

## Variance budget

Do not maximize determinism blindly. Allocate freedom intentionally:

- zero or near-zero freedom for schema, safety, protocols, file integrity, required evidence, and acceptance gates;
- bounded freedom for layout, wording, decomposition, prioritization, and repair choice;
- broad freedom only where creativity is the actual product.

A strong skill tells the model exactly where freedom is allowed.
