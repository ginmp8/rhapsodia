# Define Mode

## Purpose

Create or complete one full planning package for an already registered spec.

## Inputs

- one valid registry record;
- repository and governance evidence;
- package shape and source candidates from the selected registry handoff.

## Workflow

1. Validate cycle, registry, and existing package identity.
2. Load linked discovery evidence and relevant repository truth.
3. Create missing package artifacts through `scripts/write_artifact_scaffold.py`.
4. Populate PRD, tasks, notes, validation, and optional technical design with bounded evidence-backed content.
5. Keep immutable identity aligned with cycle and registry metadata.
6. Update only the selected registry record when planning status or handoff truth changes.
7. Validate package, evidence contract, and board.

## Package Contract

A full package normally contains:

- `manifest.yaml`: immutable identity, feature metadata, planning status/phase, source map, traceability;
- `prd.md`: problem, goals, scope, exclusions, acceptance criteria, dependencies;
- `tasks.md`: bounded task decomposition with task-local dependencies and validation expectations;
- `notes.md`: planning findings, assumptions, risks, blockers, open questions;
- `validation.md`: planned checks, commands, environments, expected evidence, and not-run state;
- `technical-design.md` only when architecture/contract/data/security/operations alignment is material.

## Rules

- never create or edit a shared catalog/queue inside `BOARD_ROOT`;
- never regenerate IDs or derive them from order;
- never copy dynamic template values blindly;
- do not claim implementation, runtime validation, completion, or approval;
- preserve MAGIA-owned execution evidence;
- if a required value is not justified, record an assumption/blocker instead of inventing it.
