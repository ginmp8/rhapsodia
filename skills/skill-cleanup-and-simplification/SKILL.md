---
name: skill-cleanup-and-simplification
description: use when asked to clean, simplify, de-duplicate, remove scaffold, consolidate references, organize templates, classify dead resources, apply safe minimal cleanup, validate package hygiene, or create a technical debt remediation plan for a chatgpt or agent skill package, scripts, references, templates, examples, validators, or small helper project. do not use for security review, benchmark scoring, full hardening, consistency repair, or domain behavior changes.
---

# Skill Cleanup and Simplification

## Purpose

Clean and simplify reusable skill packages and small supporting projects without changing domain behavior. Classify before deletion, preserve progressive-loading resources, prefer integration over removal, and validate after every applied cleanup.

This skill does not depend on MCP. Use local files, user-provided context, repository evidence, and deterministic scripts bundled with this skill.

## Modes

Select one primary mode. If the user asks for end-to-end work, stage the run in this order: audit, plan, classify, apply, validate, report.

| Mode | Use for | Mutation allowed | Primary output |
|---|---|---:|---|
| `cleanup-audit` | Find placeholders, caches, old zips, generated artifacts, duplicate files, scaffold remnants, and hygiene risks. | No | Evidence-backed inventory and findings |
| `simplification-plan` | Propose safe simplification with risk, impact, validation, and rollback. | No | Cleanup plan |
| `duplicate-consolidation` | Consolidate duplicated guidance, scripts, templates, or reference sections. | Yes, after classification | Consolidated resources and rationale |
| `dead-resource-review` | Classify resources as used, integrable, obsolete, duplicated, or blocked. | No by default | Resource classification table |
| `safe-cleanup-apply` | Apply minimal, reversible cleanup inside the allowed scope. | Yes | Changed files plus rollback notes |
| `technical-debt-plan` | Create a prioritized remediation plan for cleanup or simplification debt. | No | Prioritized remediation plan |
| `post-cleanup-validation` | Validate links, references, scripts, package hygiene, and side effects. | No, except generated validation reports outside target | Gate summary |
| `cleanup-report` | Summarize changed, removed, retained, and blocked resources. | No | Final cleanup report |

## Scope Boundaries

Use this skill for target packages such as:

- `SKILL.md`, `agents/openai.yaml`, `references/`, `scripts/`, `assets/templates/`, `examples/`, `evals/`, validators, reports, and packaging helpers;
- small helper projects bundled with or adjacent to a skill package;
- generated residue, old scaffold, duplicate guidance, stale templates, and technical-debt planning.

Do not use this skill to replace:

- security review or secret scanning;
- benchmark scoring, behavioral scenario measurement, or readiness verdicts;
- full package hardening, consistency repair, or prompt/skill creation;
- application-level refactoring unrelated to a skill package;
- domain behavior changes without evidence and tests.

## Required Inputs and Defaults

Resolve or conservatively infer:

1. `TARGET_PATH`: skill folder, extracted zip, or small helper project.
2. Mode, defaulting to `cleanup-audit` for ambiguous requests and staged end-to-end cleanup when the user explicitly asks to apply changes.
3. Allowed mutation scope, defaulting to the target folder only.
4. Blocked paths: `.git`, secrets, credentials, fixtures, expected outputs, benchmark reports, generated evidence, existing zips, user-declared read-only paths, and unrelated repository files.
5. Evidence policy: target files, user notes, prior reports, tests, validators, imports/usages, local links, package metadata, and command output.
6. Validation gates: no broken local references, no unresolved scaffold markers outside templates, no deleted protected resources, scripts compile or run when touched, package hygiene passes, and rollback notes exist for mutations.

When evidence is insufficient, produce a plan or classification. Do not delete.

## Progressive Loading

Load only what is needed:

- `references/safe-cleanup-rules.md`: deletion, consolidation, rollback, and protected-path rules.
- `references/resource-classification.md`: resource status taxonomy and evidence requirements.
- `references/technical-debt-prioritization.md`: scoring model for remediation plans.
- `assets/templates/cleanup-plan.md.template`: structure for cleanup and simplification plans.
- `assets/templates/cleanup-report.md.template`: structure for final reports.
- `scripts/cleanup_inventory.py`: read-only inventory and candidate detection.
- `scripts/validate_cleanup_package.py`: post-cleanup validation for links, placeholders, scripts, caches, zips, and package hygiene.

