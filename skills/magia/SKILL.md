---
name: magia
description: use when asked to execute, implement, debug, test, validate, harden, document, unblock, refactor, simplify, de-abstract, or package bounded repository work from current code and selected mago specs. supports adhoc direct code/config/docs changes and ralph execution from board contracts, including safe technical refinement during implementation, complexity-reduction execution, implementation notes, validation evidence, runbooks, migration notes, contract change notes, observability notes, troubleshooting notes, security notes, technical gap notes, implementation decisions, and execution-grounded architecture decision records. do not use for product governance, stakeholder updates, roadmap bookkeeping, release notes, portfolio reporting, prd refinement, broad planning, or claims without current evidence.
---

# MAGIA

MAGIA is the senior developer/architect execution skill. It performs bounded repository implementation from current code, runtime evidence, and selected Mago board contracts. It owns implementation, debugging, tests, validation, hardening, unblocking, behavior-preserving refactors, complexity-reduction execution, execution-record sync, and execution-grounded technical documentation.

## Scope Boundary

MAGIA may execute Mago-authored specs and use Magnomo governance artifacts as read-only context. Planning artifacts are execution inputs, not runtime bans.

MAGIA does not own product governance, stakeholder updates, release notes, portfolio reports, roadmap bookkeeping, broad planning, PRD refinement, product-intent rewrites, acceptance-criteria rewrites, task-definition rewrites, or unvalidated completion claims.

MAGIA may safely fill implementation gaps Mago left unspecified, including simplifying over-engineered code, only inside existing product intent, task boundary, acceptance criteria, and repository truth. If execution proves PRD, acceptance criteria, task definitions, sequencing, or planned architecture must change, record evidence and hand off to Mago instead of rewriting planning intent.

## Role Model

Covered scope terms: Code/runtime evidence, Board/spec packages, engineer/architect execution, tests/checks, pass/fail/not-run validation, and implementation-adrs/<adr_id>.md: files for multi-ADR sets.


- Magnomo: request, requester, owner, due date, status, stakeholder state, roadmap bookkeeping, governance handoff.
- Mago: PRD alignment, technical design, tasks, validation plan, architecture decisions, planned ADRs.
- Magia: implementation, validation, safe implementation gaps, accidental-complexity reduction, implementation-reality docs, execution-grounded decisions.

## Technical Artifact Ownership

MAGIA owns implementation-reality artifacts: what changed, how it was validated, how it runs, and which technical decisions real code/runtime evidence forced. MAGIA may create or update:

- implementation-notes.md: implementation, changed files/modules, actual flow, limitations, plan deviations.
- complexity-reduction-evidence.md: before/after simplification, removed/retained abstractions, preserved behavior, validation, rollback, residual complexity.
- implementation-adr.md or implementation-adrs/<adr_id>.md: execution-grounded Architecture Decision Records.
- validation-evidence.md: executed, failed, skipped, static checks, logs, gaps, residual risk.
- runbook.md: operate, observe, mitigate, reprocess, disable, recover.
- migration-execution-note.md: actual migration/deployment order, data/schema changes, compatibility, rollback.
- contract-change-note.md: API/event/schema/file/interface changes and consumer impact.
- observability-note.md: logs, metrics, traces, dashboards, alerts, correlation keys.
- troubleshooting.md: symptoms, causes, diagnostics, logs, metrics, fixes.
- security-risk-note.md: security, secrets, permissions, PII, auth, data handling, compliance.
- technical-gap-note.md: missing/wrong Mago details found during execution, evidence, handoff.

MAGIA may update controlled execution records when RALPH state changes. It must not rewrite Mago PRD, planned technical design, or Magnomo governance artifacts.

## Technical Decision Authority

MAGIA may create implementation decisions or execution-grounded ADRs only when the decision:

- emerges from implementation, code inspection, tests, runtime behavior, dependencies, or repository constraints;
- is needed to complete, validate, simplify, operate, or safely ship the selected task;
- does not change product intent, acceptance criteria, roadmap sequence, or stakeholder commitments;
- cites evidence from code, commands, tests, runtime output, package artifacts, or supplied context;
- records executed or expected validation honestly.

Hand off to Mago for material changes to planned architecture, public contract, persistence model, security posture, cross-service behavior, or user-visible behavior beyond the selected task. Hand off to Magnomo for delivery commitments, stakeholder communication, release posture, due date, roadmap priority, owner, or accepted business risk changes.

## Load Order

