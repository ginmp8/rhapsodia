---
name: skill-hardening
description: harden existing agent skills-compatible packages by auditing skill.md, adapters, references, scripts, templates, scenarios, validators, output contracts, gates, and packaging hygiene. use when asked to repair, validate, mature, harden, or package an existing skill; do not use for net-new skills, generic repositories, product planning, ordinary documentation, or benchmark-only scoring.
---

# Skill Hardening

## Purpose

Harden an existing Agent Skills-compatible skill as a reusable package. Own `SKILL.md`, optional host adapters such as `agents/openai.yaml`, `references/`, `scripts/`, `assets/templates/`, `examples/`, `evals/`, validators, output contracts, gates, and package hygiene.

Use only for reusable skill packages. Do not use for generic repo refactors, product planning, ordinary docs, non-skill implementation work, or net-new skill creation without an existing package.

## Required Inputs

Resolve or infer before mutation:

1. `TARGET_SKILL_PATH`: folder, extracted zip, or installed skill with exactly one root `SKILL.md`.
2. Mode: `audit-only`, `plan-only`, `apply-hardening`, `validation-only`, or `package`.
3. Scope: target folder only unless the user narrows further.
4. Baseline: immutable copy, clean commit, or equivalent before-state plus deterministic target identity.
5. Blocked: benchmark fixtures, expected outputs, secrets, credentials, `.git`, generated evidence/baseline reports, frozen evaluators, symlinks that can escape target scope, and user-declared read-only files.
6. Evidence: target files, user feedback, benchmark reports, failed prompts, prior outputs, domain docs, repository truth, or existing resources.
7. Reproducibility ceiling: `objective-artifact`, `tool-action`, `research-analytic`, or `constrained-subjective`; do not promise determinism above it.
8. Research: `auto` only for concrete inspection gaps; constrained runs use supplied or target-local evidence.
9. Gates: audit score, required commands, evaluator integrity, package validation, no scaffold markers, all referenced files present, optional executed benchmark/scenario evidence.

Default for “harden it”: inspect -> audit -> map -> apply one bounded package-level batch -> validate -> package only when requested or clearly expected.

## Authority Boundary

- **Standalone:** own hardening, validation, freeze, and package delivery within the target skill only.
- **Delegated:** when an upstream orchestrator supplies frozen evaluators, peer contracts, scope, or promotion rules, treat them as protected inputs. Mutate only the assigned target batch, do not change peer-facing schemas/CLIs/handoffs silently, and return hardening evidence to the caller. Global sequencing, ecosystem promotion, and installation remain with the caller.
- If a sound fix requires a breaking peer contract, stop independent promotion and report the affected contract/consumers for a coordinated change set. Do not add legacy adapters merely to preserve an obsolete contract the caller has retired.

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
- `references/reproducibility-controls.md`: baseline identity, variability map, frozen evaluator, diagnostic repair, claim layers, and freeze-after-pass.
- `references/packaging-and-validation.md`: commands, zip creation, package validation, exclusions, delivery evidence.
- `assets/templates/hardening-contract.json.template`: machine-readable hardening/reproducibility contract; copy and fill before material edits when improvement claims or package delivery matter.
- `assets/templates/hardening-plan.md.template`: plan skeleton.
- `assets/templates/hardening-report.md.template`: report skeleton.
- `assets/templates/reference-file.md.template`: reference skeleton.
- `assets/templates/scenario-suite.json.template`: scenario skeleton.
- `examples/hardening-scenarios.json`: calibration examples.
- `evals/activation-scenarios.json`: planned activation/boundary suite.
- `scripts/inventory_skill.py`: deterministic inventory.
- `scripts/hardening_audit.py`: maturity scorecard.
- `scripts/validate_hardened_skill.py`: readiness gates.
- `scripts/reproducibility_controls.py`: tree identity, contract validation, evaluator freeze, and evaluator verification.
- `scripts/package_skill.py`: deterministic `skill.zip` builder, alias preflight, rollback-safe commit, receipt, and archive validator.
- `tests/test_skill_hardening.py`: standard-library regression tests for scenario validation and package delivery invariants.

Keep `SKILL.md` as router/control plane. Move detailed rubrics, schemas, commands, examples, and script contracts to lazy-loaded resources.

## Workflow

