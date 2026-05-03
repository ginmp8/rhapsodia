---
name: skill-harness
description: use to design, run, audit, validate, package, or apply evidence-based harnesses for existing ChatGPT or agent skill packages. Supports auto/context/full modes; audit-only/plan-only/apply/validation-only/package mutation; skill folders or extracted zips; approved research; scenarios, metrics, gates, validators, reports, bounded edits, comparison, and skill.zip packaging. Do not use for generic code, normal docs/reports, product planning, prompt advice, skill creation, or skill explanations.
---

# Skill Harness

## Purpose

Build an evidence harness for an existing ChatGPT or Agent skill so it can be audited, improved, validated, compared, and packaged without ad hoc rewriting. Own `SKILL.md`, `references/`, `scripts/`, `assets/templates/`, `evals/`, examples, validators, reports, and package hygiene.

## Activate / Do Not Activate

Use when asked to inspect, audit, harden, benchmark, validate, package, or harness an existing skill package; edit a skill folder or extracted zip with evidence; define activation, non-activation, ambiguous, edge, regression, adversarial, or output-contract scenarios; create metrics, gates, evaluators, validators, reports, or packaging checks; or compare baseline/final skill quality after bounded edits.

Do not use for generic code review, application refactors, CI work, implementation outside a reusable skill, one-off prompt writing/advice, ordinary document/slide/spreadsheet/report generation, net-new skill creation, skill explanations, or autonomous work without target, scope, blocked paths, and gates. Use skill-creator for new skills or skill explanations.

## Inputs, Assumptions, Scope

Resolve before mutation: `TARGET_SKILL_PATH` with exactly one target `SKILL.md`; harness mode `auto|context|full`; mutation mode `audit-only|plan-only|apply|validation-only|package`; writable scope; blocked paths; evidence policy/source list; gates; and final artifact.

Defaults for “improve this skill”: `auto`, `apply`, target-folder-only edits, protected fixtures/secrets, baseline first, one bounded patch batch, validation, and package only when requested or clearly expected.

Blocked paths: secrets, credentials, `.git`, evaluator fixtures, expected outputs, generated baseline evidence, benchmark baselines, generated reports, old packages, and user-declared read-only paths. Gates: valid structure, no scaffold markers, references exist, deterministic validators pass, target tests pass when present, and package validation passes before any `skill.zip` claim.

## Mode Selection and Mutation Rights

Harness modes: `auto` inspects first and researches only concrete weaknesses; `context` uses target and supplied context only; `full` combines target evidence, user context, and approved current primary sources. If research is forbidden, use `context` behavior.

Mutation modes: `audit-only` reports inventory/audit findings without edits; `plan-only` writes a harness map without edits; `apply` makes target-scope edits and validates; `validation-only` reports pass/fail gates without edits unless allowed; `package` returns a validated `skill.zip` only after package checks pass.

## Resources and Progressive Loading

Always read target `SKILL.md` first. Load only needed branches:

- `references/harness-principles.md`: harness map, integration, decisions, evidence.
- `references/mode-research-policy.md`: source policy and conflicts.
- `references/skill-improvement-playbook.md`: bounded changes and common fixes.
- `references/evaluation-and-gates.md`: scores, required gates, saturated metrics, decisions.
- `references/scenario-suite-guidelines.md`: activation, non-activation, ambiguous, edge, regression, adversarial scenario schema.
- `references/harness-quality-patterns.md`: fuzzing-inspired quality patterns for entry-point coverage, structured inputs, determinism, isolation, throughput, observability, and anti-patterns.
- `references/report-contract.md`: report shape and evidence labels.
- `references/cli-and-packaging-contract.md`: command contracts, exits, exclusions, package order.
- `assets/templates/harness-plan.md.template`, `assets/templates/harness-report.md.template`, `assets/templates/scenario-suite.json.template`: copy/fill/render when useful.
- `scripts/skill_harness_inventory.py`, `scripts/skill_harness_audit.py`, `scripts/skill_harness_validate.py`, `scripts/skill_harness_package.py`: inventory, audit, validation, packaging.
- `examples/harness-hardening-cases.md`: human-review activation and boundary examples.

