# Correction Input Contract

## Purpose

Convert the review into a self-contained instruction set that another AI, skill improver, or human maintainer can execute without reading the original conversation.

## Inclusion rules

Include:

- exact target and objective;
- writable and read-only scope;
- preserved behavior and non-goals;
- confirmed required fixes in dependency order;
- selected likely fixes only when explicitly marked;
- exact paths and finding IDs;
- acceptance criteria per fix;
- validation commands and scenarios;
- reporting and package completion criteria.

Exclude:

- hidden reasoning;
- vague instructions such as "improve quality";
- speculative findings presented as mandatory fixes;
- unrelated redesign ideas;
- unsupported benchmark or readiness claims;
- security review requirements unless the user explicitly routes that work to another skill.

## Required shape

Use a fenced Markdown block so it can be copied intact.

```markdown
You are correcting the skill package `<TARGET>`.

## Objective
Resolve the evidence-backed defects from the review while preserving the skill's declared purpose, activation boundaries, outputs, and valid existing behavior.

## Mode
`apply-corrections`, followed by validation. Package only when requested and all required gates pass.

## Writable Scope
- `<target skill root>` only.

## Read-only / Protected Scope
- supplied fixtures, expected outputs, frozen evaluators, previous reports, unrelated repositories, generated evidence, and any user-declared protected paths.

## Preserve
- <behavior or contract that must not regress>

## Non-goals
- no unrelated redesign;
- no feature expansion unless required to close a listed finding;
- no weakening of activation, output, evidence, validation, or stop-condition contracts;
- no security audit in this correction workflow.

## Required Fixes

### F-001 - <title>
- Severity: ...
- Location: ...
- Problem: ...
- Required change: ...
- Acceptance criteria:
  1. ...
- Validation:
  - command or scenario
- Dependencies: none

## Questions Blocking a Fix
- <only decision-relevant unanswered questions>

## Validation Sequence
1. structural preflight;
2. affected script syntax or smoke tests;
3. activation/non-activation/ambiguous/edge scenarios;
4. local-link and package-hygiene checks;
5. report or package validation required by the target.

## Completion Report
Return:
- files changed;
- finding-by-finding closure status;
- commands executed and results;
- unresolved questions or accepted trade-offs;
- before/after score only when the same rubric/evaluator was applied;
- package path only when packaging was requested, the archive exists, and validation passed.
```

## Ordering rules

1. Repair root/package blockers.
2. Repair activation and boundary defects.
3. Repair workflow and output-contract defects.
4. Repair contradictions and resource integration.
5. Repair validators and evals.
6. Clean package noise and token duplication only after behavior is stable.
7. Revalidate after any compression or cleanup mutation.

## Quality checks

The correction input is ready only when:

- every required fix maps to a report finding;
- no finding depends on omitted evidence;
- acceptance criteria are observable;
- validations can distinguish fixed from unfixed behavior;
- dependencies and ordering are explicit;
- protected paths and non-goals prevent scope drift;
- the input makes no claim that fixes are already applied.
