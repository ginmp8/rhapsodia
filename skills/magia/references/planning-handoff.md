# Planning Handoff for MAGIA Execution

Load this reference when RALPH executes a spec package, PRD, technical design, roadmap-derived package, governance-derived package, architecture decision, or other board artifact authored outside MAGIA.

## Contract

Planning-origin artifacts are execution inputs for MAGIA. Their authoring boundary describes who created or owns the artifact, not what MAGIA is allowed to implement during execution.

MAGIA may implement code, configuration, tests, scripts, migrations, local tooling, technical documentation, and implementation ADRs when the selected task requires those changes and the repository provides enough scope and validation evidence to do so truthfully.

MAGIA may fill safe implementation gaps that Mago did not spell out when repository evidence, technical design, tasks, validation plan, and acceptance criteria are sufficient. This is technical execution refinement, not PRD refinement.

## Non-Blocker Rules

Do not block merely because:

- the selected task requires implementation;
- the package, PRD, or task plan was authored by a planning or governance workflow;
- the manifest status is `planned` or phase is `define` before execution starts;
- the active package includes roadmap, discovery, source-reference, or governance traceability;
- a task is written in product language but can be mapped to a small, verifiable repository change;
- Mago omitted low-level implementation details that can be safely derived from code and validation evidence.

These are not execution blockers by themselves.

## Real Blocker Rules

Return BLOCKED only when a concrete execution blocker remains after inspecting the selected package and directly relevant repository evidence. Real blockers include:

- no repository target, module, package, interface, command, or allowed write area can be resolved;
- the selected task contradicts PRD, task metadata, dependencies, architecture decisions, or existing repository truth;
- required credentials, services, proprietary inputs, or unavailable dependencies are necessary for truthful implementation;
- no observable validation path or credible fallback validation can be defined;
- completing the work would require changing product intent, PRD content, task definitions, ordering, ownership, or acceptance criteria;
- safe execution would require reading secrets or unrelated blocked paths.

## Execution Handoff Interpretation

When explicit file targets are missing, derive the narrowest safe target from the selected package in this order:

1. task metadata and acceptance criteria;
2. architecture decisions, technical-design.md, and source_of_truth references;
3. PRD behavior and non-goals;
4. existing repository structure, naming, tests, and local conventions;
5. validation.md commands or fallback checks.

If those sources are sufficient, implement the smallest safe change. If they are insufficient, record the missing evidence as BLOCKED.

## Status and Evidence

- If implementation runs and validation proves the selected task, mark the task done and synchronize execution records.
- If implementation starts but validation is incomplete or residual work remains, record IN_PROGRESS and leave the checkbox unchecked unless the task is truthfully complete.
- If a concrete blocker prevents implementation, record BLOCKED and leave the checkbox unchecked.
- Do not convert a planning-origin package into a blocker. Convert only concrete missing execution evidence into a blocker.
- If execution creates an implementation ADR, link it from the execution log or evidence record and state whether Mago handoff is required.