Templates are operational when copied, filled, rendered, validated, or declared in workflow. Keep this file as control plane; keep rubrics, schemas, examples, and script contracts in references/examples.

## Harness Map

Define before editing: decision; object under test; writable/read-only/blocked scope; dependencies; target entry points; scenario groups; input corpus/model; evidence sources; runner commands; evaluators; metrics; gates; and evidence record for baseline, plan, changes, command outputs, final comparison, package path, risks, and rollback.

## Workflow

1. **Inspect** target `SKILL.md`, confirm exactly one `SKILL.md`, and inventory support dirs.

   ```bash
   python /home/oai/skills/skill-harness/scripts/skill_harness_inventory.py --target <TARGET_SKILL_PATH> --output <report-dir>/inventory.json
   ```

2. **Baseline** with static audit before planning. Treat score as structural evidence, not behavior proof. If saturated, add auxiliary metrics before claiming improvement.

   ```bash
   python /home/oai/skills/skill-harness/scripts/skill_harness_audit.py --target <TARGET_SKILL_PATH> --output <report-dir>/harness-audit.md --json-output <report-dir>/harness-audit.json
   ```

3. **Plan** evidence policy, hypotheses, target entry points, input corpus/model, scenarios, metrics, evaluators, gates, validation, packaging, and risk. Prefer `assets/templates/harness-plan.md.template` for durable plans. For high-risk or saturated-score targets, load `references/harness-quality-patterns.md` and add auxiliary coverage metrics before claiming improvement.
4. **Apply** bounded edits only inside allowed scope. Preserve target behavior; move long branch rules to references; add scripts only for deterministic work; add scenario suites only when behavior evidence matters; design scenarios to reach target entry points with structured inputs, deterministic isolation, observable failures, and focused corpus slices; integrate resources by workflow reference, script consumer, validator, or copy/fill instruction; classify before deletion; never invent benchmark, scenario, validation, install, or package evidence.
5. **Validate and compare** by rerunning inventory/audit, validator, modified-script syntax checks, target tests when present, and baseline/final comparison including auxiliary metrics.

   ```bash
   python /home/oai/skills/skill-harness/scripts/skill_harness_validate.py --target <TARGET_SKILL_PATH> --output <report-dir>/validation.json
   ```

6. **Package artifact** only when gates pass; use strict packaging for publish-ready delivery or when major risks should block output.

   ```bash
   python /home/oai/skills/skill-harness/scripts/skill_harness_package.py --target <TARGET_SKILL_PATH> --output <artifact-dir>/skill.zip --report <report-dir>/package-validation.json --strict
   ```

7. **Report** with `assets/templates/harness-report.md.template` when durable output helps. Return a package path only when the file exists and package report succeeds.

## Output Contract

Final response/report includes mode and target; decision; evidence policy/source list; baseline inventory and audit gates; harness map/plan; hypotheses; scenario status; metrics/evaluators; changes; validation commands/outcomes; before/after comparison; auxiliary metrics for saturated scores; residual risks/assumptions; recommendation; and package artifact path only when valid.

Evidence labels: `measured` for executed commands/tests/validators/package/scenario results; `derived` for file/context inspection; `researched` for cited research; `proposed` for planned checks; `unknown` for unavailable facts. Scenario pass rates, activation precision/recall, and behavioral conformance are measured only after prompts execute and evaluator decisions are captured.

## Stop Conditions

Stop before editing when the target lacks exactly one `SKILL.md`, is not a skill package, mode lacks required context, requested changes touch blocked paths, validation/evaluator assets would be altered to fake success, package creation would include generated evidence/secrets/caches, needed source truth is unavailable, unsupported domain facts would be invented, or validation fails after structural changes and cannot be fixed within scope.

## Finalization Checklist

Before success claims, verify: baseline inventory/audit ran; mode/evidence policy was followed; harness map existed before edits; every added resource is referenced, script-consumed, validator-covered, or intentionally retained; scaffold markers and generated noise are absent; modified scripts ran or blockers are reported; gates are truthful; measured facts are separate from proposals; blocked paths stayed unchanged; and any returned `skill.zip` exists with passing package validation.
