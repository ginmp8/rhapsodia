# Harness Design

Use when building a complete `skill-improver` harness or when a saturated static score needs a non-saturated auxiliary contract before claiming improvement.

## Decision

After the harness runs, decide: accept, accept with risks, reject, validation-only, or plan-only. Distinguish measured evidence from proposed evidence.

## Behavior under test

Verify the skill guides a user/agent to: inspect target before mutation; prepare/freeze benchmark; measure baseline; choose one falsifiable hypothesis; edit only allowed paths; accept/reject/revert from evidence; validate/package/install only after gates; report commands, evidence, blocked paths, and risks truthfully.

## Source basis

- Supplied context: small mutable surface, fixed budget, baseline first, one measurable metric, accept/discard, logged outcomes.
- Target package: already defines benchmark freezing, blocked paths, saturated metrics, self-improvement safeguards, runner, and static scorer.
- External research: use only for concrete gaps after reading target package/context, such as changed external evaluator CLI; record sources separately.

## Scope

In scope: `SKILL.md` activation/workflow/modes/stops/output; `references/` policies; `scripts/` runners/validators; `evals/` scenarios; `references/report-template.md` plus templates consumed by `scripts/skill_improver_loop.py`; packaging exclusions, evidence, and resource-integration checks.

Out of scope unless requested: modifying locked fixtures/expected outputs during an improvement iteration; editing secrets, caches, package artifacts, generated evidence, or `.git`; claiming scenario pass rates without executed outputs; unbounded autonomous loops outside a disposable sandbox.

## Scenario suite

Use `evals/skill-improver-scenarios.json` as the frozen planned suite. A measured suite may derive from it, but measured results must be locked before candidate edits. Required categories: `should_activate`, `should_not_activate`, `ambiguous`, `edge_case`, `regression`.

## Evaluators

- Structural: inventory and audit package structure, references, placeholders, scenarios, validation, maintainability.
- Activation: review planned/measured scenarios; calculate precision/recall only when actual activation decisions are captured.
- Output conformance: final report includes baseline, final score, evaluator hash, accepted/rejected hypotheses, files changed, gates, package result, risks.
- Safety/scope: blocked paths unchanged, mutation scope respected, sandbox stated, no unsupported persistence claims.
- Packaging: run `scripts/validate_skill_improver_package.py`; verify archive excludes evidence, caches, secrets, transient state; verify `assets/templates/improvement-run-report.md.template` and `assets/templates/patch-decision-record.md.template` are consumed by `scripts/skill_improver_loop.py`. For other skills, templates must be script-consumed, workflow-filled/copied, explicitly referenced, or validator-gated before counting as integrated.

## Metrics

- Activation precision: correct activations / actual activations; not measured until outputs exist.
- Activation recall: correct activations / expected activations; not measured until outputs exist.
- Output conformance: required report sections satisfied / required sections.
- Criteria coverage: required harness criteria satisfied / required criteria.
- Robustness: passed edge+regression scenarios / executed edge+regression scenarios.
- Rework risk: low/medium/high from failed gates, unmeasured behavior, and manual-review burden.

## Gates

Blocking: exactly one skill file; frontmatter name/description; no unresolved placeholders; referenced resources exist; required scenario categories exist; deterministic validator passes; reusable templates integrated through runner/workflow/copy-fill instruction/validation gate; no blocked paths or generated evidence added as target content; package archive produced when requested.

Warnings: activation metrics planned but not measured; auxiliary metric needed because primary metric is saturated; external evaluator unavailable in runtime; self-improvement lacks separate persistent installation destination.

Informational: no extra research needed; package applies only to current runtime unless installed elsewhere; scenario suite should grow after user feedback/incidents.

## Evidence record

Record baseline inventory/audit/static score/evaluator hashes; source summary split by supplied context, target contents, and researched sources; harness map and hypotheses; changed files by control plane, references, scripts, templates/assets, scenarios, validation, packaging; commands and pass/fail outputs; before/after comparison; package path/exclusions; residual risks and next hypotheses.
