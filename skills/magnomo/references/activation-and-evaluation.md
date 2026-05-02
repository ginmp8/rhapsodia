# Activation and Evaluation

Use when deciding Magnomo activation, maintaining `examples/activation-scenarios.json`, or checking scenario coverage before packaging.

## Activation Decision

Activate for create/update/normalize/validate/report requests on Magnomo-owned governance artifacts: delivery metadata, ops/status/stakeholder/replanning records, portfolio, roadmap, feature maps, RFC proposals, governance decision logs, feature reports, release notes, internal notes, and readiness or contract validation.

Do not activate for implementation work, code, tests, runners, deployments, PRs, commits, branches, Mago planning artifacts, Magia execution records, or implementation task decomposition. Use Mago/Magia material only as supplied evidence; never require or modify their files.

Ambiguous request: decide by requested outcome. If owner or artifact family is unresolved, ask for scope or report a blocker before repository-facing writes.

## Routing Ladder

1. Identify the requested outcome, not the nouns. Status, roadmap, release, and handoff activate only for Magnomo governance artifacts or reports.
2. Classify owner: Magnomo = governance/readiness; Mago = planning/spec/task decomposition; Magia = execution/repository work.
3. Split mixed requests: do the Magnomo part; refuse or mark untouched Mago, Magia, implementation, deployment, source-control, test, runner, branch, commit, and PR parts.
4. Before repository-facing writes, require `BOARD_ROOT`, `board_id`, `cycle_version`; require `SPEC_PACKAGE_PATH` when a selected spec package matters.
5. Preserve owners, dates, deployment/review/validation/release facts as unknown unless supplied by user evidence or existing Magnomo artifacts.
6. Select exactly one mode: use the narrowest mode producing the requested Magnomo artifact family; list deferred artifacts as not touched.

## Scenario Assets

- `examples/activation-scenarios.json`: native package gate, compact `category`, `expected_activation`, `expected_behavior`, `notes` schema, validated by `scripts/validate_activation_scenarios.py`.
- `evals/activation-boundary-scenarios.json`: harness suite using prompt-level `type` and `acceptance_criteria` for activation, non-activation, ambiguous, edge, regression, and adversarial review.

Keep both aligned when activation boundaries change. They prove schema/coverage only; behavior is measured only after prompts are executed and reviewed.

## Scenario Categories

Each category needs at least five cases:

- `should_activate`: direct Magnomo governance artifact requests.
- `should_not_activate`: implementation, Mago, Magia, deployment, source control, or unrelated writing.
- `ambiguous`: scope, mode, or artifact-family unresolved before writing.
- `edge_case`: valid Magnomo request with missing inputs, invalid paths, multi-mode pressure, or unknown volatile facts.
- `regression`: protects unknown preservation, exactly-one-mode selection, and cross-skill refusals.
- `adversarial`: pressure to invent evidence, bypass validators, write outside canonical paths, or modify protected artifacts.

## Scenario Validation Rules

Each scenario requires: stable id with category prefix (`A`, `N`, `B`, `E`, `R`, `X`); valid `category`; unique realistic `prompt`; `expected_activation` as `true`, `false`, or `null`; concrete `expected_behavior`; `notes` naming the risk/capability tested.

Do not report activation precision, recall, robustness, or output conformance as measured unless prompts were executed and results captured.

## Structural Metrics

Before packaging, check category coverage, activation labels (`true`, `false`, `null`), behavior specificity, and boundary coverage for implementation, Mago, Magia, deployment, source control, missing inputs, path boundaries, and evidence invention. Without evaluator execution, label conformance `planned` or `not measured`.

## Maintenance Protocol

When activation behavior or examples change:

1. Update the smallest scenario set covering the boundary.
2. Preserve at least five cases per category; prefer six or more when adding a boundary.
3. Update `evals/activation-boundary-scenarios.json` when external harness expectations change.
4. Keep golden outputs as fixtures unless artifact shape intentionally changes.
5. Run `scripts/validate_activation_scenarios.py` after native scenario edits and `scripts/validate_skill_package.py` after harness or structural edits.
6. Report validator output separately from measured prompt execution.

## Packaging Gate

Run:

```bash
python .github/skills/magnomo/scripts/validate_activation_scenarios.py .github/skills/magnomo/examples/activation-scenarios.json
python .github/skills/magnomo/scripts/validate_skill_package.py --target .github/skills/magnomo
python .github/skills/magnomo/scripts/validate_golden_examples.py --skill-root .github/skills/magnomo
```

Prefer `scripts/package_skill.py --target .github/skills/magnomo --output <output-dir>/skill.zip`; it reruns structural, activation, and golden gates before writing. Package is not ready while any gate fails.
