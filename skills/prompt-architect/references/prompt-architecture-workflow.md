# Prompt Architecture Workflow

## At a Glance

- **Purpose:** Own the detailed authoring pipeline for complex `create`/`improve` work: choose the correct control lever, preserve semantic requirements, resolve authority/trust, define execution/context/enforcement contracts, choose rewrite scope, render the prompt, and close validation/repair.
- **Load when:** A prompt change is more than a narrow wording edit, when requirements conflict, when runtime/tool/context assumptions matter, or when a reusable prompt must be compiled from an explicit semantic contract.
- **Decision impact:** Determines which layer should control the outcome, which requirements are immutable, how conflicts are resolved, what may be enforced by prompt versus runtime, how much of the artifact may change, and what must be validated before acceptance.
- **Do not load when:** The request is only task execution, translation/summarization, or a trivial wording correction whose requirements and execution assumptions are already unambiguous.

## Contents

- 0. Choose the right lever
- 1. Build the semantic requirement ledger
- 2. Separate three authority questions
- 3. Resolve design conflicts deterministically
- 4. Establish the execution profile
- 5. Design the context contract
- 6. Map enforcement to the lowest reliable layer
- 7. Audit in execution order
- 8. Choose rewrite scope
- 9. Compile the semantic contract into a rendered prompt
- 10. Control degrees of freedom
- 11. Tool/source rules
- 12. Output contract
- 13. Examples
- 14. Candidate change ledger
- 15. Validation and repair

## 0. Choose the right lever

Before rewriting, identify the observable criterion that is failing and the lowest layer that can control it:

1. prompt semantics or presentation;
2. model/configuration;
3. context selection/retrieval;
4. native output/tool schema;
5. application/runtime control or human approval;
6. fine-tuning;
7. broader architecture.

Select `prompt`, `mixed`, or another lever explicitly. If prompt text is not the primary control, do not hide that fact by over-engineering the prompt.

## 1. Build the semantic requirement ledger

Capture each material requirement as one row:

| Field | Meaning |
|---|---|
| `id` | stable identifier |
| `requirement` | concise semantic rule |
| `authority` | `explicit`, `source-required`, `inferred`, or `optional` |
| `protected` | whether the candidate may change/remove it |
| `source` | user, file, URL, repo path, prior prompt section, or assumption |
| `status` | `preserve`, `clarify`, `change`, `remove`, `blocked` |
| `control_class` | semantic, format, authorization, security, side-effect, tooling, evidence, performance, other |
| `enforcement` | prompt, native-schema, tool-schema, application, human-approval, evaluator, mixed |
| `reason` | evidence for any non-preserve status |

Never downgrade an `explicit` or `source-required` protected requirement merely for brevity or style.

## 2. Separate three authority questions

Do not collapse these into one precedence list:

- **design authority**: which design requirement wins while authoring the prompt;
- **runtime instruction authority**: which instruction surface the executor treats as authoritative;
- **data trust**: which content is merely data, quoted/untrusted material, tool output, or trusted instruction input.

Use [runtime-contract.md](runtime-contract.md) when runtime authority or trust is material.

## 3. Resolve design conflicts deterministically

Use this precedence unless higher-priority platform/safety rules override it:

1. explicit user prohibition/requirement for the current design task;
2. legally/safety/compliance-required behavior;
3. explicit source contract or downstream compatibility requirement;
4. explicit behavior in the original prompt;
5. repeated source/project convention;
6. inferred intent;
7. stylistic preference.

If two requirements at the same authority level conflict and no local exception resolves them, mark `blocked` and ask for authority rather than silently choosing.

Specific exceptions beat general rules only when both share the same authority and the exception is clearly scoped.

## 4. Establish the execution profile

Record enough identity to know which prompt strategies and evidence are valid:

- logical executor;
- provider/host/model/snapshot when known and material;
- reasoning/configuration mode when material;
- instruction surfaces and their verified semantics;
- tools and native schema capabilities;
- profile identity or a reproducible capability fingerprint.

Unknown fields may remain explicit for structural work. Behavioral/runtime claims require enough profile identity to make comparison meaningful.

## 5. Design the context contract

When context is material, classify it before rendering:

- stable context;
- dynamic request context;
- untrusted/external context;
- retrieval/selection policy;
- budget;
- placement policy;
- overflow/trimming/summarization behavior;
- provenance requirements.

Do not assume that maximum context or one universal placement strategy is optimal. Use [context-engineering.md](context-engineering.md).

## 6. Map enforcement to the lowest reliable layer

Prompt prose is appropriate for semantic guidance, style, judgment criteria, and model behavior that only the model can perform.