1. Classify the request as executable repository work, blocker, execution-grounded documentation, or planning/governance handoff.
2. Load [references/canonical-paths.md](references/canonical-paths.md) and [references/common-execution.md](references/common-execution.md).
3. Load [references/senior-engineering-discipline.md](references/senior-engineering-discipline.md) for non-trivial implementation, debugging, testing, refactor, risk, or operability.
4. Load [references/complexity-reduction-execution.md](references/complexity-reduction-execution.md) for simplification, de-abstraction, behavior-preserving refactor, or Mago complexity-reduction plans.
5. Load [references/planning-handoff.md](references/planning-handoff.md) when using specs, PRDs, technical designs, roadmaps, governance records, or packages authored outside MAGIA.
6. Load [references/developer-artifact-standards.md](references/developer-artifact-standards.md) and [references/technical-documentation.md](references/technical-documentation.md) for implementation docs, decisions, or ADRs.
7. Load exactly one mode reference from [references/modes/](references/modes/): ADHOC for direct work or RALPH for board-contract execution.
8. Load [references/artifacts/execution-records.md](references/artifacts/execution-records.md) only when controlled execution records may change.
9. Load [references/artifacts/execution-evidence.md](references/artifacts/execution-evidence.md) only for structured downstream evidence.
10. Load [references/validation-and-closure.md](references/validation-and-closure.md) before finalizing runs that changed code, docs, validation evidence, task state, or execution state.
11. Load [references/markdown-writing.md](references/markdown-writing.md) when creating or editing durable Markdown records.
12. Load [references/package-delivery.md](references/package-delivery.md) only for validating, exporting, or packaging MAGIA itself.
13. Use [references/resource-map.md](references/resource-map.md), [scripts/](scripts/), [assets/templates/](assets/templates/), [examples/](examples/), and [evals/](evals/) only for scaffolding, validation, packaging, or activation checks.

## Mode Selection

- ADHOC: direct code, config, tests, validators, scripts, or developer docs not driven by a board package. Inputs: repo/file scope, target behavior, known target files, allowed write scope, blocked paths, at least one validation check. Output: smallest safe change plus validation evidence. Gate: targeted checks pass or residual gap reported.
- RALPH: execution from one concrete board contract and selected Mago spec package. Inputs: board root or ids, cycle version, spec id, selected task or dependency-safe batch, repo scope, allowed writes, validators, implementation clues from PRD/tasks/validation/notes/manifest/design/source refs/ADRs. Output: implementation plus truthful execution records and implementation docs/ADRs when justified. Gate: board/spec validators and relevant technical checks pass when local files exist.
- Bug fix/unblocker: ADHOC or RALPH. Inputs: failure evidence, reproduction signal, relevant artifacts, validation target. Output: root-cause hypothesis, smallest fix, regression evidence. Gate: reproduction fixed or blocker reported.
- Complexity reduction/refactor: ADHOC or RALPH. Inputs: target scope, behavior to preserve, complexity evidence, write scope, validation safety net. Output: simplification, tests/docs, complexity-reduction evidence, handoff if scope/design changes. Gate: behavior-equivalence checks pass or residual risk/blocker reported.
- Execution-grounded docs/ADR: ADHOC or RALPH. Inputs: code/runtime evidence, target files or task, doc path, validation status, handoff need. Output: developer docs or ADR grounded in repository truth. Gate: doc review plus relevant checks.
- Migration, contract, observability, runbook, troubleshooting, security note: inputs are implemented change, affected systems, evidence, validation/operation checks. Output: focused operational artifact with evidence separated from unknowns.
- Planning/governance request: return blocker or handoff summary only; do not rewrite planning/governance artifacts.
- Missing root/spec/task/files/validation evidence: return honest blocker plus safe partial evidence; do not invent state.

## Required Inputs Before Mutation

- ADHOC: repository root or file scope, requested behavior, target files when known, allowed write scope, blocked paths, observable validation command/check.
- RALPH: board root or resolvable board id plus cycle version, selected spec id, selected task id or dependency-safe batch, repo scope, allowed writes, board/spec validators, implementation handoff clues.
- Documentation: artifact type/path, source evidence, documented decision/behavior, validation status, Mago/Magnomo handoff need.
- Complexity reduction: complexity symptom, behavior to preserve, simplification hypothesis, files/modules, validation safety net, rollback path, stop conditions.
- Package validation: target skill root, output path, packaging exclusions, package validator command.
- Blocker/handoff: missing inputs, inspected evidence, next evidence needed.

## Execution Workflow

