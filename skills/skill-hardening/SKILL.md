---
name: skill-hardening
description: harden existing chatgpt or agent target skill packages by inspecting a target skill folder or extracted zip, auditing skill.md plus bundled agents, references, scripts, templates, assets, examples, evals, validators, and packaging hygiene, applying bounded package-level improvements, validating gates, and building skill.zip. use when asked to improve, mature, standardize, harden, repair, validate, or package a reusable target skill package. do not use for creating a skill from scratch, generic repository refactoring, ordinary document writing, product planning, or benchmark-only scoring without package improvements.
---

# Skill Hardening

## Purpose

Harden a target ChatGPT or Agent skill as a complete reusable package. Improve the control plane in `SKILL.md`, and inspect or improve the surrounding package resources: `agents/openai.yaml`, `references/`, `scripts/`, `assets/templates/`, `examples/`, `evals/`, validators, output contracts, and packaging hygiene.

Use this skill when the object under work is a reusable skill package. Do not use it for generic repository refactoring, product planning, normal document writing, implementation tasks where the artifact is not a skill, or net-new skill creation without an existing target package.

## Required Inputs

Resolve these before editing a target skill:

1. `TARGET_SKILL_PATH`: folder, extracted zip, or named installed skill resolving to exactly one target skill root.
2. Mutation mode: `audit-only`, `plan-only`, `apply-hardening`, `validation-only`, or `package`.
3. Allowed mutation scope: default to the target skill folder only.
4. Blocked paths: benchmark fixtures, expected outputs, secrets, `.git`, generated evidence reports, generated baseline reports, and any user-declared read-only files.
5. Evidence sources: target package files, user feedback, benchmark report, failed prompts, previous outputs, target-domain docs, repository truth, or existing package resources.
6. Research permission: in `auto` runs, research only concrete gaps found during inspection; in constrained runs, use only supplied or target-local evidence.
7. Acceptance gates: minimum audit score, required validation commands, package validation, no unresolved scaffold markers, all referenced files present, and optional benchmark or behavioral scenario results.

If the user gives only a target folder and asks to harden it, proceed with conservative defaults: audit, create a hardening map, apply one bounded package-level improvement batch, run validators, and package only if requested or clearly expected.

## Mode Selection Matrix

| User intent | Mode | Primary output | Required validation |
|---|---|---|---|
| Understand weaknesses in a target skill | `audit-only` | Audit report and prioritized findings | `scripts/hardening_audit.py` |
| Decide what supporting files should exist | `plan-only` | Hardening map with resource blueprint | Inventory plus audit report |
| Improve the target skill package | `apply-hardening` | Updated package files and validation evidence | Inventory, audit, target-specific checks, `scripts/validate_hardened_skill.py` |
| Check whether a hardened skill is ready | `validation-only` | Pass/fail gates and residual risks | `scripts/validate_hardened_skill.py`; include package check when a zip exists |
| Deliver an installable skill | `package` | `skill.zip` plus validation evidence | Folder validator, package builder, package validator |

Use one primary mode per run. If the request mixes redesign, evaluator design, validation, and package delivery, stage the work: inspect, audit, harden, validate, then package.

## Progressive Loading

Load only the resource needed for the current branch:

- `references/mature-skill-patterns.md`: mature control-plane, mode, stop-condition, and output-contract patterns.
- `references/resource-hardening-playbook.md`: deciding whether to add, integrate, migrate, or remove references, scripts, templates, assets, and examples.
- `references/evaluator-contract.md`: gate design, score interpretation, auxiliary metrics for saturated audits, and report minimums.
- `references/evidence-policy.md`: research, source handling, evidence recording, and measured-versus-proposed claim rules.
- `references/scenario-suite.md`: creating activation, non-activation, ambiguous, edge-case, regression, and adversarial scenario suites.
- `references/packaging-and-validation.md`: command contracts, zip creation, package validation, exclusion policy, and delivery evidence.
- `assets/templates/hardening-plan.md.template`: stable shape for a hardening plan.
- `assets/templates/hardening-report.md.template`: stable shape for a final hardening report.
- `assets/templates/reference-file.md.template`: shape for new target-specific references.
- `assets/templates/scenario-suite.json.template`: shape for planned behavioral scenario suites.
- `examples/hardening-scenarios.json`: concrete scenario examples for activation and conformance design.
- `evals/activation-scenarios.json`: planned scenario suite for this skill's own trigger, boundary, and edge-case behavior.
- `scripts/inventory_skill.py`: deterministic tree inventory and reference/resource integration signal.
- `scripts/package_skill.py`: deterministic package builder and archive validator for `skill.zip` delivery.

