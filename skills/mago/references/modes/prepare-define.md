# Prepare-Define Mode

## Purpose

Seed the smallest truthful package for exactly one already registered spec. Preparation converts registry handoff intent into a structurally valid package shell; it does not complete unsupported planning content.

## Inputs

- resolved canonical `BOARD_ROOT` and `cycle.yaml`;
- exactly one `registry/<spec_id>.yaml` record;
- linked discovery, governance, repository, and imported-source evidence;
- downstream mode, package shape, seed artifacts, and blockers from the registry handoff.

Old layouts must be adapted before package creation.

## Workflow

1. Validate cycle, registry, dependencies, and selected handoff.
2. Confirm the target `specs/<spec_id>/` is absent or belongs to the same immutable identity.
3. Load linked candidate docs and referenced source files as read-only evidence.
4. Create only artifacts listed by `handoff.seed_artifacts` and justified by package shape/evidence.
5. Use `scripts/write_artifact_scaffold.py`; populate immutable fields from cycle/registry metadata and never regenerate IDs.
6. Preserve source paths and evidence classes in manifest/notes/traceability.
7. Replace placeholders only where evidence supports values; keep unresolved assumptions/blockers explicit.
8. Validate package, planning/execution handoff, evidence contract, and board.
9. Update only the selected registry handoff/status when the new package state is truthfully established.

## Package Shapes

- `full`: manifest, PRD, tasks, notes, validation; technical design only when material;
- `product_only`: PRD, notes, optional product validation;
- `tasks_only`: tasks only when product scope already exists and is sufficient.

Do not seed files outside the declared shape merely to make a package look complete.

## Rules and Stop Conditions

- do not create/edit shared aggregate files;
- do not invent scope, tasks, dependencies, validation results, execution history, completion, or approval;
- package, registry, and cycle identities must agree;
- preserve original-solution references as read-only evidence;
- stop on ambiguous identity, contradictory evidence, unresolved dependencies, unsupported seed artifacts, or existing package conflict;
- truthful partial preparation with recorded blockers is preferable to unsupported completeness.
