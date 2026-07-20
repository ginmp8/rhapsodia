# MAGO Operating Rules

Use this reference for ambiguous ownership, mixed planning/execution intent, or unclear artifact boundaries.

## Ownership

MAGO owns planning records under the resolved canonical cycle root. It does not own implementation code, runtime evidence, delivery governance, stakeholder reporting, release notes, portfolio artifacts, or unrelated documentation. For mixed requests, complete only the planning-safe portion and hand execution/governance to the owning workflow.

## Canonical Write Rules

- resolve the canonical model and `BOARD_ROOT` before the first write;
- create cycle/spec identities only through the atomic identity script;
- write one independent registry record per spec;
- never create a duplicate board tree or shared editable catalog/queue;
- preserve immutable IDs, truthful history, MAGIA evidence, and source traceability;
- prefer bounded updates to existing registry/package artifacts over duplicates;
- keep all generated views outside the canonical root;
- record missing facts as blockers, assumptions, or open questions in the relevant artifact.

## Mode Discipline

Select exactly one primary mode. Reading adjacent evidence is allowed; writing another mode's artifacts is not unless a multi-stage request executes that mode as a separate bounded stage with its own validation outcome.

- discovery creates evidence/candidates, not registry/package files;
- order creates/reconciles registry records, not package PRDs;
- prepare-define seeds one registered package without unsupported content;
- product-only modes do not modify tasks;
- task-only modes do not modify product intent;
- technical-design does not become implementation/runbook output;
- execution evidence remains MAGIA-owned.

## Evidence Standard

Planning claims trace to repository inspection, current canonical artifacts, user/governance evidence, source-attributed MAGIA evidence, explicit assumptions, or validator output. Distinguish observed, inferred, planned, and measured claims. Do not convert guesses into identity, status, priority, dependencies, handoff readiness, completion, approval, specialist assignments, or runtime behavior.

## Planning/Execution Boundary

Planning authority is not an implementation prohibition. Define executable downstream tasks when scope and validation are credible. Do not mark work blocked solely because code/config/tests are required; hand it to MAGIA and reserve blockers for missing scope, files, dependencies, credentials, evidence, or validation paths.

## Handoff Reporting

When stopping at the planning boundary, state the selected mode, resolved identity/path, artifacts changed, validators run, what was intentionally not performed, downstream owner, and unresolved blockers. Never imply implementation or validation occurred when it did not.
