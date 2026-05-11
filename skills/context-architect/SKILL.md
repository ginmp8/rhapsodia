---
name: context-architect
description: use when asked to plan, scope, audit, or execute codebase changes that may span multiple files, modules, services, tests, or dependency boundaries. identifies primary and secondary files, imports, exports, usages, type references, existing conventions, test coverage, ripple effects, breaking-change risks, and a safe implementation sequence before editing. use for repository tasks, refactors, feature implementation planning, pull request preparation, dependency-impact analysis, and code-review planning. do not use for generic single-snippet questions, non-code product planning, or skill-package work unless the task is specifically about repository context mapping.
---

# Context Architect

## Purpose

Plan codebase work by mapping relevant context before implementation. The skill favors evidence from the repository over assumptions, finds existing patterns before inventing new ones, and makes multi-file change plans explicit enough for review.

## Core rule

Before modifying repository files, produce a context map. If the user already supplied an approved context map or explicitly asks to continue from a previous map, update the map only where the repository evidence has changed and then proceed.


## Scope

Own repository context mapping for code changes, refactors, feature implementation plans, dependency-impact analysis, PR preparation, and code-review planning. Do not own product governance, generic single-snippet explanation, skill-package hardening, or implementation that bypasses repository evidence.

## Required inputs

Resolve or conservatively infer these before producing a final context map:

1. Task description or change objective.
2. Available repository evidence: paths, diff, branch, failing test, stack trace, linked issue, or searchable codebase.
3. Desired mode: `context-map-only`, `implementation-plan`, `review-impact`, or `apply-after-approved-map`.
4. Safety constraints: blocked paths, generated files, migrations, secrets, production data, and user-declared read-only files.
5. Validation expectation: tests, build, lint, type check, reproduction command, or reason validation is unavailable.

## Mode selection

| User intent | Mode | Primary output | Edit allowed |
|---|---|---|---|
| Understand scope before work | `context-map-only` | context map with risks and validation plan | no |
| Prepare implementation | `implementation-plan` | context map plus ordered change plan | no |
| Review a diff or PR | `review-impact` | impacted files, hidden dependencies, risk and test gaps | no |
| Continue after an approved map | `apply-after-approved-map` | mapped edits plus validation summary | yes, after re-reading evidence |

## Workflow decision tree

1. **No repository or files available**: provide a lightweight context-discovery checklist and ask for the minimum missing artifact: repository access, paths, diff, failing test, stack trace, or relevant files.
2. **Single self-contained snippet**: answer normally; use this skill only if the snippet implies hidden call sites, tests, configuration, generated code, schema, or runtime dependencies.
3. **Multi-file or uncertain scope**: run the context mapping workflow before edits.
4. **User asks to implement**: first show the context map, then pause for approval unless the conversation already contains an explicit approval for the same plan.
5. **User asks for review or PR planning**: produce the context map plus risks, validation plan, and recommended PR split.

## Context mapping workflow

Use available repository tools and local shell commands to gather evidence. Do not assume file locations when search is available.

1. **Clarify the task in one sentence** from the user's request.
2. **Search for primary files** using names, symbols, endpoints, commands, config keys, error messages, and domain terms.
3. **Trace dependencies and usages**: imports, exports, interfaces, subclasses, handlers, dependency injection registrations, generated code, schemas, migrations, config, and feature flags.
4. **Find existing patterns**: nearby implementations, similar tests, conventions, naming, error handling, observability, transaction boundaries, validation, and rollout strategy.
5. **Identify tests and validation commands**: unit, integration, contract, migration, end-to-end, linters, type checks, build steps, and targeted reproduction commands.
6. **Estimate ripple effects**: breaking API changes, behavior changes, data migration risks, concurrency hazards, backwards compatibility, observability gaps, and operational risk.
7. **Plan the sequence**: order changes so compile-time, runtime, and test failures stay diagnosable.

For detailed command patterns, consult `references/dependency-tracing.md`. For the output format, consult `references/context-map-contract.md`.

## Required context map output

Use this structure unless the user asks for a shorter answer:

```markdown
## Context Map for: [task]

### Scope classification
- Change type: [bugfix | feature | refactor | migration | config | test | investigation]
- Scope confidence: [high | medium | low] - [why]
- Repository evidence inspected: [files, searches, diffs, commands]

### Primary files
- `path/to/file` - [why it is likely directly modified]

### Secondary files and dependencies
- `path/to/file` - [relationship, import, usage, registration, config, generated artifact, test, or runtime dependency]

### Test coverage and validation
- `path/to/test` - [what it covers]
- Commands: `[targeted command]`

### Patterns to follow
- `path/to/similar/file` - [specific convention to match]

### Ripple effects and risks
- [risk] - [mitigation]

### Suggested sequence
1. [first safe change]
2. [second safe change]

### Open questions or blockers
- [only include if they block safe execution]
```

If the map is based on incomplete repository access, mark it as provisional and state exactly what evidence is missing.

## Implementation workflow after approval

1. Re-read the primary files immediately before editing.
2. Apply changes in the suggested sequence.
3. Keep each edit aligned with an identified existing pattern or explicitly justify a new pattern.
4. Update or add tests near the changed behavior.
5. Run the narrowest useful validation first, then broader validation if the change touches shared APIs or infrastructure.
6. Summarize the final result with files changed, validation outcomes, residual risks, and any follow-up PR split.

## Review and PR-splitting rules

- Prefer smaller PRs when the context map spans unrelated domains, public interfaces plus large refactors, schema changes plus application logic, or many independent call sites.
- Warn about breaking changes before proposing edits.
- Separate mechanical renames from behavior changes when feasible.
- For migration or schema work, identify expand-contract options before destructive changes.
- For generated code, identify the source artifact and generator command before editing generated output.

## Supporting resources

- `references/context-map-contract.md`: strict output contract and compact variants.
- `references/dependency-tracing.md`: language-agnostic and ecosystem-specific tracing heuristics.
- `references/change-sequencing.md`: safe ordering, PR splitting, and validation strategy.
- `references/risk-and-validation-checklist.md`: risk checklist for code, config, data, API, security, and operations.
- `references/upstream-source.md`: attribution and adaptation notes for the upstream Context Architect agent.
- `assets/templates/context-map.md.template`: reusable template for context maps.
- `scripts/generate_context_map_skeleton.py`: generates a markdown context-map skeleton.
- `scripts/validate_context_architect_skill.py`: validates package structure and scenario schema.
- `scripts/package_skill.py`: packages this skill as `skill.zip` after structural checks.
- `evals/activation-scenarios.json`: planned activation, boundary, and edge scenarios.
- `examples/example-context-map.md`: example of a filled context map for calibration.

## Stop conditions

Stop before editing and report a blocker when:

- repository evidence is unavailable and the requested edit could affect unknown files;
- the change may expose or modify secrets, credentials, production data, or access-control rules without explicit safe context;
- the work requires destructive data changes without migration, rollback, or compatibility evidence;
- the user asks to skip the context map for a multi-file change and no prior approved map exists;
- validation cannot be run or reasoned about for a high-risk change.
