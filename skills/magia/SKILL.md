---
name: magia
description: use when asked to execute, audit, validate, harden, document, unblock, or package bounded repository work in magia. supports adhoc direct code or config changes, targeted tests, local validators, execution evidence, and ralph execution from a concrete board contract plus selected spec package. expects repository scope, selected mode inputs, observable validation, and truthful execution-state synchronization. do not use for roadmap shaping, stakeholder updates, release notes, portfolio reporting, broad planning, or claims without current evidence.
---

# MAGIA

MAGIA executes bounded repository work from current code, runtime evidence, and resolved board-contract artifacts. It owns implementation, validation, unblocking, hardening, and execution-record synchronization for scoped repository work. It does not own roadmap shaping, stakeholder communication, release notes, portfolio reporting, broad planning, or unvalidated completion claims.

## Load Order

1. Decide whether the request is executable repository work, a blocker, or a planning handoff.
2. Load [references/canonical-paths.md](references/canonical-paths.md) and [references/common-execution.md](references/common-execution.md).
3. Load exactly one mode reference from [references/modes/](references/modes/): ADHOC for direct work or RALPH for board-contract execution.
4. Load [references/artifacts/execution-records.md](references/artifacts/execution-records.md) only when controlled execution records may change.
5. Load [references/artifacts/execution-evidence.md](references/artifacts/execution-evidence.md) only when structured downstream evidence is requested or useful.
6. Load [references/validation-and-closure.md](references/validation-and-closure.md) before finalizing any run that changed code, docs, validation evidence, task state, or execution state.
7. Load [references/markdown-writing.md](references/markdown-writing.md) when generating or editing durable Markdown records.
8. Load [references/package-delivery.md](references/package-delivery.md) only when validating, exporting, or packaging the MAGIA skill itself.
9. Use [references/resource-map.md](references/resource-map.md), [scripts/](scripts/), [assets/templates/](assets/templates/), [examples/](examples/), and [evals/](evals/) only when scaffolding, validating, packaging, or checking activation behavior.

## Mode Selection Matrix

| Situation | Mode | Required inputs | Primary output | Closure gate |
|---|---|---|---|---|
| Direct code, configuration, test, validator, or documentation change not driven by a board package | ADHOC | Repository scope, target behavior or files, requested outcome, observable success check | Smallest safe change plus validation evidence | Targeted checks pass or residual gap is reported |
| Execution from a concrete board contract and one selected spec package | RALPH | Concrete board root or resolvable ids, selected spec id, selected task or dependency-safe batch, repository scope | Implementation plus truthful synchronized execution records | Board and spec validators pass when local repository files are available |
| Request changes product intent, task definitions, sequencing, roadmap, ownership, or governance outputs | Planning handoff | Evidence of the planning gap | Blocker or handoff summary only | No planning artifact rewritten by MAGIA |
| Required roots, selected ids, target files, or validation evidence are missing | Blocker | Missing input list and partial evidence gathered | Honest blocker with any safe partial work | No invented state or completion claim |

## Required Inputs by Mode

Resolve these before mutating repository or board files:

- ADHOC: repository root or file scope, requested behavior, target files when known, allowed write scope, blocked paths, and at least one observable validation command or check.
- RALPH: board root or resolvable board id plus cycle version, selected spec id, selected task id or dependency-safe batch, repository scope, allowed write scope, and applicable board/spec validators.
- Package validation: target skill root, requested artifact path, packaging exclusions, and the package validator command that must pass before claiming readiness.
- Blocker or handoff: exact missing inputs, evidence already inspected, and the next specific evidence needed.

## Execution Workflow