Keep `SKILL.md` as a router. Put detailed rubrics, schemas, command sequences, examples, and script contracts in references or examples and load them only when needed.

## Workflow

1. **Inspect the target skill.**
   - Read the target `SKILL.md` first.
   - Run `scripts/inventory_skill.py` with target and output arguments. See `references/packaging-and-validation.md` for the exact command sequence.
   - Identify `agents/`, `references/`, `scripts/`, `assets/`, `assets/templates/`, `examples/`, `evals/`, tests, benchmark evidence, validators, and unused scaffold files.

2. **Run the package hardening audit.**
   - Run `scripts/hardening_audit.py` with target, markdown output, and json output arguments. See `references/packaging-and-validation.md` for the exact command sequence.
   - Treat the audit as structural evidence, not as a substitute for domain judgment.
   - If the score is saturated, add a non-saturated auxiliary signal such as scenario-suite schema quality, unresolved-risk count, placeholder-marker count, script test pass rate, or package validation gate count.

3. **Build a hardening map.**
   - Separate planned changes into `control_plane`, `references`, `scripts`, `templates_assets`, `examples_scenarios`, `validation`, and `packaging`.
   - For each change, state the hypothesis, target files, expected improvement, and validation gate.
   - Preserve target-specific behavior that is already useful.
   - Prefer references for branch-specific rules, scripts for repeatable checks, templates for reusable artifact shapes, and examples or evals for behavioral calibration.

4. **Apply bounded changes.**
   - Edit only the allowed target skill scope.
   - Keep `SKILL.md` compact as a router and control plane; move long rubrics, schemas, and command details into references.
   - Add or improve scripts only when deterministic checks, package creation, schema enforcement, or fragile transformations benefit from automation.
   - Integrate useful supporting files before deleting them. Remove only obsolete duplicates, unused scaffold files, or files outside the declared workflow.
   - Do not leave unfinished scaffold markers, fake examples, fabricated benchmark results, secrets, or credentials.

5. **Validate and decide.**
   - Run `scripts/validate_hardened_skill.py` against the target.
   - Re-run `scripts/hardening_audit.py` after edits and compare before/after results.
   - Run modified scripts at least once on representative inputs.
   - If a gate fails, fix within scope or report the blocker. Do not claim readiness when validation failed.

6. **Package when requested.**
   - Use `scripts/package_skill.py` with target, output, and validation arguments when available.
   - Package only the final skill folder, excluding caches, `.git`, temporary reports, generated evidence, secrets, and blocked paths.
   - Validate the package after creation and report exact commands, output path, and residual risks.

## Output Contract

For any hardening run, final responses must include:

1. Mode and target path.
2. Baseline inventory and audit score, when measured.
3. Initial and final gates, including package gates when packaging was requested.
4. Harness map or hardening plan with hypotheses, scenarios, metrics, evaluators, and gates when planning or edits are in scope.
5. Changes made, grouped by `SKILL.md`, `references/`, `scripts/`, `assets/templates/`, `examples/`, `evals/`, validation, and packaging.
6. Commands executed and pass/fail outcomes.
7. Before/after score or gate comparison when available.
8. Files created, files changed, and blocked paths protected.
9. Remaining risks, assumptions, or follow-up hypotheses.
10. Package artifact path when produced.

## Stop Conditions

Stop or return a blocker before editing when:

- The target path does not contain exactly one `SKILL.md`.
- The requested mutation scope includes evaluator fixtures, expected outputs, secrets, credentials, `.git`, generated baseline evidence, or user-declared blocked paths.
- The requested change would require domain facts not present in the skill, user input, repository evidence, approved research, or supplied docs.
- A requested output would require claiming measured scenario metrics or benchmark results that were not actually executed.
- The target package cannot be validated after a structural change.
- The user asks to improve a non-skill repository without a concrete skill target.

## Finalization Checklist

Before claiming a skill is hardened:

- `SKILL.md` has valid frontmatter with only `name` and `description`, both lowercase values.
- Scope boundary, mode selection, workflow, output contract, stop conditions, and validation rules are present.
- Every referenced file exists.
- Every important supporting file is referenced, script-consumed, copied or filled by a declared workflow, validated, or intentionally asset-only with a clear rationale.
- Placeholder scaffold files and residual unfinished markers are absent.
- Scripts added or modified were run at least once, or the reason they could not run is stated.
- Template-backed structures have validation or writer coverage when mechanical correctness matters.
- Behavioral scenarios are proposed or measured; measured metrics are never fabricated.
- Packaging validation passes before sharing `skill.zip`.
