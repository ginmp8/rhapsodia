---
name: skill-hardening
description: harden existing chatgpt or agent skill packages by auditing skill.md plus bundled agents, references, scripts, templates, assets, examples, evals, validators, gates, and packaging hygiene; applying bounded package-level improvements; validating gates; and building skill.zip. use when asked to improve, mature, standardize, harden, repair, validate, or package reusable skill packages. do not use for net-new skills, generic repositories, ordinary documents, product planning, or benchmark-only scoring without package improvements.
---

# Skill Hardening

## Purpose

Harden an existing ChatGPT or Agent skill as a reusable package. Own the package control plane in `SKILL.md` plus `agents/openai.yaml`, `references/`, `scripts/`, `assets/templates/`, `examples/`, `evals/`, validators, output contracts, and packaging hygiene.

Use only when the target is a reusable skill package. Do not use for generic repository refactors, product planning, ordinary documents, implementation tasks whose artifact is not a skill, or net-new skill creation without an existing package.

## Required Inputs

Resolve before mutation:

1. `TARGET_SKILL_PATH`: folder, extracted zip, or named installed skill resolving to exactly one skill root.
2. Mode: `audit-only`, `plan-only`, `apply-hardening`, `validation-only`, or `package`.
3. Mutation scope: default target folder only.
4. Blocked: benchmark fixtures, expected outputs, secrets, `.git`, generated evidence/baseline reports, and user-declared read-only files.
5. Evidence: package files, user feedback, benchmark report, failed prompts, previous outputs, target-domain docs, repository truth, or existing resources.
6. Research: in `auto`, research only concrete inspection gaps; in constrained runs, use supplied or target-local evidence only.
7. Gates: minimum audit score, required commands, package validation, no scaffold markers, all referenced files present, optional benchmark or scenario results.

If only a target folder plus “harden it” is supplied, use conservative defaults: audit, create a hardening map, apply one bounded package-level batch, validate, and package only when requested or clearly expected.

## Modes

| Intent | Mode | Output | Validation |
|---|---|---|---|
| Understand weaknesses | `audit-only` | Audit report, prioritized findings | `scripts/hardening_audit.py` |
| Decide supporting files | `plan-only` | Hardening map, resource blueprint | Inventory plus audit |
| Improve package | `apply-hardening` | Updated files, validation evidence | Inventory, audit, target checks, `scripts/validate_hardened_skill.py` |
| Check readiness | `validation-only` | Pass/fail gates, risks | `scripts/validate_hardened_skill.py`; include package check when zip exists |
| Deliver uploadable package | `package` | `skill.zip`, validation evidence | Folder validator, package builder, archive validator |

Use one primary mode per run. For mixed redesign/evaluator/validation/package requests, stage: inspect -> audit -> harden -> validate -> package.

## Progressive Loading

Load only the needed branch resource:

- `references/mature-skill-patterns.md`: control-plane, mode, stop, output-contract patterns.
- `references/resource-hardening-playbook.md`: add/integrate/migrate/remove references, scripts, templates, assets, examples.
- `references/evaluator-contract.md`: gate design, scores, saturated-audit auxiliary metrics, report minimums.
- `references/evidence-policy.md`: research, source handling, evidence, measured-versus-proposed claims.
- `references/scenario-suite.md`: activation, non-activation, ambiguous, edge, regression, adversarial scenarios.
- `references/packaging-and-validation.md`: commands, zip creation, package validation, exclusions, delivery evidence.
- `assets/templates/hardening-plan.md.template`: hardening plan shape.
- `assets/templates/hardening-report.md.template`: final report shape.
- `assets/templates/reference-file.md.template`: target-specific reference shape.
- `assets/templates/scenario-suite.json.template`: behavioral scenario-suite shape.
- `examples/hardening-scenarios.json`: activation and conformance examples.
- `evals/activation-scenarios.json`: this skill’s planned activation/boundary scenario suite.
- `scripts/inventory_skill.py`: deterministic inventory and resource-integration signals.
- `scripts/package_skill.py`: deterministic `skill.zip` builder and archive validator.

