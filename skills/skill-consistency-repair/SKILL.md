---
name: skill-consistency-repair
description: use when asked to audit, validate, diagnose, repair, harden, or package a target chatgpt or agent skill for internal consistency across skill.md, frontmatter, activation, scope, references, scripts, assets, examples, evals, validators, reports, and packaging. especially use for contradictions, unclear ownership, unreferenced resources, stale instructions, broken local links, conflicting modes, missing output contracts, weak handoffs, or artifacts outside the declared role. do not use for ordinary code review, product planning, target-domain implementation, or generic skill benchmarking without inconsistency repair.
---

# Skill Consistency Repair

## Purpose

Audit and repair reusable skill packages so activation, authority, workflow, resources, outputs, validation, and packaging form one consistent contract. Find contradictions, orphaned resources, wrong role ownership, stale scaffold, and unsupported capability or metric claims.

## Scope Boundary

Use only for target skill packages. May inspect and repair:

- `SKILL.md`: frontmatter, activation, scope, modes, workflow, stop conditions, output contract.
- `references/`: guidance, rubrics, schemas, conditional loading.
- `scripts/`: command interfaces, validators, reports, package helpers.
- `assets/templates/`: operational output skeletons and usage rules.
- `examples/`, `evals/`: activation, non-activation, ambiguous, edge, regression, adversarial scenarios.
- `agents/openai.yaml`: user-facing metadata when it conflicts with role.
- Package hygiene: links, placeholders, generated files, blocked paths.

Out of scope: implementing target-domain behavior, rewriting unrelated repos, editing evaluator fixtures or expected outputs to make scores pass, or claiming measured behavioral metrics without executed or supplied evidence.

## Required Inputs

Resolve or infer before editing:

1. `TARGET_SKILL_PATH`: folder or extracted zip with exactly one target skill root.
2. Mode: `audit-only`, `repair-plan`, `apply-repair`, `validation-only`, or `package`.
3. Mutation scope: target skill folder unless user narrows it.
4. Blocked paths: `.git`, secrets, credentials, benchmark fixtures, expected outputs, generated baseline reports/evidence, existing packages, user-declared read-only files.
5. Evidence policy: target files, user feedback, prior failures, supplied benchmark reports, scenario evidence, optional validator output.
6. Gates: no broken local references, scaffold markers, ownership contradictions, unintegrated operational resources, target validator failures, or package validation failures.

If the target is a zip, extract to a work directory and identify the single skill root before audit.

## Mode Selection Matrix

| Intent | Mode | Output | Mutate? | Closure gate |
|---|---|---|---|---|
| Find inconsistencies | `audit-only` | Consistency report | No | `consistency_audit.py` report produced |
| Decide fixes | `repair-plan` | Prioritized plan | No | Every fix maps to evidence and validation |
| Fix package | `apply-repair` | Updated target plus report | Yes | Baseline/final audits compared; blockers reported |
| Check repaired skill | `validation-only` | Gate summary | No, except allowed report refresh | Audit and target validators run |
| Deliver archive | `package` | Validated `skill.zip` | Yes, only as needed | Folder and archive validations pass |

Use one primary mode. If the request combines audit, repair, validation, and package, run those stages in order and report each gate.

## Progressive Loading

Load only branch-relevant files:

- `references/consistency-taxonomy.md`: finding classes, severity, evidence.
- `references/repair-workflow.md`: baseline, hypothesis, patch, validation, rollback, packaging.
- `references/semantic-ownership-review.md`: role boundaries, artifact ownership, handoffs, persona drift.
- `references/resource-integration.md`: integrated, obsolete, duplicated, missing, or asset-only resources.
- `references/report-contract.md`: durable report and final-response structure.
- `references/scenario-guidelines.md`: activation, ambiguous, edge, regression, adversarial scenarios.

Operational resources:

- Inventory: `scripts/inventory_skill.py`.
- Audit: `scripts/consistency_audit.py`.
- Report validation: `scripts/validate_consistency_report.py`.
- Target packaging: `scripts/package_target_skill.py`; self-package wrapper: `scripts/package_skill.py`.
- Templates: `assets/templates/consistency-report.md.template`, `assets/templates/repair-plan.md.template`, `assets/templates/patch-decision-record.md.template`, `assets/templates/scenario-suite.json.template`.
- Planned coverage: `examples/activation-scenarios.json`; report metrics only when executed or supplied.

## Workflow

1. Inspect target: read target `SKILL.md` first, then inventory `agents/`, `references/`, `scripts/`, `assets/`, `assets/templates/`, `examples/`, `evals/`, validators, packages.
2. Baseline: run `inventory_skill.py` and `consistency_audit.py` before mutation; treat output as structural evidence, not domain judgment.
3. Classify: mechanical, semantic, behavioral, resource-integration, validation, packaging; assign severity from taxonomy.
4. Hypothesize: for each fix record inconsistency, evidence, files, effect, risk, rollback, validation; keep evaluator inputs fixed.
5. Repair: edit only allowed target files; keep `SKILL.md` compact, move branch detail to references, keep templates operational, integrate useful resources before deletion.
6. Validate: rerun the same audit, compare baseline/final, run target validators or syntax checks, validate touched scenario files.
7. Package: only after folder validation passes; exclude caches, generated reports, secrets, credentials, old zips, blocked paths.
8. Report: separate measured command output, reviewer judgment, planned scenarios, assumptions, and blockers.

## Repair Principles

- Prefer corrected ownership and activation boundaries over added prose.
- Reconcile contradictions; do not hide them by deleting evidence.
- Integrate useful resources through loading rules, workflow references, script consumers, templates, validators, or examples before deleting.
- Remove only placeholders, duplicates, obsolete generated reports, misleading examples, caches, or files with no declared workflow use.
- Make the smallest safe contract-restoring edit.
- Align role artifacts with real responsibility, not historical file names.
- When package scores saturate, also compare unresolved inconsistency, broken-link, unintegrated-resource, placeholder, and validator-failure counts.

## Output Contract

Include applicable sections:

1. Mode and target path.
2. Baseline evidence: inventory path, audit path, critical findings.
3. Decision: repair, reject, block, or package.
4. Changes by `SKILL.md`, `references/`, `scripts/`, `assets/templates/`, `examples/`, `evals/`, packaging.
5. Validation commands with pass/fail/not-run and reasons.
6. Before/after inconsistency counts when measured.
7. Protected blocked paths and rollback notes.
8. Remaining risks, assumptions, unresolved contradictions, next hypothesis.
9. Package artifact path only when a real validated `skill.zip` exists.

## Stop Conditions

Stop and report a blocker when:

- zero or multiple root `SKILL.md` files exist and the correct root is unclear;
- semantic ownership rewrite lacks required evidence;
- requested edits touch blocked paths, fixtures, expected outputs, secrets, credentials, `.git`, or unrelated repo files;
- repair requires target-domain facts absent from target files, user feedback, repo evidence, or supplied sources;
- user asks for measured scenario metrics without executed or supplied results;
- validation fails and fixing it would be unsafe or out of scope;
- archive validation fails.

## Finalization Checklist

Before claiming success, verify: target `SKILL.md` has valid minimal frontmatter if present; activation, scope, modes, workflow, stops, and output contract align; every local reference exists; important resources are referenced, script-consumed, template-filled, validator-covered, or asset-only; no non-template placeholder markers remain; touched scripts were syntax-checked or reported untested; touched scenarios keep planned-vs-measured separation; packaging excludes generated reports, caches, zips, secrets, and blocked paths; final response separates measured evidence, judgment, assumptions, and follow-up.
