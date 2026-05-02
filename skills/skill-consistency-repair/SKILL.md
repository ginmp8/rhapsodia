---
name: skill-consistency-repair
description: use when asked to audit, validate, diagnose, repair, or package chatgpt or agent skill packages for consistency across skill.md, activation, scope, references, scripts, assets, examples, evals, validators, reports, and packaging. especially use for contradictions, ownership drift, unintegrated resources, stale scaffold, broken local references, weak handoffs, unsupported metrics, or output-contract gaps. do not use for ordinary code review, product planning, target-domain implementation, or generic benchmarking without consistency repair.
---

# Skill Consistency Repair

## Purpose

Audit and repair reusable skill packages so activation, authority, workflow, resources, outputs, validation, and packaging form one consistent contract. Detect contradictions, orphaned resources, ownership drift, stale scaffold, and unsupported capability or metric claims.

## Scope Boundary

Use only for target skill packages. Inspect or repair:

- `SKILL.md`: frontmatter, activation, scope, modes, workflow, stop conditions, output contract.
- `references/`: guidance, rubrics, schemas, loading rules.
- `scripts/`: cli contracts, validators, reports, packaging helpers.
- `assets/templates/`: operational output skeletons and usage rules.
- `examples/`, `evals/`: activation, non-activation, ambiguous, edge, regression, adversarial scenarios.
- `agents/openai.yaml`: metadata when it conflicts with role.
- Package hygiene: local references, placeholders, generated files, blocked paths.

Out of scope: target-domain implementation, unrelated repositories, evaluator-fixture or expected-output edits to force passing scores, and measured behavioral claims without executed or supplied evidence.

## Required Inputs

Resolve or infer before edits:

1. `TARGET_SKILL_PATH`: folder or extracted zip with exactly one target skill root.
2. Mode: `audit-only`, `repair-plan`, `apply-repair`, `validation-only`, or `package`.
3. Mutation scope: target folder unless narrowed by the user.
4. Blocked paths: `.git`, secrets, credentials, benchmark fixtures, expected outputs, generated baseline reports/evidence, existing packages, user-declared read-only files.
5. Evidence policy: target files, user feedback, prior failures, supplied benchmark reports, scenario evidence, optional validator output.
6. Gates: no broken local references, scaffold markers, ownership contradictions, unintegrated operational resources, validator failures, or package validation failures.

For zips, extract to a work directory and identify the single skill root before audit.

## Mode Selection Matrix

| Intent | Mode | Output | Mutate? | Closure gate |
|---|---|---|---|---|
| Find inconsistencies | `audit-only` | Consistency report | No | `scripts/consistency_audit.py` report |
| Decide fixes | `repair-plan` | Prioritized plan | No | Fixes map to evidence and validation |
| Fix package | `apply-repair` | Updated target plus report | Yes | Baseline/final audits compared |
| Check repaired skill | `validation-only` | Gate summary | No, except report refresh | Audit and validators run |
| Deliver archive | `package` | Validated `skill.zip` | Yes, only as needed | Folder and archive validations pass |

Use one primary mode. For combined audit, repair, validation, and package requests, run stages in that order and report each gate.

## Progressive Loading

Load only branch-relevant files:

- `references/consistency-taxonomy.md`: finding classes, severity, evidence.
- `references/repair-workflow.md`: baseline, hypothesis, patch, validation, rollback, packaging.
- `references/semantic-ownership-review.md`: role boundaries, artifact ownership, handoffs, persona drift.
- `references/resource-integration.md`: integrated, obsolete, duplicated, missing, asset-only resources.
- `references/report-contract.md`: durable report and final-response structure.
- `references/scenario-guidelines.md`: activation, ambiguous, edge, regression, adversarial scenarios.

Operational resources: `scripts/inventory_skill.py`, `scripts/consistency_audit.py`, `scripts/validate_consistency_report.py`, `scripts/package_target_skill.py`, `scripts/package_skill.py`; templates `assets/templates/consistency-report.md.template`, `assets/templates/repair-plan.md.template`, `assets/templates/patch-decision-record.md.template`, `assets/templates/scenario-suite.json.template`; planned coverage `examples/activation-scenarios.json`. Report scenario metrics only when executed or supplied.

## Workflow

1. Inspect target `SKILL.md`, then inventory `agents/`, `references/`, `scripts/`, `assets/`, `assets/templates/`, `examples/`, `evals/`, validators, and packages.
2. Baseline with `scripts/inventory_skill.py` and `scripts/consistency_audit.py` before mutation; treat output as structural evidence.
3. Classify findings as mechanical, semantic, behavioral, resource-integration, validation, or packaging; assign taxonomy severity.
4. Record each fix hypothesis with inconsistency, evidence, files, effect, risk, rollback, validation, and frozen evaluator inputs.
5. Repair only allowed target files. Keep `SKILL.md` compact, move branch detail to references, keep templates operational, and integrate useful resources before deletion.
6. Validate with the same audit, compare baseline/final, run validators or syntax checks, and validate touched scenario files.
7. Package only after folder validation passes. Exclude caches, generated reports, secrets, credentials, old zips, and blocked paths.
8. Report measured command output, reviewer judgment, planned scenarios, assumptions, and blockers separately.

## Repair Principles

Prefer corrected ownership and activation boundaries over added prose. Reconcile contradictions; do not hide them by deleting evidence. Integrate useful resources through loading rules, workflow references, script consumers, templates, validators, or examples before deleting. Remove only placeholders, duplicates, obsolete generated reports, misleading examples, caches, or files with no declared workflow use. Align role artifacts with real responsibility, not historical file names. When scores saturate, compare unresolved inconsistency, broken-reference, unintegrated-resource, placeholder, and validator-failure counts.

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

Stop and report a blocker when: zero or multiple root `SKILL.md` files make the root unclear; semantic ownership rewrite lacks evidence; requested edits touch blocked paths, fixtures, expected outputs, secrets, credentials, `.git`, or unrelated repos; repair needs target-domain facts absent from target files, user feedback, repository evidence, or supplied sources; the user asks for measured scenario metrics without executed or supplied results; validation fails and the fix is unsafe or out of scope; archive validation fails.

## Finalization Checklist

Before claiming success, verify: valid minimal frontmatter; aligned activation, scope, modes, workflow, stops, and output contract; every local reference exists; important resources are referenced, script-consumed, template-filled, validator-covered, or asset-only; no non-template placeholder markers remain; touched scripts were syntax-checked or reported untested; touched scenarios separate planned from measured evidence; packaging excludes generated reports, caches, zips, secrets, and blocked paths; final response separates measured evidence, judgment, assumptions, and follow-up.
