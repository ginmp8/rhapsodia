# MAGIA Quickstarts

Load only for onboarding, mode selection, script discovery, or recovery guidance. These quickstarts summarize existing contracts; the linked mode, risk, validation, state, and ownership references remain authoritative.

## Choose the Entry Point

| Situation | Mode | First safe action |
|---|---|---|
| Direct bug, feature, refactor, config, test, validator, or developer-doc change | `ADHOC` | Resolve repository scope, inspect current behavior, and define one observable proof |
| Selected task from a current board/spec package | `RALPH` | Resolve board/spec/task and run readiness before mutation |
| Legacy execution notes must become current MAGIA evidence | `ADAPT` | Inspect legacy records and identify which claims have current evidence |
| Product intent, design, task, sequencing, or validation plan must change | handoff to Mago | Record the technical gap and stop the affected mutation |
| Owner, priority, date, stakeholder, release, or business-risk decision must change | handoff to nomia | Record evidence and stop the governance mutation |

For non-trivial work, begin with the [execution start card](execution-entry.md).

## ADHOC: Bug or Small Feature

1. Resolve the repository root, allowed writes, blocked paths, objective, and observable proof.
2. For an unfamiliar repository, run:

   ```text
   python scripts/inspect_repository_context.py --root <repository-root> --format markdown
   ```

3. Reproduce or inspect before editing.
4. Apply the smallest sufficient patch using existing conventions.
5. Run the narrowest proof, then applicable build, lint, contract, security, or smoke checks.
6. Report changed files, check states, residual risk, and next action.

Do not convert a small implementation request into broad redesign or cleanup.

## RALPH: Selected Task Execution

1. Resolve board root, cycle, spec, selected task, repository scope, and allowed writes.
2. Confirm a concrete PRD objective, acceptance criterion, planned validation action, and expected outcome.
3. Run the readiness validator before mutation.
4. Execute only the selected task or an explicit dependency-safe batch.
5. Use [safe execution waves](safe-parallelism.md) only when dependencies, parallel permission, write scopes, contracts, isolated checks, and reconciliation are explicit.
6. Record implementation evidence and validation evidence.
7. Update controlled task, manifest, and registry state only through current evidence and recoverable state scripts.
8. Validate execution state and board consistency before closure.

A task checkbox is never evidence by itself.

## ADAPT: Legacy Evidence Conversion

1. Resolve the current board root and spec id.
2. Inspect legacy notes and validation records without treating prose claims as executed evidence.
3. Convert only supported execution facts into `implementation-notes.md` and `validation-evidence.md`.
4. Preserve unsupported claims as gaps, `not-run`, `unknown`, or blocked evidence.
5. Validate the current execution state; do not rewrite planning artifacts to fit legacy history.

## Validation Selection

For non-trivial changes, use [validation selection](validation-selection.md). A temporary request can show required categories before concrete commands are mapped:

```text
# Preliminary only, when you have changed files/risk signals but not explicit surfaces:
python scripts/select_validation.py --input <change-descriptor.json>

# Canonical once surfaces and available checks are explicit:
python scripts/select_validation_checks.py --input <request.json> --format markdown
```

The result selects categories only. It does not execute checks or prove success.

## Recovery and Resume

When an execution was interrupted:

1. stop new writes;
2. inspect the current repository state, execution artifacts, lock, and journal;
3. identify whether the lock owner is alive;
4. compare current files with the preflight snapshot for drift;
5. recover only a dead-owner lock and a valid journal through existing state scripts;
6. repeat every check whose inputs may have changed;
7. abandon or roll back when the candidate state cannot be validated safely.

Report:

- last completed action;
- files already changed;
- commands already executed and their states;
- lock/journal condition;
- drift result;
- checks requiring repetition;
- next safe action.

Do not infer completion from an interrupted log.

## Governed Examples

### Migration

- escalate to `governed`;
- identify compatibility window, forward order, data-integrity proof, rollback/recovery, observability, and ownership;
- block closure when any required category remains unavailable.

### Authentication or Authorization

- preserve planned intent;
- require authorization and abuse-case evidence in addition to targeted integration checks;
- hand off when the change alters the security model rather than implementing it.

### API or Event Contract

- identify consumers and classify behavior as preserved, added, modified, or removed;
- require contract, compatibility, and integration evidence;
- record rollout and recovery for non-atomic consumers.

## Blocked Handoff Example

Continue with safe inspection but stop mutation when repository evidence proves the selected task requires a new public field, persistence change, or authorization rule not present in the approved planning boundary. Create a `technical-gap-note.md` with the conflicting evidence, affected surfaces, safe partial work, and required Mago decision. Do not edit the PRD, task, or acceptance criteria.

## Script Finder

| Need | Script |
|---|---|
| Repository orientation | `scripts/inspect_repository_context.py` |
| Preliminary profile inference from changed files/risk signals | `scripts/select_validation.py` |
| Canonical validation-category selection from explicit surfaces | `scripts/select_validation_checks.py` |
| Requirement/evidence convergence validation | `scripts/validate_convergence.py` |
| Read-only public SDD artifact orientation | `scripts/adapt_public_artifacts.py` |
| Conservative execution waves | `scripts/analyze_execution_waves.py` |
| RALPH readiness | `scripts/validate_execution_readiness.py` |
| Board contract | `scripts/validate_board_contract.py` |
| Execution state | `scripts/validate_execution_state.py` |
| Interrupted state repair | `scripts/heal_execution_state.py` |
| Controlled closure | `scripts/close_execution_state.py` |
| Package validation | `scripts/validate_skill_package.py` |

Use `-h` on CLI scripts before execution. Import-only modules are documented in [resource-map.md](resource-map.md) and intentionally have no standalone CLI.