1. Resolve the mode and concrete scope before editing. If the request is still ambiguous, inspect available repository or board evidence first, then continue only when the conservative scope remains truthful and bounded.
2. Load only the references needed for that branch. Do not load both ADHOC and RALPH mode references unless the request truly spans both modes.
3. Inspect the relevant repository files, runtime evidence, and active contract artifacts for the chosen mode.
4. Define at least one observable validation check before treating work as complete.
5. Make the smallest safe change that satisfies the selected executable objective.
6. Use local scripts before manual editing for template-backed writes, execution logs, execution-state sync, healing, artifact validation, boundary validation, and package validation.
7. Keep implementation, validation evidence, task state, notes, manifest state, and catalog state aligned when RALPH records change.
8. Run the narrowest validation set that proves the work and the mechanical MAGIA validators that apply.
9. Finalize with concise evidence: what changed, what passed, what failed or was not run, and what remains.

## Operating Rules

- Treat repository code, runtime output, and resolved board-contract artifacts as the source of truth.
- Preserve unknowns as unknown. Never invent product behavior, owners, task status, validation results, branch names, pull requests, releases, deployment evidence, or acceptance evidence.
- Prefer focused changes over broad rewrites or unrelated refactors.
- Keep MAGIA-created or MAGIA-updated durable documentation inside the active board root.
- Treat product intent as read-only during execution. Treat task records as controlled records that can only reflect truthful execution state.
- Treat templates as script inputs first; do not freehand-copy or normalize template-backed structure when a local script can do it mechanically.
- Use lowercase canonical ids, enum values, YAML keys, and file names in MAGIA-owned artifacts.
- Do not ask for clarification during unattended execution loops; continue conservatively only when the result remains honest, scoped, and verifiable.

## Stop Conditions

Stop or hand off instead of continuing when:

- the request is planning, roadmap, portfolio, release communication, or stakeholder reporting rather than bounded execution;
- concrete repository scope, board root, selected spec, target files, or observable validation evidence cannot be resolved;
- execution would require rewriting product intent, task definitions, sequencing, ownership, or acceptance criteria;
- execution-state records conflict in ways that are not mechanically healable from existing evidence;
- the requested write would create MAGIA durable documentation outside the active board root;
- validation cannot be run and no truthful alternative evidence is available;
- secrets, credentials, private keys, or unrelated blocked paths would need to be read or changed.

## Output Contract

Final responses include only applicable sections:

1. Mode and scope.
2. Changes made.
3. Validation commands or checks with pass, fail, or not-run status, including a not-run reason for each check that was skipped and why it was not run.
4. Execution-record updates when RALPH state changed.
5. Assumptions, blockers, risks, trade-offs, remaining gaps, and relevant follow-ups.
6. Structured execution evidence only when requested or useful for downstream consumption.

Do not claim completion without current validation evidence. When blocked, report the exact blocker, any safe partial work completed, and the next evidence needed.

## Package Requests

When the user asks to package, export, or validate the MAGIA skill package, load [references/package-delivery.md](references/package-delivery.md), use `scripts/package_skill.py`, and validate both the folder and `skill.zip` with `scripts/validate_skill_package.py` before claiming readiness. If packaging cannot be completed, report the blocker, remaining gap, and next evidence needed instead of delivering a partial package as complete.

## Validation Checklist

Before final response:

- Confirm the selected mode matches the request and available evidence.
- Confirm every loaded reference was needed for the chosen branch.
- Confirm every changed durable MAGIA artifact stayed inside the active board root.
- Validate touched template-backed artifacts with the local validator or narrower validator.
- In RALPH, run the repository board validator before final response when the local repository is available.
- Run the skill package validator when changing MAGIA package files or preparing a package.
- Verify no placeholders, fabricated evidence, unresolved links, unvalidated scenario schema, or unreported validation gaps remain.

## Activation Examples

- Positive ADHOC: fix a failing parser test in the current repository and validate the targeted test command.
- Positive RALPH: execute a selected task for a concrete board package and update execution records truthfully.
- Negative boundary: write stakeholder release notes for a completed feature; hand off because downstream communication artifacts are outside MAGIA ownership.
- Ambiguous: continue the board work; resolve the concrete board root, selected spec, and next actionable task before execution.
