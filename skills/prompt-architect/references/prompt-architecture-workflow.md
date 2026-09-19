# Prompt Architecture Workflow

Use this reference for `create` and `improve` work that needs more than a narrow wording edit.

## 1. Build the requirement ledger

Capture each material requirement as one row:

| Field | Meaning |
|---|---|
| `id` | stable identifier |
| `requirement` | concise semantic rule |
| `authority` | `explicit`, `source-required`, `inferred`, or `optional` |
| `protected` | whether the candidate may change/remove it |
| `source` | user, file, URL, repo path, prior prompt section, or assumption |
| `status` | `preserve`, `clarify`, `change`, `remove`, `blocked` |
| `reason` | evidence for any non-preserve status |

Never downgrade an `explicit` or `source-required` protected requirement merely for brevity or style.

## 2. Resolve conflicts deterministically

Use this precedence unless higher-priority platform/safety rules override it:

1. explicit user prohibition/requirement for the current task;
2. legally/safety/compliance-required behavior;
3. explicit source contract or downstream compatibility requirement;
4. explicit behavior in the original prompt;
5. repeated source/project convention;
6. inferred intent;
7. stylistic preference.

If two requirements at the same authority level conflict and no local exception resolves them, mark `blocked` and ask for authority rather than silently choosing.

Specific exceptions beat general rules only when both share the same authority and the exception is clearly scoped.

## 3. Audit in execution order

Inspect:

1. task/objective;
2. intended executor and audience;
3. inputs/context;
4. authority and conflicts;
5. tools and source access;
6. workflow/decision order;
7. output contract;
8. examples;
9. safety/privacy;
10. success criteria and validation readiness.

Classify each finding as:

- `observation` — directly visible;
- `inference` — plausible but not explicit;
- `recommendation` — proposed design choice;
- `blocking-conflict` — cannot be safely resolved without authority.

## 4. Choose rewrite scope

### Minimal rewrite

Use when the existing prompt has a sound structure and the defect is narrow. Prefer changing the smallest semantic surface.

### Structural rewrite

Use only when one or more are true:

- execution order is materially confusing;
- constraints are scattered or contradictory;
- output contract cannot be tested;
- examples materially conflict with rules;
- tool/source behavior is unsafe or ambiguous;
- multiple defects share the same structural cause.

Preserve externally referenced headings, variables, schemas, examples, and section names unless changing them is part of the explicit task.

## 5. Canonical prompt architecture

Use this order when relevant:

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

## 6. Control degrees of freedom

Use the lowest reliable control:

- exact syntax/schema -> explicit format or validator;
- repeated defaults -> canonical default;
- tie -> ordered tie-breaker;
- subjective trade-off -> rubric + evidence;
- uncertain fact -> assumption or source requirement;
- unsafe ambiguity -> stop condition.

Do not use examples as the only mechanism for critical behavior. State the rule first; examples illustrate it.

## 7. Tool/source rules

For each tool or source capability that matters, define:

- trigger;
- allowed inputs;
- prohibited use;
- fallback when unavailable;
- evidence/citation expectations;
- stop condition when absence would make the result unreliable.

Never name a tool the target executor does not actually have unless the prompt explicitly describes an adapter or hypothetical interface.

## 8. Output contract

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

## 9. Examples

Add examples when they stabilize behavior that prose alone leaves ambiguous.

Rules:

- examples follow rules, not replace them;
- use placeholders for user-specific/secrets;
- keep examples internally consistent with constraints;
- preserve user-marked immutable examples exactly;
- include an anti-example only when it clarifies a common failure mode.

## 10. Candidate change ledger

For `improve`, record material changes as:

`requirement id -> baseline behavior -> candidate behavior -> reason -> validation scenario`

A wording-only edit with no behavioral effect need not be listed.

## 11. Validation and repair

Freeze evaluation criteria before candidate mutation when improvement claims matter.

For each failure:

`scenario -> criterion -> evidence -> causal defect -> smallest repair -> same-scenario rerun`

After the same material defect set fails to improve twice, stop that repair branch and report it. Maximum default cycles: three.