## Workflow

1. **Inspect first.** Identify the root, read `SKILL.md` before other files when the target is a skill, and list package resources.
2. **Run read-only inventory when filesystem access exists.** Use:

   ```bash
   python -S scripts/cleanup_inventory.py --target <TARGET_PATH> --output <REPORT_DIR>/cleanup-inventory.json
   ```

3. **Classify before deletion.** Use `references/resource-classification.md`. A resource can be deleted only when it is a confirmed placeholder, generated artifact, cache, true duplicate, or obsolete file with evidence.
4. **Prefer integration.** If a reference, template, example, or validator appears useful but unreferenced, integrate it through workflow links, loading rules, script usage, validation coverage, or explicit asset-only rationale.
5. **Plan simplification.** For every proposed change, state evidence, target files, expected simplification, behavior risk, rollback, and validation gate.
6. **Apply minimal cleanup.** In `safe-cleanup-apply`, make the smallest reversible change. Do not change domain semantics, public contracts, activation boundaries, evaluator fixtures, expected outputs, or benchmark evidence.
7. **Validate after changes.** Use:

   ```bash
   python -S scripts/validate_cleanup_package.py --target <TARGET_PATH> --output <REPORT_DIR>/cleanup-validation.json
   ```

   Also run touched scripts, target validators, tests, or packaging checks when present.
8. **Report truthfully.** Separate measured command output from reviewer judgment. State retained resources and blockers, not only removals.

## Deletion and Consolidation Rules

Deletion is allowed only when all are true:

1. The resource is not protected or blocked.
2. The resource was classified with evidence.
3. There is no declared progressive-loading, template, example, fixture, expected-output, or report role.
4. Removal does not change domain behavior, public interfaces, validation baselines, or expected outputs.
5. A rollback path is clear.
6. Post-cleanup validation passes or the failure is reported as a blocker.

Consolidation is allowed when duplication is real, not merely similar wording serving different modes. Preserve the clearest source of truth, update all references, and keep compatibility aliases or migration notes when names are externally referenced.

## Technical Debt Planning

For `technical-debt-plan`, score each item on 1-5 scales:

- ease: lower implementation difficulty is better;
- impact: package quality, maintainability, validation, or context-efficiency improvement;
- risk: consequence of leaving the debt in place;
- confidence: evidence strength for the finding.

Prioritize high impact, high risk, high confidence, and low-to-medium ease. Include prerequisites, ordered steps, validation, rollback, and ownership notes.

## Stop Conditions

Stop and report a blocker when:

- the target has zero or multiple candidate roots and the correct root cannot be identified;
- requested changes touch `.git`, secrets, credentials, fixtures, expected outputs, benchmark reports, generated evidence, old zips, or unrelated files;
- deletion would rely only on absence of references from a shallow search;
- a resource may support progressive loading or external use and has no replacement plan;
- the change requires domain facts not present in evidence;
- validation fails and cannot be repaired within scope;
- the user asks this skill to perform security review, benchmark scoring, full hardening, or consistency repair.

## Output Contract

For every run, include applicable sections:

1. Mode and target.
2. Evidence inspected and commands executed.
3. Resource classification summary.
4. Deletion/consolidation decisions with rationale.
5. Changes made or proposed, grouped by `SKILL.md`, `references/`, `scripts/`, `assets/templates/`, `examples/`, `evals/`, validation, and packaging.
6. Validation results and failed gates.
7. Protected blocked paths.
8. Rollback notes.
9. Remaining risks, limitations, and recommended next actions.

## Finalization Checklist

Before claiming completion:

- all resources considered for deletion were classified;
- useful unreferenced resources were integrated or explicitly retained;
- no non-template scaffold markers remain;
- local markdown links and referenced files still resolve;
- touched scripts compile or run on representative input;
- package excludes caches, generated reports, secrets, credentials, and existing zip files;
- `skill.zip` exists only when real packaging validation succeeded;
- final report distinguishes applied changes, recommendations, blockers, and assumptions.
