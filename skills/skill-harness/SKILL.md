---
name: skill-harness
description: use when asked to design, run, audit, validate, package, or apply an evidence-based harness to improve a target chatgpt or agent skill package. supports auto, context, and full modes for inspecting skill folders or extracted zips, researching approved references, defining activation and edge scenarios, metrics, evaluators, gates, reports, validators, bounded edits, and skill.zip packaging. especially use for improving skill.md, references, scripts, templates, activation behavior, validation evidence, and packaging hygiene. do not use for generic code refactoring, normal document or report writing, product planning, or prompt advice unless the object under test is a reusable skill package.
---

# Skill Harness

## Purpose

Build an evidence-based harness around a target ChatGPT or Agent skill so the target can be audited, improved, validated, compared, and packaged through controlled evidence rather than ad hoc rewriting.

The skill owns reusable skill-package improvement work across `SKILL.md`, `references/`, `scripts/`, `assets/templates/`, `evals/`, activation scenarios, validators, reports, and packaging hygiene.

## Activation Boundaries

Use this skill when the user asks to:

- inspect, audit, harden, benchmark, validate, package, or apply a harness to an existing skill package;
- produce evidence-backed changes to a target skill folder or extracted skill zip;
- define activation scenarios, negative triggers, edge cases, metrics, gates, validators, reports, or packaging checks for a skill;
- compare baseline and final skill quality after bounded edits.

Do not use this skill for:

- generic code review, application refactoring, CI work, or repository implementation where the object under test is not a reusable skill;
- one-off prompt writing or prompt advice without a concrete target skill package;
- ordinary document, slide, spreadsheet, or report generation unless the artifact belongs to the skill package;
- creating a skill from scratch or explaining how ChatGPT skills work; use the skill-creator workflow instead;
- unbounded autonomous changes without target path, allowed scope, blocked paths, and validation gates.

## Required Inputs

Resolve or infer these before mutating any target:

1. `TARGET_SKILL_PATH`: a folder or extracted zip containing exactly one target skill.
2. Harness mode: `auto`, `context`, or `full`.
3. Mutation mode: `audit-only`, `plan-only`, `apply`, `validation-only`, or `package`.
4. Allowed mutation scope, defaulting to the target skill folder only.
5. Blocked paths, including secrets, `.git`, evaluator fixtures, expected outputs, generated baseline evidence, and any user-declared read-only paths.
6. Evidence policy: target files, supplied context, approved research sources, internal sources, or repository truth.
7. Acceptance gates: structural validity, no unresolved scaffold markers, referenced resources exist, deterministic validators pass, package validation passes when packaging is requested, and target-specific tests pass when available.
8. Final artifact expectation: report only, applied edits, validation result, or `skill.zip`.

If the user gives only a target skill and asks to improve it, use conservative defaults: `mode=auto`, `mutation=apply`, target-folder-only edits, protected fixtures and secrets, baseline before editing, one bounded improvement batch, validation, and packaging only when requested or clearly expected.

## Mode Selection

| User intent | Mode | Required inputs | Research rule | Primary output |
|---|---|---|---|---|
| Improve a target skill with little context | `auto` | target path, mutation scope, blocked paths | inspect target first, then research only where concrete weaknesses require it | harness plan plus bounded target improvements |
| Improve using supplied constraints only | `context` | target path and binding context | use only target contents and provided context | constrained changes and validation evidence |
| Combine supplied context with broader discovery | `full` | target path, context, research permission | reconcile target evidence, user context, and current primary sources | comprehensive harness run and package decision |

If the user forbids research, use `context` behavior even when they name another mode.

## Resource Map and Progressive Loading

Always read the target `SKILL.md` first. Then load only the resource needed for the current branch:

- `references/harness-principles.md` for decision statements, harness maps, components, evidence records, and scenario coverage.
- `references/mode-research-policy.md` for source selection, source conflicts, or research restrictions.
- `references/skill-improvement-playbook.md` for choosing bounded package changes.
- `references/evaluation-and-gates.md` for scoring, gates, saturated metrics, or readiness decisions.
- `references/scenario-suite-guidelines.md` for activation, ambiguous, edge, regression, or adversarial scenarios.
- `references/report-contract.md` for final responses or durable reports.
- `references/cli-and-packaging-contract.md` for deterministic command contracts, package exclusions, and script exit semantics.

Reusable assets and scripts:

- `assets/templates/harness-plan.md.template` is the default shape for harness plans.
- `assets/templates/harness-report.md.template` is the default shape for durable reports.
- `assets/templates/scenario-suite.json.template` is the default shape for new planned scenario suites when the user allows scenario file creation.
- Treat these templates as operational assets: they may be copied, filled, rendered by script, or used by the agent during a declared workflow. Do not migrate or remove a useful template merely because no script reads it directly.
- `scripts/skill_harness_inventory.py` creates deterministic structural inventory.
- `scripts/skill_harness_audit.py` scores harness readiness.
- `scripts/skill_harness_validate.py` evaluates structural, scenario, and script gates.
- `scripts/skill_harness_package.py` validates and writes `skill.zip`.
- `examples/harness-hardening-cases.md` provides concrete activation and boundary examples for human review.

Keep this `SKILL.md` as the control plane. Put detailed rubrics, schemas, examples, and script contracts in references or examples and load them conditionally.

## Harness Definition Model

Define the harness before editing. A valid harness map must name:

