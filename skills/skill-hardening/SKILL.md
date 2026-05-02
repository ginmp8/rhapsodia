---
name: skill-hardening
description: harden existing chatgpt or agent skill packages by auditing skill.md, agents, references, scripts, templates, scenarios, validators, output contracts, gates, and packaging hygiene. use for skill repair, maturity review, validation, hardening, and skill.zip delivery; not for net-new skills, generic repos, product planning, or benchmark-only scoring.
---

# Skill Hardening

## Purpose

Harden an existing ChatGPT or Agent skill as a reusable package. Own `SKILL.md`, `agents/openai.yaml`, `references/`, `scripts/`, `assets/templates/`, `examples/`, `evals/`, validators, output contracts, gates, and package hygiene.

Use only for reusable skill packages. Do not use for generic repo refactors, product planning, ordinary docs, non-skill implementation work, or net-new skill creation without an existing package.

## Inputs

Resolve or infer before mutation:

1. `TARGET_SKILL_PATH`: folder, extracted zip, or installed skill with exactly one root `SKILL.md`.
2. Mode: `audit-only`, `plan-only`, `apply-hardening`, `validation-only`, or `package`.
3. Scope: target folder only unless the user narrows further.
4. Blocked: benchmark fixtures, expected outputs, secrets, credentials, `.git`, generated evidence/baseline reports, symlinks that can escape target scope, and user-declared read-only files.
5. Evidence: target files, user feedback, benchmark reports, failed prompts, prior outputs, domain docs, repository truth, or existing resources.
6. Research: `auto` only for concrete inspection gaps; constrained runs use supplied or target-local evidence.
7. Gates: audit score, required commands, package validation, no scaffold markers, all referenced files present, optional benchmark/scenario evidence.

Default for “harden it”: inspect -> audit -> map -> apply one bounded package-level batch -> validate -> package only when requested or clearly expected.

## Modes

| Intent | Mode | Output | Validation |
|---|---|---|---|
| Understand weaknesses | `audit-only` | audit report, prioritized findings | `scripts/hardening_audit.py` |
| Decide support files | `plan-only` | hardening map, resource blueprint | inventory plus audit |
| Improve package | `apply-hardening` | updated files, validation evidence | inventory, audit, `scripts/validate_hardened_skill.py` |
| Check readiness | `validation-only` | pass/fail gates, risks | `scripts/validate_hardened_skill.py`; include zip check if present |
| Deliver package | `package` | validated `skill.zip` | folder validator, package builder, archive validator |

Use one primary mode. For mixed requests: inspect -> audit -> harden -> validate -> package.

## Load only needed resources

- `references/mature-skill-patterns.md`: control plane, modes, outputs, stop rules.
- `references/resource-hardening-playbook.md`: resource add/integrate/migrate/remove rules.
- `references/evaluator-contract.md`: gates, scores, saturated-audit auxiliary metrics, report minimums.
- `references/evidence-policy.md`: source order, measured-vs-proposed claims, research limits.
- `references/scenario-suite.md`: activation, non-activation, ambiguous, edge, regression, adversarial scenarios.
- `references/packaging-and-validation.md`: commands, zip creation, package validation, exclusions, delivery evidence.
- `assets/templates/hardening-plan.md.template`: plan skeleton.
- `assets/templates/hardening-report.md.template`: report skeleton.
- `assets/templates/reference-file.md.template`: reference skeleton.
- `assets/templates/scenario-suite.json.template`: scenario skeleton.
- `examples/hardening-scenarios.json`: calibration examples.
- `evals/activation-scenarios.json`: planned activation/boundary suite.
- `scripts/inventory_skill.py`: deterministic inventory.
- `scripts/hardening_audit.py`: maturity scorecard.
- `scripts/validate_hardened_skill.py`: readiness gates.
- `scripts/package_skill.py`: `skill.zip` builder and archive validator.

Keep `SKILL.md` as router/control plane. Move detailed rubrics, schemas, commands, examples, and script contracts to lazy-loaded resources.

## Workflow

1. **Inspect**: read target `SKILL.md`; run `scripts/inventory_skill.py`; inventory `agents/`, `references/`, `scripts/`, `assets/`, templates, `examples/`, `evals/`, tests, benchmark evidence, validators, packages, generated noise, and unused scaffold.
2. **Audit**: run `scripts/hardening_audit.py` with markdown/json outputs; treat it as structural evidence. If score is saturated, add a non-saturated signal: scenario quality, unresolved risks, placeholder count, script test pass rate, package gates, or token delta.
3. **Map**: group changes by `control_plane`, `references`, `scripts`, `templates_assets`, `examples_scenarios`, `validation`, `packaging`. For each change record hypothesis, files, expected effect, validation gate, and accept/reject decision.
4. **Apply**: edit only allowed target files. Keep `SKILL.md` compact. Use references for branch rules, scripts for deterministic checks, templates for artifact shapes, examples/evals for calibration. Remove only obsolete duplicates, generated noise, caches, old zips, unused scaffold, or files outside workflow.
5. **Validate**: run `scripts/validate_hardened_skill.py`; re-run `scripts/hardening_audit.py`; run modified scripts once on representative inputs. Fix failed gates within scope or report the blocker. Never claim readiness after failed validation.
6. **Package**: when requested, run `scripts/package_skill.py` with target, output, and validation. Package only the final skill folder; exclude caches, `.git`, temporary reports, generated evidence, secrets, symlinks, and blocked paths. Validate archive before providing `skill.zip`.

## Output contract

Final responses include applicable:

1. Mode and target path.
2. Baseline inventory/audit score when measured.
3. Initial/final gates, including package gates when requested.
4. Hardening plan with hypotheses, scenarios, metrics, evaluators, gates.
5. Changes by `SKILL.md`, `references/`, `scripts/`, `assets/templates/`, `examples/`, `evals/`, validation, packaging.
6. Commands executed with pass/fail outcomes.
7. Before/after score or gate comparison.
8. Files changed and blocked paths protected.
9. Remaining risks, assumptions, follow-up hypotheses.
10. Package path only when produced and validated.

## Stop conditions

Stop before editing when target root is ambiguous; scope requires blocked paths without explicit authorization; needed facts are absent from evidence; requested output would claim unexecuted benchmark/scenario metrics; package cannot be validated after structural change; or the user asks to improve a non-skill repo without a concrete skill target.

## Finalization checklist

Before claiming hardened status: frontmatter has only lowercase `name` and `description`; scope, modes, workflow, output contract, stop, validation, and packaging rules are present; referenced files exist; support files are referenced, script-consumed, copied/filled, validated, or intentionally asset-only; no scaffold markers remain; added/modified scripts ran once or blockers are stated; template-backed strict structures have validation/writer coverage; measured metrics are never fabricated; folder and archive validation pass before sharing `skill.zip`.
