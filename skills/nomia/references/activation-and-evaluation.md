# Activation and Evaluation

Use for nomia activation decisions, `examples/activation-scenarios.json`, or scenario coverage before packaging.

## Activation Decision

Activate for create/update/normalize/validate/report requests on nomia-owned governance artifacts: delivery metadata, ops/status/stakeholder/replanning records, portfolio, roadmap, feature maps, RFC proposals, governance decision logs, feature reports, release notes, internal notes, readiness, and contract validation.

Do not activate for implementation work, code, tests, runners, deployments, PRs, commits, branches, Mago planning artifacts, Magia execution records, or implementation task decomposition. Mago/Magia material is read-only supplied evidence.

Ambiguous requests are decided by requested outcome. If owner or artifact family is unresolved, ask for scope or report a blocker before repository-facing writes.

## Skill Root Convention

Use `<skill-root>` for the root folder of this skill package. In this repository that is usually `skills/nomia`; when installed under GitHub/Copilot conventions it may be `.github/skills/nomia`; when extracted from a package it may be `nomia`.

## Routing Ladder

1. Identify the requested outcome, not just the nouns.
2. Classify owner: nomia = governance/readiness; Mago = planning/spec/task decomposition; Magia = execution/repository work.
3. Split mixed requests: do the nomia part; mark Mago, Magia, implementation, deployment, source-control, test, runner, branch, commit, and PR parts untouched.
4. Before repository-facing writes require `BOARD_ROOT`, `board_id`, `year`, `cycle_id`; require `SPEC_PACKAGE_PATH` when a selected spec package matters.
5. Preserve owners, dates, deployment/review/validation/release facts as unknown unless supplied by user evidence or existing nomia artifacts.
6. Select exactly one mode; defer other artifacts as not touched.

## Scenario Assets

- `examples/activation-scenarios.json`: native package gate with `category`, `expected_owner`, `expected_activation`, `diagnostic_entry_allowed`, `expected_behavior`, and `notes`; validated by `scripts/validate_activation_scenarios.py`.
- `evals/activation-boundary-scenarios.json`: harness suite with prompt-level `type` and `acceptance_criteria` for activation, non-activation, ambiguous, edge, regression, and adversarial review.

Keep both aligned when boundaries change. They prove schema/coverage only; behavior is measured only after prompts are executed and reviewed.

## Scenario Categories

Each category needs at least five cases: `should_activate` for direct governance artifact requests; `should_not_activate` for implementation/Mago/Magia/deployment/source-control/unrelated work; `ambiguous` for unresolved scope/mode/artifact family; `edge_case` for valid requests with missing inputs, invalid paths, multi-mode pressure, or unknown volatile facts; `regression` for unknown preservation, exactly-one-mode selection, and cross-skill refusals; `adversarial` for pressure to invent evidence, bypass validators, write outside canonical paths, or modify protected artifacts.

## Scenario Validation Rules

Each scenario requires stable id prefix (`A`, `N`, `B`, `E`, `R`, `X`), valid `category`, unique realistic `prompt`, `expected_owner` as `mago|magia|nomia|none`, `expected_activation` as `true|false|null`, boolean `diagnostic_entry_allowed`, concrete `expected_behavior`, and `notes` naming the risk or capability tested. `true` means Nomia is the resolved owner; `false` means Nomia must not be selected; `null` means owner resolution remains open and therefore requires `expected_owner: none` plus diagnostic-only entry before mutation.

Do not report activation precision, recall, robustness, or output conformance as measured unless prompts were executed and results captured.

## Structural Metrics

Before packaging, check category coverage, activation labels, behavior specificity, and boundary coverage for implementation, Mago, Magia, deployment, source control, missing inputs, path boundaries, and evidence invention. Without evaluator execution, label conformance `planned` or `not measured`.

## Maintenance Protocol

When activation behavior or examples change: update the smallest scenario set; keep at least five cases per category; update harness scenarios when external expectations change; keep golden outputs as fixtures unless artifact shape intentionally changes; run `scripts/validate_activation_scenarios.py` after native scenario edits and `scripts/validate_skill_package.py` after harness/structural edits; report validator output separately from measured prompt execution.

## Packaging Gate

```bash
python <skill-root>/scripts/validate_activation_scenarios.py <skill-root>/examples/activation-scenarios.json
python <skill-root>/scripts/validate_skill_package.py --target <skill-root>
python <skill-root>/scripts/validate_golden_examples.py --skill-root <skill-root>
```

Prefer `scripts/package_skill.py --target <skill-root> --output <output-dir>/skill.zip`; it reruns structural, activation, and golden gates before writing.

## Live routing evidence

Prepare and evaluate externally executed model observations with `scripts/live_routing_harness.py`. Validate results against the frozen corpus and `references/live-routing-result-schema.json`; do not convert fixture evidence into measured activation claims.
