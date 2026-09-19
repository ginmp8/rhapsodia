# Correction Input Contract

## Purpose

Convert the review into a self-contained instruction set that another AI, skill improver, or human maintainer can execute without reading the original conversation.

## Inclusion rules

Include:

- exact target and objective;
- writable and read-only scope;
- preserved current behavior and non-goals;
- current canonical sources and owners;
- confirmed required fixes in dependency order;
- selected likely fixes only when explicitly marked;
- legacy classification and canonical replacement for legacy-related fixes;
- exact paths and finding IDs;
- acceptance criteria per fix;
- positive current tests and negative rejection tests;
- validation commands and scenarios;
- reporting and package completion criteria.

Exclude:

- hidden reasoning;
- vague instructions such as "improve quality";
- speculative findings presented as mandatory fixes;
- deletion based only on a word, filename, age, or version label;
- unrelated redesign ideas;
- unsupported benchmark, compatibility, or readiness claims;
- historical prose reintroduced only to satisfy a textual gate;
- security review requirements unless the user explicitly routes that work to another skill.

## Required shape

Use a fenced Markdown block so it can be copied intact.

```markdown
You are correcting the skill package `<TARGET>`.

## Objective
Resolve the evidence-backed defects from the review while preserving the skill's current declared purpose, activation boundaries, owners, outputs, canonical contracts, and valid existing behavior.

## Mode
`apply-corrections`, followed by validation. Package only when requested and all required gates pass.

## Writable Scope
- `<target skill root>` only.

## Read-only / Protected Scope
- supplied fixtures, expected outputs, frozen evaluators, previous reports, unrelated repositories, generated evidence, peer skills unless explicitly writable, and any user-declared protected paths.

## Preserve
- <current behavior or contract that must not regress>
- real historical release numbers in factual changelog entries;
- valid migration-only behavior only when every isolation gate remains satisfied.

## Non-goals
- no unrelated redesign;
- no feature expansion unless required to close a listed finding;
- no weakening of activation, ownership, output, evidence, validation, compatibility, or stop-condition contracts;
- no implicit backward compatibility;
- no security audit in this correction workflow.

## Legacy and Compatibility Constraints
- treat the listed canonical sources as authoritative unless a blocking contradiction is proved;
- remove `obsolete`, consolidate `duplicate`, repair `contradictory`, and remove or externalize `noise`;
- preserve `current` items;
- keep `migration-only` items only in an explicit isolated adapter mode;
- do not decide `blocked` items until the named evidence is obtained;
- normal flows must reject old schemas, fields, states, paths, identifiers, and versions;
- migration output must be converted to the current format before normal mutation or handoff;
- do not add historical text to satisfy keyword-based validators;
- replace fragile textual gates with structural or behavioral validation;
- preserve owner boundaries and remove direct runtime peer-skill coupling unless explicitly current and justified.

## Canonical Sources
| Concept | Source | Owner/writer | Consumers |
|---|---|---|---|

## Required Fixes

### F-001 - <title>
- Severity: ...
- Category: ...
- Legacy classification: ... | not applicable
- Canonical source: ... | not applicable | unresolved
- Location: ...
- Problem: ...
- Required change: ...
- Acceptance criteria:
  1. ...
- Validation:
  - positive current scenario or command;
  - negative legacy-rejection scenario when applicable.
- Dependencies: none

## Questions Blocking a Fix
- <only decision-relevant unanswered owner, consumer, version, migration, or compatibility questions>

## Validation Sequence
1. structural preflight and local-link validation;
2. affected script syntax or smoke tests;
3. current positive scenarios;
4. explicit rejection of removed aliases, schemas, states, paths, identifiers, and versions;
5. migration isolation, failure atomicity, and loss-reporting tests when a migration remains;
6. producer/consumer and ownership checks for shared contracts;
7. activation/non-activation/ambiguous/edge scenarios;
8. package-hygiene and reproducible-archive checks;
9. report or package validation required by the target.

## Completion Report
Return:
- files changed;
- finding-by-finding closure status;
- legacy classification result for each corrected candidate;
- current canonical sources after correction;
- commands and positive/negative tests executed with results;
- removed, consolidated, isolated, preserved, and blocked item counts;
- unresolved questions or accepted trade-offs;
- before/after score only when the same rubric/evaluator was applied;
- package path only when packaging was requested, the archive exists, and validation passed.
```

## Ordering rules

1. Resolve ambiguous roots and canonical-source contradictions.
2. Repair root/package blockers.
3. Repair activation and boundary defects.
4. Remove implicit legacy acceptance and unauthorized ownership transfers from common paths.
5. Repair workflow and output-contract defects.
6. Isolate valid migrations and convert their output to the current contract.
7. Consolidate duplicated contracts and resource drift.
8. Repair validators, producer/consumer tests, rejection tests, and evals.
9. Remove obsolete examples, tests, scripts, changelog instructions, residue, and context noise.
10. Revalidate after any compression, cleanup, or package mutation.

## Quality checks

The correction input is ready only when:

- every required fix maps to a report finding;
- no finding depends on omitted evidence;
- every legacy-related fix includes classification and canonical source or states `unresolved`;
- no deletion instruction relies only on a search match;
- acceptance criteria are observable;
- validations distinguish current acceptance from obsolete rejection;
- migration-only behavior has explicit isolation validation;
- dependencies and ordering are explicit;
- protected paths and non-goals prevent scope drift;
- the input makes no claim that fixes are already applied.