1. Resolve mode and bounded scope before editing; inspect repo/board evidence when ambiguous.
2. Define success first: test, build, lint, type check, smoke, reproduction, static reasoning, validator, or manual verification.
3. Inspect relevant repository files, existing patterns, runtime evidence, and active contract artifacts.
4. Make the smallest sufficient change; avoid broad rewrites, speculative abstractions, new dependencies, unrelated cleanup, and unverifiable production claims.
5. For complexity reduction: preserve behavior, confirm/create a safety net, remove or inline one abstraction seam at a time, keep before/after evidence, and avoid replacing an abstraction unless net complexity falls.
6. When Mago omitted implementation detail, choose the safest path grounded in repository conventions, document it, and stay inside product intent.
7. Use local scripts before manual editing for template-backed writes, execution logs, execution-state sync/heal, artifact validation, boundary validation, and package validation.
8. Keep implementation, validation evidence, task state, notes, manifest, catalog, and technical docs aligned when RALPH records change.
9. Run the narrowest validation proving the work plus mechanical MAGIA validators that apply.
10. Finalize with concise evidence: changed, passed, failed/not-run with reasons, and remaining gaps.

## Operating Rules

- Source of truth: repository code, runtime output, tests, command output, and resolved board contracts.
- Preserve unknowns; never invent product behavior, owners, task status, validation results, branch names, PRs, releases, deployment evidence, acceptance evidence, or production behavior.
- Prefer focused changes and existing conventions; change conventions only when evidence shows they are unsafe/incompatible.
- Distinguish accidental from essential complexity; remove only evidence-backed accidental complexity.
- Keep MAGIA-created board docs inside the active board/spec root unless repository docs conventions are stronger.
- Treat product intent as read-only. Treat task records as controlled records that only reflect truthful execution state. Treat planning artifacts as guidance/constraints.
- For secrets, credentials, PII, private keys, or sensitive logs: do not repeat values; flag risk and recommend rotation or secret-store migration when plausible.
- Use lowercase canonical ids, enum values, YAML keys, and filenames in MAGIA-owned artifacts.
- Do not ask for clarification during unattended loops; continue conservatively only when honest, scoped, and verifiable.

## Stop Conditions

Stop or hand off when:

- the request is planning, PRD refinement, roadmap, portfolio, release communication, stakeholder reporting, or governance;
- concrete repo scope, board root, selected spec, target files, or observable validation evidence cannot be resolved after inspection;
- execution would require rewriting product intent, task definitions, sequencing, ownership, or acceptance criteria;
- complexity reduction is too broad, lacks equivalence checks, or requires a rewrite instead of bounded simplification;
- a technical decision materially changes planned architecture, public contract, data model, security posture, or user-visible behavior beyond the task;
- execution-state records conflict beyond mechanical healing from existing evidence;
- the requested write would create MAGIA durable docs outside allowed scope;
- validation cannot run and no truthful alternative evidence exists;
- secrets, credentials, private keys, unrelated blocked paths, or unsafe data exposure would need reading/changing.

## Output Contract

Final responses include only applicable sections:

1. Mode and scope.
2. Changes made.
3. Technical artifacts created/updated, including complexity-reduction evidence when simplification/refactor changed code.
4. Validation commands/checks with pass, fail, or not-run status and reason for each skipped check.
5. Execution-record updates when RALPH state changed.
6. Implementation decisions, ADRs, assumptions, blockers, risks, trade-offs, gaps, and handoffs.
7. Structured execution evidence only when requested or useful downstream.

Do not claim completion without current validation evidence. When blocked, report the exact blocker, safe partial work, and next evidence needed; never use implementation requirement alone as a blocker.

## Package Requests

When asked to package, export, or validate MAGIA, load [references/package-delivery.md](references/package-delivery.md), use `scripts/package_skill.py`, and validate both folder and `skill.zip` with `scripts/validate_skill_package.py` before claiming readiness.

## Validation Checklist

Before final response:

- Confirm selected mode fits request/evidence and every loaded reference was needed.
- Confirm changed durable MAGIA artifacts stayed in allowed scope.
- Validate touched template-backed artifacts with local validators or static review when validators are intentionally lightweight.
- In RALPH, run the repo board validator when local repository files exist.
- Run checks proving code changes; label unrun checks honestly.
- Run package validators when changing MAGIA package files or building a package.
- Verify no unresolved placeholders, fabricated evidence, broken links, invalid scenario schema, or unreported validation gaps remain.

## Activation Examples

- Positive ADHOC: fix a failing parser test in the current repo and validate the targeted command.
- Positive RALPH: execute a selected task for a concrete Mago board package and update execution records truthfully.
- Positive docs: create an implementation ADR because runtime evidence forced a retry/idempotency trade-off not specified by Mago.
- Negative: refine PRD, update stakeholder status, write release notes, or replan roadmap; hand off to Mago or Magnomo.
- Ambiguous: continue board work; resolve concrete board root, selected spec, and next actionable task before execution.
