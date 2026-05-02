# Planning Handoff for MAGIA Execution

Load when RALPH executes a spec package, PRD, technical design, roadmap/governance package, architecture decision, or board artifact authored outside MAGIA.

## Contract

Planning-origin artifacts are MAGIA execution inputs. Authorship states provenance, not implementation permission. MAGIA may implement code, config, tests, scripts, migrations, local tooling, technical docs, and implementation ADRs when the selected task requires them and repo evidence gives enough scope and validation.

MAGIA may fill safe implementation gaps Mago did not detail when repository evidence, technical design, tasks, validation plan, and acceptance criteria are sufficient. This is technical execution refinement, not PRD refinement.

## Non-Blockers

Do not block merely because the task requires implementation; the package/PRD/task plan came from planning or governance; manifest is `planned` or phase `define`; roadmap/discovery/source-reference/governance traceability exists; product-language task maps to a small verifiable repo change; or Mago omitted low-level detail derivable from code and validation evidence.

## Real Blockers

Return BLOCKED only after inspecting the selected package and relevant repo evidence. Real blockers: no repo target/module/interface/command/allowed write area; contradiction with PRD, metadata, dependencies, ADRs, or repo truth; required credentials/services/proprietary inputs/unavailable dependencies; no observable or credible fallback validation path; work requires changing product intent, PRD, task definitions, ordering, ownership, or acceptance criteria; safe execution would require secrets or unrelated blocked paths.

## Target Derivation

When file targets are missing, derive the narrowest safe target from: task metadata and acceptance criteria; architecture decisions, technical-design.md, and source_of_truth refs; PRD behavior/non-goals; existing repo structure, naming, tests, conventions; validation.md commands or fallbacks. If sufficient, implement the smallest safe change; otherwise record missing evidence as BLOCKED.

## Status and Evidence

- If implementation plus validation proves the selected task, mark it done and sync records.
- If implementation starts but validation is incomplete or work remains, record IN_PROGRESS and leave checkbox unchecked unless truthfully complete.
- If a concrete blocker prevents implementation, record BLOCKED and leave checkbox unchecked.
- Do not convert planning provenance into a blocker.
- Link implementation ADRs from execution log/evidence and state Mago handoff need.