Keep `SKILL.md` as router/control plane. Put detailed rubrics, schemas, command sequences, examples, and script contracts in lazy-loaded resources.

## Workflow

1. **Inspect**
   - Read target `SKILL.md` first.
   - Run `scripts/inventory_skill.py`; exact command sequence is in `references/packaging-and-validation.md`.
   - Inventory `agents/`, `references/`, `scripts/`, `assets/`, `assets/templates/`, `examples/`, `evals/`, tests, benchmark evidence, validators, and unused scaffold.

2. **Audit**
   - Run `scripts/hardening_audit.py` with markdown and json outputs; see `references/packaging-and-validation.md`.
   - Treat audit as structural evidence, not domain judgment.
   - If the score is saturated, add a non-saturated signal: scenario-suite schema quality, unresolved-risk count, placeholder count, script test pass rate, or package gate count.

3. **Map**
   - Group planned changes by `control_plane`, `references`, `scripts`, `templates_assets`, `examples_scenarios`, `validation`, and `packaging`.
   - For each change, state hypothesis, files, expected improvement, and validation gate.
   - Preserve useful target behavior.
   - Prefer references for branch rules, scripts for repeatable checks, templates for reusable artifact shapes, and examples/evals for behavioral calibration.

4. **Apply bounded changes**
   - Edit only allowed target-scope files.
   - Keep `SKILL.md` compact; move long rubrics, schemas, and command detail to references.
   - Add or improve scripts only for deterministic checks, package creation, schema enforcement, or fragile transformations.
   - Integrate useful support files before deleting them. Remove only obsolete duplicates, unused scaffold, or files outside the workflow.
   - Never leave unfinished scaffold markers, fake examples, fabricated benchmark results, secrets, or credentials.

5. **Validate**
   - Run `scripts/validate_hardened_skill.py` against the target.
   - Re-run `scripts/hardening_audit.py` and compare before/after.
   - Run modified scripts once on representative inputs.
   - If a gate fails, fix within scope or report the blocker. Do not claim readiness after failed validation.

6. **Package**
   - When requested, run `scripts/package_skill.py` with target, output, and validation arguments.
   - Package only the final skill folder; exclude caches, `.git`, temporary reports, generated evidence, secrets, and blocked paths.
   - Validate the archive and report commands, path, and residual risks.

## Output Contract

Final responses include applicable:

1. Mode and target path.
2. Baseline inventory and audit score, when measured.
3. Initial/final gates, including package gates when packaging was requested.
4. Hardening plan with hypotheses, scenarios, metrics, evaluators, and gates when planning or edits are in scope.
5. Changes by `SKILL.md`, `references/`, `scripts/`, `assets/templates/`, `examples/`, `evals/`, validation, packaging.
6. Commands executed and pass/fail outcomes.
7. Before/after score or gate comparison.
8. Files created/changed and blocked paths protected.
9. Remaining risks, assumptions, or follow-up hypotheses.
10. Package artifact path when produced.

## Stop Conditions

Stop before editing when:

- Target path lacks exactly one `SKILL.md`.
- Requested scope includes fixtures, expected outputs, secrets, credentials, `.git`, generated baseline/evidence, or user-blocked paths.
- Requested change needs domain facts absent from the skill, user input, repository evidence, approved research, or supplied docs.
- Requested output would claim scenario metrics or benchmark results not executed or supplied.
- Package cannot be validated after a structural change.
- User asks to improve a non-skill repository without a concrete skill target.

## Finalization Checklist

Before claiming hardened status:

- `SKILL.md` frontmatter has only lowercase `name` and `description`.
- Scope boundary, modes, workflow, output contract, stop conditions, and validation rules are present.
- Referenced files exist; important support files are referenced, script-consumed, copied/filled by workflow, validated, or asset-only by rationale.
- No placeholder scaffold or unfinished markers remain.
- Added/modified scripts were run once, or the reason they could not run is stated.
- Template-backed structures have validation or writer coverage when mechanical correctness matters.
- Behavioral scenarios are proposed or measured; measured metrics are never fabricated.
- Package validation passes before sharing `skill.zip`.