1. Decision: what release, merge, package, or readiness decision the run supports.
2. Object under test: target files and behaviors being evaluated.
3. Scope boundary: writable paths, read-only paths, blocked paths, and external dependencies.
4. Scenarios: activation, non-activation, ambiguous, edge, regression, and adversarial cases.
5. Evidence: target files, supplied context, researched sources, fixtures, golden examples, and measured command output.
6. Runner: commands for inventory, audit, validation, tests, and packaging.
7. Evaluators: deterministic checks, scenario review, human review hooks, and any target-specific validators.
8. Metrics: static score, gate status, scenario conformance when measured, validation pass/fail, package success, and auxiliary metrics for saturated scores.
9. Gates: non-negotiable pass/fail rules.
10. Evidence record: baseline, plan, changes, commands, outputs, final comparison, package path, and residual risks.

## Workflow

### 1. Inspect the target

- Read target `SKILL.md` first.
- Confirm the target contains exactly one `SKILL.md`.
- List `agents/`, `references/`, `scripts/`, `assets/`, `assets/templates/`, `examples/`, and `evals/` when present.
- Run inventory before editing.

Default inventory command:

```bash
python /home/oai/skills/skill-harness/scripts/skill_harness_inventory.py --target <TARGET_SKILL_PATH> --output <report-dir>/inventory.json
```

### 2. Establish the baseline

Run the static harness audit before planning changes:

```bash
python /home/oai/skills/skill-harness/scripts/skill_harness_audit.py --target <TARGET_SKILL_PATH> --output <report-dir>/harness-audit.md --json-output <report-dir>/harness-audit.json
```

Treat the score as structural evidence. Do not replace domain judgment, scenario execution, target-specific tests, or packaging validation with the score. If the score is saturated, define auxiliary metrics before claiming improvement.

### 3. Select evidence policy

- `auto`: derive research questions from observed weaknesses and use approved sources only as needed.
- `context`: use target files and supplied context only.
- `full`: combine supplied context with additional approved research and resolve conflicts explicitly.

Record used sources, excluded sources, conflicts, and unresolved unknowns.

### 4. Build the harness map

Use `assets/templates/harness-plan.md.template` unless the user requested a lighter inline plan. The plan must cover control plane, references, scripts, templates/assets, scenarios, validation, packaging, evidence, hypotheses, and acceptance gates.

### 5. Apply bounded improvements

- Preserve useful target-specific behavior.
- Edit only allowed paths.
- Move long rules to references and link them from this control plane.
- Add deterministic scripts for fragile, repetitive, schema-like, or validation-heavy tasks.
- Add scenario suites only when activation or behavior evidence matters and the user permits writing scenario files.
- Add templates only for stable repeatable artifacts, and keep each template integrated through a workflow reference, script consumer, validator, or explicit copy/fill instruction.
- When an audit or benchmark flags weak supporting-resource integration, classify the resource first. Prefer integrating, referencing, validating, or documenting useful assets before deleting them. Remove assets only when they are placeholders, duplicated, obsolete, misleading, or have no declared workflow use.
- Do not invent domain facts, benchmark results, scenario pass rates, validation evidence, installation status, or package state.

### 6. Validate and compare

After edits:

- Re-run inventory and audit.
- Run `scripts/skill_harness_validate.py` against the target.
- Run syntax checks for added or modified scripts.
- Run target-specific validators or tests when present.
- Run packaging validation when a package is requested.
- Compare baseline and final results, including auxiliary metrics when static scores are saturated.

Default validation command:

```bash
python /home/oai/skills/skill-harness/scripts/skill_harness_validate.py --target <TARGET_SKILL_PATH> --output <report-dir>/validation.json
```

Default package command:

```bash
python /home/oai/skills/skill-harness/scripts/skill_harness_package.py --target <TARGET_SKILL_PATH> --output <artifact-dir>/skill.zip --report <report-dir>/package-validation.json
```

### 7. Report and package

Use `assets/templates/harness-report.md.template` for durable reporting. Include mode, target, decision, evidence sources, baseline score, harness plan, changes, commands, before/after comparison, gates, residual risks, and package artifact path.

Return a package path only when `skill.zip` exists and the packaging report indicates success.

## Output Contracts

| Mutation mode | Required output | Mutation allowed |
|---|---|---|
| `audit-only` | baseline inventory, audit score, findings, missing components, prioritized improvements | no target edits |
| `plan-only` | harness map, evidence policy, proposed files, validation gates, implementation sequence | no target edits |
| `apply` | applied changes, validation evidence, before/after comparison, remaining risks | yes, within allowed scope |
| `validation-only` | pass/fail gates, commands, evidence paths, blockers, remediation | no target edits unless explicitly allowed |
| `package` | installable `skill.zip`, package validation evidence, exclusions, rollback notes | yes, only as needed to pass gates |

## Stop Conditions

Stop before editing and report a blocker when:

- the target path does not contain exactly one `SKILL.md`;
- the target is not a ChatGPT or Agent skill package;
- required context is missing in `context` mode;
- the user asks for external research under `context` constraints;
- requested changes would touch secrets, `.git`, evaluator fixtures, expected outputs, benchmark baselines, generated evidence, or user-declared blocked paths;
- the requested improvement requires unsupported domain facts;
- validation fails after structural changes and cannot be fixed within allowed scope.

## Finalization Checklist

Before claiming success:

- baseline inventory and audit were executed;
- selected mode and evidence policy were followed;
- harness map existed before edits;
- every added resource is referenced, script-consumed, validator-covered, or intentionally retained as an operational asset with declared workflow use;
- unresolved scaffold markers are absent;
- modified scripts were run or reported as untested;
- gates were evaluated truthfully;
- measured facts are separated from proposed scenarios and assumptions;
- blocked paths were not changed;
- `skill.zip` path points to a real artifact when package mode is claimed.
