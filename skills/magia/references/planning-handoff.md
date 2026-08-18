# Planning Handoff for MAGIA Execution

Load when RALPH executes a spec package, PRD, technical design, roadmap/governance package, architecture decision, or board artifact authored outside MAGIA.

## Contract

Planning-origin artifacts are execution inputs for MAGIA. Authorship states provenance, not implementation permission. MAGIA may implement code, config, tests, scripts, migrations, local tooling, technical docs, and implementation ADRs when the selected task requires them and repo evidence gives enough scope and validation.

Handoff is bidirectional. Mago plans, Magia executes, and nomia interprets delivery implications. MAGIA returns technical gaps to Mago through `technical-gap-note.md`, implementation ADRs, implementation notes, or validation evidence; MAGIA returns delivery-impact evidence to nomia only as source evidence, not as stakeholder communication authored by MAGIA.

MAGIA may fill safe implementation gaps Mago did not detail when repository evidence, technical design, execution-handoff-plan.md, tasks, validation plan, and acceptance criteria are sufficient. This is technical execution refinement, not PRD refinement.

## Typed Envelope Handoff

Validate `mago_to_magia` with local `scripts/ecosystem_handoff.py` before treating planning references as an execution entry. The envelope must identify the Mago package version, canonical `spec_id`, planning state, requirement and acceptance references, selected task ids, validation references, technical criticality, execution sequence, provenance, freshness, unknowns, and conflicts. It remains planning evidence, not runtime proof.

After execution, build `magia_to_mago` when implementation findings require planning reconciliation and `magia_to_nomia` when current execution or validation evidence has delivery impact. The producer automatically adds contract-v3 state projections for Nomia. Do not freehand `complete` or `passed` governance-facing states, and do not use the envelope to close governance or accept business risk.

```text
python scripts/ecosystem_handoff.py validate --input <mago-handoff.json> --operation consume
python scripts/ecosystem_handoff.py build --direction magia_to_mago --payload <payload.json> --source <validation-evidence> --authority magia --evidence-ref <ref> --output <handoff.json>
```

## Non-Blockers

Do not block merely because the task requires implementation; the package/PRD/task plan came from planning or governance; manifest is `planned` or phase `define`; roadmap/discovery/source-reference/governance traceability exists; product-language task maps to a small verifiable repo change; or Mago omitted low-level detail derivable from code and validation evidence.

## Real Blockers

Return BLOCKED only when a concrete execution blocker remains after inspecting the selected package and relevant repo evidence. Real blockers: no repo target/module/interface/command/allowed write area; contradiction with PRD, metadata, dependencies, ADRs, or repo truth; required credentials/services/proprietary inputs/unavailable dependencies; no observable or credible fallback validation path; work requires changing product intent, PRD, task definitions, ordering, ownership, or acceptance criteria; safe execution would require secrets or unrelated blocked paths.

## Target Derivation

When file targets are missing, derive the narrowest safe target from: task metadata and acceptance criteria; architecture decisions, technical-design.md, execution-handoff-plan.md, and source_of_truth refs; PRD behavior/non-goals; existing repo structure, naming, tests, conventions; validation.md planned commands or fallbacks. If sufficient, implement the smallest safe change; otherwise record missing evidence as BLOCKED.

## Status and Evidence

- If implementation plus validation proves the selected task, mark it done and sync records.
- If implementation starts but validation is incomplete or work remains, record IN_PROGRESS and leave checkbox unchecked unless truthfully complete.
- If a concrete blocker prevents implementation, record BLOCKED and leave checkbox unchecked.
- Do not convert planning provenance into a blocker.
- Link implementation ADRs from implementation-notes.md and validation-evidence.md, and state Mago handoff need. Treat execution-handoff-plan.md as planned input, not proof of implementation.
- If execution evidence affects release posture, stakeholder risk, owner, due date, roadmap priority, accepted business risk, or go/no-go decisions, record the evidence and hand off to nomia; do not update delivery governance artifacts from MAGIA.