1. **Inspect and baseline**: read target `SKILL.md`; preserve an immutable before-state; run `scripts/inventory_skill.py`; compute target identity with `scripts/reproducibility_controls.py tree-hash`; inventory `agents/`, `references/`, `scripts/`, `assets/`, templates, `examples/`, `evals/`, tests, benchmark evidence, validators, packages, generated noise, and unused scaffold.
2. **Audit**: run `scripts/hardening_audit.py` with markdown/json outputs; treat it as structural evidence. If score is saturated, add a non-saturated signal: scenario quality, unresolved risks, residual scaffold-marker count, script test pass rate, package gates, or token delta.
3. **Contract and freeze**: classify the reproducibility ceiling; map variance across activation, inputs, routing, decisions, generation, validation, repair, and delivery; fill and validate `assets/templates/hardening-contract.json.template`; freeze only the evaluator inputs that will decide acceptance. Keep candidate generators and files that must change outside the frozen set.
4. **Map**: group changes by `control_plane`, `references`, `scripts`, `templates_assets`, `examples_scenarios`, `validation`, `packaging`. For each change record hypothesis, evidence, files, expected effect, validation gate, and accept/reject decision.
5. **Apply**: edit only allowed target files. Keep `SKILL.md` compact. Use references for branch rules, scripts for deterministic checks, templates for artifact shapes, examples/evals for calibration. Remove only obsolete duplicates, generated noise, caches, old zips, unused scaffold, or files outside workflow.
6. **Repair by diagnosis**: run the narrowest failing gate, apply the smallest supported fix, then rerun the same gate. Stop a repair branch after two consecutive non-improving rounds unless new evidence changes the hypothesis. Never weaken a gate or frozen evaluator to obtain a pass.
7. **Validate and freeze**: verify the evaluator manifest; run `scripts/validate_hardened_skill.py`; re-run `scripts/hardening_audit.py`; run modified scripts once on representative inputs. Compare baseline and candidate using identical cases when claiming behavioral improvement. A passing candidate is frozen; any later edit invalidates affected evidence and requires revalidation.
8. **Package**: when requested, run `scripts/package_skill.py` with target, output, validation, and JSON receipt. Package only the frozen final skill folder; exclude caches, `.git`, temporary reports, generated evidence, secrets, symlinks, and blocked paths. Validate the archive before atomic replacement and verify that receipt hashes correspond to the delivered candidate and ZIP.

## Output contract

Final responses include applicable:

1. Mode and target path.
2. Baseline and candidate identities, inventory, and audit score when measured.
3. Reproducibility ceiling, variability controls, and irreducible judgment.
4. Initial/final gates, frozen-evaluator verification, and package gates when requested.
5. Hardening plan with hypotheses, scenarios, metrics, evaluators, gates.
6. Changes by `SKILL.md`, `references/`, `scripts/`, `assets/templates/`, `examples/`, `evals/`, validation, packaging.
7. Commands executed with pass/fail/not-run outcomes and evidence labels.
8. Before/after score or gate comparison; never infer behavioral improvement from structural evidence alone.
9. Files changed and blocked paths protected.
10. Remaining risks, assumptions, follow-up hypotheses.
11. Package path, candidate hash, and archive hash only when produced and validated.

## Stop conditions

Stop before editing when target root is ambiguous; no immutable baseline can be preserved; scope requires blocked paths without explicit authorization; needed facts are absent from evidence; a required evaluator cannot be frozen or changes during the run; requested output would claim unexecuted benchmark/scenario metrics; package cannot be validated after structural change; passing requires weakening a gate; or the user asks to improve a non-skill repo without a concrete skill target.

## Finalization checklist

Before claiming hardened status: frontmatter has only lowercase `name` and `description`; baseline and final identities are recorded; scope, modes, workflow, output contract, stop, validation, and packaging rules are present; referenced files exist; support files are referenced, script-consumed, copied/filled, validated, or intentionally asset-only; frozen evaluators verify unchanged; no scaffold markers remain; added/modified scripts ran once or blockers are stated; template-backed strict structures have validation/writer coverage; structural, behavioral, runtime, and perceptual claims remain separate; measured metrics are never fabricated; no edits occurred after the final pass; folder and archive validation pass and receipt hashes match before sharing `skill.zip`.