Prefer stronger controls when available:

- exact output syntax -> native structured output/schema;
- tool arguments -> tool schema;
- authorization -> application/runtime policy;
- destructive side effect -> application/runtime + approval where required;
- objective acceptance -> deterministic validator/evaluator;
- uncertain external fact -> source requirement/fallback.

A security, authorization, or side-effect guarantee enforced only with prompt text is a blocking design defect unless the user explicitly accepts prompt-only best-effort behavior and the claim is downgraded accordingly.

## 7. Audit in execution order

Inspect:

1. success criterion/right lever;
2. task/objective;
3. executor/profile;
4. inputs/context;
5. design authority/conflicts;
6. runtime instruction authority and data trust;
7. tools/source access;
8. enforcement layer;
9. workflow/decision order;
10. output contract;
11. examples;
12. safety/privacy;
13. success criteria and validation readiness.

Classify each finding as `observation`, `inference`, `recommendation`, or `blocking-conflict`.

## 8. Choose rewrite scope

### Minimal rewrite

Use when the existing prompt has a sound structure and the defect is narrow. Prefer changing the smallest semantic surface.

### Structural rewrite

Use only when one or more are true:

- execution order is materially confusing;
- constraints are scattered or contradictory;
- output contract cannot be tested;
- examples materially conflict with rules;
- tool/source behavior is unsafe or ambiguous;
- context/authority/enforcement boundaries are materially wrong;
- multiple defects share the same structural cause.

Preserve externally referenced headings, variables, schemas, examples, and section names unless changing them is part of the explicit task.

## 9. Compile the semantic contract into a rendered prompt

For reusable or cross-host work, keep this separation:

`semantic contract -> execution profile -> host/model strategies -> rendered prompt + runtime controls`

The semantic contract owns goals and invariants. The execution profile owns volatile host/model assumptions. The rendered prompt is one deployment artifact, not the sole source of truth.

Use this rendered order when relevant:

1. one-line task instruction;
2. context/role;
3. inputs and assumptions;
4. workflow/decision tree;
5. tool and source rules;
6. constraints/prohibitions;
7. output contract;
8. examples;
9. edge cases/stop conditions.

This is a default, not a mandatory template. Omit empty sections. Do not restructure a governed prompt just to match this order if the current structure is already clear and compatible.

## 10. Control degrees of freedom

Use the lowest reliable control:

- exact syntax/schema -> native format/schema or validator where available;
- repeated defaults -> canonical default;
- tie -> ordered tie-breaker;
- subjective trade-off -> rubric + evidence;
- uncertain fact -> assumption or source requirement;
- unsafe ambiguity -> stop condition.

Do not use examples as the only mechanism for critical behavior. State the rule first; examples illustrate it.

Do not universalize model-specific techniques. XML, examples, roles, self-checks, chain decomposition, and context placement are strategies selected by evidence/profile, not mandatory prompt anatomy.

## 11. Tool/source rules

For each tool or source capability that matters, define:

- trigger;
- allowed inputs;
- prohibited use;
- fallback when unavailable;
- evidence/citation expectations;
- stop condition when absence would make the result unreliable.

Never name a tool the target executor does not actually have unless the prompt explicitly describes an adapter or hypothetical interface.

## 12. Output contract

A strong output contract specifies only what downstream correctness needs:

- structure/order;
- required/optional fields;
- allowed syntax;
- length or granularity constraints when material;
- citation/evidence placement;
- whether code fences are allowed;
- empty/unknown/error representation;
- ordering/tie rules where consumers depend on them.

Avoid ceremonial formatting that adds tokens without reducing ambiguity.

## 13. Examples

Add examples when they stabilize behavior that prose alone leaves ambiguous.

Rules:

- examples follow rules, not replace them;
- use placeholders for user-specific/secrets;
- keep examples internally consistent with constraints;
- preserve user-marked immutable examples exactly;
- include an anti-example only when it clarifies a common failure mode.

## 14. Candidate change ledger

For `improve`, record material changes as:

`requirement id -> baseline behavior -> candidate behavior -> reason -> validation scenario`

A wording-only edit with no behavioral effect need not be listed.

## 15. Validation and repair

Freeze evaluation criteria before candidate mutation when improvement claims matter. Freeze the material execution-profile identity too when behavioral/runtime comparison depends on it.

For each failure:

`scenario -> criterion -> evidence -> causal defect -> smallest repair -> same scenario -> adjacent regressions`

After the same material defect set fails to improve twice, stop that repair branch and report it. Maximum default cycles: three.
